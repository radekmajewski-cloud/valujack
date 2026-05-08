import csv
import re
from datetime import datetime

# Load data from both TWO CSVs
csv_data = {}
for csv_file in ['Company data/twos 2026-04-06.csv', 'Company data/twos extra.csv']:
    try:
        with open(csv_file, 'r', encoding='iso-8859-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                ticker = row.get('Info - Ticker', '').strip()
                if ticker and ticker not in csv_data:  # Don't overwrite
                    csv_data[ticker] = {
                        'roic': row.get('ROIC - Current', '').strip(),
                        'pe': row.get('P/E - Current', '').strip(),
                        'de': row.get('Debt-Equity - Current', '').strip(),
                        'perf_1m': row.get('Performance - Perform. 1m', '').strip()
                    }
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")

print(f"Loaded data for {len(csv_data)} TWO companies\n")

# Read cards
with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0
not_found = []

# Process cards 249-289 (broken TWO cards)
for card_id in range(249, 290):
    match = re.search(
        rf"({{ id: {card_id},.*?ticker: '([^']+)',.*?)"
        rf"(metrics: \[[^\]]+\])",
        content, re.DOTALL
    )
    
    if match and '[value]' in match.group(0):
        ticker = match.group(2)
        old_metrics = match.group(3)
        
        if ticker in csv_data:
            data = csv_data[ticker]
            
            # Clean values
            def clean_val(v):
                if not v: return '—'
                v = v.replace(',', '.').replace('%', '').strip()
                try:
                    return str(round(float(v), 1)) + '%'
                except:
                    return '—'
            
            def clean_num(v):
                if not v: return '—'
                v = v.replace(',', '.').strip()
                try:
                    return str(round(float(v), 1))
                except:
                    return '—'
            
            roic = clean_val(data['roic'])
            pe = clean_num(data['pe'])
            perf = clean_val(data['perf_1m'])
            de = clean_num(data['de'])
            
            new_metrics = f"metrics: [{{ l: 'ROIC', v: '{roic}' }}, {{ l: 'P/E', v: '{pe}' }}, {{ l: '1m Performance', v: '{perf}' }}, {{ l: 'Debt/Equity', v: '{de}' }}]"
            
            # Replace
            old_full = match.group(0)
            new_full = old_full.replace(old_metrics, new_metrics)
            content = content.replace(old_full, new_full, 1)
            updated += 1
            
            if updated <= 10:
                print(f"  Card {card_id} ({ticker}): Fixed")
        else:
            not_found.append((card_id, ticker))

print(f"\n=== SUMMARY ===")
print(f"Updated: {updated} cards")
print(f"Not found in CSVs: {len(not_found)} cards")
if not_found:
    print("\nMissing tickers:")
    for card_id, ticker in not_found[:10]:
        print(f"  Card {card_id}: {ticker}")

print(f"\nBackup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

