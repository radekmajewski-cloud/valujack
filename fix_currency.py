import re
import csv
from datetime import datetime

CARDS_PATH = '/Users/radekmajewski/Downloads/valujack/public/cards.js'
CSV_PATH = '/Users/radekmajewski/Downloads/valujack/Company data/All_company_data_2026-04-18.csv'

def parse_num(s):
    if not s or s.strip() == '':
        return None
    s = s.strip().replace('%','').replace(',','.')
    try:
        return float(s)
    except:
        return None

# Load currency from CSV
csv_currency = {}
with open(CSV_PATH, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        ticker = row['Info - Ticker'].strip()
        currency = row.get('Info - Price Currency', '').strip()
        if currency:
            csv_currency[ticker] = currency

print(f"Loaded currency for {len(csv_currency)} companies")

with open(CARDS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
backup = CARDS_PATH + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}_before_currency_fix'
with open(backup, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Backup: {backup}")

# Match card blocks and fix currency: ''
card_pattern = re.compile(r"(\{ id: \d+.*?)\},\s*\n", re.DOTALL)

updated = 0
not_found = []

def fix_card(m):
    global updated
    card = m.group(1)

    # Only process if currency is empty
    if "currency: ''" not in card:
        return m.group(0)

    # Extract ticker
    ticker_match = re.search(r"ticker: '([^']+)'", card)
    if not ticker_match:
        return m.group(0)

    ticker = ticker_match.group(1)
    currency = csv_currency.get(ticker)

    if not currency:
        not_found.append(ticker)
        return m.group(0)

    new_card = card.replace("currency: ''", f"currency: '{currency}'")
    updated += 1
    if updated <= 20:
        print(f"  {ticker:15s} → {currency}")

    return new_card + '},\n'

new_content = card_pattern.sub(fix_card, content)

with open(CARDS_PATH, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\n✅ Fixed currency for {updated} cards")
print(f"⚠️  Not found: {len(not_found)}: {not_found[:10]}")

remaining = new_content.count("currency: ''")
print(f"Remaining missing currency: {remaining}")
