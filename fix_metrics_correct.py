import csv
import re

print("🔧 Adding missing D/E and RS Rating - FIXED version")
print("="*80)

# Load screener
screener = {}
with open('Company data/All_company_data_2026-04-18.csv', 'r') as f:
    reader = csv.DictReader(f, delimiter=',')
    for row in reader:
        ticker = row.get('Info - Ticker', '').strip()
        if ticker:
            screener[ticker] = row

print(f"✅ Loaded {len(screener)} companies\n")

with open('public/cards.js', 'r') as f:
    content = f.read()

# Backup
import shutil
shutil.copy('public/cards.js', 'public/cards.js.bak_before_metrics_fix_correct')
print("✅ Backup created\n")

fixed = 0
cards = re.split(r'(?=\{ id:)', content)

for card_chunk in cards:
    ticker_match = re.search(r"ticker: '([^']+)'", card_chunk)
    if not ticker_match:
        continue
    
    ticker = ticker_match.group(1)
    if ticker not in screener:
        continue
    
    data = screener[ticker]
    de_ratio = data.get('Debt-Equity - Current', '').replace(',', '.').strip()
    rs_rank = data.get('RS Rank - L - 0-100', '').replace(',', '.').strip()
    
    new_card = card_chunk
    changes = []
    
    # Add D/E to KING cards - properly close previous metric
    if de_ratio and "type: 'KING'" in new_card and "D/E" not in new_card:
        metrics_match = re.search(r"(metrics: \[.*?)(}\])", new_card)
        if metrics_match:
            prefix = metrics_match.group(1)
            # Add closing brace for previous metric, then new D/E metric
            new_metrics = prefix + "}, { l: 'D/E', v: '" + de_ratio + "' }]"
            new_card = new_card.replace(metrics_match.group(0), new_metrics)
            changes.append('D/E=' + de_ratio)
    
    # Add rsRating field to JOKER/JACK cards
    if rs_rank and ("type: 'JOKER'" in new_card or "type: 'JACK'" in new_card) and "rsRating:" not in new_card:
        new_card = re.sub(
            r"(revGrowth: '[^']*',)",
            r"\1 rsRating: '" + rs_rank + "',",
            new_card
        )
        changes.append('RS=' + rs_rank)
    
    if changes:
        content = content.replace(card_chunk, new_card)
        fixed += 1
        print(f"✅ {ticker:15} | {', '.join(changes)}")

with open('public/cards.js', 'w') as f:
    f.write(content)

print(f"\n{'='*80}")
print(f"✅ Fixed {fixed} cards")
