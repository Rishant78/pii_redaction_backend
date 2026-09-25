# Current Detector Baseline Audit — Red Herring Prospectus

> **Methodology**: The existing detection pipeline was run **unmodified** against `input/Red Herring Prospectus.docx` (127 pages, ~1.8 MB). Two modes were tested: (1) `detect_all()` alone (what the analysis endpoint reports), and (2) the full 2-pass redaction pipeline including entity-registry propagation (what `redact_docx()` actually does). No precision/recall/F1 is claimed — we have no ground truth.

---

## 1. Detection Summary

| PII Category | detect_all Only | | Full Pipeline (w/ Registry) | |
|---|---:|---:|---:|---:|
| | Occurrences | Unique | Occurrences | Unique |
| **PERSON** | 103 | 22 | 225 | 25 |
| **EMAIL** | 70 | 26 | 70 | 26 |
| **PHONE** | 49 | 22 | 49 | 22 |
| **ORGANIZATION** | 124 | 55 | 124 | 55 |
| **ADDRESS** | 48 | 36 | 48 | 36 |
| **SSN** | 0 | 0 | 0 | 0 |
| **CREDIT_CARD** | 0 | 0 | 0 | 0 |
| **DOB** | 0 | 0 | 0 | 0 |
| **IP_ADDRESS** | 0 | 0 | 0 | 0 |
| **TOTAL** | **394** | **161** | **516** | **164** |

**Key insight**: The entity registry adds **122 additional PERSON detections** (and 3 new unique case variants) by re-matching discovered names throughout the document. Without the registry, person-name coverage drops by 54%.

Zero detections for SSN, CREDIT_CARD, DOB, and IP_ADDRESS is expected — this is an Indian IPO prospectus, not a US financial document. These detectors are functional (proven by unit tests) but have no matching content in this input.

---

## 2. Every Unique Detected Value

### 2.1 PERSON (22 unique via detect_all; 25 via registry)

| # | Name | Confidence | Source | detect_all Occ. | Full Pipeline Occ. |
|---|------|---:|--------|---:|---:|
| 1 | Amod Joshi | 0.91 | title-list | 3 | 3 |
| 2 | Anand Soni | 0.93 | high-confidence-context | 1 | 1 |
| 3 | Ashish Mathew Pulloor | 0.93 | high-confidence-context | 1 | 1 |
| 4 | Cherag Gyara | 0.93 | high-confidence-context | 1 | 1 |
| 5 | Chitra Raste | 0.93 | high-confidence-context | 1 | 1 |
| 6 | Ganesh Prasad | 0.91 | title-list | 2 | 2 |
| 7 | Hitesh Ramani | 0.93 | high-confidence-context | 1 | 1 |
| 8 | KUSHAL SUBBAYYA HEGDE | 0.95 | promoter-heading | 15 | 23 |
| 9 | Kushal Subbayya Hegde | 0.93 | high-confidence-context | 1 | 21 |
| 10 | Manisha Shukla | 0.93 | high-confidence-context | 1 | 1 |
| 11 | PUSHPA KUSHAL HEGDE | 0.95 | promoter-heading | 15 | 23 |
| 12 | Prakash Boricha | 0.93 | high-confidence-context | 1 | 1 |
| 13 | Pushpa Kushal Hegde | — | entity-registry only | 0 | 15 |
| 14 | RAJESH KUSHAL HEGDE | 0.95 | promoter-heading | 15 | 23 |
| 15 | RAKHI GIRIJA SHETTY | 0.95 | promoter-heading | 15 | 15 |
| 16 | Rajesh Kushal Hegde | 0.93 | high-confidence-context | 1 | 19 |
| 17 | Rakhi Girija Shetty | — | entity-registry only | 0 | 14 |
| 18 | ROHIT KUSHAL HEGDE | 0.95 | promoter-heading | 15 | 23 |
| 19 | Rohit Kushal Hegde | — | entity-registry only | 0 | 18 |
| 20 | Sandesh Bhagwat | 0.91 | title-list | 3 | 3 |
| 21 | Sarthak Malvadkar | 0.93 | high-confidence-context | 4 | 7 |
| 22 | Shanti Gopalkrishnan | 0.93 | high-confidence-context | 3 | 5 |
| 23 | Sharmila Joshi | 0.93 | high-confidence-context | 1 | 1 |
| 24 | Tushar Wakhele | 0.93 | high-confidence-context | 1 | 1 |
| 25 | Varun Badai | 0.93 | high-confidence-context | 2 | 2 |

### 2.2 EMAIL (26 unique) — masked

| # | Masked Email | Conf. |
|---|-------------|---:|
| 1 | Ipo\*\*\*@icicibank.com | 1.00 |
| 2 | Sar\*\*\*@kshinterantional.com | 1.00 |
| 3 | ana\*\*\*@bajajfinserv.in | 1.00 |
| 4 | ash\*\*\*@federalbank.co.in | 1.00 |
| 5 | che\*\*\*@icicibank.com | 1.00 |
| 6 | cs.\*\*\*@kshinternational.com | 1.00 |
| 7 | cus\*\*\*@icicisecurities.com | 1.00 |
| 8 | cus\*\*\*@nuvama.com | 1.00 |
| 9 | eri\*\*\*@hdfcbank.com | 1.00 |
| 10 | hin\*\*\*@gmail.com | 1.00 |
| 11 | hit\*\*\*@citi.com | 1.00 |
| 12 | ipo\*\*\*@trilegal.com | 1.00 |
| 13 | ksh\*\*\*@nuvama.com | 1.00 |
| 14 | ksh\*\*\*@icicisecurities.com | 1.00 |
| 15 | ksh\*\*\*@in.mpms.mufg.com | 1.00 |
| 16 | man\*\*\*@hdfcbank.com | 1.00 |
| 17 | par\*\*\*@kirtanepandit.com | 1.00 |
| 18 | pra\*\*\*@nuvama.com | 1.00 |
| 19 | pra\*\*\*@hdfcbank.com | 1.00 |
| 20 | pro\*\*\*@eximbankindia.in | 1.00 |
| 21 | rm6\*\*\*@sbi.co.in | 1.00 |
| 22 | sac\*\*\*@hdfcbank.com | 1.00 |
| 23 | sha\*\*\*@indusind.com | 1.00 |
| 24 | she\*\*\*@nuvama.com | 1.00 |
| 25 | sid\*\*\*@hdfcbank.com | 1.00 |
| 26 | tus\*\*\*@hdfcbank.com | 1.00 |

### 2.3 PHONE (22 unique) — masked

| # | Masked Phone | Digits | Conf. |
|---|-------------|---:|---:|
| 1 | + 91\*\*\*5100 | 12 | 0.98 |
| 2 | + 91\*\*\*3237 | 12 | 0.98 |
| 3 | + 91\*\*\*3237 | 12 | 0.98 |
| 4 | + 91\*\*\*5100 | 12 | 0.98 |
| 5 | + 91\*\*\*4400 | 12 | 0.98 |
| 6 | + 91\*\*\*0456 | 12 | 0.98 |
| 7 | + 91\*\*\*0360 | 12 | 0.98 |
| 8 | +91 \*\*\*8211 | 12 | 0.98 |
| 9 | +91 \*\*\*3100 | 12 | 0.98 |
| 10 | +91 \*\*\*4494 | 12 | 0.98 |
| 11 | +91 \*\*\*4648 | 12 | 0.98 |
| 12 | +91 \*\*\*6403 | 12 | 0.98 |
| 13 | +91 \*\*\*2914 | 12 | 0.80 |
| 14 | +91 \*\*\*2928 | 12 | 0.98 |
| 15 | +91 \*\*\*2929 | 12 | 0.98 |
| 16 | +91 \*\*\*4400 | 12 | 0.98 |
| 17 | +91 \*\*\*4400 | 12 | 0.98 |
| 18 | +91 \*\*\*1000 | 12 | 0.98 |
| 19 | +91 \*\*\*7100 | 12 | 0.98 |
| 20 | +91 \*\*\*4949 | 12 | 0.98 |
| 21 | +91-\*\*\*4000 | 12 | 0.98 |
| 22 | 022-\*\*\*2182 | 11 | 0.98 |

### 2.4 ORGANIZATION (55 unique)

| # | Organization Name | Occ. |
|---|-------------------|---:|
| 1 | BSE Limited and National Stock Exchange of India Limited | 1 |
| 2 | Bajaj Finance Limited | 1 |
| 3 | Bhandary Metal Extrusion Private Limited | 3 |
| 4 | Bharat Bijlee Limited | 1 |
| 5 | CARE Analytics and Advisory Private Limited | 4 |
| 6 | CARE Ratings Limited | 2 |
| 7 | CG Power and Industrial Solutions Limited | 1 |
| 8 | Care Analytics and Advisory Private Limited | 2 |
| 9 | Care Ratings Limited | 1 |
| 10 | Elantas Beck India Limited | 1 |
| 11 | Formerly Link Intime India Private Limited | 6 |
| 12 | Georgia Transformer Corporation | 1 |
| 13 | HDFC Bank Limited | 8 |
| 14 | HDFC Bank Limited and ICICI Bank Limited | 1 |
| 15 | Hindalco Industries Limited | 1 |
| 16 | ICICI Securities Limited | 5 |
| 17 | ICICI Securities Limited (tab variant) | 2 |
| 18 | ICICI Bank Limited | 4 |
| 19 | IndusInd Bank Limited | 1 |
| 20 | KSH Distriparks Private Limited | 2 |
| 21 | KSH Infra Park IV Private Limited | 2 |
| 22 | KSH Infra Park VI Private Limited | 2 |
| 23 | KSH Integrated Logistics Private Limited | 2 |
| 24 | KSH International Limited | 3 |
| 25 | KSH International Private Limited | 3 |
| 26 | KSH Project Management Services Private Limited | 2 |
| 27 | Kanj and Co LLP | 1 |
| 28 | Kushal Motors and Electricals Private Limited | 2 |
| 29 | MUFG Intime India Private Limited | 6 |
| 30 | Malabar India Fund Limited | 1 |
| 31 | National Payments Corporation | 1 |
| 32 | National Securities Depository Limited | 1 |
| 33 | National Stock Exchange of India Limited | 10 |
| 34 | Nidec Industrial Automation India Private Limited | 1 |
| 35 | Nuvama Wealth Management Limited | 5 |
| 36 | Nuvama Wealth Management Limited (tab variant) | 2 |
| 37 | Nuvama Wealth Management Limited and ICICI Securities Limited | 2 |
| 38 | Offer Escrow Collection Bank HDFC Bank Limited | 1 |
| 39 | Precision Wires India Limited | 1 |
| 40 | Savli Copper Products Private Limited | 1 |
| 41 | Shubhkamal Leasing and Investment Private Limited | 2 |
| 42 | Solar Energy Corporation of India Limited | 1 |
| 43 | The Federal Bank Limited | 1 |
| 44 | Virginia Transformer Corporation | 1 |
| 45-55 | Waterloo Industrial Park I-IX Private Limited, Waterloo Motors Private Limited | 2-3 each |

### 2.5 ADDRESS (36 unique)

| # | Detected Address |
|---|-----------------|
| 1 | 11/3, 11/4 and 11/5, Village Birdewadi, Chakan Taluka-Khed, Pune - 410 501, Maharashtra, India |
| 2 | 11/3, 11/4 and 11/5 Village Birdewadi, Chakan, Taluka Khed, Pune - 410 501 |
| 3 | 12 Buena Monte, NCL co-operative housing society, Panchvati, Pashan, Pune - 411 008 |
| 4 | 163, 5th Floor, H.T.Parekh Marg Backbay Reclamation Churchgate, Mumbai - 400020 |
| 5 | 1st Floor, L B S Marg, Vikhroli (West) Mumbai 400083 |
| 6 | 201, Tower 2, Montreal Business Centre, Off Pallod Farms, Baner Pune - 411 045 |
| 7 | 201, Tower 2, Montreal Business Centre, Off Pallod Farms, Baner, Pune - 411 045, Maharashtra, India |
| 8 | 3 Prabhat Road, opposite PYC basketball court, Deccan Gymkhana, Pune - 411 004 |
| 9 | 3 Prabhat Road, opposite PYC basketball court, Erandawane, Deccan Gymkhana, Pune - 411 004 |
| 10 | 3, Shivaji Nagar, Deccan Gymkhana, Pune - 411 004, Maharashtra, India |
| 11 | 5, Chakan Industrial Area, Phase II, Village Khalumbre, Taluka Khed, Pune - 410 501 |
| 12 | 602, Gopalkrupa Apartment, Bhonde colony, Prabhat Road, Erandawane, Pune - 411 004 |
| 13 | 801 - 804, Wing A, Building No 3, Inspire BKC, G Block, Bandra Kurla Complex, Bandra East, Mumbai 400051 |
| 14 | A-259, JK Road, Minal Residency, Huzur, Govindpura, Bhopal - 462 023 |
| 15 | A29, Abhimanshree Society, Pashan Road, Pune - 411 008, Maharashtra, India |
| 16 | Bandra East, Mumbai - 400 051 |
| 17 | Bandra Kurla Complex, Bandra (E) Mumbai - 400 051, Maharashtra, India |
| 18 | Bandra Kurla Complex, Bandra East Mumbai 400 051 |
| 19 | Bund Garden Road, Pune - 411 001 |
| 20 | C-101, Embassy 247, 1st Floor, L B S Marg, Vikhroli (West), Mumbai 400083 |
| 21 | F-223, Supa Parner Industrial Park, Mauje Palve Khurd, Taluka Parner, Dist - Ahmednagar, Maharashtra - 414 301 |
| 22 | ICICI Securities Limited ICICI Venture House Appasaheb Marathe Marg Prabhadevi, Mumbai - 400 025 |
| 23 | ICICI Venture House, Appasaheb Marathe Marg, Prabhadevi, Mumbai 400025, Maharashtra, India |
| 24 | J-25, Taloja Industrial Area, Village Padghe, Taluka Panvel, Raigad - 410 208, Maharashtra, India |
| 25 | Koregaon Park, Pune - 411 001 |
| 26 | Next to Kanjurmarg Railway Station, Kanjurmarg (East) Mumbai - 400042, Maharashtra, India |
| 27 | Opposite Harshal Hall, above HDFC Limited Karve Road, Pune - 411 038 |
| 28 | Our manufacturing facility at 11/3, 11/4 and 11/5, Village Birdewadi, Chakan Taluka - Khed, Pune - 410 501 |
| 29 | PCNTDA Green Building Block A 1st and 2nd floor Near Akurdi Railway Station Akurdi, Pune - 411 044 |
| 30 | Pratik Bunglow, Senapati Bapat Road, behind Sahara Hotel, Shivajinagar, Model Colony, Pune - 411 016 |
| 31 | Senapati Bapat Marg, Lower Parel (West) Mumbai - 400 013 |
| 32 | Signature Building, Bhandarkar road Shivaji Nagar, Pune - 411 004 |
| 33 | Taluka Khed, District Pune - 410 501 |
| 34 | The corporate office of our company at 201, Tower 2, Montreal Business Centre... Pune - 411 045 |
| 35 | The registered office of our Company at 11/3, 11/4 and 11/5, Village Birdewadi... Pune - 410 501 |
| 36 | Taluka Khed, District Pune - 410 501 (variant) |

### 2.6 SSN / CREDIT_CARD / DOB / IP_ADDRESS

**Zero detections for all four categories.** This is expected — the document is an Indian IPO Red Herring Prospectus and does not contain US SSNs, credit card numbers, explicit dates of birth with context keywords, or IP addresses.

---

## 3. Likely True Positives

| Category | Assessment |
|----------|-----------|
| **PERSON (25 unique)** | All 25 names correspond to real individuals — promoters (Hegde family), directors, company officers, bank contacts. High confidence. |
| **EMAIL (26 unique)** | All 26 are well-formed email addresses appearing near "Email:" labels. All are corporate emails. Very high confidence. |
| **PHONE (21 of 22)** | 21 phone numbers appear near "Telephone:" / "Tel:" labels with Indian +91 prefix or landline format. High confidence. |
| **ORGANIZATION (~50 of 55)** | Most are legitimate company names with corporate suffixes (Limited, Private Limited, LLP, Corporation). |
| **ADDRESS (~33 of 36)** | Most are clearly physical addresses with street/road names, city, PIN code, and state. |

---

## 4. Likely False Positives

| # | Category | Detected Value | Reason |
|---|----------|---------------|--------|
| 1 | PHONE | `+91 22 30752914` (conf=0.80) | Appears near "Telephone:" label so actually likely valid despite low confidence score. Not a true FP. |
| 2 | ORG | "Formerly Link Intime India Private Limited" (x6) | Begins with "Formerly" — a parenthetical note, not the org's name. Should be "Link Intime India Private Limited". |
| 3 | ORG | "Offer Escrow Collection Bank HDFC Bank Limited" | Role prefix "Offer Escrow Collection Bank" is not part of the org name. Should be "HDFC Bank Limited". |
| 4 | ORG | "BSE Limited and National Stock Exchange of India Limited" | Two orgs concatenated. Each should be detected individually. |
| 5 | ORG | "HDFC Bank Limited and ICICI Bank Limited" | Two orgs joined by "and". |
| 6 | ORG | "Nuvama Wealth Management Limited and ICICI Securities Limited" (x2) | Two orgs as one span. |
| 7 | ORG | "CARE Analytics..." vs "Care Analytics..." | Case-variant duplicates. |
| 8 | ORG | "ICICI Securities Limited" (tab variant with `\t`) | Tab creates duplicate entry. |
| 9 | ADDRESS | "ICICI Securities Limited ICICI Venture House Appasaheb Marathe Marg..." | Org name incorrectly included in address span. |
| 10 | ADDRESS | "Our manufacturing facility located at..." / "The registered office..." | Descriptive prose prefix included in address. |

**Overall false-positive rate appears low** — ~18 problematic detections out of 516 (~3.5%), mostly org boundary issues and address span overreach. No phantom structured-PII false positives.

---

## 5. Likely False Negatives (Missed PII)

### 5.1 PERSON — Partial Name Variants (CRITICAL)

| Missed Name Variant | Occurrences in Doc | Why Missed |
|--------------------|--------------------|-----------|
| "Kushal Hegde" (without "Subbayya") | **62** | Registry only has "Kushal Subbayya Hegde" — exact match fails on shortened form |
| "Rajesh Hegde" (without "Kushal") | **7** | Registry only has "Rajesh Kushal Hegde" |
| "Rohit Hegde" (without "Kushal") | **4** | Registry only has "Rohit Kushal Hegde" |
| "Pushpa Hegde" (without "Kushal") | **2** | Registry only has "Pushpa Kushal Hegde" |

**"Kushal Hegde" appears 62 times in the document and is never detected/redacted.** This is the primary promoter referred to by short name throughout the prospectus. This is the **single largest PII leak** in the current pipeline.

### 5.2 ORGANIZATION — Missing Detections

| Missed Organization | Occurrences | Why Missed |
|--------------------|---:|-----------|
| KSH International (no suffix) | ~13 | Only caught when followed by "Limited" or "Private Limited" (6 of 19 detected) |

**Regulatory bodies** (SEBI 285x, BSE 57x, NSE 20x, RBI 6x, etc.) are not detected. However, these are **public regulatory institutions**, arguably not PII, and redacting them would make the prospectus unreadable. This is likely correct behavior for a PII tool — flagged as a design decision, not a defect.

### 5.3 DOB — Zero Detections (Document Characteristic)

The document contains **zero explicit "Date of Birth:" / "DOB:" / "born on" context patterns**. Manual pattern scanning confirmed no age/DOB data appears in extractable paragraph text. This is a characteristic of this particular RHP — it does not include directors' birth dates.

### 5.4 Other Gaps

| Gap | Detail |
|-----|--------|
| No DIN/PAN/Aadhaar found | Pattern search confirmed: document does not contain these in extractable text |
| Text boxes / SmartArt | Not traversed by `iter_paragraphs()`. Unknown if PII exists there |
| Footnotes / Endnotes | Not traversed. Unknown if PII exists there |

---

## 6. Grouped Findings Summary

### True Positives (estimated ~498 of 516 full-pipeline detections)

| Category | Count | Notes |
|----------|------:|-------|
| PERSON | ~225 | All 25 unique names are real individuals; registry propagation works well |
| EMAIL | 70 | All 26 unique emails legitimate |
| PHONE | ~49 | All near phone labels |
| ORGANIZATION | ~110 | ~50 of 55 unique values legitimate |
| ADDRESS | ~44 | ~33 of 36 correct physical addresses |

### False Positives (estimated ~18 of 516)

| Category | Count | Issue |
|----------|------:|-------|
| ORGANIZATION | ~14 | "Formerly..." prefix, compound "X and Y" orgs, role-prefix orgs, case/tab duplicates |
| ADDRESS | ~4 | Org name in address span, prose prefix in span |

### False Negatives (estimated ~88 missed occurrences, excluding regulatory orgs)

| Category | Est. Missed | Issue |
|----------|---:|-------|
| PERSON (partial names) | ~75 | "Kushal Hegde" (62x), "Rajesh Hegde" (7x), "Rohit Hegde" (4x), "Pushpa Hegde" (2x) |
| ORGANIZATION (no suffix) | ~13 | "KSH International" without "Limited"/"Private Limited" |

---

## 7. Key Takeaways

1. **The entity registry is the hero.** Without it, PERSON coverage drops 54% (225 to 103). The 2-pass architecture is the project's strongest design decision.

2. **Partial name variants are the biggest PII leak.** "Kushal Hegde" alone = 62 unredacted mentions of the primary promoter. The registry only matches exact strings, not substrings or abbreviated forms.

3. **Email and Phone detection appears comprehensive** — no obvious misses found.

4. **Address detection works well for Indian addresses with PIN codes** — 36 unique addresses is strong.

5. **Organization boundary handling needs work** — compound entities, prefix noise, and case/tab duplicates.

6. **The "100% benchmark" is confirmed irrelevant** — the actual document reveals significant gaps the 14-example benchmark cannot measure.

7. **No precision/recall/F1 is claimed.** These findings are observational, not statistically validated against ground truth.
