import re
from datetime import datetime

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# Find all KING cards where ind1v has a value but metrics has '—' for Dividend Yield
pattern = r"(type: 'KING'.*?ind1l: 'DIVIDEND YIELD', ind1v: '([^']+)'.*?)(metrics: \[{ l: 'Dividend Yield', v: '—' })"

def replace_div(match):
    global updated
    div_value = match.group(2)
    updated += 1
    if updated <= 20:
        print(f"  Copying ind1v={div_value} to metrics")
    return match.group(1) + f"metrics: [{{ l: 'Dividend Yield', v: '{div_value}' }}"

content = re.sub(pattern, replace_div, content, flags=re.DOTALL)

print(f"\nUpdated {updated} KING cards")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")
    import shutil
    shutil.copy(backup, 'public/cards.js')
    print("✓ Auto-restored")

