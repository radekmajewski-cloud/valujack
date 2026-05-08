import re
from datetime import datetime

# Currency mapping by country
CURRENCY_MAP = {
    'USA': 'USD',
    'Canada': 'CAD',
    'UK': 'GBP',
    'Germany': 'EUR',
    'France': 'EUR',
    'Italy': 'EUR',
    'Spain': 'EUR',
    'Netherlands': 'EUR',
    'Belgium': 'EUR',
    'Austria': 'EUR',
    'Ireland': 'EUR',
    'Portugal': 'EUR',
    'Finland': 'EUR',
    'Greece': 'EUR',
    'Luxembourg': 'EUR',
    'Sweden': 'SEK',
    'Norway': 'NOK',
    'Denmark': 'DKK',
    'Switzerland': 'CHF',
    'Poland': 'PLN',
    'Czech Republic': 'CZK',
    'Hungary': 'HUF',
    'Romania': 'RON',
    'Israel': 'ILS',
    'Turkey': 'TRY',
    'Russia': 'RUB',
    'Japan': 'JPY',
    'China': 'CNY',
    'Hong Kong': 'HKD',
    'Singapore': 'SGD',
    'South Korea': 'KRW',
    'Taiwan': 'TWD',
    'India': 'INR',
    'Australia': 'AUD',
    'New Zealand': 'NZD',
    'Brazil': 'BRL',
    'Mexico': 'MXN',
    'Argentina': 'ARS',
    'Chile': 'CLP',
    'South Africa': 'ZAR',
}

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0
not_found = []

# Find all cards with empty currency
for card_id in range(1, 710):
    match = re.search(
        rf"({{ id: {card_id},.*?country: '([^']+)', currency: ')('')",
        content, re.DOTALL
    )
    
    if match:
        country = match.group(2)
        currency = CURRENCY_MAP.get(country)
        
        if currency:
            # Replace empty currency with correct one
            old_text = match.group(0)
            new_text = match.group(1) + currency + match.group(3)
            content = content.replace(old_text, new_text, 1)
            updated += 1
            
            if updated <= 20:
                print(f"  Card {card_id}: {country} → {currency}")
        else:
            not_found.append((card_id, country))

print(f"\n=== SUMMARY ===")
print(f"Updated: {updated} cards")

if not_found:
    print(f"\nCountries not in map ({len(not_found)} cards):")
    unique_countries = set(c[1] for c in not_found)
    for country in sorted(unique_countries):
        count = sum(1 for c in not_found if c[1] == country)
        print(f"  {country}: {count} cards")

print(f"\nBackup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

