import csv
import re
from datetime import datetime

# Get data for GTM and MXHN
two_data = {}
for csv_file in ['Company data/twos 2026-04-06.csv', 'Company data/twos extra.csv']:
    with open(csv_file, 'r', encoding='iso-8859-1') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            ticker = row.get('Info - Ticker', '').strip()
            if ticker in ['GTM', 'MXHN']:
                two_data[ticker] = {
                    'roic': row.get('ROIC - Current', '').replace(',', '.').replace('%', '').strip(),
                    'perf': row.get('Performance - Perform. 1m', '').replace(',', '.').replace('%', '').strip()
                }

print(f"Found data for: {', '.join(two_data.keys())}\n")

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# Find cards with these tickers
for ticker in two_data.keys():
    # Find card with this ticker
    card_match = re.search(rf"(ticker: '{ticker}'.*?)(metrics: \[[^\]]+\])", content, re.DOTALL)
    
    if card_match and '—' in card_match.group(2):
        d = two_data[ticker]
        
        roic = f"{float(d['roic']):.1f}%" if d['roic'] else '—'
        perf = f"{float(d['perf']):.1f}%" if d['perf'] else '—'
        
        # Get existing P/E and D/E
        old_metrics = card_match.group(2)
        pe_match = re.search(r"{ l: 'P/E', v: '([^']+)' }", old_metrics)
        de_match = re.search(r"{ l: 'Debt/Equity', v: '([^']+)' }", old_metrics)
        
        pe = pe_match.group(1) if pe_match else '—'
        de = de_match.group(1) if de_match else '—'
        
        new_metrics = f"metrics: [{{ l: 'Return on Capital', v: '{roic}' }}, {{ l: 'P/E', v: '{pe}' }}, {{ l: '1m Performance', v: '{perf}' }}, {{ l: 'Debt/Equity', v: '{de}' }}]"
        
        old_full = card_match.group(0)
        new_full = card_match.group(1) + new_metrics
        
        content = content.replace(old_full, new_full, 1)
        updated += 1
        print(f"  {ticker}: Updated (ROIC={roic}, 1m Perf={perf})")

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

