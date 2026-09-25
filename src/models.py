from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class PIIType(str, Enum):
    PERSON = "PERSON"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    ORGANIZATION = "ORGANIZATION"
    ADDRESS = "ADDRESS"
    SSN = "SSN"
    CREDIT_CARD = "CREDIT_CARD"
    DOB = "DOB"
    IP_ADDRESS = "IP_ADDRESS"

@dataclass(frozen=True)
class Span:
    start: int
    end: int
    text: str
    pii_type: PIIType
    confidence: float = 1.0
    source: str = "rule"
    field_id: Optional[str] = None
    canonical_text: Optional[str] = None

@dataclass
class DetectionResult:
    spans: list[Span] = field(default_factory=list)
    stats: dict[str, int] = field(default_factory=dict)

    def add(self, span: Span) -> None:
        self.spans.append(span)
