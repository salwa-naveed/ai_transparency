"""Removes the Audit section from the site (index.html, app.js) at the author's request. The audit spreadsheet stays in audit/ but is no longer linked."""
import os, re
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')

hp = os.path.join(R, 'index.html')
h = open(hp, encoding='utf-8').read()
a = h.index('  <section id="audit">')
b = h.index('  <section id="about">')
h = h[:a] + h[b:]
h = h.replace('\n    <a href="#audit">Audit</a>', '')
h = h.replace('\n<script src="data/audit.js?v=20261114"></script>', '')
h = re.sub(r'\n<script src="data/audit\.js[^"]*"></script>', '', h)
# About: keep a short, neutral note about caveats; drop numbers and links to the removed section
i = h.index('      <li><b>Independent audit (Nov. 2026):</b>')
j = h.index('</li>', i) + 5
h = h[:i] + '''      <li><b>Independent check:</b> every quote was confirmed by script to be an exact match in the stored text, and independent reviewers re-read the surrounding text and re-checked each rating and description. Quotes that carry a yellow "Caveat" line are real passages with a limit worth knowing (for example "may" instead of "shall", an exemption, a delayed date, or a definition rather than a duty).</li>''' + h[j:]
open(hp, 'w', encoding='utf-8').write(h)

ap = os.path.join(R, 'app.js')
s = open(ap, encoding='utf-8').read()
a = s.index('/* ---------- audit ---------- */')
b = s.index('/* ---------- nav ---------- */')
s = s[:a] + s[b:]
s = s.replace("const secs=['overview','map','chart','laws','audit','about']", "const secs=['overview','map','chart','laws','about']")
open(ap, 'w', encoding='utf-8').write(s)

dp = os.path.join(R, 'data', 'audit.js')
if os.path.exists(dp):
    os.remove(dp)
print('audit' in h.lower(), 'sections left:', re.findall(r'<section id="(\w+)"', h))
