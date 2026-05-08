import re

CARDS_PATH = '/Users/radekmajewski/Downloads/valujack/public/cards.js'

descriptions = {
    387: ('ACT Energy Technologies Ltd', 'Canadian oilfield tubular services. Recovery play.', 'Oilfield services recovery.', "ACT Energy Technologies provides tubular running services and equipment rental to the Canadian oil and gas industry. The company operates in the Western Canadian Sedimentary Basin and benefits from rising Canadian energy investment as oilsands and tight oil activity expands.", 'Canadian oilfield services. Recovery momentum.', 'Energy services recovery.', "A Canadian oilfield tubular services company recovering in the Western Canadian energy sector. ACT Energy benefits from rising Canadian energy investment and tight oil activity expansion, with revenue growing 9.8% annualised.", ["Tubular running services and equipment rental for Canadian oil and gas producers.", "Operations in the Western Canadian Sedimentary Basin — core Canadian energy geography.", "Revenue grew 9.8% annualised as Canadian energy investment activity expanded.", "Recovery play with improving margins as oilfield services pricing strengthens."]),
    466: ('ZTO Express Inc', 'Chinese parcel delivery giant. High ROIC.', 'China parcel delivery leader.', "ZTO Express is one of China's largest parcel delivery companies, operating an asset-light network model that handles billions of parcels annually for Chinese e-commerce platforms including Alibaba and JD.com. The company benefits from structural growth in Chinese e-commerce and cross-border shipping.", 'China e-commerce delivery. High ROIC.', 'China logistics compounder.', "A Chinese parcel delivery company with a 21.5% ROIC and EPS growth of 15.3% annualised. ZTO Express operates an asset-light network handling billions of parcels annually for Chinese e-commerce — a structural growth business benefiting from China's continued e-commerce expansion.", ["One of China's largest parcel delivery networks serving Alibaba, JD.com and other platforms.", "ROIC of 21.5% reflects strong network economics from China's leading e-commerce delivery.", "EPS grew 15.3% annualised as Chinese e-commerce parcel volumes expanded consistently.", "Revenue grew 13.2% annualised with structural demand from China e-commerce growth."]),
}

with open(CARDS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

updated = 0
for card_id, (company, tag, tagBold, tagFull, pick, pickBold, pickFull, bullets) in descriptions.items():
    # Fix tag/pick/tagFull/pickFull
    pattern = re.compile(
        rf"(id: {card_id}, type: 'JACK'.*?tag: ')[^']*('.*?tagBold: ')[^']*('.*?tagFull: \")[^\"]*(\",.*?pick: ')[^']*('.*?pickBold: ')[^']*('.*?pickFull: \")[^\"]*(\",)",
        re.DOTALL
    )
    replacement = rf"\g<1>{tag}\g<2>{tagBold}\g<3>{tagFull}\g<4>{pick}\g<5>{pickBold}\g<6>{pickFull}\g<7>"
    new_content = pattern.sub(replacement, content)
    if new_content != content:
        content = new_content
        updated += 1
        print(f"✅ {card_id}: {company} (descriptions)")
    else:
        print(f"➡️  {card_id}: {company} (descriptions already set)")

    # Fix bullets - use a more targeted approach
    bullets_str = ', '.join([f'"{b}"' for b in bullets])
    # Try matching the generic bullets pattern
    old_bullets = re.search(rf'(id: {card_id},.*?bullets: \[)(.*?)(\])', content, re.DOTALL)
    if old_bullets:
        old = old_bullets.group(0)
        new = old_bullets.group(1) + bullets_str + old_bullets.group(3)
        content = content.replace(old, new)
        print(f"✅ {card_id}: {company} (bullets)")

with open(CARDS_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Updated {updated}/2 JACK cards")
print(f"Remaining generic: {content.count('operates in')}")
