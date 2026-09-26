// Vercel serverless function: the lead list, for the owner only.
//
//   GET /api/leads             -> HTML table
//   GET /api/leads?format=csv  -> CSV download
//
// Access: you must be signed in to valujack.com (the normal email link) with
// an address in ADMINS. Everyone else gets 404, so the page does not even
// reveal that it exists.

import { Redis } from '@upstash/redis';
import crypto from 'node:crypto';

const ADMINS = ['radek.majewski@gmail.com'];

const redis = new Redis({
  url: process.env.KV_REST_API_URL,
  token: process.env.KV_REST_API_TOKEN,
});

function sessionEmail(req) {
  const secret = process.env.SESSION_SECRET;
  if (!secret) return null;
  const jar = {};
  (req.headers.cookie || '').split(';').forEach(p => {
    const i = p.indexOf('=');
    if (i > 0) jar[p.slice(0, i).trim()] = decodeURIComponent(p.slice(i + 1).trim());
  });
  const raw = jar.vj_session;
  if (!raw) return null;
  const parts = String(raw).split('.');
  if (parts.length !== 3) return null;
  const body = `${parts[0]}.${parts[1]}`;
  const expected = crypto.createHmac('sha256', secret).update(body).digest('base64url');
  const a = Buffer.from(parts[2]), b = Buffer.from(expected);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
  if (Number(parts[1]) < Date.now()) return null;
  try { return Buffer.from(parts[0], 'base64url').toString('utf8'); } catch (_e) { return null; }
}

const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const csvCell = s => { const v = String(s == null ? '' : s); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; };

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  const me = (sessionEmail(req) || '').toLowerCase();
  if (!ADMINS.includes(me)) return res.status(404).send('Not found');

  let rows = [];
  try {
    const emails = (await redis.smembers('vj_leads')) || [];
    const recs = await Promise.all(emails.map(e => redis.get(`vj_lead:${e}`)));
    const pros = await Promise.all(emails.map(e => redis.get(`vj_pro:${e}`)));
    rows = emails.map((e, i) => {
      const r = recs[i] ? (typeof recs[i] === 'string' ? JSON.parse(recs[i]) : recs[i]) : { email: e };
      const p = pros[i] ? (typeof pros[i] === 'string' ? JSON.parse(pros[i]) : pros[i]) : null;
      return { ...r, pro: p ? (p.source || 'yes') : '' };
    }).sort((a, b) => String(b.first || '').localeCompare(String(a.first || '')));
  } catch (e) {
    console.error('leads:', e);
    return res.status(500).send('Could not read the list.');
  }

  if (req.query && req.query.format === 'csv') {
    const head = ['email', 'first', 'last', 'count', 'consent', 'pro', 'consentAt', 'consentText'];
    const lines = [head.join(',')].concat(rows.map(r => [r.email, r.first, r.last, r.count || 1, r.consent ? 'yes' : 'no', r.pro, r.consentAt, r.consentText].map(csvCell).join(',')));
    res.setHeader('Content-Type', 'text/csv; charset=utf-8');
    res.setHeader('Content-Disposition', `attachment; filename="valujack_leads_${new Date().toISOString().slice(0, 10)}.csv"`);
    return res.status(200).send('\ufeff' + lines.join('\n'));
  }

  const yes = rows.filter(r => r.consent).length;
  const tr = rows.map(r => `<tr><td>${esc(r.email)}</td><td>${esc(String(r.first || '').slice(0, 10))}</td><td>${esc(String(r.last || '').slice(0, 10))}</td><td class=n>${esc(r.count || 1)}</td><td class="${r.consent ? 'y' : 'no'}">${r.consent ? 'yes' : 'no'}</td><td>${esc(r.pro)}</td></tr>`).join('');
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  return res.status(200).send(`<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><meta name=robots content=noindex>
<title>ValuJack leads</title><style>
body{margin:0;background:#1F3D24;color:#E8F5EE;font-family:Georgia,serif;padding:24px 16px}
h1{font-size:1.5rem;margin:0 0 6px}p{color:#A8C4B4;margin:0 0 18px}
a.btn{display:inline-block;background:#C9A84C;color:#0A1A0A;text-decoration:none;font-family:Arial,sans-serif;font-weight:700;letter-spacing:.08em;font-size:.85rem;padding:10px 16px;border-radius:8px;margin-bottom:18px}
.wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;min-width:560px;font-size:.95rem}
th{text-align:left;font-family:Arial,sans-serif;font-size:.72rem;letter-spacing:.14em;color:#7AB898;border-bottom:1px solid #3F6B4A;padding:8px}
td{padding:8px;border-bottom:1px solid #2E5236}td.n{text-align:right}.y{color:#7AB898}.no{color:#D89A6A}
</style></head><body>
<h1>ValuJack leads</h1><p>${rows.length} sign-ups &middot; ${yes} agreed to be emailed &middot; only email those marked <b class=y>yes</b></p>
<a class=btn href="/api/leads?format=csv">DOWNLOAD CSV</a>
<div class=wrap><table><tr><th>EMAIL</th><th>FIRST</th><th>LAST</th><th>VISITS</th><th>CONSENT</th><th>PRO</th></tr>${tr}</table></div>
</body></html>`);
}
