#!/usr/bin/env python3
import re
import shutil
from datetime import datetime

def backup_cards_js(filepath='public/cards.js'):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'public/cards.js.backup_{timestamp}'
    print(f"💾 Creating backup: {backup_path}")
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created!")
    return backup_path

def test_update_crus(filepath='public/cards.js'):
    print(f"\n📖 Reading {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n🔍 Looking for CRUS card (id: 85)...")
    
    # Find the CRUS card - it starts with id: 85
    pattern = r"(\{ id: 85,.*?ticker: 'CRUS'.*?stars: (\d+))"
    
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print(f"❌ ERROR: Could not find CRUS card")
        # Show what's around line 712
        lines = content.split('\n')
        print("\nShowing lines 710-720:")
        for i in range(709, 720):
            print(f"{i+1}: {lines[i]}")
        return False
    
    current_stars = match.group(2)
    print(f"✅ Found CRUS card!")
    print(f"   Current stars: {current_stars}")
    
    # Find where to insert - after stars: X
    insert_pattern = r"(\{ id: 85,.*?ticker: 'CRUS'.*?)(stars: \d+)"
    insert_match = re.search(insert_pattern, content, re.DOTALL)
    
    if not insert_match:
        print("❌ Could not find insertion point")
        return False
    
    insert_pos = insert_match.end(2)
    
    # New AI fields to add
    new_fields = """, aiScanScore: 8, aiScanStars: 4.4, compositeStars: 3.38, aiStatus: 'BOOST', aiScanDate: '2026-03-27'"""
    
    # Insert the new fields
    updated_content = content[:insert_pos] + new_fields + content[insert_pos:]
    
    # Show the change
    start = max(0, insert_pos - 150)
    end = min(len(updated_content), insert_pos + len(new_fields) + 150)
    print(f"\n📝 UPDATED section:")
    print("-" * 80)
    print(updated_content[start:end])
    print("-" * 80)
    
    response = input("\nSave this update? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        print(f"\n💾 Saving...")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"✅ SAVED! CRUS updated with AI scan data")
        print(f"\n🎯 Changes:")
        print(f"   Original stars: {current_stars}")
        print(f"   New compositeStars: 3.38")
        print(f"   AI Score: +8 (BOOST)")
        return True
    else:
        print(f"\n❌ Cancelled - no changes made")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("VALUJACK AI SCAN - TESTING ON CRUS")
    print("=" * 60)
    
    try:
        backup_path = backup_cards_js()
        success = test_update_crus()
        
        if success:
            print("\n✅ SUCCESS! Test CRUS in browser now")
            print("   Open public/index.html")
        else:
            print(f"\n   Backup at: {backup_path}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
