import csv
import re
from datetime import datetime

# Load TWO CSV data
csv_data = {}
for csv_file in ['Company data/twos 2026-04-06.csv', 'Company data/twos extra.csv']:
    try:
        with open(csv_file, 'r', encoding='iso-8859-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                ticker = row.get('Info - Ticker', '').strip()
                if ticker and ticker not in csv_data:
                    csv_data[ticker] = {
                        'roic': row.get('ROIC - Current', '').strip(),
                        'pe': row.get('P/E - Current', '').strip(),
                        'de': row.get('Debt-Equity - Current', '').strip(),
                        'perf_1m': row.get('Performance - Perform. 1m', '').strip()
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

# Process each broken TWO card individually
for card_id in range(249, 290):
    # Find the entire card
    card_pattern = rf"({{ id: {card_id}, type: 'TWO'.*?ticker: '([^']+)'.*?)(metrics: \[[^\]]+\])(.*?}},)"
    
    match = re.search(card_pattern, content, re.DOTALL)
    if match and '[value]' in match.group(3):
        ticker = match.group(2)
        
        if ticker in csv_data:
            data = csv_data[ticker]
            
            def clean_pct(v):
                if not v: return '—'
                v = v.replace(',', '.').replace('%', '').strip()
                try:
                    return f"{round(float(v), 1)}%"
                except:
                    return '—'
            
            def clean_num(v):
                if not v: return '—'
                v = v.replace(',', '.').strip()
                try:
                    return str(round(float(v), 1))
                except:
                    return '—'
            
            new_metrics = f"metrics: [{{ l: 'ROIC', v: '{clean_pct(data['roic'])}' }}, {{ l: 'P/E', v: '{clean_num(data['pe'])}' }}, {{ l: '1m Performance', v: '{clean_pct(data['perf_1m'])}' }}, {{ l: 'Debt/Equity', v: '{clean_num(data['de'])}' }}]"
            
            # Replace the entire card
            old_card = match.group(0)
            new_card = match.group(1) + new_metrics + match.group(4)
            
            content = content.replace(old_card, new_card, 1)
            updated += 1
            
            if updated <= 10:
                print(f"  Card {card_id} ({ticker}): Fixed")

print(f"\n=== SUMMARY ===")
print(f"Updated {updated} cards")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR - reverting")
    import shutil
    shutil.copy(backup, 'public/cards.js')

