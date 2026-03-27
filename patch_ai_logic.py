#!/usr/bin/env python3
"""
ValuJack — Patch draw logic to respect AI status (BLOCK/WARN/BOOST)
Run once after building the AI scan system.
"""

import shutil

src = '/Users/radekmajewski/Downloads/ValuJack/public/index.html'
shutil.copy(src, src + '.bak_before_ai_logic')
content = open(src).read()

# 1. Add AI status filter to eligibleCards
old = """              // Minimum 3 stars to appear in rotation (TWO cards use lower threshold — contrarian strategy)
              if (c.type === 'TWO') {
                  if ((c.stars || 0) < 2) return false;
              } else {
                  if ((c.stars || 0) < 3) return false;
              }"""

new = """              // Minimum 3 stars to appear in rotation (TWO cards use lower threshold — contrarian strategy)
              if (c.type === 'TWO') {
                  if ((c.stars || 0) < 2) return false;
              } else {
                  if ((c.stars || 0) < 3) return false;
              }

              // AI sentiment filter — block cards with critical issues
              if (c.aiStatus === 'BLOCK') return false;"""

if old in content:
    content = content.replace(old, new)
    print('Fix 1 done - BLOCK cards excluded from rotation')
else:
    print('ERROR fix 1 - pattern not found')

# 2. Boost high AI score cards by temporarily raising their stars in pool sorting
old2 = "const sortedEligible = [...eligibleCards].sort((a, b) => (b.stars || 0) - (a.stars || 0));"
new2 = """// Apply AI boost/warn to effective star rating for sorting
        const effectiveStars = (c) => {
            const base = c.stars || 0;
            if (c.aiStatus === 'BOOST') return Math.min(5, base + 1);
            if (c.aiStatus === 'WARN')  return Math.max(1, base - 1);
            return base;
        };
        const sortedEligible = [...eligibleCards].sort((a, b) => effectiveStars(b) - effectiveStars(a));"""

if old2 in content:
    content = content.replace(old2, new2)
    print('Fix 2 done - BOOST/WARN adjusts sort priority')
else:
    print('ERROR fix 2 - pattern not found')

open(src, 'w').write(content)
print('\nDone - AI logic patched into draw system')
print('Run: vercel --prod')
