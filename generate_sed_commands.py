#!/usr/bin/env python3
import csv

# Load CSV data
data = {}
for csv_file in ['Company data/twos 2026-04-06.csv', 'Company data/twos extra.csv']:
    try:
        with open(csv_file, 'r', encoding='iso-8859-1') as f:
            for row in csv.DictReader(f, delimiter=';'):
                t = row['Info - Ticker'].strip()
                data[t] = {
                    '1y': row['Performance - Perform. 1y'].replace(',', '.').strip(),
                    '1m': row['Performance - Perform. 1m'].replace(',', '.').strip(),
                    'gm': row['Gross marg - Average 1y'].replace('%', '').replace(',', '.').strip()
                }
    except FileNotFoundError:
        continue

print(f"# Generated sed commands for {len(data)} tickers")
print(f"# Run these one at a time\n")

# Generate sed commands for each ticker
for ticker, vals in sorted(data.items()):
    print(f"# {ticker}: 1y={vals['1y']}, 1m={vals['1m']}, gm={vals['gm']}%")
    
    # For safety, only output first 5 as examples
    if list(data.keys()).index(ticker) < 5:
        # These are example sed commands - we'll refine the approach
        print(f"# sed -i '' 's/ticker: \\'{ticker}\\'.*ind1v: \\'[^']*\\'/ticker: \\'{ticker}\\'...ind1v: \\'{vals['1y']}\\'/g' public/cards.js")
    
print(f"\n# Total: {len(data)} tickers ready")
print("\n# Missing from CSV (need manual data):")
missing = ['ADYEN', 'EPAM', 'FISV', 'PANW', 'PAYC', 'ZBH', 'ZS']
for m in missing:
    print(f"#   - {m}")
