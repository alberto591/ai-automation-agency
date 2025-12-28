def test_full_lead_cycle(client, mock_container):
    """
    Simulates a full lead cycle:
    1. New lead arrives.
    2. AI processes and responds.
    3. Human takes over.
    4. Human sends manual message.
    """
    # 1. New lead arrives
    mock_container.lead_processor.process_lead.return_value = "AI: Hello, how can I help?"
    payload = {"name": "Integration Test", "agency": "Test Corp", "phone": "+390000000001"}
    response = client.post("/api/leads", json=payload)
    assert response.status_code == 200
    assert response.json()["ai_response"] == "AI: Hello, how can I help?"

    # 2. Human takes over
    response = client.post("/api/leads/takeover", json={"phone": "+390000000001"})
    assert response.status_code == 200
    mock_container.lead_processor.takeover.assert_called_with("+390000000001")

    # 3. Human sends manual message
    payload_msg = {"phone": "+390000000001", "message": "Human here!"}
    response = client.post("/api/leads/message", json=payload_msg)
    assert response.status_code == 200
    mock_container.lead_processor.send_manual_message.assert_called()


def test_viewing_flow(client, mock_container):
    """
    Simulates a viewing scheduling flow.
    """
    payload = {"phone": "+390000000002", "start_time": "2025-05-01T10:00:00Z"}
    response = client.post("/api/leads/schedule", json=payload)
    assert response.status_code == 200
    mock_container.journey.transition_to.assert_called()
