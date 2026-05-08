import re
from datetime import datetime

# Yahoo Finance suffix mapping
SUFFIX_MAP = {
    'Germany': '.DE',
    'Sweden': '.ST',
    'UK': '.L',
    'Norway': '.OL',
    'France': '.PA',
    'Belgium': '.BR',
    'Netherlands': '.AS',
    'Spain': '.MC',
    'Italy': '.MI',
    'Denmark': '.CO',
    'Finland': '.HE',
    'Canada': '.TO',
    'USA': '',
    '': ''
}

# Read cards
with open('public/cards.js', 'r') as f:
    content = f.read()

# Backup
backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# Fix cards 319-709
for card_id in range(319, 710):
    pattern = rf"({{ id: {card_id},.*?yahooTicker: ')([^']+)('.*?ticker: ')([^']+)('.*?country: ')([^']*)(')".replace(' ', r'\s*')
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        yahoo_ticker = match.group(2)
        ticker = match.group(4)
        country = match.group(6)
        
        # Check if yahooTicker already has a suffix
        if '.' not in yahoo_ticker and country in SUFFIX_MAP:
            suffix = SUFFIX_MAP[country]
            new_yahoo = ticker + suffix
            
            # Replace
            old = f"yahooTicker: '{yahoo_ticker}'"
            new = f"yahooTicker: '{new_yahoo}'"
            content = content.replace(old, new, 1)
            updated += 1
            
            if updated <= 10:
                print(f"  Card {card_id} ({country}): {yahoo_ticker} → {new_yahoo}")

print(f"\n=== SUMMARY ===")
print(f"Updated {updated} Yahoo tickers")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

print("✓ Done")

