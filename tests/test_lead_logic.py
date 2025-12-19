import pytest
from unittest.mock import MagicMock
from lead_manager import get_market_context, get_valuation_report, handle_incoming_message

def test_get_market_context_success(mock_external_services):
    """Verify that market context is correctly averaged from Supabase data."""
    supabase = mock_external_services["supabase"]
    
    # Mock return data for 'Navigli' zone
    mock_data = [
        {"price_per_mq": 5000},
        {"price_per_mq": 6000}
    ]
    supabase.table.return_value.select.return_value.ilike.return_value.execute.return_value = MagicMock(data=mock_data)
    
    context = get_market_context("Navigli")
    
    assert "ZONA NAVIGLI" in context
    assert "€5500/mq" in context # Average of 5000 and 6000

def test_get_market_context_no_data(mock_external_services):
    """Verify that empty result is returned when no market data exists."""
    supabase = mock_external_services["supabase"]
    supabase.table.return_value.select.return_value.ilike.return_value.execute.return_value = MagicMock(data=[])
    
    context = get_market_context("Mars")
    assert context == ""

def test_get_valuation_report_success(mock_external_services):
    """Verify that valuation report calculates the +/- 7% range correctly."""
    supabase = mock_external_services["supabase"]
    
    # Mock market context for the zone
    mock_data = [{"price_per_mq": 10000}]
    supabase.table.return_value.select.return_value.ilike.return_value.execute.return_value = MagicMock(data=mock_data)
    
    report = get_valuation_report("Via Dante 10, Brera")
    
    assert "VALUTAZIONE AI COMPLETATA" in report
    assert "€9300/mq" in report # 10000 - 7%
    assert "€10700/mq" in report # 10000 + 7%

def test_handle_incoming_message_valuation_trigger(mock_external_services):
    """Verify that handle_incoming_message detects appraisal requests."""
    supabase = mock_external_services["supabase"]
    
    # Mock market data for the trigger
    mock_data = [{"price_per_mq": 5000}]
    supabase.table.return_value.select.return_value.ilike.return_value.execute.return_value = MagicMock(data=mock_data)
    
    # Mock history and search
    supabase.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = MagicMock(data=[])
    
    msg = "RICHIESTA VALUTAZIONE: Navigli 1, Milano"
    response = handle_incoming_message("+39333000000", msg)
    
    assert "VALUTAZIONE AI COMPLETATA" in response
    assert "NAVIGLI" in response
