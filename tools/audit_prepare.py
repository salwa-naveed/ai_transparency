"""Prepares input files for an independent audit of every quote and framework rating.
Usage: python3 -I tools/audit_prepare.py WORK_DIR
Needs WORK_DIR/texts/<KEY>.txt (from tools/fetch_texts.py; federal memos as FED_M-25-21.txt and FED_M-25-22.txt).
Writes WORK_DIR/audit_in_<n>.json (one file per audit group) and WORK_DIR/codebook.md.
Also runs the mechanical checks: is each quote an exact substring of the stored text (letters and digits only, case-insensitive)?"""
import json, os, re, sys

W = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')

KEYS = {('FED', 'OMB M-25-21'): 'FED_M-25-21', ('FED', 'OMB M-25-22'): 'FED_M-25-22', ('NY', 'LOADinG Act (S 7543)'): 'NY_S7543',
        ('NY', 'S 7599 / A 8295'): 'NY_S7599', ('NY', 'S 822 / A 433 (Ch. 96)'): 'NY_S822', ('CT', 'PA 23-16 (SB 1103)'): 'CT_SB1103', ('CT', 'PA 26-15 (SB 5)'): 'CT_SB5',
        ('MD', 'SB 818 (AI Governance Act)'): 'MD_SB818', ('VT', 'H 410 (Act 132)'): 'VT_H410', ('CA', 'AB 302'): 'CA_AB302',
        ('CA', 'SB 896'): 'CA_SB896', ('CO', 'SB 26-189'): 'CO_SB189', ('TX', 'HB 149 (TRAIGA)'): 'TX_HB149', ('TX', 'SB 1964'): 'TX_SB1964',
        ('TX', 'HB 2060'): 'TX_HB2060', ('KY', 'SB 4'): 'KY_SB4', ('MT', 'HB 178'): 'MT_HB178', ('AR', 'HB 1958 (Act 848)'): 'AR_HB1958',
        ('IN', 'SB 150'): 'IN_SB150', ('UT', 'HB 444 / HB 450'): 'UT_HB444', ('OH', 'SB 315'): 'OH_SB315', ('NC', 'H 565'): 'NC_H565',
        ('MI', 'HB 4537'): 'MI_HB4537', ('PA', 'HB 1925'): 'PA_HB1925', ('MA', 'H 77'): 'MA_H77', ('NY', 'A 7278'): 'NY_A7278',
        ('CA', 'SB 1248'): 'CA_SB1248', ('CA', 'SB 430'): 'CA_SB430', ('CA', 'AB 2412'): 'CA_AB2412', ('IL', 'HB 3567'): 'IL_HB3567',
        ('IL', 'SB 1366'): 'IL_SB1366', ('GA', 'HB 147'): 'GA_HB147', ('RI', 'H 7119'): 'RI_H7119', ('OK', 'HB 3545'): 'OK_HB3545',
        ('OR', 'HB 4103'): 'OR_HB4103', ('NH', 'SB 657'): 'NH_SB657', ('NH', 'HB 1506'): 'NH_HB1506', ('NM', 'SB 68'): 'NM_SB68',
        ('FL', 'S 146'): 'FL_S146', ('MS', 'HB 1640'): 'MS_HB1640', ('AK', 'SB 2'): 'AK_SB2'}
EXTRA_FILES = {'UT_HB444': ['UT_HB450.txt'], 'NY_S7599': ['NY_S8831.txt']}
GROUPS = [['FED_M-25-21', 'FED_M-25-22', 'NY_S7543', 'NY_S7599', 'MD_SB818', 'CO_SB189'],
          ['OH_SB315', 'TX_HB149', 'TX_SB1964', 'TX_HB2060', 'MT_HB178', 'AR_HB1958'],
          ['CT_SB1103', 'CT_SB5', 'VT_H410', 'CA_AB302', 'CA_SB896', 'KY_SB4', 'IN_SB150', 'UT_HB444'],
          ['NC_H565', 'MI_HB4537', 'PA_HB1925', 'MA_H77', 'NY_A7278', 'CA_SB1248', 'CA_SB430', 'CA_AB2412'],
          ['IL_HB3567', 'IL_SB1366', 'GA_HB147', 'RI_H7119', 'OK_HB3545', 'OR_HB4103', 'NH_SB657', 'NH_HB1506', 'NM_SB68', 'FL_S146', 'MS_HB1640', 'AK_SB2']]


def norm(s):
    s = s.replace('’', "'").replace('‘', "'").replace('–', '-').replace('—', '-').lower()
    return re.sub(r'[^a-z0-9]', '', s)


def load_js(path, var):
    s = open(path, encoding='utf-8').read()
    return json.loads(s[s.index(var + '=') + len(var) + 1:].rstrip().rstrip(';'))


POL = load_js(os.path.join(ROOT, 'data', 'policies.js'), 'window.POL')
QUOTES = load_js(os.path.join(ROOT, 'data', 'quotes.js'), 'window.QUOTES')
by_key = {}
for p in POL:
    k = KEYS.get((p[0], p[1]))
    if k:
        by_key[k] = p

rows = {}
for k, p in by_key.items():
    label = p[0] + '|' + p[1]
    files = [k + '.txt'] + EXTRA_FILES.get(k, [])
    texts = []
    for f in files:
        fp = os.path.join(W, 'texts', f)
        texts.append(open(fp, encoding='utf-8', errors='replace').read() if os.path.exists(fp) else '')
    hay = norm(''.join(texts))
    qs = []
    for i, q in enumerate(QUOTES.get(label, {}).get('q', [])):
        if not q.get('quote'):
            continue
        qs.append({'qid': '%s#%d' % (k, i + 1), 'part': q['part'], 'where': q['where'], 'quote': q['quote'], 'specifics': q['specifics'],
                   'note': q.get('note', ''), 'extractor_verdict': q['supported'], 'exact_match_in_text': norm(q['quote']) in hay})
    rows[k] = {'key': k, 'state': p[0], 'bill': p[1], 'title': p[2], 'year': p[3], 'status': p[4], 'scope': p[5], 'rating_tags': p[6],
               'description': p[7], 'confidence': p[9], 'files': files, 'quotes': qs}

for n, g in enumerate(GROUPS, 1):
    json.dump([rows[k] for k in g if k in rows], open(os.path.join(W, 'audit_in_%d.json' % n), 'w'), indent=1)
bad = [(r['key'], q['qid']) for r in rows.values() for q in r['quotes'] if not q['exact_match_in_text']]
print('entries', len(rows), 'quotes', sum(len(r['quotes']) for r in rows.values()), 'exact-match failures', len(bad), bad[:10])

open(os.path.join(W, 'codebook.md'), 'w').write('''# Codebook (rating rules)
Ratings per framework part: 2 = close match, 1 = loose match, 0 = rolled back (a duty once required and since removed), absent = none found.
I Public inventory. Close: agencies must inventory the AI/ADS they use, with a public posting or report. Loose: inventory is internal or partial, or a registry of another kind.
N Notice and explanation. Close: the person affected must be told an automated tool was used, or get an explanation of an adverse outcome. Loose: only a general duty to disclose AI use or AI interaction, not tied to a decision about the person.
A Impact assessment, testing, monitoring. Close: a required pre-use impact assessment, testing or recurring monitoring of agency systems. Loose: risk-management standards, or an assessment duty that is vague, narrow or known only from a short summary.
H Human review and appeal. Close: a human must review, verify or make the final decision on decisions that affect rights or benefits. Loose: a policy-level requirement, or review limited to certain plans or decision types.
V Vendor and developer duties. Close: developers or vendors must give agencies or deployers documentation, or cooperate with assessments. Loose: the vendor is named in an inventory, or the law only touches procurement.
O Oversight body and enforcement. Close: a designated enforcement authority with penalties, or an independent oversight office. Loose: an advisory council or committee, or reporting to the legislature only.
Scope: ben = text names benefits, Medicaid, SNAP or eligibility; gov = government AI use generally.
''')
