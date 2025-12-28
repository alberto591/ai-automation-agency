from unittest.mock import MagicMock, patch

import pytest

from infrastructure.adapters.supabase_adapter import SupabaseAdapter


@pytest.fixture
def adapter():
    with patch("infrastructure.adapters.supabase_adapter.create_client") as mock_create:
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        return SupabaseAdapter()


def test_get_market_stats_success(adapter):
    # Setup the chain: adapter.client.table().select().ilike().execute()
    mock_execute = MagicMock()
    mock_execute.execute.return_value = MagicMock(
        data=[
            {"price_per_mq": 5000, "price": 500000, "sqm": 100},
            {"price_per_mq": 6000, "price": 600000, "sqm": 100},
        ]
    )

    adapter.client.table.return_value.select.return_value.ilike.return_value = mock_execute

    stats = adapter.get_market_stats("Milano")
    assert stats["listings_count"] == 2
    assert stats["avg_price_sqm"] == 5500


def test_save_lead(adapter):
    mock_execute = MagicMock()
    mock_execute.execute.return_value = MagicMock(data=[{"id": 1}])
    adapter.client.table.return_value.upsert.return_value = mock_execute
    # Mocking the second call inside save_lead (for messages)
    adapter.client.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[])

    result = adapter.save_lead(
        {
            "customer_phone": "+393331234567",
            "customer_name": "Test",
            "messages": [{"role": "user", "content": "hello"}],
        }
    )
    assert result is None
