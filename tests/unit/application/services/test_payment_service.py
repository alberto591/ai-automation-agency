from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from application.services.payment_service import PaymentService
from domain.models import PaymentSchedule


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_msg():
    return MagicMock()


@pytest.fixture
def payment_service(mock_db, mock_msg):
    return PaymentService(db=mock_db, msg=mock_msg)


def test_create_payment_schedule(payment_service, mock_db):
    schedule = PaymentSchedule(lead_id="lead123", amount=500.0, due_date=datetime.now())
    mock_db.save_payment_schedule.return_value = "pay_id"

    res = payment_service.create_payment_schedule(schedule)

    assert res == "pay_id"
    mock_db.save_payment_schedule.assert_called_once()


def test_process_daily_reminders(payment_service, mock_db, mock_msg):
    # Setup: one payment due in 7 days
    today = datetime.now()
    due_date = today + timedelta(days=7)
    mock_db.get_due_payments.return_value = [
        {
            "id": "p1",
            "lead_id": "lead123",
            "lead_phone": "+39123456789",
            "amount": 1000.0,
            "due_date": due_date.date().isoformat(),
            "reminder_days": [7, 3, 0],
            "description": "Rent Jan",
        }
    ]

    # Execute
    stats = payment_service.process_daily_reminders()

    # Assert
    assert stats["sent"] == 1
    mock_msg.send_message.assert_called_once()
    assert "Rent Jan" in mock_msg.send_message.call_args[0][1]
