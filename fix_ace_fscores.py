import csv
import re
from datetime import datetime

# Load F-Score data
ace_fscores = {}
with open('Company data/aces 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    for row in reader:
        ticker = row.get('Info - Ticker', '').strip()
        fscore = row.get('F-Score - Point', '').strip()
        if ticker and fscore:
            ace_fscores[ticker] = fscore

print(f"Loaded {len(ace_fscores)} F-Scores\n")

with open('public/cards.js', 'r') as f:
    content = f.read()

backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

updated = 0

# Fix ACE cards by card ID
for card_id in range(1, 710):
    pattern = rf"({{ id: {card_id}, type: 'ACE'.*?ticker: '([^']+)'.*?{{ l: 'F-Score', v: ')—(' }})"
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        ticker = match.group(2)
        
        if ticker in ace_fscores:
            fscore = ace_fscores[ticker]
            new_text = match.group(1) + fscore + match.group(3)
            content = content.replace(match.group(0), new_text, 1)
            updated += 1
            print(f"  Card {card_id} ({ticker}): F-Score = {fscore}")

print(f"\nUpdated {updated} ACE cards")
print(f"Backup: {backup}")

with open('public/cards.js', 'w') as f:
    f.write(content)

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")
    import shutil
    shutil.copy(backup, 'public/cards.js')
    print("✓ Auto-restored")

