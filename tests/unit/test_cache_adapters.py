from unittest.mock import MagicMock, patch

from infrastructure.adapters.cache_adapter import InMemoryCacheAdapter, RedisAdapter


class TestRedisAdapter:
    @patch("infrastructure.adapters.cache_adapter.redis.from_url")
    def test_redis_adapter_connects_successfully(self, mock_redis):
        """Test that RedisAdapter connects to Redis successfully."""
        # Setup
        mock_client = MagicMock()
        mock_redis.return_value = mock_client

        # Execute
        adapter = RedisAdapter("redis://localhost:6379/0")

        # Verify
        mock_redis.assert_called_once_with("redis://localhost:6379/0", decode_responses=True)
        mock_client.ping.assert_called_once()
        assert adapter._client is mock_client

    @patch("infrastructure.adapters.cache_adapter.redis.from_url")
    def test_redis_adapter_handles_connection_failure(self, mock_redis):
        """Test graceful handling when Redis connection fails."""
        # Setup
        mock_redis.side_effect = Exception("Connection refused")

        # Execute
        adapter = RedisAdapter("redis://localhost:6379/0")

        # Verify fallback
        assert adapter._client is None

    @patch("infrastructure.adapters.cache_adapter.redis.from_url")
    def test_redis_adapter_handles_no_url(self, mock_redis):
        """Test that empty URL is handled gracefully."""
        # Execute
        adapter = RedisAdapter("")

        # Verify
        assert adapter._client is None
        mock_redis.assert_not_called()

    @patch("infrastructure.adapters.cache_adapter.redis.from_url")
    def test_get_returns_value_when_redis_available(self, mock_redis):
        """Test GET operation when Redis is available."""
        # Setup
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.get.return_value = "test_value"

        adapter = RedisAdapter("redis://localhost:6379/0")

        # Execute
        result = adapter.get("test_key")

        # Verify
        mock_client.get.assert_called_once_with("test_key")
        assert result == "test_value"

    @patch("infrastructure.adapters.cache_adapter.redis.from_url")
    def test_get_returns_none_when_redis_unavailable(self, mock_redis):
        """Test GET returns None when Redis is unavailable."""
        # Setup
        mock_redis.side_effect = Exception("Redis down")
        adapter = RedisAdapter("redis://localhost:6379/0")

        # Execute
        result = adapter.get("test_key")

        # Verify
        assert result is None

    @patch("infrastructure.adapters.cache_adapter.redis.from_url")
    def test_get_handles_redis_error(self, mock_redis):
        """Test GET handles errors during retrieval."""
        # Setup
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.get.side_effect = Exception("Redis error")

        adapter = RedisAdapter("redis://localhost:6379/0")

        # Execute
        result = adapter.get("test_key")

        # Verify
        assert result is None

    @patch("infrastructure.adapters.cache_adapter.redis.from_url")
    def test_set_stores_value_with_ttl(self, mock_redis):
        """Test SET operation with TTL."""
        # Setup
        mock_client = MagicMock()
        mock_redis.return_value = mock_client

        adapter = RedisAdapter("redis://localhost:6379/0")

        # Execute
        adapter.set("test_key", "test_value", ttl=300)

        # Verify
        mock_client.setex.assert_called_once_with("test_key", 300, "test_value")

    @patch("infrastructure.adapters.cache_adapter.redis.from_url")
    def test_set_uses_default_ttl(self, mock_redis):
        """Test SET uses default TTL when not specified."""
        # Setup
        mock_client = MagicMock()
        mock_redis.return_value = mock_client

        adapter = RedisAdapter("redis://localhost:6379/0")

        # Execute
        adapter.set("test_key", "test_value")

        # Verify
        mock_client.setex.assert_called_once_with("test_key", 3600, "test_value")

    @patch("infrastructure.adapters.cache_adapter.redis.from_url")
    def test_delete_removes_key(self, mock_redis):
        """Test DELETE operation."""
        # Setup
        mock_client = MagicMock()
        mock_redis.return_value = mock_client

        adapter = RedisAdapter("redis://localhost:6379/0")

        # Execute
        adapter.delete("test_key")

        # Verify
        mock_client.delete.assert_called_once_with("test_key")


class TestInMemoryCacheAdapter:
    def test_inmemory_cache_initialization(self):
        """Test InMemoryCacheAdapter initializes correctly."""
        # Execute
        adapter = InMemoryCacheAdapter()

        # Verify
        assert adapter._data == {}

    def test_set_and_get(self):
        """Test basic SET and GET operations."""
        # Setup
        adapter = InMemoryCacheAdapter()

        # Execute
        adapter.set("key1", "value1")
        result = adapter.get("key1")

        # Verify
        assert result == "value1"

    def test_get_nonexistent_key_returns_none(self):
        """Test GET returns None for nonexistent keys."""
        # Setup
        adapter = InMemoryCacheAdapter()

        # Execute
        result = adapter.get("nonexistent")

        # Verify
        assert result is None

    def test_set_overwrites_existing_value(self):
        """Test SET overwrites existing values."""
        # Setup
        adapter = InMemoryCacheAdapter()
        adapter.set("key1", "old_value")

        # Execute
        adapter.set("key1", "new_value")
        result = adapter.get("key1")

        # Verify
        assert result == "new_value"

    def test_delete_removes_key(self):
        """Test DELETE removes keys."""
        # Setup
        adapter = InMemoryCacheAdapter()
        adapter.set("key1", "value1")

        # Execute
        adapter.delete("key1")
        result = adapter.get("key1")

        # Verify
        assert result is None

    def test_delete_nonexistent_key_does_not_error(self):
        """Test DELETE on nonexistent key doesn't raise error."""
        # Setup
        adapter = InMemoryCacheAdapter()

        # Execute (should not raise)
        adapter.delete("nonexistent")

        # Verify - just check it completes
        assert True

    def test_ttl_parameter_is_accepted_but_ignored(self):
        """Test that TTL parameter is accepted but not enforced (in-memory limitation)."""
        # Setup
        adapter = InMemoryCacheAdapter()

        # Execute
        adapter.set("key1", "value1", ttl=1)  # TTL is ignored in this simple implementation
        result = adapter.get("key1")

        # Verify - value is still there (no auto-expiration)
        assert result == "value1"
