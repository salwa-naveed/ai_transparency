"""Builds data/outcomes.js from LegiScan bulk datasets (CSV Basic, one folder per state session).

Usage:  python3 -I tools/build_outcomes.py "/path/to/AI Data"

LegiScan status codes: 1 introduced, 2 engrossed, 3 enrolled, 4 passed (enacted), 5 vetoed, 6 failed.
Output status codes used by the site: E enacted, P passed both chambers / awaiting governor,
V vetoed, F failed or died when the session ended, A still alive in a legislature that is in session.

AI relevance is a keyword match on the bill title and the first 250 characters of its description.
It is a screen, not a judgment: expect some false positives and misses. The 115 laws in data/data.js
come from the Transparency Coalition report and are not filtered by this script.
"""
import csv, glob, html, json, os, re, sys

csv.field_size_limit(10**8)
ROOT = sys.argv[1]
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'outcomes.js')
DATA_JS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'data.js')

CORE = re.compile(r"artificial intelligence|chatbot|chat bot|deepfake|deep fake|synthetic media|synthetic content|synthetic image|digital replica|automated decision|algorithm|generative|machine learning|companion (?:chat|bot|ai)|conversational|large language|frontier (?:model|artificial|ai)|digitally altered|digitally manipulated|digital forger|computer-generated|ai-generated|ai generated|ai system|ai tool|ai model|ai technolog|ai companion|ai chat", re.I)
AI_CS = re.compile(r"\bAI\b")
RESOLUTION = re.compile(r'^[A-Z]{0,2}(?:CR|R)\d')
ALIVE = {'MA', 'MI', 'NJ', 'NC', 'OH', 'PA', 'DC'}   # legislatures still able to act as of Oct. 2026 (per Transparency Coalition)

# Reviewed by hand: enacted/vetoed AI bills that the keyword screen found but that are not in the Coalition's report,
# and bills the screen missed. Keyed by (state, normalized bill number).
EXCLUDE = {('CA','SB1047'),('CT','HB5222'),('CT','HB5229'),('CT','SB417'),('FL','S1816'),('IL','SB3020'),('MD','SB114'),('MD','SB905'),
           ('MS','SB2294'),('SC','H5085'),('TN','HB2246'),('TN','SB2586'),('AZ','SB1214'),('RI','H8060'),('RI','S3338'),('CT','SB483')}
# Framework tags (I N P M C V; 2 close analogue, 1 loose) for the extra enacted/pending bills, assigned by hand from LegiScan descriptions.
TAGS = {('ME','LD517'):'N1', ('NY','S8828'):'V2 C1', ('NY','S8831'):'I1 P1', ('NY','A9581'):'I1 M1',
        ('RI','H7538'):'N1', ('RI','S2570'):'N1', ('TN','HB1455'):'C1', ('TN','SB1493'):'C1', ('TN','HB1513'):'N1', ('TN','SB1624'):'N1',
        ('TN','HB1946'):'C1', ('TN','SB1700'):'C1', ('UT','HB320'):'C1', ('VA','SB384'):'M1 C1', ('VA','SB394'):'I1'}
FORCE = {('AZ','HB2133'),('CO','HB1210'),('KY','HB366')}

def num(b):
    return re.sub(r'^([A-Za-z]+)0+(\d)', r'\1\2', re.sub(r'\s', '', b)).upper()

def screen(r):
    t = r['title'] + ' ' + r['description'][:250]
    return bool(CORE.search(t) or AI_CS.search(t))

def klass(r):
    s = int(r['status'] or 0); sd = r['status_date']; la = r['last_action_date']; st = r['st']
    if RESOLUTION.match(r['num']): return None
    if s == 4: return 'E' if sd >= '2026-01-01' else None
    if s == 5: return 'V' if sd >= '2026-01-01' else None
    if s == 6: return 'F' if sd >= '2026-01-01' else None
    if s == 3: return 'P'
    if s in (1, 2):
        if st == 'NY' and s == 2 and 'return' in r['last_action'].lower(): return 'P'   # NY: passed both houses, not yet delivered
        if st in ALIVE: return 'A'
        if la >= '2026-01-01' or r['sess'].startswith('2026'): return 'F'
    return None

def category(t):
    t = t.lower()
    rules = [('ther', r'therap|psychotherap|mental health'), ('chat', r'chatbot|companion|conversational'),
             ('elec', r'election|campaign|political'), ('deep', r'deepfake|deep fake|digital replica|synthetic media|synthetic depiction|csam|child sexual|intimate image|likeness|digital forg|computer-generated'),
             ('hlth', r'health|insur|medical|patient|utilization|prior auth'), ('edu', r'school|student|education|teacher|college|universit'),
             ('mkt', r'pric|rent|antitrust|collu'), ('work', r'employ|worker|workplace|labor'), ('priv', r'privacy|data broker|biometric|personal data'),
             ('aud', r'audit|frontier|verification organization|safety framework|catastrophic'), ('disc', r'disclos|provenance|transparen|watermark|label'),
             ('adm', r'automated decision|algorithm|government|state agenc|agency')]
    for c, p in rules:
        if re.search(p, t): return c
    return 'oth'

# bills already listed in the Coalition set (data/data.js) are skipped here
txt = open(DATA_JS, encoding='utf-8').read()
known = set()
for st, b in re.findall(r"^\['(\w\w)','([^']+)'", txt, re.M):
    for x in re.split(r'/| and ', b):
        n = re.sub(r'\s', '', x).upper()
        for c in {n, n.replace('HB','H'), n.replace('SB','S'), n.replace('S','SB',1), n.replace('H','HB',1), n.replace('A','AB',1)}:
            known.add((st, c))

seen = set(); out = []
for d in sorted(glob.glob(ROOT + '/*/*')):
    f = d + '/csv/bills.csv'
    if not os.path.exists(f): continue
    st = os.path.basename(os.path.dirname(d)).split('-')[0]
    if st == 'US': continue
    for r in csv.DictReader(open(f, encoding='utf-8', errors='replace')):
        r['st'] = st; r['sess'] = os.path.basename(d); r['num'] = num(r['bill_number'])
        if r['bill_id'] in seen: continue
        key = (st, r['num'])
        if key in EXCLUDE: continue
        if not (screen(r) or key in FORCE): continue
        c = klass(r)
        if not c: continue
        seen.add(r['bill_id'])
        if key in known: continue
        title = html.unescape(re.sub(r'\s+', ' ', r['title']).strip())
        if len(title) < 25 or title.upper().startswith('AN ACT TO AMEND TENNESSEE'):
            title = html.unescape(re.sub(r'\s+', ' ', r['description']).strip())
        title = title[:110] + ('…' if len(title) > 110 else '')
        note = re.sub(r'\s+', ' ', r['last_action']).strip()[:80] + (' (' + r['last_action_date'] + ')' if r['last_action_date'] else '')
        out.append([st, r['num'], title, category(r['title'] + ' ' + r['description'][:250]), c, note, 'L', r['url'], TAGS.get(key, '')])

out.sort(key=lambda x: ('EPVAF'.index(x[4]), x[0], x[1]))
exp = sorted({os.path.basename(p) for p in glob.glob(ROOT + '/*')})
with open(OUT_PATH, 'w', encoding='utf-8') as fh:
    fh.write('/* Generated by tools/build_outcomes.py from LegiScan bulk datasets (exported Oct. 2026). Do not edit by hand.\n'
             '   [state, bill, title, category, status E/P/V/F/A, last action, source tag, LegiScan URL, framework tags] */\n')
    fh.write('window.OUT=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
import collections
print(len(out), dict(collections.Counter(x[4] for x in out)))
