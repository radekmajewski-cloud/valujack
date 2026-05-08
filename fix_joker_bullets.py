#!/usr/bin/env python3
import re

with open('public/cards.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix DCBO specifically - should be Canada not USA
content = re.sub(
    r"(ticker: 'DCBO'.*?bullets: \[\"Docebo Inc — it services in )[A-Za-z]+\.",
    r"\1Canada.",
    content,
    flags=re.DOTALL
)

# Check all other JOKER cards and fix them individually
fixes = [
    ('NVDA', 'USA'), ('AMD', 'USA'), ('APP', 'USA'), ('BTDR', 'USA'),
    ('CLS', 'USA'), ('FIX', 'USA'), ('LLY', 'USA'), ('EME', 'USA'),
    ('GDWN', 'UK'), ('IDR', 'Spain'), ('ALNSC', 'France'), ('STX', 'USA')
]

for ticker, country in fixes:
    pattern = rf"(ticker: '{ticker}'.*?bullets: \[\"[^\"]+— [a-z ]+in )[A-Za-z?]+\."
    replacement = rf"\1{country}."
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('public/cards.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed bullets for all JOKER cards with correct countries")
