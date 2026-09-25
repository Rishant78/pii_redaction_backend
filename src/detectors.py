from __future__ import annotations
import re
from typing import Iterable
from .models import Span, PIIType

EMAIL_RE = re.compile(r"(?<![\w.+-])([A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)(?![\w.-])")
IP_RE = re.compile(r"(?<![\w.])(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)(?![\w.])")
SSN_RE = re.compile(r"(?<!\d)(\d{3}-\d{2}-\d{4})(?!\d)")
CC_RE = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")
PHONE_RE = re.compile(r"(?<![\w])(?:\+\s?\d{1,3}[\s.-]?)?(?:\(?\d{2,5}\)?[\s.-]?)?\d{3,5}[\s.-]?\d{3,5}(?![\d])")
DATE_RE = re.compile(r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s*,?\s+\d{4}|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},?\s+\d{4})\b", re.I)
PIN_RE = re.compile(r"\b[1-9]\d{2}\s?\d{3}\b")

CORP_SUFFIX_RE = re.compile(r"\b[A-Z][A-Za-z0-9&’/-]*(?:\s+(?:[A-Z][A-Za-z0-9&’/-]*|and|of|the)){0,9}?(?:\s+(?i:Limited|Ltd\.?|Private Limited|Pvt\.?\s+Ltd\.?|LLP|L\.L\.P\.|Corporation|Inc\.?|Incorporated|Holdings|Industries))+\b")
TRUST_RE = re.compile(r"\b(?:[A-Z][A-Za-z0-9&.'’/-]*\s+){0,8}Family Trust\b")

PERSON_CONTEXT_RE = re.compile(
    r"Contact\s+Person\s*[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})(?=\s*(?:Company|Telephone|Tel|Email|Website|SEBI|,|$))|"
    r"(?:Chairman\s+and\s+Executive\s+Director|Chief\s+Executive\s+Officer|Chief\s+Financial\s+Officer|Company\s+Secretary|Managing\s+Director|Joint\s+Managing\s+Director|Whole-time\s+Director|Independent\s+Chartered\s+Engineer|Technical\s+Director|CEO|CFO|CS)[^.;\n]{0,140}?\b(?:being|namely)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",
    re.I,
)

PERSON_TITLE_LIST_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})(?=\s*,\s*(?:CEO|CFO|CS|Technical\s+Director|Director)\b)")


# Conservative title/name pattern. It is intentionally not applied globally.
NAME_RE = re.compile(r"\b[A-Z][a-z]{1,30}(?:\s+[A-Z][a-z]{1,30}){1,4}\b")

ADDRESS_HINTS = re.compile(r"\b(?:road|marg|street|lane|complex|tower|building|bldg|floor|wing|plot|village|taluka|taluka-khed|district|industrial area|phase|sector|park|estate|nagar|peth|opp(?:osite)?|near|mumbai|pune|maharashtra|india)\b", re.I)
DOB_CONTEXT_RE = re.compile(r"(?:date\s+of\s+birth|dob|born\s+on|birth\s+date)\s*[:\-]?\s*", re.I)


def luhn_valid(number: str) -> bool:
    digits = [int(c) for c in number if c.isdigit()]
    if not 13 <= len(digits) <= 19:
        return False
    checksum = 0
    parity = len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


def _span_matches(pattern, text: str, pii_type: PIIType, confidence=1.0, source="regex") -> list[Span]:
    return [Span(m.start(1) if m.lastindex else m.start(), m.end(1) if m.lastindex else m.end(), m.group(1) if m.lastindex else m.group(), pii_type, confidence, source) for m in pattern.finditer(text)]


def detect_structured(text: str) -> list[Span]:
    spans: list[Span] = []
    spans += _span_matches(EMAIL_RE, text, PIIType.EMAIL)
    spans += _span_matches(IP_RE, text, PIIType.IP_ADDRESS)
    spans += _span_matches(SSN_RE, text, PIIType.SSN)

    for m in CC_RE.finditer(text):
        raw = m.group().strip()
        digits = ''.join(c for c in raw if c.isdigit())
        if luhn_valid(digits):
            spans.append(Span(m.start(), m.end(), raw, PIIType.CREDIT_CARD, 0.99, "luhn"))

    for m in PHONE_RE.finditer(text):
        raw = m.group().strip(" .,-")
        digits = ''.join(c for c in raw if c.isdigit())
        # Avoid years, financial values, page numbers and ordinary short numbers.
        if 10 <= len(digits) <= 15 and not (len(digits) == 10 and digits.startswith(("0000", "1111", "9999"))):
            context = text[max(0, m.start()-25):min(len(text), m.end()+25)].lower()
            confidence = 0.98 if any(k in context for k in ("tel", "telephone", "phone", "mobile", "contact")) else 0.80
            if confidence >= 0.80:
                spans.append(Span(m.start(), m.end(), raw, PIIType.PHONE, confidence, "phone-regex"))

    # DOB is contextual: ordinary dates are NOT redacted.
    for cm in DOB_CONTEXT_RE.finditer(text):
        dm = DATE_RE.search(text, cm.end(), min(len(text), cm.end()+80))
        if dm:
            spans.append(Span(dm.start(), dm.end(), dm.group(), PIIType.DOB, 0.99, "dob-context"))
    return spans


def detect_addresses(text: str) -> list[Span]:
    spans=[]
    if len(text.strip()) < 150 and ADDRESS_HINTS.search(text):
        if re.match(r'^\s*(?:[1-9][0-9]{0,3}[a-zA-Z]?/[0-9a-zA-Z]+|[1-9][0-9]{0,3}[a-zA-Z]?)\b', text):
            spans.append(Span(0, len(text), text.strip(), PIIType.ADDRESS, 0.85, "short-isolated-address"))

    ADDRESS_PREFIX_STRIP = re.compile(
        r'^(?:The\s+|Our\s+)?(?:registered\s+office|corporate\s+office|manufacturing\s+facility|address)\s*'
        r'(?:of\s+(?:our\s+)?Company\s+)?'
        r'(?:is\s+)?(?:located\s+)?(?:at)?\s*[:\-]?\s*', re.I)
        
    ADDRESS_LABEL_RE = re.compile(
        r'\b(?:(?:Registered\s+Office|Corporate\s+Office|Manufacturing\s+Facility|Mailing\s+Address|Address)\s*(?:of\s+(?:our\s+)?Company\s+)?(?:\s*[:\-\n]\s*|\s+(?:is\s+)?(?:located|situated)\s+at\s+|\s+at\s+)'
        r'|(?:Gat\s+No\.|Plot\s+No\.|Flat\s+No\.|House\s+No\.|Survey\s+No\.|Door\s+No\.)\s+)',
        re.I
    )

    markers=(
        "Registered Office at", "Corporate Office at", "Registered Office:", "Corporate Office:",
        "Address:", "address:", "Office:", "Gat No.", "Plot No.", "Flat No.", "House No.", "Survey No.", "Door No."
    )
    
    # 1. PIN-based fallback logic
    for m in PIN_RE.finditer(text):
        window_start=max(0,m.start()-350)
        prefix=text[window_start:m.end()]
        marker_hits=[]
        for marker in markers:
            idx=prefix.lower().rfind(marker.lower())
            if idx>=0:
                marker_hits.append((idx, marker))
        if marker_hits:
            idx, marker=max(marker_hits, key=lambda x:x[0])
            if marker.lower() in ("gat no.", "plot no.", "flat no.", "house no.", "survey no.", "door no."):
                start=window_start+idx
            else:
                start=window_start+idx+len(marker)
        else:
            start=None
        if start is None:
            # Fall back to the latest sentence/line boundary in the local window.
            candidates=[prefix.rfind(x) for x in (". ", "; ", "\n\n", ".\n")]
            boundary=max(candidates)
            start=window_start+boundary+2 if boundary>=0 else window_start
            
        end=m.end()
        tail=text[end:min(len(text),end+70)]
        stop=re.search(r"(?:;|\b(?:Telephone|Tel|Phone|E-mail|Email|Website|Contact Person|Contact person|Corporate Office|Registered Office)\b)", tail, re.I)
        extension=tail[:stop.start()] if stop else tail
        # Only extend through a plausible address tail; avoid swallowing arbitrary prose.
        mext=re.match(r"^\s*,\s*(?:Maharashtra|Karnataka|Gujarat|Delhi|Rajasthan|Uttar Pradesh|Tamil Nadu|Telangana|Kerala|West Bengal|Andhra Pradesh|Madhya Pradesh|Haryana|Punjab|India)(?:\s*,\s*(?:India))?", extension, re.I)
        if mext:
            end += len(mext.group())
            
        candidate=text[start:end].strip(" ,;:-")
        
        # Strip prose prefixes
        prefix_m = ADDRESS_PREFIX_STRIP.match(candidate)
        if prefix_m:
            candidate = candidate[prefix_m.end():].lstrip(" ,;:-")
            
        # Strip leading organization names to prevent absorption
        org_m = CORP_SUFFIX_RE.match(candidate)
        if org_m:
            candidate = candidate[org_m.end():].lstrip(" ,;:-")
            
        actual_start = text.rfind(candidate, start, end)
        
        if actual_start >= 0 and len(candidate)>=15 and ADDRESS_HINTS.search(candidate):
            spans.append(Span(actual_start,actual_start+len(candidate),candidate,PIIType.ADDRESS,0.94,"pin+address-hints"))
            
    # 2. No-PIN Label-based logic
    for m in ADDRESS_LABEL_RE.finditer(text):
        label = m.group()
        if re.search(r'\b(?:Gat|Plot|Flat|House|Survey|Door)\b', label, re.I):
            start = m.start()
        else:
            start = m.end()
            
        # skip if this is already inside a detected span
        if any(s.start <= start <= s.end for s in spans):
            continue
            
        window = text[start:start+250]
        stop_re = re.compile(r'(?:;|(?<!\bNo)\.\s|\n\n|\n?(?:Telephone|Tel|Phone|E-mail|Email|Website|Contact Person)\b)', re.I)
        stop_m = stop_re.search(window)
        if stop_m:
            end = start + stop_m.start()
        else:
            end = start + len(window)
            
        candidate = text[start:end].strip(" ,;:-")
        
        org_m = CORP_SUFFIX_RE.match(candidate)
        if org_m:
            candidate = candidate[org_m.end():].lstrip(" ,;:-")
            
        actual_start = text.rfind(candidate, start, end)
        if actual_start >= 0 and len(candidate)>=15 and ADDRESS_HINTS.search(candidate) and not PIN_RE.search(candidate):
            spans.append(Span(actual_start,actual_start+len(candidate),candidate,PIIType.ADDRESS,0.90,"label-context"))
            
    return spans


def detect_organizations(text: str) -> list[Span]:
    spans=[]
    BAD_PREFIXES = re.compile(r"^(?:Formerly|Offer\s+Escrow\s+Collection\s+Bank|Escrow\s+Collection\s+Bank|Sponsor\s+Bank|Refund\s+Bank|Syndicate\s+Member|Lead\s+Manager|BRLM|Registrar)\s+", re.I)
    SUFFIX_PATTERN = re.compile(r'(?:\s+(?:Limited|Ltd\.?|Private Limited|Pvt\.?\s+Ltd\.?|LLP|L\.L\.P\.|Corporation|Inc\.?|Incorporated|Holdings|Industries))+$', re.I)
    
    for pattern in (CORP_SUFFIX_RE, TRUST_RE):
        for m in pattern.finditer(text):
            start = m.start()
            val = m.group()
            
            while val and val[0] in " ,;:()":
                val = val[1:]
                start += 1
            while val and val[-1] in " ,;:()":
                val = val[:-1]
                
            while True:
                prefix_match = BAD_PREFIXES.match(val)
                if prefix_match:
                    length = len(prefix_match.group())
                    val = val[length:]
                    start += length
                else:
                    break
                    
            normalized=re.sub(r"\s+"," ",val).strip().lower()
            if normalized in {"our company","the company","company"} or normalized.startswith("company ") or "family trust" in normalized:
                continue
                
            val_no_suffix = SUFFIX_PATTERN.sub('', val).strip()
            if not val_no_suffix or val_no_suffix.lower() in {"private", "public", "india", "the", "a", "an", "and", "of", "limited", "co", "co.", "ltd"}:
                continue
                
            if len(val)>=8 and len(val.split())>=2:
                spans.append(Span(start,start+len(val),val,PIIType.ORGANIZATION,0.88,"corporate-suffix"))
    return spans


def detect_contextual_people(text: str) -> list[Span]:
    spans=[]
    generic={
        "contact person","contact","promoter","promoters","promoter selling shareholders",
        "promoter group","selling shareholder","selling shareholders","company secretary",
        "compliance officer","chief executive officer","chief financial officer",
        "key managerial personnel","group companies","syndicate members","red herring prospectus",
        "other regulatory","statutory disclosures","materiality policy","companies act",
        "equity shares","equity share","offered shares","capital structure","company",
        "the company","our company","practicing company"
    }
    
    # Existing regex contexts
    for m in PERSON_CONTEXT_RE.finditer(text):
        for group_index in (1,2):
            candidate=m.group(group_index)
            if not candidate: continue
            candidate=candidate.strip(" ,;:()")
            if candidate.lower() in generic: continue
            if len(candidate.split()) < 2: continue
            spans.append(Span(m.start(group_index),m.end(group_index),candidate,PIIType.PERSON,0.93,"high-confidence-context"))

    # 1. Contact Person list context: Contact Person: Name 1 / Name 2
    for m in re.finditer(r"Contact\s+Person\s*[:\-]?\s*([^\n;.]+)", text, re.I):
        tail = m.group(1)
        for nm in NAME_RE.finditer(tail):
            c = nm.group()
            if c.lower() not in generic and len(c.split()) >= 2:
                spans.append(Span(m.start(1) + nm.start(), m.start(1) + nm.end(), c, PIIType.PERSON, 0.93, "contact-person-list"))

    # 2. Transfer of shares: transfer of shares (by|to|from) NAME
    for m in re.finditer(r"(?:transfer\s+of\s+(?:equity\s+)?shares\s+(?:by|to|from)|transferred\s+(?:by|to|from))\s+([^\n;.,]+)", text, re.I):
        tail = m.group(1)
        for nm in NAME_RE.finditer(tail):
            if any(x in nm.group().lower() for x in ("huf", "trust", "limited", "company", "group", "bank", "ltd", "pvt")): continue
            spans.append(Span(m.start(1) + nm.start(), m.start(1) + nm.end(), nm.group(), PIIType.PERSON, 0.93, "share-transfer"))

    # 3. Consent from: consent (dated ... )?from NAME
    for m in re.finditer(r"consent\s+(?:(?:letter\s+)?dated\s+[A-Za-z0-9\s,]+)?from\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})", text, re.I):
        spans.append(Span(m.start(1), m.end(1), m.group(1), PIIType.PERSON, 0.93, "consent-from"))

    # 4. "namely, NAME" or "being NAME"
    for m in re.finditer(r"\b(?:namely|being)\s*,?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})", text, re.I):
        if m.group(1).lower() not in generic:
            spans.append(Span(m.start(1), m.end(1), m.group(1), PIIType.PERSON, 0.93, "namely-being"))

    # 5. "Director", "Shareholder", "Promoter" list contexts:
    for m in re.finditer(r"\b(?:Promoters?|Shareholders?|Directors?|Members?|Founders?|Individuals?)\s*(?:are|:|include|,)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}(?:\s*(?:,|and|/)\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})*)", text, re.I):
        tail = m.group(1)
        for nm in NAME_RE.finditer(tail):
            spans.append(Span(m.start(1) + nm.start(), m.start(1) + nm.end(), nm.group(), PIIType.PERSON, 0.90, "role-list"))

    # High-confidence first-page promoter heading.
    for marker in re.finditer(r"OUR\s+PROMOTERS\s*:", text):
        tail=text[marker.end():marker.end()+550]
        for nm in re.finditer(r"(?:\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){2,3}\b|\b[A-Z]{2,}(?:\s+[A-Z]{2,}){2,3}\b)", tail):
            candidate=nm.group()
            if any(x in candidate.lower() for x in ("family trust","private limited","industrial park")): continue
            spans.append(Span(marker.end()+nm.start(),marker.end()+nm.end(),candidate,PIIType.PERSON,0.95,"promoter-heading"))
            
    for m in PERSON_TITLE_LIST_RE.finditer(text):
        candidate=m.group(1).strip()
        spans.append(Span(m.start(1),m.end(1),candidate,PIIType.PERSON,0.91,"title-list"))

    # 6. Isolated exact names in cells
    if NAME_RE.fullmatch(text):
        GENERIC_CELL_WORDS = {'The','Our','Your','Total','Amount','Rs','Rupees','Equity','Share','Face','Value','Issue','Price','Premium','Discount','Offer','Sale','Net','Gross','Company','Office','Corporate','Registered','Maharashtra','India','Private','Limited','Public','Trust','Huf','Bank','Group','Committee','Offender','Tension','Factor','Branch','Slip','Date','Obligations','Ratio','Restaurants','Advice','Agreement','Centres','Portion','Measures','Form','Kilometers','Policy','Engineer','Rate','Time','Day','Electricals','Current','Application','Fund','Agreements','Accounts','Director','Engine','Authority','Scheme','Estimates','Intermediaries','Pipeline','Resources','Motors','Incentives','Foundation','Fees','Authorization','Voltaic','Shareholders','Agency','Companies','Plan','Dollars','Yojana','Lot','Wires','Sector','Process','Facility','Goods','Cell','System','Act','Welfare','Commission','Directors','Duty','Locations','Government','Outlook','Trusts','Shareholder','Prospectus','Investor','Bidder','Statements','Details','Banks','Exchanges','Wheelers','Funds','Bill','Borrower','Defaulter','Entities','Task','Force','Gas','Monitoring','Members','Horsepower','Measure','Document','Kingdom','Account','Monetary','Laboratories','Vehicles', 'National', 'Central', 'High', 'Low', 'Continuous', 'Transposed', 'Conductors', 'Automated', 'Clearing', 'House', 'Identification', 'Number', 'Volume', 'Growth', 'Profit', 'After', 'Tax', 'Margin', 'Life', 'Insurance', 'Diesel', 'Generators', 'Standard', 'Magnet', 'Winding', 'Wire', 'Development', 'Finance', 'Institution', 'Promoter', 'Risk', 'Management', 'Fugitive', 'Economic', 'Electricity', 'Regulatory', 'Capacity', 'Utilization', 'Rajesh', 'Acknowledgement', 'Pricing', 'Renewable', 'Purchase', 'Fixed', 'Asset', 'Turnover', 'Designated', 'Quick', 'Service', 'Allotment', 'Underwriting', 'Bidding', 'Mutual', 'Stakeholders', 'Relationship', 'Graded', 'Surveillance', 'Revision', 'Circuit', 'Independent', 'Chartered', 'Compound', 'Annual', 'Indian', 'Working', 'Voltage', 'Anchor', 'Alternate', 'Investment', 'Free', 'Trade', 'Escrow', 'Managing', 'Combustion', 'Integrated', 'First', 'Revised', 'Infrastructure', 'Production', 'Linked', 'Advance', 'Fuel', 'Supply', 'Photo', 'Selling', 'International', 'Energy', 'United', 'States', 'Pradhan', 'Mantri', 'Awas', 'Bid', 'Syndicate', 'Power', 'Book', 'Building', 'Offered', 'Supa', 'Sangeeta', 'Export', 'Promotion', 'Capital', 'Advanced', 'Chemistry', 'Battery', 'Storage', 'Retail', 'Labour', 'Electrotechnical', 'Broker', 'Basic', 'Custom', 'Specified', 'State', 'Monetization', 'World', 'Financial', 'Reporting', 'Standards', 'Rakhi', 'Abridged', 'Rohit', 'Sunil', 'Parents', 'Revamped', 'Distribution', 'Restated', 'Brushless', 'Demographic', 'Sponsor', 'Three', 'Depositories', 'Fraudulent', 'Wilful', 'Education', 'Information', 'Automotive', 'Joint', 'Liquid', 'Propane', 'Second', 'Fractional', 'Additional', 'General', 'Four', 'Audit', 'Agreement', 'Refund', 'Factories', 'Specialised', 'Registrar'}
        words = set(text.split())
        if not words.intersection(GENERIC_CELL_WORDS) and len(words) >= 2:
            spans.append(Span(0, len(text), text, PIIType.PERSON, 0.90, "isolated-exact-name"))
            
    # Also catch "Sangeeta Ramprasad Rai, her spouse"
    for m in re.finditer(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}),\s+(?:her|his)\s+(?:spouse|children|husband|wife|son|daughter|brother|sister|father|mother)", text):
        spans.append(Span(m.start(1), m.end(1), m.group(1), PIIType.PERSON, 0.93, "spouse-relative"))

    return spans


def merge_and_resolve(spans: Iterable[Span]) -> list[Span]:
    # Keep highest-confidence span when overlaps occur. Prefer structured types over broad entities.
    priority={PIIType.EMAIL:100, PIIType.PHONE:95, PIIType.SSN:100, PIIType.CREDIT_CARD:100, PIIType.IP_ADDRESS:100, PIIType.DOB:98, PIIType.ADDRESS:90, PIIType.PERSON:70, PIIType.ORGANIZATION:60}
    ordered=sorted(spans,key=lambda s:(s.start,-(s.end-s.start),-priority[s.pii_type],-s.confidence))
    accepted=[]
    for s in ordered:
        overlap=False
        for a in accepted:
            if not (s.end<=a.start or s.start>=a.end):
                overlap=True
                break
        if not overlap:
            accepted.append(s)
    return sorted(accepted,key=lambda s:s.start)


def detect_all(text: str) -> list[Span]:
    spans=[]
    spans += detect_structured(text)
    spans += detect_addresses(text)
    spans += detect_organizations(text)
    spans += detect_contextual_people(text)
    return merge_and_resolve(spans)
