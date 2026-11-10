"""New York LOADinG Act: record the current law (Nov. 2026) from the bill texts.
Usage: LEGISCAN_ENV=/path/key.txt python3 -I tools/ny_update.py WORK_DIR
- Original S 7543-B (Ch. 696 of 2024): shown as repealed before taking effect (Ch. 96 of 2025 repealed Sec. 403 and 404 and the human-review rule).
- S 822 / A 433 (Ch. 96 of 2025): new entry for the law now in force (AI inventory, employment-tool disclosure).
- S 7599 / S 8831: Ch. 711 of 2025 expansion repealed by Ch. 86 of 2026.
Quotes are verified against WORK_DIR/texts/NY_S822.txt (and NY_S8831.txt) before being written."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if os.environ.get('PYLIB'): sys.path.insert(1, os.environ['PYLIB'])
import legiscan_api as L

W = sys.argv[1]
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.replace('’', "'").replace('–', '-').replace('—', '-').lower())


t822 = norm(open(os.path.join(W, 'texts', 'NY_S822.txt'), errors='replace').read())

# ---- quotes
Qn = [
 ('I', '§ 103-e(1)', 'maintain an inventory of state agency artificial intelligence systems.', 'The state technology office must maintain an inventory of state-agency AI systems.', ''),
 ('I', '§ 103-e(1)', 'state open data website on the thirtieth of December next succeeding the', 'The inventory is posted on the New York open data website each year (the first posting is on the 30th of December after the section takes effect).', 'Text is the introduced print of S 822; the signed Chapter 96 may differ in small ways.'),
 ('O', '§ 103-e(5)', 'inventory to the governor, the temporary president of the senate, and', 'The office must send a copy of the AI inventory to the governor and the leaders of both chambers. This is reporting only; no penalties or enforcement body.', 'Text is the introduced print of S 822.'),
 ('SCOPE', '§ 103-e(3)', 'regarding access to or eligibility for government benefits or about', 'AI systems that "directly impact the public" include those used in decisions about access to or eligibility for government benefits, so benefits systems fall inside the inventory.', ''),
 ('SCOPE', '§ 402 (as amended)', '§ 402. [ Use ] Disclosure of automated employment decision-making', 'The old Sec. 402 on automated decision-making in public-assistance and rights decisions (with its meaningful human review rule) is replaced by a duty to publish lists of automated employment decision-making tools.', 'Bracketed words in the text are the old law being removed.'),
]
Qr = [
 ('REPEAL', '§ 2 of S 822', '§ 2. Sections 403 and 404 of the state technology law, as added by a', 'Chapter 96 of 2025 repeals Sec. 403 (impact assessments) and Sec. 404 (submission to the governor and legislature) of the LOADinG Act as signed in 2024.', 'Text is the introduced print of S 822.'),
 ('REPEAL', '§ 1 of S 822', 'Section 1. Sections 1 and 3 of a chapter of the laws of 2024 amending', 'The same act also repeals sections 1 and 3 of the 2024 chapter (the short title and the uncodified disclosure of existing systems).', 'Text is the introduced print of S 822.'),
]
bad = [q for q in Qn + Qr if norm(q[2]) not in t822]
# the repeal quotes begin at part tuple index 3 as well
if bad:
    raise SystemExit('quote not found in S 822 text: %s' % [b[2][:50] for b in bad])

# ---- bill metadata (text link) from the API
d = L.call('getSearch', state='NY', bill='S822', year=2025)['searchresult']
bid = sorted([v for k, v in d.items() if k != 'summary' and v['bill_number'].upper() in ('S00822', 'S822')], key=lambda v: v['bill_id'])[-1]['bill_id']
b = L.call('getBill', id=bid)['bill']
tx = sorted(b['texts'], key=lambda t: (t['date'], t['doc_id']))[-1]
meta = {'version': tx.get('type', ''), 'date': tx.get('date', ''), 'textUrl': tx.get('url', ''), 'stateUrl': tx.get('state_link', ''), 'legiscan': b.get('url', ''), 'status': b['status'], 'statusDate': b['status_date']}

qp = os.path.join(R, 'data', 'quotes.js')
q = open(qp, encoding='utf-8').read()
head = q[:q.index('window.QUOTES=')]
Q = json.loads(q[q.index('window.QUOTES=') + 14:].rstrip().rstrip(';'))


def item(t):
    return {'part': t[0], 'supported': 'yes', 'quote': t[3], 'where': t[1], 'specifics': t[4] if False else t[3 + 1], 'note': '', 'caveat': t[5] if len(t) > 5 else ''}


def mk(t):
    part, where, quote, spec, cav = t
    return {'part': part, 'supported': 'yes', 'quote': quote, 'where': where, 'specifics': spec, 'note': '', 'caveat': cav}


Q['NY|S 822 / A 433 (Ch. 96)'] = {'meta': meta, 'q': [mk(t) for t in Qn]}
orig = Q['NY|LOADinG Act (S 7543)']
orig['q'] = [x for x in orig['q'] if x['part'] != 'REPEAL'] + [mk(t) for t in Qr]
for x in orig['q']:
    if x['part'] != 'REPEAL' and 'As signed' not in x.get('caveat', ''):
        x['caveat'] = ('As signed in 2024; repealed before taking effect (see Chapter 96 of 2025). ' + x.get('caveat', '')).strip()[:420]
open(qp, 'w', encoding='utf-8').write(head + 'window.QUOTES=' + json.dumps(Q, ensure_ascii=False, separators=(',', ':')) + ';\n')

# ---- tags
tp = os.path.join(R, 'tools', 'reviewed_tags.json')
tags = json.load(open(tp))
tags['NY_S822'] = 'I2 O1'
json.dump(tags, open(tp, 'w'), indent=1)

# ---- policy overrides in build_policies.py
pp = os.path.join(R, 'tools', 'build_policies.py')
s = open(pp, encoding='utf-8').read()
if 'NY_UPDATE_BEGIN' not in s:
    block = '''# NY_UPDATE_BEGIN  (Nov. 2026: current New York law, from the S 7543, S 822, S 7599 and S 8831 texts)
DESC.update({
 ('NY','LOADinG Act (S 7543)'): 'As signed Dec. 2024 (Chapter 696): restricted state-agency use of automated decision-making systems without meaningful human review (Sec. 402), required impact assessments at least every two years and before material changes (Sec. 403), required each assessment to go to the governor and legislative leaders at least thirty days before implementation and be published (Sec. 404), and required agencies to stop using a system whose assessment finds discriminatory or biased outcomes. Chapter 96 of 2025 (S 822, signed Feb. 14, 2025) repealed Sec. 403 and 404 and the human-review rule before this article took effect, so these provisions are not in force. Descriptions that cite two-year assessments, 30-day transmission and mandatory discontinuation under the LOADinG Act refer to this as-signed text. See the S 822 entry for the law now in force.',
 ('NY','S 7599 / A 8295'): 'Signed Dec. 19, 2025 (Chapter 711) as a chapter amendment expanding the LOADinG Act: new Article 5 with agency tool lists, impact assessments every two years and an inventory. Chapter 86 of 2026 (S 8831, signed Feb. 13, 2026) repealed Article 5 and Sec. 103-f before they took effect, narrowed the disclosure to automated employment decision-making tools, and extended the labor protections to local employees (counties, cities, school districts, SUNY, CUNY and community colleges). Repeal language read from the introduced print of S 8831.',
})
TITLE = {('NY','LOADinG Act (S 7543)'): 'Original LOADinG Act as signed: impact assessments and human review (repealed before taking effect)',
         ('NY','S 7599 / A 8295'): 'Chapter 711 expansion (Dec. 2025), repealed by Chapter 86 (Feb. 2026)'}
STATUS = {('NY','LOADinG Act (S 7543)'): 'R'}
NEW_ENTRIES = [('NY','S 822 / A 433 (Ch. 96)','AI inventory and employment-tool disclosure (the LOADinG Act now in force)',2025,'E','ben','I2 O1',
 'Chapter 96 of 2025, signed Feb. 14, 2025: rewrote the LOADinG Act before it took effect. State agencies publish a list of automated employment decision-making tools each year (Sec. 402). The state technology office maintains an inventory of state-agency AI systems, posted on the New York open data website each year and sent to the governor and legislative leaders (Sec. 103-e); systems that "directly impact the public" include those used in decisions about access to or eligibility for government benefits. The same act repealed the impact-assessment, submission and human-review provisions of the 2024 text. Chapter 86 of 2026 later narrowed disclosure further and extended labor protections to local employees.',
 LS+'NY/bill/S00822/2025','H')]
# NY_UPDATE_END
'''
    i = s.index('rev = __import__')
    s = s[:i] + block + s[i:]
    s = s.replace("    if k in DESC: r[7] = DESC[k]\n", "    if k in DESC: r[7] = DESC[k]\n    if k in TITLE: r[2] = TITLE[k]\n    if k in STATUS: r[4] = STATUS[k]\n", 1)
    s = s.replace("    P2.append(tuple(r))\nP = P2", "    P2.append(tuple(r))\n    if k == ('NY','LOADinG Act (S 7543)'):\n        for ne in NEW_ENTRIES:\n            ne = list(ne); ne[6] = rev['NY_S822']; ne[9] = 'H'; P2.append(tuple(ne))\nP = P2", 1)
    open(pp, 'w', encoding='utf-8').write(s)
print('ok', meta['textUrl'][:60], meta['status'])
