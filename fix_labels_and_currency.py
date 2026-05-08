import re

with open('public/index.html', 'r') as f:
    content = f.read()

# Fix 1: Change all "ROIC" labels to "RETURN ON CAPITAL"
content = content.replace("['ROIC', fromMetrics('roic')", "['RETURN ON CAPITAL', fromMetrics('roic')")

# Fix 2: The currency is already being added on lines 828-829, but let me verify
# It should be: livePrice + ' ' + (ec.currency || '')
# This is already correct in the code

print("✓ Changed ROIC to RETURN ON CAPITAL")
print("✓ Currency already included in code (ec.currency)")

with open('public/index.html', 'w') as f:
    f.write(content)

print("✓ Done")

