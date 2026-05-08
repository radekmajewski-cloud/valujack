import csv
import re
from datetime import datetime

# Load specific tickers
target_tickers = ['BMY', 'BPF.UN', 'ENV', 'J0L', '74E', 'KN8', 'NYKA', 'OFH', 'ORI1']
king_divs = {}

with open('Company data/kings 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        ticker = row.get('Info - Ticker', '').strip()
        if ticker in target_tickers:
            div = row.get('Div. Yield - Current', '').replace(',', '.').replace('%', '').strip()
            try:
                king_divs[ticker] = f"{float(div):.1f}%"
            except:
                pass

print(f"Loaded {len(king_divs)} dividends\n")

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

for ticker, div_value in king_divs.items():
    # Escape special regex characters in ticker
    escaped_ticker = re.escape(ticker)
    
    pattern = rf"(type: 'KING'.*?ticker: '{escaped_ticker}'.*?ind1l: 'DIVIDEND YIELD', ind1v: ')([^']*?)(', ind2l:.*?metrics: \[{{ l: 'Dividend Yield', v: ')([^']*?)(' }})"
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        new_text = match.group(1) + div_value + match.group(3) + div_value + match.group(5)
        content = content.replace(match.group(0), new_text, 1)
        updated += 1
        print(f"  {ticker}: {div_value}")

print(f"\nUpdated {updated} cards")
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

