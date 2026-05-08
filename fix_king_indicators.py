import csv
import re
from datetime import datetime

# Load dividend data for all KING cards
div_data = {}
with open('Company data/kings 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        ticker = row.get('Info - Ticker', '').strip()
        div = row.get('Div. Yield - Current', '').strip()
        if ticker and div:
            div_clean = div.replace(',', '.').replace('%', '')
            try:
                val = float(div_clean)
                if val > 0:
                    div_data[ticker] = val
            except:
                pass

print(f"Loaded {len(div_data)} KING dividends\n")

# Read cards
with open('public/cards.js', 'r') as f:
    content = f.read()

# Backup
backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# Find all KING cards and update ind1l/ind1v to show dividend
pattern = r"(type: 'KING'.*?ticker: '([^']+)'.*?)(ind1l: '[^']+', ind1v: '[^']+')"

def fix_indicator(match):
    global updated
    prefix = match.group(1)
    ticker = match.group(2)
    old_ind = match.group(3)
    
    if ticker in div_data:
        div_val = div_data[ticker]
        new_ind = f"ind1l: 'DIVIDEND %', ind1v: '{div_val:.1f}%'"
        updated += 1
        if updated <= 10:
            print(f"  {ticker}: {old_ind} → {new_ind}")
        return prefix + new_ind
    return match.group(0)

content = re.sub(pattern, fix_indicator, content, flags=re.DOTALL)

print(f"\n=== SUMMARY ===")
print(f"Updated {updated} KING card indicators")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

# Syntax check
import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

