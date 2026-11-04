"""Fetches bill records and full text from the LegiScan API for every entry in data/policies.js that is a bill.
Usage: LEGISCAN_ENV=/path/.env python3 -I tools/fetch_texts.py OUT_DIR
Writes OUT_DIR/<STATE>_<BILL>.json (record) and OUT_DIR/<STATE>_<BILL>.txt (plain text of the latest version)."""
import base64, html, io, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import legiscan_api as L
PYLIB = '/private/tmp/claude-501/w/pylib'
if os.path.isdir(PYLIB): sys.path.insert(1, PYLIB)

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
# (state, bill number, search year hint)
T = [('NY','S7543',2023),('NY','S7599',2025),('NY','S8831',2025),('CT','SB1103',2023),('CT','SB5',2026),('MD','SB818',2024),('VT','H410',2022),
     ('CA','AB302',2023),('CA','SB896',2023),('CO','SB189',2026),('TX','HB149',2025),('TX','SB1964',2025),('TX','HB2060',2023),
     ('KY','SB4',2025),('MT','HB178',2025),('AR','HB1958',2025),('IN','SB150',2024),('UT','HB444',2025),('UT','HB450',2026),('UT','HB320',2026),
     ('OH','SB315',2025),('NC','H565',2025),('MI','HB4537',2025),('PA','HB1925',2025),('MA','H77',2025),('NY','A7278',2025),
     ('CA','SB1248',2025),('CA','SB430',2025),('CA','AB2412',2025),('HI','SB59',2025),('IL','HB3567',2025),('IL','SB1366',2025),
     ('GA','HB147',2025),('RI','H7119',2026),('OK','HB3545',2026),('OR','HB4103',2026),('NH','SB657',2026),('NH','HB1506',2026),
     ('NM','SB68',2026),('FL','S146',2026),('MS','HB1640',2026),('AK','SB2',2025)]
norm = lambda b: re.sub(r'^([A-Za-z]+)0+(\d)', r'\1\2', re.sub(r'\s', '', b)).upper()

def to_text(mime, raw):
    if 'pdf' in mime:
        import pypdf
        r = pypdf.PdfReader(io.BytesIO(raw))
        return '\n'.join((p.extract_text() or '') for p in r.pages)
    s = raw.decode('utf-8', errors='replace')
    if 'html' in mime or '<html' in s[:500].lower():
        s = re.sub(r'(?is)<(script|style).*?>.*?</\1>', ' ', s)
        s = re.sub(r'(?i)<br\s*/?>|</p>|</div>|</li>|</tr>', '\n', s)
        s = html.unescape(re.sub(r'<[^>]+>', ' ', s))
    return s

summary = []
for st, bill, yr in T:
    tag = '%s_%s' % (st, bill)
    cand = None
    for year in (yr, 1):
        try:
            d = L.call('getSearch', state=st, bill=bill, year=year)
        except RuntimeError as e:
            continue
        res = [v for k, v in d['searchresult'].items() if k != 'summary' and norm(v['bill_number']) == norm(bill)]
        if res:
            cand = sorted(res, key=lambda v: v['bill_id'])[-1] if year != 1 else min(res, key=lambda v: abs(int(str(v.get('last_action_date', '2000'))[:4]) - yr))
            break
    if not cand:
        summary.append((tag, 'NOT FOUND')); continue
    b = L.call('getBill', id=cand['bill_id'])['bill']
    rec = {k: b.get(k) for k in ('bill_id', 'bill_number', 'title', 'description', 'status', 'status_date', 'url', 'state_link', 'session')}
    rec['history_tail'] = b.get('history', [])[-3:]
    rec['texts'] = [{k: t.get(k) for k in ('doc_id', 'date', 'type', 'mime', 'url', 'state_link')} for t in b.get('texts', [])]
    txt = ''
    if b.get('texts'):
        t = sorted(b['texts'], key=lambda t: (t['date'], t['doc_id']))[-1]
        d = L.call('getBillText', id=t['doc_id'])['text']
        try:
            txt = to_text(d['mime'], base64.b64decode(d['doc']))
        except Exception as e:
            txt = ''; rec['text_error'] = str(e)
        rec['text_used'] = {k: d.get(k) for k in ('doc_id', 'date', 'type', 'mime')}
    open(os.path.join(OUT, tag + '.json'), 'w').write(json.dumps(rec, indent=1))
    open(os.path.join(OUT, tag + '.txt'), 'w').write(txt)
    summary.append((tag, 'status %s %s | %s | text %d chars | %s' % (rec['status'], rec['status_date'], rec['session'].get('session_name') if rec['session'] else '', len(txt), (rec.get('text_used') or {}).get('type'))))
for s in summary: print(*s)
print('API calls:', L.calls())
