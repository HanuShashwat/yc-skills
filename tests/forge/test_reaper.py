"""
Tests for reaper logic.
"""
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from src.forge.reaper import run_reaper


@pytest.fixture
def db_path(tmp_path):
    db_file = tmp_path / "test_reaper.db"
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
            """
        )
    return str(db_file)


def insert_item(db_path: str, content_id: str, state: str, retry_count: int, last_processed_offset_hours: int):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        last_processed = None
        if last_processed_offset_hours is not None:
            last_processed = (datetime.now(timezone.utc) + timedelta(hours=last_processed_offset_hours)).isoformat()
            
        cursor.execute(
            """
            INSERT INTO content (
                content_id, source_type, url, title, content_hash, file_path, state, retry_count, last_processed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (content_id, "library", f"http://test.com/{content_id}", "Title", "hash", "path", state, retry_count, last_processed)
        )
        conn.commit()


def test_reaper_ignores_fresh_items(db_path):
    # Only 1 hour old, shouldn't be reaped
    insert_item(db_path, "fresh", "extracting", 0, -1)
    # Not extracting state
    insert_item(db_path, "chunked", "chunked", 0, -3)
    
    count = run_reaper(db_path)
    assert count == 0
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT state FROM content WHERE content_id = 'fresh'")
        assert cursor.fetchone()[0] == "extracting"


def test_reaper_recovers_stale_item(db_path):
    # 3 hours old, should be reaped
    insert_item(db_path, "stale", "extracting", 0, -3)
    
    count = run_reaper(db_path)
    assert count == 1
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT state, retry_count FROM content WHERE content_id = 'stale'")
        state, retry = cursor.fetchone()
        assert state == "chunked"
        assert retry == 1


def test_reaper_marks_failed_after_max_retries(db_path):
    # Already failed 3 times (retry_count=3). This 4th failure pushes it over 3.
    insert_item(db_path, "doomed", "extracting", 3, -3)
    
    count = run_reaper(db_path)
    assert count == 1
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT state, retry_count FROM content WHERE content_id = 'doomed'")
        state, retry = cursor.fetchone()
        assert state == "failed"
        assert retry == 4


def test_reaper_handles_null_retry_count(db_path):
    # In case retry_count is somehow NULL
    with sqlite3.connect(db_path) as conn:
        last_processed = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
        conn.execute(
            """
            INSERT INTO content (
                content_id, source_type, url, title, content_hash, file_path, state, last_processed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("null_retry", "library", "http://test.com/null", "Title", "hash", "path", "extracting", last_processed)
        )
        
    count = run_reaper(db_path)
    assert count == 1
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT state, retry_count FROM content WHERE content_id = 'null_retry'")
        state, retry = cursor.fetchone()
        assert state == "chunked"
        assert retry == 1
