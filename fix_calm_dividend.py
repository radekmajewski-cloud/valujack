import re
from datetime import datetime

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

# Fix Card 40 - update Dividend Yield from 9.9% to 11.1%
# Find the metrics line and replace
pattern = r"({ id: 40,.*?metrics: \[{ l: 'Dividend Yield', v: ')9\.9%('.*?\])"

def fix_div(match):
    return match.group(1) + '11.1%' + match.group(2)

content = re.sub(pattern, fix_div, content, flags=re.DOTALL)

print("✓ Updated Card 40 Dividend Yield: 9.9% → 11.1%")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

