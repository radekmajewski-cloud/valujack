// Vercel serverless function: the SHARED draw log (the "notebook").
//
// Two jobs, one place:
//   GET  /api/draw          -> returns the draws from the last 14 days
//                              (the app uses these tickers to block repeats)
//   POST /api/draw          -> records today's two cards (idempotent per date)
//                              with ticker, company, date, price -> the track record
//
// Storage: Upstash Redis, connected via the Vercel integration.
// Vercel injected the credentials as KV_REST_API_URL / KV_REST_API_TOKEN,
// so we point the client at those names explicitly.

import { Redis } from '@upstash/redis';

const redis = new Redis({
  url: process.env.KV_REST_API_URL,
  token: process.env.KV_REST_API_TOKEN,
});

// One key holds the whole log as a JSON array of day-rows.
const LOG_KEY = 'vj_draw_log';
const WINDOW_DAYS = 14;
const ONE_DAY_MS = 86400000;

function todayStr() {
  const d = new Date();
  return d.getFullYear() + '-' +
    String(d.getMonth() + 1).padStart(2, '0') + '-' +
    String(d.getDate()).padStart(2, '0');
}

async function readLog() {
  const raw = await redis.get(LOG_KEY);
  if (!raw) return [];
  // Upstash may return an already-parsed object/array or a JSON string.
  if (Array.isArray(raw)) return raw;
  if (typeof raw === 'string') {
    try { return JSON.parse(raw); } catch (_e) { return []; }
  }
  return [];
}

export default async function handler(req, res) {
  // CORS — same as prices.js
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // ── READ: last 14 days of draws ──────────────────────────────────────
  if (req.method === 'GET') {
    try {
      const log = await readLog();
      const cutoff = Date.now() - WINDOW_DAYS * ONE_DAY_MS;
      const recent = log.filter(r => {
        if (!r) return false;
        const t = r.ts != null ? r.ts : (r.date ? new Date(r.date).getTime() : 0);
        return t >= cutoff;
      });
      return res.status(200).json({ draws: recent });
    } catch (error) {
      console.error('draw GET error:', error);
      // Never break the picker — return empty so the app falls back gracefully.
      return res.status(200).json({ draws: [], error: error.message });
    }
  }

  // ── WRITE: record today's draw (idempotent per date) ─────────────────
  if (req.method === 'POST') {
    try {
      const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
      const date = body.date || todayStr();

      // Minimal validation — must have both tickers to record a row.
      if (!body.free_ticker || !body.pro_ticker) {
        return res.status(400).json({ error: 'free_ticker and pro_ticker required' });
      }

      const row = {
        date: date,
        free_id: body.free_id ?? null,
        free_ticker: body.free_ticker,
        free_company: body.free_company || '',
        free_price: body.free_price ?? null,
        free_currency: body.free_currency || '',
        free_type: body.free_type || '',
        free_stars: body.free_stars || 0,
        pro_id: body.pro_id ?? null,
        pro_ticker: body.pro_ticker,
        pro_company: body.pro_company || '',
        pro_price: body.pro_price ?? null,
        pro_currency: body.pro_currency || '',
        pro_type: body.pro_type || '',
        pro_stars: body.pro_stars || 0,
        ts: Date.now(),
      };

      const log = await readLog();
      const ix = log.findIndex(r => r && r.date === date);

      // FIRST-WRITE-WINS for the day's CARDS (so the track-record start price
      // and the chosen stocks don't change if the page is reopened later),
      // but allow filling in a price if the first write happened before prices
      // had loaded.
      if (ix >= 0) {
        const existing = log[ix];
        const sameCards =
          existing.free_ticker === row.free_ticker &&
          existing.pro_ticker === row.pro_ticker;
        if (sameCards) {
          // Only backfill prices that were missing on the first write.
          if (existing.free_price == null && row.free_price != null) existing.free_price = row.free_price;
          if (existing.pro_price == null && row.pro_price != null) existing.pro_price = row.pro_price;
          log[ix] = existing;
        }
        // If cards differ, keep the first recorded draw (first-write-wins).
      } else {
        log.push(row);
      }

      await redis.set(LOG_KEY, JSON.stringify(log));

      return res.status(200).json({ ok: true, date: date });
    } catch (error) {
      console.error('draw POST error:', error);
      return res.status(500).json({ error: 'Failed to record draw', message: error.message });
    }
  }

  return res.status(405).json({ error: 'Method not allowed' });
}
