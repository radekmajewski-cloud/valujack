import csv
import re
from datetime import datetime

# Load dividend data
div_data = {}
with open('Company data/kings 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        ticker = row.get('Info - Ticker', '').strip()
        div = row.get('Div. Yield - Current', '').strip()
        if ticker and div:
            div_clean = div.replace(',', '.').replace('%', '')
            try:
                val = float(div_clean)
                if val > 0:
                    div_data[ticker] = val
            except:
                pass

print(f"Loaded {len(div_data)} KING dividends\n")

# Read cards
with open('public/cards.js', 'r') as f:
    content = f.read()

# Backup
backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

added = 0

# Find each card individually by ID (319-709)
for card_id in range(319, 710):
    # Match this specific card
    pattern = rf"{{ id: {card_id}, type: 'KING'.*?ticker: '([^']+)'.*?metrics: \[([^\]]+)\]"
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        ticker = match.group(1)
        metrics = match.group(2)
        
        if ticker in div_data and 'Div. Yield' not in metrics:
            div_val = div_data[ticker]
            old_metrics = f"metrics: [{metrics}]"
            new_metrics = f"metrics: [{metrics}, {{ l: 'Div. Yield', v: '{div_val:.1f}%' }}]"
            
            content = content.replace(old_metrics, new_metrics, 1)
            added += 1
            if added <= 10:
                print(f"  Card {card_id} ({ticker}): {div_val:.1f}%")

print(f"\n=== SUMMARY ===")
print(f"Added {added} dividend yields")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

print("✓ Done")

