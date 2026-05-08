import csv
import re
from datetime import datetime

# Load CSV data with all needed metrics
csv_data = {}
for strategy_file in ['kings', 'jacks', 'queens', 'aces', 'jokers', 'twos']:
    try:
        with open(f'Company data/{strategy_file} 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                ticker = row.get('Info - Ticker', '').strip()
                if ticker:
                    csv_data[ticker] = {
                        'pe': row.get('P/E - Current', '').strip(),
                        'roic': row.get('ROIC - Average 5y', '') or row.get('ROIC - Average 3y', '') or row.get('ROIC - Current', ''),
                        'de': row.get('Debt-Equity - Current', '').strip(),
                        'fcf_margin': row.get('FCF margin - Current', '') or row.get('FCF margin - Average 3y', ''),
                        'eps_growth': row.get('Earnings g. - Growth 5y', '') or row.get('Earnings g. - Growth 3y', ''),
                        'rev_growth': row.get('Revenue g. - Growth 5y', ''),
                        'div_yield': row.get('Div. Yield - Current', '').strip(),
                        'fscore': row.get('F-Score - Point', '').strip(),
                        'perf_1y': row.get('Performance - Perform. 1y', '').strip(),
                        'perf_1m': row.get('Performance - Perform. 1m', '').strip()
                    }
    except Exception as e:
        print(f"Error loading {strategy_file}: {e}")

print(f"Loaded data for {len(csv_data)} companies\n")

# Read cards
with open('public/cards.js', 'r') as f:
    content = f.read()

# Backup
backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# Process cards 319-709
for card_id in range(319, 710):
    match = re.search(
        rf"({{ id: {card_id}, type: '(\w+)',.*?ticker: '([^']+)',.*?)"
        rf"(metrics: \[[^\]]+\])",
        content, re.DOTALL
    )
    
    if match:
        strategy = match.group(2)
        ticker = match.group(3)
        old_metrics = match.group(4)
        
        if ticker in csv_data:
            data = csv_data[ticker]
            
            # Clean and format values
            def clean_val(v):
                if not v: return '—'
                v = v.replace(',', '.').replace('%', '').strip()
                try:
                    return str(round(float(v), 1)) + '%' if v else '—'
                except:
                    return v
            
            def clean_num(v):
                if not v: return '—'
                v = v.replace(',', '.').strip()
                try:
                    return str(round(float(v), 1))
                except:
                    return v
            
            # Build metrics based on strategy
            if strategy == 'KING':
                div = clean_val(data['div_yield'])
                roic = clean_val(data['roic'])
                pe = clean_num(data['pe'])
                de = clean_num(data['de'])
                new_metrics = f"metrics: [{{ l: 'Dividend Yield', v: '{div}' }}, {{ l: 'ROIC', v: '{roic}' }}, {{ l: 'P/E', v: '{pe}' }}, {{ l: 'Debt/Equity', v: '{de}' }}]"
            
            elif strategy == 'JACK':
                perf = clean_val(data['perf_1y'])
                eps = clean_val(data['eps_growth'])
                roic = clean_val(data['roic'])
                fcf = clean_val(data['fcf_margin'])
                new_metrics = f"metrics: [{{ l: 'Price Strength', v: '{perf}' }}, {{ l: 'EPS Growth', v: '{eps}' }}, {{ l: 'ROIC', v: '{roic}' }}, {{ l: 'Free Cash', v: '{fcf}' }}]"
            
            elif strategy == 'QUEEN':
                roic = clean_val(data['roic'])
                pe = clean_num(data['pe'])
                eps = clean_val(data['eps_growth'])
                de = clean_num(data['de'])
                new_metrics = f"metrics: [{{ l: 'ROIC', v: '{roic}' }}, {{ l: 'P/E', v: '{pe}' }}, {{ l: 'EPS Growth', v: '{eps}' }}, {{ l: 'Debt/Equity', v: '{de}' }}]"
            
            elif strategy == 'ACE':
                fscore = data['fscore'] or '—'
                roic = clean_val(data['roic'])
                fcf = clean_val(data['fcf_margin'])
                de = clean_num(data['de'])
                new_metrics = f"metrics: [{{ l: 'F-Score', v: '{fscore}' }}, {{ l: 'ROIC', v: '{roic}' }}, {{ l: 'Free Cash', v: '{fcf}' }}, {{ l: 'Debt/Equity', v: '{de}' }}]"
            
            elif strategy == 'JOKER':
                eps = clean_val(data['eps_growth'])
                perf = clean_val(data['perf_1y'])
                roic = clean_val(data['roic'])
                fcf = clean_val(data['fcf_margin'])
                new_metrics = f"metrics: [{{ l: 'EPS Growth', v: '{eps}' }}, {{ l: 'Price Strength', v: '{perf}' }}, {{ l: 'ROIC', v: '{roic}' }}, {{ l: 'Free Cash', v: '{fcf}' }}]"
            
            elif strategy == 'TWO':
                roic = clean_val(data['roic'])
                pe = clean_num(data['pe'])
                perf = clean_val(data['perf_1m'])
                de = clean_num(data['de'])
                new_metrics = f"metrics: [{{ l: 'ROIC', v: '{roic}' }}, {{ l: 'P/E', v: '{pe}' }}, {{ l: '1m Performance', v: '{perf}' }}, {{ l: 'Debt/Equity', v: '{de}' }}]"
            
            else:
                continue
            
            # Replace
            old_full = match.group(0)
            new_full = old_full.replace(old_metrics, new_metrics)
            content = content.replace(old_full, new_full, 1)
            updated += 1
            
            if updated <= 10:
                print(f"  {ticker} ({strategy}): Updated metrics")

print(f"\n=== SUMMARY ===")
print(f"Updated {updated} card metrics")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

