#!/usr/bin/env python3
"""Mock price API for local testing — returns fairValue*0.85 for every card (simulates undervalued)"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, re, urllib.parse, sys
sys.path.insert(0, '.')

# Read fairValues from cards.js
import re
with open('/Users/radekmajewski/Downloads/valujack/public/cards.js') as f:
    content = f.read()

# Extract all yahooTicker + fairValue pairs
prices = {}
for m in re.finditer(r"yahooTicker:\s*'([^']+)'.*?fairValue:\s*([\d.]+)", content):
    ticker, fv = m.group(1), float(m.group(2))
    prices[ticker] = {"price": round(fv * 0.85, 2), "currency": "USD"}

print(f"Loaded {len(prices)} tickers")

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if '/api/prices' in self.path:
            qs = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(qs)
            tickers = params.get('tickers', [''])[0].split(',')
            result = {t: prices.get(t, {"price": 50, "currency": "USD"}) for t in tickers}
            body = json.dumps(result).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()
    def log_message(self, *a): pass

print("Mock API running on http://localhost:3001")
HTTPServer(('', 3001), Handler).serve_forever()
