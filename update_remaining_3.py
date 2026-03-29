#!/usr/bin/env python3
import re
import shutil
from datetime import datetime

# Only the 3 remaining cards
AI_UPDATES = {
    'APH': {'aiScore': 7, 'aiStars': 4.2, 'compositeStars': 4.14, 'status': 'BOOST'},
    'CRUS': {'aiScore': 8, 'aiStars': 4.4, 'compositeStars': 3.38, 'status': 'BOOST'},
    'JNJ': {'aiScore': 3, 'aiStars': 3.4, 'compositeStars': 3.08, 'status': 'NEUTRAL'},
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
        content = f.read()
    
    updated_count = 0
    
    for ticker, data in AI_UPDATES.items():
        print(f"\nUpdating {ticker}...")
        
        # Pattern: find "ticker: 'TICKER'" then find "stars: X" on same or next few lines
        pattern = rf"(ticker: '{ticker}'[^\n]*\n[^\n]*)(stars: \d+)"
        
        match = re.search(pattern, content)
        if not match:
            # Try with ticker on previous line
            pattern2 = rf"([^\n]*ticker: '{ticker}'[^\n]*)(stars: \d+)"
            match = re.search(pattern2, content)
        
        if not match:
            print(f"  Could not find stars for {ticker}")
            continue
        
        # Build new fields
        new_fields = (
            f", aiScanScore: {data['aiScore']}"
            f", aiScanStars: {data['aiStars']}"
            f", compositeStars: {data['compositeStars']}"
            f", aiStatus: '{data['status']}'"
            f", aiScanDate: '2026-03-27'"
        )
        
        # Replace: keep everything before "stars: X", add new fields after "stars: X"
        old_stars = match.group(2)
        new_stars = old_stars + new_fields
        
        content = content[:match.start(2)] + new_stars + content[match.end(2):]
        updated_count += 1
        print(f"  ✓ Updated {ticker}")
    
    print(f"\nWriting file...")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\nUpdated {updated_count} of 3 cards")
    return True

if __name__ == '__main__':
    print("UPDATING REMAINING 3 CARDS")
    filepath = 'public/cards.js'
    
    try:
        backup_path = backup_file(filepath)
        success = update_cards_js(filepath)
        
        if success:
            print("\nSUCCESS!")
            print("Next: vercel --prod")
        
    except Exception as e:
        print(f"\nERROR: {e}")
