#!/bin/bash
echo "=== ValuJack Missing Data Fixer ==="
echo ""

if [ "$1" != "apply" ]; then
    echo "Scanning for cards with missing data..."
    echo ""
    
    python3 << 'PYTHON_EOF'
import re, csv

with open('public/cards.js', 'r') as f:
    lines = f.readlines()

# Find cards by looking for lines with [value]
cards_with_issues = {}
current_ticker = None

for line in lines:
    if "ticker: '" in line:
        match = re.search(r"ticker: '([^']+)'", line)
        if match:
            current_ticker = match.group(1)
    
    if current_ticker and '[value]' in line:
        if current_ticker not in cards_with_issues:
            # Get company name
            company_match = re.search(r"company: '([^']+)'", line)
            type_match = re.search(r"type: '([^']+)'", line)
            cards_with_issues[current_ticker] = {
                'company': company_match.group(1) if company_match else '',
                'type': type_match.group(1) if type_match else 'TWO',
                'count': 0
            }
        cards_with_issues[current_ticker]['count'] += line.count('[value]')

if not cards_with_issues:
    print("✅ No cards with missing data!")
    exit()

print(f"Found {len(cards_with_issues)} cards with missing data:\n")

with open('Company data/missing_data_TODAY.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Ticker', 'Company', 'Type', 'Performance 1y (%)', 'Performance 1m (%)', 'Gross Margin (%)'])
    
    for ticker, info in sorted(cards_with_issues.items()):
        print(f"  {info['type']:10} | {ticker:10} | {info['company'][:40]:40} | {info['count']} [value]")
        writer.writerow([ticker, info['company'], info['type'], '', '', ''])

print(f"\n✅ Created: Company data/missing_data_TODAY.csv")
print("\nNEXT:")
print("1. Fill in the CSV with screener data")
print("2. Run: ./fix_missing_data.sh apply")
PYTHON_EOF

else
    echo "Applying fixes..."
    echo ""
    
    python3 << 'APPLY_EOF'
import csv, re

data = {}
try:
    with open('Company data/missing_data_TODAY.csv', 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            ticker = row['Ticker'].strip()
            if row['Performance 1y (%)'].strip():
                data[ticker] = {
                    '1y': row['Performance 1y (%)'].replace('%', '').replace(',', '.').strip(),
                    '1m': row['Performance 1m (%)'].replace('%', '').replace(',', '.').strip(),
                    'gm': row['Gross Margin (%)'].replace('%', '').replace(',', '.').strip()
                }
except:
    print("❌ CSV not found or empty!")
    exit(1)

print(f"Loaded {len(data)} cards\n")

with open('public/cards.js', 'r') as f:
    content = f.read()

for ticker, vals in data.items():
    start = content.find(f"ticker: '{ticker}'")
    if start == -1:
        continue
    end = content.find("}, ", start) + 2
    old = content[start:end]
    new = old
    
    new = re.sub(r"'Gross Margin', v: '\d*\.?\[value\]'", f"'Gross Margin', v: '{vals['gm']}%'", new)
    new = re.sub(r"'1m Perf', v: '\+\d*\.?\[value\]'", f"'1m Perf', v: '+{vals['1m']}%'", new)
    new = re.sub(r"rawV: '\+\d*\.?\[value\]'", f"rawV: '+{vals['1m']}%'", new)
    new = re.sub(r"rawV: '\+\[value\]'", f"rawV: '+{vals['1y']}%'", new)
    new = re.sub(r"rawV: '-\[value\]'", f"rawV: '{vals['1y']}%'", new)
    new = re.sub(r"rawV: '\d*\.?\[value\]'", f"rawV: '{vals['gm']}%'", new)
    new = re.sub(r"'Up \d*\.?\[value\] last month", f"'Up {vals['1m']}% last month", new)
    
    content = content.replace(old, new)
    print(f"✅ {ticker}" if new.count('[value]') == 0 else f"⚠️  {ticker}")

with open('public/cards.js', 'w') as f:
    f.write(content)

print("\n✅ Done! Now: git add public/cards.js && git commit -m 'Fix missing data' && git push && vercel --prod")
APPLY_EOF
fi
