"""Tidies two caveat strings on the New York LOADinG quotes."""
import os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
p = os.path.join(R, 'data', 'quotes.js')
s = open(p, encoding='utf-8').read()
s = s.replace('(see Chapter 96 of 2025). a definition, not itself a duty', '(see Chapter 96 of 2025). This is a definition, not itself a duty.')
s = s.replace('Checked against the LegiScan text and a second copy of S 7543-B supplied by the author.', 'Matches a second copy of the S 7543-B text.')
open(p, 'w', encoding='utf-8').write(s)
print(s.count('a definition, not itself a duty') , s.count('supplied by the author'))
