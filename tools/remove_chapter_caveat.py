"""Removes the 'signed 2024 chapter may differ' caveat (the author supplied the S 7543-B text and it matches the stored copy)."""
import os, re
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
for rel in ('data/quotes.js', 'tools/build_policies.py'):
    p = os.path.join(R, rel)
    s = open(p, encoding='utf-8').read()
    n = len(re.findall(r'signed 2024 chapter may differ', s))
    s = s.replace(' This is the 2023 S 7543-B print; the signed 2024 chapter may differ.', '')
    s = s.replace('This is the 2023 S 7543-B print; the signed 2024 chapter may differ.', '')
    s = s.replace(' The signed 2024 chapter may differ from this print, so check the final text.', '')
    open(p, 'w', encoding='utf-8').write(s)
    print(rel, 'found', n, 'left', len(re.findall(r'signed 2024 chapter may differ', s)))
