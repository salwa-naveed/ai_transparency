/* Data for the State AI Transparency Law Map.
   LAWS: every entry in the Transparency Coalition "2026 State AI Legislation Report" (Oct. 27, 2026; 115 entries, 30 states).
   Fields: [state, bill, short title, category, status (E enacted / P passed-awaiting-signature), framework tags]
   Framework tags: letter = framework step, digit = how closely the law mirrors it (2 close analogue, 1 loose analogue).
     I public inventory/registry · N individual notice · P pre-deployment assessment/testing
     M monitoring, human oversight, audits · C oversight commission/council · V vendor/developer duties
   Tags are the site author's reading of the report's summaries, not the report's own classification. */

window.CATS = {
  chat: 'Chatbot safety',
  soc:  'Kids & social media',
  deep: 'Deepfakes & likeness',
  elec: 'Election AI disclosure',
  hlth: 'Health insurance & clinical AI',
  ther: 'AI therapy bans',
  edu:  'Schools & education',
  disc: 'AI disclosure & provenance',
  aud:  'Audits & frontier AI safety',
  adm:  'Automated decision systems',
  priv: 'Privacy & data',
  mkt:  'Pricing & antitrust',
  work: 'Workplace',
  oth:  'Other'
};

window.FW = [
  {k:'I', n:'Public inventory', s:'Step 1', d:'Agencies publish a machine-readable, annually updated inventory of every automated decision system used in a covered decision (name, purpose, vendor, deployment date, last impact assessment, waivers).'},
  {k:'N', n:'Individual notice & explanation', s:'Step 2', d:'Each notice says whether an ADS was used, names it, and gives a plain-language explanation of any adverse decision within [10] days, with human review, correction and appeal rights.'},
  {k:'P', n:'Pre-deployment impact assessment & testing', s:'Step 3', d:'Published assessment before use: accuracy, error rates by protected group, proxy testing, edge cases, human-algorithm interaction test; sent to the governor and legislative leaders [30] days ahead.'},
  {k:'M', n:'Post-deployment monitoring, oversight & audits', s:'Step 3', d:'Override and agreement rates by group, reversal rates, re-testing when model or vendor changes, compliance audits, mandatory discontinuation of discriminatory systems, human review.'},
  {k:'C', n:'Independent oversight body', s:'Step 3', d:'A state commission (the paper cites Rhode Island\'s Commission for Human Rights) that receives referrals, orders corrections and can require suspension.'},
  {k:'V', n:'Vendor & developer obligations', s:'Step 4', d:'Contracts require documentation of uses, limits, validation and subgroup performance; cooperation with audits; tiered disclosure; no trade-secret bar to applicant disclosure; procurement condition.'},
  {k:'E', n:'Enforcement', s:'Design choice', d:'Attorney general, private right of action, an independent third-party office, or none.'}
];

window.LAWS = [
['AL','SB 63','AI in health insurance prior authorizations','hlth','E','N2 M1'],
['AL','HJR 51','AI and Children\'s Internet Safety Commission','soc','E','C1'],
['AZ','HB 2665','Cade\'s Law: encouraging a minor\'s suicide','oth','E',''],
['CA','AB 2','Social media duty of care, liability for injury','soc','E',''],
['CA','AB 302','Addictive feeds in school communication','soc','E',''],
['CA','AB 502','AI in deceptive election ads and election officials','elec','E','N1'],
['CA','AB 1159','Student data cannot train AI (HESIPA)','priv','E','V1'],
['CA','AB 1331','Workplace surveillance in bathrooms','work','E',''],
['CA','AB 1405','State AI Auditor Registry','aud','E','I1 M2'],
['CA','AB 1609','Customer service chatbot disclosure','disc','E','N1'],
['CA','AB 1651','AI disclosure for State Bar exam materials','disc','E','I1 N1'],
['CA','AB 1709','Ban addictive feeds for under 16; e-Safety Advisory Commission','soc','E','C1'],
['CA','AB 1792','Digital violence in school health instruction','edu','E',''],
['CA','AB 1856','Digital Age Assurance Act update','soc','E',''],
['CA','AB 1883','Limits on workplace data incl. neural data','work','E',''],
['CA','AB 1979','Health care chatbots under CMIA','hlth','E',''],
['CA','AB 2025','AI disclosure in rental ads','disc','E','N1'],
['CA','AB 2071','Digital wellness in health education','edu','E',''],
['CA','AB 2148','Public school employees must be human','edu','E',''],
['CA','AB 2246','Age-Appropriate Design Code revisions','soc','E',''],
['CA','AB 2392','GenAI procurement standards for colleges','edu','E','V1'],
['CA','AB 2713','AI Transparency Act update (provenance)','disc','E','V1'],
['CA','SB 503','Bias risks in AI clinical decision support','hlth','E','P2 V2'],
['CA','SB 813','Framework and standards for AI auditors (IVOs)','aud','E','M2 V1'],
['CA','SB 867','Four-year moratorium on AI toys','oth','E',''],
['CA','SB 928','CSU instructors must be human','edu','E',''],
['CA','SB 947','Worker protections for AI and ADS','adm','E','N1'],
['CA','SB 951','90-day notice of tech displacement','work','E','N1'],
['CA','SB 1000','AI Transparency Act modification','disc','E','V1'],
['CA','SB 1050','Synthetic performers in ads','disc','E','N1'],
['CA','SB 1111','Digital replica impersonation','deep','E',''],
['CA','SB 1119','Adam\'s Law: chatbot safety','chat','E','N1 P2 M2'],
['CA','SB 1128','No required devices in kindergarten','edu','E',''],
['CA','SB 1159','AI is not a person under Public Records Act','oth','E',''],
['CO','SB 189','Revised 2024 AI Act (lighter ADMT framework)','adm','E','N1'],
['CO','HB 1139','Human review of AI health authorization denials','hlth','E','N2 M1'],
['CO','HB 1195','Prohibition of AI therapy chatbots','ther','E',''],
['CO','HB 1263','Chatbot safety and kids\' algorithmic addiction','chat','E','N1'],
['CT','SB 4','Data Privacy Act: data brokers, facial recognition','priv','E','I1'],
['CT','SB 5','Omnibus AI and online safety act','adm','E','N1 P1 M1 C1 V1'],
['GA','SB 540','Chatbot safety and disclosure','chat','E','N1'],
['GA','SB 444','AI in health insurance decisions','hlth','E','M1'],
['HI','SB 3001','Chatbot disclosures and safety protocols','chat','E','N1'],
['HI','HB 2137','Deepfake protections; synthetic performer disclosure','deep','E','N1'],
['ID','HB 542','Stop Harms from Addictive Social Media Act','soc','E',''],
['ID','SB 1297','Conversational AI Safety Act','chat','E','N1'],
['ID','HB 727','Synthetic media in voyeurism law','deep','E',''],
['ID','SB 1227','Statewide framework for AI in K-12','edu','E','M1'],
['IL','SB 315','AI Safety Measures Act (frontier models)','aud','E','I1 P2 M2 V2'],
['IL','HB 5511','Children\'s Online Social Media Safety Act','soc','E',''],
['IL','SB 318','Prohibition on bots buying tickets','oth','E',''],
['IL','SB 343','Rental price fixing via collusion or AI','mkt','E',''],
['IL','SB 2909','No AI scoring in teacher evaluations','edu','E','M1'],
['IL','SB 3114','Human review of claim downcoding','hlth','E','M1'],
['IN','HB 1271','AI in health care approvals: disclosure and appeal','hlth','E','N2 M1'],
['IA','SF 2417','Chatbot safety act for minors','chat','E','N1'],
['IA','HF 2635','AI cannot be sole basis for prior-auth denial','hlth','E','M1'],
['ME','LD 2082','Prohibiting AI therapy chatbots','ther','E',''],
['LA','HB 119','Deepfake protections','deep','E',''],
['LA','HB 459','AI disclosure in campaign material','elec','E','N1'],
['LA','HB 475','Consent to AI-transcribed medical recordings','hlth','E','N1'],
['LA','HB 639','AI disclosure in campaign calls','elec','E','N1'],
['LA','SB 386','Louisiana Data Privacy Act','priv','E',''],
['KS','HB 2183','AI-generated CSAM','deep','E',''],
['KS','HB 2537','Sexual extortion including AI (minors)','deep','E',''],
['MD','SB 8','AI deepfake protections','deep','E',''],
['MD','SB 720','State guidance on evaluating AI tools in schools','edu','E','V1'],
['MD','SB 141','AI deepfakes in election materials','elec','E',''],
['MD','HB 895','Surveillance pricing ban (food retailers)','mkt','E',''],
['NE','LB 525','Conversational AI Safety Act','chat','E','N1'],
['NJ','A 3497','FAIR Act: algorithmic rent inflation','mkt','E',''],
['MN','HF 4138','Kids Social Media Safety Act','soc','E',''],
['NY','Safe By Design Act','Child online safety defaults (FY27 budget)','soc','E',''],
['NY','S 9051','AI chatbot safety with child protections (signed Oct. 28)','chat','E','N1'],
['NY','A 6578','AI Training Data Transparency Act','disc','P','I1 V2'],
['NY','S 6954','Provenance data on synthetic content','disc','P','V1'],
['NY','S 8451','FAIR News Act: AI-created news disclosure','disc','P','N1'],
['NY','A 9349','Ban on surveillance pricing','mkt','P',''],
['NY','A 3411','AI inaccuracy warning label','disc','P','N1'],
['OK','SB 1734','Responsible Technology in Schools Act','edu','E','V1'],
['OK','HB 3244','AI in aggravated identity theft','deep','E',''],
['OR','SB 1546','AI Chatbot Safety Act','chat','E','N1 M1'],
['PA','SB 806','AI Deceptive Advertising Act (Act 99, signed Oct. 22)','disc','E','N1'],
['RI','S 2195 / H 7350','Chatbot safety; annual reports to AG','chat','E','I1 M2'],
['RI','H 7349 / S 2197','Oversight of AI in mental health care','ther','E',''],
['SC','H 3431','Social Media Regulation Act','soc','E',''],
['SC','H 4591','Stop Harm From Addictive Social Media Act','soc','E',''],
['TN','SB 837','Personhood excludes AI','oth','E',''],
['TN','SB 1469','Minors under 14 monetizing video','soc','E',''],
['TN','SB 1580','Prohibiting AI therapy chatbots','ther','E',''],
['TN','SB 2310','Bell-to-bell device limits, K-5','edu','E',''],
['TN','SB 2041','Deepfake intimate image civil action','deep','E',''],
['UT','SB 69','Bell-to-bell phone restrictions','edu','E',''],
['UT','HB 276','Digital Voyeurism Prevention Act (provenance)','deep','E','V1'],
['UT','SB 73','Online age verification','soc','E',''],
['UT','HB 273','Balance Act: AI in school standards','edu','E',''],
['UT','HB 289','AI-generated CSAM definition','deep','E',''],
['UT','SB 150','AI in medical scope of practice','hlth','E','M1'],
['UT','SB 319','AI in health insurance authorizations','hlth','E','I1 N2 M1'],
['UT','HB 218','Digital skills course; Advisory Tech Council','edu','E','C1'],
['UT','SB 256','Libel and slander in the age of AI','deep','E',''],
['VT','H 211','Data broker regulation','priv','E','I1'],
['VT','H 814','Neurological rights','priv','E',''],
['VT','H 816','Therapy bots ban; AI Advisory Council','ther','E','C1'],
['VT','S 23','AI disclosure in election materials','elec','E','N1'],
['VA','HB 580','Consumer Counsel programs on AI fraud','oth','E','M1'],
['VA','HB 797','Study: licensing third-party AI auditors','aud','E','M1 C1'],
['VA','HB 1186','AI in public schools','edu','E',''],
['VA','SB 245','Social media in school communications','edu','E',''],
['WA','HB 2225','Chatbot safety and kids protections','chat','E','N1 M1'],
['WA','SB 5105','AI-generated CSAM','deep','E',''],
['WA','SB 5886','Digital likeness property right','deep','E',''],
['WA','HB 1170','AI disclosure and provenance','disc','E','N1 V1'],
['WA','SB 5395','Human review of AI prior-auth denials','hlth','E','N1 M2'],
['WY','HB 102','AI chatbots, minors and self-harm','chat','E','']
];

/* Enforcement mechanism by state (framework design choice), drawn from the report and the uploaded policy paper.
   lvl: 2 = a regulator-enforced mechanism with stated penalties or a private right, 1 = general consumer-protection route. */
window.ENF = {
  CA:{lvl:2, t:'AB 1709: attorney general, up to $50,000 per affected minor. SB 1119: narrow private right of action limited to actual harm, plus biennial independent audits sent to the AG. AB 1159: private right of action.'},
  RI:{lvl:2, t:'Attorney general; chatbot violations up to $15,000 per day.'},
  OR:{lvl:2, t:'SB 1546: users with ascertainable harm may sue for damages and injunctions.'},
  ID:{lvl:2, t:'HB 542: attorney general plus a private right of action.'},
  MN:{lvl:2, t:'HF 4138: attorney general (deceptive trade practice) plus a private right of action.'},
  WY:{lvl:2, t:'HB 102: felony penalties up to 10 years, but only with proof of harmful intent.'},
  WA:{lvl:1, t:'HB 2225: unfair or deceptive act in trade.'},
  ME:{lvl:1, t:'LD 2082: unfair trade practice.'},
  MD:{lvl:1, t:'HB 895: unfair or deceptive trade practice with a 45-day right to cure.'},
  UT:{lvl:1, t:'HB 276: Utah Division of Consumer Protection.'},
  NY:{lvl:1, t:'Safe By Design Act: attorney general promulgates regulations and enforces.'},
  CT:{lvl:1, t:'Per the policy paper, Connecticut relies on attorney general enforcement only.'},
  CO:{lvl:1, t:'Per the policy paper, attorney general enforcement only with a 60-day cure period.'},
  TX:{lvl:2, t:'Per the policy paper, attorney general enforcement only, 60-day cure period, penalties up to $200,000 per violation.'}
};

/* Benchmarks from the uploaded policy paper (and, where flagged, background knowledge). These are the whiteboard's columns.
   src: 'paper' = stated in the policy paper; 'bg' = background knowledge of the author, verify before citing. */
window.BENCH = {
  FED:{name:'Federal (OMB M-25-21)', cells:{
    I:{lvl:2, src:'paper', t:'Annual AI use-case inventories; public reporting of determinations and waivers for high-impact uses.'},
    P:{lvl:2, src:'paper', t:'Pre-deployment testing and impact assessment for high-impact AI.'},
    M:{lvl:2, src:'paper', t:'Ongoing monitoring after deployment.'}
  }},
  NY:{name:'New York (LOADinG Act, 2024)', cells:{
    I:{lvl:2, src:'bg', t:'LOADinG Act requires state agencies to inventory the automated decision-making tools they use. The paper cites the Act for assessments, not inventories; verify.'},
    P:{lvl:2, src:'paper', t:'Impact assessment for bias and discrimination at least every two years; transmitted to the governor and legislative leaders and published 30 days before a new system takes effect.'},
    M:{lvl:2, src:'paper', t:'Mandatory discontinuation of any system found to be discriminatory.'}
  }},
  TX:{name:'Texas', cells:{
    N:{lvl:1, src:'bg', t:'TRAIGA (2025) requires government agencies to tell people when they interact with AI. Not in the uploaded sources; verify.'},
    E:{lvl:2, src:'paper', t:'Attorney general enforcement only, 60-day cure period, penalties up to $200,000 per violation.'}
  }},
  CO:{name:'Colorado (2024 AI Act)', cells:{
    P:{lvl:0, src:'paper', t:'SB 189 (2026) eliminated risk-management programs and annual impact assessments, a rollback of this step.'}
  }}
};

window.SCOPE_NOTE = 'Scope choice from the paper: Colorado covers only tools that "materially influence" outcomes; the paper recommends a broad definition for the inventory step.';
