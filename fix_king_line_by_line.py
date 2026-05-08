import csv
from datetime import datetime

# Load dividend data
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

print(f"Loaded {len(king_divs)} dividends\n")

with open('public/cards.js', 'r') as f:
    lines = f.readlines()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.writelines(lines)

updated = 0

# Track current card's ticker
current_ticker = None
for i, line in enumerate(lines):
    # Find ticker
    if "ticker: '" in line and "type: 'KING'" in lines[max(0, i-5):i+1] if i >= 5 else "type: 'KING'" in lines[:i+1]:
        # Extract ticker
        import re
        match = re.search(r"ticker: '([^']+)'", line)
        if match:
            current_ticker = match.group(1)
    
    # Replace dividend if we have data
    if current_ticker and current_ticker in king_divs:
        if "{ l: 'Dividend Yield', v: '—' }" in line:
            lines[i] = line.replace(
                "{ l: 'Dividend Yield', v: '—' }",
                f"{{ l: 'Dividend Yield', v: '{king_divs[current_ticker]}' }}"
            )
            updated += 1
            if updated <= 20:
                print(f"  Line {i}: {current_ticker} = {king_divs[current_ticker]}")
            current_ticker = None  # Reset to avoid double-update

print(f"\nUpdated {updated} lines")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.writelines(lines)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

