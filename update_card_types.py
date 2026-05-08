import csv
import re
from datetime import datetime

# Get JACK data from CSV
jack_data = {}
with open('Company data/jacks 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        ticker = row.get('Info - Ticker', '').strip()
        if ticker:
            jack_data[ticker] = {
                'eps_growth': row.get('Earnings g. - Y-Y Growth', '').replace(',', '.').replace('%', '').strip(),
                'roic': row.get('ROIC - Current', '').replace(',', '.').replace('%', '').strip(),
            }

print(f"Loaded {len(jack_data)} JACK companies\n")

# Misclassified tickers
misclassified = ['GPOR', 'HLMA', 'HOLX', 'INVA', 'KWS', 'LHX', 'LIK', 'LQDT', 'FII', 'MZX', 'NESR', 'NYT', 'NORAM', 'NVT', 'OET', '761', 'PLXS', 'POWL', 'PSMT', 'REX', 'RPRX', 'SAND', 'SAP', 'SIS', 'SENEA', 'SOFF', 'THR', 'TPZ', 'TIH', 'VAL', 'VLGEA', 'WAB', 'GRMN']

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# Find and update each misclassified card
for ticker in misclassified:
    # Find ACE card with this ticker
    pattern = rf"({{ id: \d+, )(type: 'ACE')(.*?ticker: '{re.escape(ticker)}')"
    
    matches = list(re.finditer(pattern, content, re.DOTALL))
    
    for match in matches:
        # Change type to JACK
        old_text = match.group(0)
        new_text = match.group(1) + "type: 'JACK'" + match.group(3)
        content = content.replace(old_text, new_text, 1)
        updated += 1
        
        if updated <= 20:
            print(f"  {ticker}: Changed ACE → JACK")

print(f"\n=== SUMMARY ===")
print(f"Changed {updated} cards from ACE to JACK")
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

