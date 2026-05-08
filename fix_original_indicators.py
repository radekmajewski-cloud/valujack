import re
from datetime import datetime

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# Process original cards 1-318
for card_id in range(1, 319):
    match = re.search(
        rf"({{ id: {card_id}, type: '(\w+)',.*?)"
        rf"(ind1l: '([^']+)', ind1v: '([^']+)', ind2l: '([^']+)', ind2v: '([^']+)')",
        content, re.DOTALL
    )
    
    if match:
        strategy = match.group(2)
        old_indicators = match.group(3)
        ind1l_current = match.group(4)
        ind1v_current = match.group(5)
        ind2l_current = match.group(6)
        ind2v_current = match.group(7)
        
        # Determine what ind1l SHOULD be for this strategy
        correct_ind1l = {
            'KING': 'DIVIDEND %',
            'JACK': 'PRICE STRENGTH',
            'QUEEN': 'ROIC',
            'ACE': 'F-SCORE',
            'JOKER': 'EPS GROWTH',
            'TWO': 'ROIC'
        }.get(strategy)
        
        # Only update if ind1l is wrong
        if correct_ind1l and ind1l_current != correct_ind1l:
            # Keep current values, just fix labels
            # We need to extract the right value from metrics or scores
            # For now, keep the existing value but fix the label
            
            # Map old label to new label for this strategy
            if strategy == 'KING' and ind1l_current != 'DIVIDEND %':
                # Find dividend value in metrics
                div_match = re.search(r"{ l: 'Div(?:idend)?\s*(?:Yield)?', v: '([^']+)'", match.group(0))
                if div_match:
                    new_ind1v = div_match.group(1)
                    new_indicators = f"ind1l: 'DIVIDEND %', ind1v: '{new_ind1v}', ind2l: '{ind2l_current}', ind2v: '{ind2v_current}'"
                    
                    old_full = match.group(0)
                    new_full = old_full.replace(old_indicators, new_indicators)
                    content = content.replace(old_full, new_full, 1)
                    updated += 1
                    if updated <= 10:
                        print(f"  Card {card_id} (KING): Fixed ind1")
            
            elif strategy == 'TWO' and ind1l_current == '1Y PERFORMANCE':
                # Find ROIC value in metrics
                roic_match = re.search(r"{ l: 'ROIC', v: '([^']+)'", match.group(0))
                if roic_match:
                    new_ind1v = roic_match.group(1)
                    new_indicators = f"ind1l: 'ROIC', ind1v: '{new_ind1v}', ind2l: '{ind2l_current}', ind2v: '{ind2v_current}'"
                    
                    old_full = match.group(0)
                    new_full = old_full.replace(old_indicators, new_indicators)
                    content = content.replace(old_full, new_full, 1)
                    updated += 1
                    if updated <= 10:
                        print(f"  Card {card_id} (TWO): Fixed ind1")

print(f"\n=== SUMMARY ===")
print(f"Updated {updated} original card indicators")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

