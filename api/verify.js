// Diagnostic endpoint v2 — read-only.
//
//   ?tickers=CX,ORK.OL        resolve symbols (as before)
//   ?search=CombinedX+AB      ask Yahoo which symbols match a company name
//
// The search mode is what lets a wrong ticker be repaired from evidence:
// look up the name, then resolve each candidate and keep only the one whose
// currency and exchange match the card. Nothing is ever inferred from the
// ticker string alone — that is how CX became Cemex.
//
// Runs on Vercel, so it never rate-limits the caller.

const UA = { 'User-Agent': 'Mozilla/5.0' };

async function resolve(sym) {
  try {
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(sym)}`;
    const r = await fetch(url, { headers: UA });
    if (!r.ok) return { error: `http_${r.status}` };
    const meta = (await r.json())?.chart?.result?.[0]?.meta;
    if (!meta) return { error: 'no_meta' };
    return {
      symbol: meta.symbol || null,
      longName: meta.longName || meta.shortName || null,
      currency: meta.currency || null,
      exchange: meta.exchangeName || null,
      fullExchange: meta.fullExchangeName || null,
      type: meta.instrumentType || null,
      price: meta.regularMarketPrice ?? null
    };
  } catch (e) {
    return { error: String(e.message || e).slice(0, 80) };
  }
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const { tickers, search } = req.query;

  // ── name search ─────────────────────────────────────────────────────────
  if (search) {
    try {
      const url = `https://query2.finance.yahoo.com/v1/finance/search`
                + `?q=${encodeURIComponent(search)}&quotesCount=10&newsCount=0`;
      const r = await fetch(url, { headers: UA });
      if (!r.ok) return res.status(200).json({ query: search, error: `http_${r.status}`, candidates: [] });

      const quotes = (await r.json())?.quotes || [];
      const candidates = quotes
        .filter(q => q.symbol)
        .map(q => ({
          symbol: q.symbol,
          name: q.longname || q.shortname || null,
          exchange: q.exchange || null,
          exchDisp: q.exchDisp || null,
          type: q.quoteType || null
        }));

      // Resolve each candidate so the caller sees real currency and exchange,
      // not just what the search index claims.
      const resolved = {};
      await Promise.all(candidates.slice(0, 8).map(async c => {
        resolved[c.symbol] = await resolve(c.symbol);
      }));

      return res.status(200).json({ query: search, candidates, resolved });
    } catch (e) {
      return res.status(200).json({ query: search, error: String(e.message || e).slice(0, 80), candidates: [] });
    }
  }

  // ── bulk resolve ────────────────────────────────────────────────────────
  if (!tickers) {
    return res.status(400).json({ error: 'tickers or search parameter required' });
  }

  const list = tickers.split(',').map(t => t.trim()).filter(Boolean).slice(0, 25);
  const out = {};
  await Promise.all(list.map(async t => { out[t] = await resolve(t); }));
  return res.status(200).json(out);
}
