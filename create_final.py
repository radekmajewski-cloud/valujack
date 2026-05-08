#!/usr/bin/env python3
import re

# Read current working file
with open('public/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Component code (working version from earlier)
component = open('/home/claude/index_complete_working.html', 'r').readlines()[93:275]
component_text = ''.join(component)

# Fix momentum text
component_text = component_text.replace(
    'not an algorithm chasing momentum, not a sponsored pick',
    'not a sponsored pick, not a random selection'
)

# Insert before function Home
content = content.replace('function Home() {', component_text + '\nfunction Home() {')

# Remove old card descriptions and insert component call
# This is complex - let me just mark where it should go
print("Component ready but script incomplete")
print("Saving to temp file for manual review")

with open('public/index_temp.html', 'w') as f:
    f.write(content)
