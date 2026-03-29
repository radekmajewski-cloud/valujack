#!/usr/bin/env python3
"""
ValuJack Weekly AI Scan — Export Script
Exports all ELIGIBLE cards for AI analysis.
Run: python3 export_for_ai_scan.py
Output: ai_scan/cards_for_scan.txt
"""

import re, os
from datetime import datetime

CARDS_JS = '/Users/radekmajewski/Downloads/ValuJack/public/cards.js'
OUTPUT_DIR = '/Users/radekmajewski/Downloads/ValuJack/ai_scan'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'cards_for_scan.txt')

os.makedirs(OUTPUT_DIR, exist_ok=True)

content = open(CARDS_JS).read()

card_pattern = re.compile(
    r'\{\s*id:\s*(\d+).*?'
    r"type:\s*'(\w+)'.*?"
    r"company:\s*'([^']+)'.*?"
    r"ticker:\s*'([^']+)'.*?"
    r"sector:\s*'([^']+)'.*?"
    r"country:\s*'([^']*)'.*?"
    r"currency:\s*'([^']*)'.*?"
    r"stars:\s*(\d+).*?"
    r"fairValue:\s*([\d.]+)",
    re.DOTALL
)

cards = []
for m in card_pattern.finditer(content):
    card = {
        'id': int(m.group(1)),
        'type': m.group(2),
        'company': m.group(3),
        'ticker': m.group(4),
        'sector': m.group(5),
        'country': m.group(6),
        'currency': m.group(7),
        'stars': int(m.group(8)),
        'fairValue': float(m.group(9)),
    }
    # Apply same eligibility filters as draw logic
    stars = card['stars']
    ctype = card['type']
    min_stars = 2
    if stars < min_stars:
        continue
    cards.append(card)

type_order = {'KING': 0, 'JACK': 1, 'QUEEN': 2, 'ACE': 3, 'JOKER': 4, 'TWO': 5}
cards.sort(key=lambda c: (type_order.get(c['type'], 9), c['company']))

with open(OUTPUT_FILE, 'w') as f:
    f.write(f"VALUJACK WEEKLY AI SCAN\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    f.write(f"Eligible cards: {len(cards)}\n")
    f.write("=" * 60 + "\n\n")
    f.write("""INSTRUCTIONS:
For each company, search current news and provide:

---
ID: [id] | [TICKER] | [COMPANY] | [TYPE] | [SECTOR] | [COUNTRY]
NEWS: [1-2 sentence summary of most relevant recent news]
SHORT-TERM: [POSITIVE/NEUTRAL/NEGATIVE] — [reason]
LONG-TERM: [NONE/LOW/MEDIUM/HIGH impact] — [reason]
THESIS: [INTACT/UNCERTAIN/BROKEN]
STATUS: [BOOST/NEUTRAL/WARN/BLOCK]
SCORE: [number -10 to +10]
REASON: [1 sentence plain English for the user]
OPPORTUNITY: [YES/NO] — [if YES, why this is a buying opportunity]
---

KEY RULES:
- KING: dividend cut = BLOCK
- JACK: momentum broken = WARN/BLOCK
- QUEEN: ROIC collapse = BLOCK
- ACE: F-score deteriorating = BLOCK
- JOKER: growth slowing = BLOCK
- TWO: recovery stalled = WARN
- Short-term noise + intact thesis = BOOST (buying opportunity)
- Fundamental moat change = BLOCK
- Same news can be BOOST for one type, BLOCK for another
- Search web before assessing — never assume

""")

    current_type = None
    for c in cards:
        if c['type'] != current_type:
            current_type = c['type']
            names = {'KING':'KING — Dividends','JACK':'JACK — Momentum',
                     'QUEEN':'QUEEN — Magic Formula','ACE':'ACE — F-Score',
                     'JOKER':'JOKER — Growth','TWO':'TWO — Contrarian'}
            f.write(f"\n{'='*60}\n{names.get(current_type, current_type)}\n{'='*60}\n\n")
        f.write(f"ID:{c['id']} | {c['ticker']} | {c['company']} | {c['sector']} | {c['country']} | Stars:{c['stars']} | FV:{c['fairValue']} {c['currency']}\n")

print(f"Exported {len(cards)} eligible cards to {OUTPUT_FILE}")
