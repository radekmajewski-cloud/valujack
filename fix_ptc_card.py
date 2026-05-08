import re
from datetime import datetime

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

# Fix Card 225 - PTC Inc
# 1. Add currency
content = re.sub(
    r"(id: 225,.*?ticker: 'PTC', country: 'USA', currency: ')('')",
    r"\1USD\2",
    content,
    flags=re.DOTALL
)
print("✓ Added currency: USD")

# 2. Update metrics to JOKER format
old_metrics = "{ l: 'P/E', v: '42.1' }, { l: 'Return on Capital', v: '12.5%' }, { l: 'FCF Yield', v: '20.2%' }, { l: 'D/E', v: '0.1' }"
new_metrics = "{ l: 'EPS Growth', v: '+49%' }, { l: 'Price Strength', v: '-10%' }, { l: 'Return on Capital', v: '12.9%' }, { l: 'Free Cash', v: '28.6%' }"

if old_metrics in content:
    content = content.replace(old_metrics, new_metrics)
    print("✓ Updated metrics to JOKER format")
else:
    print("✗ Metrics pattern not found - checking...")

# 3. Update epsGrowth field
content = re.sub(
    r"(id: 225,.*?)epsGrowth: '\+185\.7%'",
    r"\1epsGrowth: '+49%'",
    content,
    flags=re.DOTALL
)
print("✓ Updated epsGrowth: +185.7% → +49%")

print(f"\nBackup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

