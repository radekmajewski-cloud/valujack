import csv
import re
from datetime import datetime

# Load dividend data
king_data = {}
with open('Company data/kings 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        ticker = row.get('Info - Ticker', '').strip()
        if ticker:
            div = row.get('Div. Yield - Current', '').replace(',', '.').replace('%', '').strip()
            if div:
                try:
                    king_data[ticker] = f"{float(div):.1f}%"
                except:
                    pass

print(f"Loaded {len(king_data)} KING dividends\n")

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# Process all KING cards in one pass
def replace_dividend(match):
    global updated
    ticker = match.group(1)
    if ticker in king_data:
        updated += 1
        if updated <= 20:
            print(f"  {ticker}: {king_data[ticker]}")
        return f"type: 'KING'.*?ticker: '{ticker}'.*?{{ l: 'Dividend Yield', v: '{king_data[ticker]}' }}"
    return match.group(0)

# Replace pattern
content = re.sub(
    r"type: 'KING'.*?ticker: '([^']+)'.*?{ l: 'Dividend Yield', v: '—' }",
    replace_dividend,
    content,
    flags=re.DOTALL
)

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

