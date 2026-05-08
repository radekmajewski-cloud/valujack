import csv
import re
from datetime import datetime

# Load CSV data
csv_data = {}
for strategy_file in ['kings', 'jacks', 'queens', 'aces', 'jokers', 'twos']:
    try:
        with open(f'Company data/{strategy_file} 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                ticker = row.get('Info - Ticker', '').strip()
                if ticker:
                    csv_data[ticker] = {
                        'company': row.get('Info - Name', ''),
                        'industry': row.get('Info - Industry', ''),
                        'sector': row.get('Info - Sector', '')
                    }
    except:
        pass

print(f"Loaded {len(csv_data)} companies from CSVs\n")

# Read cards
with open('public/cards.js', 'r') as f:
    content = f.read()

# Backup
backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# Process cards 319-709
for card_id in range(319, 710):
    match = re.search(
        rf"({{ id: {card_id}, type: '(\w+)',.*?ticker: '([^']+)',.*?)"
        rf"(tagFull: \"[^\"]+\", )"
        rf"(pick: '[^']+', pickBold: '[^']+', )"
        rf"(pickFull: \"[^\"]+\")",
        content, re.DOTALL
    )
    
    if match:
        strategy = match.group(2)
        ticker = match.group(3)
        
        if ticker in csv_data:
            data = csv_data[ticker]
            company = data['company']
            industry = data['industry']
            
            # Generate descriptions
            if strategy == 'KING':
                tagFull = f"{company} operates in the {industry.lower()} industry. The company focuses on stable operations and consistent performance. It maintains a track record of regular dividend payments."
                pickFull = "A steady dividend payer with reliable operations and strong cash generation."
            
            elif strategy == 'JACK':
                tagFull = f"{company} works in {industry.lower()}. The business shows strong price momentum and improving market position. It operates with a focus on growth."
                pickFull = "A momentum stock with accelerating performance and expanding opportunities."
            
            elif strategy == 'QUEEN':
                tagFull = f"{company} operates in the {industry.lower()} sector. The company combines quality operations with reasonable valuation. It serves its market with established products and services."
                pickFull = "A quality business with strong fundamentals trading at fair value."
            
            elif strategy == 'ACE':
                tagFull = f"{company} is in the {industry.lower()} industry. The business generates solid earnings while maintaining efficient operations. It focuses on consistent execution."
                pickFull = "An undervalued company with strong fundamentals and improving prospects."
            
            elif strategy == 'JOKER':
                tagFull = f"{company} operates in {industry.lower()}. The company shows rapid growth with expanding revenue. It targets growing market opportunities."
                pickFull = "A fast-growing business with strong momentum and significant upside potential."
            
            elif strategy == 'TWO':
                tagFull = f"{company} works in {industry.lower()}. The business experienced challenges but maintains solid fundamentals. It shows signs of recovery and stabilization."
                pickFull = "A recovery opportunity with improving trends and solid underlying business."
            
            # Replace
            old_text = match.group(0)
            new_text = (
                match.group(1) +
                f'tagFull: "{tagFull}", ' +
                match.group(5) +
                f'pickFull: "{pickFull}"'
            )
            
            content = content.replace(old_text, new_text, 1)
            updated += 1
            
            if updated <= 10:
                print(f"  {ticker} ({strategy}): Updated")

print(f"\n=== SUMMARY ===")
print(f"Updated {updated} card descriptions")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

