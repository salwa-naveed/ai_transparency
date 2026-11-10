"""Applies the independent audit to the site data.
Usage: python3 -I tools/audit_apply.py WORK_DIR
Reads WORK_DIR/audit_in_*.json and audit_out_*.json; edits data/quotes.js and tools/reviewed_tags.json; writes data/audit_decisions.json
(used by tools/audit_excel.py for the 'Action taken' columns). Run tools/build_policies.py afterwards.

Rules
- Quote whose section label the auditor corrected: label replaced.
- Quote the auditor says does NOT support its claimed part: dropped.
- Rating where the auditor found no matching duty: tag removed (and that part's quotes dropped).
- Rating the auditor wants lower: lowered. Rating the auditor wants higher: raised, unless the auditor called it borderline or scope-dependent.
- Rating on an entry shown as repealed: left as is (the chart already shows it as rolled back).
- Context flags (struck text, 'may', exemptions, sunsets, truncation, definitions) become a visible caveat on the quote."""
import glob, json, os, re, sys

W = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')
BORDER = {('TX_SB1964', 'V'), ('FED_M-25-22', 'V'), ('MA_H77', 'N'), ('MA_H77', 'V'), ('NC_H565', 'O')}
FLAG_TEXT = {'STRUCT_TEXT': 'the text mixes struck-through and new words', 'PERMISSIVE_MAY': 'permissive ("may"), not mandatory',
             'CONDITIONAL_OR_EXEMPTION': 'limited by conditions or exceptions', 'SUNSET_OR_DELAYED': 'delayed or expires',
             'TRUNCATED_MISLEADING': 'the quote cuts off part of the sentence', 'DEFINITION_ONLY': 'a definition, not itself a duty',
             'PREAMBLE_OR_FINDINGS': 'findings or preamble, not operative law'}


def load_js(path, var):
    s = open(path, encoding='utf-8').read()
    return s[:s.index(var + '=')], json.loads(s[s.index(var + '=') + len(var) + 1:].rstrip().rstrip(';'))


head, QUOTES = load_js(os.path.join(DATA, 'quotes.js'), 'window.QUOTES')
ins, qa, ra = {}, {}, []
for f in sorted(glob.glob(os.path.join(W, 'audit_in_*.json'))):
    for e in json.load(open(f)):
        ins[e['key']] = e
for f in sorted(glob.glob(os.path.join(W, 'audit_out_*.json'))):
    d = json.load(open(f))
    for r in d['quote_audit']:
        qa[r['qid']] = r
    ra += d['rating_audit']

tags_path = os.path.join(HERE, 'reviewed_tags.json')
tags = json.load(open(tags_path))
cur = {k: {t[0]: t[1] for t in v.split()} for k, v in tags.items()}
dec_rating = {}
for r in ra:
    k, p = r['key'], r['part']
    c = str(r['claimed']); a = str(r['audited'])
    e = ins.get(k, {})
    why = ''
    if e.get('status') == 'R' and a != 'none':
        act = 'Left as is: entry is shown as repealed before taking effect'
    elif c == '0':
        act = 'Left as is: rolled-back rating kept'
    elif c == a:
        act = 'No change: auditor agrees'
    elif a == '0':
        act = 'Left as is: auditor says rolled back; the site already marks this part with a 0'
    elif a == 'none':
        cur[k].pop(p, None); act = 'APPLIED: rating removed (auditor found no matching duty)'
    elif c == 'none' and a in '12':
        if (k, p) in BORDER:
            act = 'NOT applied: auditor called this borderline'
        else:
            cur[k][p] = a; act = 'APPLIED: rating added at %s' % a
    elif int(a) < int(c):
        cur[k][p] = a; act = 'APPLIED: rating lowered from %s to %s' % (c, a)
    else:
        if (k, p) in BORDER:
            act = 'NOT applied: auditor called this borderline or scope-dependent'
        else:
            cur[k][p] = a; act = 'APPLIED: rating raised from %s to %s' % (c, a)
    dec_rating['%s|%s' % (k, p)] = act

removed_parts = {(r['key'], r['part']) for r in ra if str(r['audited']) == 'none' and str(r['claimed']) not in ('none', '0') }
new_tags = {k: ' '.join(p + v for p, v in sorted(d.items(), key='INAHVO'.index if False else (lambda kv: 'INAHVO'.index(kv[0])))) for k, d in cur.items()}
json.dump(new_tags, open(tags_path, 'w'), indent=1)

dec_quote = {}
KEYLABEL = {}
for k, e in ins.items():
    KEYLABEL[k] = e['state'] + '|' + e['bill']
for k, e in ins.items():
    lab = KEYLABEL[k]
    items = QUOTES.get(lab, {}).get('q', [])
    out = []
    for i, q in enumerate(items):
        qid = '%s#%d' % (k, i + 1)
        if not q.get('quote'):
            out.append(q); continue
        a = qa.get(qid)
        if not a:
            out.append(q); continue
        act = 'Kept'
        if a['supports_claim'] == 'No':
            dec_quote[qid] = 'DROPPED: auditor says the quote does not support its claimed part'; continue
        if (k, q['part']) in removed_parts:
            dec_quote[qid] = 'DROPPED: rating for this part was removed'; continue
        if a['where_correct'] == 'no' and a.get('correct_label'):
            lab_new = re.sub(r'\s*\(.*$', '', a['correct_label']) if len(a['correct_label']) > 60 else a['correct_label']
            q['where'] = lab_new; act = 'Kept; section label corrected to "%s"' % lab_new
        flags = [FLAG_TEXT[f] for f in a.get('context_flags', []) if f in FLAG_TEXT]
        cav = '; '.join(flags)
        if a['severity'] != 'OK' and a.get('comment'):
            cav = (cav + '. ' if cav else '') + a['comment']
        q['caveat'] = cav[:420]
        dec_quote[qid] = act
        out.append(q)
    QUOTES[lab]['q'] = out

json.dump({'quotes': dec_quote, 'ratings': dec_rating}, open(os.path.join(DATA, 'audit_decisions.json'), 'w'), indent=1)
with open(os.path.join(DATA, 'quotes.js'), 'w', encoding='utf-8') as fh:
    fh.write(head + 'window.QUOTES=' + json.dumps(QUOTES, ensure_ascii=False, separators=(',', ':')) + ';\n')
import collections
print('quotes', collections.Counter(v.split(':')[0].split(';')[0] for v in dec_quote.values()))
print('ratings', collections.Counter(v.split(':')[0] for v in dec_rating.values()))
for kk, v in dec_rating.items():
    if v.startswith('APPLIED') or v.startswith('NOT'): print(kk, v)
