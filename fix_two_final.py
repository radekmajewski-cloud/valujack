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

# For each ticker, replace ALL [value] and malformed values
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
    
    # Fix ind1v: '--22.90%' or '-22.[value]' → '-27.1%'
    new_card = re.sub(r"ind1v: '[+-]*\d+\..*?'", f"ind1v: '{vals['1y']}'", new_card)
    
    # Fix ind2v: '+-22.90%' or '+[value]' → '+27.1%' or '-27.1%'
    new_card = re.sub(r"ind2v: '[+-]*.*?'", f"ind2v: '{vals['1y']}'", new_card)
    
    # Fix Gross Margin: '50.50%' or '50.[value]' → '50.5%'
    new_card = re.sub(
        r"('Gross Margin', v: ')[^']*'",
        r"\1" + vals['gm'] + "%'",
        new_card
    )
    
    # Fix 1m Perf: '+6.30%' or '+6.[value]' → '+2.4%'
    new_card = re.sub(
        r"('1m Perf', v: ')[^']*'",
        r"\1" + vals['1m'] + "'",
        new_card
    )
    
    # Fix rawV for 1m Perf
    # Find Recovery rawV
    new_card = re.sub(
        r"(raw: '1m Perf', rawV: ')[^']*'",
        r"\1" + vals['1m'] + "'",
        new_card
    )
    
    # Fix rawV for Gross Margin  
    new_card = re.sub(
        r"(raw: 'Gross Margin', rawV: ')[^']*'",
        r"\1" + vals['gm'] + "%'",
        new_card
    )
    
    # Fix Undervalued rawV
    new_card = re.sub(
        r"(raw: 'Undervalued', rawV: ')[^']*'",
        r"\1" + vals['1y'] + "'",
        new_card
    )
    
    # Fix tagBold: 'Up 6.30%' or 'Up 6.[value]' → 'Up 2.4%'
    new_card = re.sub(
        r"(tagBold: 'Up )[^%]*%",
        r"\1" + vals['1m'].replace('%', '') + "%",
        new_card
    )
    
    # Fix bullets: 'Up 6.30%' or 'Up 6.[value]' → 'Up 2.4%'
    new_card = re.sub(
        r"(Up )\d+\.\d+%( last month)",
        r"\1" + vals['1m'].replace('%', '') + "%" + r"\2",
        new_card
    )
    
    content = content.replace(card, new_card)

# Write
with open('public/cards.js', 'w') as f:
    f.write(content)

print(f"\n✅ Fixed TWO cards")
