import re
from datetime import datetime

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

# Fix Card 3: N4Q1.DE → HME.V
content = content.replace("yahooTicker: 'N4Q1.DE'", "yahooTicker: 'HME.V'")
print("✓ Fixed Card 3: N4Q1.DE → HME.V")

# Fix Card 6: VDE.BR → VAN.BR
content = content.replace("yahooTicker: 'VDE.BR'", "yahooTicker: 'VAN.BR'")
print("✓ Fixed Card 6: VDE.BR → VAN.BR")

print(f"\nBackup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

