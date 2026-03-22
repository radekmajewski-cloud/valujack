#!/usr/bin/env python3
"""
ValuJack Scoring Pipeline
=========================
Reads screener CSVs, scores each company against all eligible strategies,
assigns each company to its best-fit strategy (one company, one card),
calls Claude API for contextual AI scores, and outputs a patch JSON
plus a ready-to-deploy index.html patcher.

Usage:
    python3 valujack_scorer.py \
        --kings   Kings_2026-03-19.csv \
        --jacks   Jacks_2026-03-19.csv \
        --queens  Queens_2026-03-19.csv \
        --aces    Aces__2026-03-19.csv \
        --jokers  Jokers_2026-03-19.csv \
        --index   /path/to/index.html \
        --api-key YOUR_ANTHROPIC_API_KEY \
        --output  scores_output.json

Required packages: pandas, anthropic, requests
Install: pip install pandas anthropic
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

import pandas as pd

# ─────────────────────────────────────────────
# 1. CSV LOADING
# ─────────────────────────────────────────────

def load_csv(path: str) -> pd.DataFrame:
    """Load a screener CSV — handles semicolon separator and latin-1 encoding."""
    return pd.read_csv(path, sep=';', encoding='latin-1')


def clean_pct(val) -> float:
    """Convert '12,30%' or '12.30%' or 12.3 → float (0.0–100.0 scale)."""
    if pd.isna(val):
        return 0.0
    s = str(val).strip().replace('%', '').replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return 0.0


def clean_num(val) -> float:
    """Convert '1.234,5' or '1234.5' or '1 234' → float."""
    if pd.isna(val):
        return 0.0
    s = str(val).strip().replace(' ', '').replace(',', '.')
    # Handle European thousands separator: if >1 dot, keep only last as decimal
    parts = s.split('.')
    if len(parts) > 2:
        s = ''.join(parts[:-1]) + '.' + parts[-1]
    try:
        return float(s)
    except ValueError:
        return 0.0


def parse_price_position(val) -> float:
    """
    'Stock price - Price/L 1y' and 'Price/H 1y' give % above 52wk low/high.
    This returns 0-100 where 0 = at 52wk low, 100 = at 52wk high.
    val is like '131%' meaning price is 131% above the low.
    To get position in range: need both low% and high%.
    Returns raw percentage above low.
    """
    return clean_pct(val)


# ─────────────────────────────────────────────
# 2. SCORING HELPERS
# ─────────────────────────────────────────────

def score_pe(pe: float, low: float = 8, high: float = 30) -> float:
    """Lower P/E = better. Returns 0-100."""
    if pe <= 0:
        return 0.0
    if pe <= low:
        return 100.0
    if pe >= high:
        return 0.0
    return 100.0 * (high - pe) / (high - low)


def score_roe(roe: float) -> float:
    """ROE %. Higher = better. 0-100 mapped to 0-30%+ range."""
    if roe <= 0:
        return 0.0
    return min(100.0, roe / 30.0 * 100.0)


def score_roic(roic: float) -> float:
    """ROIC %. Higher = better. 15%+ is excellent."""
    if roic <= 0:
        return 0.0
    return min(100.0, roic / 20.0 * 100.0)


def score_fcf_margin(fcf: float) -> float:
    """FCF margin %. Higher = better. 20%+ excellent."""
    if fcf <= 0:
        return 20.0  # small positive for neutral
    return min(100.0, fcf / 25.0 * 100.0)


def score_debt_equity(de: float) -> float:
    """Lower D/E = better. 0 = 100pts, 2+ = 0pts."""
    if de < 0:
        return 50.0
    return max(0.0, 100.0 - (de / 2.0 * 100.0))


def score_growth(g: float, target: float = 15.0) -> float:
    """Earnings/revenue growth %. Target = excellent threshold."""
    if g <= 0:
        return 0.0
    return min(100.0, g / target * 100.0)


def score_momentum_rs(rs: float) -> float:
    """RS Rank 0-100. Direct mapping."""
    return max(0.0, min(100.0, float(rs) if not pd.isna(rs) else 0.0))


def score_price_vs_ma(pct_above: float) -> float:
    """
    Price vs MA200: pct_above is % above MA200 (from 'Price / MA - MA 200d').
    For momentum: being above MA200 is good, but not too far above.
    5-20% above = 100 pts. Below = scaled down. >30% = starts to fade (risk of pullback).
    """
    if pct_above <= -20:
        return 0.0
    if pct_above < 0:
        return max(0.0, 50.0 + pct_above * 2.5)
    if pct_above <= 20:
        return 80.0 + pct_above  # 80-100
    return max(50.0, 100.0 - (pct_above - 20) * 2)


def score_fair_value(price: float, fair_value: float) -> float:
    """
    Margin of Safety score. Returns 0-100.
    MoS = (fair_value - price) / fair_value
    >=25% MoS → 100 pts (strongly undervalued)
    0-25% MoS → 40-100 pts
    Overvalued → decreasing score
    >30% overvalued → veto territory (handled separately)
    """
    if fair_value <= 0 or price <= 0:
        return 50.0
    mos = (fair_value - price) / fair_value * 100  # in %
    if mos >= 25:
        return 100.0
    if mos >= 5:
        return 40.0 + (mos - 5) / 20.0 * 60.0
    if mos >= -5:
        return 30.0 + (mos + 5) / 10.0 * 10.0  # 30-40
    if mos >= -30:
        return max(0.0, 30.0 + mos)  # 0-30 for overvalued
    return 0.0


def score_dividend_health(div_yield: float, stable_10y: int, stable_5y: int,
                           div_growth_5y: float) -> float:
    """
    KING: Dividend health composite. 0-100.
    - Yield: 2-5% is ideal for aristocrats
    - Stability: 10y (max 5pts) + 5y (max 5pts) — treat as 0-10 total
    - Growth: positive growth is key
    """
    # Yield score (2-5% sweet spot)
    if div_yield <= 0:
        yield_score = 0.0
    elif div_yield < 1:
        yield_score = div_yield / 1.0 * 30.0
    elif div_yield <= 5:
        yield_score = 30.0 + (div_yield - 1) / 4.0 * 50.0
    elif div_yield <= 8:
        yield_score = 80.0 - (div_yield - 5) / 3.0 * 30.0  # high yield risk
    else:
        yield_score = 20.0  # danger zone

    # Stability score (both 10y and 5y on scale of 5)
    stability_score = (min(int(stable_10y), 10) / 10.0 * 50.0 +
                       min(int(stable_5y), 5) / 5.0 * 50.0)

    # Growth score
    growth_score = score_growth(div_growth_5y, target=10.0)

    return yield_score * 0.4 + stability_score * 0.3 + growth_score * 0.3


def score_earnings_stability(stable_5y: int, max_val: int = 5) -> float:
    """Earnings stable years. 0-100."""
    return min(int(stable_5y), max_val) / max_val * 100.0


def score_piotroski(fscore: int) -> float:
    """F-Score 0-9. 7+ = strong, 9 = perfect."""
    return min(int(fscore), 9) / 9.0 * 100.0


def score_canslim(canslim: float) -> float:
    """CANSLIM composite 0-100. Direct."""
    return max(0.0, min(100.0, float(canslim) if not pd.isna(canslim) else 0.0))


def score_price_position_52w(pct_above_low: float, pct_below_high: float) -> float:
    """
    For JOKER/JACK: being near 52wk high is bullish.
    pct_above_low: % price is above 52wk low (e.g. 131 means 131% above low)
    pct_below_high: % price is below 52wk high (e.g. 8 means 8% below high = near high)
    Returns 0-100 where near 52wk high = high score.
    """
    # pct_below_high = 100 - (price/high * 100) ... but we have price/high 1y directly
    # The CSV has 'Stock price - Price/H 1y' as % above high (negative = below high)
    # We interpret pct_below_high as how many % below the high
    if pct_below_high <= 0:
        return 100.0  # at or above 52wk high
    if pct_below_high <= 10:
        return 80.0 + (10 - pct_below_high) * 2.0
    if pct_below_high <= 25:
        return max(20.0, 80.0 - (pct_below_high - 10) * 4.0)
    return max(0.0, 20.0 - (pct_below_high - 25))


# ─────────────────────────────────────────────
# 3. VETO RULES
# ─────────────────────────────────────────────

def check_veto_dead_momentum(rs_rank: float, pct_above_low: float) -> bool:
    """
    Veto 1: RS Rank < 50 AND price in bottom 25% of 52wk range.
    pct_above_low: % above 52wk low. If price = low → 0%. Bottom 25% roughly = low pct.
    We approximate: if pct_above_low < 25 AND rs_rank < 50 → veto.
    """
    return rs_rank < 50 and pct_above_low < 25


def check_veto_extreme_overvaluation(price: float, fair_value: float) -> bool:
    """Veto 3: Price > 130% of fair value."""
    if fair_value <= 0:
        return False
    return price > fair_value * 1.30


# ─────────────────────────────────────────────
# 4. STRATEGY SCORERS
# ─────────────────────────────────────────────

def score_king(row: dict) -> dict:
    """
    KING — Dividend Aristocrats
    Weights: Fair Price/MoS 20%, Dividend Health 25%, Business Quality 15%,
             Growth 5%, Momentum/Technical 0%, Earnings Stability 10%,
             Financial Health 10%, Contextual AI 5% (remainder placeholder),
             [data-driven total: 95%, AI fills 5%]
    """
    price = clean_num(row.get('Stock price - Current', 0))
    fv    = clean_num(row.get('Fair value', 0))
    roic  = clean_pct(row.get('ROIC - Average 5y', 0))
    fcf   = clean_pct(row.get('FCF margin - Current', 0))
    de    = clean_num(row.get('Debt-Equity - Current', 0))
    eg5   = clean_pct(row.get('Earnings g. - Growth 5y', 0))
    rg5   = clean_pct(row.get('Revenue g. - Growth 5y', 0))
    div_y = clean_pct(row.get('Div. Yield - Current', 0))
    d10   = clean_num(row.get('Dividend - Stable 10y', 0))
    d5    = clean_num(row.get('Dividend - Stable 5y', 0))
    dg5   = clean_pct(row.get('Dividend g. - Growth 5y', 0))
    stab  = clean_num(row.get('Earnings - Stable 5y', 0))  # not in Kings CSV directly
    roe   = clean_pct(row.get('ROE - Current', 0))

    fair_score  = score_fair_value(price, fv)
    div_score   = score_dividend_health(div_y, d10, d5, dg5)
    qual_score  = (score_roic(roic) * 0.6 + score_fcf_margin(fcf) * 0.4)
    growth_score = score_growth(max(eg5, rg5), target=10.0)
    earn_stab   = score_earnings_stability(int(d10), max_val=10)  # use div stability as proxy
    fin_health  = score_debt_equity(de)

    # Veto check
    veto_ov = check_veto_extreme_overvaluation(price, fv)
    if veto_ov:
        fair_score = 0.0

    # Weighted sum (excluding AI 5% — filled later)
    raw = (
        fair_score  * 0.20 +
        div_score   * 0.25 +
        qual_score  * 0.15 +
        growth_score* 0.05 +
        earn_stab   * 0.10 +
        fin_health  * 0.10
    )
    # Scale to 95 (leaving 5 for AI)
    data_score = raw * (95 / 85)  # weights above sum to 85%

    if veto_ov and data_score > 52.25:  # 55 * 0.95
        data_score = 52.25

    return {
        'strategy': 'KING',
        'data_score': round(data_score, 1),
        'components': {
            'fair_value': round(fair_score, 1),
            'dividend_health': round(div_score, 1),
            'business_quality': round(qual_score, 1),
            'growth': round(growth_score, 1),
            'earnings_stability': round(earn_stab, 1),
            'financial_health': round(fin_health, 1),
        },
        'veto_overvalued': veto_ov,
    }


def score_jack(row: dict) -> dict:
    """
    JACK — Minervini Momentum
    Weights: Fair Price 15%, Dividend Health 0%, Business Quality 20%,
             Growth 25%, Momentum/Technical 20%, Earnings Stability 5%,
             Financial Health 0%, Contextual AI 25% (data portion: 75%)
    """
    price   = clean_num(row.get('Stock price - Current', 0))
    fv      = clean_num(row.get('Fair value', 0))
    roic    = clean_pct(row.get('ROIC - Average 5y', 0))
    fcf     = clean_pct(row.get('FCF margin - Current', 0))
    roe     = clean_pct(row.get('ROE - Current', 0))
    eg5     = clean_pct(row.get('Earnings g. - Growth 5y', 0))
    rs_rank = clean_num(row.get('RS Rank - L - 0-100', 0))
    ma50    = clean_pct(row.get('Price / MA - MA 50d', 0))
    ma200   = clean_pct(row.get('Price / MA - MA 200d', 0))
    p_low   = clean_pct(row.get('Stock price - Price/L 1y', 0))   # % above 52wk low
    p_high  = clean_pct(row.get('Stock price - Price/H 1y', 0))   # % below 52wk high (negative if above)
    stab_e  = clean_num(row.get('Earnings - Stable 5y', 0))
    stab_cf = clean_num(row.get('OP Cash F. - Stable 5y', 0))

    # % below 52wk high — if p_high is like "8%" meaning 8% below high
    pct_below_high = max(0.0, -p_high) if p_high <= 0 else p_high

    fair_score  = score_fair_value(price, fv)
    qual_score  = (score_roic(roic) * 0.5 + score_roe(roe) * 0.3 + score_fcf_margin(fcf) * 0.2)
    growth_sc   = score_growth(eg5, target=20.0)
    rs_sc       = score_momentum_rs(rs_rank)
    ma_sc       = (score_price_vs_ma(ma50) * 0.4 + score_price_vs_ma(ma200) * 0.6)
    pos_sc      = score_price_position_52w(p_low, pct_below_high)
    momentum_sc = rs_sc * 0.4 + ma_sc * 0.4 + pos_sc * 0.2
    earn_stab   = (score_earnings_stability(int(stab_e)) * 0.5 +
                   score_earnings_stability(int(stab_cf)) * 0.5)

    # Veto 1 — Dead Momentum
    veto_mom = check_veto_dead_momentum(rs_rank, p_low)
    veto_ov  = check_veto_extreme_overvaluation(price, fv)
    if veto_ov:
        fair_score = 0.0

    # Weights sum to 75% (AI = 25%)
    raw = (
        fair_score  * 0.15 +
        qual_score  * 0.20 +
        growth_sc   * 0.25 +
        momentum_sc * 0.20 +
        earn_stab   * 0.05
    )
    # Scale to 75 (AI fills 25)
    data_score = raw * (75 / 85)

    if veto_mom:
        data_score = min(data_score, 33.75)  # cap total at 45 (75% of 45 = 33.75)
    if veto_ov and data_score > 41.25:
        data_score = 41.25

    return {
        'strategy': 'JACK',
        'data_score': round(data_score, 1),
        'components': {
            'fair_value': round(fair_score, 1),
            'business_quality': round(qual_score, 1),
            'growth': round(growth_sc, 1),
            'momentum': round(momentum_sc, 1),
            'earnings_stability': round(earn_stab, 1),
        },
        'veto_dead_momentum': veto_mom,
        'veto_overvalued': veto_ov,
    }


def score_queen(row: dict) -> dict:
    """
    QUEEN — Magic Formula
    Weights: Fair Price 20%, Dividend Health 5%, Business Quality 25%,
             Growth 10%, Momentum/Technical 10%, Earnings Stability 10%,
             Financial Health 10%, Contextual AI 10% (data: 90%)
    """
    price   = clean_num(row.get('Stock price - Current', 0))
    fv      = clean_num(row.get('Fair value', 0))
    roic    = clean_pct(row.get('ROIC - Average 5y', 0))
    fcf     = clean_pct(row.get('FCF margin - Current', 0))
    pm      = clean_pct(row.get('Profit marg - Current', 0))
    de      = clean_num(row.get('Debt-Equity - Current', 0))
    eg5     = clean_pct(row.get('Earnings g. - Growth 5y', 0))
    rg5     = clean_pct(row.get('Revenue g. - Growth 5y', 0))
    ma200   = clean_pct(row.get('Price / MA - MA 200d', 0))
    rsi     = clean_num(row.get('RSI - RSI(14)', 0))
    stab_e  = clean_num(row.get('Earnings - Stable 5y', 0))
    stab_d  = clean_num(row.get('Dividend - Stable 5y', 0))
    div_y   = clean_pct(row.get('Dividend - Current', 0))
    perf1m  = clean_pct(row.get('Performance - Perform. 1m', 0))
    perf1y  = clean_pct(row.get('Performance - Perform. 1y', 0))

    fair_score  = score_fair_value(price, fv)
    qual_score  = (score_roic(roic) * 0.5 + score_fcf_margin(fcf) * 0.3 +
                   min(100.0, pm / 20.0 * 100.0) * 0.2)
    div_score   = min(100.0, div_y / 3.0 * 100.0) if div_y > 0 else 30.0
    growth_sc   = score_growth(max(eg5, rg5), target=12.0)

    # RSI neutral zone 40-60 is fine; prefer not overbought/oversold
    rsi_sc = 100.0 - abs(rsi - 50) * 2.0 if rsi > 0 else 50.0
    mom_sc = (score_price_vs_ma(ma200) * 0.6 + rsi_sc * 0.4)

    earn_stab   = (score_earnings_stability(int(stab_e)) * 0.7 +
                   score_earnings_stability(int(stab_d)) * 0.3)
    fin_health  = score_debt_equity(de)

    veto_ov = check_veto_extreme_overvaluation(price, fv)
    if veto_ov:
        fair_score = 0.0

    raw = (
        fair_score  * 0.20 +
        div_score   * 0.05 +
        qual_score  * 0.25 +
        growth_sc   * 0.10 +
        mom_sc      * 0.10 +
        earn_stab   * 0.10 +
        fin_health  * 0.10
    )
    data_score = raw * (90 / 90)  # weights sum to 90%

    if veto_ov and data_score > 49.5:
        data_score = 49.5

    return {
        'strategy': 'QUEEN',
        'data_score': round(data_score, 1),
        'components': {
            'fair_value': round(fair_score, 1),
            'dividend_health': round(div_score, 1),
            'business_quality': round(qual_score, 1),
            'growth': round(growth_sc, 1),
            'momentum': round(mom_sc, 1),
            'earnings_stability': round(earn_stab, 1),
            'financial_health': round(fin_health, 1),
        },
        'veto_overvalued': veto_ov,
    }


def score_ace(row: dict) -> dict:
    """
    ACE — Piotroski F-Score
    Weights: Fair Price 15%, Dividend Health 5%, Business Quality 15%,
             Growth 10%, Momentum/Technical 10%, Earnings Stability 20%,
             Financial Health 20%, Contextual AI 5% (data: 95%)
    """
    price   = clean_num(row.get('Stock price - Current', 0))
    fv      = clean_num(row.get('Fair value', 0))
    roic    = clean_pct(row.get('ROIC - Average 5y', 0))
    fcf     = clean_pct(row.get('FCF margin - Average 3y', 0))
    roa     = clean_pct(row.get('ROA - Average 5y', 0))
    de      = clean_num(row.get('Debt-Equity - Current', 0))
    cr      = clean_num(row.get('Current r. - Current', 0))
    eg5     = clean_pct(row.get('Earnings g. - Growth 5y', 0))
    fs      = clean_num(row.get('F-Score - Point', 0))
    ma200   = clean_pct(row.get('Price / MA - MA 200d', 0))
    rs_rank = clean_pct(row.get('Performance - Perform. 1y', 0))  # proxy
    stab_e  = clean_num(row.get('Earnings - Stable 5y', 0))
    stab_d  = clean_num(row.get('Dividend - Stable 5y', 0))
    stab_cf = clean_num(row.get('OP Cash F. - Stable 5y', 0))

    fair_score   = score_fair_value(price, fv)
    qual_score   = (score_roic(roic) * 0.4 + score_fcf_margin(fcf) * 0.3 +
                    min(100.0, roa / 10.0 * 100.0) * 0.3)
    piotro_sc    = score_piotroski(int(fs))
    growth_sc    = score_growth(eg5, target=10.0)
    mom_sc       = score_price_vs_ma(ma200)

    # ACE heavily weights earnings stability
    earn_stab    = (score_earnings_stability(int(stab_e)) * 0.5 +
                    score_earnings_stability(int(stab_cf)) * 0.5)

    # Financial health: D/E + current ratio
    cr_sc      = min(100.0, (cr - 1.0) / 1.5 * 100.0) if cr > 1 else max(0.0, cr / 1.0 * 50.0)
    fin_health = (score_debt_equity(de) * 0.6 + cr_sc * 0.4)

    div_proxy  = 50.0  # no dividend col in ACE CSV

    veto_ov = check_veto_extreme_overvaluation(price, fv)
    if veto_ov:
        fair_score = 0.0

    # Combine: F-Score blended into business quality
    raw = (
        fair_score  * 0.15 +
        div_proxy   * 0.05 +
        (qual_score * 0.5 + piotro_sc * 0.5) * 0.15 +
        growth_sc   * 0.10 +
        mom_sc      * 0.10 +
        earn_stab   * 0.20 +
        fin_health  * 0.20
    )
    data_score = raw * (95 / 95)

    if veto_ov and data_score > 52.25:
        data_score = 52.25

    return {
        'strategy': 'ACE',
        'data_score': round(data_score, 1),
        'components': {
            'fair_value': round(fair_score, 1),
            'piotroski': round(piotro_sc, 1),
            'business_quality': round(qual_score, 1),
            'growth': round(growth_sc, 1),
            'momentum': round(mom_sc, 1),
            'earnings_stability': round(earn_stab, 1),
            'financial_health': round(fin_health, 1),
        },
        'veto_overvalued': veto_ov,
    }


def score_joker(row: dict) -> dict:
    """
    JOKER — CANSLIM Growth
    Weights: Fair Price 10%, Dividend Health 0%, Business Quality 20%,
             Growth 35%, Momentum/Technical 20%, Earnings Stability 5%,
             Financial Health 0%, Contextual AI 20% (data: 80%)
    Note: JOKER exempt from Veto 3 (overvaluation).
    """
    price   = clean_num(row.get('Stock price - Current', 0))
    fv      = clean_num(row.get('Fair value', 0))
    roic    = clean_pct(row.get('ROIC - Average 5y', 0))
    fcf     = clean_pct(row.get('FCF margin - Current', 0))
    eg5     = clean_pct(row.get('Earnings g. - Growth 5y', 0))
    eg_yy   = clean_pct(row.get('Earnings g. - Y-Y Growth', 0))
    eg1y    = clean_pct(row.get('Earnings g. - Growth 1y', 0))
    eg3y    = clean_pct(row.get('Earnings g. - Growth 3y', 0))
    rg3     = clean_pct(row.get('Revenue g. - Growth 3y', 0))
    rs_rank = clean_num(row.get('RS Rank - L - 0-100', 0))
    vol_rk  = clean_num(row.get('Volume Rank - 0-100', 0))
    canslim = clean_num(row.get('Canslim - 0-100', 0))
    trend   = clean_pct(row.get('Trend - Price/H-L 1y', 0))  # % of 52wk range
    perf1y  = clean_pct(row.get('Performance - Perform. 1y', 0))

    fair_score  = score_fair_value(price, fv)
    qual_score  = (score_roic(roic) * 0.6 + score_fcf_margin(fcf) * 0.4)

    # Growth: weight recent (YY) more than 5y for JOKER
    growth_sc = (
        score_growth(eg_yy, 50.0) * 0.30 +
        score_growth(eg1y, 30.0)  * 0.25 +
        score_growth(eg3y, 25.0)  * 0.20 +
        score_growth(rg3, 20.0)   * 0.15 +
        score_growth(eg5, 15.0)   * 0.10
    )

    # Momentum: RS rank, CANSLIM score, trend position
    mom_sc = (
        score_momentum_rs(rs_rank) * 0.35 +
        score_canslim(canslim)     * 0.35 +
        min(100.0, trend)          * 0.30
    )

    # Veto 1
    veto_mom = check_veto_dead_momentum(rs_rank, trend)

    raw = (
        fair_score  * 0.10 +
        qual_score  * 0.20 +
        growth_sc   * 0.35 +
        mom_sc      * 0.20 +
        50.0        * 0.05   # earnings stability placeholder (no col)
    )
    data_score = raw * (80 / 90)

    if veto_mom:
        data_score = min(data_score, 36.0)  # cap at 45 total → 80% = 36

    return {
        'strategy': 'JOKER',
        'data_score': round(data_score, 1),
        'components': {
            'fair_value': round(fair_score, 1),
            'business_quality': round(qual_score, 1),
            'growth': round(growth_sc, 1),
            'momentum': round(mom_sc, 1),
        },
        'veto_dead_momentum': veto_mom,
    }


# ─────────────────────────────────────────────
# 5. CLAUDE AI SCORING
# ─────────────────────────────────────────────

AI_WEIGHT = {
    'KING':  0.15,   # raised — dividend news matters
    'JACK':  0.25,
    'QUEEN': 0.10,
    'ACE':   0.05,
    'JOKER': 0.20,
}

STRATEGY_AI_FOCUS = {
    'KING':  "dividend sustainability, recent dividend news (cuts/suspensions/cancellations), yield safety, and long-term income compounding quality",
    'JACK':  "price momentum strength, earnings acceleration catalyst, and institutional interest signals",
    'QUEEN': "business moat, pricing power, competitive advantage, and quality-at-a-discount thesis",
    'ACE':   "balance sheet strength, cash flow quality, and improving financial fundamentals trajectory",
    'JOKER': "growth runway, market leadership potential, and momentum sustainability for this growth leader",
}


def get_ai_score(company: str, ticker: str, sector: str, industry: str,
                 strategy: str, components: dict, api_key: str) -> float:
    """Call Claude API for contextual AI score. Returns 0-100."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        focus = STRATEGY_AI_FOCUS.get(strategy, "overall investment quality")
        comp_str = "\n".join(f"  - {k}: {v}/100" for k, v in components.items())

        prompt = f"""You are a professional investment analyst scoring a stock for the ValuJack {strategy} strategy.

Company: {company} ({ticker})
Sector: {sector} | Industry: {industry}
Strategy: {strategy}

Financial data scores (0-100):
{comp_str}

Your task: Provide a CONTEXTUAL AI SCORE from 0-100 focusing specifically on {focus}.

Consider:
- Business quality and competitive positioning
- Industry tailwinds or headwinds
- Management track record if known
- Any relevant recent developments
- How well this company fits the {strategy} strategy thesis

Respond with ONLY a JSON object in this exact format:
{{"score": <number 0-100>, "reasoning": "<2-3 sentences max>"}}

Be honest and precise. A score of 50 is neutral/average. Reserve 80+ for genuinely exceptional cases."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()
        # Clean potential markdown
        response_text = re.sub(r'```json|```', '', response_text).strip()
        data = json.loads(response_text)
        score = float(data.get('score', 50))
        reasoning = data.get('reasoning', '')
        return max(0.0, min(100.0, score)), reasoning

    except Exception as e:
        print(f"  ⚠ AI scoring failed for {ticker}: {e}", file=sys.stderr)
        return 50.0, "AI scoring unavailable"


# ─────────────────────────────────────────────
# 6. MAIN PIPELINE
# ─────────────────────────────────────────────

def load_all_companies(args) -> list[dict]:
    """Load all CSVs, tag each row with its source strategy pool."""
    all_companies = []

    file_map = {
        'KING':  args.kings,
        'JACK':  args.jacks,
        'QUEEN': args.queens,
        'ACE':   args.aces,
        'JOKER': args.jokers,
    }

    for strategy, filepath in file_map.items():
        if not filepath or not Path(filepath).exists():
            print(f"  ⚠ Skipping {strategy} — file not found: {filepath}", file=sys.stderr)
            continue
        df = load_csv(filepath)
        for _, row in df.iterrows():
            ticker = str(row.get('Info - Ticker', '')).strip()
            if not ticker or ticker.lower() == 'nan':
                continue
            company = str(row.get('Company', ticker)).strip()
            d = row.to_dict()
            d['_source_strategy'] = strategy
            d['_ticker'] = ticker
            d['_company'] = company
            all_companies.append(d)

    return all_companies


def deduplicate_by_ticker(companies: list[dict]) -> list[dict]:
    """
    If a ticker appears in multiple strategy files, keep one row per ticker.
    Prefer the row from the strategy it would score highest in (resolved later).
    For now, keep all rows but flag duplicates.
    """
    seen = {}
    result = []
    for c in companies:
        t = c['_ticker']
        if t not in seen:
            seen[t] = True
            result.append(c)
        # Duplicate tickers from different files: we'll score all and pick best
    return result


SCORERS = {
    'KING':  score_king,
    'JACK':  score_jack,
    'QUEEN': score_queen,
    'ACE':   score_ace,
    'JOKER': score_joker,
}


def score_all_strategies(row: dict) -> dict:
    """Score a company against all 5 strategies. Returns dict of results."""
    results = {}
    for strategy, scorer in SCORERS.items():
        try:
            results[strategy] = scorer(row)
        except Exception as e:
            results[strategy] = {'strategy': strategy, 'data_score': 0.0,
                                  'components': {}, 'error': str(e)}
    return results


def assign_best_strategy(scores: dict) -> str:
    """Pick the strategy where this company scores highest."""
    best = max(scores.items(), key=lambda x: x[1].get('data_score', 0))
    return best[0]


def run_pipeline(args):
    print("=" * 60)
    print("ValuJack Scoring Pipeline")
    print("=" * 60)

    # Load
    print("\n📂 Loading screener data...")
    companies = load_all_companies(args)
    companies = deduplicate_by_ticker(companies)
    print(f"   {len(companies)} unique companies loaded")

    # Score all strategies
    print("\n📊 Scoring companies across all strategies...")
    scored = []
    for c in companies:
        all_scores = score_all_strategies(c)
        best_strategy = assign_best_strategy(all_scores)
        best_data_score = all_scores[best_strategy]['data_score']

        scored.append({
            'ticker': c['_ticker'],
            'company': c['_company'],
            'best_strategy': best_strategy,
            'data_score': best_data_score,
            'all_strategy_scores': {k: v['data_score'] for k, v in all_scores.items()},
            'components': all_scores[best_strategy].get('components', {}),
            'veto_dead_momentum': all_scores[best_strategy].get('veto_dead_momentum', False),
            'veto_overvalued': all_scores[best_strategy].get('veto_overvalued', False),
            'sector': str(c.get('Info - Sector', '')),
            'industry': str(c.get('Info - Industry', '')),
            '_row': c,
        })

    # AI scoring
    if args.api_key:
        print(f"\n🤖 Running AI scoring (Claude API)...")
        print(f"   Scoring {len(scored)} companies — estimated cost: ~${len(scored) * 0.01:.2f}")
        for i, s in enumerate(scored):
            # Only AI-score companies that might make the cut (data_score > 35)
            if s['data_score'] < 35:
                s['ai_score'] = 50.0
                s['ai_reasoning'] = "Below threshold — skipped"
                continue

            print(f"   [{i+1}/{len(scored)}] {s['ticker']} ({s['best_strategy']})...", end='', flush=True)
            ai_score, reasoning = get_ai_score(
                company=s['company'],
                ticker=s['ticker'],
                sector=s['sector'],
                industry=s['industry'],
                strategy=s['best_strategy'],
                components=s['components'],
                api_key=args.api_key,
            )
            s['ai_score'] = ai_score
            s['ai_reasoning'] = reasoning
            ai_weight = AI_WEIGHT[s['best_strategy']]
            data_weight = 1.0 - ai_weight
            s['final_score'] = round(
                s['data_score'] * data_weight / (1 - ai_weight) * data_weight +
                ai_score * ai_weight,
                1
            )
            # Cleaner: data_score is already scaled to (1-ai_weight)*100
            # final = data_score + ai_score * ai_weight
            s['final_score'] = round(s['data_score'] + ai_score * ai_weight, 1)
            s['final_score'] = min(100.0, s['final_score'])

            print(f" data={s['data_score']} ai={ai_score:.0f} → final={s['final_score']}")
            time.sleep(0.3)  # rate limiting
    else:
        print("\n⚠ No API key provided — using data scores only (no AI component)")
        for s in scored:
            s['ai_score'] = 50.0
            s['ai_reasoning'] = "No API key"
            s['dividend_suspended'] = False
            s['final_score'] = s['data_score']

    # Apply veto caps to final scores
    for s in scored:
        if s.get('veto_dead_momentum'):
            s['final_score'] = min(s['final_score'], 45.0)
            s['veto_applied'] = 'dead_momentum'
        elif s.get('veto_overvalued'):
            s['final_score'] = min(s['final_score'], 55.0)
            s['veto_applied'] = 'extreme_overvaluation'
        else:
            s['veto_applied'] = None

    # Star ratings
    for s in scored:
        fs = s['final_score']
        if fs >= 85:
            s['stars'] = 5
        elif fs >= 70:
            s['stars'] = 4
        elif fs >= 55:
            s['stars'] = 3
        elif fs >= 40:
            s['stars'] = 2
        else:
            s['stars'] = 1

    # Filter: only rotation-eligible (stars >= 3, score >= 55)
    eligible = [s for s in scored if s['final_score'] >= 55]
    print(f"\n✅ {len(eligible)} companies eligible for rotation (score ≥ 55)")

    # Sort by final score desc
    scored.sort(key=lambda x: x['final_score'], reverse=True)
    eligible.sort(key=lambda x: x['final_score'], reverse=True)

    # Output JSON
    output = {
        'generated': pd.Timestamp.now().isoformat(),
        'total_scored': len(scored),
        'eligible_for_rotation': len(eligible),
        'companies': [
            {
                'ticker': s['ticker'],
                'company': s['company'],
                'strategy': s['best_strategy'],
                'final_score': s['final_score'],
                'data_score': s['data_score'],
                'ai_score': s.get('ai_score', 50.0),
                'stars': s['stars'],
                'veto': s['veto_applied'],
                'all_scores': s['all_strategy_scores'],
                'components': s['components'],
                'ai_reasoning': s.get('ai_reasoning', ''),
            }
            for s in scored
        ],
    }

    out_path = args.output or 'valujack_scores.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Scores saved → {out_path}")

    # Print summary table
    print("\n" + "=" * 70)
    print(f"{'TICKER':<10} {'COMPANY':<30} {'STRATEGY':<8} {'SCORE':>6} {'STARS':>6}")
    print("-" * 70)
    for s in scored[:40]:  # top 40
        flag = " ⚠" if s['veto_applied'] else ""
        stars = "★" * s['stars'] + "☆" * (5 - s['stars'])
        print(f"{s['ticker']:<10} {s['company'][:29]:<30} {s['best_strategy']:<8} "
              f"{s['final_score']:>6.1f} {stars}{flag}")

    if args.index and Path(args.index).exists():
        patch_index_html(args.index, scored)

    return output


# ─────────────────────────────────────────────
# 7. INDEX.HTML PATCHER
# ─────────────────────────────────────────────

def patch_index_html(index_path: str, scored: list[dict]):
    """
    Patch valuation signal data in index.html.
    Looks for ticker patterns in the JS card data and updates score-related fields.
    This is a conservative patch — only updates fields we can confidently map.
    """
    print(f"\n🔧 Patching {index_path}...")

    score_map = {s['ticker']: s for s in scored}

    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()

    patch_count = 0
    for ticker, s in score_map.items():
        # Find the card data block for this ticker in the JS
        # Pattern: id: 'TICKER' ... valuejackScore: N
        pattern = rf"(id:\s*['\"]?{re.escape(ticker)}['\"]?.*?valuejackScore:\s*)(\d+(?:\.\d+)?)"
        replacement = rf"\g<1>{s['final_score']}"
        new_html, n = re.subn(pattern, replacement, html, flags=re.DOTALL | re.IGNORECASE)
        if n > 0:
            html = new_html
            patch_count += n

    out_path = index_path.replace('.html', '_scored.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"   Patched {patch_count} score values → {out_path}")
    print(f"   Review {out_path} before deploying with: vercel --prod")


# ─────────────────────────────────────────────
# 8. CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='ValuJack Scoring Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('--kings',   help='KING screener CSV')
    parser.add_argument('--jacks',   help='JACK screener CSV')
    parser.add_argument('--queens',  help='QUEEN screener CSV')
    parser.add_argument('--aces',    help='ACE screener CSV')
    parser.add_argument('--jokers',  help='JOKER screener CSV')
    parser.add_argument('--index',   help='Path to index.html for patching')
    parser.add_argument('--api-key', help='Anthropic API key for AI scoring')
    parser.add_argument('--output',  help='Output JSON path (default: valujack_scores.json)',
                        default='valujack_scores.json')
    parser.add_argument('--dry-run', action='store_true',
                        help='Score only, skip AI and HTML patching')

    args = parser.parse_args()

    if args.dry_run:
        args.api_key = None
        args.index = None

    if not any([args.kings, args.jacks, args.queens, args.aces, args.jokers]):
        parser.print_help()
        print("\n⚠ No CSV files specified. Exiting.")
        sys.exit(1)

    run_pipeline(args)


if __name__ == '__main__':
    main()
