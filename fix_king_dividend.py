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

csv_div = {}
with open(CSV_PATH, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        ticker = row['Info - Ticker'].strip()
        div = parse_num(row.get('Div. Yield - Current',''))
        if div is not None:
            csv_div[ticker] = f"{div:.1f}%"

print(f"Loaded dividend yield for {len(csv_div)} companies")

with open(CARDS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

card_pattern = re.compile(r"(\{ id: \d+.*?)\},\s*\n", re.DOTALL)

updated = 0
not_found = []

def fix_card(m):
    global updated
    card = m.group(1)
    if "type: 'KING'" not in card:
        return m.group(0)
    if "ind1l: 'DIV YIELD'" in card:
        return m.group(0)
    ticker_match = re.search(r"ticker: '([^']+)'", card)
    if not ticker_match:
        return m.group(0)
    ticker = ticker_match.group(1)
    div = csv_div.get(ticker)
    if not div:
        not_found.append(ticker)
        return m.group(0)
    new_card = re.sub(r"ind1l: '[^']*', ind1v: '[^']*'",
                      f"ind1l: 'DIV YIELD', ind1v: '{div}'", card)
    updated += 1
    if updated <= 20:
        print(f"  {ticker:15s} → DIV YIELD: {div}")
    return new_card + '},\n'

new_content = card_pattern.sub(fix_card, content)

with open(CARDS_PATH, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\n✅ Fixed DIV YIELD for {updated} KING cards")
print(f"⚠️  Not found: {len(not_found)}: {not_found[:10]}")
