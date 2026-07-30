"""
Tests for LLMClient.
"""
import sqlite3
from unittest.mock import MagicMock, patch

import pytest

from src.config import ProviderConfig
from src.forge.llm_client import LLMClient


@pytest.fixture
def db_path(tmp_path):
    db_file = tmp_path / "test_usage.db"
    with sqlite3.connect(db_file) as conn:
        conn.executescript(
            """
            CREATE TABLE usage_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                model TEXT NOT NULL,
                batch_id TEXT,
                prompt_tokens INTEGER NOT NULL,
                completion_tokens INTEGER NOT NULL,
                total_tokens INTEGER NOT NULL,
                cost_estimate_usd REAL,
                call_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                success INTEGER NOT NULL,
                error_message TEXT
            );
            """
        )
    return str(db_file)


@pytest.fixture
def mock_config():
    mock = MagicMock()
    
    provider1 = ProviderConfig(
        api_key="key1", base_url="url1", model="model1", 
        daily_token_limit=1000, daily_request_limit=100, 
        priority=2, timeout=30, max_retries=2
    )
    provider2 = ProviderConfig(
        api_key="key2", base_url="url2", model="model2", 
        daily_token_limit=1000, daily_request_limit=100, 
        priority=1, timeout=30, max_retries=2
    )
    
    mock.providers.providers = {"provider1": provider1, "provider2": provider2}
    mock.providers.quotas.buffer_percent = 10
    return mock


@patch("src.forge.llm_client.load_config")
def test_get_provider(mock_load, db_path, mock_config):
    mock_load.return_value = mock_config
    
    client = LLMClient(db_path=db_path)
    
    # Priority 1 is provider2, Priority 2 is provider1
    # Both have 1000 limit * 0.9 = 900 remaining
    best_name, best_provider = client.get_provider(100)
    assert best_name == "provider2"
    assert best_provider.model == "model2"
    
    # Let's add usage to provider2 so it falls below 100 remaining
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO usage_log (provider, model, prompt_tokens, completion_tokens, total_tokens, call_type, timestamp, success) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("provider2", "model2", 400, 450, 850, "extract", "2026-07-31T00:00:00", 1)
        )
        
    # Now provider2 has 900 - 850 = 50 remaining.
    # We ask for 100. It should pick provider1.
    best_name, best_provider = client.get_provider(100)
    assert best_name == "provider1"


@patch("src.forge.llm_client.load_config")
@patch("openai.OpenAI")
def test_call_success_json(mock_openai, mock_load, db_path, mock_config):
    mock_load.return_value = mock_config
    
    mock_client_instance = MagicMock()
    mock_openai.return_value = mock_client_instance
    
    # Setup mock response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"key": "value"}'
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 5
    
    mock_client_instance.chat.completions.create.return_value = mock_response
    
    client = LLMClient(db_path=db_path)
    result = client.call("Hello", call_type="extract", response_format_json=True)
    
    assert isinstance(result, dict)
    assert result["key"] == "value"
    
    # Verify usage was logged
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT total_tokens, success FROM usage_log WHERE call_type = 'extract'")
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == 15
        assert row[1] == 1


@patch("src.forge.llm_client.load_config")
@patch("openai.OpenAI")
def test_call_retry_json_parse(mock_openai, mock_load, db_path, mock_config):
    mock_load.return_value = mock_config
    
    mock_client_instance = MagicMock()
    mock_openai.return_value = mock_client_instance
    
    # First response is bad JSON, second is good
    bad_response = MagicMock()
    bad_response.choices[0].message.content = 'Not a JSON'
    
    good_response = MagicMock()
    good_response.choices[0].message.content = '{"fixed": true}'
    
    mock_client_instance.chat.completions.create.side_effect = [bad_response, good_response]
    
    client = LLMClient(db_path=db_path)
    result = client.call("Hello", call_type="extract", response_format_json=True)
    
    assert result["fixed"] is True
    # The first call should have used default temp, second should have used 0.1
    # We can check how many times create was called
    assert mock_client_instance.chat.completions.create.call_count == 2
