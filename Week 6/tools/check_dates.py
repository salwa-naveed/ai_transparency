"""Prints the LegiScan history lines (signing, effective dates) for entries whose descriptions state dates.
Usage: LEGISCAN_ENV=/path/key.txt python3 -I tools/check_dates.py WORK_DIR"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import legiscan_api as L

W = sys.argv[1]
for key in ['OH_SB315', 'MT_HB178', 'AR_HB1958', 'TX_HB149', 'CO_SB189', 'CT_SB5', 'KY_SB4', 'NY_S7599', 'NY_S8831', 'MD_SB818', 'VT_H410', 'IN_SB150', 'TX_SB1964']:
    rec = json.load(open(os.path.join(W, 'texts', key + '.json')))
    b = L.call('getBill', id=rec['bill_id'])['bill']
    hist = b.get('history', [])
    keep = [h for h in hist if any(w in h['action'].lower() for w in ('sign', 'effective', 'approved', 'chapter', 'governor', 'act no', 'public act'))]
    print('==', key, rec['status'], rec['status_date'])
    for h in keep[-5:]:
        print('  ', h['date'], h['action'][:110])
print('API calls', L.calls())
