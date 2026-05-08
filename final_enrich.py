import csv
import re
from datetime import datetime

# Load CSV data
ticker_data = {}
for filepath, strategy in [
    ('Company data/kings 2026-04-06.csv', 'KING'),
    ('Company data/jacks 2026-04-06.csv', 'JACK'),
    ('Company data/queens 2026-04-06.csv', 'QUEEN'),
    ('Company data/aces 2026-04-06.csv', 'ACE'),
    ('Company data/jokers 2026-04-06.csv', 'JOKER'),
    ('Company data/twos 2026-04-06.csv', 'TWO')
]:
    try:
        with open(filepath, 'r', encoding='iso-8859-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                ticker = row.get('Info - Ticker', '').strip()
                if ticker:
                    eps = row.get('Earnings g. - Growth 5y', '').strip() or row.get('Earnings g. - Growth 3y', '').strip()
                    rev = row.get('Revenue g. - Growth 5y', '').strip()
                    div = row.get('Div. Yield - Current', '').strip()
                    
                    ticker_data[ticker] = {
                        'eps': eps.replace(',', '.') if eps else '',
                        'rev': rev.replace(',', '.') if rev else '',
                        'div': div.replace(',', '.') if div else '',
                        'strategy': strategy
                    }
    except:
        pass

print(f"Loaded {len(ticker_data)} tickers\n")

# Read cards
with open('public/cards.js', 'r') as f:
    content = f.read()

# Backup
backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

stats = {'eps': 0, 'rev': 0}

# Use substitution function
def replace_growth(match):
    ticker = match.group(1)
    country = match.group(2)
    currency = match.group(3)
    
    eps_val = '—'
    rev_val = '—'
    
    if ticker in ticker_data:
        data = ticker_data[ticker]
        
        if data['eps']:
            try:
                val = float(data['eps'])
                if val != 0:
                    sign = '+' if val > 0 else ''
                    eps_val = f"{sign}{int(val)}%"
                    stats['eps'] += 1
            except:
                pass
        
        if data['rev']:
            try:
                val = float(data['rev'])
                if val != 0:
                    sign = '+' if val > 0 else ''
                    rev_val = f"{sign}{int(val)}%"
                    stats['rev'] += 1
            except:
                pass
    
    return f"ticker: '{ticker}', country: '{country}', currency: '{currency}', epsGrowth: '{eps_val}', revGrowth: '{rev_val}'"

pattern = r"ticker: '([^']+)', country: '([^']*)', currency: '([^']*)', epsGrowth: '—', revGrowth: '—'"
content = re.sub(pattern, replace_growth, content)

print(f"=== SUMMARY ===")
print(f"EPS: {stats['eps']}, Rev: {stats['rev']}")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

print("✓ Done")

