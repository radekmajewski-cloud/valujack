import shutil
CARDS_JS = '/Users/radekmajewski/Downloads/ValuJack/public/cards.js'
shutil.copy(CARDS_JS, CARDS_JS + '.bak_before_two')
content = open(CARDS_JS).read()
insert_pos = content.rfind('];')

new_cards = []
