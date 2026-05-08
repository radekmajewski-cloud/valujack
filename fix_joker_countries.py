#!/usr/bin/env python3
"""Fix JOKER cards by adding country names from CSV to tag, tagFull, pickFull, and bullets fields."""

import re
import sys

# Read the JOKER CSV to get country mappings
csv_path = "Company data/Joker 2_2026-03-19.csv"
joker_countries = {}

print(f"Reading country data from {csv_path}...")
with open(csv_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines[1:]:  # Skip header
        parts = line.strip().split('\t')
        if len(parts) >= 3:
            ticker = parts[0].strip()
            country = parts[2].strip()
            if ticker and country:
                joker_countries[ticker] = country

print(f"Found {len(joker_countries)} tickers with country data")
print(f"Tickers: {', '.join(joker_countries.keys())}")

# Read cards.js
cards_path = "public/cards.js"
print(f"\nReading {cards_path}...")
with open(cards_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Track changes
changes_made = 0
cards_fixed = []

# Find all JOKER cards with "?." in tag field
pattern = r"(type: 'JOKER'.*?ticker: '([A-Z\s]+)'.*?tag: '[^']*\.\s*\?\.',)"
matches = list(re.finditer(pattern, content, re.DOTALL))

print(f"\nFound {len(matches)} JOKER cards with '?.' in tag field")

for match in matches:
    card_block = match.group(1)
    ticker = match.group(2).strip()
    
    # Get country for this ticker
    country = joker_countries.get(ticker)
    if not country:
        print(f"  ⚠️  No country found for {ticker}, skipping")
        continue
    
    print(f"  Fixing {ticker} → {country}")
    
    # Fix all occurrences in this card block
    # 1. tag: 'IT Services. ?.' → 'IT Services. Canada.'
    new_block = re.sub(
        r"(tag: '[^']*)\.\s*\?\.",
        r"\1. " + country + ".",
        card_block
    )
    
    # 2. tagFull: "...company in ?, trading..." → "...company in Canada, trading..."
    new_block = re.sub(
        r"(company in )\?",
        r"\1" + country,
        new_block
    )
    
    # 3. bullets: "...it services in ?." → "...it services in Canada."
    new_block = re.sub(
        r"( in )\?\.",
        r"\1" + country + ".",
        new_block
    )
    
    # 4. Fix grammar: "a IT services" → "an IT services"
    new_block = re.sub(r"\ba IT services\b", "an IT services", new_block)
    new_block = re.sub(r"\bit services\b", "IT services", new_block)
    
    # Replace in content
    content = content.replace(card_block, new_block)
    changes_made += 1
    cards_fixed.append(ticker)

# Write output
output_path = "public/cards.js"
print(f"\nWriting fixed file to {output_path}...")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Fixed {changes_made} JOKER cards: {', '.join(cards_fixed)}")
print(f"Output written to: {output_path}")
