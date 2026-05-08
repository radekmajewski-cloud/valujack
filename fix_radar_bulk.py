import re
import csv
import json
from datetime import datetime

CARDS_PATH = '/Users/radekmajewski/Downloads/valujack/public/cards.js'
CSV_PATH = '/Users/radekmajewski/Downloads/valujack/Company data/All_company_data_2026-04-18.csv'

# ── Radar dimensions per card type ───────────────────────────────────────────
# Colors match existing working cards
RADAR = {
    'KING':  [
        ('Dividend',       '#4CAF82'),
        ('Fair Price',     '#D4884A'),
        ('Profit',         '#5B8FD4'),
        ('Stable Earnings','#9B6ED4'),
        ('Low Debt',       '#C4784A'),
    ],
    'JACK':  [
        ('Earnings Growth','#5B8FD4'),
        ('Momentum',       '#D4884A'),
        ('Profit',         '#4CAF82'),
        ('Fair Price',     '#9B6ED4'),
        ('Stable Earnings','#C4784A'),
    ],
    'QUEEN': [
        ('Profit',         '#5B8FD4'),
        ('Fair Price',     '#D4884A'),
        ('Earnings Growth','#4CAF82'),
        ('Stable Earnings','#9B6ED4'),
        ('Low Debt',       '#C4784A'),
    ],
    'ACE':   [
        ('Stable Earnings','#4CAF82'),
        ('Low Debt',       '#9B6ED4'),
        ('Profit',         '#5B8FD4'),
        ('Earnings Growth','#D4884A'),
        ('Fair Price',     '#C4784A'),
    ],
    'JOKER': [
        ('Earnings Growth','#5B8FD4'),
        ('Momentum',       '#D4884A'),
        ('Profit',         '#4CAF82'),
        ('Revenue Growth', '#9B6ED4'),
        ('Fair Price',     '#C4784A'),
    ],
    'TWO':   [
        ('Recovery',       '#D85A30'),
        ('Quality',        '#5B8FD4'),
        ('Fair Price',     '#9B6ED4'),
        ('Low Debt',       '#4CAF82'),
        ('Profit',         '#C4784A'),
    ],
}

# ── Load CSV ──────────────────────────────────────────────────────────────────
def parse_num(s):
    if not s or s.strip() == '':
        return None
    s = s.strip().replace('%','').replace(',','.')
    try:
        return float(s)
    except:
        return None

csv_data = {}  # ticker -> row dict
with open(CSV_PATH, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        ticker = row['Info - Ticker'].strip()
        csv_data[ticker] = row

print(f"Loaded {len(csv_data)} companies from CSV")

# ── Score calculators ─────────────────────────────────────────────────────────
def score_fscore(row):
    v = parse_num(row.get('F-Score - Point',''))
    if v is None: return 5, 'F-Score', 'N/A'
    s = round(v / 9 * 10)
    return min(10, max(1, s)), 'F-Score', f'{int(v)}/9'

def score_roic(row):
    v = parse_num(row.get('ROIC - Current',''))
    if v is None: return 5, 'ROIC', 'N/A'
    # 0%=1, 10%=5, 20%=7, 30%+=10
    if v <= 0: s = 1
    elif v >= 30: s = 10
    else: s = round(1 + v / 30 * 9)
    return min(10, max(1, s)), 'ROIC', f'{v:.1f}%'

def score_gross_margin(row):
    v = parse_num(row.get('Gross marg - Average 1y',''))
    if v is None: return 5, 'Gross Margin', 'N/A'
    s = round(v / 100 * 10)
    return min(10, max(1, s)), 'Gross Margin', f'{v:.0f}%'

def score_debt(row):
    v = parse_num(row.get('Debt-Equity - Current',''))
    if v is None: return 5, 'D/E', 'N/A'
    # Lower is better: 0=10, 0.5=8, 1=6, 2=4, 3+=1
    if v < 0: s = 3
    elif v <= 0.2: s = 10
    elif v <= 0.5: s = 8
    elif v <= 1.0: s = 6
    elif v <= 2.0: s = 4
    elif v <= 3.0: s = 2
    else: s = 1
    return s, 'D/E', f'{v:.1f}'

def score_earnings_growth(row):
    v = parse_num(row.get('Earnings g. - Growth 5y',''))
    if v is None: return 5, 'EPS Growth 5y', 'N/A'
    if v >= 30: s = 10
    elif v >= 20: s = 8
    elif v >= 10: s = 6
    elif v >= 0: s = 4
    else: s = 2
    return s, 'EPS Growth 5y', f'+{v:.0f}%' if v >= 0 else f'{v:.0f}%'

def score_revenue_growth(row):
    v = parse_num(row.get('Revenue g. - Growth 1y',''))
    if v is None: return 5, 'Rev Growth', 'N/A'
    if v >= 20: s = 10
    elif v >= 10: s = 8
    elif v >= 5: s = 6
    elif v >= 0: s = 4
    else: s = 2
    return s, 'Rev Growth', f'+{v:.0f}%' if v >= 0 else f'{v:.0f}%'

def score_momentum(row):
    v = parse_num(row.get('RS Rank - L - 0-100',''))
    if v is None:
        v = parse_num(row.get('Performance - Perform. 1m',''))
        if v is None: return 5, 'RS Rank', 'N/A'
        s = round((v + 30) / 60 * 10)
        return min(10, max(1, s)), '1M Perf', f'{v:.1f}%'
    s = round(v / 100 * 10)
    return min(10, max(1, s)), 'RS Rank', f'{int(v)}'

def score_dividend(row):
    v = parse_num(row.get('Div. Yield - Current',''))
    stable = parse_num(row.get('Dividend - Stable 5y',''))
    if v is None: return 5, 'Div. Yield', 'N/A'
    if v >= 5: s = 10
    elif v >= 3: s = 8
    elif v >= 2: s = 6
    elif v >= 1: s = 4
    else: s = 2
    if stable and stable >= 4: s = min(10, s + 1)
    return s, 'Div. Yield', f'{v:.1f}%'

def score_fair_price(row, card_fair_value, card_ticker):
    # Use fair value from card vs current price from CSV
    price = parse_num(row.get('Stock price - Current',''))
    if price and card_fair_value and price > 0:
        mos = (card_fair_value - price) / card_fair_value * 100
        if mos >= 40: s = 10
        elif mos >= 25: s = 8
        elif mos >= 10: s = 6
        elif mos >= 0: s = 4
        else: s = 2  # overvalued
        return s, 'Undervalued', f'{mos:+.0f}%'
    return 5, 'Fair Price', 'N/A'

def score_recovery(row):
    v = parse_num(row.get('Performance - Perform. 1m',''))
    if v is None: return 4, '1M Perf', 'N/A'
    if v >= 15: s = 8
    elif v >= 10: s = 7
    elif v >= 5: s = 5
    elif v >= 0: s = 4
    else: s = 2
    return s, '1M Perf', f'+{v:.1f}%' if v >= 0 else f'{v:.1f}%'

def score_stable_earnings(row):
    v = parse_num(row.get('Dividend - Stable 5y',''))  # reused as earnings stability proxy
    fscore = parse_num(row.get('F-Score - Point',''))
    if fscore is not None:
        s = round(fscore / 9 * 10)
        return min(10, max(1,s)), 'Stable Earnings', f'{int(fscore)}/10'
    if v is None: return 5, 'Stable Earnings', 'N/A'
    s = round(v / 5 * 10)
    return min(10, max(1,s)), 'Stable Earnings', f'{int(v)}/5'

# ── Build scores for a card ───────────────────────────────────────────────────
def build_scores(card_type, row, fair_value, ticker):
    dims = RADAR.get(card_type, [])
    scores = []
    for label, color in dims:
        if label == 'Dividend':
            v, raw, rawV = score_dividend(row)
        elif label == 'Fair Price':
            v, raw, rawV = score_fair_price(row, fair_value, ticker)
        elif label == 'Profit':
            v, raw, rawV = score_gross_margin(row)
        elif label == 'Low Debt':
            v, raw, rawV = score_debt(row)
        elif label == 'Stable Earnings':
            v, raw, rawV = score_stable_earnings(row)
        elif label == 'Earnings Growth':
            v, raw, rawV = score_earnings_growth(row)
        elif label == 'Revenue Growth':
            v, raw, rawV = score_revenue_growth(row)
        elif label == 'Momentum':
            v, raw, rawV = score_momentum(row)
        elif label == 'Recovery':
            v, raw, rawV = score_recovery(row)
        elif label == 'Quality':
            v, raw, rawV = score_fscore(row)
        else:
            v, raw, rawV = 5, label, 'N/A'
        scores.append(f"{{ l: '{label}', v: {v}, max: 10, color: '{color}', raw: '{raw}', rawV: '{rawV}' }}")
    return '[' + ', '.join(scores) + ']'

# ── Process cards.js ──────────────────────────────────────────────────────────
with open(CARDS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
backup = CARDS_PATH + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}_before_radar_bulk'
with open(backup, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Backup: {backup}")

# Parse cards with empty scores using regex
# Match: type, ticker, fairValue, then scores: []
pattern = re.compile(
    r"id: (\d+), type: '([A-Z]+)', isPro: (?:true|false), fairValue: ([0-9.]+|null).*?ticker: '([^']+)'.*?scores: \[\]",
    re.DOTALL
)

updated = 0
not_found = []

def replacer(m):
    global updated
    card_id = m.group(1)
    card_type = m.group(2)
    fair_val_str = m.group(3)
    ticker = m.group(4)
    
    fair_value = float(fair_val_str) if fair_val_str != 'null' else None
    
    row = csv_data.get(ticker)
    if row is None:
        not_found.append(ticker)
        return m.group(0)
    
    scores_str = build_scores(card_type, row, fair_value, ticker)
    updated += 1
    if updated <= 20:
        print(f"  #{card_id} {ticker:12s} ({card_type})")
    
    return m.group(0).replace('scores: []', f'scores: {scores_str}')

new_content = pattern.sub(replacer, content)

with open(CARDS_PATH, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\n✅ Updated radar scores for {updated} cards")
print(f"⚠️  Not found in CSV: {len(not_found)} cards")
if not_found[:20]:
    print(f"   First 20: {not_found[:20]}")

# Verify
remaining = new_content.count('scores: []')
print(f"\nRemaining empty scores: {remaining}")
