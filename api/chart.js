// api/chart.js — 1-year weekly price history via Yahoo Finance

export const config = { runtime: 'edge' };

const cache = {};
const CACHE_TTL = 6 * 60 * 60 * 1000;

export default async function handler(req) {
    const url = new URL(req.url);
    const ticker = url.searchParams.get('ticker');
    if (!ticker) {
        return new Response(JSON.stringify({ error: 'Missing ticker' }), {
            status: 400,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });
    }
    const now = Date.now();
    if (cache[ticker] && (now - cache[ticker].ts) < CACHE_TTL) {
        return new Response(JSON.stringify(cache[ticker].data), {
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });
    }
    const toTs = Math.floor(now / 1000);
    const fromTs = toTs - 365 * 24 * 60 * 60;
    try {
        const yahooUrl = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(ticker)}?interval=1wk&period1=${fromTs}&period2=${toTs}&includePrePost=false`;
        const res = await fetch(yahooUrl, {
            headers: { 'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json' }
        });
        if (!res.ok) throw new Error('Yahoo fetch failed: ' + res.status);
        const json = await res.json();
        const result = json?.chart?.result?.[0];
        if (!result || !result.timestamp || !result.indicators?.quote?.[0]?.close) {
            throw new Error('No data returned');
        }
        const timestamps = result.timestamp;
        const closes = result.indicators.quote[0].close;
        const points = timestamps
            .map((t, i) => ({ t, c: closes[i] }))
            .filter(p => p.c !== null && p.c !== undefined && !isNaN(p.c));
        if (points.length < 4) throw new Error('Insufficient data');
        cache[ticker] = { ts: now, data: points };
        return new Response(JSON.stringify(points), {
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });
    } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), {
            status: 500,
            headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
        });
    }
}
