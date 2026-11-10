"""One-time fixes from the final audit (Nov. 2026). Usage: python3 -I tools/final_fixes.py WORK_DIR"""
import json, os, sys

W = sys.argv[1]
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

# 1. description corrections (dates and claims that the bill text or LegiScan history did not support)
p = os.path.join(R, 'tools', 'build_policies.py')
s = open(p, encoding='utf-8').read()
marker = "SCOPE = {"
add = '''DESC.update({  # final audit (Nov. 2026): dates checked against LegiScan bill history, claims against bill text
 ('MT','HB 178'): 'Signed May 5, 2025. Government must disclose AI-generated material that was not reviewed by a human, and public-facing AI interfaces. A human with authority to reject or change it must review any AI recommendation or decision that could affect a person\\'s legal rights, duties or privileges. Benefits not named.',
 ('AR','HB 1958 (Act 848)'): 'Act 848 of 2025. Every public entity adopts a policy on authorized AI and automated decision tools; a human must make final decisions. No penalties or central oversight.',
 ('NH','SB 657'): 'Passed the Senate and was amended in the House; on May 21, 2026 the Senate moved not to concur with the House amendment. No further action found; the session has ended.',
 ('NY','S 7599 / A 8295'): 'Signed Dec. 19, 2025 (Chapter 711): agency tool lists, impact assessments every two years, inventory on the open data site. S 8831 (Chapter 86, signed Feb. 13, 2026) repealed that article before it took effect and keeps only employment-tool lists. The repeal language was read from the introduced print of S 8831, so check the signed version.',
})
'''
if "('MT','HB 178'): 'Signed May 5, 2025." not in s:
    i = s.index(marker)
    s = s[:i] + add + s[i:]
    open(p, 'w', encoding='utf-8').write(s)

# 2. quotes: drop the two Vermont quotes for parts that are non-binding recommendations; add TRAIGA text link
qp = os.path.join(R, 'data', 'quotes.js')
q = open(qp, encoding='utf-8').read()
head = q[:q.index('window.QUOTES=')]
Q = json.loads(q[q.index('window.QUOTES=') + 14:].rstrip().rstrip(';'))
vt = Q['VT|H 410 (Act 132)']
vt['q'] = [x for x in vt['q'] if not (x['part'] in ('N', 'H') and x.get('supported') == 'partial')]
rec = json.load(open(os.path.join(W, 'texts', 'TX_HB149.json')))
t = sorted(rec['texts'], key=lambda t: (t['date'], t['doc_id']))[-1]
Q['TX|HB 149 (TRAIGA)']['meta'] = {'version': t.get('type', ''), 'date': t.get('date', '') if str(t.get('date', ''))[:4] > '1999' else '', 'textUrl': t.get('url', ''),
                                   'stateUrl': t.get('state_link', ''), 'legiscan': rec.get('url', ''), 'status': rec['status'], 'statusDate': rec['status_date']}
open(qp, 'w', encoding='utf-8').write(head + 'window.QUOTES=' + json.dumps(Q, ensure_ascii=False, separators=(',', ':')) + ';\n')

# 3. page wording
hp = os.path.join(R, 'index.html')
h = open(hp, encoding='utf-8').read()
h = h.replace('Texas, New York and California from your whiteboard, plus Colorado', 'Texas, New York and California (the original comparison set), plus Colorado')
h = h.replace('with a column for your own check.', 'with a column for a reviewer\'s own check.')
h = h.replace('They found 10 serious problems among 261 quotes (five wrong section labels and six quotes that did not support the part they were cited for), disagreed with about 40 ratings, and found seven description claims the text contradicts.',
              'They found 10 serious problems among 261 quotes (five wrong section labels and six quotes that did not support the part they were cited for; one quote had both problems), disagreed with 40 ratings, and found seven description claims the text contradicts.')
h = h.replace('The Chief AI Officer', 'The Chief AI Officer')
open(hp, 'w', encoding='utf-8').write(h)
print('done')
