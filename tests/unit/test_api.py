def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_user_profile(client):
    response = client.get("/api/user/profile")
    assert response.status_code == 200
    assert "agency_name" in response.json()


def test_create_lead_success(client, mock_container):
    mock_container.lead_processor.process_lead.return_value = "AI Response"
    payload = {"name": "John Doe", "agency": "Test Agency", "phone": "+393331234567"}
    response = client.post("/api/leads", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["ai_response"] == "AI Response"


def test_create_lead_invalid_phone(client):
    payload = {"name": "John Doe", "agency": "Test Agency", "phone": "invalid-phone"}
    response = client.post("/api/leads", json=payload)
    assert response.status_code == 400
    assert "Invalid phone format" in response.json()["detail"]


def test_takeover_lead(client, mock_container):
    response = client.post("/api/leads/takeover", json={"phone": "+393331234567"})
    assert response.status_code == 200
    mock_container.lead_processor.takeover.assert_called_with("+393331234567")


def test_resume_lead(client, mock_container):
    response = client.post("/api/leads/resume", json={"phone": "+393331234567"})
    assert response.status_code == 200
    mock_container.lead_processor.resume.assert_called_with("+393331234567")


def test_send_manual_message(client, mock_container):
    mock_container.lead_processor.send_manual_message.return_value = "msg_123"
    payload = {"phone": "+393331234567", "message": "Hello manual"}
    response = client.post("/api/leads/message", json=payload)
    assert response.status_code == 200
    assert response.json()["sid"] == "msg_123"
    mock_container.lead_processor.send_manual_message.assert_called()


def test_update_lead(client, mock_container):
    payload = {
        "phone": "+393331234567",
        "name": "Updated Name",
        "budget": 500000,
        "status": "active",
    }
    response = client.patch("/api/leads", json=payload)
    assert response.status_code == 200
    mock_container.lead_processor.update_lead_details.assert_called()


def test_schedule_viewing(client, mock_container):
    payload = {"phone": "+393331234567", "start_time": "2025-12-28T10:00:00Z"}
    response = client.post("/api/leads/schedule", json=payload)
    assert response.status_code == 200
    mock_container.journey.transition_to.assert_called()


def test_generate_appraisal_pdf_success(client, mock_container):
    """Test successful PDF generation for appraisal report."""
    from unittest.mock import patch

    payload = {
        "address": "Via Roma 1, Milano",
        "fifi_data": {
            "predicted_value": 500000,
            "confidence_range": "EUR 480.000 - EUR 520.000",
            "confidence_level": 90,
            "features": {"sqm": 100, "bedrooms": 2},
            "investment_metrics": {"monthly_rent": 1500, "cap_rate": 3.6},
            "comparables": [],
        },
    }

    with patch("infrastructure.ai_pdf_generator.PropertyPDFGenerator") as mock_gen:
        mock_instance = mock_gen.return_value
        mock_instance.generate_appraisal_report.return_value = "temp/documents/appraisal_test.pdf"

        response = client.post("/api/appraisals/generate-pdf", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "pdf_path" in data
        assert "filename" in data
        assert data["message"] == "PDF generato con successo"
        mock_instance.generate_appraisal_report.assert_called_once()


def test_generate_appraisal_pdf_failure(client):
    """Test error handling when PDF generation fails."""
    from unittest.mock import patch

    payload = {
        "address": "Via Roma 1, Milano",
        "fifi_data": {"predicted_value": 500000},
    }

    with patch("infrastructure.ai_pdf_generator.PropertyPDFGenerator") as mock_gen:
        mock_instance = mock_gen.return_value
        mock_instance.generate_appraisal_report.side_effect = Exception("PDF generation error")

        response = client.post("/api/appraisals/generate-pdf", json=payload)

        assert response.status_code == 500
        assert "Failed to generate PDF" in response.json()["detail"]


def test_generate_appraisal_estimate(client, mock_container):
    """Test appraisal estimation endpoint."""
    mock_container.appraisal_service.estimate_value.return_value = {
        "estimated_value": 450000.0,
        "estimated_range_min": 430000.0,
        "estimated_range_max": 470000.0,
        "avg_price_sqm": 4736.0,
        "price_sqm_min": 4526.0,
        "price_sqm_max": 4947.0,
        "comparables": [],
        "reasoning": "Estimated based on market data",
        "market_trend": "stable",
    }

    payload = {
        "city": "Roma",
        "zone": "Centro",
        "property_type": "apartment",
        "surface_sqm": 95,
        "condition": "good",
        "bedrooms": 2,
    }

    response = client.post("/api/appraisals/estimate", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "estimated_value" in data
    assert "estimated_range_min" in data
    assert "estimated_range_max" in data
    assert data["estimated_value"] == 450000.0
    mock_container.appraisal_service.estimate_value.assert_called_once()
