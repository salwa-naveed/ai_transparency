"""Final-audit fix: the New York LOADinG text DOES require discontinuation of discriminatory systems (Sec. 403(2)); add the quote and correct the description."""
import json, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
qp = os.path.join(R, 'data', 'quotes.js')
q = open(qp, encoding='utf-8').read()
head = q[:q.index('window.QUOTES=')]
Q = json.loads(q[q.index('window.QUOTES=') + 14:].rstrip().rstrip(';'))
e = Q['NY|LOADinG Act (S 7543)']
new = {'part': 'A', 'supported': 'yes', 'quote': 'produces discriminatory or biased outcomes, the state agency shall cease',
       'where': '§ 403(2)', 'specifics': 'If an impact assessment finds the system produces discriminatory or biased outcomes, the agency must stop using the system and any information it produced.',
       'note': 'Added after the independent audit, from the same stored text.', 'caveat': 'This is the 2023 S 7543-B print; the signed 2024 chapter may differ.'}
if not any(x['quote'] == new['quote'] for x in e['q']):
    e['q'].append(new)
open(qp, 'w', encoding='utf-8').write(head + 'window.QUOTES=' + json.dumps(Q, ensure_ascii=False, separators=(',', ':')) + ';\n')
p = os.path.join(R, 'tools', 'build_policies.py')
s = open(p, encoding='utf-8').read()
old = "The text read here has no discontinuation requirement and no public inventory (disclosures go to the legislature); the signed 2024 chapter may differ from this print, so check the final text."
rep = "It also requires an agency to cease using a system whose assessment finds discriminatory or biased outcomes (Sec. 403(2)). It has no public inventory (disclosures go to the legislature). The signed 2024 chapter may differ from this print, so check the final text."
assert old in s
s = s.replace(old, rep)
open(p, 'w', encoding='utf-8').write(s)
ap = os.path.join(R, 'tools', 'audit_excel.py')
a = open(ap, encoding='utf-8').read()
line = "    'The columns \"YOUR check\" are for a human spot-check"
if 'Added after the audit' not in a:
    a = a.replace(line, "    'Added after the audit: one quote (New York LOADinG Act, Sec. 403(2), discontinuation of discriminatory systems) was added during the final check; it was verified by script only. Descriptions of Montana HB 178, Arkansas HB 1958, New Hampshire SB 657 and New York S 7599 were also corrected in the final check, and two Vermont quotes for non-binding items were dropped.',\n" + line)
    open(ap, 'w', encoding='utf-8').write(a)
print('ok')
