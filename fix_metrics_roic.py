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

# Load ROIC from CSV
csv_roic = {}
with open(CSV_PATH, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        ticker = row['Info - Ticker'].strip()
        roic = parse_num(row.get('ROIC - Current',''))
        if roic is not None:
            csv_roic[ticker] = f"{roic:.1f}%"

print(f"Loaded ROIC for {len(csv_roic)} companies")

with open(CARDS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
backup = CARDS_PATH + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}_before_metrics_roic_fix'
with open(backup, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Backup: {backup}")

# Fix ROIC inside metrics array: { l: 'ROIC', v: '0.0%' }
# We need to find the ticker for each card first, then fix its metrics ROIC
# Strategy: find each card block, get ticker, fix metrics ROIC if 0.0%

# Match full card objects
card_pattern = re.compile(r"(\{ id: \d+.*?)\},\s*\n", re.DOTALL)

updated = 0
not_found = []

def fix_card(m):
    global updated
    card = m.group(1)
    
    # Only process if metrics has ROIC 0.0%
    if "l: 'ROIC', v: '0.0%'" not in card:
        return m.group(0)
    
    # Extract ticker
    ticker_match = re.search(r"ticker: '([^']+)'", card)
    if not ticker_match:
        return m.group(0)
    
    ticker = ticker_match.group(1)
    roic = csv_roic.get(ticker)
    
    if roic is None:
        not_found.append(ticker)
        return m.group(0)
    
    new_card = card.replace("l: 'ROIC', v: '0.0%'", f"l: 'ROIC', v: '{roic}'")
    updated += 1
    if updated <= 20:
        print(f"  {ticker:15s} → metrics ROIC: {roic}")
    
    return new_card + '},\n'

new_content = card_pattern.sub(fix_card, content)

with open(CARDS_PATH, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\n✅ Fixed metrics ROIC for {updated} cards")
print(f"⚠️  Not found: {len(not_found)}: {not_found[:10]}")

remaining = new_content.count("l: 'ROIC', v: '0.0%'")
print(f"Remaining metrics ROIC 0.0%: {remaining}")
