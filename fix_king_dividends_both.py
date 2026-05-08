import csv
import re
from datetime import datetime

# Load KING CSV dividend data
king_divs = {}
with open('Company data/kings 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        ticker = row.get('Info - Ticker', '').strip()
        div = row.get('Div. Yield - Current', '').replace(',', '.').replace('%', '').strip()
        if ticker and div:
            try:
                king_divs[ticker] = f"{float(div):.1f}%"
            except:
                pass

print(f"Loaded {len(king_divs)} KING dividends from CSV\n")

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# For each ticker with dividend data, find and update the card
for ticker, div_value in king_divs.items():
    # Pattern: Find KING card with this ticker that has missing dividend
    pattern = rf"(type: 'KING'.*?ticker: '{ticker}'.*?ind1l: 'DIVIDEND YIELD', ind1v: ')(—|[^']*?)(', ind2l:.*?metrics: \[{{ l: 'Dividend Yield', v: ')(—|[^']*?)(' }})"
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        # Check if either ind1v or metrics has —
        ind1v_val = match.group(2)
        metrics_val = match.group(4)
        
        if ind1v_val == '—' or metrics_val == '—':
            # Replace both with the correct dividend
            new_text = match.group(1) + div_value + match.group(3) + div_value + match.group(5)
            content = content.replace(match.group(0), new_text, 1)
            updated += 1
            
            if updated <= 20:
                print(f"  {ticker}: {div_value} (was ind1v={ind1v_val}, metrics={metrics_val})")

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
    import shutil
    shutil.copy(backup, 'public/cards.js')
    print("✓ Auto-restored")

