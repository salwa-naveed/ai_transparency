"""Final-audit fix: New York LOADinG Act description, now checked against the bill text and the official NY Senate page."""
import os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
p = os.path.join(R, 'tools', 'build_policies.py')
s = open(p, encoding='utf-8').read()
key = " ('MT','HB 178'): 'Signed May 5, 2025."
new = (" ('NY','LOADinG Act (S 7543)'): 'Chapter 696 of 2024, amended by Chapter 96 of 2025. Checked against the S 7543-B text: Article 4 restricts state-agency use of automated decision-making systems (Sec. 402), "
       "requires impact assessments at least once every two years and before material changes (Sec. 403), and requires each assessment to go to the governor and legislative leaders at least thirty days before implementation and to be published on the agency website (Sec. 404). "
       "The NY Senate sponsor memo describes it as barring unauthorized agency use without meaningful human review. The text read here has no discontinuation requirement and no public inventory (disclosures go to the legislature); "
       "the signed 2024 chapter may differ from this print, so check the final text. The 2025 expansion (S 7599) was repealed in 2026.',\n")
if "Checked against the S 7543-B text" not in s:
    i = s.index(key)
    s = s[:i] + new + s[i:]
    open(p, 'w', encoding='utf-8').write(s)
print('ok')
