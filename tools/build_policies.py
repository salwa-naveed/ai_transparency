"""Builds data/policies.js: state and federal policies on GOVERNMENT use of AI / automated decision systems (ADS),
focused on public benefits (Medicaid, SNAP, unemployment, eligibility), mapped to the policy framework in the fellowship paper.

Usage: python3 -I tools/build_policies.py ["/path/to/LegiScan AI Data"]
If the LegiScan folder is given, 2026 statuses and URLs are looked up there (bill number must match).

Framework tags: I inventory · N notice & explanation · A impact assessment/testing/monitoring ·
                H human review & appeal · V vendor/procurement duties · O oversight body / enforcement
                2 = close analogue, 1 = loose analogue, 0 = explicitly absent or rolled back.
Status: E enacted · R repealed or rolled back before taking effect · A alive (legislature still in session) ·
        F failed / died / stalled when the session ended · V vetoed
Scope:  ben = explicitly covers benefits, Medicaid, SNAP or eligibility decisions; gov = government/state-agency AI use generally
Conf:   H = official page or 2+ independent sources; M = one secondary source or sources partly conflict; L = thin
"""
import csv, glob, json, os, re, sys
csv.field_size_limit(10**8)

LS = 'https://legiscan.com/'
# (state, bill, short title, year, status, scope, tags, what it does, source URL or None, confidence)
P = [
# ---- federal
('FED','OMB M-25-21','Federal agency AI use: inventories and high-impact AI practices',2025,'E','ben','I2 A2 H2',
 'Annual public AI use-case inventories; for high-impact AI: pre-deployment testing, impact assessment, ongoing monitoring, human oversight and appeals; waivers reported publicly. Agencies had until Apr. 3, 2026. The policy paper says high-impact uses include adjudicating benefits and fraud detection; that wording was not confirmed in the memo itself.',
 'https://regulations.ai/regulations/RAI-US-NA-OMMAFXX-2025','M'),
('FED','OMB M-25-22','Federal agency AI acquisition (vendor requirements)',2025,'E','gov','V1',
 'Governs how federal agencies buy AI from vendors, for contracts awarded or renewed from about Oct. 2025. Known only from law-firm summaries; the memo itself and its vendor-documentation terms were not retrieved.',
 None,'L'),
# ---- enacted: government use of AI/ADS
('NY','LOADinG Act (S 7543)','State agency use of automated decision-making tools',2024,'E','ben','I2 A2 H2 O1',
 'Chapter 696 of 2024, amended by Chapter 96 of 2025. State agencies disclose the automated tools they use; the policy paper cites it for public impact assessments every two years, 30-day advance transmission to the governor and legislators, and mandatory discontinuation of discriminatory systems. A researcher found human review of rights-and-benefits decisions in it. NOT re-verified against the statute text: check Article 4 of the State Technology Law, because the 2025 expansion (S 7599) was repealed in 2026.',
 'https://www.nysenate.gov/legislation/bills/2023/S7543','M'),
('NY','S 7599 / A 8295','2025 expansion: agency impact assessments and inventory',2025,'R','gov','I2 A2',
 'Signed Dec. 19, 2025 (Chapter 711): agency tool lists, impact assessments every two years, inventory on the open data site. Repealed before taking effect by S 8831 (Chapter 86 of 2026), which keeps only employment-tool lists.',
 'https://www.nysenate.gov/legislation/bills/2025/S7599','H'),
('CT','PA 23-16 (SB 1103)','State agency AI inventory and impact assessments',2023,'E','gov','I2 A2 O1',
 'The Department of Administrative Services inventories state-agency AI systems and posts them on the open data portal; impact assessments are required before deployment. Benefits are not named.',
 'https://portal.ct.gov/das','M'),
('CT','PA 26-15 (SB 5)','Omnibus AI and online safety act (state-agency sections)',2026,'E','gov','I1 A1 V1',
 'Signed May 27, 2026. A secondary source says state agencies must complete impact assessments before procurement and the state inventory must record vendor and assessment status. Details not confirmed against the text.',
 LS+'CT/bill/SB00005/2026','L'),
('MD','SB 818 (AI Governance Act)','State government AI inventory and impact assessments',2024,'E','ben','I2 A2 V1 O2',
 'Chapter 496 of 2024. The Department of Information Technology keeps a public inventory (vendor, purpose, assessment status) and requires impact assessments for high-risk AI; its definition of rights-impacting AI includes government benefits. A Governor\'s AI Subcabinet oversees it. No notice or human-review duty found.',
 'https://mgaleg.maryland.gov/2024RS/chapters_noln/Ch_496_sb0818E.pdf','H'),
('VT','H 410 (Act 132)','Division of AI, state inventory and AI Council',2022,'E','gov','I2 A1 O2',
 'Created a Division of AI in the Agency of Digital Services, required an inventory of automated decision systems that "make or support government decisions", and an AI Council. Notice, human review and vendor duties not found.',
 'https://legislature.vermont.gov/bill/status/2022/H.410','M'),
('CA','AB 302','Inventory of high-risk automated decision systems',2023,'E','gov','I2 O1',
 'The Department of Technology inventories high-risk ADS used by state agencies and reports to the legislature. Whether the statute names benefits was not re-checked.',
 LS+'CA/bill/AB302/2023','M'),
('CA','SB 896','Generative AI Accountability Act',2024,'E','gov','I1 N2 A1',
 'State agencies must disclose generative AI use in public communications; risk analysis and an inventory of generative AI uses.',
 LS+'CA/bill/SB896/2023','M'),
('CO','SB 26-189','Automated decision-making technology (replaces the 2024 AI Act)',2026,'E','ben','N2 H2 V2 O2 A0',
 'Signed May 14, 2026, effective Jan. 1, 2027. Names "essential government services and public benefits" as a covered area. Notice when used, explanation of adverse outcomes within 30 days, meaningful human review and data correction, developer documentation to deployers, attorney-general enforcement with a 60-day cure. It removed the earlier impact-assessment and risk-management duties. Whether state and local agencies count as regulated deployers is unresolved.',
 'https://leg.colorado.gov/bills/SB26-189','H'),
('TX','HB 149 (TRAIGA)','Government agencies must disclose AI interaction',2025,'E','gov','N1 O2',
 'Effective Jan. 1, 2026. Agencies must tell people when they interact with AI; bars social scoring; creates an AI Council and a sandbox. Attorney-general enforcement only, 60-day cure, penalties up to $200,000 per violation. No impact-assessment, human-review or vendor duty.',
 'https://www.akingump.com/en/insights/ai-law-and-regulation-tracker/texas-enacts-a-pair-of-ai-governance-laws-hb-149-and-sb-1188','H'),
('TX','SB 1964','Agency AI inventory and risk standards',2025,'E','gov','I2 A1 O1',
 'Agency AI inventories posted on the open data portal; the Department of Information Resources sets risk-management standards for "heightened scrutiny" AI (consequential decisions) and runs a public-sector sandbox. Benefits not named.',
 'https://capitol.texas.gov/BillLookup/History.aspx?LegSess=89R&Bill=SB1964','M'),
('TX','HB 2060','AI Advisory Council',2023,'E','gov','O1',
 'Created an AI Advisory Council to study state-agency AI use.',
 LS+'TX/bill/HB2060/2023','M'),
('KY','SB 4','AI Governance Committee and agency AI standards',2025,'E','gov','I2 A1 O1',
 'Signed Mar. 24, 2025. Creates an AI Governance Committee; the state technology office sets standards, requires an AI inventory, risk management for high-risk AI and annual reports; agencies must disclose AI use.',
 'https://apps.legislature.ky.gov/record/25rs/sb4.html','H'),
('MT','HB 178','Government use of AI: disclosure and human review',2025,'E','gov','N2 H2',
 'Effective Oct. 1, 2025. Government must disclose AI-published material and public-facing AI interfaces, and a human with authority to reject or change it must review any AI recommendation or decision that could affect a person\'s legal rights, duties or privileges. Benefits not named.',
 LS+'MT/bill/HB178/2025','H'),
('AR','HB 1958 (Act 848)','Public entities must adopt AI and ADS policies',2025,'E','gov','H1',
 'Effective Aug. 2025. Every public entity adopts a policy on authorized AI and automated decision tools; a human must make final decisions. No penalties or central oversight.',
 LS+'AR/bill/HB1958/2025','M'),
('IN','SB 150','AI task force and state-agency AI inventory',2024,'E','gov','I1 O1',
 'Creates an AI task force; agencies inventory AI in use or under consideration. Whether the inventory is public was not confirmed. Expires Dec. 31, 2027.',
 LS+'IN/bill/SB150/2024','M'),
('UT','HB 444 / HB 450','Government ADM treated as high-risk data processing',2025,'E','gov','A1 O1',
 'Treats government automated decision-making as high-risk processing under the state data privacy act. Described by one tracker only.',
 LS+'UT/bill/HB444/2025','L'),
('UT','HB 320','Office of Artificial Intelligence Policy amendments',2026,'E','gov','O1',
 'Expands the Office of AI Policy\'s authority, including over other agencies. Content known only from the title.',
 LS+'UT/bill/HB0320/2026','L'),
('OH','SB 315','Medicaid program integrity and SNAP cybersecurity: automated fraud tools',2026,'E','ben','H2 O1',
 'Signed July 2026, main provisions effective Oct. 6, 2026. The Medicaid department may use automated review and fraud-detection tools, but no action is taken without a department employee verifying the findings.',
 LS+'OH/bill/SB315/2025','M'),
# ---- pending / alive
('NC','H 565','Limit AI use in Medicaid and commercial insurance',2025,'A','ben','H2 V1 O1',
 'Would bar insurers and Medicaid prepaid health plans from using AI as the sole basis to deny care, with provider attestations. Passed the House; re-referred in the Senate June 2026.',
 LS+'NC/bill/H565/2025','M'),
('MI','HB 4537','No Medicaid denials based on AI review',2025,'A','ben','H1',
 'The Medicaid agency or contracted plans may not deny, modify or delay a claim based on an AI review. In committee since 2025.',
 LS+'MI/bill/HB4537/2025','M'),
('PA','HB 1925','AI in utilization review, including Medicaid and CHIP managed care',2025,'A','ben','H1 N1',
 'Amends Title 67 (Public Welfare): AI in utilization review may not override clinical judgment, including for Medicaid and CHIP managed care plans. Passed the House; status conflicts between sources.',
 LS+'PA/bill/HB1925/2025','M'),
('MA','H 77','Fostering AI responsibility',2025,'A','gov','H1',
 'One tracker says it bars agency ADS for benefits or rights decisions unless a law authorizes it; LegiScan gives only a generic description. Reported favorably by committee.',
 LS+'MA/bill/H77/2025','L'),
# ---- failed / died / stalled
('NY','A 7278','No AI decisions affecting benefits by state agencies',2025,'F','ben','H2',
 'Would bar state agencies from using AI to make decisions affecting individuals\' rights, benefits or services; decisions made by human staff. Never left committee.',
 LS+'NY/bill/A07278/2025','H'),
('CA','SB 1248','State agencies: automated decision systems',2026,'F','gov','',
 'Held in committee May 14, 2026. LegiScan gives no description; a tracker says it would limit state agency ADS, including for public benefits.',
 LS+'CA/bill/SB1248/2025','M'),
('CA','SB 430','Local agencies: automated decision systems',2025,'F','ben','H2',
 'Failed Feb. 2, 2026. A tracker says it would bar ADS output as the sole basis for adverse supportive-services decisions by local agencies.',
 LS+'CA/bill/SB430/2025','M'),
('CA','AB 2412','State agencies: public communications (generative AI)',2026,'F','gov','N1',
 'Amends the government code on generative AI in state agency communications. Did not pass.',
 LS+'CA/bill/AB2412/2025','L'),
('HI','SB 59','Algorithmic discrimination and eligibility determinations',2025,'F','ben','N2 O2',
 'Would bar discriminatory algorithmic eligibility determinations, require notices to people whose data is used, annual reports to the attorney general and civil enforcement. Covers private users too. Carried over to 2026 and died.',
 LS+'HI/bill/SB59/2026','H'),
('IL','HB 3567','Meaningful Human Review of AI Act',2025,'F','gov','H2 A2 V1',
 'Would bar state agencies and contractors from using ADS without continuous meaningful human review and require impact assessments. Re-referred to Rules; no action.',
 LS+'IL/bill/HB3567/2025','H'),
('IL','SB 1366','State Government AI Act',2025,'F','gov','I1 A1 V1',
 'Would have the Department of Innovation and Technology set rules on procurement, use and assessment of AI by state agencies. No action.',
 LS+'IL/bill/SB1366/2025','M'),
('GA','HB 147','Annual inventory of AI use by state agencies',2025,'F','gov','I2',
 'Would require the Georgia Technology Authority to inventory AI used by state agencies and report annually. Reported by a Senate committee in 2025; never passed.',
 LS+'GA/bill/HB147/2025','H'),
('RI','H 7119','AI Accountability Act: state agency inventory and commission',2026,'F','gov','I2 O2',
 'Would require an inventory of state agencies using AI and create a 13-member permanent commission. Held for further study.',
 LS+'RI/bill/H7119/2026','H'),
('OK','HB 3545','State agencies: prohibited and permitted AI uses',2026,'F','gov','H1',
 'Would set prohibited and permitted AI uses by state agencies through the state management office. A tracker says it required human review of high-risk decisions. Stalled in committee.',
 LS+'OK/bill/HB3545/2026','M'),
('OR','HB 4103','Commission on AI and a Chief AI Officer',2026,'F','gov','O1',
 'Would create a state commission on AI and a Chief AI Officer. Died in committee at adjournment.',
 LS+'OR/bill/HB4103/2026','H'),
('NH','SB 657','AI and IT systems used by state agencies',2026,'F','gov','',
 'Passed the Senate and was amended; died after the chambers did not agree.',
 LS+'NH/bill/SB657/2026','M'),
('NH','HB 1506','Exception to restricted AI uses by state agencies',2026,'F','gov','',
 'Sent to interim study.',
 LS+'NH/bill/HB1506/2026','M'),
('NM','SB 68','Artificial Intelligence Government Use Act',2026,'F','gov','',
 'Postponed indefinitely. LegiScan gives only the title.',
 LS+'NM/bill/SB68/2026','M'),
('FL','S 146','Use of AI by state agencies (study)',2026,'F','gov','',
 'Would have the Florida Digital Service study AI use by state agencies. Died in committee.',
 LS+'FL/bill/S0146/2026','H'),
('MS','HB 1640','Automated wage verification for human services eligibility',2026,'F','ben','',
 'Would require the Department of Human Services to use automated commercial wage-verification services in benefits eligibility. Failed.',
 LS+'MS/bill/HB1640/2026','M'),
('AK','SB 2','AI, deepfakes, cybersecurity, data transfers',2025,'F','gov','',
 'Includes rules on AI use by state agencies and data transfers between agencies. Referred to committee and not enacted before adjournment.',
 LS+'AK/bill/SB2/2025','M'),
]

ROOT = sys.argv[1] if len(sys.argv) > 1 else None
status_by = {}
if ROOT:
    for d in sorted(glob.glob(ROOT + '/*/*')):
        f = d + '/csv/bills.csv'
        if not os.path.exists(f): continue
        st = os.path.basename(os.path.dirname(d)).split('-')[0]
        for r in csv.DictReader(open(f, encoding='utf-8', errors='replace')):
            n = re.sub(r'^([A-Za-z]+)0+(\d)', r'\1\2', re.sub(r'\s', '', r['bill_number'])).upper()
            status_by[(st, n)] = r

out = []
for s in P:
    st, bill, title, year, status, scope, tags, desc, url, conf = s
    if ROOT:
        key = (st, re.sub(r'\s', '', bill.split('/')[0].split('(')[0]).upper())
        r = status_by.get(key)
        mine = (url or '').rstrip('/').split('/')[-1]
        if r and url and url.startswith(LS) and r['url'].rstrip('/').split('/')[-1] == mine:
            url = r['url']          # same session year: bill identity confirmed, use LegiScan's exact URL
            print('verified  ', key, r['status_desc'], r['status_date'], '| listed as', status)
        elif url and url.startswith(LS):
            print('NOT CHECKED', key, '(older session or different year; link built from LegiScan URL pattern)')
    out.append([st, bill, title, year, status, scope, tags, desc, url, conf])

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, '..', 'data', 'policies.js'), 'w', encoding='utf-8') as fh:
    fh.write('/* Generated by tools/build_policies.py. Government and benefits AI/ADS policies; see that file for field meanings. */\n')
    fh.write('window.POL=' + json.dumps(out, ensure_ascii=False, indent=0, separators=(',', ':')) + ';\n')
print(len(out), 'policies')
