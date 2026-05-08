import csv
import re
from datetime import datetime

# Load KING CSV dividend data
king_data = {}
with open('Company data/kings 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        ticker = row.get('Info - Ticker', '').strip()
        if ticker:
            div = row.get('Div. Yield - Current', '').replace(',', '.').replace('%', '').strip()
            king_data[ticker] = div

print(f"Loaded {len(king_data)} KING companies\n")

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# Find all KING cards with missing dividend yield
for card_id in range(1, 710):
    match = re.search(
        rf"({{ id: {card_id}, type: 'KING'.*?ticker: '([^']+)'.*?)(metrics: \[{{ l: 'Dividend Yield', v: '—'[^\]]+\])",
        content, re.DOTALL
    )
    
    if match:
        ticker = match.group(2)
        old_metrics = match.group(3)
        
        if ticker in king_data:
            div_value = king_data[ticker]
            
            try:
                div_pct = f"{float(div_value):.1f}%"
            except:
                div_pct = '—'
            
            # Replace the dividend yield value in metrics
            new_metrics = old_metrics.replace("{ l: 'Dividend Yield', v: '—' }", f"{{ l: 'Dividend Yield', v: '{div_pct}' }}")
            
            old_full = match.group(0)
            new_full = match.group(1) + new_metrics
            
            content = content.replace(old_full, new_full, 1)
            updated += 1
            
            if updated <= 20:
                print(f"  Card {card_id} ({ticker}): Dividend = {div_pct}")

print(f"\n=== SUMMARY ===")
print(f"Updated {updated} KING cards")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

