import csv
import re
from datetime import datetime

# Load JOKER 2 CSV
joker_data = {}
with open('Company data/Joker 2_2026-03-19.csv', 'r', encoding='iso-8859-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        ticker = row.get('Info - Ticker', '').strip()
        if ticker:
            joker_data[ticker] = {
                'eps': row.get('Earnings g. - Growth 5y', '').replace(',', '.').replace('%', '').strip(),
                'perf': row.get('Performance - Perform. 1y', '').replace(',', '.').replace('%', '').strip(),
                'roic': row.get('ROIC - Average 5y', '') or row.get('ROIC - Current', ''),
                'fcf': row.get('FCF margin - Current', '').replace(',', '.').replace('%', '').strip()
            }
            joker_data[ticker]['roic'] = joker_data[ticker]['roic'].replace(',', '.').replace('%', '').strip()

print(f"Loaded {len(joker_data)} JOKER companies from Joker 2 CSV\n")

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# Cards 237-247
for card_id in [237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247]:
    # Find ticker
    ticker_match = re.search(rf"id: {card_id},.*?ticker: '([^']+)'", content, re.DOTALL)
    if not ticker_match:
        continue
    
    ticker = ticker_match.group(1)
    
    if ticker not in joker_data:
        print(f"  Card {card_id} ({ticker}): No data in CSV")
        continue
    
    # Find and replace old metrics pattern
    old_pattern = rf"(id: {card_id},.*?)(metrics: \[{{ l: 'P/E'[^\]]+\]\])"
    
    match = re.search(old_pattern, content, re.DOTALL)
    if match:
        d = joker_data[ticker]
        
        def fmt(v):
            if not v: return '—'
            try:
                val = float(v)
                sign = '+' if val > 0 else ''
                return f"{sign}{int(val)}%"
            except:
                return '—'
        
        new_metrics = f"metrics: [{{ l: 'EPS Growth', v: '{fmt(d['eps'])}' }}, {{ l: 'Price Strength', v: '{fmt(d['perf'])}' }}, {{ l: 'Return on Capital', v: '{fmt(d['roic'])}' }}, {{ l: 'Free Cash', v: '{fmt(d['fcf'])}' }}]"
        
        content = content.replace(match.group(2), new_metrics, 1)
        updated += 1
        print(f"  Card {card_id} ({ticker}): Fixed")

print(f"\n=== SUMMARY ===")
print(f"Updated {updated} cards")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

