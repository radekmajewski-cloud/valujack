#!/usr/bin/env python3
import re
import shutil
from datetime import datetime

filepath = 'public/cards.js'

# Backup
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup = f'{filepath}.backup_{timestamp}'
shutil.copy2(filepath, backup)
print(f"Backup: {backup}")

with open(filepath, 'r') as f:
    content = f.read()

# Add AI scores to ESEA only (id: 1)
# Pattern: find "ticker: 'ESEA'" then find "stars: 5" on same line
pattern = r"(yahooTicker: 'ESEA', stars: 5)"
replacement = r"\1, aiScanScore: 7, aiScanStars: 4.2, compositeStars: 4.59, aiStatus: 'BOOST', aiScanDate: '2026-03-27'"

if pattern in content:
    print("ERROR: Pattern not found - trying different approach")
else:
    content = re.sub(pattern, replacement, content)
    print("✓ Added AI scores to ESEA")

with open(filepath, 'w') as f:
    f.write(content)

# Verify
with open(filepath, 'r') as f:
    verify = f.read()
    
if 'aiScanScore: 7' in verify and "ticker: 'ESEA'" in verify:
    print("✅ VERIFIED: AI scores added successfully")
    print("\nESEA now has:")
    print("  - aiScanScore: 7")
    print("  - compositeStars: 4.59")
    print("  - aiStatus: BOOST")
else:
    print("❌ FAILED: AI scores not found")

print(f"\nTo verify manually:")
print(f"  grep -A1 \"ticker: 'ESEA'\" public/cards.js | grep aiScanScore")
