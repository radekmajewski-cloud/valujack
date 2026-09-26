// Vercel serverless function: start a subscription.
//
//   POST /api/checkout   { plan: 'monthly' | 'annual' }  -> { url }
//
// Returns a Stripe Checkout URL. The caller is redirected there; Stripe
// collects the card and the email, and the webhook grants access afterwards.
//
// Deliberately does NOT require a signed-in session. Forcing someone to create
// an account before they can pay adds a step before the only action that
// matters. If they are signed in we prefill their address; if not, Stripe asks
// for one and they sign in with it afterwards.
//
// No Stripe SDK: two form-encoded POSTs is less code than a dependency tree.

import crypto from 'node:crypto';

const PRICES = {
  monthly: 'price_1UFXLhFT4gg0XGmJ9hdI8lHK',
  annual: 'price_1UFXQ3FT4gg0XGmJxdux6Y5f',
};

const COOKIE = 'vj_session';

function sessionEmail(req) {
  const secret = process.env.SESSION_SECRET;
  if (!secret) return null;
  const jar = {};
  (req.headers.cookie || '').split(';').forEach(p => {
    const i = p.indexOf('=');
    if (i > 0) jar[p.slice(0, i).trim()] = decodeURIComponent(p.slice(i + 1).trim());
  });
  const raw = jar[COOKIE];
  if (!raw) return null;
  const parts = String(raw).split('.');
  if (parts.length !== 3) return null;
  const body = `${parts[0]}.${parts[1]}`;
  const expected = crypto.createHmac('sha256', secret).update(body).digest('base64url');
  const a = Buffer.from(parts[2]), b = Buffer.from(expected);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
  if (Number(parts[1]) < Date.now()) return null;
  try {
    return Buffer.from(parts[0], 'base64url').toString('utf8');
  } catch (_e) {
    return null;
  }
}

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'method not allowed' });
  }

  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) {
    console.error('checkout: STRIPE_SECRET_KEY missing');
    return res.status(500).json({ error: 'payments are not configured' });
  }

  const body = typeof req.body === 'string'
    ? JSON.parse(req.body || '{}') : (req.body || {});
  const plan = body.plan === 'annual' ? 'annual' : 'monthly';
  const price = PRICES[plan];

  const host = req.headers['x-forwarded-host'] || req.headers.host;
  const proto = String(host).startsWith('localhost')
    ? 'http' : (req.headers['x-forwarded-proto'] || 'https').split(',')[0];
  const origin = `${proto}://${host}`;

  const email = sessionEmail(req);

  const form = new URLSearchParams();
  form.set('mode', 'subscription');
  form.set('line_items[0][price]', price);
  form.set('line_items[0][quantity]', '1');
  form.set('success_url', `${origin}/?subscribed=1`);
  form.set('cancel_url', `${origin}/?subscribed=0`);
  // The webhook needs an address to grant against, and subscription events
  // carry metadata where the session's customer_details do not.
  form.set('subscription_data[metadata][vj_plan]', plan);
  if (email) {
    form.set('customer_email', email);
    form.set('subscription_data[metadata][vj_email]', email);
  }
  // Card details are never seen by us; Stripe hosts the page.
  form.set('billing_address_collection', 'auto');

  try {
    const r = await fetch('https://api.stripe.com/v1/checkout/sessions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${key}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: form.toString(),
    });
    const data = await r.json();
    if (!r.ok) {
      console.error('stripe checkout:', r.status, JSON.stringify(data));
      return res.status(502).json({ error: 'could not start checkout' });
    }
    return res.status(200).json({ url: data.url });
  } catch (e) {
    console.error('stripe checkout:', e);
    return res.status(502).json({ error: 'could not start checkout' });
  }
}
