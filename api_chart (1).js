// api/chart.js — Finnhub 1-year daily candle data with daily KV cache

export const config = { runtime: 'edge' };

// Simple in-memory cache (per cold-start; edge functions may share)
// Key: ticker, Value: { ts: timestamp, data: [...] }
const cache = {};
const CACHE_TTL = 60 * 60 * 6 * 1000; // 6 hours

// Yahoo Finance → Finnhub ticker conversion
// Finnhub uses: AAPL (US), AAPL.L (London), AAPL.DE (Xetra), etc.
// Yahoo uses same suffixes so we can use them directly for most exchanges.
// Exceptions: Yahoo .ST = Stockholm; Finnhub = same .ST ✓
// Yahoo .HE = Helsinki; Finnhub = same .HE ✓
// Yahoo .OL = Oslo; Finnhub = same .OL ✓
// Yahoo .PA = Paris; Finnhub = same .PA ✓
// Yahoo .MI = Milan; Finnhub = same .MI ✓
// Yahoo .VI = Vienna; Finnhub = same .VI ✓
// Yahoo .BR = Brussels; Finnhub = same .BR ✓
// Yahoo .CO = Copenhagen; Finnhub = same .CO ✓
// Yahoo .TO = Toronto; Finnhub = same .TO ✓
// Yahoo dashes: BETS-B.ST → Finnhub: BETS-B.ST ✓ (Finnhub handles this)
function toFinnhubTicker(yahooTicker) {
    // Direct passthrough — Finnhub supports the same suffix convention
    return yahooTicker;
}

export default async function handler(req) {
    const url = new URL(req.url);
    const ticker = url.searchParams.get('ticker');

    if (!ticker) {
        return new Response(JSON.stringify({ error: 'Missing ticker' }), {
            status: 400,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });
    }

    const finnhubTicker = toFinnhubTicker(ticker);
    const now = Date.now();

    // Return cached data if fresh
    if (cache[finnhubTicker] && (now - cache[finnhubTicker].ts) < CACHE_TTL) {
        return new Response(JSON.stringify(cache[finnhubTicker].data), {
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*', 'X-Cache': 'HIT' }
        });
    }

    const apiKey = process.env.FINNHUB_API_KEY;
    if (!apiKey) {
        return new Response(JSON.stringify({ error: 'API key not configured' }), {
            status: 500,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });
    }

    // 1-year range: from 1 year ago to today
    const toTs = Math.floor(now / 1000);
    const fromTs = toTs - 365 * 24 * 60 * 60;

    try {
        const finnhubUrl = `https://finnhub.io/api/v1/stock/candle?symbol=${encodeURIComponent(finnhubTicker)}&resolution=W&from=${fromTs}&to=${toTs}&token=${apiKey}`;
        const res = await fetch(finnhubUrl);
        if (!res.ok) throw new Error('Finnhub fetch failed: ' + res.status);

        const json = await res.json();

        if (json.s !== 'ok' || !json.c || json.c.length === 0) {
            // Try with daily resolution as fallback
            const dailyUrl = `https://finnhub.io/api/v1/stock/candle?symbol=${encodeURIComponent(finnhubTicker)}&resolution=D&from=${fromTs}&to=${toTs}&token=${apiKey}`;
            const res2 = await fetch(dailyUrl);
            const json2 = await res2.json();

            if (json2.s !== 'ok' || !json2.c || json2.c.length === 0) {
                return new Response(JSON.stringify({ error: 'No data', ticker: finnhubTicker }), {
                    status: 404,
                    headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
                });
            }

            // Downsample daily to ~52 weekly points to keep payload small
            const closes = json2.c;
            const timestamps = json2.t;
            const step = Math.max(1, Math.floor(closes.length / 52));
            const sampled = [];
            for (let i = 0; i < closes.length; i += step) {
                sampled.push({ t: timestamps[i], c: closes[i] });
            }
            // Always include last point
            const last = closes.length - 1;
            if (sampled[sampled.length - 1].t !== timestamps[last]) {
                sampled.push({ t: timestamps[last], c: closes[last] });
            }

            cache[finnhubTicker] = { ts: now, data: sampled };
            return new Response(JSON.stringify(sampled), {
                headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
            });
        }

        // Weekly data — map to { t, c } pairs
        const result = json.t.map((t, i) => ({ t, c: json.c[i] }));

        cache[finnhubTicker] = { ts: now, data: result };
        return new Response(JSON.stringify(result), {
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });

    } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), {
            status: 500,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });
    }
}
