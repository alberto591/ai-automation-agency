import pytest
from unittest.mock import patch, MagicMock
from lead_manager import get_valuation_report

@patch("lead_manager.supabase")
@patch("market_service.get_live_market_price")
def test_valuation_tuscany_postcode_resolution(mock_live_price, mock_supabase):
    """Verify that Tuscany postcodes resolve to correct zones (fixing the Milano fallback bug)."""
    # Mock internal DB to return nothing so it falls through to zone logic
    mock_supabase.table.return_value.select.return_value.ilike.return_value.execute.return_value = MagicMock(data=[])
    mock_live_price.return_value = None # No live price either
    
    # Test Figline postcode
    report = get_valuation_report("Via Roma 1", postcode="50063")
    assert "VALUTAZIONE ISTANTANEA AI" in report
    assert "FIGLINE E INCISA VALDARNO" in report
    
    # Test Firenze prefix
    report = get_valuation_report("Via dei Serragli 10", postcode="50124")
    assert "FIRENZE" in report

@patch("lead_manager.supabase")
@patch("market_service.get_live_market_price")
def test_valuation_tuscany_address_extraction(mock_live_price, mock_supabase):
    """Verify extraction of multi-word zone from address string."""
    mock_supabase.table.return_value.select.return_value.ilike.return_value.execute.return_value = MagicMock(data=[])
    mock_live_price.return_value = None
    
    # Explicit address match
    report = get_valuation_report("Appartamento a Forte dei Marmi, Via Italica")
    assert "FORTE DEI MARMI" in report
    
    # ZIP extraction from string
    report = get_valuation_report("Via Roma 1, 53100")
    assert "SIENA" in report

@patch("lead_manager.supabase")
@patch("market_service.get_live_market_price")
def test_valuation_milano_fallback(mock_live_price, mock_supabase):
    """Verify default fallback to Milano for unknown areas."""
    mock_supabase.table.return_value.select.return_value.ilike.return_value.execute.return_value = MagicMock(data=[])
    mock_live_price.return_value = None
    
    report = get_valuation_report("Indirizzo Sconosciuto")
    assert "MILANO" in report
