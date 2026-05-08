#!/usr/bin/env python3
import csv
import re

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

print(f"Loaded {len(data)} tickers")

# Read file
with open('public/cards.js', 'r') as f:
    content = f.read()

# For each ticker, do simple string replacements
for ticker, vals in data.items():
    if f"ticker: '{ticker}'" not in content:
        continue
    
    print(f"{ticker}: 1y={vals['1y']}, 1m={vals['1m']}, gm={vals['gm']}%")
    
    # Find the card block
    start = content.find(f"ticker: '{ticker}'")
    if start == -1:
        continue
    end = content.find("}, ", start) + 2
    card = content[start:end]
    
    new_card = card
    
    # Replace patterns using format strings to avoid backreference issues
    new_card = re.sub(r"ind1v: '[^']*'", "ind1v: '" + vals['1y'] + "'", new_card)
    new_card = re.sub(r"ind2v: '[^']*'", "ind2v: '" + vals['1y'] + "'", new_card) 
    new_card = re.sub(r"'Gross Margin', v: '[^']*'", "'Gross Margin', v: '" + vals['gm'] + "%'", new_card)
    new_card = re.sub(r"'1m Perf', v: '[^']*'", "'1m Perf', v: '" + vals['1m'] + "'", new_card)
    new_card = re.sub(r"raw: '1m Perf', rawV: '[^']*'", "raw: '1m Perf', rawV: '" + vals['1m'] + "'", new_card)
    new_card = re.sub(r"raw: 'Gross Margin', rawV: '[^']*'", "raw: 'Gross Margin', rawV: '" + vals['gm'] + "%'", new_card)
    new_card = re.sub(r"raw: 'Undervalued', rawV: '[^']*'", "raw: 'Undervalued', rawV: '" + vals['1y'] + "'", new_card)
    
    # Fix tagBold and bullets
    perf_1m_num = vals['1m'].replace('%', '')
    new_card = re.sub(r"(tagBold: 'Up )[^%]*%", "tagBold: 'Up " + perf_1m_num + "%", new_card)
    new_card = re.sub(r"'Up [^%]*% last month", "'Up " + perf_1m_num + "% last month", new_card)
    
    content = content.replace(card, new_card)

# Write
with open('public/cards.js', 'w') as f:
    f.write(content)

print(f"\n✅ Fixed TWO cards")
