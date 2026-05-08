import re, shutil, os
from datetime import datetime

path = '/Users/radekmajewski/Downloads/valujack/public/cards.js'
backup = path + '.backup_' + datetime.now().strftime('%Y%m%d_%H%M%S') + '_before_bic_ticker_fix'
shutil.copy2(path, backup)
print(f'Backup: {backup}')

with open(path, 'r') as f:
    content = f.read()

# Fix 1: yahooTicker BB -> BB.PA (only for BIC card, id 322)
# Fix both yahooTicker and ticker fields within BIC's card block
old = "id: 322, type: 'KING', isPro: false, fairValue: 77.04, yahooTicker: 'BB', stars: 3, sector: 'Food and Beverage', sectorIcon: '🏢', irLink: '', company: 'Bic', ticker: 'BB',"
new = "id: 322, type: 'KING', isPro: false, fairValue: 77.04, yahooTicker: 'BB.PA', stars: 3, sector: 'Consumer Goods', sectorIcon: '🏢', irLink: '', company: 'Bic', ticker: 'BB.PA',"

if old in content:
    content = content.replace(old, new)
    print('✓ Fixed yahooTicker and ticker: BB -> BB.PA')
else:
    print('✗ Could not find BIC card header to fix tickers')

# Fix 2: pickFull missing dividend yield value
old2 = "a  dividend yield and over 160 countries"
new2 = "a 5.3% dividend yield and over 160 countries"

if old2 in content:
    content = content.replace(old2, new2)
    print('✓ Fixed pickFull missing dividend yield text')
else:
    print('✗ Could not find pickFull gap to fix')

with open(path, 'w') as f:
    f.write(content)

print('Done.')
