#!/usr/bin/env python3
import re

# Read cards.js
with open('public/cards.js', 'r') as f:
    content = f.read()

# Define the 7 tickers with old-style cards
old_style_tickers = ['FISV', 'PANW', 'PAYC', 'ZBH', 'ZS', 'ADYEN', 'EPAM']

for ticker in old_style_tickers:
    if f"ticker: '{ticker}'" not in content:
        print(f"Warning: {ticker} not found")
        continue
    
    # Find the card block
    start = content.find(f"ticker: '{ticker}'")
    if start == -1:
        continue
    end = content.find("}, ", start) + 2
    card = content[start:end]
    new_card = card
    
    # Remove [value] from narrative fields - make them generic
    # tag: 'Something. Down [value].' → 'Something. Recent pullback.'
    new_card = re.sub(r"(tag: '[^']*\.) Down \[value\]\.(')", r"\1 Recent pullback.\2", new_card)
    
    # pick: 'Something. Down [value].' → 'Something. Recent pullback.'
    new_card = re.sub(r"(pick: '[^']*\.) Down \[value\]\.(')", r"\1 Recent pullback.\2", new_card)
    
    # bullets: "EPS growth of [value] over 5 years" → "EPS growth over 5 years"
    new_card = re.sub(r"EPS growth of \[value\] over 5 years", "strong EPS growth over 5 years", new_card)
    
    # Replace in content
    content = content.replace(card, new_card)
    print(f"✅ Cleaned narrative text for {ticker}")

# Write back
with open('public/cards.js', 'w') as f:
    f.write(content)

print(f"\n✅ Cleaned narrative [value] placeholders from 7 TWO cards")
