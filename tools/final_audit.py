"""Consistency checks on the finished data. Usage: python3 -I tools/final_audit.py WORK_DIR
Checks: every quote is an exact match in its stored text; every tagged framework part has at least one quote; quotes exist only for tagged parts;
site outcome agrees with the LegiScan record fetched from the API; every entry has a full-text link."""
import json, os, re, sys

W = sys.argv[1]
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


def load_js(p, v):
    s = open(p, encoding='utf-8').read()
    return json.loads(s[s.index(v + '=') + len(v) + 1:].rstrip().rstrip(';'))


def norm(s):
    s = s.replace('’', "'").replace('‘', "'").replace('–', '-').replace('—', '-').lower()
    return re.sub(r'[^a-z0-9]', '', s)


POL = load_js(os.path.join(R, 'data', 'policies.js'), 'window.POL')
Q = load_js(os.path.join(R, 'data', 'quotes.js'), 'window.QUOTES')
src = open(os.path.join(R, 'tools', 'audit_prepare.py')).read()
ns = {}
exec(src[src.index('KEYS = {'):src.index('EXTRA_FILES')], ns)
KEYS = ns['KEYS']
EXTRA = {'UT_HB444': ['UT_HB450.txt'], 'NY_S7599': ['NY_S8831.txt'], 'NY_S7543': ['NY_S822.txt']}
issues = []
nq = 0
for p in POL:
    st, bill, title, yr, status, scope, tags, desc, url, conf = p
    k = KEYS[(st, bill)]
    lab = st + '|' + bill
    e = Q.get(lab, {'q': [], 'meta': {}})
    hay = ''.join(norm(open(os.path.join(W, 'texts', f), errors='replace').read()) for f in [k + '.txt'] + EXTRA.get(k, []))
    for q in e['q']:
        if q.get('quote'):
            nq += 1
            if norm(q['quote']) not in hay:
                issues.append(('QUOTE NOT IN TEXT', k, q['part'], q['quote'][:50]))
    tp = {t[0] for t in tags.split()}
    for t in tags.split():
        if not [q for q in e['q'] if q['part'] == t[0] and q.get('quote')]:
            issues.append(('TAG WITHOUT QUOTE', k, t))
    for q in e['q']:
        if q.get('quote') and q['part'] not in tp and q['part'] not in ('SCOPE', 'REPEAL'):
            issues.append(('QUOTE FOR UNTAGGED PART', k, q['part'], q['supported']))
    jp = os.path.join(W, 'texts', k + '.json')
    if os.path.exists(jp):
        r = json.load(open(jp))
        ok = {'E': [4], 'R': [4], 'A': [1, 2, 3], 'F': [1, 2, 6]}[status]
        if r['status'] not in ok:
            issues.append(('STATUS MISMATCH', k, 'site', status, 'legiscan', r['status'], r['status_date']))
    if not e['meta'].get('textUrl'):
        issues.append(('NO TEXT URL', k))
print(len(POL), 'entries,', nq, 'quotes checked; issues:', len(issues))
for i in issues:
    print(i)
