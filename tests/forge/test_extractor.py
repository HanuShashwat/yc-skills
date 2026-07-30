"""
Tests for extraction stage.
"""
import sqlite3
import json
from unittest.mock import patch, MagicMock

import pytest

from src.forge.extractor import run_extraction


@pytest.fixture
def db_path(tmp_path):
    db_file = tmp_path / "test_extract.db"
    with sqlite3.connect(db_file) as conn:
        conn.executescript(
            """
            CREATE TABLE content (
                content_id TEXT PRIMARY KEY,
                source_type TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                title TEXT NOT NULL,
                speaker TEXT,
                designation TEXT,
                published_at TEXT,
                content_hash TEXT NOT NULL,
                file_path TEXT NOT NULL,
                state TEXT NOT NULL,
                topic_guess TEXT,
                retry_count INTEGER DEFAULT 0,
                last_processed TEXT,
                error_message TEXT
            );
            
            CREATE TABLE chunks (
                chunk_id TEXT PRIMARY KEY,
                content_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                word_count INTEGER NOT NULL,
                char_count INTEGER NOT NULL,
                speaker TEXT,
                timestamp_start TEXT,
                timestamp_end TEXT,
                FOREIGN KEY (content_id) REFERENCES content(content_id)
            );
            
            CREATE TABLE extracted_items (
                item_id TEXT PRIMARY KEY,
                batch_id TEXT NOT NULL,
                chunk_id TEXT NOT NULL,
                in_batch_index INTEGER NOT NULL,
                quote TEXT NOT NULL,
                speaker TEXT NOT NULL,
                designation TEXT,
                topic TEXT NOT NULL,
                source_url TEXT NOT NULL,
                is_framework INTEGER NOT NULL CHECK(is_framework IN (0, 1)),
                is_warning INTEGER NOT NULL CHECK(is_warning IN (0, 1)),
                extraction_date TEXT NOT NULL
            );
            """
        )
    return str(db_file)


@pytest.fixture
def setup_data(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO content (
                content_id, source_type, url, title, content_hash, file_path, state, speaker, designation
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("cid1", "library", "http://test.com/1", "T1", "hash1", "path1", "extracting", "S1", "D1")
        )
        
        cursor.execute(
            """
            INSERT INTO chunks (
                chunk_id, content_id, chunk_index, text, word_count, char_count
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("chunk1", "cid1", 0, "Chunk text 1", 10, 50)
        )
        
        cursor.execute(
            """
            INSERT INTO chunks (
                chunk_id, content_id, chunk_index, text, word_count, char_count
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("chunk2", "cid1", 1, "Chunk text 2", 10, 50)
        )
        conn.commit()
    return db_path


def test_run_extraction_success(setup_data):
    mock_response = {
        "extracted_items": [
            {
                "in_batch_index": 1,
                "quote": "Quote 1",
                "speaker": "S1",
                "designation": "D1",
                "source_id": "cid1",
                "source_url": "http://test.com/1",
                "topic": "fundraising",
                "type": "framework",
                "context": "Context 1",
                "is_partial": False
            },
            {
                "in_batch_index": 2,
                "quote": "Quote 2",
                "speaker": "S1",
                "designation": "D1",
                "source_id": "cid1",
                "source_url": "http://test.com/1",
                "topic": "hiring",
                "type": "warning",
                "context": "Context 2",
                "is_partial": True
            }
        ],
        "contradictions": []
    }
    
    with patch("src.forge.extractor.LLMClient") as MockLLM:
        mock_instance = MockLLM.return_value
        mock_instance.call.return_value = json.dumps(mock_response)
        
        run_extraction("batch123", ["cid1"], setup_data)
        
        with sqlite3.connect(setup_data) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT state FROM content WHERE content_id = 'cid1'")
            assert cursor.fetchone()[0] == "extracted"
            
            cursor.execute("SELECT count(*) FROM extracted_items WHERE batch_id = 'batch123'")
            assert cursor.fetchone()[0] == 2
            
            cursor.execute("SELECT is_framework, is_warning FROM extracted_items WHERE in_batch_index = 1")
            row1 = cursor.fetchone()
            assert row1[0] == 1  # is_framework
            assert row1[1] == 0  # is_warning
            
            cursor.execute("SELECT is_framework, is_warning FROM extracted_items WHERE in_batch_index = 2")
            row2 = cursor.fetchone()
            assert row2[0] == 0  # is_framework
            assert row2[1] == 1  # is_warning


def test_run_extraction_retry_on_bad_json(setup_data):
    mock_good_response = {
        "extracted_items": [],
        "contradictions": []
    }
    
    with patch("src.forge.extractor.LLMClient") as MockLLM:
        mock_instance = MockLLM.return_value
        mock_instance.call.side_effect = ["{ bad json", json.dumps(mock_good_response)]
        
        with patch("src.forge.extractor.open", new_callable=MagicMock) as mock_open:
            with patch("os.makedirs"):
                run_extraction("batch_retry", ["cid1"], setup_data)
                
                assert mock_instance.call.call_count == 2
                mock_open.assert_called_with("data/errors/batch_retry.json", "w", encoding="utf-8")
                
                with sqlite3.connect(setup_data) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT state FROM content WHERE content_id = 'cid1'")
                    assert cursor.fetchone()[0] == "extracted"


def test_run_extraction_fails_after_retry(setup_data):
    with patch("src.forge.extractor.LLMClient") as MockLLM:
        mock_instance = MockLLM.return_value
        mock_instance.call.side_effect = ["{ bad json", "{ still bad"]
        
        with patch("src.forge.extractor.open", new_callable=MagicMock):
            with patch("os.makedirs"):
                with pytest.raises(ValueError, match="Parse error"):
                    run_extraction("batch_fail", ["cid1"], setup_data)
                    
                with sqlite3.connect(setup_data) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT state FROM content WHERE content_id = 'cid1'")
                    assert cursor.fetchone()[0] == "extracting"


def test_run_extraction_skips_invalid_batch_index(setup_data):
    mock_response = {
        "extracted_items": [
            {
                "in_batch_index": 999,  # Doesn't exist
                "quote": "Quote 1",
                "speaker": "S1",
                "designation": "D1",
                "source_id": "cid1",
                "source_url": "http://test.com/1",
                "topic": "fundraising",
                "type": "framework",
                "context": "Context 1",
                "is_partial": False
            }
        ],
        "contradictions": []
    }
    
    with patch("src.forge.extractor.LLMClient") as MockLLM:
        mock_instance = MockLLM.return_value
        mock_instance.call.return_value = json.dumps(mock_response)
        
        run_extraction("batch_skip", ["cid1"], setup_data)
        
        with sqlite3.connect(setup_data) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM extracted_items WHERE batch_id = 'batch_skip'")
            # Skipped item, count should be 0
            assert cursor.fetchone()[0] == 0
            
            # State is still updated since LLM call succeeded
            cursor.execute("SELECT state FROM content WHERE content_id = 'cid1'")
            assert cursor.fetchone()[0] == "extracted"


def test_run_extraction_no_content_ids(db_path):
    # Should exit early without database hits
    run_extraction("batch_empty", [], db_path)
