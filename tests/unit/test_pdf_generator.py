import os
import tempfile

import pytest

from infrastructure.ai_pdf_generator import PropertyPDFGenerator


class TestPropertyPDFGenerator:
    @pytest.fixture
    def generator(self):
        return PropertyPDFGenerator()

    @pytest.fixture
    def sample_appraisal_data(self):
        return {
            "address": "Via Roma 1, Milano",
            "predicted_value": 500000,
            "confidence_range": "EUR 480.000 - EUR 520.000",
            "confidence_level": 90,
            "features": {
                "sqm": 100,
                "bedrooms": 2,
                "bathrooms": 1,
                "condition": "Ottimo",
                "has_elevator": True,
                "has_balcony": False,
            },
            "investment_metrics": {
                "monthly_rent": 1500,
                "annual_rent": 18000,
                "cap_rate": 3.6,
                "roi_5_year": 25.0,
                "cash_on_cash_return": 10.5,
                "down_payment_20pct": 100000,
            },
            "comparables": [
                {"title": "Comp 1", "sale_price_eur": 490000, "sqm": 95},
                {"title": "Comp 2", "sale_price_eur": 510000, "sqm": 105},
            ],
        }

    def test_generate_appraisal_report(self, generator, sample_appraisal_data):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            output_path = tmp.name

        try:
            # Generate PDF
            result_path = generator.generate_appraisal_report(sample_appraisal_data, output_path)

            # verify path
            assert result_path == output_path
            assert os.path.exists(result_path)
            assert os.path.getsize(result_path) > 1000  # Should be non-empty

        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)

    def test_generate_property_pdf_basic(self, generator):
        # Existing method test
        data = {
            "title": "Test Property",
            "price": 300000,
            "sqm": 80,
            "description": "Test description",
        }
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            output_path = tmp.name

        try:
            result_path = generator.generate_property_pdf(data, output_path)
            assert os.path.exists(result_path)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
