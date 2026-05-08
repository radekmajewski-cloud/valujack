import csv
import re

print("🔧 Adding EPS Growth and Price Strength to JOKER card metrics")
print("="*80)

with open('public/cards.js', 'r') as f:
    content = f.read()

# Backup
import shutil
shutil.copy('public/cards.js', 'public/cards.js.bak_before_joker_metrics')
print("✅ Backup created\n")

fixed = 0
cards = re.split(r'(?=\{ id:)', content)

for card_chunk in cards:
    if "type: 'JOKER'" not in card_chunk:
        continue
    
    ticker_match = re.search(r"ticker: '([^']+)'", card_chunk)
    if not ticker_match:
        continue
    
    ticker = ticker_match.group(1)
    
    # Get epsGrowth and rsRating from fields
    eps_match = re.search(r"epsGrowth: '([^']+)'", card_chunk)
    rs_match = re.search(r"rsRating: '([^']+)'", card_chunk)
    
    if not eps_match and not rs_match:
        continue
    
    new_card = card_chunk
    changes = []
    
    # Find metrics array
    metrics_match = re.search(r"(metrics: \[.*?)(}\])", new_card)
    if metrics_match:
        prefix = metrics_match.group(1)
        
        # Add EPS Growth if exists and not already in metrics
        if eps_match and "l: 'EPS Growth'" not in new_card:
            eps_val = eps_match.group(1)
            prefix += "}, { l: 'EPS Growth', v: '" + eps_val + "' "
            changes.append(f'EPS Growth={eps_val}')
        
        # Add Price Strength if exists and not already in metrics
        if rs_match and "l: 'Price Strength'" not in new_card:
            rs_val = rs_match.group(1)
            prefix += "}, { l: 'Price Strength', v: '" + rs_val + "' "
            changes.append(f'Price Strength={rs_val}')
        
        if changes:
            new_metrics = prefix + "}]"
            new_card = new_card.replace(metrics_match.group(0), new_metrics)
            content = content.replace(card_chunk, new_card)
            fixed += 1
            print(f"✅ {ticker:15} | {', '.join(changes)}")

with open('public/cards.js', 'w') as f:
    f.write(content)

print(f"\n{'='*80}")
print(f"✅ Fixed {fixed} JOKER cards")
