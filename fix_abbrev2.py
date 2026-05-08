import re

CARDS_PATH = '/Users/radekmajewski/Downloads/valujack/public/cards.js'

with open(CARDS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

def clean_prose(text):
    text = re.sub(r'ROIC of [\d.]+%\s+reflects', 'high return on capital reflects', text)
    text = re.sub(r'ROIC of [\d.]+%', 'high return on capital', text)
    text = re.sub(r'an? [\d.]+% ROIC', 'high return on capital', text)
    text = re.sub(r'[\d.]+% ROIC', 'high return on capital', text)
    text = text.replace('ROIC', 'return on capital')
    text = re.sub(r'EPS grew [\d.]+% annualised', 'earnings grew consistently', text)
    text = re.sub(r'EPS grew [\d.]+%', 'earnings grew consistently', text)
    text = re.sub(r'EPS growth of [\d.]+%', 'consistent earnings growth', text)
    text = text.replace('EPS', 'earnings per share')
    text = re.sub(r'[Rr]evenue grew [\d.]+% annualised', 'revenue grew consistently', text)
    text = re.sub(r'[Rr]evenue growing [\d.]+% annualised', 'revenue growing consistently', text)
    text = re.sub(r'P/E of [\d.]+x?', 'attractively valued', text)
    text = re.sub(r'P/E at [\d.]+x?', 'attractively valued', text)
    text = text.replace('P/E', 'valuation')
    text = re.sub(r'FCF yield of [\d.]+%', 'strong free cash flow yield', text)
    text = re.sub(r'[\d.]+% FCF yield', 'strong free cash flow yield', text)
    text = text.replace('FCF', 'free cash flow')
    text = re.sub(r'up [\d.]+%', 'rising strongly', text)
    text = re.sub(r'down [\d.]+%', 'declining significantly', text)
    text = re.sub(r'grew [\d.]+%', 'grew consistently', text)
    text = re.sub(r'growing [\d.]+%', 'growing consistently', text)
    text = re.sub(r'[\d]+\.[\d]+%', '', text)
    text = re.sub(r'[\d]+%', '', text)
    text = text.replace('SaaS', 'software subscription')
    text = text.replace('LNG', 'liquefied natural gas')
    text = text.replace('VLCC', 'supertanker')
    text = text.replace('NGL', 'natural gas liquids')
    text = text.replace('OCTG', 'oil country steel tubes')
    text = text.replace('MENA', 'Middle East and North Africa')
    text = text.replace('CEE', 'Central and Eastern Europe')
    text = text.replace('CRO', 'contract research organisation')
    text = text.replace('CDMO', 'contract drug manufacturer')
    text = text.replace('UCaaS', 'cloud communications')
    text = text.replace('PCB', 'printed circuit board')
    text = text.replace('OEM', 'original equipment manufacturer')
    text = text.replace('NAV', 'net asset value')
    text = text.replace('EBITDA', 'operating earnings')
    text = text.replace('MRO', 'maintenance and repair')
    return text

# Extract and clean only specific prose fields
def process_card(m):
    card = m.group(0)
    
    # Only clean these specific fields using targeted regex
    # tagFull
    card = re.sub(r'(tagFull: ")(.*?)(")', lambda x: x.group(1) + clean_prose(x.group(2)) + x.group(3), card, flags=re.DOTALL)
    # pickFull  
    card = re.sub(r'(pickFull: ")(.*?)(")', lambda x: x.group(1) + clean_prose(x.group(2)) + x.group(3), card, flags=re.DOTALL)
    # tag
    card = re.sub(r"(tag: ')((?:(?!tagBold)[^'])*?)(')", lambda x: x.group(1) + clean_prose(x.group(2)) + x.group(3), card)
    # tagBold
    card = re.sub(r"(tagBold: ')(.*?)(')", lambda x: x.group(1) + clean_prose(x.group(2)) + x.group(3), card)
    # pick
    card = re.sub(r"(pick: ')((?:(?!pickBold)[^'])*?)(')", lambda x: x.group(1) + clean_prose(x.group(2)) + x.group(3), card)
    # pickBold
    card = re.sub(r"(pickBold: ')(.*?)(')", lambda x: x.group(1) + clean_prose(x.group(2)) + x.group(3), card)
    # bullets - each bullet string
    card = re.sub(r'(")((?:(?!")[^"])*?)(", (?="|\]))', lambda x: x.group(1) + clean_prose(x.group(2)) + x.group(3), card)
    
    return card

card_pattern = re.compile(r'\{ id: \d+.*?\},\s*\n', re.DOTALL)
new_content = card_pattern.sub(process_card, content)

with open(CARDS_PATH, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Done!")
