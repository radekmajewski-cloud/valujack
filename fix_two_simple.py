#!/usr/bin/env python3
import csv

# Read CSV data
data = {}
with open('Company data/twos 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
    for row in csv.DictReader(f, delimiter=';'):
        t = row['Info - Ticker'].strip()
        data[t] = {
            '1y': row['Performance - Perform. 1y'].replace(',', '.').strip(),
            '1m': row['Performance - Perform. 1m'].replace(',', '.').strip(), 
            'gm': row['Gross marg - Average 1y'].replace(',', '.').strip()
        }

with open('Company data/twos extra.csv', 'r', encoding='iso-8859-1') as f:
    for row in csv.DictReader(f, delimiter=';'):
        t = row['Info - Ticker'].strip()
        if t not in data:
            data[t] = {
                '1y': row['Performance - Perform. 1y'].replace(',', '.').strip(),
                '1m': row['Performance - Perform. 1m'].replace(',', '.').strip(),
                'gm': row['Gross marg - Average 1y'].replace(',', '.').strip()
            }

print(f"Loaded {len(data)} tickers")

# Read file
with open('public/cards.js', 'r') as f:
    content = f.read()

# For each ticker, do simple replacements
fixed = []
for ticker, vals in data.items():
    if f"ticker: '{ticker}'" not in content or '[value]' not in content:
        continue
    
    # Find the card section
    start = content.find(f"ticker: '{ticker}'")
    if start == -1:
        continue
    end = content.find("}, ", start) + 2
    if end <= start:
        continue
    
    card = content[start:end]
    if '[value]' not in card:
        continue
        
    print(f"{ticker}: 1y={vals['1y']}, 1m={vals['1m']}, gm={vals['gm']}")
    
    # Simple replacements - just replace the exact patterns
    new_card = card.replace('-[value]', vals['1y'])
    new_card = new_card.replace('+[value]', vals['1y']) 
    new_card = new_card.replace('[value]%', vals['gm'])
    new_card = new_card.replace('[value]', vals['1m'])
    
    content = content.replace(card, new_card)
    fixed.append(ticker)

# Write
with open('public/cards.js', 'w') as f:
    f.write(content)

print(f"\n✅ Fixed {len(fixed)} cards")
