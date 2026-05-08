import csv
import re
from datetime import datetime

# Load CSV data to get the actual values
csv_data = {}
for strategy_file in ['kings', 'jacks', 'queens', 'aces', 'jokers', 'twos']:
    try:
        with open(f'Company data/{strategy_file} 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                ticker = row.get('Info - Ticker', '').strip()
                if ticker:
                    csv_data[ticker] = {
                        'fscore': row.get('F-Score - Point', '').strip(),
                        'perf_1y': row.get('Performance - Perform. 1y', '').replace(',', '.').replace('%', '').strip(),
                        'eps': row.get('Earnings g. - Growth 5y', '') or row.get('Earnings g. - Growth 3y', ''),
                        'roic': row.get('ROIC - Average 5y', '') or row.get('ROIC - Average 3y', '') or row.get('ROIC - Current', ''),
                        'div': row.get('Div. Yield - Current', '').strip()
                    }
    except:
        pass

print(f"Loaded CSV data for {len(csv_data)} companies\n")

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# Process cards 319-709
for card_id in range(319, 710):
    match = re.search(
        rf"({{ id: {card_id}, type: '(\w+)',.*?ticker: '([^']+)',.*?fairValue: ([^,]+),.*?)"
        rf"(ind1l: '[^']+', ind1v: '[^']+', ind2l: '[^']+', ind2v: '[^']+')",
        content, re.DOTALL
    )
    
    if match:
        strategy = match.group(2)
        ticker = match.group(3)
        fair_value = match.group(4)
        old_indicators = match.group(5)
        
        # Calculate undervalued % (will be filled by live price in frontend)
        # For now use placeholder
        undervalued = '—'
        
        new_indicators = None
        
        if ticker in csv_data:
            d = csv_data[ticker]
            
            def clean_pct(v):
                if not v: return '—'
                v = v.replace(',', '.').replace('%', '').strip()
                try:
                    val = float(v)
                    sign = '+' if val > 0 else ''
                    return f"{sign}{int(val)}%"
                except:
                    return '—'
            
            if strategy == 'KING':
                div = clean_pct(d['div'])
                new_indicators = f"ind1l: 'DIVIDEND %', ind1v: '{div}', ind2l: 'UNDERVALUED BY', ind2v: '{undervalued}'"
            
            elif strategy == 'JACK':
                perf = clean_pct(d['perf_1y'])
                eps = clean_pct(d['eps'])
                new_indicators = f"ind1l: 'PRICE STRENGTH', ind1v: '{perf}', ind2l: 'EPS GROWTH', ind2v: '{eps}'"
            
            elif strategy == 'QUEEN':
                roic = clean_pct(d['roic'])
                new_indicators = f"ind1l: 'ROIC', ind1v: '{roic}', ind2l: 'UNDERVALUED BY', ind2v: '{undervalued}'"
            
            elif strategy == 'ACE':
                fscore = d['fscore'] or '—'
                new_indicators = f"ind1l: 'F-SCORE', ind1v: '{fscore}', ind2l: 'UNDERVALUED BY', ind2v: '{undervalued}'"
            
            elif strategy == 'JOKER':
                eps = clean_pct(d['eps'])
                perf = clean_pct(d['perf_1y'])
                new_indicators = f"ind1l: 'EPS GROWTH', ind1v: '{eps}', ind2l: 'PRICE STRENGTH', ind2v: '{perf}'"
            
            elif strategy == 'TWO':
                roic = clean_pct(d['roic'])
                new_indicators = f"ind1l: 'ROIC', ind1v: '{roic}', ind2l: 'UNDERVALUED BY', ind2v: '{undervalued}'"
        
        if new_indicators:
            old_full = match.group(0)
            new_full = old_full.replace(old_indicators, new_indicators)
            content = content.replace(old_full, new_full, 1)
            updated += 1
            
            if updated <= 10:
                print(f"  Card {card_id} ({strategy}/{ticker}): Updated")

print(f"\n=== SUMMARY ===")
print(f"Updated {updated} card indicators")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

