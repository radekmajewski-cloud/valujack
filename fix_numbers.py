import re

CARDS_PATH = '/Users/radekmajewski/Downloads/valujack/public/cards.js'

with open(CARDS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

def clean_descriptions(text):
    # FCF yield of X% -> free cash flow yield
    text = re.sub(r'FCF yield of [\d.]+%', 'strong free cash flow yield', text)
    text = re.sub(r'[\d.]+% FCF yield', 'strong free cash flow yield', text)
    text = text.replace('FCF', 'free cash flow')
    
    # Remove standalone percentages in prose
    # "X% margin" -> "strong margin"
    text = re.sub(r'[\d.]+% margin', 'strong margin', text)
    # "X% CAGR" -> "consistent growth"
    text = re.sub(r'[\d.]+% CAGR', 'consistent growth', text)
    # "X% yield" -> "attractive yield"
    text = re.sub(r'[\d.]+% yield', 'attractive yield', text)
    # "X% dividend" -> "attractive dividend"
    text = re.sub(r'[\d.]+% dividend', 'attractive dividend', text)
    # "X% market share" -> "dominant market share"
    text = re.sub(r'[\d.]+% market share', 'dominant market share', text)
    # "X% of fair value" -> "below fair value"
    text = re.sub(r'[\d.]+% of fair value', 'below fair value', text)
    # "X% below fair value" -> "below fair value"
    text = re.sub(r'[\d.]+% below fair value', 'below fair value', text)
    # "up X%" -> "rising strongly"
    text = re.sub(r'up [\d.]+%', 'rising strongly', text)
    # "down X%" -> "declining significantly"
    text = re.sub(r'down [\d.]+%', 'declining significantly', text)
    # "grew X%" -> "grew consistently"
    text = re.sub(r'grew [\d.]+%', 'grew consistently', text)
    # "growing X%" -> "growing consistently"
    text = re.sub(r'growing [\d.]+%', 'growing consistently', text)
    # "over X%" -> "exceptionally high"
    text = re.sub(r'over [\d.]+%', 'exceptionally high', text)
    # "above X%" -> "above average"
    text = re.sub(r'above [\d.]+%', 'above average', text)
    # "more than X%" -> "significantly"
    text = re.sub(r'more than [\d.]+%', 'significantly', text)
    # Remove any remaining standalone percentages
    text = re.sub(r'[\d]+\.[\d]+%', '', text)
    text = re.sub(r'[\d]+%', '', text)
    
    # Abbreviations
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
    text = text.replace('PEO', 'professional employer')
    text = text.replace('PCB', 'printed circuit board')
    text = text.replace('OEM', 'original equipment manufacturer')
    text = text.replace('ARPU', 'revenue per user')
    text = text.replace('GMV', 'transaction volume')
    text = text.replace('NAV', 'net asset value')
    text = text.replace('EBITDA', 'operating earnings')
    text = text.replace('CAGR', 'compound annual growth')
    text = text.replace('MRO', 'maintenance and repair')
    text = text.replace('P&A', 'plugging and abandonment')
    text = text.replace('REIT', 'real estate investment trust')
    text = text.replace('DCF', 'discounted cash flow')
    
    return text

# Process description fields only - split at scores:
card_pat = re.compile(r'(\{ id: \d+.*?), scores:', re.DOTALL)

def process_card(m):
    desc = m.group(1)
    cleaned = clean_descriptions(desc)
    return cleaned + ', scores:'

new_content = card_pat.sub(process_card, content)

with open(CARDS_PATH, 'w', encoding='utf-8') as f:
    f.write(new_content)

# Verify
card_blocks = re.findall(r'\{ id: \d+.*?\},\s*\n', new_content, re.DOTALL)
pct = sum(1 for b in card_blocks if re.search(r'\d+%', b.split('scores:')[0].split('ind1')[0]))
print(f"Remaining percentages in prose: {pct}")
print("Done!")
