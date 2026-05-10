# ValuJack Methodology — Card Selection Pipeline

**Last updated:** 9 May 2026

---

## Starting point

A pool of approximately 681 companies, each tagged to one of six strategies (King, Queen, Ace, Jack, Joker, Two), each with a fair value already calculated and a ValuJack quality score (stars).

This is the universe. Every card in the deck comes from here.

---

## The three layers of evaluation

Every card is evaluated on three independent dimensions:

### 1. Fundamentals score (0–10) — How good is this business under its strategy?

Slow-moving. Refreshed quarterly or when earnings come out. Comes from the radar values (Growth, Profitability, Balance sheet). Note: Fair Price is removed from the radar to avoid double-counting with the price layer.

### 2. Context score (0–10) — Is now a good time for this company?

Medium-moving. Refreshed weekly by Claude. Captures sector cycle, recent news, macro fit, near-term catalysts. Comes with a one-sentence reason that is visible to the user. A score of 0 means AVOID — material problem, do not pick.

### 3. Price score (0–10) — Is the price right today?

Fast-moving. Refreshed every weekday morning. Based on today's margin of safety: (Fair Value − Current Price) / Fair Value × 100. A score of 0 means no margin of safety — drop from today's pick.

---

## Strategy-specific weights

Different strategies care about the three layers in different proportions. Each strategy has its own multipliers, with each strategy showing a clearly distinct personality:

| Strategy | Fundamentals | Context | Price | Role of context |
|---|---|---|---|---|
| **King** — Dividend Aristocrats | 1.5 | 0.5 | 1.5 | Falling-knife check |
| **Queen** — Magic Formula | 1.5 | 0.5 | 2.0 | Falling-knife check |
| **Ace** — Piotroski F-Score | 2.0 | 1.5 | 1.0 | Validates real improvement |
| **Jack** — Minervini Momentum | 1.0 | 2.5 | 0 | Context IS the strategy |
| **Joker** — CANSLIM Growth | 2.0 | 1.5 | 0.5 | Confirms growth thesis |
| **Two** — Contrarian / Phoenix | 1.0 | 2.0 | 2.5 | Recovery vs value trap |

**Combined weight formula:** (Fundamentals × W_fund) + (Context × W_context) + (Price × W_price)

These multipliers are tunable. If after running the system for a month something feels off, change the table — do not rewrite the logic.

---

## The weekly cycle

### Weekend (Saturday / Sunday) — Build the Weekly Pool

1. Apply Friday-close MoS filter to the full universe. Drop any card not undervalued at Friday's close.
2. Claude assesses context for each surviving card. Web search for material news, sector cycle, macro fit. Assign Context score (0–10) and one-sentence reason. Mark any AVOID cards (score 0).
3. Calculate combined weight for each card using its strategy's multipliers.
4. Rank all cards across all strategies in one combined list.
5. Take the top ~30 cards as the Weekly Pool. (Number is a target, not a rule — could be 25 or 35 depending on what the market is offering.)
6. Flipper reviews and approves. Edit context notes, block individual cards, accept the rest. Approximately 15–20 minutes.

### Each weekday morning — Daily pick

1. Refresh live price for the approved cards.
2. Recalculate Price score based on today's MoS. Drop cards that are no longer undervalued.
3. Apply vetos in order:
   - No two cards from the same strategy on the same day
   - No same strategy two days in a row (soft preference, can break if needed)
   - No card shown in the last 14 days (cooldown)
   - No two cards from the same sector on the same day (strict, since only 2 cards per day)
4. Weighted random draw: pick 1 FREE card (King or Jack) and 1 PRO card (Queen, Ace, Joker, or Two). Weights based on combined weight × cooldown factor.
5. Display to user.

### Mid-week override (rare)

If material news breaks for a card in the active pool, Flipper can manually block it through the admin page. The picker will skip it from that point forward until the next weekly review.

---

## Why this design

- **Three independent scores, not one black box.** Every pick is explainable: we can show the user the three numbers and a one-line context note.
- **Weekly editorial review before publication.** No card reaches a user without Flipper having seen it on Sunday.
- **Weighted random, not deterministic.** Best card has highest probability of being picked, but not 100%. Gives variety without sacrificing quality.
- **Flexible strategy mix.** No fixed pairs by day of week. The picker shows the genuinely best opportunities, which means the strategy mix shifts week to week with what the market offers.
- **Each strategy has a distinct personality.** The weight table ensures Jack picks behave like Jack picks (momentum), Two picks behave like Two picks (contrarian deep value), etc. — no homogenisation across strategies.
- **The methodology is the product.** This pipeline is the competitive advantage. Other apps run automated screens. ValuJack adds human + AI editorial review with a transparent, defensible scoring system.

---

## Things this methodology deliberately does NOT do

- Does not chase intraday news (weekly context is enough for value/quality investing).
- Does not force every strategy to deal cards every week.
- Does not hide reasoning from the user (context note is visible).
- Does not auto-publish without weekend review.

---

## Glossary

- **MoS (Margin of Safety)** = (Fair Value − Current Price) / Fair Value × 100. Positive means undervalued.
- **Veto** = a hard rule that overrides the weighted random pick.
- **Cooldown** = a time window during which a recently-shown card is excluded.
- **Weekly Pool** = the ~30 cards approved on Sunday, from which the daily picker draws all week.
