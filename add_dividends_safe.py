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

# Process each KING card individually by ID
for card_id in range(319, 710):
    pattern = rf"({{ id: {card_id}, type: 'KING'.*?ticker: '([^']+)'.*?metrics: \[)([^\]]+)(\])"
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        ticker = match.group(2)
        metrics = match.group(3)
        
        # Only add if ticker has dividend AND metrics doesn't already have it
        if ticker in div_data and 'Div. Yield' not in metrics:
            div_val = div_data[ticker]
            
            # Build new metrics - add to END before closing ]
            old_full = match.group(0)
            new_metrics = f"{match.group(1)}{metrics}, {{ l: 'Div. Yield', v: '{div_val:.1f}%' }}{match.group(4)}"
            
            content = content.replace(old_full, new_metrics, 1)
            added += 1
            if added <= 10:
                print(f"  Card {card_id} ({ticker}): {div_val:.1f}%")

print(f"\n=== SUMMARY ===")
print(f"Added {added} dividend yields")
print(f"Backup: {backup}")

# Write and validate
with open('public/cards.js', 'w') as f:
    f.write(content)

# Check syntax
import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True, text=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR - reverting")
    subprocess.run(['cp', backup, 'public/cards.js'])

