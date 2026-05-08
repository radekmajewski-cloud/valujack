#!/usr/bin/env python3
import re
import csv

# Read cards.js
with open('public/cards.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all TWO cards with [value]
two_cards = []
pattern = r"{ id: (\d+), type: 'TWO'[^}]*ticker: '([^']+)'[^}]*company: '([^']+)'[^}]*}"

for match in re.finditer(pattern, content):
    card_text = match.group(0)
    if '[value]' in card_text:
        card_id = match.group(1)
        ticker = match.group(2)
        company = match.group(3)
        
        # Extract what needs to be filled
        perf_1y = re.search(r"ind1v: '([+-]?\d+\.)\[value\]", card_text)
        perf_1m = re.search(r"Up (\d+\.)\[value\]", card_text)
        gross_margin = re.search(r"Gross Margin.*?'(\d+\.)\[value\]", card_text)
        
        two_cards.append({
            'ID': card_id,
            'Ticker': ticker,
            'Company': company,
            '1Y_Performance_Prefix': perf_1y.group(1) if perf_1y else '',
            '1Y_Performance_Value': '[FILL IN]',
            '1M_Performance_Prefix': perf_1m.group(1) if perf_1m else '',
            '1M_Performance_Value': '[FILL IN]',
            'Gross_Margin_Prefix': gross_margin.group(1) if gross_margin else '',
            'Gross_Margin_Value': '[FILL IN]'
        })

# Write CSV
with open('two_cards_to_fix.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['ID', 'Ticker', 'Company', '1Y_Performance_Prefix', '1Y_Performance_Value', '1M_Performance_Prefix', '1M_Performance_Value', 'Gross_Margin_Prefix', 'Gross_Margin_Value'])
    writer.writeheader()
    writer.writerows(two_cards)

print(f"✅ Exported {len(two_cards)} TWO cards to: two_cards_to_fix.csv")
print("\nInstructions:")
print("1. Open two_cards_to_fix.csv")
print("2. Fill in the [FILL IN] columns with actual percentages (just the number, no % sign)")
print("3. Example: If 1Y performance is -27.1%, put '27.1' in 1Y_Performance_Value")
print("4. Save and send back to me")
