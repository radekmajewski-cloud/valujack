import csv
import re
from datetime import datetime

# Load CSV data
csv_data = {}
for csv_file in ['Company data/twos 2026-04-06.csv', 'Company data/twos extra.csv']:
    try:
        with open(csv_file, 'r', encoding='iso-8859-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                ticker = row.get('Info - Ticker', '').strip()
                if ticker and ticker not in csv_data:
                    csv_data[ticker] = {
                        'roic': row.get('ROIC - Current', '').replace(',', '.').replace('%', '').strip(),
                        'pe': row.get('P/E - Current', '').replace(',', '.').strip(),
                        'de': row.get('Debt-Equity - Current', '').replace(',', '.').strip(),
                        'perf_1m': row.get('Performance - Perform. 1m', '').replace(',', '.').replace('%', '').strip()
                    }
    except:
        pass

print(f"Loaded {len(csv_data)} companies\n")

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# For each TWO card (249-289), find and replace metrics
for card_id in range(249, 290):
    # Match the specific card and its metrics
    pattern = rf"({{ id: {card_id}, type: 'TWO'.*?ticker: '([^']+)'.*?)(metrics: \[[^\]]+\])"
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        ticker = match.group(2)
        old_metrics = match.group(3)
        
        if ticker in csv_data:
            d = csv_data[ticker]
            
            try:
                roic = f"{float(d['roic']):.1f}%" if d['roic'] else '—'
                pe = f"{float(d['pe']):.1f}" if d['pe'] else '—'
                perf = f"{float(d['perf_1m']):.1f}%" if d['perf_1m'] else '—'
                de = f"{float(d['de']):.1f}" if d['de'] else '—'
            except:
                continue
            
            new_metrics = f"metrics: [{{ l: 'ROIC', v: '{roic}' }}, {{ l: 'P/E', v: '{pe}' }}, {{ l: '1m Performance', v: '{perf}' }}, {{ l: 'Debt/Equity', v: '{de}' }}]"
            
            # Replace just the metrics part
            content = content.replace(old_metrics, new_metrics, 1)
            updated += 1
            
            if updated <= 10:
                print(f"  Card {card_id} ({ticker}): Updated")

print(f"\n=== SUMMARY ===")
print(f"Updated {updated} TWO card metrics")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

