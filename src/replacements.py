from __future__ import annotations
import hashlib
import re
from .models import PIIType

FIRST_NAMES=["Aarav","Adrian","Alex","Anika","Arjun","Daniel","Elena","Ethan","Isha","Jordan","Karan","Maya","Nora","Rhea","Ryan","Sara","Sofia","Vikram","Zara"]
LAST_NAMES=["Anderson","Bennett","Carter","Davis","Evans","Foster","Garcia","Hughes","Kapoor","Morgan","Parker","Reed","Shah","Singh","Turner","Walker","Wilson","Young"]
ORG_PREFIX=["Meridian","Northstar","Pioneer","Summit","Bluecrest","Silverline","Vertex","Oakridge","Evergreen","Atlas"]
ORG_SUFFIX=["Industries Limited","Technologies Private Limited","Advisory LLP","Holdings Limited","Industrial Services Limited","Infrastructure Private Limited"]

class ReplacementGenerator:
    def __init__(self):
        self.by_type: dict[PIIType,dict[str,str]]={t:{} for t in PIIType}

    def _index(self, original:str, salt:str)->int:
        return int(hashlib.sha256((salt+"|"+original.lower()).encode()).hexdigest()[:8],16)

    def generate(self, original:str, pii_type:PIIType)->str:
        if original in self.by_type[pii_type]: return self.by_type[pii_type][original]
        i=self._index(original,pii_type.value)
        if pii_type==PIIType.PERSON:
            value=f"{FIRST_NAMES[i%len(FIRST_NAMES)]} {LAST_NAMES[(i//len(FIRST_NAMES))%len(LAST_NAMES)]}"
        elif pii_type==PIIType.EMAIL:
            value=f"{FIRST_NAMES[i%len(FIRST_NAMES)].lower()}.{LAST_NAMES[(i//len(FIRST_NAMES))%len(LAST_NAMES)].lower()}@example.com"
        elif pii_type==PIIType.PHONE:
            value=f"+91 {10+(i%90):02d} {1000+(i//90%9000):04d} {1000+(i//(90*9000)%9000):04d}"
        elif pii_type==PIIType.ORGANIZATION:
            value=f"{ORG_PREFIX[i%len(ORG_PREFIX)]} {ORG_SUFFIX[(i//len(ORG_PREFIX))%len(ORG_SUFFIX)]}"
        elif pii_type==PIIType.ADDRESS:
            value=f"{10+(i%89)} Example Industrial Estate, Sector {1+(i%30)}, Pune – {400000+(i%999):06d}, Maharashtra, India"
        elif pii_type==PIIType.SSN:
            value=f"{100+(i%899):03d}-{10+(i//899%89):02d}-{1000+(i//(899*89)%8999):04d}"
        elif pii_type==PIIType.CREDIT_CARD:
            # Deterministic Visa-style number, then fix check digit.
            digits="4"+f"{i%10**14:014d}"
            body=digits[:15]
            total=0
            rev=list(map(int,body[::-1]))
            for pos,d in enumerate(rev):
                if pos%2==0:
                    d*=2
                    if d>9:d-=9
                total+=d
            value=body+str((-total)%10)
            value=" ".join([value[:4],value[4:8],value[8:12],value[12:]])
        elif pii_type==PIIType.DOB:
            year=1970+(i%30); month=1+(i%12); day=1+(i%27)
            value=f"{day:02d}/{month:02d}/{year}"
        elif pii_type==PIIType.IP_ADDRESS:
            value=f"192.0.2.{1+(i%254)}"
        else:
            value="[REDACTED]"
        self.by_type[pii_type][original]=value
        return value
