import re
from datetime import datetime

CURRENCY_MAP = {
    'USA': 'USD', 'Canada': 'CAD', 'UK': 'GBP',
    'Germany': 'EUR', 'France': 'EUR', 'Italy': 'EUR', 'Spain': 'EUR',
    'Netherlands': 'EUR', 'Belgium': 'EUR', 'Austria': 'EUR',
    'Ireland': 'EUR', 'Portugal': 'EUR', 'Finland': 'EUR',
    'Sweden': 'SEK', 'Norway': 'NOK', 'Denmark': 'DKK',
    'Switzerland': 'CHF', 'Japan': 'JPY', 'Australia': 'AUD',
    'Singapore': 'SGD', 'Hong Kong': 'HKD', 'Israel': 'ILS',
}

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0
unknown_countries = set()

# Find and replace all empty currencies
def replace_currency(match):
    global updated, unknown_countries
    country = match.group(1)
    currency = CURRENCY_MAP.get(country, None)
    
    if currency:
        updated += 1
        if updated <= 20:
            print(f"  {country} → {currency}")
        return f"country: '{country}', currency: '{currency}'"
    else:
        unknown_countries.add(country)
        return match.group(0)  # Keep original

# Replace pattern: country: 'X', currency: ''
content = re.sub(
    r"country: '([^']+)', currency: ''",
    replace_currency,
    content
)

print(f"\n=== SUMMARY ===")
print(f"Updated: {updated} cards")

if unknown_countries:
    print(f"\nUnknown countries: {', '.join(sorted(unknown_countries))}")

print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

