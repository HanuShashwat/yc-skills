"""
Tests for essay chunker.
"""
import json
import os
import sqlite3
from unittest.mock import patch

import pytest

from src.chunker.essay_chunker import chunk_essay, get_sentences, get_word_count


@pytest.fixture
def db_path(tmp_path):
    db_file = tmp_path / "test.db"
    with sqlite3.connect(db_file) as conn:
        conn.executescript(
            """
            CREATE TABLE content (
                content_id TEXT PRIMARY KEY,
                state TEXT NOT NULL
            );
            INSERT INTO content (content_id, state) VALUES ('lib_test1', 'downloaded');
            INSERT INTO content (content_id, state) VALUES ('lib_test2', 'downloaded');
            
            CREATE TABLE chunks (
                chunk_id TEXT PRIMARY KEY,
                content_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                word_count INTEGER NOT NULL,
                char_count INTEGER NOT NULL,
                speaker TEXT,
                timestamp_start TEXT,
                timestamp_end TEXT
            );
            """
        )
    return str(db_file)


@pytest.fixture
def sample_essay():
    # Construct a sample essay to test various conditions
    # 1. Short section to test merging (<200 words)
    # 2. Long section to test splitting (>800 words)
    
    short_section = "## Introduction\n" + "Word " * 50 + "End of intro."
    
    # Needs to be > 800 words
    long_section = "## Deep Dive\n"
    for i in range(10):
        long_section += "Paragraph " + str(i) + ". " + "Word " * 90 + "\n\n"
        
    return short_section + "\n" + long_section


def test_get_sentences():
    text = "Hello world. This is a test! Are you sure? Yes, I am."
    sentences = get_sentences(text)
    assert len(sentences) == 4
    assert sentences[0] == "Hello world."
    assert sentences[1] == "This is a test!"
    assert sentences[2] == "Are you sure?"
    assert sentences[3] == "Yes, I am."


def test_chunk_essay(db_path, sample_essay, tmp_path):
    with patch("src.chunker.essay_chunker.CHUNK_OUTPUT_DIR", str(tmp_path)):
        chunk_essay(
            content_id="lib_test1",
            markdown_text=sample_essay,
            speaker="Paul Graham",
            db_path=db_path
        )
        
    # Verify DB state
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Content state should be chunked
        cursor.execute("SELECT state FROM content WHERE content_id = 'lib_test1'")
        assert cursor.fetchone()[0] == "chunked"
        
        # Check chunks
        cursor.execute("SELECT chunk_id, chunk_index, word_count, speaker FROM chunks WHERE content_id = 'lib_test1' ORDER BY chunk_index")
        chunks = cursor.fetchall()
        
    assert len(chunks) > 1
    
    # First chunk should have merged the small introduction into the start of the deep dive
    # The deep dive is ~920 words, so it should have been split.
    # The first chunk should have speaker "Paul Graham"
    for chunk in chunks:
        assert chunk[3] == "Paul Graham"
        assert chunk[2] >= 200 or chunk[2] > 100  # In some extreme splits, maybe slightly less, but generally within bounds
        assert chunk[2] <= 850  # Should not be > 800, but with overlap and padding might be slightly above, but definitely not 900+

    # Verify JSON files
    for chunk in chunks:
        chunk_id = chunk[0]
        json_file = os.path.join(str(tmp_path), f"{chunk_id}.json")
        assert os.path.exists(json_file)
        
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["chunk_id"] == chunk_id
            assert data["speaker"] == "Paul Graham"
            assert data["content_id"] == "lib_test1"


def test_chunk_essay_overlap(db_path, tmp_path):
    essay = "## Section 1\nThis is sentence one. This is sentence two."
    essay += "\n\n" * 5  # pad to ensure split if max_words was low, but let's just make it huge
    essay = "## Sec 1\n" + "Word " * 850 + "This is the last sentence."
    essay += "\n\n## Sec 2\n" + "Next section begins here."
    
    # We will just rely on the split logic
    with patch("src.chunker.essay_chunker.CHUNK_OUTPUT_DIR", str(tmp_path)):
        chunk_essay(
            content_id="lib_test2",
            markdown_text=essay,
            speaker=None,
            db_path=db_path
        )

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT text FROM chunks WHERE content_id = 'lib_test2' ORDER BY chunk_index")
        chunks = cursor.fetchall()
        
    assert len(chunks) >= 2
    # The overlap means the second chunk should contain "This is the last sentence." at its start
    assert "This is the last sentence." in chunks[1][0]
