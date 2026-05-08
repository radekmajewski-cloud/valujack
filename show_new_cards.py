import re

with open('public/cards.js', 'r') as f:
    content = f.read()

# Find all cards with id >= 319
pattern = r'{ id: (\d+), type: \'(\w+)\',.*?company: \'([^\']+)\', ticker: \'([^\']+)\'.*?fairValue: ([\d.]+)'
matches = re.findall(pattern, content)

new_cards = [(int(m[0]), m[1], m[3], m[2], m[4]) for m in matches if int(m[0]) >= 319]

print(f'\n=== NEW COMPANIES: {len(new_cards)} cards (IDs 319-709) ===\n')
print(f"{'ID':<5} {'Type':<6} {'Ticker':<10} {'Company':<45} {'Fair Value'}")
print('-' * 100)

for card in new_cards[:50]:
    print(f"{card[0]:<5} {card[1]:<6} {card[2]:<10} {card[3][:45]:<45} {card[4]}")

print(f'\n... and {len(new_cards)-50} more cards\n')

by_type = {}
for card in new_cards:
    by_type[card[1]] = by_type.get(card[1], 0) + 1

print('Breakdown by strategy:')
for t in ['KING', 'JACK', 'QUEEN', 'ACE', 'JOKER', 'TWO']:
    print(f'  {t}: {by_type.get(t, 0)} cards')
