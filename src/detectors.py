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
    
    ADDRESS_PREFIX_STRIP = re.compile(
        r'^(?:The\s+|Our\s+)?(?:registered\s+office|corporate\s+office|manufacturing\s+facility|address)\s*'
        r'(?:of\s+(?:our\s+)?Company\s+)?'
        r'(?:is\s+)?(?:located\s+)?(?:at)?\s*[:\-]?\s*', re.I)
        
    ADDRESS_LABEL_RE = re.compile(
        r'\b(?:Registered\s+Office|Corporate\s+Office|Manufacturing\s+Facility|Mailing\s+Address|Address)\s*(?:of\s+(?:our\s+)?Company\s+)?'
        r'(?:\s*[:\-\n]\s*|\s+(?:is\s+)?(?:located|situated)\s+at\s+)',
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
            start=window_start+idx+len(marker)
        else:
            start=None
        if start is None:
            # Fall back to the latest sentence/line boundary in the local window.
            candidates=[prefix.rfind(x) for x in (". ", "; ", "\n")]
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
        start = m.end()
        # skip if this is already inside a detected span
        if any(s.start <= start <= s.end for s in spans):
            continue
            
        window = text[start:start+250]
        stop_re = re.compile(r'(?:;|\.\s|\n\n|\n?(?:Telephone|Tel|Phone|E-mail|Email|Website|Contact Person)\b)', re.I)
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
    for m in PERSON_CONTEXT_RE.finditer(text):
        for group_index in (1,2):
            candidate=m.group(group_index)
            if not candidate: continue
            candidate=candidate.strip(" ,;:()")
            if candidate.lower() in generic: continue
            if len(candidate.split()) < 2: continue
            spans.append(Span(m.start(group_index),m.end(group_index),candidate,PIIType.PERSON,0.93,"high-confidence-context"))

    # High-confidence first-page promoter heading. Later occurrences can be
    # redacted through the global entity registry once these names are known.
    for marker in re.finditer(r"OUR\s+PROMOTERS\s*:", text):
        tail=text[marker.end():marker.end()+550]
        for nm in re.finditer(r"(?:\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){2,3}\b|\b[A-Z]{2,}(?:\s+[A-Z]{2,}){2,3}\b)", tail):
            candidate=nm.group()
            if any(x in candidate.lower() for x in ("family trust","private limited","industrial park")): continue
            spans.append(Span(marker.end()+nm.start(),marker.end()+nm.end(),candidate,PIIType.PERSON,0.95,"promoter-heading"))
    for m in PERSON_TITLE_LIST_RE.finditer(text):
        candidate=m.group(1).strip()
        spans.append(Span(m.start(1),m.end(1),candidate,PIIType.PERSON,0.91,"title-list"))
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
