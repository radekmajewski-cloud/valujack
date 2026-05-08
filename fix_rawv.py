import csv
import re

print("🔧 Fixing rawV fields in scores arrays...")
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

# Load cards.js
with open('public/cards.js', 'r') as f:
    content = f.read()

# Backup
import shutil
shutil.copy('public/cards.js', 'public/cards.js.bak_before_rawv_fix_v2')
print("✅ Backup created\n")

fixed = 0
all_tickers = list(set(re.findall(r"ticker: '([^']+)'", content)))

for ticker in all_tickers:
    if ticker not in screener:
        continue
    
    data = screener[ticker]
    de_ratio = data.get('Debt-Equity - Current', '').replace(',', '.').strip()
    rs_rank = data.get('RS Rank - L - 0-100', '').replace(',', '.').strip()
    
    card_pattern = f"ticker: '{ticker}'"
    card_start = content.find(card_pattern)
    if card_start == -1:
        continue
    
    card_end = content.find('}, ', card_start) + 2
    old_card = content[card_start:card_end]
    new_card = old_card
    
    changes = []
    
    if de_ratio and "raw: 'Low Debt'" in new_card:
        new_card = re.sub(
            r"(raw: 'Low Debt', rawV: ')(\d+/10)(')",
            f"\\1{de_ratio}\\3",
            new_card
        )
        if new_card != old_card:
            changes.append(f'D/E: {de_ratio}')
            old_card = new_card
    
    if rs_rank and "raw: 'Momentum'" in new_card:
        new_card = re.sub(
            r"(raw: 'Momentum', rawV: ')(\d+/10)(')",
            f"\\1{rs_rank}\\3",
            new_card
        )
        if new_card != old_card:
            changes.append(f'RS: {rs_rank}')
    
    if changes:
        content = content.replace(old_card, new_card)
        fixed += 1
        print(f"✅ {ticker:15} | {', '.join(changes)}")

with open('public/cards.js', 'w') as f:
    f.write(content)

print(f"\n{'='*80}")
print(f"✅ Fixed {fixed} cards with actual rawV values")
