import csv
import re
from datetime import datetime

# Load JACK data
jack_data = {}
with open('Company data/jacks 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        ticker = row.get('Info - Ticker', '').strip()
        if ticker:
            pe = row.get('P/E - Current', '').replace(',', '.').strip()
            fcf = row.get('FCF yield - Current', '').replace(',', '.').replace('%', '').strip()
            
            jack_data[ticker] = {
                'pe': pe if pe else '—',
                'fcf_yield': f"{float(fcf):.1f}%" if fcf else '—'
            }

print(f"Loaded {len(jack_data)} JACK companies\n")

# Converted tickers (now JACK but with wrong metrics)
converted = ['GPOR', 'HLMA', 'HOLX', 'INVA', 'KWS', 'LHX', 'LIK', 'LQDT', 'FII', 'MZX', 'NESR', 'NYT', 'NORAM', 'NVT', 'OET', '761', 'PLXS', 'POWL', 'PSMT', 'REX', 'RPRX', 'SAND', 'SAP', 'SIS', 'SENEA', 'SOFF', 'THR', 'TPZ', 'TIH', 'VAL', 'VLGEA', 'WAB', 'GRMN']

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

for ticker in converted:
    if ticker not in jack_data:
        continue
    
    # Find JACK card with this ticker that has F-Score
    pattern = rf"(type: 'JACK'.*?ticker: '{re.escape(ticker)}'.*?metrics: \[){{ l: 'F-Score', v: '[^']*' }}(, {{ l: 'Return on Capital'.*?{{ l: 'Free Cash', v: ')[^']*'( }})"
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        pe_val = jack_data[ticker]['pe']
        fcf_val = jack_data[ticker]['fcf_yield']
        
        # Replace F-Score with P/E and Free Cash with FCF Yield
        new_metrics = f"{match.group(1)}{{ l: 'P/E', v: '{pe_val}' }}{match.group(2)}{fcf_val}'{match.group(3)}"
        
        content = content.replace(match.group(0), new_metrics, 1)
        updated += 1
        
        if updated <= 20:
            print(f"  {ticker}: P/E={pe_val}, FCF Yield={fcf_val}")

print(f"\nUpdated {updated} JACK cards")
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

