# ValuJack Scoring Pipeline

A Python script that reads screener CSV exports, scores all companies across
all five strategies, assigns each company to its best-fit strategy, calls
the Claude API for contextual AI scores, and outputs a ready-to-review JSON
plus an optional patched `index.html`.

---

## Requirements

```bash
pip install pandas anthropic
```

---

## Weekly Workflow

### Step 1 — Take a backup
```bash
cp /Users/radekmajewski/Downloads/ValuJack/public/index.html \
   /Users/radekmajewski/Downloads/ValuJack/public/index_backup_$(date +%Y%m%d).html
```

### Step 2 — Export fresh screener CSVs
Export the five strategy screeners as CSV files. Put them in a folder, e.g. `~/valujack_data/`.

### Step 3 — Run the scorer (dry run first — no API cost)
```bash
python3 valujack_scorer.py \
  --kings   ~/valujack_data/Kings_2026-03-19.csv \
  --jacks   ~/valujack_data/Jacks_2026-03-19.csv \
  --queens  ~/valujack_data/Queens_2026-03-19.csv \
  --aces    ~/valujack_data/Aces__2026-03-19.csv \
  --jokers  ~/valujack_data/Jokers_2026-03-19.csv \
  --dry-run \
  --output scores_dry.json
```

Review `scores_dry.json`. Check for outliers or anything surprising.

### Step 4 — Full run with AI scoring
```bash
python3 valujack_scorer.py \
  --kings   ~/valujack_data/Kings_2026-03-19.csv \
  --jacks   ~/valujack_data/Jacks_2026-03-19.csv \
  --queens  ~/valujack_data/Queens_2026-03-19.csv \
  --aces    ~/valujack_data/Aces__2026-03-19.csv \
  --jokers  ~/valujack_data/Jokers_2026-03-19.csv \
  --api-key YOUR_ANTHROPIC_API_KEY \
  --index   /Users/radekmajewski/Downloads/ValuJack/public/index.html \
  --output  scores_$(date +%Y%m%d).json
```

This will:
1. Score all 235+ companies across all 5 strategies
2. Assign each company to its best strategy (one company, one card)
3. Call Claude API for contextual AI scores (skips companies below 35 data score)
4. Save full results to `scores_YYYYMMDD.json`
5. Produce `index_scored.html` — a patched version of your index.html

### Step 5 — Review and deploy
```bash
# Review the patched file
diff /Users/radekmajewski/Downloads/ValuJack/public/index.html index_scored.html

# If happy, copy to public folder
cp index_scored.html /Users/radekmajewski/Downloads/ValuJack/public/index.html

# Deploy
cd /Users/radekmajewski/Downloads/ValuJack
vercel --prod
```

---

## How Scoring Works

### Data Score (75–95% depending on strategy)

Each strategy scores companies on its core metrics:

| Metric            | KING | JACK | QUEEN | ACE | JOKER |
|-------------------|------|------|-------|-----|-------|
| Fair Price / MoS  | 20%  | 15%  | 20%   | 15% | 10%   |
| Dividend Health   | 25%  | —    | 5%    | 5%  | —     |
| Business Quality  | 15%  | 20%  | 25%   | 15% | 20%   |
| Growth            | 5%   | 25%  | 10%   | 10% | 35%   |
| Momentum          | —    | 20%  | 10%   | 10% | 20%   |
| Earnings Stability| 10%  | 5%   | 10%   | 20% | 5%    |
| Financial Health  | 10%  | —    | 10%   | 20% | —     |

### AI Score (5–25% depending on strategy)

JACK and JOKER weight AI highest (25% and 20%) because momentum and growth
judgment requires current context that pure financials miss.

The AI component focuses on:
- **KING**: dividend sustainability and income compounding quality
- **JACK**: momentum strength and earnings acceleration catalyst
- **QUEEN**: business moat, pricing power, and competitive advantage
- **ACE**: balance sheet strength and improving fundamentals trajectory
- **JOKER**: growth runway, market leadership, and momentum sustainability

### Veto Rules

| Veto | Trigger | Result |
|------|---------|--------|
| Dead Momentum | RS Rank < 50 AND price in bottom 25% of 52wk range | Score capped at 45 |
| Extreme Overvaluation | Price > 130% of fair value | Fair score = 0, max 55 |

### Star Ratings

| Stars | Score | Label |
|-------|-------|-------|
| ★★★★★ | 85–100 | Exceptional |
| ★★★★☆ | 70–84  | Strong |
| ★★★☆☆ | 55–69  | Good |
| ★★☆☆☆ | 40–54  | Watchlist |
| ★☆☆☆☆ | <40    | Not shown |

Only companies scoring ≥ 55 (★★★☆☆+) appear in the active rotation.

---

## Output JSON Structure

```json
{
  "generated": "2026-03-21T...",
  "total_scored": 235,
  "eligible_for_rotation": 172,
  "companies": [
    {
      "ticker": "EVO",
      "company": "Evolution",
      "strategy": "KING",
      "final_score": 90.4,
      "data_score": 85.6,
      "ai_score": 78.0,
      "stars": 5,
      "veto": null,
      "all_scores": {
        "KING": 90.4,
        "JACK": 61.2,
        "QUEEN": 74.1,
        "ACE": 68.3,
        "JOKER": 42.1
      },
      "components": {
        "fair_value": 95.0,
        "dividend_health": 88.0,
        "business_quality": 91.0,
        "growth": 72.0,
        "earnings_stability": 100.0,
        "financial_health": 85.0
      },
      "ai_reasoning": "Evolution has dominant market position..."
    }
  ]
}
```

---

## Calibration Notes

After the first full run, compare scores against your existing card ratings.
If any well-known cards score unexpectedly low or high, adjust the metric
thresholds in the scoring functions at the top of `valujack_scorer.py`.

Key thresholds to tune:
- `score_fair_value()` — MoS breakpoints
- `score_roic()` — what counts as "excellent" ROIC
- `score_growth()` — target growth rates per strategy
- `score_dividend_health()` — yield sweet spot range

---

## File Naming Convention

Keep dated copies of both CSVs and score JSONs for trend tracking:
```
Kings_2026-03-19.csv
scores_20260319.json
scores_20260326.json   ← next week
```

This lets you track score changes week-over-week and catch outliers.
