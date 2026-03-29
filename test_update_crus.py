#!/usr/bin/env python3
"""
ValuJack AI Scan Integration - SAFE TEST VERSION
Updates ONLY CRUS as a test, with automatic backup
Run from: ~/Downloads/ValuJack/
"""

import re
import shutil
from datetime import datetime

def backup_cards_js(filepath='public/cards.js'):
    """Create timestamped backup of cards.js"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'public/cards.js.backup_{timestamp}'
    
    print(f"💾 Creating backup: {backup_path}")
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created successfully!")
    
    return backup_path

def test_update_single_card(filepath='public/cards.js', ticker='CRUS'):
    """Test update on a single card"""
    
    print(f"\n📖 Reading {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    ai_data = {
        'aiScore': 8,
        'aiStars': 4.4,
        'compositeStars': 3.38,
        'status': 'BOOST'
    }
    
    print(f"\n🔍 Looking for {ticker} card...")
    
    pattern = rf'(\{{[^}}]*ticker:\s*["\']({ticker})["\'][^}}]*stars:\s*(\d+))'
    
    match = re.search(pattern, content)
    
    if not match:
        print(f"❌ ERROR: Could not find {ticker} card")
        return False
    
    print(f"✅ Found {ticker} card!")
    print(f"   Current stars: {match.group(3)}")
    
    stars_pattern = rf'(ticker:\s*["\']({ticker})["\'][^}}]*)(stars:\s*\d+)'
    stars_match = re.search(stars_pattern, content)
    
    if not stars_match:
        print(f"❌ ERROR: Could not find stars field for {ticker}")
        return False
    
    insert_pos = stars_match.end(3)
    
    new_fields = f""",
    aiScanScore: {ai_data['aiScore']},
    aiScanStars: {ai_data['aiStars']},
    compositeStars: {ai_data['compositeStars']},
    aiStatus: '{ai_data['status']}',
    aiScanDate: '2026-03-27'"""
    
    updated_content = content[:insert_pos] + new_fields + content[insert_pos:]
    
    start = max(0, insert_pos - 100)
    end = min(len(updated_content), insert_pos + len(new_fields) + 200)
    print(f"\n📝 UPDATED card structure (excerpt):")
    print("-" * 60)
    print(updated_content[start:end])
    print("-" * 60)
    
    response = input("\nSave this update? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        print(f"\n💾 Saving updated file...")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"✅ SAVED! {ticker} has been updated with AI scan data")
        return True
    else:
        print(f"\n❌ Update cancelled - no changes made")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("VALUJACK AI SCAN - SAFE TEST MODE")
    print("Testing on CRUS only, with backup")
    print("=" * 60)
    
    try:
        backup_path = backup_cards_js()
        success = test_update_single_card()
        
        if success:
            print("\n✅ TEST SUCCESSFUL!")
            print("\nNEXT: Open public/index.html and verify CRUS loads correctly")
        else:
            print(f"\n⚠️ Backup still available at: {backup_path}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
