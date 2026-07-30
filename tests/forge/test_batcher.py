"""
Tests for batch selector.
"""
import sqlite3
import pytest

from src.forge.batcher import select_batch, BatchSelectionError


@pytest.fixture
def db_path(tmp_path):
    db_file = tmp_path / "test_batch.db"
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


def insert_items(db_path: str, count: int, topic: str, state: str = "chunked"):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        for i in range(count):
            content_id = f"id_{topic}_{state}_{i}"
            cursor.execute(
                """
                INSERT INTO content (
                    content_id, source_type, url, title, content_hash, file_path, state, topic_guess
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (content_id, "library", f"http://test.com/{content_id}", "Title", "hash", "path", state, topic)
            )
        conn.commit()


def test_batcher_with_specific_topic(db_path):
    insert_items(db_path, 10, "fundraising")
    
    batch_id, content_ids = select_batch(db_path, topic="fundraising", batch_size=7)
    assert batch_id is not None
    assert len(content_ids) == 7
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT state, last_processed FROM content WHERE content_id = ?", (content_ids[0],))
        row = cursor.fetchone()
        assert row[0] == "extracting"
        assert row[1] is not None


def test_batcher_no_topic_picks_most_frequent(db_path):
    insert_items(db_path, 6, "hiring")
    insert_items(db_path, 10, "product")  # Most unprocessed
    
    batch_id, content_ids = select_batch(db_path, batch_size=8)
    assert len(content_ids) == 8
    assert all("product" in cid for cid in content_ids)


def test_batcher_aborts_if_less_than_5(db_path):
    insert_items(db_path, 4, "fundraising")
    with pytest.raises(BatchSelectionError, match="Insufficient items"):
        select_batch(db_path, topic="fundraising")


def test_batcher_bounds_batch_size(db_path):
    insert_items(db_path, 25, "growth")
    # Requesting 30 should max out at 20
    batch_id, content_ids = select_batch(db_path, topic="growth", batch_size=30)
    assert len(content_ids) == 20
    
    # Requesting 3 should floor at 5
    batch_id, content_ids = select_batch(db_path, topic="growth", batch_size=3)
    assert len(content_ids) == 5


def test_batcher_only_picks_chunked(db_path):
    insert_items(db_path, 4, "fundraising", state="chunked")
    insert_items(db_path, 5, "fundraising", state="extracting")
    with pytest.raises(BatchSelectionError, match="Insufficient items"):
        select_batch(db_path, topic="fundraising")
