// Vercel serverless function: sign-in and entitlement.
//
// Three actions on one route, so there is one place to reason about sessions.
//
//   POST /api/auth            { email }        -> issues a single-use magic link
//   GET  /api/auth?token=...                   -> verifies it, sets the session cookie
//   GET  /api/auth?action=me                   -> { signedIn, email, pro }
//   POST /api/auth?action=out                  -> clears the session
//
// Entitlement lives in Redis under vj_pro:<email>. Nothing here writes it —
// that is the Stripe webhook's job. Until then it can be set by hand, which is
// how the flow gets tested before payments exist.
//
// Sessions are a signed cookie, not a stored session: the cookie carries the
// email and an expiry, signed with SESSION_SECRET. Nothing to look up, and
// nothing an attacker can forge without the secret.

import { Redis } from '@upstash/redis';
import crypto from 'node:crypto';

const redis = new Redis({
  url: process.env.KV_REST_API_URL,
  token: process.env.KV_REST_API_TOKEN,
});

const COOKIE = 'vj_session';
const SESSION_DAYS = 90;
const LINK_MINUTES = 20;

// Open beta: anyone who asks for a sign-in link gets PRO (source 'beta')
// until subscriptions open. Set to false at paid launch.
const OPEN_BETA = true;
const CONSENT_TEXT = 'Email me when subscriptions open, and occasional ValuJack news. Unsubscribe any time.';

function secret() {
  const s = process.env.SESSION_SECRET;
  if (!s || s.length < 24) {
    throw new Error('SESSION_SECRET is missing or too short');
  }
  return s;
}

function sign(value) {
  return crypto.createHmac('sha256', secret()).update(value).digest('base64url');
}

function makeSession(email) {
  const exp = Date.now() + SESSION_DAYS * 86400000;
  const body = `${Buffer.from(email).toString('base64url')}.${exp}`;
  return `${body}.${sign(body)}`;
}

function readSession(raw) {
  if (!raw) return null;
  const parts = String(raw).split('.');
  if (parts.length !== 3) return null;
  const body = `${parts[0]}.${parts[1]}`;
  const expected = sign(body);
  // constant-time compare, so a wrong signature leaks nothing by timing
  const a = Buffer.from(parts[2]);
  const b = Buffer.from(expected);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
  if (Number(parts[1]) < Date.now()) return null;
  try {
    return Buffer.from(parts[0], 'base64url').toString('utf8');
  } catch (_e) {
    return null;
  }
}

function cookiesFrom(req) {
  const out = {};
  (req.headers.cookie || '').split(';').forEach(p => {
    const i = p.indexOf('=');
    if (i > 0) out[p.slice(0, i).trim()] = decodeURIComponent(p.slice(i + 1).trim());
  });
  return out;
}

function setCookie(res, value, maxAgeSec) {
  res.setHeader('Set-Cookie',
    `${COOKIE}=${value}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=${maxAgeSec}`);
}

function cleanEmail(v) {
  const e = String(v || '').trim().toLowerCase();
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(e) ? e : null;
}

async function isPro(email) {
  try {
    const raw = await redis.get(`vj_pro:${email}`);
    if (!raw) return false;
    const rec = typeof raw === 'string' ? JSON.parse(raw) : raw;
    if (!rec || rec.status !== 'active') return false;
    if (rec.until && Number(rec.until) < Date.now()) return false;
    return true;
  } catch (_e) {
    // Never lock a paying subscriber out because Redis blinked. Fail closed on
    // access but do not throw: the caller shows the free deck.
    return false;
  }
}

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  const action = (req.query && req.query.action) || '';
  const token = (req.query && req.query.token) || '';

  try {
    secret();
  } catch (e) {
    console.error('auth config:', e.message);
    return res.status(500).json({ error: 'auth not configured' });
  }

  // ── who am I ────────────────────────────────────────────────────────────
  if (action === 'me') {
    const email = readSession(cookiesFrom(req)[COOKIE]);
    if (!email) return res.status(200).json({ signedIn: false, pro: false });
    return res.status(200).json({ signedIn: true, email, pro: await isPro(email) });
  }

  // ── sign out ────────────────────────────────────────────────────────────
  if (action === 'out') {
    setCookie(res, '', 0);
    return res.status(200).json({ ok: true });
  }

  // ── follow the link ─────────────────────────────────────────────────────
  if (req.method === 'GET' && token) {
    let email = null;
    try {
      email = await redis.get(`vj_magic:${token}`);
    } catch (e) {
      console.error('magic lookup:', e);
    }
    if (!email) {
      return res.redirect(302, '/?signin=expired');
    }
    // single use
    try { await redis.del(`vj_magic:${token}`); } catch (_e) {}
    setCookie(res, makeSession(String(email)), SESSION_DAYS * 86400);
    return res.redirect(302, '/?signin=ok');
  }

  // ── ask for a link ──────────────────────────────────────────────────────
  if (req.method === 'POST') {
    const body = typeof req.body === 'string'
      ? JSON.parse(req.body || '{}') : (req.body || {});
    const email = cleanEmail(body.email);
    if (!email) return res.status(400).json({ error: 'a valid email is required' });

    // Open beta: grant PRO unless the address already has a record (a paying
    // subscriber or a hand-granted comp must never be overwritten).
    if (OPEN_BETA) {
      try {
        const existing = await redis.get(`vj_pro:${email}`);
        if (!existing) {
          await redis.set(`vj_pro:${email}`, JSON.stringify({
            status: 'active', source: 'beta',
            granted: new Date().toISOString().slice(0, 10),
            until: null, note: 'open beta',
          }));
        }
      } catch (e) { console.error('beta grant:', e); }
    }

    // Lead list: who asked, and whether they agreed to be emailed. Consent is
    // only ever added here, never silently removed.
    try {
      const now = new Date().toISOString();
      const lk = `vj_lead:${email}`;
      const raw = await redis.get(lk);
      const prev = raw ? (typeof raw === 'string' ? JSON.parse(raw) : raw) : null;
      const agreed = body.consent === true;
      const consent = agreed || !!(prev && prev.consent);
      await redis.set(lk, JSON.stringify({
        email,
        first: (prev && prev.first) || now,
        last: now,
        count: ((prev && prev.count) || 0) + 1,
        source: (prev && prev.source) || 'signin',
        consent,
        consentText: consent ? CONSENT_TEXT : '',
        consentAt: agreed ? now : ((prev && prev.consentAt) || ''),
      }));
      await redis.sadd('vj_leads', email);
      // Tell the owner about each NEW sign-up (first time only).
      if (!prev && process.env.RESEND_API_KEY) {
        try {
          await fetch('https://api.resend.com/emails', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${process.env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({
              from: process.env.MAIL_FROM || 'ValuJack <info@valujack.com>',
              to: ['radek.majewski@gmail.com'],
              subject: `New ValuJack sign-up: ${email}`,
              text: `${email} asked for a sign-in link and now has Pro (beta).\n`
                  + `Agreed to be emailed: ${consent ? 'yes' : 'no'}\n\n`
                  + `All sign-ups: https://www.valujack.com/api/leads`,
            }),
          });
        } catch (e) { console.error('notify owner:', e); }
      }
    } catch (e) { console.error('lead store:', e); }

    const t = crypto.randomBytes(32).toString('base64url');
    try {
      await redis.set(`vj_magic:${t}`, email, { ex: LINK_MINUTES * 60 });
    } catch (e) {
      console.error('magic store:', e);
      return res.status(500).json({ error: 'could not issue a link' });
    }

    const host = req.headers['x-forwarded-host'] || req.headers.host;
    const proto = String(host).startsWith('localhost') ? 'http' : (req.headers['x-forwarded-proto'] || 'https').split(',')[0];
    const link = `${proto}://${host}/api/auth?token=${t}`;

    // No email sender wired yet. Returning the link keeps the flow testable
    // end to end; this branch disappears once Resend is configured.
    if (!process.env.RESEND_API_KEY) {
      console.log('magic link for', email, link);
      return res.status(200).json({ ok: true, sent: false, link });
    }

    try {
      const r = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.RESEND_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          from: process.env.MAIL_FROM || 'ValuJack <info@valujack.com>',
          to: [email],
          subject: 'Your ValuJack sign-in link',
          text: `Open this link to sign in to ValuJack:\n\n${link}\n\n`
              + `It works once and expires in ${LINK_MINUTES} minutes. `
              + `If you did not ask for it, ignore this email.`,
        }),
      });
      if (!r.ok) {
        console.error('resend:', r.status, await r.text());
        return res.status(502).json({ error: 'could not send the email' });
      }
    } catch (e) {
      console.error('resend:', e);
      return res.status(502).json({ error: 'could not send the email' });
    }

    return res.status(200).json({ ok: true, sent: true });
  }

  return res.status(405).json({ error: 'method not allowed' });
}
