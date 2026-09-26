// Vercel serverless function: Stripe webhook.
//
//   POST /api/stripe-webhook
//
// Writes the same vj_pro:<email> record that grant_pro.py writes, with
// source 'stripe' instead of 'comp'. The app cannot tell a paying subscriber
// from a comped tester, which is the point: one path for access.
//
// Two things this gets right that are easy to get wrong:
//
//   Signature verification. Anyone can POST to this URL. Without checking the
//   Stripe-Signature header, anyone could grant themselves a subscription.
//   That needs the RAW body, so body parsing is disabled below.
//
//   Expiry with grace. The record carries an 'until' taken from the
//   subscription's period end plus three days. A card that fails to renew at
//   midnight should not lock someone out before Stripe has retried.

import { Redis } from '@upstash/redis';
import crypto from 'node:crypto';

export const config = { api: { bodyParser: false } };

const redis = new Redis({
  url: process.env.KV_REST_API_URL,
  token: process.env.KV_REST_API_TOKEN,
});

const GRACE_DAYS = 3;

function rawBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', c => chunks.push(c));
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

// Stripe-Signature: t=<unix>,v1=<hex>[,v1=<hex>]
function verify(raw, header, secret) {
  if (!header || !secret) return false;
  const parts = {};
  String(header).split(',').forEach(p => {
    const i = p.indexOf('=');
    if (i > 0) {
      const k = p.slice(0, i).trim();
      const v = p.slice(i + 1).trim();
      (parts[k] = parts[k] || []).push(v);
    }
  });
  const t = parts.t && parts.t[0];
  const sigs = parts.v1 || [];
  if (!t || !sigs.length) return false;

  // Reject anything older than five minutes: a captured request should not be
  // replayable indefinitely.
  if (Math.abs(Date.now() / 1000 - Number(t)) > 300) return false;

  const expected = crypto.createHmac('sha256', secret)
    .update(`${t}.${raw.toString('utf8')}`).digest('hex');
  const a = Buffer.from(expected);
  return sigs.some(s => {
    const b = Buffer.from(s);
    return a.length === b.length && crypto.timingSafeEqual(a, b);
  });
}

async function stripeGet(path) {
  const r = await fetch(`https://api.stripe.com/v1/${path}`, {
    headers: { 'Authorization': `Bearer ${process.env.STRIPE_SECRET_KEY}` },
  });
  if (!r.ok) throw new Error(`stripe GET ${path}: ${r.status}`);
  return r.json();
}

async function grant(email, sub) {
  const until = sub && sub.current_period_end
    ? (sub.current_period_end * 1000) + GRACE_DAYS * 86400000
    : null;
  const rec = {
    status: 'active',
    source: 'stripe',
    granted: new Date().toISOString().slice(0, 10),
    until,
    note: (sub && sub.metadata && sub.metadata.vj_plan) || '',
    stripe_customer: sub ? sub.customer : null,
    stripe_subscription: sub ? sub.id : null,
  };
  await redis.set(`vj_pro:${email}`, JSON.stringify(rec));
  console.log('granted PRO to', email, 'until', until);
}

async function revoke(email, reason) {
  const raw = await redis.get(`vj_pro:${email}`);
  if (!raw) return;
  let rec;
  try {
    rec = typeof raw === 'string' ? JSON.parse(raw) : raw;
  } catch (_e) {
    rec = {};
  }
  // Never let Stripe revoke a hand-granted comp. They are different things and
  // a cancelled card should not remove access somebody was given.
  if (rec.source === 'comp') {
    console.log('left comp alone for', email);
    return;
  }
  await redis.del(`vj_pro:${email}`);
  console.log('revoked PRO for', email, '-', reason);
}

async function emailFor(sub) {
  if (sub && sub.metadata && sub.metadata.vj_email) return sub.metadata.vj_email;
  if (sub && sub.customer) {
    try {
      const c = await stripeGet(`customers/${sub.customer}`);
      if (c && c.email) return c.email;
    } catch (e) {
      console.error('customer lookup:', e.message);
    }
  }
  return null;
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'method not allowed' });
  }

  const secret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!secret) {
    console.error('webhook: STRIPE_WEBHOOK_SECRET missing');
    return res.status(500).end();
  }

  let raw;
  try {
    raw = await rawBody(req);
  } catch (e) {
    return res.status(400).end();
  }

  if (!verify(raw, req.headers['stripe-signature'], secret)) {
    console.error('webhook: bad signature');
    return res.status(400).end();
  }

  let event;
  try {
    event = JSON.parse(raw.toString('utf8'));
  } catch (_e) {
    return res.status(400).end();
  }

  try {
    const obj = event.data && event.data.object;

    if (event.type === 'checkout.session.completed') {
      const email = (obj.customer_details && obj.customer_details.email)
        || obj.customer_email;
      if (!email) {
        console.error('checkout completed with no email', obj.id);
      } else if (obj.subscription) {
        const sub = await stripeGet(`subscriptions/${obj.subscription}`);
        // Record the address on the subscription so later events can find it
        // without another lookup.
        if (!(sub.metadata && sub.metadata.vj_email)) {
          const f = new URLSearchParams();
          f.set('metadata[vj_email]', email);
          await fetch(`https://api.stripe.com/v1/subscriptions/${sub.id}`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${process.env.STRIPE_SECRET_KEY}`,
              'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: f.toString(),
          });
        }
        await grant(email.toLowerCase(), sub);
      }
    }

    else if (event.type === 'customer.subscription.updated'
          || event.type === 'customer.subscription.created') {
      const email = await emailFor(obj);
      if (email) {
        const live = obj.status === 'active' || obj.status === 'trialing';
        if (live) await grant(email.toLowerCase(), obj);
        else await revoke(email.toLowerCase(), `status ${obj.status}`);
      }
    }

    else if (event.type === 'customer.subscription.deleted') {
      const email = await emailFor(obj);
      if (email) await revoke(email.toLowerCase(), 'subscription cancelled');
    }

    else if (event.type === 'invoice.payment_succeeded') {
      // Renewal. Push the expiry out so an active subscriber never lapses
      // because the record went stale.
      if (obj.subscription) {
        const sub = await stripeGet(`subscriptions/${obj.subscription}`);
        const email = await emailFor(sub);
        if (email) await grant(email.toLowerCase(), sub);
      }
    }
  } catch (e) {
    // Returning 500 makes Stripe retry, which is what we want for a transient
    // Redis or network failure.
    console.error('webhook handler:', event.type, e);
    return res.status(500).end();
  }

  return res.status(200).json({ received: true });
}
