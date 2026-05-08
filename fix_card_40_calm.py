import re
from datetime import datetime

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

# Fix Card 40 - Cal-Maine Foods
old_metrics = "{ l: 'Div. Yield', v: '9.9%' }, { l: 'P/E', v: '3.7' }, { l: 'ROIC', v: '51.4%' }, { l: 'FCF Yield', v: '27.8%' }"
new_metrics = "{ l: 'Dividend Yield', v: '9.9%' }, { l: 'ROIC', v: '51.4%' }, { l: 'P/E', v: '3.7' }, { l: 'Debt/Equity', v: '0.2' }"

if old_metrics in content:
    content = content.replace(old_metrics, new_metrics)
    print("✓ Updated Card 40 metrics to KING format")
    print("  Added: Debt/Equity = 0.2")
else:
    print("✗ Pattern not found")

print(f"\nBackup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

