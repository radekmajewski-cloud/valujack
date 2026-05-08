import re
from datetime import datetime

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

# Fix Card 1 - Cal-Maine Foods
# Replace old metrics with new KING metrics
old_metrics = "metrics: [{ l: 'Div. Yield', v: '2.0%' }, { l: 'P/E', v: '13.4' }, { l: 'ROIC', v: '17.0%' }, { l: 'FCF Yield', v: '12.3%' }]"
new_metrics = "metrics: [{ l: 'Dividend Yield', v: '2.0%' }, { l: 'ROIC', v: '51.4%' }, { l: 'P/E', v: '13.4' }, { l: 'Debt/Equity', v: '0.2' }]"

if old_metrics in content:
    content = content.replace(old_metrics, new_metrics)
    print("✓ Updated Card 1 metrics to KING format")
    print("  Added: Debt/Equity = 0.2")
    print("  Updated: ROIC 17.0% → 51.4% (from CSV)")
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

