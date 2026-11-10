"""HTTP status of every link in data/policies.js and data/quotes.js. Usage: python3 -I tools/check_links.py
LegiScan answers scripted requests with 403 even for valid pages, so those are reported separately as 'blocked to scripts'."""
import json, subprocess, sys, os, collections
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


def load_js(p, v):
    s = open(p, encoding='utf-8').read()
    return json.loads(s[s.index(v + '=') + len(v) + 1:].rstrip().rstrip(';'))


POL = load_js(os.path.join(R, 'data', 'policies.js'), 'window.POL')
Q = load_js(os.path.join(R, 'data', 'quotes.js'), 'window.QUOTES')
urls = collections.OrderedDict()
for p in POL:
    if p[8]:
        urls.setdefault(p[8], []).append(p[0] + ' ' + p[1] + ' (source)')
for lab, v in Q.items():
    for k in ('textUrl', 'stateUrl', 'legiscan'):
        u = v['meta'].get(k)
        if u:
            urls.setdefault(u, []).append(lab + ' ' + k)
res = collections.Counter()
bad = []
for u, who in urls.items():
    r = subprocess.run(['curl', '-sL', '-m', '25', '-A', 'Mozilla/5.0', '-o', '/dev/null', '-w', '%{http_code}', '--max-redirs', '5', u], capture_output=True, text=True)
    code = r.stdout.strip()
    host = u.split('/')[2]
    if 'legiscan.com' in host:
        res['legiscan (blocked to scripts: %s)' % code] += 1
    elif code.startswith('2'):
        res['ok'] += 1
    else:
        res['FAILED %s' % code] += 1
        bad.append((code, u, who[0]))
print(len(urls), 'links;', dict(res))
for b in bad:
    print(b)
