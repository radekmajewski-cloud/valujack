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

# Step 1: Remove AI scores from APP (id: 238)
print("\n1. Removing AI scores from APP (wrong card)...")
content = re.sub(
    r"(ticker: 'APP'[^\n]*\n[^\n]*stars: \d+), aiScanScore: 7, aiScanStars: 4\.2, compositeStars: 4\.14, aiStatus: 'BOOST', aiScanDate: '2026-03-27'",
    r"\1",
    content
)

# Step 2: Remove AI scores from B7C0  
print("2. Removing AI scores from B7C0 (wrong card)...")
content = re.sub(
    r"(ticker: 'B7C0'[^\n]*\n[^\n]*stars: \d+), aiScanScore: 8, aiScanStars: 4\.4, compositeStars: 3\.38, aiStatus: 'BOOST', aiScanDate: '2026-03-27'",
    r"\1",
    content
)

# Step 3: Add AI scores to APH (correct card)
print("3. Adding AI scores to APH (correct card)...")
content = re.sub(
    r"(ticker: 'APH'[^\n]*\n[^\n]*)(stars: 2)",
    r"\1\2, aiScanScore: 7, aiScanStars: 4.2, compositeStars: 4.14, aiStatus: 'BOOST', aiScanDate: '2026-03-27'",
    content
)

# Step 4: Add AI scores to CRUS (correct card)
print("4. Adding AI scores to CRUS (correct card)...")
content = re.sub(
    r"(ticker: 'CRUS'[^\n]*\n[^\n]*)(stars: 2)",
    r"\1\2, aiScanScore: 8, aiScanStars: 4.4, compositeStars: 3.38, aiStatus: 'BOOST', aiScanDate: '2026-03-27'",
    content
)

with open(filepath, 'w') as f:
    f.write(content)

print("\n✅ SUCCESS! Fixed all 4 cards")
print("Now: vercel --prod")
