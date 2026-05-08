import csv
import re
from datetime import datetime

# Load all CSV data
csv_files = {
    'Company data/kings 2026-04-06.csv': 'KING',
    'Company data/jacks 2026-04-06.csv': 'JACK', 
    'Company data/queens 2026-04-06.csv': 'QUEEN',
    'Company data/aces 2026-04-06.csv': 'ACE',
    'Company data/jokers 2026-04-06.csv': 'JOKER',
    'Company data/twos 2026-04-06.csv': 'TWO'
}

ticker_data = {}

for filepath, strategy in csv_files.items():
    try:
        with open(filepath, 'r', encoding='iso-8859-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                ticker = row.get('Info - Ticker', '').strip()
                if ticker:
                    ticker_data[ticker] = {
                        'div': row.get('Div. Yield - Current', '').strip().replace(',', '.'),
                        'eps': row.get('Earnings g. - Growth 5y', '').strip() or row.get('Earnings g. - Growth 3y', '').strip(),
                        'rev': row.get('Revenue g. - Growth 5y', '').strip(),
                        'strategy': strategy
                    }
                    ticker_data[ticker]['eps'] = ticker_data[ticker]['eps'].replace(',', '.')
                    ticker_data[ticker]['rev'] = ticker_data[ticker]['rev'].replace(',', '.')
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

print(f"Loaded {len(ticker_data)} tickers\n")

# Read cards.js
with open('public/cards.js', 'r') as f:
    lines = f.readlines()
    content = ''.join(lines)

# Backup
backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

stats = {'eps': 0, 'rev': 0, 'div': 0}

# Process line by line for cards 319-709
new_lines = []
for i, line in enumerate(lines):
    new_line = line
    
    # Check if this line contains a ticker
    ticker_match = re.search(r"ticker: '([^']+)'", line)
    if ticker_match:
        ticker = ticker_match.group(1)
        
        if ticker in ticker_data:
            data = ticker_data[ticker]
            
            # Update epsGrowth if it's '—'
            if "epsGrowth: '—'" in line and data['eps']:
                try:
                    val = float(data['eps'])
                    if val != 0:
                        sign = '+' if val > 0 else ''
                        new_line = line.replace("epsGrowth: '—'", f"epsGrowth: '{sign}{int(val)}%'")
                        stats['eps'] += 1
                except:
                    pass
            
            # Update revGrowth if it's '—'
            if "revGrowth: '—'" in line and data['rev']:
                try:
                    val = float(data['rev'])
                    if val != 0:
                        sign = '+' if val > 0 else ''
                        new_line = new_line.replace("revGrowth: '—'", f"revGrowth: '{sign}{int(val)}%'")
                        stats['rev'] += 1
                except:
                    pass
    
    new_lines.append(new_line)

# Join back
content = ''.join(new_lines)

# Add dividend yields to KING metrics (separate pass)
for ticker, data in ticker_data.items():
    if data['strategy'] == 'KING' and data['div']:
        try:
            val = float(data['div'])
            if val > 0:
                # Find pattern: KING card with this ticker that has metrics ending with D/E
                pattern = rf"type: 'KING'.*?ticker: '{re.escape(ticker)}'.*?metrics: \[([^\]]+{{ l: 'D/E', v: '[^']+' }})\]"
                matches = list(re.finditer(pattern, content, re.DOTALL))
                
                for match in matches:
                    if 'Div. Yield' not in match.group(1):
                        old_metrics = match.group(0)
                        # Add div yield before closing ]
                        new_metrics = old_metrics.replace('}]', f"}}, {{ l: 'Div. Yield', v: '{val:.1f}%' }}]")
                        content = content.replace(old_metrics, new_metrics, 1)
                        stats['div'] += 1
                        if stats['div'] <= 10:
                            print(f"  {ticker}: +Div {val:.1f}%")
        except:
            pass

print(f"\n=== SUMMARY ===")
print(f"EPS Growth: {stats['eps']}")
print(f"Rev Growth: {stats['rev']}")  
print(f"Div Yield: {stats['div']}")
print(f"\nBackup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

