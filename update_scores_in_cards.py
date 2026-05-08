import json
import re
from datetime import datetime

# Load scores
with open('scores_20260406.json') as f:
    scores_data = json.load(f)

# Create ticker -> score mapping
score_map = {}
for company in scores_data['companies']:
    score_map[company['ticker']] = {
        'score': company['final_score'],
        'stars': company['stars'],
        'strategy': company['strategy']
    }

print(f"Loaded {len(score_map)} scored companies")

# Read cards.js
with open('public/cards.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Backup
backup_file = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup_file, 'w', encoding='utf-8') as f:
    f.write(content)
print(f"Backup created: {backup_file}")

# Update cards with scores
updated = 0
for ticker, info in score_map.items():
    # Find card with this ticker and update stars
    pattern = f"(ticker: '{ticker}'.*?stars: )\\d+"
    matches = list(re.finditer(pattern, content))
    
    if matches:
        for match in matches:
            old_stars = content[match.start():match.end()].split('stars: ')[1]
            new_stars = str(info['stars'])
            
            if old_stars != new_stars:
                content = content[:match.start()] + f"ticker: '{ticker}', stars: {new_stars}" + content[match.end():]
                updated += 1

print(f"Updated {updated} cards with new stars")

# Write updated cards.js
with open('public/cards.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✓ cards.js updated successfully!")

