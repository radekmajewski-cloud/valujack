import re
from datetime import datetime

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

# Fix Card 225 metrics - use exact match
old_metrics_225 = "metrics: [{ l: 'P/E', v: '21.9' }, { l: 'Return on Capital', v: '9.7%' }, { l: 'FCF Yield', v: '31.1%' }, { l: 'D/E', v: '0.7' }]"
new_metrics_225 = "metrics: [{ l: 'EPS Growth', v: '+49%' }, { l: 'Price Strength', v: '-10%' }, { l: 'Return on Capital', v: '12.9%' }, { l: 'Free Cash', v: '28.6%' }]"

if old_metrics_225 in content:
    content = content.replace(old_metrics_225, new_metrics_225)
    print("✓ Updated Card 225 metrics to JOKER format")
else:
    print("✗ Metrics not found")

# Fix currency - simpler pattern
content = re.sub(
    r"({ id: 225,.*?country: 'USA', currency: ')('')",
    r"\1USD\2",
    content,
    flags=re.DOTALL
)
print("✓ Added USD currency")

# Fix epsGrowth
content = re.sub(
    r"({ id: 225,.*?epsGrowth: ')\+105\.9%(')",
    r"\1+49%\2",
    content,
    flags=re.DOTALL
)
print("✓ Updated epsGrowth to +49%")

print(f"\nBackup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

