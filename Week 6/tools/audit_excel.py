"""Builds the audit workbook from audit inputs and auditor outputs.
Usage: python3 -I tools/audit_excel.py WORK_DIR OUT.xlsx
WORK_DIR holds audit_in_<n>.json and audit_out_<n>.json (n = 1..5), codebook.md, texts/.
Sheets: Summary, Quote audit (one row per quote), Rating audit (one row per entry and framework part),
Claim checks (facts in each entry description), Codebook, Method."""
import glob, json, os, re, sys
if os.environ.get('PYLIB'): sys.path.insert(0, os.environ['PYLIB'])
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

W, OUT = sys.argv[1], sys.argv[2]
PART = {'I': 'Public inventory', 'N': 'Notice & explanation', 'A': 'Impact assessment, testing & monitoring', 'H': 'Human review & appeal',
        'V': 'Vendor & developer duties', 'O': 'Oversight body & enforcement', 'SCOPE': 'Scope', 'REPEAL': 'Repeal'}
RATING = {'2': 'Close match', '1': 'Loose match', '0': 'Rolled back', 'none': 'None found'}

entries = {}
for f in sorted(glob.glob(os.path.join(W, 'audit_in_*.json'))):
    for e in json.load(open(f)):
        entries[e['key']] = e
quotes = {q['qid']: (e, q) for e in entries.values() for q in e['quotes']}
qa, ra, cc = {}, [], []
for f in sorted(glob.glob(os.path.join(W, 'audit_out_*.json'))):
    d = json.load(open(f))
    for r in d.get('quote_audit', []):
        qa[r['qid']] = r
    ra += d.get('rating_audit', [])
    cc += d.get('claim_checks', [])

HERE = os.path.dirname(os.path.abspath(__file__))
DEC = json.load(open(os.path.join(HERE, '..', 'data', 'audit_decisions.json')))
NOW = {k: {t[0]: t[1] for t in v.split()} for k, v in json.load(open(os.path.join(HERE, 'reviewed_tags.json'))).items()}
hdr_fill = PatternFill('solid', fgColor='1F3A5F')
hdr_font = Font(bold=True, color='FFFFFF')
RED = PatternFill('solid', fgColor='F8CBAD')
YEL = PatternFill('solid', fgColor='FFF2CC')
GRN = PatternFill('solid', fgColor='E2EFDA')
wrap = Alignment(wrap_text=True, vertical='top')


def sheet(wb, title, header, rows, widths, freeze='A2'):
    ws = wb.create_sheet(title)
    ws.append(header)
    for c in ws[1]:
        c.fill, c.font, c.alignment = hdr_fill, hdr_font, Alignment(wrap_text=True, vertical='center')
    for r in rows:
        ws.append(r)
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = wrap
    ws.freeze_panes = freeze
    ws.auto_filter.ref = ws.dimensions
    return ws


wb = Workbook()
wb.remove(wb.active)

# ---- quote audit
qrows = []
for qid, (e, q) in quotes.items():
    a = qa.get(qid, {})
    flags = ', '.join(a.get('context_flags', []))
    sev = a.get('severity', 'NOT AUDITED')
    qrows.append([qid, e['state'], e['bill'], e['year'], e['status'], PART.get(q['part'], q['part']), q['where'], q['quote'],
                  'Yes' if q['exact_match_in_text'] else 'NO', a.get('located', ''), a.get('where_correct', ''), a.get('correct_label', ''),
                  flags, a.get('supports_claim', ''), sev, a.get('comment', ''), q['specifics'], DEC['quotes'].get(qid, ''), '', ''])
ws = sheet(wb, 'Quote audit', ['Quote ID', 'State', 'Bill', 'Year', 'Outcome', 'Framework part', 'Claimed section', 'Quote (copied from text)',
                               'Script: exact match in stored text', 'Auditor: found in text', 'Auditor: section label correct', 'Corrected label',
                               'Context flags', 'Auditor: supports claim', 'Severity', 'Auditor comment', 'Claimed plain-English meaning',
                               'Action taken on the site', 'YOUR check (Y / N / ?)', 'Your notes'],
           qrows, [11, 7, 20, 7, 9, 22, 18, 70, 12, 11, 12, 16, 22, 12, 11, 45, 45, 38, 14, 30])
dv = DataValidation(type='list', formula1='"Y,N,?"', allow_blank=True)
ws.add_data_validation(dv)
dv.add('S2:S%d' % (len(qrows) + 1))
for row in ws.iter_rows(min_row=2):
    sev = row[14].value
    row[14].fill = {'MAJOR': RED, 'MINOR': YEL, 'OK': GRN}.get(sev, YEL)
    if row[8].value == 'NO':
        row[8].fill = RED

# ---- rating audit
claimed = {}
for e in entries.values():
    for t in (e['rating_tags'] or '').split():
        claimed[(e['key'], t[0])] = t[1]
seen = set()
rrows = []
for r in ra:
    k = (r['key'], r['part'])
    seen.add(k)
    e = entries.get(r['key'], {})
    rrows.append([r['key'], e.get('state', ''), e.get('bill', ''), e.get('status', ''), PART.get(r['part'], r['part']),
                  RATING.get(str(claimed.get(k, 'none')), '?'), RATING.get(str(r.get('audited')), '?'), r.get('agree', ''), r.get('reason', ''), DEC['ratings'].get('%s|%s' % (r['key'], r['part']), ''), RATING.get(str(NOW.get(r['key'], {}).get(r['part'], 'none')), '?'), '', ''])
for (key, p), v in claimed.items():
    if (key, p) not in seen:
        e = entries[key]
        rrows.append([key, e['state'], e['bill'], e['status'], PART.get(p, p), RATING.get(v, '?'), 'NOT AUDITED', '', '', '', RATING.get(str(NOW.get(key, {}).get(p, 'none')), '?'), '', ''])
ws = sheet(wb, 'Rating audit', ['Entry key', 'State', 'Bill', 'Outcome', 'Framework part', 'Rating on the site', 'Auditor\'s rating', 'Agree?',
                                 'Auditor reason', 'Action taken on the site', 'Rating on the site now', 'YOUR check (Y / N / ?)', 'Your notes'],
           rrows, [14, 7, 22, 9, 28, 14, 14, 9, 70, 40, 14, 14, 30])
dv2 = DataValidation(type='list', formula1='"Y,N,?"', allow_blank=True)
ws.add_data_validation(dv2)
dv2.add('K2:K%d' % (len(rrows) + 1))
for row in ws.iter_rows(min_row=2):
    row[7].fill = {'yes': GRN, 'no': RED}.get(row[7].value, YEL)

# ---- claim checks
crows = [[c['key'], entries.get(c['key'], {}).get('state', ''), entries.get(c['key'], {}).get('bill', ''), c.get('claim', ''), c.get('verified', ''), c.get('evidence', ''), ('Description corrected on the site' if c.get('verified') == 'no' else ('Left as is: comes from outside the bill text (status, signing date or the policy paper)' if c.get('verified') == 'unverifiable' else '')), '']
         for c in cc]
ws = sheet(wb, 'Claim checks', ['Entry key', 'State', 'Bill', 'Claim in description', 'Verified in bill text?', 'Evidence', 'Action taken on the site', 'Your notes'], crows, [14, 7, 22, 70, 14, 70, 40, 30])
for row in ws.iter_rows(min_row=2):
    row[4].fill = {'yes': GRN, 'no': RED}.get(row[4].value, YEL)

# ---- codebook, method
ws = wb.create_sheet('Codebook')
for line in open(os.path.join(W, 'codebook.md')).read().splitlines():
    ws.append([line])
ws.column_dimensions['A'].width = 160
for row in ws.iter_rows():
    row[0].alignment = wrap
ws = wb.create_sheet('Method')
for line in [
    'How this audit was done',
    '1. Quotes were first extracted from the full text of each bill or memo (LegiScan API text; OMB memos from whitehouse.gov) by one set of reviewers.',
    '2. A script then checked every quote is an exact substring of the stored text (letters and digits only, case-insensitive). Column "Script: exact match" shows the result.',
    '3. A second, independent set of AI reviewers re-read the text around each quote and judged: whether they found it, whether the section label is right, context flags (struck-through text, preamble, "may" vs "shall", exemptions, sunsets), and whether it supports the claimed part.',
    '4. The same reviewers re-rated every framework part against the codebook using the whole bill text, and checked the facts in each entry description.',
    'Limits: all judgments except the script check are made by AI reviewers. Text extracted from PDFs can contain line numbers, odd spacing and struck-through words. Close vs. loose is a judgment under the codebook, not an objective fact.',
    'The columns "YOUR check" are for a human spot-check: open the full text, press Ctrl+F, paste the first words of the quote, and mark Y, N or ?.',
]:
    ws.append([line])
ws.column_dimensions['A'].width = 160
for row in ws.iter_rows():
    row[0].alignment = wrap
ws['A1'].font = Font(bold=True, size=14)

# ---- summary (first)
ws = wb.create_sheet('Summary', 0)
n_q = len(quotes)
audited = [qid for qid in quotes if qid in qa]
sev = {s: sum(1 for qid in audited if qa[qid].get('severity') == s) for s in ('OK', 'MINOR', 'MAJOR')}
exact = sum(1 for _, q in quotes.values() if q['exact_match_in_text'])
rd = [r for r in ra]
dis = sum(1 for r in rd if r.get('agree') == 'no')
cnone = sum(1 for c in cc if c.get('verified') == 'no')
cun = sum(1 for c in cc if c.get('verified') == 'unverifiable')
rows = [
    ['Quote and rating audit: summary', ''],
    ['Entries audited', len(entries)],
    ['Quotes', n_q],
    ['Quotes that are exact matches in the stored text (script)', '%d of %d' % (exact, n_q)],
    ['Quotes reviewed by an independent auditor', '%d of %d' % (len(audited), n_q)],
    ['Auditor severity: OK', sev['OK']],
    ['Auditor severity: MINOR', sev['MINOR']],
    ['Auditor severity: MAJOR', sev['MAJOR']],
    ['Quotes where the auditor says the section label is wrong', sum(1 for qid in audited if qa[qid].get('where_correct') == 'no')],
    ['Quotes where the auditor says the quote does not support the claim', sum(1 for qid in audited if qa[qid].get('supports_claim') == 'No')],
    ['Ratings reviewed', len(rd)],
    ['Ratings where the auditor disagrees with the site', dis],
    ['Description claims checked', len(cc)],
    ['Description claims contradicted by the text', cnone],
    ['Description claims not verifiable in the bill text', cun],
]
for r in rows:
    ws.append(r)
ws.column_dimensions['A'].width = 80
ws.column_dimensions['B'].width = 18
ws['A1'].font = Font(bold=True, size=14)
wb.save(OUT)
print('saved', OUT, '| quotes', n_q, 'audited', len(audited), sev, 'rating disagreements', dis, 'claims no/unverifiable', cnone, cun)
