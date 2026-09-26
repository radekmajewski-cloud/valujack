"""
leads.py - list, export and remove Pro waitlist sign-ups.

Reads KV_REST_API_URL / KV_REST_API_TOKEN from .env.local (vercel env pull .env.local)
or from the environment, like grant_pro.py.

    python3 ./leads.py list
    python3 ./leads.py export              # -> ~/Desktop/valujack_leads.csv
    python3 ./leads.py remove someone@example.com   # unsubscribe / GDPR erasure
"""
import csv, json, os, sys, urllib.request

def env():
    vals = dict(os.environ)
    if os.path.exists('.env.local'):
        for line in open('.env.local'):
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                vals.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    url, tok = vals.get('KV_REST_API_URL'), vals.get('KV_REST_API_TOKEN')
    if not url or not tok:
        sys.exit('KV_REST_API_URL / KV_REST_API_TOKEN not found. Run: vercel env pull .env.local')
    return url, tok

URL, TOKEN = env()

def cmd(*args):
    req = urllib.request.Request(URL, data=json.dumps(list(args)).encode(),
                                 headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())['result']

def records():
    out = []
    for e in sorted(cmd('SMEMBERS', 'vj_leads') or []):
        raw = cmd('GET', f'vj_lead:{e}')
        if raw:
            out.append(json.loads(raw) if isinstance(raw, str) else raw)
    return out

if len(sys.argv) < 2 or sys.argv[1] not in ('list', 'export', 'remove'):
    sys.exit(__doc__)
if sys.argv[1] == 'list':
    rs = records()
    print(f"{'email':38} {'first':12} {'last':12} {'n':>3}  consent")
    for r in rs:
        print(f"{r['email']:38} {r['first'][:10]:12} {r['last'][:10]:12} {r.get('count',1):>3}  {'yes' if r.get('consent') else 'no'}")
    print(f"\n{len(rs)} lead(s), {sum(1 for r in rs if r.get('consent'))} agreed to be emailed.")
elif sys.argv[1] == 'export':
    rs = records()
    path = os.path.expanduser('~/Desktop/valujack_leads.csv')
    with open(path, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['email', 'first', 'last', 'count', 'consent', 'consentAt', 'consentText'])
        for r in rs: w.writerow([r['email'], r['first'], r['last'], r.get('count', 1), 'yes' if r.get('consent') else 'no', r.get('consentAt', ''), r.get('consentText', '')])
    print(f'{len(rs)} lead(s) written to {path}')
else:
    if len(sys.argv) < 3: sys.exit('usage: python3 ./leads.py remove someone@example.com')
    e = sys.argv[2].strip().lower()
    cmd('DEL', f'vj_lead:{e}'); cmd('SREM', 'vj_leads', e)
    print(f'removed {e}')
