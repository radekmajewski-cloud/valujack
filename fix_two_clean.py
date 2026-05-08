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
                    '1y': row['Performance - Perform. 1y'].replace('%', '').replace(',', '.').strip(),
                    '1m': row['Performance - Perform. 1m'].replace('%', '').replace(',', '.').strip(),
                    'gm': row['Gross marg - Average 1y'].replace('%', '').replace(',', '.').strip()
                }
    except FileNotFoundError:
        continue

print(f"Loaded {len(data)} tickers from CSVs")

# Read cards.js
with open('public/cards.js', 'r') as f:
    lines = f.readlines()

# Process line by line
fixed_count = 0
current_ticker = None

for i, line in enumerate(lines):
    # Track which ticker we're in
    if "ticker: '" in line:
        match = re.search(r"ticker: '([^']+)'", line)
        if match:
            current_ticker = match.group(1)
    
    # If we're in a ticker with data, do replacements
    if current_ticker and current_ticker in data:
        d = data[current_ticker]
        
        # Replace patterns
        # ind1v: '-22.[value]' → ind1v: '-27.1%'
        new_line = re.sub(
            r"(ind1v: ')([+-])(\d+\.)\[value\](')",
            lambda m: m.group(1) + m.group(2) + d['1y'] + '%' + m.group(4),
            line
        )
        
        # ind2v: '+[value]' or '-[value]' → ind2v: '+27.1%' or '-27.1%'
        new_line = re.sub(
            r"(ind2v: ')([+-])\[value\](')",
            lambda m: m.group(1) + m.group(2) + d['1y'] + '%' + m.group(3),
            new_line
        )
        
        # 'Gross Margin', v: '50.[value]' → 'Gross Margin', v: '50.5%'
        new_line = re.sub(
            r"('Gross Margin', v: ')(\d+\.)\[value\](')",
            lambda m: m.group(1) + d['gm'] + '%' + m.group(3),
            new_line
        )
        
        # '1m Perf', v: '+6.[value]' → '1m Perf', v: '+2.4%'
        new_line = re.sub(
            r"('1m Perf', v: ')([+-])(\d+\.)\[value\](')",
            lambda m: m.group(1) + m.group(2) + d['1m'] + '%' + m.group(4),
            new_line
        )
        
        # rawV: '+6.[value]' → rawV: '+2.4%'
        new_line = re.sub(
            r"(rawV: ')([+-])(\d+\.)\[value\](')",
            lambda m: m.group(1) + m.group(2) + d['1m'] + '%' + m.group(4),
            new_line
        )
        
        # rawV: '50.[value]' → rawV: '50.5%'  
        new_line = re.sub(
            r"(rawV: ')(\d+\.)\[value\](')",
            lambda m: m.group(1) + d['gm'] + '%' + m.group(3),
            new_line
        )
        
        # tagBold: 'Up 6.[value] last month' → 'Up 2.4% last month'
        new_line = re.sub(
            r"(Up )(\d+\.)\[value\]",
            lambda m: m.group(1) + d['1m'] + '%',
            new_line
        )
        
        # bullets: 'Up 6.[value] last month' → 'Up 2.4% last month'
        # (same pattern, already covered above)
        
        if new_line != line:
            fixed_count += 1
            
        lines[i] = new_line

# Write output
with open('public/cards.js', 'w') as f:
    f.writelines(lines)

print(f"✅ Fixed {fixed_count} lines across TWO cards")
