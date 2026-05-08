import re
from datetime import datetime

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# Fix cards 319-709 where tagFull starts with " operates"
for card_id in range(319, 710):
    match = re.search(
        rf"({{ id: {card_id},.*?company: '([^']+)',.*?)"
        rf"(tagFull: \" operates)",
        content, re.DOTALL
    )
    
    if match:
        company = match.group(2)
        old = f'tagFull: " operates'
        new = f'tagFull: "{company} operates'
        
        # Replace only this occurrence
        old_full = match.group(0)
        new_full = old_full.replace(old, new)
        content = content.replace(old_full, new_full, 1)
        
        updated += 1
        if updated <= 10:
            print(f"  Card {card_id}: Added '{company}'")

print(f"\n=== SUMMARY ===")
print(f"Fixed {updated} company names")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

