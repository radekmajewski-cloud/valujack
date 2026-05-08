#!/usr/bin/env python3
"""Fix TWO cards by filling in [value] placeholders from CSV data."""

import re
import csv

# Read both CSV files
csv_data = {}

print("Reading twos 2026-04-06.csv...")
with open('Company data/twos 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        ticker = row['Info - Ticker'].strip()
        csv_data[ticker] = {
            '1y_perf': row['Performance - Perform. 1y'].replace('%', '').replace(',', '.').strip(),
            '1m_perf': row['Performance - Perform. 1m'].replace('%', '').replace(',', '.').strip(),
            'gross_margin': row['Gross marg - Average 1y'].replace('%', '').replace(',', '.').strip()
        }

print("Reading twos extra.csv...")
with open('Company data/twos extra.csv', 'r', encoding='iso-8859-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        ticker = row['Info - Ticker'].strip()
        if ticker not in csv_data:
            csv_data[ticker] = {
                '1y_perf': row['Performance - Perform. 1y'].replace('%', '').replace(',', '.').strip(),
                '1m_perf': row['Performance - Perform. 1m'].replace('%', '').replace(',', '.').strip(),
                'gross_margin': row['Gross marg - Average 1y'].replace('%', '').replace(',', '.').strip()
            }

print(f"Loaded data for {len(csv_data)} tickers")

# Backup first
import shutil
shutil.copy('public/cards.js', 'public/cards.js.backup_before_two_fix')
print("Backup created: public/cards.js.backup_before_two_fix")

# Read cards.js
with open('public/cards.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Track changes
cards_fixed = []

# Fix each ticker individually
for ticker, data in csv_data.items():
    if f"ticker: '{ticker}'" not in content or '[value]' not in content:
        continue
    
    # Extract just the numbers
    perf_1y = data['1y_perf'].lstrip('+-')
    perf_1m = data['1m_perf'].lstrip('+-')
    gross = data['gross_margin']
    
    print(f"Fixing {ticker}: 1y={perf_1y}%, 1m={perf_1m}%, margin={gross}%")
    
    # Find and replace for this specific ticker
    # Pattern: match the entire card block
    pattern = rf"({{[^{{]*ticker: '{ticker}'[^}}]*}})"
    
    def replace_values(match):
        card = match.group(0)
        # Replace all [value] patterns for this specific card
        card = re.sub(r"ind1v: '([+-])(\d+\.)\[value\]'", rf"ind1v: '\1\2{perf_1y}'", card)
        card = re.sub(r"ind2v: '([+-])\[value\]'", rf"ind2v: '\1{perf_1y}'", card)
        card = re.sub(r"'Gross Margin', v: '(\d+\.)\[value\]'", rf"'Gross Margin', v: '\1{gross}%'", card)
        card = re.sub(r"'1m Perf', v: '([+-])(\d+\.)\[value\]'", rf"'1m Perf', v: '\1\2{perf_1m}%'", card)
        card = re.sub(r"rawV: '([+-])(\d+\.)\[value\]'", rf"rawV: '\1\2{perf_1m}%'", card)
        card = re.sub(r"rawV: '(\d+\.)\[value\]'", rf"rawV: '{gross}%'", card)
        card = re.sub(r"'Up (\d+\.)\[value\]%", rf"'Up \1{perf_1m}%", card)
        card = re.sub(r"Up (\d+\.)\[value\]", rf"Up \1{perf_1m}%", card)
        return card
    
    content = re.sub(pattern, replace_values, content, flags=re.DOTALL)
    cards_fixed.append(ticker)

# Write output
with open('public/cards.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Fixed {len(cards_fixed)} TWO cards")
print("Output written to: public/cards.js")
