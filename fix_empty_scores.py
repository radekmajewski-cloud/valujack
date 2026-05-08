import json
import re
from datetime import datetime

# Load scoring data
with open('scores_20260406.json') as f:
    scores_data = json.load(f)

component_map = {}
for c in scores_data['companies']:
    component_map[c['ticker']] = {
        'strategy': c['strategy'],
        'components': c['components']
    }

print(f"Loaded {len(component_map)} scored companies\n")

# Read cards.js
with open('public/cards.js', 'r') as f:
    content = f.read()

# Backup
backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

RADAR_MAP = {
    'KING': ['Dividend', 'Fair Price', 'Profit', 'Stable Earnings', 'Low Debt'],
    'JACK': ['Earnings Growth', 'Momentum', 'Profit', 'Fair Price', 'Stable Earnings'],
    'QUEEN': ['Profit', 'Fair Price', 'Earnings Growth', 'Stable Earnings', 'Low Debt'],
    'ACE': ['Growth', 'Profit', 'Low Debt', 'Fair Price', 'Stable Earnings'],
    'JOKER': ['Growth', 'Profit', 'Low Debt', 'Fair Price', 'Momentum']
}

COMPONENT_TO_SCORE = {
    'Dividend': 'dividend_health',
    'Fair Price': 'fair_value',
    'Profit': 'business_quality',
    'Stable Earnings': 'earnings_stability',
    'Low Debt': 'financial_health',
    'Earnings Growth': 'growth',
    'Growth': 'growth',
    'Momentum': 'momentum'
}

updated = 0

# Find cards with empty scores - simpler pattern
pattern = r"ticker: '([^']+)'[^}]+?scores: \[\]"

def add_scores(match):
    global updated
    ticker = match.group(1)
    
    if ticker not in component_map:
        return match.group(0)
    
    strategy = component_map[ticker]['strategy']
    components = component_map[ticker]['components']
    
    if strategy not in RADAR_MAP:
        return match.group(0)
    
    # Build scores array
    scores_list = []
    for label in RADAR_MAP[strategy]:
        comp_key = COMPONENT_TO_SCORE.get(label)
        if comp_key and comp_key in components:
            value = int(components[comp_key] / 10)
            scores_list.append(f"{{ l: '{label}', v: {value}, max: 10, color: '#5B8FD4', raw: '{label}', rawV: '{value}/10' }}")
    
    if scores_list:
        scores_str = "scores: [" + ", ".join(scores_list) + "]"
        updated += 1
        if updated <= 10:
            print(f"  {ticker:8s} ({strategy})")
        return match.group(0).replace("scores: []", scores_str)
    
    return match.group(0)

content = re.sub(pattern, add_scores, content)

print(f"\n✓ Added radar scores to {updated} cards")
print(f"✓ Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

