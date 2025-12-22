import csv
import os
from unittest.mock import patch

from market_scraper import save_to_market_data, scrape_immobiliare

from agency_outreach import generate_outreach_csv


def test_scrape_immobiliare_parsing():
    """Verify that Immobiliare scraper correctly extracts data from mock HTML."""
    mock_html = """
    <html>
        <div class="nd-list__item nd-list__item--main nd-list__item--price">€ 500.000</div>
        <li aria_label="superficie">100 m²</li>
        <h1 class="nd-title">Bellissimo Attico</h1>
        <span class="nd-title__sub-title">Zona Navigli, Milano</span>
    </html>
    """

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = mock_html

        data = scrape_immobiliare("https://www.immobiliare.it/test")

        assert data["price"] == 500000
        assert data["sqm"] == 100
        assert data["price_per_mq"] == 5000
        assert "Navigli" in data["zone"]


def test_agency_outreach_csv_generation(tmp_path):
    """Verify that the outreach script generates a valid CSV file."""
    mock_agencies = [
        {"name": "Test Agency", "phone": "+39000", "address": "Via Test 1", "city": "Milano"}
    ]

    test_file = tmp_path / "test_outreach.csv"
    generate_outreach_csv(mock_agencies, filename=str(test_file))

    assert os.path.exists(test_file)

    with open(test_file, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["name"] == "Test Agency"
        assert "Milano" in rows[0]["city"]


def test_save_to_market_data_upsert(mock_external_services):
    """Verify that scraper calls Supabase upsert correctly."""
    supabase = mock_external_services["scraper_supabase"]

    dummy_data = {
        "portal_url": "test.com",
        "title": "Test",
        "price": 100,
        "sqm": 10,
        "price_per_mq": 10,
        "zone": "Test",
        "city": "Test",
    }

    save_to_market_data(dummy_data)
    supabase.table.return_value.upsert.assert_called_with(dummy_data, on_conflict="portal_url")
