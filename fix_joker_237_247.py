import csv
import re
from datetime import datetime

# Load JOKER CSV data
joker_data = {}
try:
    with open('Company data/jokers 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            ticker = row.get('Info - Ticker', '').strip()
            if ticker:
                joker_data[ticker] = {
                    'eps': row.get('Earnings g. - Growth 5y', '').replace(',', '.').replace('%', '').strip(),
                    'perf': row.get('Performance - Perform. 1y', '').replace(',', '.').replace('%', '').strip(),
                    'roic': row.get('ROIC - Average 5y', '') or row.get('ROIC - Current', ''),
                    'fcf': row.get('FCF margin - Current', '').replace(',', '.').replace('%', '').strip()
                }
                joker_data[ticker]['roic'] = joker_data[ticker]['roic'].replace(',', '.').replace('%', '').strip()
except Exception as e:
    print(f"Error loading CSV: {e}")

print(f"Loaded data for {len(joker_data)} JOKER companies\n")

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

for card_id in range(237, 248):
    # Find the card and its old metrics
    card_match = re.search(
        r"({ id: " + str(card_id) + r", type: 'JOKER'.*?ticker: '([^']+)'.*?)(metrics: \[[^\]]+\])",
        content, re.DOTALL
    )
    
    if card_match:
        ticker = card_match.group(2)
        old_metrics_full = card_match.group(3)
        
        # Only update if it has old format
        if "P/E" in old_metrics_full or "FCF Yield" in old_metrics_full:
            if ticker in joker_data:
                d = joker_data[ticker]
                
                def fmt_pct(v):
                    if not v: return '—'
                    try:
                        val = float(v)
                        sign = '+' if val > 0 else ''
                        return f"{sign}{int(val)}%"
                    except:
                        return '—'
                
                eps = fmt_pct(d['eps'])
                perf = fmt_pct(d['perf'])
                roic = fmt_pct(d['roic'])
                fcf = fmt_pct(d['fcf'])
                
                new_metrics = f"metrics: [{{ l: 'EPS Growth', v: '{eps}' }}, {{ l: 'Price Strength', v: '{perf}' }}, {{ l: 'Return on Capital', v: '{roic}' }}, {{ l: 'Free Cash', v: '{fcf}' }}]"
                
                # Replace
                old_full = card_match.group(0)
                new_full = card_match.group(1) + new_metrics
                
                content = content.replace(old_full, new_full, 1)
                updated += 1
                print(f"  Card {card_id} ({ticker}): Updated")

print(f"\n=== SUMMARY ===")
print(f"Updated {updated} JOKER cards")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

