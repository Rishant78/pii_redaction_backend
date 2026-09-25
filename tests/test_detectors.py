from src.detectors import detect_all
from src.models import PIIType

def types(text):
    return [(s.text,s.pii_type) for s in detect_all(text)]

def has(text, value, pii_type):
    return any(v == value and t == pii_type for v,t in types(text))

def test_email():
    assert has('Email: rashi.patil@example.com','rashi.patil@example.com',PIIType.EMAIL)

def test_phone():
    assert has('Telephone: +91 98765 43210','+91 98765 43210',PIIType.PHONE)

def test_ssn():
    assert has('SSN: 123-45-6789','123-45-6789',PIIType.SSN)

def test_credit_card():
    assert has('Card: 4111 1111 1111 1111','4111 1111 1111 1111',PIIType.CREDIT_CARD)

def test_ip():
    assert has('Server IP: 192.0.2.44','192.0.2.44',PIIType.IP_ADDRESS)

def test_dob_context():
    assert has('Date of Birth: 19 July 2004','19 July 2004',PIIType.DOB)

def test_person_context():
    assert has('Contact Person: Aarav Mehta','Aarav Mehta',PIIType.PERSON)

def test_org():
    assert has('Company: Meridian Technologies Private Limited','Meridian Technologies Private Limited',PIIType.ORGANIZATION)

def test_does_not_redact_generic_date():
    assert not any(t==PIIType.DOB for _,t in types('The offer closes on December 18, 2025.'))

def test_compound_organization_splitting():
    res = types('BSE Limited and National Stock Exchange of India Limited')
    assert ('BSE Limited', PIIType.ORGANIZATION) in res
    assert ('National Stock Exchange of India Limited', PIIType.ORGANIZATION) in res
    assert not any('and' in s[0].lower() for s in res)

def test_organization_role_prefix():
    res = types('Offer Escrow Collection Bank HDFC Bank Limited')
    assert ('HDFC Bank Limited', PIIType.ORGANIZATION) in res
    assert not any('Offer' in s[0] for s in res)

def test_organization_historical_prefix():
    res = types('Formerly Link Intime India Private Limited')
    assert ('Link Intime India Private Limited', PIIType.ORGANIZATION) in res
    assert not any('Formerly' in s[0] for s in res)

def test_normal_phrase_not_organization():
    res = types('The Quick Brown Fox and the Lazy Dog')
    assert not any(t == PIIType.ORGANIZATION for _, t in res)

def test_suffix_only_false_positives_ignored():
    res = types('the company is a Private Limited company')
    assert not any(t == PIIType.ORGANIZATION for _, t in res)
    res2 = types('registered in India Limited')
    assert not any(t == PIIType.ORGANIZATION for _, t in res2)
    res3 = types('a Public Limited corporation')
    assert not any(t == PIIType.ORGANIZATION for _, t in res3)

# --- ADDRESS TESTS ---

def test_address_with_pin():
    # Ordinary pin-based
    assert has('123 Fake Street, Mumbai - 400 001, Maharashtra, India', '123 Fake Street, Mumbai - 400 001, Maharashtra, India', PIIType.ADDRESS)

def test_address_strips_prose_prefix():
    res = types('Our manufacturing facility located at 123 Fake Street, Mumbai - 400 001, Maharashtra, India')
    assert has('Our manufacturing facility located at 123 Fake Street, Mumbai - 400 001, Maharashtra, India', '123 Fake Street, Mumbai - 400 001, Maharashtra, India', PIIType.ADDRESS)
    assert not has('Our manufacturing facility located at 123 Fake Street, Mumbai - 400 001, Maharashtra, India', 'Our manufacturing facility located at 123 Fake Street, Mumbai - 400 001, Maharashtra, India', PIIType.ADDRESS)

def test_address_no_pin_with_label():
    text = 'Registered Office: 12 Buena Monte, NCL co-operative housing society, Panchvati, Pashan, Pune. Telephone: 123'
    # Should find the address and stop at ". Telephone"
    assert has(text, '12 Buena Monte, NCL co-operative housing society, Panchvati, Pashan, Pune', PIIType.ADDRESS)

def test_address_strips_organization():
    text = 'ICICI Securities Limited 123 Fake Street, Mumbai - 400 001'
    # Org is "ICICI Securities Limited", Address is the rest
    res = types(text)
    assert ('ICICI Securities Limited', PIIType.ORGANIZATION) in res
    assert ('123 Fake Street, Mumbai - 400 001', PIIType.ADDRESS) in res
    assert not any(t == PIIType.ADDRESS and 'ICICI Securities Limited' in v for v, t in res)

def test_address_negative_prose():
    text = 'We plan to expand our operations in Mumbai and Pune by next year.'
    # Has locations "Mumbai" and "Pune" but no address indicators
    res = types(text)
    assert not any(t == PIIType.ADDRESS for _, t in res)

def test_organization_greedy_suffix_matching():
    # Suffixes should be greedily matched to avoid leaving trailing duplicates
    res = types('Hindalco Industries Limited')
    assert ('Hindalco Industries Limited', PIIType.ORGANIZATION) in res
    assert not any(v == 'Hindalco Industries' for v, t in res)
    
    res2 = types('Vertex Advisory LLP Limited Limited Limited')
    assert ('Vertex Advisory LLP Limited Limited Limited', PIIType.ORGANIZATION) in res2
    assert not any(v == 'Vertex Advisory LLP' for v, t in res2)
    
    res3 = types('XYZ Technologies Private Limited Limited')
    assert ('XYZ Technologies Private Limited Limited', PIIType.ORGANIZATION) in res3
    assert not any(v == 'XYZ Technologies' for v, t in res3)
