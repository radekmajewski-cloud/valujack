import csv
import re
from datetime import datetime

# Read all CSVs and build ticker → data map
csv_files = {
    'KING': 'Company data/kings 2026-04-06.csv',
    'JACK': 'Company data/jacks 2026-04-06.csv',
    'QUEEN': 'Company data/queens 2026-04-06.csv',
    'ACE': 'Company data/aces 2026-04-06.csv',
    'JOKER': 'Company data/jokers 2026-04-06.csv',
    'TWO': 'Company data/twos 2026-04-06.csv'
}

ticker_data = {}

print("Loading CSV data...\n")

for strategy, filepath in csv_files.items():
    try:
        with open(filepath, 'r', encoding='iso-8859-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                ticker = row.get('Info - Ticker', '').strip()
                if not ticker:
                    continue
                
                # Extract all available metrics
                data = {
                    'strategy': strategy,
                    'div_yield': row.get('Div. Yield - Current', '').strip(),
                    'eps_growth': row.get('Earnings g. - Growth 5y', '').strip() or row.get('Earnings g. - Growth 3y', '').strip(),
                    'rev_growth': row.get('Revenue g. - Growth 5y', '').strip(),
                    'fcf_margin': row.get('FCF margin - Current', '').strip() or row.get('FCF margin - Average 3y', '').strip(),
                    'perf_1y': row.get('Performance - Perform. 1y', '').strip(),
                }
                
                ticker_data[ticker] = data
        
        print(f"  ✓ {strategy:6s}: {len([t for t,d in ticker_data.items() if d['strategy']==strategy])} companies")
    except Exception as e:
        print(f"  ✗ {strategy}: {e}")

print(f"\nTotal tickers loaded: {len(ticker_data)}\n")

# Read cards.js
with open('public/cards.js', 'r') as f:
    content = f.read()

# Backup
backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

print(f"✓ Backup created: {backup}\n")

# Track updates
updates = {
    'div_yield': 0,
    'eps_growth': 0,
    'rev_growth': 0,
    'metrics_enhanced': 0
}

# Pattern to match cards 319-709 (the new cards)
pattern = r"({ id: (3\d\d|[4-6]\d\d|70[0-9]), type: '(\w+)',.*?ticker: '([^']+)'.*?)(epsGrowth: '[^']*',)"

def enrich_card(match):
    full_card = match.group(1)
    card_id = int(match.group(2))
    card_type = match.group(3)
    ticker = match.group(4)
    eps_field = match.group(5)
    
    if ticker not in ticker_data:
        return match.group(0)
    
    data = ticker_data[ticker]
    updated_card = full_card
    
    # Update epsGrowth if we have data
    if data['eps_growth']:
        try:
            eps_val = float(data['eps_growth'].replace(',', '.'))
            if eps_val != 0:
                new_eps = f"epsGrowth: '+{int(eps_val)}%'," if eps_val > 0 else f"epsGrowth: '{int(eps_val)}%',"
                updated_card = updated_card.replace(eps_field, new_eps)
                updates['eps_growth'] += 1
        except:
            pass
    
    # Update revGrowth if we have data
    if data['rev_growth']:
        try:
            rev_val = float(data['rev_growth'].replace(',', '.'))
            if rev_val != 0:
                new_rev = f"revGrowth: '+{int(rev_val)}%'" if rev_val > 0 else f"revGrowth: '{int(rev_val)}%'"
                updated_card = re.sub(r"revGrowth: '[^']*'", new_rev, updated_card)
                updates['rev_growth'] += 1
        except:
            pass
    
    # Add Div. Yield to metrics for KING cards
    if card_type == 'KING' and data['div_yield']:
        try:
            div_val = float(data['div_yield'].replace(',', '.'))
            if div_val > 0:
                # Check if Div. Yield already exists
                if 'Div. Yield' not in updated_card:
                    # Find metrics array and add dividend
                    metrics_match = re.search(r"(metrics: \[[^\]]+)", updated_card)
                    if metrics_match:
                        div_metric = f", {{ l: 'Div. Yield', v: '{div_val:.1f}%' }}"
                        updated_card = updated_card.replace(metrics_match.group(0), metrics_match.group(0) + div_metric)
                        updates['div_yield'] += 1
                        if updates['div_yield'] <= 5:
                            print(f"  {ticker:10s} (KING) → Added Div. Yield: {div_val:.1f}%")
        except:
            pass
    
    return updated_card + eps_field

content = re.sub(pattern, enrich_card, content, flags=re.DOTALL)

print(f"\n=== ENRICHMENT SUMMARY ===")
print(f"EPS Growth updated: {updates['eps_growth']} cards")
print(f"Revenue Growth updated: {updates['rev_growth']} cards")
print(f"Dividend Yield added: {updates['div_yield']} KING cards")
print(f"\n✓ Backup: {backup}")

# Write updated file
with open('public/cards.js', 'w') as f:
    f.write(content)

print("✓ cards.js updated successfully")

