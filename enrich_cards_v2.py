import csv
import re
from datetime import datetime

# Read all CSVs
csv_files = {
    'KING': 'Company data/kings 2026-04-06.csv',
    'JACK': 'Company data/jacks 2026-04-06.csv',
    'QUEEN': 'Company data/queens 2026-04-06.csv',
    'ACE': 'Company data/aces 2026-04-06.csv',
    'JOKER': 'Company data/jokers 2026-04-06.csv',
    'TWO': 'Company data/twos 2026-04-06.csv'
}

ticker_data = {}

for strategy, filepath in csv_files.items():
    try:
        with open(filepath, 'r', encoding='iso-8859-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                ticker = row.get('Info - Ticker', '').strip()
                if not ticker:
                    continue
                
                ticker_data[ticker] = {
                    'div_yield': row.get('Div. Yield - Current', '').strip(),
                    'eps_growth': row.get('Earnings g. - Growth 5y', '').strip() or row.get('Earnings g. - Growth 3y', '').strip(),
                    'rev_growth': row.get('Revenue g. - Growth 5y', '').strip(),
                }
    except:
        pass

print(f"Loaded data for {len(ticker_data)} tickers\n")

# Read cards.js
with open('public/cards.js', 'r') as f:
    content = f.read()

# Backup
backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updates = {'eps': 0, 'rev': 0, 'div': 0}

# Update epsGrowth for cards with ticker in our data
def update_eps(match):
    ticker = match.group(1)
    if ticker in ticker_data and ticker_data[ticker]['eps_growth']:
        try:
            val = float(ticker_data[ticker]['eps_growth'].replace(',', '.'))
            if val != 0:
                updates['eps'] += 1
                sign = '+' if val > 0 else ''
                return f"ticker: '{ticker}', country: '{match.group(2)}', currency: '{match.group(3)}', epsGrowth: '{sign}{int(val)}%',"
        except:
            pass
    return match.group(0)

content = re.sub(r"ticker: '([^']+)', country: '([^']*)', currency: '([^']*)', epsGrowth: '[^']*',", update_eps, content)

# Update revGrowth
def update_rev(match):
    ticker = match.group(1)
    if ticker in ticker_data and ticker_data[ticker]['rev_growth']:
        try:
            val = float(ticker_data[ticker]['rev_growth'].replace(',', '.'))
            if val != 0:
                updates['rev'] += 1
                sign = '+' if val > 0 else ''
                return f"ticker: '{ticker}',.*?revGrowth: '{sign}{int(val)}%'"
        except:
            pass
    return match.group(0)

# Simpler approach for revGrowth
for ticker, data in ticker_data.items():
    if data['rev_growth']:
        try:
            val = float(data['rev_growth'].replace(',', '.'))
            if val != 0:
                sign = '+' if val > 0 else ''
                new_val = f"'{sign}{int(val)}%'"
                # Find and replace for this ticker
                pattern = f"ticker: '{re.escape(ticker)}'(.*?)revGrowth: '[^']*'"
                matches = list(re.finditer(pattern, content, re.DOTALL))
                if matches:
                    for match in matches:
                        old = match.group(0)
                        new = re.sub(r"revGrowth: '[^']*'", f"revGrowth: {new_val}", old)
                        content = content.replace(old, new)
                        updates['rev'] += 1
        except:
            pass

# Add dividend yields to KING metrics
for ticker, data in ticker_data.items():
    if data['div_yield']:
        try:
            val = float(data['div_yield'].replace(',', '.'))
            if val > 0:
                # Find KING cards with this ticker that don't have Div. Yield
                pattern = f"type: 'KING'(.*?)ticker: '{re.escape(ticker)}'(.*?)metrics: \[([^\]]+)\]"
                matches = list(re.finditer(pattern, content, re.DOTALL))
                for match in matches:
                    if 'Div. Yield' not in match.group(3):
                        old_metrics = match.group(3)
                        new_metrics = old_metrics + f", {{ l: 'Div. Yield', v: '{val:.1f}%' }}"
                        content = content.replace(f"metrics: [{old_metrics}]", f"metrics: [{new_metrics}]")
                        updates['div'] += 1
                        if updates['div'] <= 5:
                            print(f"  {ticker:10s} → Div. Yield: {val:.1f}%")
        except:
            pass

print(f"\n=== SUMMARY ===")
print(f"EPS Growth: {updates['eps']} cards")
print(f"Rev Growth: {updates['rev']} cards")
print(f"Div Yield: {updates['div']} cards")
print(f"\nBackup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

