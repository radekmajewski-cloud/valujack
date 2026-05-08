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
            '1y_perf': row['Performance - Perform. 1y'].strip(),
            '1m_perf': row['Performance - Perform. 1m'].strip(),
            'gross_margin': row['Gross marg - Average 1y'].strip()
        }

print("Reading twos extra.csv...")
with open('Company data/twos extra.csv', 'r', encoding='iso-8859-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        ticker = row['Info - Ticker'].strip()
        if ticker not in csv_data:
            csv_data[ticker] = {
                '1y_perf': row['Performance - Perform. 1y'].strip(),
                '1m_perf': row['Performance - Perform. 1m'].strip(),
                'gross_margin': row['Gross marg - Average 1y'].strip()
            }

print(f"Loaded data for {len(csv_data)} tickers")

# Read cards.js
with open('public/cards.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Track changes
cards_fixed = []
changes_made = 0

# Find all TWO cards with [value]
for ticker, data in csv_data.items():
    # Check if this ticker has [value] in cards.js
    ticker_pattern = f"ticker: '{ticker}'"
    if ticker_pattern not in content:
        continue
    
    # Find the card block
    card_start = content.find(ticker_pattern)
    if card_start == -1:
        continue
    
    # Check if this card has [value]
    card_end = content.find("}, ", card_start) + 2
    card_block = content[card_start:card_end]
    
    if '[value]' not in card_block:
        continue
    
    print(f"Fixing {ticker}...")
    
    # Convert European format to US: "50,5%" -> "50.5"
    gross_margin = data['gross_margin'].replace('%', '').replace(',', '.').strip()
    perf_1m = data['1m_perf'].replace('%', '').replace(',', '.').strip()
    perf_1y = data['1y_perf'].replace('%', '').replace(',', '.').strip()
    
    # Remove +/- signs and keep just numbers
    perf_1m_num = perf_1m.lstrip('+-')
    perf_1y_num = perf_1y.lstrip('+-')
    
    # Replace all [value] with actual data
    new_block = card_block
    
    # Replace: -22.[value] with actual 1y performance
    new_block = re.sub(r'(-\d+\.)\[value\]', r'\g<1>' + perf_1y_num, new_block)
    new_block = re.sub(r'(\+\d+\.)\[value\]', r'\g<1>' + perf_1y_num, new_block)
    
    # Replace: 50.[value] with gross margin
    new_block = re.sub(r'(\d+\.)\[value\]%', r'\g<1>' + gross_margin + '%', new_block)
    new_block = re.sub(r"'(\d+\.)\[value\]'", r"'" + r'\g<1>' + gross_margin + "'", new_block)
    
    # Replace: +6.[value] with 1m performance
    new_block = re.sub(r'Up (\d+\.)\[value\]', r'Up \g<1>' + perf_1m_num + '%', new_block)
    new_block = re.sub(r"'\+(\d+\.)\[value\]'", r"'+\g<1>" + perf_1m_num + "'", new_block)
    
    # Replace +[value] and -[value] standalone
    new_block = new_block.replace('+[value]', perf_1y)
    new_block = new_block.replace('-[value]', perf_1y)
    
    # Update content
    content = content.replace(card_block, new_block)
    cards_fixed.append(ticker)
    changes_made += 1

# Write output
with open('public/cards.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Fixed {changes_made} TWO cards: {', '.join(cards_fixed)}")
print(f"Output written to: public/cards.js")
