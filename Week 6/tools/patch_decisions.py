"""Records the Vermont quotes dropped in the final audit in data/audit_decisions.json, then rebuild the Excel and data/audit.js.
Usage: python3 -I tools/patch_decisions.py WORK_DIR"""
import glob, json, os, sys

W = sys.argv[1]
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
dp = os.path.join(R, 'data', 'audit_decisions.json')
dec = json.load(open(dp))
for f in sorted(glob.glob(os.path.join(W, 'audit_in_*.json'))):
    for e in json.load(open(f)):
        if e['key'] == 'VT_H410':
            for q in e['quotes']:
                if q['part'] in ('N', 'H') and q['extractor_verdict'] == 'partial':
                    dec['quotes'][q['qid']] = 'DROPPED (final check): shows only a non-binding recommendation to the AI Council, not a duty'
json.dump(dec, open(dp, 'w'), indent=1)
print([k for k, v in dec['quotes'].items() if 'final check' in v])
