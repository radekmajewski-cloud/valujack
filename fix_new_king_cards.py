import csv
import re
from datetime import datetime

# Load ALL KING dividends from CSV
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

print(f"Loaded {len(king_divs)} KING dividends\n")

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# Process cards by ID - only cards 319+ (new cards)
for card_id in range(319, 710):
    # Find KING card with missing dividend
    pattern = rf"({{ id: {card_id}, type: 'KING'.*?ticker: '([^']+)'.*?ind1l: 'DIVIDEND YIELD', ind1v: ')([^']*?)(', ind2l:.*?{{ l: 'Dividend Yield', v: ')([^']*?)(' }})"
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        ticker = match.group(2)
        ind1v_val = match.group(3)
        metrics_val = match.group(5)
        
        # Check if either has —
        if (ind1v_val == '—' or metrics_val == '—') and ticker in king_divs:
            div_value = king_divs[ticker]
            new_text = match.group(1) + div_value + match.group(4) + div_value + match.group(6)
            content = content.replace(match.group(0), new_text, 1)
            updated += 1
            
            if updated <= 20:
                print(f"  Card {card_id} ({ticker}): {div_value}")

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

