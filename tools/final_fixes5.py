"""Adds the effective-date clause of S 7543-B (verified in both the LegiScan copy and the author's PDF) to the New York LOADinG entry."""
import json, os, re, sys
W = sys.argv[1]
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
quote = 'of this act shall take effect one year after it shall have become a law.'
for f in ('texts/NY_S7543.txt', 'user/S7543B.txt'):
    p = os.path.join(W, f)
    if os.path.exists(p):
        assert norm(quote) in norm(open(p, errors='replace').read()), f
qp = os.path.join(R, 'data', 'quotes.js')
q = open(qp, encoding='utf-8').read()
head = q[:q.index('window.QUOTES=')]
Q = json.loads(q[q.index('window.QUOTES=') + 14:].rstrip().rstrip(';'))
e = Q['NY|LOADinG Act (S 7543)']
if not any(x['quote'] == quote for x in e['q']):
    e['q'].append({'part': 'SCOPE', 'supported': 'yes', 'quote': quote, 'where': '§ 4 (effective date)',
                   'specifics': 'As passed, the new Article 4 (Sections 401 to 404) was to take effect one year after the act became law. Chapter 96 of 2025 moved that date to July 1, 2025 and repealed Sections 403 and 404 first.',
                   'note': 'Section 2 of the act is the one that adds Article 4.', 'caveat': 'Checked against the LegiScan text and a second copy of S 7543-B supplied by the author.'})
open(qp, 'w', encoding='utf-8').write(head + 'window.QUOTES=' + json.dumps(Q, ensure_ascii=False, separators=(',', ':')) + ';\n')
print('ok')
