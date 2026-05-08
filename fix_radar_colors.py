import json
import re
from datetime import datetime

# Color palette for radar dimensions
COLORS = ['#5B8FD4', '#D4884A', '#4CAF82', '#9B6ED4', '#C4784A']

# Read cards.js
with open('public/cards.js', 'r') as f:
    content = f.read()

# Backup
backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# Find all scores arrays and fix colors
pattern = r"(scores: \[)([^\]]+)(\])"

def fix_colors(match):
    global updated
    prefix = match.group(1)
    scores_content = match.group(2)
    suffix = match.group(3)
    
    # Split into individual score objects
    score_items = re.findall(r'\{[^}]+\}', scores_content)
    
    if len(score_items) == 0:
        return match.group(0)  # Empty scores array
    
    # Assign colors
    fixed_items = []
    for i, item in enumerate(score_items):
        color = COLORS[i % len(COLORS)]
        # Replace the color value
        fixed_item = re.sub(r"color: '[^']*'", f"color: '{color}'", item)
        fixed_items.append(fixed_item)
    
    updated += 1
    return prefix + ", ".join(fixed_items) + suffix

content = re.sub(pattern, fix_colors, content)

print(f"✓ Fixed colors in {updated} cards")
print(f"✓ Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)
