import re

CARDS_PATH = '/Users/radekmajewski/Downloads/valujack/public/cards.js'

with open(CARDS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

def clean_descriptions(text):
    text = re.sub(r'ROIC of [\d.]+%\s+reflects', 'high return on capital reflects', text)
    text = re.sub(r'ROIC of [\d.]+%', 'high return on capital', text)
    text = re.sub(r'a [\d.]+% ROIC', 'high return on capital', text)
    text = re.sub(r'an [\d.]+% ROIC', 'high return on capital', text)
    text = re.sub(r'[\d.]+% ROIC', 'high return on capital', text)
    text = text.replace('ROIC', 'return on capital')
    text = re.sub(r'EPS grew [\d.]+% annualised', 'earnings grew consistently', text)
    text = re.sub(r'EPS growth of [\d.]+%', 'consistent earnings growth', text)
    text = re.sub(r'EPS grew [\d.]+%', 'earnings grew consistently', text)
    text = text.replace('EPS', 'earnings per share')
    text = re.sub(r'[Rr]evenue grew [\d.]+% annualised', 'revenue grew consistently', text)
    text = re.sub(r'[Rr]evenue growing [\d.]+% annualised', 'revenue growing consistently', text)
    text = re.sub(r'P/E of [\d.]+x?', 'attractively valued', text)
    text = re.sub(r'P/E at [\d.]+x?', 'attractively valued', text)
    text = text.replace('P/E', 'valuation')
    return text

with open(CARDS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Process description fields only - split each card at scores:
card_pat = re.compile(r'(\{ id: \d+.*?), scores:', re.DOTALL)

def process_card(m):
    desc = m.group(1)
    cleaned = clean_descriptions(desc)
    return cleaned + ', scores:'

new_content = card_pat.sub(process_card, content)

with open(CARDS_PATH, 'w', encoding='utf-8') as f:
    f.write(new_content)

card_blocks = re.findall(r'\{ id: \d+.*?\},\s*\n', new_content, re.DOTALL)
roic = sum(1 for b in card_blocks if 'ROIC' in b.split('scores:')[0])
eps = sum(1 for b in card_blocks if 'EPS' in b.split('scores:')[0])
pe = sum(1 for b in card_blocks if 'P/E' in b.split('scores:')[0])
print(f"Remaining ROIC: {roic}")
print(f"Remaining EPS: {eps}")
print(f"Remaining P/E: {pe}")
print("Done!")
