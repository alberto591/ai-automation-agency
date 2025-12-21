import pytest
from lead_manager import fuzzy_keyword_match, TIER1_TAKEOVER_KEYWORDS, TIER2_ALERT_KEYWORDS

def test_fuzzy_match_exact():
    """Exact keyword match."""
    assert fuzzy_keyword_match("Voglio parlare con un umano", TIER1_TAKEOVER_KEYWORDS) is True
    assert fuzzy_keyword_match("Cerco uno sconto immediato", TIER2_ALERT_KEYWORDS) is True

def test_fuzzy_match_synonym():
    """Synonym keyword match (persona -> umano)."""
    assert fuzzy_keyword_match("Vorrei parlare con una persona reale", TIER1_TAKEOVER_KEYWORDS) is True
    assert fuzzy_keyword_match("C'è qualcuno dello staff?", TIER1_TAKEOVER_KEYWORDS) is True

def test_fuzzy_match_typo():
    """Fuzzy match with a slight typo (umanoo)."""
    # 'umanoo' vs 'umano' is 5/6 = 83.3% ratio. Threshold is 80.
    assert fuzzy_keyword_match("Voglio un umanoo", TIER1_TAKEOVER_KEYWORDS) is True

def test_fuzzy_match_substring():
    """Substring match should work if it's within a word."""
    # 'staff' in 'staffetta' (Wait, but we split by words? 
    # Actually fuzzy_keyword_match uses `if keyword_lower in text_lower` FIRST)
    assert fuzzy_keyword_match("Chiamo lo backstage", ["back"]) is True # Substring match

def test_fuzzy_match_noise_exclusion():
    """Should NOT match very short words or unrelated words with low score."""
    assert fuzzy_keyword_match("Lo", ["Lavoro"]) is False # Too short
    assert fuzzy_keyword_match("Cacao", ["Cassa"]) is False # Under threshold

def test_fuzzy_match_case_insensitive():
    """Should be case insensitive."""
    assert fuzzy_keyword_match("UMANO", TIER1_TAKEOVER_KEYWORDS) is True
    assert fuzzy_keyword_match("sCoNtO", TIER2_ALERT_KEYWORDS) is True

def test_fuzzy_match_empty_input():
    """Handle empty or None input gracefully."""
    assert fuzzy_keyword_match("", TIER1_TAKEOVER_KEYWORDS) is False
    assert fuzzy_keyword_match(None, TIER1_TAKEOVER_KEYWORDS) is False
