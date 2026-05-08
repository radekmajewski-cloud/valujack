import csv
import re
from datetime import datetime

# Load dividend data for KING cards
div_data = {}
with open('Company data/kings 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        ticker = row.get('Info - Ticker', '').strip()
        div = row.get('Div. Yield - Current', '').strip()
        if ticker and div:
            # Remove % and replace ,
            div_clean = div.replace(',', '.').replace('%', '')
            try:
                val = float(div_clean)
                if val > 0:
                    div_data[ticker] = val
            except:
                pass

print(f"Loaded {len(div_data)} KING dividends\n")

# Read cards
with open('public/cards.js', 'r') as f:
    content = f.read()

# Backup
backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

added = 0

# Find KING cards and add dividend
for ticker, div_val in div_data.items():
    # Pattern: KING card with this ticker, metrics ending with D/E
    pattern = rf"(type: 'KING'.*?ticker: '{re.escape(ticker)}'.*?metrics: \[[^\]]+{{ l: 'D/E', v: '[^']+' }})\]"
    
    matches = list(re.finditer(pattern, content, re.DOTALL))
    for match in matches:
        if 'Div. Yield' not in match.group(0):
            old = match.group(0)
            new = old + f", {{ l: 'Div. Yield', v: '{div_val:.1f}%' }}]"
            content = content.replace(old, new, 1)
            added += 1
            if added <= 10:
                print(f"  {ticker}: {div_val:.1f}%")

print(f"\n=== SUMMARY ===")
print(f"Added {added} dividend yields")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

print("✓ Done")

