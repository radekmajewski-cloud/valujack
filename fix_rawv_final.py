import csv
import re

print("🔧 Fixing rawV in scores arrays with actual data")
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
shutil.copy('public/cards.js', 'public/cards.js.bak_before_rawv_final')
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
    
    # Fix Low Debt rawV in KING cards
    if de_ratio and "raw: 'Low Debt'" in new_card:
        old_pattern = r"(raw: 'Low Debt', rawV: ')([^']+)(')"
        replacement = r"\g<1>" + de_ratio + r"\g<3>"
        new_card = re.sub(old_pattern, replacement, new_card)
        if new_card != card_chunk:
            changes.append(f'Low Debt rawV={de_ratio}')
    
    # Fix Momentum rawV in JOKER/JACK cards
    if rs_rank and "raw: 'Momentum'" in new_card:
        old_pattern = r"(raw: 'Momentum', rawV: ')([^']+)(')"
        replacement = r"\g<1>" + rs_rank + r"\g<3>"
        new_card = re.sub(old_pattern, replacement, new_card)
        if new_card != card_chunk:
            changes.append(f'Momentum rawV={rs_rank}')
    
    if changes:
        content = content.replace(card_chunk, new_card)
        fixed += 1
        print(f"✅ {ticker:15} | {', '.join(changes)}")

with open('public/cards.js', 'w') as f:
    f.write(content)

print(f"\n{'='*80}")
print(f"✅ Fixed {fixed} cards")
