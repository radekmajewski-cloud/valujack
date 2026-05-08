#!/usr/bin/env python3
import re
from datetime import datetime

# Read cards.js
with open('public/cards.js', 'r', encoding='utf-8') as f:
    content = f.read()

print("=== REMOVING DUPLICATE CARDS ===\n")

# Cards to remove by ID
cards_to_remove = {
    12: ('BETS B', 'Betsson AB - keeping TWO #250'),
    51: ('GTT', 'Gaztransport - duplicate of 9TG'),
    74: ('STRA', 'Strategic Education - duplicate of SQE'),
    94: ('RE0', 'Hafnia Ltd - duplicate of HAFN'),
    112: ('S0QA', 'Scorpio Tankers - duplicate of STNG'),
    131: ('HAFNI', 'Hafnia Limited - duplicate of HAFN'),
    253: ('DCBO', 'Docebo Inc - duplicate'),
    294: ('JNJ', 'Johnson & Johnson - duplicate'),
    297: ('TRMD A', 'TORM - duplicate'),
    315: ('BA.', 'BAE Systems - duplicate'),
    316: ('LDO', 'Leonardo SpA - duplicate'),
    317: ('UHS', 'Universal Health - duplicate'),
}

removed = 0

for card_id, (ticker, reason) in cards_to_remove.items():
    pattern = r'\{\s*id:\s*' + str(card_id) + r',.*?\},\s*\n'
    matches = list(re.finditer(pattern, content, re.DOTALL))
    
    if matches:
        for match in matches:
            content = content.replace(match.group(0), '')
            print(f"Removed ID {card_id:3d}: {reason}")
            removed += 1

# Backup
backup = f'public/cards.js.backup_dedup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open('public/cards.js', 'r') as f:
    original = f.read()
with open(backup, 'w') as f:
    f.write(original)

# Write cleaned file
with open('public/cards.js', 'w', encoding='utf-8') as f:
    f.write(content)

remaining = len(re.findall(r'\{\s*id:', content))

print(f"\n=== SUMMARY ===")
print(f"Removed: {removed} duplicate cards")
print(f"Remaining: {remaining} cards")
print(f"Backup: {backup}")
