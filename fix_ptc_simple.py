with open('public/cards.js', 'r') as f:
    lines = f.readlines()

# Find line with Card 225 and currency: ''
for i, line in enumerate(lines):
    if "id: 225," in line:
        # Find the currency line (should be within next 5 lines)
        for j in range(i, min(i+10, len(lines))):
            if "currency: ''," in lines[j]:
                lines[j] = lines[j].replace("currency: '',", "currency: 'USD',")
                print(f"✓ Fixed currency on line {j+1}")
                break

with open('public/cards.js', 'w') as f:
    f.writelines(lines)

print("✓ Done")

import subprocess
result = subprocess.run(['node', '-c', 'public/cards.js'], capture_output=True)
if result.returncode == 0:
    print("✓ Syntax check passed")
else:
    print("✗ SYNTAX ERROR")

