import re

# Read the current index.html
with open('/Users/radekmajewski/Downloads/valujack/public/index.html', 'r') as f:
    content = f.read()

# Find the start and end of THE CARDS section
start_pattern = r'React\.createElement\("p", \{ style: \{ color: \'#5A8A6A\'.*?\}, "THE CARDS"\),'
end_pattern = r'React\.createElement\("p", \{ style: \{ color: \'#A8C4B4\'.*?"Fast Growth.*?\)\)\),'

# Find the positions
start_match = re.search(start_pattern, content, re.DOTALL)
end_match = re.search(end_pattern, content, re.DOTALL)

if start_match and end_match:
    start_pos = start_match.start()
    end_pos = end_match.end()
    
    # New strategy cards section
    new_section = '''React.createElement("p", { style: { color: '#5A8A6A', fontSize: '0.72rem', fontFamily: 'Barlow Condensed,sans-serif', fontWeight: 700, letterSpacing: '0.2em', marginBottom: 8 } }, "THE CARDS"),
                    React.createElement("h2", { style: { fontFamily: 'Playfair Display,serif', fontSize: '1.7rem', color: '#E8F5EE', lineHeight: 1.2, marginBottom: 24 } }, "Six strategies. Six proven approaches."),
                    
                    React.createElement("div", { 
                        className: "strategy-grid",
                        style: { 
                            display: 'grid', 
                            gridTemplateColumns: isMobile ? '1fr' : 'repeat(2, 1fr)', 
                            gap: '16px', 
                            marginBottom: '32px' 
                        } 
                    },
                        // KING card
                        React.createElement("div", {
                            className: "strategy-card",
                            style: {
                                background: 'linear-gradient(135deg, #C0152A 0%, #8B0F1F 100%)',
                                borderRadius: '12px',
                                padding: '16px',
                                border: '2px solid rgba(255,255,255,0.1)'
                            }
                        },
                            React.createElement("div", { style: { display: 'flex', alignItems: 'center', marginBottom: 12 } },
                                React.createElement("span", { style: { fontSize: '1.8rem', marginRight: 12 } }, "♚"),
                                React.createElement("div", null,
                                    React.createElement("h3", { style: { color: '#FFFFFF', fontSize: '1.1rem', fontWeight: 700, margin: 0, fontFamily: 'Barlow Condensed,sans-serif' } }, "KING"),
                                    React.createElement("p", { style: { color: '#FFD700', fontSize: '0.8rem', margin: 0, fontWeight: 600 } }, "FREE"))),
                            React.createElement("h4", { style: { color: '#FFFFFF', fontSize: '0.95rem', fontWeight: 600, marginBottom: 8, fontFamily: 'Barlow Condensed,sans-serif' } }, "Dividend Aristocrats"),
                            React.createElement("p", { style: { color: 'rgba(255,255,255,0.9)', fontSize: '0.85rem', lineHeight: 1.4, margin: 0 } }, "Companies that have raised dividends for 10+ consecutive years. Steady income while you wait for price appreciation.")),

                        // JACK card  
                        React.createElement("div", {
                            className: "strategy-card",
                            style: {
                                background: 'linear-gradient(135deg, #1A1A1A 0%, #000000 100%)',
                                borderRadius: '12px',
                                padding: '16px',
                                border: '2px solid rgba(255,255,255,0.1)'
                            }
                        },
                            React.createElement("div", { style: { display: 'flex', alignItems: 'center', marginBottom: 12 } },
                                React.createElement("span", { style: { fontSize: '1.8rem', marginRight: 12 } }, "♝"),
                                React.createElement("div", null,
                                    React.createElement("h3", { style: { color: '#FFFFFF', fontSize: '1.1rem', fontWeight: 700, margin: 0, fontFamily: 'Barlow Condensed,sans-serif' } }, "JACK"),
                                    React.createElement("p", { style: { color: '#FFD700', fontSize: '0.8rem', margin: 0, fontWeight: 600 } }, "FREE"))),
                            React.createElement("h4", { style: { color: '#FFFFFF', fontSize: '0.95rem', fontWeight: 600, marginBottom: 8, fontFamily: 'Barlow Condensed,sans-serif' } }, "Minervini Momentum"),
                            React.createElement("p", { style: { color: 'rgba(255,255,255,0.9)', fontSize: '0.85rem', lineHeight: 1.4, margin: 0 } }, "Stocks in confirmed uptrends with accelerating earnings. Ride the winners when momentum is on your side.")),

                        // TWO card
                        React.createElement("div", {
                            className: "strategy-card",
                            style: {
                                background: 'linear-gradient(135deg, #7A1A1A 0%, #5A1A1A 100%)',
                                borderRadius: '12px',
                                padding: '16px',
                                border: '2px solid rgba(192, 192, 192, 0.3)'
                            }
                        },
                            React.createElement("div", { style: { display: 'flex', alignItems: 'center', marginBottom: 12 } },
                                React.createElement("span", { style: { fontSize: '1.8rem', marginRight: 12, color: '#C0C0C0' } }, "♠"),
                                React.createElement("div", null,
                                    React.createElement("h3", { style: { color: '#FFFFFF', fontSize: '1.1rem', fontWeight: 700, margin: 0, fontFamily: 'Barlow Condensed,sans-serif' } }, "TWO"),
                                    React.createElement("p", { style: { color: '#FFD700', fontSize: '0.8rem', margin: 0, fontWeight: 600 } }, "FREE"))),
                            React.createElement("h4", { style: { color: '#FFFFFF', fontSize: '0.95rem', fontWeight: 600, marginBottom: 8, fontFamily: 'Barlow Condensed,sans-serif' } }, "Contrarian Recovery"),
                            React.createElement("p", { style: { color: 'rgba(255,255,255,0.9)', fontSize: '0.85rem', lineHeight: 1.4, margin: 0 } }, "Quality companies beaten down below fair value. Phoenix stocks ready to rise from temporary setbacks.")),

                        // QUEEN card
                        React.createElement("div", {
                            className: "strategy-card",
                            style: {
                                background: 'linear-gradient(135deg, #4A1A6B 0%, #6B2A8B 100%)',
                                borderRadius: '12px',
                                padding: '16px',
                                border: '2px solid rgba(255,215,0,0.3)'
                            }
                        },
                            React.createElement("div", { style: { display: 'flex', alignItems: 'center', marginBottom: 12 } },
                                React.createElement("span", { style: { fontSize: '1.8rem', marginRight: 12 } }, "♛"),
                                React.createElement("div", null,
                                    React.createElement("h3", { style: { color: '#FFFFFF', fontSize: '1.1rem', fontWeight: 700, margin: 0, fontFamily: 'Barlow Condensed,sans-serif' } }, "QUEEN"),
                                    React.createElement("p", { style: { color: '#FFD700', fontSize: '0.8rem', margin: 0, fontWeight: 600 } }, "PRO"))),
                            React.createElement("h4", { style: { color: '#FFFFFF', fontSize: '0.95rem', fontWeight: 600, marginBottom: 8, fontFamily: 'Barlow Condensed,sans-serif' } }, "Magic Formula"),
                            React.createElement("p", { style: { color: 'rgba(255,255,255,0.9)', fontSize: '0.85rem', lineHeight: 1.4, margin: 0 } }, "High-return businesses temporarily mispriced by the market. Quality companies without the premium price tag.")),

                        // ACE card
                        React.createElement("div", {
                            className: "strategy-card",
                            style: {
                                background: 'linear-gradient(135deg, #4A1A6B 0%, #6B2A8B 100%)',
                                borderRadius: '12px',
                                padding: '16px',
                                border: '2px solid rgba(255,215,0,0.3)'
                            }
                        },
                            React.createElement("div", { style: { display: 'flex', alignItems: 'center', marginBottom: 12 } },
                                React.createElement("span", { style: { fontSize: '1.8rem', marginRight: 12 } }, "♠"),
                                React.createElement("div", null,
                                    React.createElement("h3", { style: { color: '#FFFFFF', fontSize: '1.1rem', fontWeight: 700, margin: 0, fontFamily: 'Barlow Condensed,sans-serif' } }, "ACE"),
                                    React.createElement("p", { style: { color: '#FFD700', fontSize: '0.8rem', margin: 0, fontWeight: 600 } }, "PRO"))),
                            React.createElement("h4", { style: { color: '#FFFFFF', fontSize: '0.95rem', fontWeight: 600, marginBottom: 8, fontFamily: 'Barlow Condensed,sans-serif' } }, "Piotroski F-Score"),
                            React.createElement("p", { style: { color: 'rgba(255,255,255,0.9)', fontSize: '0.85rem', lineHeight: 1.4, margin: 0 } }, "Companies quietly improving behind the scenes. Nine financial strength indicators signal businesses getting stronger.")),

                        // JOKER card
                        React.createElement("div", {
                            className: "strategy-card",
                            style: {
                                background: 'linear-gradient(135deg, #4A1A6B 0%, #6B2A8B 100%)',
                                borderRadius: '12px',
                                padding: '16px',
                                border: '2px solid rgba(255,215,0,0.3)'
                            }
                        },
                            React.createElement("div", { style: { display: 'flex', alignItems: 'center', marginBottom: 12 } },
                                React.createElement("span", { style: { fontSize: '1.8rem', marginRight: 12 } }, "★"),
                                React.createElement("div", null,
                                    React.createElement("h3", { style: { color: '#FFFFFF', fontSize: '1.1rem', fontWeight: 700, margin: 0, fontFamily: 'Barlow Condensed,sans-serif' } }, "JOKER"),
                                    React.createElement("p", { style: { color: '#FFD700', fontSize: '0.8rem', margin: 0, fontWeight: 600 } }, "PRO"))),
                            React.createElement("h4", { style: { color: '#FFFFFF', fontSize: '0.95rem', fontWeight: 600, marginBottom: 8, fontFamily: 'Barlow Condensed,sans-serif' } }, "CANSLIM Growth"),
                            React.createElement("p", { style: { color: 'rgba(255,255,255,0.9)', fontSize: '0.85rem', lineHeight: 1.4, margin: 0 } }, "Tomorrow's market leaders found today. Explosive earnings growth backed by institutional buying and strong fundamentals.")))'''

    # Replace the section
    new_content = content[:start_pos] + new_section + content[end_pos:]
    
    # Write the updated file
    with open('/Users/radekmajewski/Downloads/valujack/public/index.html', 'w') as f:
        f.write(new_content)
    
    print("✅ Strategy cards section successfully replaced!")
    print("✅ Added TWO card (missing from original)")
    print("✅ All 6 strategies now visible as interactive cards")
else:
    print("❌ Could not find THE CARDS section to replace")
