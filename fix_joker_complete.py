#!/usr/bin/env python3
import re

# Country mappings for JOKER cards
countries = {
    'NVDA': 'USA', 'AMD': 'USA', 'APP': 'USA', 'BTDR': 'USA',
    'CLS': 'USA', 'FIX': 'USA', 'DCBO': 'Canada', 'LLY': 'USA',
    'EME': 'USA', 'GDWN': 'UK', 'IDR': 'Spain', 'ALNSC': 'France',
    'STX': 'USA'
}

with open('public/cards.js', 'r', encoding='utf-8') as f:
    content = f.read()

for ticker, country in countries.items():
    # Fix tagFull: "...in ?, trading..." → "...in Canada, trading..."
    content = re.sub(
        rf"(ticker: '{ticker}'.*?tagFull: \"[^\"]*company in )\?",
        rf"\1{country}",
        content,
        flags=re.DOTALL
    )
    
    # Fix bullets: "...in ?." → "...in Canada."
    content = re.sub(
        rf"(ticker: '{ticker}'.*?bullets: \[\"[^\"]*— [a-z ]+ in )\?\.",
        rf"\1{country}.",
        content,
        flags=re.DOTALL
    )

with open('public/cards.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed tagFull and bullets for all JOKER cards")
