import csv
import re
from datetime import datetime

# Read kings CSV to get dividend yields
dividend_map = {}
with open('Company data/kings 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        ticker = row.get('Info - Ticker', '').strip()
        div_yield = row.get('Div. Yield - Current', '').strip()
        if ticker and div_yield:
            try:
                # Convert to percentage format
                div_val = float(div_yield.replace(',', '.'))
                dividend_map[ticker] = f"{div_val:.1f}%"
            except:
                pass

print(f"Loaded dividend data for {len(dividend_map)} KING tickers\n")

# Read cards.js
with open('public/cards.js', 'r') as f:
    content = f.read()

# Backup
backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# Find all KING cards and add Div. Yield to metrics
pattern = r"(type: 'KING'.*?ticker: '([^']+)'.*?metrics: \[)([^\]]+)(\])"

def add_dividend(match):
    global updated
    prefix = match.group(1)
    ticker = match.group(2)
    metrics_content = match.group(3)
    suffix = match.group(4)
    
    # Check if already has Div. Yield
    if 'Div. Yield' in metrics_content:
        return match.group(0)
    
    # Check if we have dividend data
    if ticker not in dividend_map:
        return match.group(0)
    
    # Add Div. Yield metric
    div_metric = f"{{ l: 'Div. Yield', v: '{dividend_map[ticker]}' }}"
    new_metrics = metrics_content + ", " + div_metric
    
    updated += 1
    if updated <= 10:
        print(f"  {ticker:10s} → Div. Yield: {dividend_map[ticker]}")
    
    return prefix + new_metrics + suffix

content = re.sub(pattern, add_dividend, content, flags=re.DOTALL)

print(f"\n✓ Added dividend yield to {updated} KING cards")
print(f"✓ Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

