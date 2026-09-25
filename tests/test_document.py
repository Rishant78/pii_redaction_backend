import pytest
from docx import Document
from src.document import discover_entities, generate_person_aliases, iter_paragraphs, generate_org_aliases
from src.models import PIIType

def test_generate_person_aliases():
    assert generate_person_aliases("Kushal Subbayya Hegde") == ["Kushal Hegde"]
    assert generate_person_aliases("Rajesh Kushal Hegde") == ["Rajesh Hegde"]
    assert generate_person_aliases("Amod Joshi") == []
    assert generate_person_aliases("A B C D") == ["A D"]
    assert generate_person_aliases("kushal subbayya hegde") == []

def test_generate_org_aliases():
    # Suffix omitting
    assert "KSH International" in generate_org_aliases("KSH International Limited")
    # Whitespace normalization
    assert "HDFC Bank Limited" in generate_org_aliases("HDFC   Bank\tLimited")
    # Don't drop suffix if < 2 words remain
    assert "BSE" not in generate_org_aliases("BSE Limited")

def create_doc_with_paragraphs(texts):
    doc = Document()
    for t in texts:
        doc.add_paragraph(t)
    return doc

def test_discover_entities_full_and_short_names():
    doc = create_doc_with_paragraphs([
        "Contact Person: Kushal Subbayya Hegde",
    ])
    registry = discover_entities(doc)
    assert registry[(PIIType.PERSON.value, "Kushal Subbayya Hegde")] == "Kushal Subbayya Hegde"
    assert registry[(PIIType.PERSON.value, "Kushal Hegde")] == "Kushal Subbayya Hegde"

def test_ambiguous_short_name_not_automatically_matched():
    doc = create_doc_with_paragraphs([
        "Contact Person: Rajesh Kushal Hegde",
        "Contact Person: Rajesh Ramesh Hegde",
    ])
    registry = discover_entities(doc)
    assert registry[(PIIType.PERSON.value, "Rajesh Kushal Hegde")] == "Rajesh Kushal Hegde"
    assert registry[(PIIType.PERSON.value, "Rajesh Ramesh Hegde")] == "Rajesh Ramesh Hegde"
    assert (PIIType.PERSON.value, "Rajesh Hegde") not in registry

def test_unrelated_surname_not_matched():
    aliases = generate_person_aliases("Kushal Subbayya Hegde")
    assert "Hegde" not in aliases
    assert "Kushal" not in aliases

def test_case_and_whitespace_variation_in_regex():
    import re
    from src.models import Span
    
    doc = create_doc_with_paragraphs([
        "Contact Person: Kushal Subbayya Hegde"
    ])
    registry = discover_entities(doc)
    text = "We met with kushal  hegde today."
    spans = []
    for (type_name, lookup_string), canonical in registry.items():
        if type_name == PIIType.PERSON.value:
            pattern_parts = [re.escape(w) for w in lookup_string.split()]
            pattern = r'\b' + r'\s+'.join(pattern_parts) + r'\b'
        else:
            pattern = re.escape(lookup_string)
        
        for match in re.finditer(pattern, text, re.I):
            spans.append(Span(match.start(), match.end(), match.group(), PIIType(type_name), 1.0, "entity-registry", canonical_text=canonical))
            
    assert len(spans) == 1
    assert spans[0].text == "kushal  hegde"
    assert spans[0].canonical_text == "Kushal Subbayya Hegde"

def test_organization_canonical_normalization():
    # Should normalize case and whitespace
    doc = create_doc_with_paragraphs([
        "Company: HDFC   Bank\tLimited",
    ])
    registry = discover_entities(doc)
    # The canonical entry should be properly normalized/title-cased
    canonical = registry.get((PIIType.ORGANIZATION.value, "HDFC   Bank\tLimited"))
    assert canonical == "Hdfc Bank Limited"
    # The generated alias (without suffix) should map to the same canonical
    assert registry.get((PIIType.ORGANIZATION.value, "Hdfc Bank")) == "Hdfc Bank Limited"
