#!/usr/bin/env python3
import shutil
from datetime import datetime

filepath = 'public/index.html'

# Backup
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup = f'{filepath}.backup_{timestamp}'
shutil.copy2(filepath, backup)
print(f"Backup: {backup}")

# Read
with open(filepath, 'r') as f:
    content = f.read()

# Replace the eligibility logic to use compositeStars
old_code = '''              // Minimum 3 stars to appear in rotation (TWO cards use lower threshold — contrarian strategy)
              if (c.type === 'TWO') {
                  if ((c.stars || 0) < 2) return false;
              } else {
                  if ((c.stars || 0) < 3) return false;
              }'''

new_code = '''              // Use compositeStars if available (AI scan integrated), fallback to stars
              const effectiveStars = c.compositeStars !== undefined ? c.compositeStars : (c.stars || 0);
              
              // Minimum threshold: 3.5 composite stars, OR high AI boost override (7+ with 3.3+)
              const meetsThreshold = effectiveStars >= 3.5 || 
                                    (c.aiScanScore >= 7 && effectiveStars >= 3.3);
              
              if (c.type === 'TWO') {
                  if (effectiveStars < 2) return false;
              } else {
                  if (!meetsThreshold) return false;
              }'''

if old_code in content:
    content = content.replace(old_code, new_code)
    print("✓ Updated eligibility logic to use compositeStars")
else:
    print("✗ Could not find old code to replace")
    exit(1)

# Write
with open(filepath, 'w') as f:
    f.write(content)

print("\nSUCCESS! Now deploy: vercel --prod")
