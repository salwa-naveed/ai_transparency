"""Fetch one bill's latest text with the LegiScan API. Usage: LEGISCAN_ENV=/path/key.txt python3 -I tools/fetch_one.py STATE BILL YEAR OUT.txt"""
import base64, html, io, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if os.environ.get('PYLIB'): sys.path.insert(1, os.environ['PYLIB'])
import legiscan_api as L
st, bill, year, out = sys.argv[1:5]
norm = lambda b: re.sub(r'^([A-Za-z]+)0+(\d)', r'\1\2', re.sub(r'\s', '', b)).upper()
d = L.call('getSearch', state=st, bill=bill, year=int(year))['searchresult']
res = [v for k, v in d.items() if k != 'summary' and norm(v['bill_number']) == norm(bill)]
b = L.call('getBill', id=sorted(res, key=lambda v: v['bill_id'])[-1]['bill_id'])['bill']
print(b['bill_number'], b['title'][:100], '| status', b['status'], b['status_date'])
for h in b.get('history', [])[-6:]:
    print('  ', h['date'], h['action'][:100])
t = sorted(b['texts'], key=lambda t: (t['date'], t['doc_id']))[-1]
x = L.call('getBillText', id=t['doc_id'])['text']
raw = base64.b64decode(x['doc'])
if 'pdf' in x['mime']:
    import pypdf
    txt = '\n'.join((p.extract_text() or '') for p in pypdf.PdfReader(io.BytesIO(raw)).pages)
else:
    s = raw.decode('utf-8', 'replace')
    s = re.sub(r'(?i)<br\s*/?>|</p>|</div>|</li>|</tr>', '\n', s)
    txt = html.unescape(re.sub(r'<[^>]+>', ' ', s))
open(out, 'w').write(txt)
print('version', x['type'], x['date'], len(txt), 'chars')
