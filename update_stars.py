import json
import re
from datetime import datetime

# Load scores
with open('scores_20260406.json') as f:
    scores_data = json.load(f)

score_map = {c['ticker']: c['stars'] for c in scores_data['companies']}
print(f"Loaded {len(score_map)} scored companies\n")

# Read cards.js
with open('public/cards.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
backup_file = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup_file, 'w', encoding='utf-8') as f:
    f.write(content)

# Find and update stars
updated = 0
pattern = r"{ id: (\d+),.*?yahooTicker: '([^']+)', stars: (\d+)"

def replace_stars(match):
    global updated
    card_id = match.group(1)
    ticker = match.group(2)
    old_stars = match.group(3)
    
    if ticker in score_map:
        new_stars = score_map[ticker]
        if int(old_stars) != new_stars:
            updated += 1
            print(f"Card {card_id} ({ticker}): {old_stars}★ → {new_stars}★")
        return match.group(0).replace(f"stars: {old_stars}", f"stars: {new_stars}")
    return match.group(0)

content = re.sub(pattern, replace_stars, content)

print(f"\n✓ Updated {updated} cards")

# Write
with open('public/cards.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✓ Saved to public/cards.js")
print(f"✓ Backup: {backup_file}")

