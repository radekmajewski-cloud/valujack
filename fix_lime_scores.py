path = '/Users/radekmajewski/Downloads/valujack/public/cards.js'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old = "company: 'Lime Technologies', ticker: 'LIME', country: 'Sweden', currency: '', epsGrowth: '12.2%', revGrowth: '7.9%', tag: 'IT Services. Beaten down quality.', tagBold: 'Quality business.', tagFull: \"Lime Technologies operates in IT Services.\", pick: 'Beaten down quality.', pickBold: 'Fair valuation.', pickFull: \"A contrarian opportunity with solid fundamentals.\", ind1l: 'P/E', ind1v: '24.6', ind2l: 'ROIC', ind2v: '21.6%', metrics: [{ l: 'P/E', v: '24.6' }, { l: 'ROIC', v: '21.6%' }, { l: 'Debt/Equity', v: '1.5' }, { l: 'F-Score', v: '9' }, { l: '1M Performance', v: '15.4%' }], scores: []"

new = "company: 'Lime Technologies', ticker: 'LIME', country: 'Sweden', currency: 'SEK', epsGrowth: '12.2%', revGrowth: '7.9%', tag: 'Nordic CRM leader. Quality at a discount.', tagBold: 'Nordic CRM leader.', tagFull: 'Lime Technologies is a profitable Nordic SaaS CRM business with 100% gross margins, a nine-point F-Score, and a long track record of consistent growth serving niche verticals across Sweden, Norway and Finland.', pick: 'Contrarian entry. Quality intact.', pickBold: 'Phoenix recovery signal.', pickFull: 'A high-quality Nordic SaaS business with a perfect F-Score and exceptional margins trading below fair value after a prolonged drawdown. The fundamentals have not deteriorated — the price has.', ind1l: '1Y PERFORMANCE', ind1v: '-38.2%', ind2l: 'ROIC', ind2v: '21.6%', metrics: [{ l: 'P/E', v: '24.6' }, { l: 'ROIC', v: '21.6%' }, { l: 'F-Score', v: '9/9' }, { l: 'Gross Margin', v: '100%' }, { l: 'Debt/Equity', v: '1.5' }, { l: '1M Performance', v: '3.6%' }], scores: [{ l: 'Recovery', v: 4, max: 10, color: '#D85A30', raw: '1m Perf', rawV: '+3.6%' }, { l: 'Quality', v: 9, max: 10, color: '#5B8FD4', raw: 'F-Score', rawV: '9/9' }, { l: 'Fair Price', v: 2, max: 10, color: '#9B6ED4', raw: 'Undervalued', rawV: '-34%' }, { l: 'Low Debt', v: 5, max: 10, color: '#4CAF82', raw: 'D/E', rawV: '1.5' }, { l: 'Profit', v: 10, max: 10, color: '#C4784A', raw: 'Gross Margin', rawV: '100%' }]"

if old in content:
    content = content.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Done! Verifying...")
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Lime Technologies' in line:
                # Print scores section
                start = line.find('scores:')
                print(line[start:start+200])
else:
    print("❌ Pattern not found — no changes made.")
