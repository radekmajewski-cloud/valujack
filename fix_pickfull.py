import re

CARDS_PATH = '/Users/radekmajewski/Downloads/valujack/public/cards.js'

pickfulls = {
    284: "Adyen has been beaten down significantly from its peak — yet the underlying payment processing business continues to grow and the competitive moat is intact. The market has punished a period of margin investment without crediting the long-term platform dominance. Quality at a contrarian entry.",
    285: "EPAM has sold off sharply on geopolitical concerns tied to its Eastern European delivery model — but the company has successfully diversified operations and client demand for high-quality software engineering remains strong. Fundamentals intact at a beaten-down price.",
    286: "Fiserv has pulled back sharply despite consistent earnings delivery — the market is pricing in more disruption than the data supports. Mission-critical payment infrastructure for thousands of banks and merchants does not disappear. A quality fintech franchise at a contrarian price.",
    287: "Palo Alto Networks has pulled back on near-term billings concerns — yet the underlying shift to AI-powered cybersecurity consolidation plays directly to its platform strength. The dip has created an entry point into the dominant cybersecurity platform at a more attractive valuation.",
    288: "Paycom has been sold down aggressively after slowing growth concerns — but the business generates exceptional free cash flow and serves a sticky mid-market HR software niche with very high switching costs. The selloff has created a quality entry point in a durable software franchise.",
    289: "Zimmer Biomet has underperformed as surgical volumes and procedure timing disappointed — yet hip and knee replacement demand is structurally growing with ageing populations. The medical device franchise is intact and the stock trades below fair value on temporary headwinds.",
    290: "Zscaler has pulled back sharply as enterprise software spending normalised — but zero trust security adoption is a multi-year structural trend that is still in early innings. The dip has created an entry point into the leading zero trust platform at a more reasonable valuation.",
    291: "ADP has compounded its dividend for over 45 consecutive years — a record matched by fewer than a dozen companies globally. The stock offers a growing yield backed by a truly recession-proof payroll franchise that every employer must use regardless of economic conditions.",
    292: "BAE Systems is positioned at the centre of the largest Western defence spending cycle in a generation — NATO commitments, rising threat perceptions, and government budget prioritisation all point to sustained demand growth for its ships, vehicles, and electronic systems.",
    293: "Clorox offers a growing dividend yield from one of the most recession-resistant consumer staples portfolios in the US. Households do not stop buying bleach and cleaning products in downturns — the brand commands shelf space and consumer loyalty that has been built over decades.",
    295: "McDonald's has compounded its dividend for over 45 consecutive years and the stock is trading below fair value — an unusual combination for one of the most durable franchises in consumer history. The asset-light royalty model means the company collects fees regardless of commodity costs.",
    296: "S&P Global holds a regulated duopoly in credit ratings — a business that cannot be disrupted because issuers must pay for ratings to access capital markets. The stock trades modestly below fair value offering a rare entry point into one of the world's great regulatory moats.",
    298: "Omnicom is in the process of acquiring Interpublic to create the world's largest advertising group — a transaction that should drive significant cost synergies and pricing power. The stock trades at a meaningful discount to fair value ahead of deal completion.",
    299: "Greggs is the fastest-growing food-on-the-go brand in the UK — expanding its store estate, evening hours, and delivery channels simultaneously. The stock trades at a substantial discount to fair value, offering an attractive entry point into one of the UK's most consistent retail compounders.",
    300: "ASML is the only company on earth that can manufacture extreme ultraviolet lithography machines — the tools that every advanced chipmaker must use to produce the next generation of semiconductors. Trading at a meaningful discount to fair value with a multi-year order backlog already secured.",
    302: "JDE Peets owns the most recognisable coffee brands in continental Europe and is growing its premium Peets and specialty coffee presence. The stock trades below fair value despite consistent cash generation — the market has undervalued the durability of coffee consumption across economic cycles.",
    303: "Leonardo is the primary beneficiary of Italy's defence modernisation programme and rising NATO commitments across Southern Europe. With a large order backlog, growing helicopter and electronic warfare revenues, and a stock trading at a deep discount to fair value, the opportunity is compelling.",
    304: "Rolls-Royce has completed a dramatic operational turnaround — returning to profitability, restoring cash generation, and rebuilding its order book. The stock still trades below fair value despite the transformation, offering an entry point before the market fully prices in the recovery.",
    305: "Saab is at the centre of Sweden's NATO accession and a generational increase in Scandinavian defence spending. The Gripen fighter jet programme, submarine contracts, and radar systems are all benefiting from structural budget increases — and the stock still trades below fair value.",
    307: "Rheinmetall is the primary supplier of artillery ammunition, armoured vehicles, and air defence systems to NATO's eastern flank rearmament. With a multi-year order backlog, production capacity expansion underway, and a stock trading at a substantial discount to fair value, the setup is exceptional.",
    308: "Amazon is trading below fair value despite AWS being the world's largest cloud platform with structural growth ahead. The market continues to undervalue the combination of cloud dominance, advertising growth, and logistics infrastructure — three compounding businesses in one stock.",
    309: "Deckers owns HOKA — one of the fastest-growing running shoe brands in the world — alongside the culturally durable UGG franchise. The stock trades at a substantial discount to fair value despite exceptional brand momentum, creating a rare entry point into a premium footwear compounder.",
    310: "Datadog is the standard observability platform for modern cloud infrastructure — and the stock trades at a meaningful discount to fair value. As enterprises accelerate cloud migration and AI workload deployment, monitoring and observability spending grows with it.",
    311: "Lululemon has built one of the most loyal consumer communities in premium apparel — and the stock trades at a significant discount to fair value after a period of demand softening. The brand's pricing power, community model, and international expansion runway remain structurally intact.",
    312: "Prosus holds a major stake in Tencent — one of China's most dominant technology platforms — at a persistent discount to the value of its underlying assets. The stock has been trading below the sum of its parts for years, offering patient investors access to world-class internet assets at a discount.",
    313: "Qualcomm holds fundamental 5G patents that every smartphone manufacturer must licence — a royalty stream that is largely independent of production cycles. Trading near fair value, the stock offers exposure to structural 5G and AI edge computing growth with a growing dividend.",
    314: "Universal Health Services operates acute care hospitals and behavioural health centres at a time when US mental health infrastructure is chronically undersupplied. The stock trades at a meaningful discount to fair value — the market undervalues the pricing power and structural demand for behavioural health beds.",
}

with open(CARDS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

updated = 0
for card_id, new_pickfull in pickfulls.items():
    pattern = re.compile(
        rf"(id: {card_id},.*?pickFull: \")([^\"]*)(\")",
        re.DOTALL
    )
    new_content = pattern.sub(rf"\g<1>{new_pickfull}\g<3>", content)
    if new_content != content:
        content = new_content
        updated += 1
        print(f"✅ {card_id}")
    else:
        print(f"❌ {card_id}: not found")

with open(CARDS_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nUpdated {updated}/27 cards")
