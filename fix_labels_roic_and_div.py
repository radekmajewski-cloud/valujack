import re
from datetime import datetime

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

# Fix 1: DIVIDEND % → DIVIDEND YIELD (Page 1 indicators)
count_div = content.count("ind1l: 'DIVIDEND %'")
content = content.replace("ind1l: 'DIVIDEND %'", "ind1l: 'DIVIDEND YIELD'")
print(f"✓ Updated {count_div} cards: DIVIDEND % → DIVIDEND YIELD")

# Fix 2: ROIC → RETURN ON CAPITAL (Page 1 indicators)
count_roic_ind = content.count("ind1l: 'ROIC'")
content = content.replace("ind1l: 'ROIC'", "ind1l: 'RETURN ON CAPITAL'")
print(f"✓ Updated {count_roic_ind} cards: ROIC → RETURN ON CAPITAL (Page 1)")

# Fix 3: ROIC → Return on Capital (Page 2 metrics)
count_roic_metric = content.count("{ l: 'ROIC',")
content = content.replace("{ l: 'ROIC',", "{ l: 'Return on Capital',")
print(f"✓ Updated {count_roic_metric} metrics: ROIC → Return on Capital (Page 2)")

print(f"\nBackup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

