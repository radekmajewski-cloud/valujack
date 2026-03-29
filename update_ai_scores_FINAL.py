#!/usr/bin/env python3
import re
import shutil
from datetime import datetime

AI_UPDATES = {
    'ESEA': {'aiScore': 7, 'aiStars': 4.2, 'compositeStars': 4.59, 'status': 'BOOST'},
    'UHS': {'aiScore': -2, 'aiStars': 2.2, 'compositeStars': 4.19, 'status': 'WARN'},
    'TSM': {'aiScore': 6, 'aiStars': 4.0, 'compositeStars': 4.00, 'status': 'BOOST'},
    'DDOG': {'aiScore': 6, 'aiStars': 4.0, 'compositeStars': 4.00, 'status': 'BOOST'},
    'APH': {'aiScore': 7, 'aiStars': 4.2, 'compositeStars': 4.14, 'status': 'BOOST'},
    'ZS': {'aiScore': 5, 'aiStars': 3.8, 'compositeStars': 3.96, 'status': 'BOOST'},
    'OMC': {'aiScore': 0, 'aiStars': 2.5, 'compositeStars': 3.70, 'status': 'WARN'},
    'MLI': {'aiScore': 1, 'aiStars': 3.0, 'compositeStars': 3.80, 'status': 'WARN'},
    'JDEP': {'aiScore': 1, 'aiStars': 3.0, 'compositeStars': 3.80, 'status': 'NEUTRAL'},
    'CRUS': {'aiScore': 8, 'aiStars': 4.4, 'compositeStars': 3.38, 'status': 'BOOST'},
    'DAC': {'aiScore': 7, 'aiStars': 4.2, 'compositeStars': 3.34, 'status': 'BOOST'},
    'JNJ': {'aiScore': 3, 'aiStars': 3.4, 'compositeStars': 3.08, 'status': 'NEUTRAL'},
    'ARLP': {'aiScore': 2, 'aiStars': 3.2, 'compositeStars': 3.04, 'status': 'NEUTRAL'},
}

def backup_file(filepath):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'{filepath}.backup_{timestamp}'
    shutil.copy2(filepath, backup_path)
    print(f"Backup: {backup_path}")
    return backup_path

def update_cards_js(filepath='public/cards.js'):
    print(f"\nReading {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    updated_count = 0
    
    for ticker, data in AI_UPDATES.items():
        print(f"\nLooking for {ticker}...")
        ticker_line = None
        stars_line = None
        
        for i, line in enumerate(lines):
            if f"ticker: '{ticker}'" in line or f'ticker: "{ticker}"' in line:
                ticker_line = i
                for j in range(i, min(i + 20, len(lines))):
                    if re.search(r'stars:\s*\d+', lines[j]):
                        stars_line = j
                        break
                break
        
        if stars_line is None:
            print(f"  Skipping {ticker}")
            continue
        
        stars_match = re.search(r'stars:\s*(\d+)', lines[stars_line])
        current_stars = stars_match.group(1) if stars_match else '?'
        print(f"  Found at line {stars_line + 1}, stars: {current_stars}")
        
        original_line = lines[stars_line]
        new_fields = (
            f", aiScanScore: {data['aiScore']}"
            f", aiScanStars: {data['aiStars']}"
            f", compositeStars: {data['compositeStars']}"
            f", aiStatus: '{data['status']}'"
            f", aiScanDate: '2026-03-27'"
        )
        
        updated_line = re.sub(r'(stars:\s*\d+)', r'\1' + new_fields, original_line)
        lines[stars_line] = updated_line
        updated_count += 1
    
    print(f"\nWriting file...")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"\nUpdated {updated_count} of {len(AI_UPDATES)} cards")
    return True

if __name__ == '__main__':
    print("VALUJACK AI SCAN UPDATE")
    filepath = 'public/cards.js'
    
    try:
        backup_path = backup_file(filepath)
        success = update_cards_js(filepath)
        
        if success:
            print("\nSUCCESS!")
            print("\nNext: vercel --prod")
        
    except Exception as e:
        print(f"\nERROR: {e}")
