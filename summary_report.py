import re

with open('public/cards.js', 'r') as f:
    content = f.read()

# Find all new cards (id >= 319)
new_cards = []
for match in re.finditer(r"{ id: (\d+), type: '(\w+)'.*?company: '([^']+)'.*?ticker: '([^']+)'.*?fairValue: ([\d.]+)", content):
    card_id = int(match.group(1))
    if card_id >= 319:
        new_cards.append({
            'id': card_id,
            'type': match.group(2),
            'company': match.group(3),
            'ticker': match.group(4),
            'fv': float(match.group(5))
        })

print(f"\n=== NEW COMPANIES ADDED: {len(new_cards)} cards ===\n")

by_type = {}
for c in new_cards:
    by_type[c['type']] = by_type.get(c['type'], 0) + 1

print("Breakdown by strategy:")
for t in ['KING', 'JACK', 'QUEEN', 'ACE', 'JOKER', 'TWO']:
    print(f"  {t:6s}: {by_type.get(t, 0):3d} cards")

print(f"\nFirst 20 new companies:")
print(f"{'ID':<5} {'Type':<6} {'Ticker':<10} {'Company':<50} {'Fair Value'}")
print("-" * 90)

for c in new_cards[:20]:
    print(f"{c['id']:<5} {c['type']:<6} {c['ticker']:<10} {c['company'][:50]:<50} {c['fv']:.2f}")

print(f"\n... and {len(new_cards)-20} more companies (IDs {new_cards[20]['id']}-{new_cards[-1]['id']})")
print(f"\n✓ All {len(new_cards)} new companies successfully added to ValuJack!")
