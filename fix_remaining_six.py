import re
from datetime import datetime

# Hardcode the 6 cards with their dividend values
card_fixes = {
    486: ('EJI', '2.4%'),
    497: ('SSA1', '2.2%'),
    513: ('NYKA', '5.2%'),
    516: ('OFH', '3.1%'),
    521: ('02M1', '2.5%'),
    589: ('STRA', '2.9%')
}

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

for card_id, (ticker, div_value) in card_fixes.items():
    # Find this specific card and update both ind1v and metrics
    pattern = rf"({{ id: {card_id}, type: 'KING'.*?ind1l: 'DIVIDEND YIELD', ind1v: ')([^']*?)(', ind2l:.*?{{ l: 'Dividend Yield', v: ')([^']*?)(' }})"
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        new_text = match.group(1) + div_value + match.group(3) + div_value + match.group(5)
        content = content.replace(match.group(0), new_text, 1)
        updated += 1
        print(f"  Card {card_id} ({ticker}): {div_value}")

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

