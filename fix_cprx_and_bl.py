import re
from datetime import datetime

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

# Fix 1: CPRX company name in tagFull
old_cprx_tagfull = 'tagFull: " is in the biotechnology industry.'
new_cprx_tagfull = 'tagFull: "Catalyst Pharmaceuticals Inc is in the biotechnology industry.'
content = content.replace(old_cprx_tagfull, new_cprx_tagfull)
print("✓ Fixed CPRX company name")

# Fix 2: CPRX EPS growth
old_cprx_eps = "ticker: 'CPRX', country: 'USA', currency: '', epsGrowth: '—'"
new_cprx_eps = "ticker: 'CPRX', country: 'USA', currency: '', epsGrowth: '+19%'"
content = content.replace(old_cprx_eps, new_cprx_eps)
print("✓ Fixed CPRX EPS growth")

# Fix 3: BL broken [value] placeholders - need to check what the real values should be
# For now, just flag it
if '[value]' in content:
    count = content.count('[value]')
    print(f"⚠ Warning: {count} [value] placeholders still in file (Card 251 - BL)")

print(f"\nBackup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

