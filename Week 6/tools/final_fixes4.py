"""Final-audit cleanup: the NY Sec. 403(2) quote already existed (so nothing was added); only the description was wrong. Fix the Method note and add the print-version caveat."""
import json, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ap = os.path.join(R, 'tools', 'audit_excel.py')
a = open(ap, encoding='utf-8').read()
old = "    'Added after the audit: one quote (New York LOADinG Act, Sec. 403(2), discontinuation of discriminatory systems) was added during the final check; it was verified by script only. Descriptions of Montana HB 178, Arkansas HB 1958, New Hampshire SB 657 and New York S 7599 were also corrected in the final check, and two Vermont quotes for non-binding items were dropped.',\n"
new = "    'Final check (after the audit): descriptions of Montana HB 178, Arkansas HB 1958, New Hampshire SB 657, New York S 7599 and the New York LOADinG Act were corrected against LegiScan bill histories and the bill text; two Vermont quotes that showed only non-binding recommendations were dropped.',\n"
if old in a:
    a = a.replace(old, new)
    open(ap, 'w', encoding='utf-8').write(a)
qp = os.path.join(R, 'data', 'quotes.js')
q = open(qp, encoding='utf-8').read()
head = q[:q.index('window.QUOTES=')]
Q = json.loads(q[q.index('window.QUOTES=') + 14:].rstrip().rstrip(';'))
for x in Q['NY|LOADinG Act (S 7543)']['q']:
    if x['where'] == 'Section 403(2)' and not x['caveat']:
        x['caveat'] = 'This is the 2023 S 7543-B print; the signed 2024 chapter may differ.'
open(qp, 'w', encoding='utf-8').write(head + 'window.QUOTES=' + json.dumps(Q, ensure_ascii=False, separators=(',', ':')) + ';\n')
print('ok')
