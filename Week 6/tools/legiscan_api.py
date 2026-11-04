"""Small LegiScan API client. Reads the key from the LEGISCAN_API_KEY environment variable or from a .env file whose path
is given in LEGISCAN_ENV. The key is never written to any output file."""
import json, os, time, urllib.parse, urllib.request

def key():
    k = os.environ.get('LEGISCAN_API_KEY')
    p = os.environ.get('LEGISCAN_ENV')
    if not k and p and os.path.exists(p):
        for line in open(p):
            if line.startswith('LEGISCAN_API_KEY='): k = line.split('=', 1)[1].strip()
    if not k: raise SystemExit('Set LEGISCAN_API_KEY or LEGISCAN_ENV')
    return k

_calls = 0
def call(op, **params):
    global _calls
    q = urllib.parse.urlencode(dict(params, key=key(), op=op))
    req = urllib.request.Request('https://api.legiscan.com/?' + q, headers={'User-Agent': 'policy-research-script'})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode('utf-8'))
    _calls += 1
    if data.get('status') != 'OK':
        raise RuntimeError('LegiScan error for %s: %s' % (op, data.get('alert', data)))
    time.sleep(0.3)
    return data

def calls(): return _calls
