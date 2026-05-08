import re
import csv
from datetime import datetime

CARDS_PATH = '/Users/radekmajewski/Downloads/valujack/public/cards.js'
CSV_PATH = '/Users/radekmajewski/Downloads/valujack/Company data/All_company_data_2026-04-18.csv'

# ── Load ROIC from CSV ────────────────────────────────────────────────────────
def parse_num(s):
    if not s or s.strip() == '':
        return None
    s = s.strip().replace('%','').replace(',','.')
    try:
        return float(s)
    except:
        return None

csv_roic = {}  # ticker -> ROIC string like "21.6%"
with open(CSV_PATH, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        ticker = row['Info - Ticker'].strip()
        roic = parse_num(row.get('ROIC - Current',''))
        if roic is not None:
            csv_roic[ticker] = f"{roic:.1f}%"

print(f"Loaded ROIC for {len(csv_roic)} companies from CSV")

# ── Read cards.js ─────────────────────────────────────────────────────────────
with open(CARDS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
backup = CARDS_PATH + f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}_before_roic_fix'
with open(backup, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Backup: {backup}")

# ── Find cards with ROIC 0.0% and fix them ───────────────────────────────────
# Pattern: capture ticker and the full card line context
pattern = re.compile(
    r"(ticker: '([^']+)'[^}]*?ind2l: 'ROIC', ind2v: '0\.0%')",
    re.DOTALL
)

updated = 0
not_found = []

def replacer(m):
    global updated
    full = m.group(1)
    ticker = m.group(2)
    
    roic = csv_roic.get(ticker)
    if roic is None:
        not_found.append(ticker)
        return m.group(0)
    
    if roic == '0.0%':
        not_found.append(f"{ticker}(genuinely0)")
        return m.group(0)
    
    updated += 1
    if updated <= 20:
        print(f"  {ticker:15s} → ROIC: {roic}")
    
    new_full = full.replace("ind2l: 'ROIC', ind2v: '0.0%'", f"ind2l: 'ROIC', ind2v: '{roic}'")
    return new_full

new_content = pattern.sub(replacer, content)

# Also fix ROIC in metrics array
pattern2 = re.compile(
    r"(ticker: '([^']+)'[^}]*?l: 'ROIC', v: '0\.0%')",
    re.DOTALL
)

updated2 = 0

def replacer2(m):
    global updated2
    full = m.group(1)
    ticker = m.group(2)
    
    roic = csv_roic.get(ticker)
    if roic is None or roic == '0.0%':
        return m.group(0)
    
    updated2 += 1
    new_full = full.replace("l: 'ROIC', v: '0.0%'", f"l: 'ROIC', v: '{roic}'")
    return new_full

new_content = pattern2.sub(replacer2, new_content)

with open(CARDS_PATH, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\n✅ Fixed ROIC ind2v for {updated} cards")
print(f"✅ Fixed ROIC metrics for {updated2} cards")
print(f"⚠️  Not found/genuinely zero: {len(not_found)}")
if not_found[:20]:
    print(f"   {not_found[:20]}")

remaining = new_content.count("ind2v: '0.0%'")
print(f"\nRemaining ROIC 0.0%: {remaining}")
