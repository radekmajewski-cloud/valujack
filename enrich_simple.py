import csv
import re
from datetime import datetime

# Load CSV data
ticker_data = {}
csv_files = {
    'Company data/kings 2026-04-06.csv': 'KING',
    'Company data/jacks 2026-04-06.csv': 'JACK',
    'Company data/queens 2026-04-06.csv': 'QUEEN',
    'Company data/aces 2026-04-06.csv': 'ACE',
    'Company data/jokers 2026-04-06.csv': 'JOKER',
    'Company data/twos 2026-04-06.csv': 'TWO'
}

for filepath, strategy in csv_files.items():
    try:
        with open(filepath, 'r', encoding='iso-8859-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                ticker = row.get('Info - Ticker', '').strip()
                if ticker:
                    ticker_data[ticker] = {
                        'div': row.get('Div. Yield - Current', '').strip(),
                        'eps': row.get('Earnings g. - Growth 5y', '').strip() or row.get('Earnings g. - Growth 3y', '').strip(),
                        'rev': row.get('Revenue g. - Growth 5y', '').strip(),
                        'strategy': strategy
                    }
    except:
        pass

print(f"Loaded {len(ticker_data)} tickers\n")

# Read cards.js
with open('public/cards.js', 'r') as f:
    content = f.read()

# Backup
backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

stats = {'eps': 0, 'rev': 0, 'div': 0}

# Process each ticker
for ticker, data in ticker_data.items():
    
    # Update EPS Growth
    if data['eps']:
        try:
            val = float(data['eps'].replace(',', '.'))
            if val != 0:
                sign = '+' if val > 0 else ''
                old = f"ticker: '{ticker}', country: "
                if old in content:
                    # Find the epsGrowth field after this ticker
                    start = content.find(old)
                    if start != -1:
                        # Find epsGrowth in next 200 chars
                        section = content[start:start+300]
                        eps_match = re.search(r"epsGrowth: '([^']*)'", section)
                        if eps_match and eps_match.group(1) in ['—', '']:
                            old_eps = f"epsGrowth: '{eps_match.group(1)}'"
                            new_eps = f"epsGrowth: '{sign}{int(val)}%'"
                            content = content.replace(old + section[:section.find(old_eps)+len(old_eps)], 
                                                     old + section[:section.find(old_eps)] + new_eps, 1)
                            stats['eps'] += 1
                            if stats['eps'] <= 5:
                                print(f"  {ticker}: EPS Growth = {sign}{int(val)}%")
        except:
            pass
    
    # Update Rev Growth
    if data['rev']:
        try:
            val = float(data['rev'].replace(',', '.'))
            if val != 0:
                sign = '+' if val > 0 else ''
                pattern = f"ticker: '{ticker}'.*?revGrowth: '—'"
                new_rev = f"revGrowth: '{sign}{int(val)}%'"
                if re.search(pattern, content, re.DOTALL):
                    content = re.sub(pattern, lambda m: m.group(0).replace("revGrowth: '—'", new_rev), content, count=1, flags=re.DOTALL)
                    stats['rev'] += 1
        except:
            pass
    
    # Add Div Yield for KING
    if data['strategy'] == 'KING' and data['div']:
        try:
            val = float(data['div'].replace(',', '.'))
            if val > 0:
                # Find this KING ticker
                pattern = f"type: 'KING'.*?ticker: '{ticker}'.*?metrics: \[([^\]]+)\]"
                match = re.search(pattern, content, re.DOTALL)
                if match and 'Div. Yield' not in match.group(1):
                    old_metrics = match.group(0)
                    new_metrics = old_metrics.replace(']', f", {{ l: 'Div. Yield', v: '{val:.1f}%' }}]")
                    content = content.replace(old_metrics, new_metrics, 1)
                    stats['div'] += 1
                    if stats['div'] <= 5:
                        print(f"  {ticker}: Div. Yield = {val:.1f}%")
        except:
            pass

print(f"\n=== SUMMARY ===")
print(f"EPS: {stats['eps']}, Rev: {stats['rev']}, Div: {stats['div']}")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

