import re

with open('public/cards.js', 'r', encoding='utf-8') as f:
    content = f.read()

cards = []
for match in re.finditer(r'{ id: (\d+),.*?type: \'(\w+)\'.*?company: \'([^\']+)\'.*?ticker: \'([^\']+)\'.*?fairValue: ([\d.]+).*?stars: (\d).*?sector: \'([^\']+)\'.*?country: \'([^\']+)\'', content):
    card_id = int(match.group(1))
    if card_id >= 319:
        cards.append({
            'id': card_id,
            'type': match.group(2),
            'company': match.group(3),
            'ticker': match.group(4),
            'fairValue': match.group(5),
            'stars': match.group(6),
            'sector': match.group(7),
            'country': match.group(8)
        })

print(f'NEW COMPANIES REPORT - {len(cards)} cards (IDs 319-709)')
print('=' * 100)
print(f"{'ID':<5} {'Type':<6} {'Ticker':<10} {'Company':<40} {'Fair Value':<12} {'Stars'} {'Country'}")
print('-' * 100)

for c in cards[:50]:
    print(f"{c['id']:<5} {c['type']:<6} {c['ticker']:<10} {c['company'][:40]:<40} {c['fairValue']:<12} {c['stars']:<5} {c['country']}")

print(f"\n... and {len(cards)-50} more cards")
print(f"\nBreakdown by strategy:")

by_type = {}
for c in cards:
    by_type[c['type']] = by_type.get(c['type'], 0) + 1

for t in ['KING', 'JACK', 'QUEEN', 'ACE', 'JOKER', 'TWO']:
    print(f"  {t}: {by_type.get(t, 0)} cards")
