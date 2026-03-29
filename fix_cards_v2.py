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

# Remove AI scores from APP
print("1. Removing from APP...")
content = re.sub(
    r"(ticker: 'APP'[^}]*stars: 3), aiScanScore: 7, aiScanStars: 4\.2, compositeStars: 4\.14, aiStatus: 'BOOST', aiScanDate: '2026-03-27'",
    r"\1",
    content
)

# Remove AI scores from B7C0
print("2. Removing from B7C0...")
content = re.sub(
    r"(ticker: 'B7C0'[^}]*stars: 2), aiScanScore: 8, aiScanStars: 4\.4, compositeStars: 3\.38, aiStatus: 'BOOST', aiScanDate: '2026-03-27'",
    r"\1",
    content
)

# Add to APH
print("3. Adding to APH...")
content = re.sub(
    r"(yahooTicker: 'APH',\s+stars: 2)",
    r"\1, aiScanScore: 7, aiScanStars: 4.2, compositeStars: 4.14, aiStatus: 'BOOST', aiScanDate: '2026-03-27'",
    content
)

# Add to CRUS  
print("4. Adding to CRUS...")
content = re.sub(
    r"(yahooTicker: 'CRUS',\s+stars: 2)",
    r"\1, aiScanScore: 8, aiScanStars: 4.4, compositeStars: 3.38, aiStatus: 'BOOST', aiScanDate: '2026-03-27'",
    content
)

with open(filepath, 'w') as f:
    f.write(content)

print("\n✅ Done!")
print("vercel --prod")
