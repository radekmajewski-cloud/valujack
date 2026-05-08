import re
from datetime import datetime

with open('public/index.html', 'r') as f:
    content = f.read()

backup = f'public/index.html.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
with open(backup, 'w') as f:
    f.write(content)

# Replace fromMetrics('roic') with fromMetrics('return on capital', 'roic')
# This will search for both old and new label names
count = content.count("fromMetrics('roic')")
content = content.replace("fromMetrics('roic')", "fromMetrics('return on capital', 'roic')")

print(f"✓ Updated {count} instances: fromMetrics('roic') → fromMetrics('return on capital', 'roic')")
print(f"Backup: {backup}")

with open('public/index.html', 'w') as f:
    f.write(content)

