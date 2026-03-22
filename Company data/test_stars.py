INDEX = "/Users/radekmajewski/Downloads/ValuJack/public/index.html"
OUTPUT = "/Users/radekmajewski/Downloads/ValuJack/public/index_stars.html"
with open(INDEX,"r",encoding="utf-8") as f: html = f.read()
FT = "gridTemplateColumns: '1fr 1fr', gap: 4 } },"
BT = "\"COMPANY HEALTH\"),"
print("FT found:", FT in html)
print("BT found:", BT in html)
with open(OUTPUT,"w",encoding="utf-8") as f: f.write(html)
print("Done")