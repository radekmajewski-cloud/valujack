import csv
from datetime import datetime

# Load dividend data
king_data = {}
with open('Company data/kings 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        ticker = row.get('Info - Ticker', '').strip()
        if ticker:
            div = row.get('Div. Yield - Current', '').replace(',', '.').replace('%', '').strip()
            if div:
                try:
                    king_data[ticker] = f"{float(div):.1f}%"
                except:
                    pass

print(f"Loaded {len(king_data)} KING dividends\n")

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

# Simple string replacement - find and replace "{ l: 'Dividend Yield', v: '—' }"
# But only for tickers we have data for
updated = 0
for ticker, div_value in king_data.items():
    # Search for this specific ticker in a KING card with missing dividend
    pattern = f"ticker: '{ticker}'"
    
    if pattern in content:
        # Find all occurrences and check if it's a KING card with missing dividend
        old_str = "{ l: 'Dividend Yield', v: '—' }"
        new_str = f"{{ l: 'Dividend Yield', v: '{div_value}' }}"
        
        # Check if this ticker has the missing dividend pattern nearby
        idx = content.find(pattern)
        if idx != -1:
            # Check within 500 chars if it's a KING card with missing dividend
            chunk = content[max(0, idx-200):min(len(content), idx+500)]
            if "type: 'KING'" in chunk and old_str in chunk:
                # Replace just this occurrence
                before = content[:max(0, idx-200)]
                middle = content[max(0, idx-200):min(len(content), idx+500)]
                after = content[min(len(content), idx+500):]
                
                middle = middle.replace(old_str, new_str, 1)
                content = before + middle + after
                
                updated += 1
                if updated <= 20:
                    print(f"  {ticker}: {div_value}")

print(f"\n=== SUMMARY ===")
print(f"Updated {updated} KING cards")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")
    import shutil
    shutil.copy(backup, 'public/cards.js')
    print("✓ Auto-restored from backup")

