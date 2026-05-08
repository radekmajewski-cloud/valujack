#!/usr/bin/env python3
import re
import csv
from datetime import datetime

# Read cards.js
with open('public/cards.js', 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Original file size: {len(content)} bytes")

# CSV files
csv_files = {
    'KING': 'Company data/kings 2026-04-06.csv',
    'JACK': 'Company data/jacks 2026-04-06.csv',
    'QUEEN': 'Company data/queens 2026-04-06.csv',
    'ACE': 'Company data/aces 2026-04-06.csv',
    'JOKER': 'Company data/jokers 2026-04-06.csv',
    'TWO': 'Company data/twos 2026-04-06.csv'
}

ticker_to_fairvalue = {}

# Collect fair values from CSVs
print("\n=== COLLECTING DATA ===")
for strategy, filename in csv_files.items():
    try:
        with open(filename, 'r', encoding='iso-8859-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                ticker = row.get('Info - Ticker', '').strip()
                fair_value = row.get('Fair value', '').strip()
                if ticker and fair_value:
                    try:
                        fv = float(fair_value.replace(',', '.'))
                        ticker_to_fairvalue[ticker] = fv
                    except:
                        pass
    except Exception as e:
        print(f"Error: {e}")

print(f"Collected {len(ticker_to_fairvalue)} fair values")

# Update cards
print("\n=== UPDATING CARDS ===")
updates = 0

for ticker, new_fv in ticker_to_fairvalue.items():
    pattern = r"(ticker:\s*'" + re.escape(ticker) + r"'.*?fairValue:\s*)(\d+(?:\.\d+)?)"
    matches = list(re.finditer(pattern, content, flags=re.DOTALL))
    
    if matches:
        for match in reversed(matches):
            old_fv = float(match.group(2))
            if abs(old_fv - new_fv) > 0.01:
                new_text = match.group(1) + str(new_fv)
                content = content[:match.start()] + new_text + content[match.end():]
                print(f"  ✓ {ticker:10s} {old_fv:8.2f} → {new_fv:8.2f}")
                updates += 1

# Backup
backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open('public/cards.js', 'r') as f:
    original = f.read()
with open(backup, 'w') as f:
    f.write(original)

# Write updated file
with open('public/cards.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n=== SUMMARY ===")
print(f"Updates: {updates}")
print(f"Backup: {backup}")
