import re
from datetime import datetime

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

# Fix Card 236
# 1. Fix currency
content = re.sub(
    r"(id: 236,.*?ticker: 'ZAP', country: 'Norway', currency: ')('')",
    r"\1NOK\2",
    content,
    flags=re.DOTALL
)
print("✓ Fixed currency: '' → 'NOK'")

# 2. Fix metrics (EPS Growth, Price Strength, ROIC, Free Cash)
old_metrics_236 = "metrics: [{ l: 'P/E', v: '46.3' }, { l: 'ROIC', v: '2.7%' }, { l: 'FCF Yield', v: '28.0%' }, { l: 'D/E', v: '0.5' }]"
new_metrics_236 = "metrics: [{ l: 'EPS Growth', v: '+58%' }, { l: 'Price Strength', v: '-9%' }, { l: 'ROIC', v: '5.3%' }, { l: 'Free Cash', v: '3.5%' }]"

content = content.replace(old_metrics_236, new_metrics_236)
print("✓ Updated metrics to JOKER format")

# 3. Fix epsGrowth field
content = re.sub(
    r"(id: 236,.*?)epsGrowth: '\+96\.9%'",
    r"\1epsGrowth: '+58%'",
    content,
    flags=re.DOTALL
)
print("✓ Fixed epsGrowth: +96.9% → +58%")

print(f"\nBackup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

