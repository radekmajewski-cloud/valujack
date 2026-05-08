import re
from datetime import datetime

# Read cards
with open('public/cards.js', 'r') as f:
    content = f.read()

# Backup
backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

# Placeholder scores for TWO strategy (contrarian/value)
two_placeholder = [
    { 'l': 'Profit', 'v': 5, 'max': 10, 'color': '#5B8FD4', 'raw': 'Profit', 'rawV': '5/10' },
    { 'l': 'Fair Price', 'v': 7, 'max': 10, 'color': '#D4884A', 'raw': 'Fair Price', 'rawV': '7/10' },
    { 'l': 'Stable Earnings', 'v': 5, 'max': 10, 'color': '#4CAF82', 'raw': 'Stable Earnings', 'rawV': '5/10' },
    { 'l': 'Low Debt', 'v': 6, 'max': 10, 'color': '#9B6ED4', 'raw': 'Low Debt', 'rawV': '6/10' },
    { 'l': 'Recovery', 'v': 5, 'max': 10, 'color': '#C4784A', 'raw': 'Recovery', 'rawV': '5/10' }
]

# Other strategies get generic placeholder
generic_placeholder = [
    { 'l': 'Quality', 'v': 5, 'max': 10, 'color': '#5B8FD4', 'raw': 'Quality', 'rawV': '5/10' },
    { 'l': 'Value', 'v': 5, 'max': 10, 'color': '#D4884A', 'raw': 'Value', 'rawV': '5/10' },
    { 'l': 'Growth', 'v': 5, 'max': 10, 'color': '#4CAF82', 'raw': 'Growth', 'rawV': '5/10' },
    { 'l': 'Momentum', 'v': 5, 'max': 10, 'color': '#9B6ED4', 'raw': 'Momentum', 'rawV': '5/10' },
    { 'l': 'Safety', 'v': 5, 'max': 10, 'color': '#C4784A', 'raw': 'Safety', 'rawV': '5/10' }
]

def score_to_str(scores):
    items = []
    for s in scores:
        items.append(f"{{ l: '{s['l']}', v: {s['v']}, max: {s['max']}, color: '{s['color']}', raw: '{s['raw']}', rawV: '{s['rawV']}' }}")
    return '[' + ', '.join(items) + ']'

updated = 0

# Find cards with scores: []
pattern = r"({ id: \d+, type: '(\w+)',.*?)(scores: \[\])(,)"

def add_scores(match):
    global updated
    prefix = match.group(1)
    card_type = match.group(2)
    suffix = match.group(4)
    
    # Choose appropriate placeholder
    if card_type == 'TWO':
        scores_str = score_to_str(two_placeholder)
    else:
        scores_str = score_to_str(generic_placeholder)
    
    updated += 1
    if updated <= 10:
        print(f"  Card {card_type}: added placeholder scores")
    
    return prefix + f"scores: {scores_str}" + suffix

content = re.sub(pattern, add_scores, content, flags=re.DOTALL)

print(f"\n=== SUMMARY ===")
print(f"Added placeholder scores to {updated} cards")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

# Syntax check
import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

