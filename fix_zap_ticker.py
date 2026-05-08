import re
from datetime import datetime

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

# Fix Card 236 - ZAP ticker
# Find and replace yahooTicker: 'ZAP' with yahooTicker: 'ZAP.OL' for Norway card
pattern = r"(id: 236,.*?country: 'Norway'.*?yahooTicker: ')ZAP(')";
replacement = r"\1ZAP.OL\2"

content = re.sub(pattern, replacement, content, flags=re.DOTALL)

print("✓ Fixed Card 236: ZAP → ZAP.OL")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

