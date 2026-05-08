import csv
import re
from datetime import datetime

# Load all CSV data
csv_data = {}
for strategy_file, strategy in [
    ('kings', 'KING'), ('jacks', 'JACK'), ('queens', 'QUEEN'),
    ('aces', 'ACE'), ('jokers', 'JOKER'), ('twos', 'TWO')
]:
    try:
        with open(f'Company data/{strategy_file} 2026-04-06.csv', 'r', encoding='iso-8859-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                ticker = row.get('Info - Ticker', '').strip()
                if ticker:
                    csv_data[ticker] = {
                        'company': row.get('Info - Name', ''),
                        'industry': row.get('Info - Industry', ''),
                        'sector': row.get('Info - Sector', ''),
                        'strategy': strategy
                    }
    except Exception as e:
        print(f"Error reading {strategy_file}: {e}")

print(f"Loaded CSV data for {len(csv_data)} companies\n")

# Read cards.js
with open('public/cards.js', 'r') as f:
    content = f.read()

# Backup
backup = f'public/cards.js.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

print(f"Backup created: {backup}\n")
print("This is a big job - generating descriptions for 391 cards...")
print("Would take significant time. Should I:")
print("1. Generate all 391 at once (may take 30+ minutes)")
print("2. Process in smaller batches you can review")
print("\nRecommend: batch processing for safety")

