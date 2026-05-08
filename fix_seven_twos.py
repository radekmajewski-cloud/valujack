#!/usr/bin/env python3
import csv
import re

# Read the 7 tickers
data = {}
with open('Company data/TWO_cards_missing_data.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        ticker = row['Ticker'].strip()
        # Convert European format (comma decimal) to US format (dot decimal)
        perf_1y = row['Performance 1y (%)'].strip().replace(',', '.')
        perf_1m = row['Performance 1m (%)'].strip().replace(',', '.')
        gm = row['Gross Margin (%)'].strip().replace(',', '.')
        
        data[ticker] = {
            '1y': perf_1y + '%',
            '1m': perf_1m + '%',
            'gm': gm
        }

print("Data converted:")
for ticker, vals in data.items():
    print(f"{ticker}: 1y={vals['1y']}, 1m={vals['1m']}, gm={vals['gm']}%")

# Read cards.js
with open('public/cards.js', 'r') as f:
    content = f.read()

# Fix each of the 7 tickers
for ticker, vals in data.items():
    if f"ticker: '{ticker}'" not in content:
        print(f"Warning: {ticker} not found in cards.js")
        continue
    
    # Find the card block
    start = content.find(f"ticker: '{ticker}'")
    if start == -1:
        continue
    end = content.find("}, ", start) + 2
    card = content[start:end]
    
    new_card = card
    
    # Replace all occurrences of [value] and malformed values
    new_card = re.sub(r"ind1v: '[^']*'", f"ind1v: '{vals['1y']}'", new_card)
    new_card = re.sub(r"ind2v: '[^']*'", f"ind2v: '{vals['1y']}'", new_card)
    new_card = re.sub(r"'Gross Margin', v: '[^']*'", f"'Gross Margin', v: '{vals['gm']}%'", new_card)
    new_card = re.sub(r"'1m Perf', v: '[^']*'", f"'1m Perf', v: '{vals['1m']}'", new_card)
    new_card = re.sub(r"raw: '1m Perf', rawV: '[^']*'", f"raw: '1m Perf', rawV: '{vals['1m']}'", new_card)
    new_card = re.sub(r"raw: 'Gross Margin', rawV: '[^']*'", f"raw: 'Gross Margin', rawV: '{vals['gm']}%'", new_card)
    new_card = re.sub(r"raw: 'Undervalued', rawV: '[^']*'", f"raw: 'Undervalued', rawV: '{vals['1y']}'", new_card)
    
    # Fix tagBold and bullets
    perf_1m_num = vals['1m'].replace('%', '')
    new_card = re.sub(r"tagBold: '[^']*'", f"tagBold: 'Up {perf_1m_num}% last month.'", new_card)
    new_card = re.sub(r"'Up [^']*% last month", f"'Up {perf_1m_num}% last month", new_card)
    
    # Replace in content
    content = content.replace(card, new_card)
    print(f"✅ Fixed {ticker}")

# Write back
with open('public/cards.js', 'w') as f:
    f.write(content)

print(f"\n✅ Fixed 7 TWO cards")
