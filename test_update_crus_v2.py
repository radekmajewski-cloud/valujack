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
    
    # Find the exact line with stars for id: 85
    # Look for "id: 85" then find "stars: X" within the same object
    lines = content.split('\n')
    
    crus_start_line = None
    crus_stars_line = None
    
    for i, line in enumerate(lines):
        if 'id: 85,' in line:
            crus_start_line = i
            # Now find stars within next ~20 lines
            for j in range(i, min(i + 20, len(lines))):
                if re.search(r'stars:\s*\d+', lines[j]):
                    crus_stars_line = j
                    break
            break
    
    if crus_start_line is None:
        print("❌ Could not find id: 85")
        return False
    
    if crus_stars_line is None:
        print("❌ Could not find stars field for CRUS")
        return False
    
    print(f"✅ Found CRUS card at line {crus_start_line + 1}")
    print(f"   Stars field at line {crus_stars_line + 1}")
    
    # Show context
    print(f"\n📄 Current CRUS card (lines {crus_start_line + 1}-{crus_stars_line + 3}):")
    print("-" * 80)
    for i in range(crus_start_line, min(crus_stars_line + 3, len(lines))):
        print(f"{i+1}: {lines[i]}")
    print("-" * 80)
    
    # Extract current stars value
    stars_match = re.search(r'stars:\s*(\d+)', lines[crus_stars_line])
    current_stars = stars_match.group(1) if stars_match else '?'
    print(f"\n   Current stars: {current_stars}")
    
    # Modify the stars line to add AI fields
    original_line = lines[crus_stars_line]
    
    # Add AI fields right after stars: X
    updated_line = re.sub(
        r'(stars:\s*\d+)',
        r'\1, aiScanScore: 8, aiScanStars: 4.4, compositeStars: 3.38, aiStatus: \'BOOST\', aiScanDate: \'2026-03-27\'',
        original_line
    )
    
    print(f"\n📝 UPDATED line {crus_stars_line + 1}:")
    print("-" * 80)
    print(f"BEFORE: {original_line}")
    print(f"AFTER:  {updated_line}")
    print("-" * 80)
    
    # Verify this is actually CRUS
    context_lines = '\n'.join(lines[max(0, crus_start_line):min(crus_stars_line + 2, len(lines))])
    if 'CRUS' not in context_lines:
        print("\n⚠️  WARNING: This doesn't look like the CRUS card!")
        print("Showing context:")
        print(context_lines)
        return False
    
    response = input("\nSave this update? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        # Update the line
        lines[crus_stars_line] = updated_line
        
        # Reconstruct content
        updated_content = '\n'.join(lines)
        
        print(f"\n💾 Saving...")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ SAVED! CRUS updated with AI scan data")
        print(f"\n🎯 Changes:")
        print(f"   Line {crus_stars_line + 1} modified")
        print(f"   Original stars: {current_stars}")
        print(f"   New compositeStars: 3.38")
        print(f"   AI Score: +8 (BOOST)")
        return True
    else:
        print(f"\n❌ Cancelled - no changes made")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("VALUJACK AI SCAN - TESTING ON CRUS (v2)")
    print("=" * 60)
    
    try:
        backup_path = backup_cards_js()
        success = test_update_crus()
        
        if success:
            print("\n✅ SUCCESS! Test in browser:")
            print("   open public/index.html")
        else:
            print(f"\n   Backup at: {backup_path}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
