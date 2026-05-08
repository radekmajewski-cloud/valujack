import re
from datetime import datetime

with open('public/index.html', 'r') as f:
    content = f.read()

# Find the stratRows section (lines 802-826 approximately)
old_section = '''                            let stratRows = [];
                            if (ec.type === 'KING') {
                                stratRows = [
                                    ['DIVIDEND %', fromMetrics('div') || '—'],
                                    ['P/E RATIO', pe],
                                ];
                            } else if (ec.type === 'QUEEN') {
                                stratRows = [
                                    ['RETURN ON CAPITAL', fromMetrics('roic') || fromScores('roic') || '—'],
                                    ['CASH FLOW %', fromMetrics('fcf') || fromScores('fcf yield', 'fcf') || '—'],
                                ];
                            } else if (ec.type === 'JACK') {
                                stratRows = [
                                    ['EARNINGS GROWTH', ec.epsGrowth || fromScores('eps growth', 'eps') || '—'],
                                    ['1Y PERFORMANCE', ec.rsRating || fromScores('rel. strength', 'rs rating') || '—'],
                                ];
                            } else if (ec.type === 'ACE') {
                                stratRows = [
                                    ['EARNINGS GROWTH', ec.epsGrowth || fromScores('eps growth', 'piotroski') || '—'],
                                    ['RETURN ON CAPITAL', fromMetrics('roic') || fromScores('roic') || '—'],
                                ];
                            } else if (ec.type === 'JOKER') {
                                stratRows = [
                                    ['EARNINGS GROWTH', ec.epsGrowth || fromScores('eps growth', 'eps') || '—'],
                                    ['REVENUE GROWTH', ec.revGrowth || fromScores('rev. growth', 'rev growth') || '—'],
                                ];
                            }'''

new_section = '''                            let stratRows = [];
                            if (ec.type === 'KING') {
                                stratRows = [
                                    ['DIVIDEND YIELD', fromMetrics('dividend yield', 'div') || '—'],
                                    ['ROIC', fromMetrics('roic') || '—'],
                                    ['P/E', fromMetrics('p/e', 'pe') || '—'],
                                    ['DEBT/EQUITY', fromMetrics('debt/equity', 'debt') || '—'],
                                ];
                            } else if (ec.type === 'JACK') {
                                stratRows = [
                                    ['PRICE STRENGTH', fromMetrics('price strength') || '—'],
                                    ['EPS GROWTH', fromMetrics('eps growth') || '—'],
                                    ['ROIC', fromMetrics('roic') || '—'],
                                    ['FREE CASH', fromMetrics('free cash') || '—'],
                                ];
                            } else if (ec.type === 'QUEEN') {
                                stratRows = [
                                    ['ROIC', fromMetrics('roic') || '—'],
                                    ['P/E', fromMetrics('p/e', 'pe') || '—'],
                                    ['EPS GROWTH', fromMetrics('eps growth') || '—'],
                                    ['DEBT/EQUITY', fromMetrics('debt/equity', 'debt') || '—'],
                                ];
                            } else if (ec.type === 'ACE') {
                                stratRows = [
                                    ['F-SCORE', fromMetrics('f-score', 'fscore') || '—'],
                                    ['ROIC', fromMetrics('roic') || '—'],
                                    ['FREE CASH', fromMetrics('free cash') || '—'],
                                    ['DEBT/EQUITY', fromMetrics('debt/equity', 'debt') || '—'],
                                ];
                            } else if (ec.type === 'JOKER') {
                                stratRows = [
                                    ['EPS GROWTH', fromMetrics('eps growth') || '—'],
                                    ['PRICE STRENGTH', fromMetrics('price strength') || '—'],
                                    ['ROIC', fromMetrics('roic') || '—'],
                                    ['FREE CASH', fromMetrics('free cash') || '—'],
                                ];
                            } else if (ec.type === 'TWO') {
                                stratRows = [
                                    ['ROIC', fromMetrics('roic') || '—'],
                                    ['P/E', fromMetrics('p/e', 'pe') || '—'],
                                    ['1M PERFORMANCE', fromMetrics('1m performance') || '—'],
                                    ['DEBT/EQUITY', fromMetrics('debt/equity', 'debt') || '—'],
                                ];
                            }'''

if old_section in content:
    content = content.replace(old_section, new_section)
    print("✓ Updated stratRows to show 4 metrics per strategy")
else:
    print("✗ Pattern not found - manual edit needed")

with open('public/index.html', 'w') as f:
    f.write(content)

print("✓ Done")

