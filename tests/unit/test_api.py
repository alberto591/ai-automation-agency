def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


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
    payload = {"phone": "+393331234567", "message": "Hello manual"}
    response = client.post("/api/leads/message", json=payload)
    assert response.status_code == 200
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
