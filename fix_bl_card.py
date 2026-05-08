import re
from datetime import datetime

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

# Fix BL card 251 - replace broken metrics
old_bl_metrics = "metrics: [{ l: 'P/E', v: '100.1' }, { l: 'F-Score', v: '7/9' }, { l: 'Gross Margin', v: '75.[value]' }, { l: '1m Perf', v: '+22.[value]' }]"

new_bl_metrics = "metrics: [{ l: 'ROIC', v: '—' }, { l: 'P/E', v: '100.1' }, { l: '1m Performance', v: '—' }, { l: 'Debt/Equity', v: '4.2' }]"

if old_bl_metrics in content:
    content = content.replace(old_bl_metrics, new_bl_metrics)
    print("✓ Fixed BL metrics")
else:
    print("✗ Pattern not found - checking actual content...")
    # Find what BL actually has
    match = re.search(r"{ id: 251,.*?metrics: \[([^\]]+)\]", content, re.DOTALL)
    if match:
        print(f"BL actual metrics:\n{match.group(1)[:200]}")

print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

