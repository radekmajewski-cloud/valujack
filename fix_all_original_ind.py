import re
from datetime import datetime

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

# Target labels for each strategy
TARGET_IND1 = {
    'KING': 'DIVIDEND %',
    'JACK': 'PRICE STRENGTH', 
    'QUEEN': 'ROIC',
    'ACE': 'F-SCORE',
    'JOKER': 'EPS GROWTH',
    'TWO': 'ROIC'
}

updated = 0

# Process ALL cards 1-709
for card_id in range(1, 710):
    match = re.search(
        rf"({{ id: {card_id}, type: '(\w+)',.*?)"
        rf"(ind1l: '([^']+)', ind1v: '([^']+)', ind2l: '([^']+)', ind2v: '([^']+)')",
        content, re.DOTALL
    )
    
    if match:
        strategy = match.group(2)
        old_indicators = match.group(3)
        current_ind1l = match.group(4)
        current_ind1v = match.group(5)
        ind2l = match.group(6)
        ind2v = match.group(7)
        
        target_ind1l = TARGET_IND1.get(strategy)
        
        # If ind1l doesn't match target, find the correct value from metrics
        if target_ind1l and current_ind1l != target_ind1l:
            card_text = match.group(0)
            new_ind1v = None
            
            # Search for the target metric in the card's metrics array
            if target_ind1l == 'DIVIDEND %':
                metric_match = re.search(r"{ l: '[Dd]iv(?:idend)?\s*(?:[Yy]ield)?', v: '([^']+)'", card_text)
                if metric_match:
                    new_ind1v = metric_match.group(1)
            
            elif target_ind1l == 'ROIC':
                metric_match = re.search(r"{ l: 'ROIC', v: '([^']+)'", card_text)
                if metric_match:
                    new_ind1v = metric_match.group(1)
            
            elif target_ind1l == 'F-SCORE':
                metric_match = re.search(r"{ l: 'F-Score', v: '([^']+)'", card_text)
                if metric_match:
                    new_ind1v = metric_match.group(1)
            
            elif target_ind1l == 'EPS GROWTH':
                # Check epsGrowth field
                eps_match = re.search(r"epsGrowth: '([^']+)'", card_text)
                if eps_match:
                    new_ind1v = eps_match.group(1)
            
            elif target_ind1l == 'PRICE STRENGTH':
                # Check rsRating or 1y performance
                rs_match = re.search(r"rsRating: '([^']+)'", card_text)
                if rs_match:
                    new_ind1v = rs_match.group(1)
            
            if new_ind1v:
                new_indicators = f"ind1l: '{target_ind1l}', ind1v: '{new_ind1v}', ind2l: '{ind2l}', ind2v: '{ind2v}'"
                
                old_full = match.group(0)
                new_full = old_full.replace(old_indicators, new_indicators)
                content = content.replace(old_full, new_full, 1)
                updated += 1
                
                if updated <= 15:
                    print(f"  Card {card_id} ({strategy}): {current_ind1l} → {target_ind1l}")

print(f"\n=== SUMMARY ===")
print(f"Updated {updated} card indicators")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

