import csv
from datetime import datetime

# Load dividends
king_divs = {'BMY': '2.7%', 'BPF.UN': '6.2%', 'ENV': '5.1%', 'J0L': '2.8%', '74E': '5.0%', 'KN8': '3.6%', 'NYKA': '5.2%', 'OFH': '3.1%', 'ORI1': '11.0%'}

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# Simple replacement approach
for ticker, div_value in king_divs.items():
    # Replace in metrics array
    old_str = f"ticker: '{ticker}'.*?{{ l: 'Dividend Yield', v: '—' }}"
    
    # Find position
    import re
    match = re.search(old_str, content, re.DOTALL)
    if match:
        # Replace just this occurrence
        new_metrics = f"{{ l: 'Dividend Yield', v: '{div_value}' }}"
        content = content.replace("{ l: 'Dividend Yield', v: '—' }", new_metrics, 1)
        
        # Also update ind1v
        ind_pattern = f"ticker: '{ticker}'.*?ind1v: '—'"
        ind_match = re.search(ind_pattern, content, re.DOTALL)
        if ind_match:
            content = content.replace("ind1v: '—'", f"ind1v: '{div_value}'", 1)
        
        updated += 1
        print(f"  {ticker}: {div_value}")

print(f"\nUpdated {updated} cards")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

