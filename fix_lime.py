import re

path = '/Users/radekmajewski/Downloads/valujack/public/cards.js'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: ticker LIME -> LIME.ST
content = content.replace("yahooTicker: 'LIME',", "yahooTicker: 'LIME.ST',")

# Fix 2: ROIC 0.0% -> 21.6% for Lime Technologies only
# Target the specific pattern within the Lime Technologies card
content = content.replace(
    "company: 'Lime Technologies', ticker: 'LIME', country: 'Sweden', currency: '', epsGrowth: '12.2%', revGrowth: '7.9%', tag: 'IT Services. Beaten down quality.', tagBold: 'Quality business.', tagFull: \"Lime Technologies operates in IT Services.\", pick: 'Beaten down quality.', pickBold: 'Fair valuation.', pickFull: \"A contrarian opportunity with solid fundamentals.\", ind1l: 'P/E', ind1v: '24.6', ind2l: 'ROIC', ind2v: '0.0%', metrics: [{ l: 'P/E', v: '24.6' }, { l: 'ROIC', v: '0.0%' }",
    "company: 'Lime Technologies', ticker: 'LIME', country: 'Sweden', currency: '', epsGrowth: '12.2%', revGrowth: '7.9%', tag: 'IT Services. Beaten down quality.', tagBold: 'Quality business.', tagFull: \"Lime Technologies operates in IT Services.\", pick: 'Beaten down quality.', pickBold: 'Fair valuation.', pickFull: \"A contrarian opportunity with solid fundamentals.\", ind1l: 'P/E', ind1v: '24.6', ind2l: 'ROIC', ind2v: '21.6%', metrics: [{ l: 'P/E', v: '24.6' }, { l: 'ROIC', v: '21.6%' }"
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done. Verifying...")

with open(path, 'r', encoding='utf-8') as f:
    for line in f:
        if 'Lime Technologies' in line:
            print(line[:300])
