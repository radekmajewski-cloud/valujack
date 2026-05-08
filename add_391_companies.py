
#!/usr/bin/env python3
import csv
import re
from datetime import datetime

def safe_float(val, default=0.0):
    if not val or val.strip() == '':
        return default
    try:
        return float(val.replace(',', '.').strip())
    except:
        return default

STRATEGY_INFO = {
    'KING': {'desc': 'dividend aristocrat', 'short': 'Dividend compounder'},
    'JACK': {'desc': 'momentum play', 'short': 'Momentum growth'},
    'QUEEN': {'desc': 'magic formula pick', 'short': 'Quality at value'},
    'ACE': {'desc': 'financially strong company', 'short': 'Financial strength'},
    'JOKER': {'desc': 'CANSLIM growth stock', 'short': 'Growth leader'},
    'TWO': {'desc': 'contrarian opportunity', 'short': 'Beaten down quality'}
}

print("Reading current cards.js...")
with open('public/cards.js', 'r', encoding='utf-8') as f:
    content = f.read()

existing_tickers = set(re.findall(r"ticker:\s*'([^']+)'", content))
existing_ids = [int(m) for m in re.findall(r'id:\s*(\d+)', content)]
next_id = max(existing_ids) + 1

print(f"Current pool: {len(existing_tickers)} tickers")
print(f"Next ID: {next_id}\n")

csv_files = {
    'KING': 'Company data/kings 2026-04-06.csv',
    'JACK': 'Company data/jacks 2026-04-06.csv',
    'QUEEN': 'Company data/queens 2026-04-06.csv',
    'ACE': 'Company data/aces 2026-04-06.csv',
    'JOKER': 'Company data/jokers 2026-04-06.csv',
    'TWO': 'Company data/twos 2026-04-06.csv'
}

cards_code = []
current_id = next_id

for strategy, filename in csv_files.items():
    strategy_count = 0
    print(f"Processing {strategy}...")
    
    try:
        with open(filename, 'r', encoding='iso-8859-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            for row in reader:
                ticker = row.get('Info - Ticker', '').strip()
                company = row.get('Company', '').strip()
                
                if ticker in existing_tickers or not ticker or not company:
                    continue
                
                fair_value = safe_float(row.get('Fair value', '0'))
                if fair_value == 0:
                    continue
                    
                country = row.get('Info - Country', 'Unknown').strip()
                industry = row.get('Info - Industry', 'Unknown').strip()
                sector = row.get('Info - Sector', 'Unknown').strip()
                
                pe = safe_float(row.get('P/E - Current', '0'))
                roic = safe_float(row.get('ROIC - Average 5y', '0').replace('%', ''))
                debt_eq = safe_float(row.get('Debt-Equity - Current', '0'))
                
                is_pro = 'true' if strategy in ['QUEEN', 'ACE', 'JOKER'] else 'false'
                
                card = f"""    {{ id: {current_id}, type: '{strategy}', isPro: {is_pro}, fairValue: {fair_value}, yahooTicker: '{ticker}', stars: 3, sector: '{sector}', sectorIcon: '🏢', irLink: '', company: '{company}', ticker: '{ticker}', country: '{country}', currency: '', epsGrowth: '—', revGrowth: '—', tag: '{industry}. {STRATEGY_INFO[strategy]["short"]}.', tagBold: 'Quality business.', tagFull: "{company} operates in {industry}.", pick: '{STRATEGY_INFO[strategy]["short"]}.', pickBold: 'Fair valuation.', pickFull: "A {STRATEGY_INFO[strategy]["desc"]} with solid fundamentals.", ind1l: 'P/E', ind1v: '{pe:.1f}', ind2l: 'ROIC', ind2v: '{roic:.1f}%', metrics: [{{ l: 'P/E', v: '{pe:.1f}' }}, {{ l: 'ROIC', v: '{roic:.1f}%' }}, {{ l: 'D/E', v: '{debt_eq:.1f}' }}], scores: [], bullets: ["Operates in {industry}.", "Fair value: {fair_value:.0f}.", "3-star rating."], }},"""
                
                cards_code.append(card)
                current_id += 1
                strategy_count += 1
                
        print(f"  → Added {strategy_count} cards")
                
    except Exception as e:
        print(f"  ERROR: {e}")

print(f"\n=== SUMMARY ===")
print(f"Total new cards: {len(cards_code)}")

pattern = r'(.*)(,\s*\n];)'
match = re.search(pattern, content, re.DOTALL)

if match:
    before = match.group(1)
    new_content = before + ',' + '\n' + '\n'.join(cards_code) + '\n];'
    
    backup_file = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    with open('public/cards.js', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    old_count = len(re.findall(r'\{ id:', content))
    new_count = len(re.findall(r'\{ id:', new_content))
    
    print(f"\n✓ Successfully updated cards.js")
    print(f"  Before: {old_count} cards")
    print(f"  After: {new_count} cards")
    print(f"  Added: {new_count - old_count} cards")
    print(f"  Backup: {backup_file}")
else:
    print("\nERROR: Could not find insertion point!")
