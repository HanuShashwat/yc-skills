"""
Tests for transcript chunker.
"""
import sqlite3
from unittest.mock import patch

import pytest

from src.chunker.transcript_chunker import chunk_transcript, parse_transcript_line


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
            INSERT INTO content (content_id, state) VALUES ('yt_test1', 'downloaded');
            
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


def test_parse_transcript_line():
    ts, spk, text = parse_transcript_line("[00:01:05] Paul Graham: Hello world.")
    assert ts == "00:01:05"
    assert spk == "Paul Graham"
    assert text == "Hello world."
    
    ts, spk, text = parse_transcript_line("[00:02:10] Just some text.")
    assert ts == "00:02:10"
    assert spk is None
    assert text == "Just some text."
    
    ts, spk, text = parse_transcript_line("No timestamp here.")
    assert ts is None
    assert spk is None
    assert text == "No timestamp here."


def test_chunk_transcript(db_path, tmp_path):
    # Create a mock transcript file
    transcript_path = tmp_path / "test.transcript.txt"
    lines = [
        "[00:00:01] Paul Graham: This is the start of a talk.",
        "[00:00:05] Paul Graham: I will speak for a long time.",
        "[00:00:10] Sam Altman: I will interrupt you now.",
        "[00:00:15] Sam Altman: With my own point."
    ]
    # Add a huge block for Sam to trigger the max_words split
    for i in range(200):
        lines.append(f"[00:01:{i%60:02d}] Sam Altman: Here is sentence {i} with about five words.")
        
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    with patch("src.chunker.transcript_chunker.CHUNK_OUTPUT_DIR", str(tmp_path)):
        chunk_transcript(
            content_id="yt_test1", 
            file_path=str(transcript_path), 
            default_speaker="Unknown", 
            db_path=db_path
        )
        
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT chunk_index, speaker, word_count, timestamp_start, timestamp_end FROM chunks WHERE content_id='yt_test1' ORDER BY chunk_index")
        chunks = cursor.fetchall()
        
    assert len(chunks) >= 3
    
    # Chunk 0 should be Paul Graham
    assert chunks[0][1] == "Paul Graham"
    assert chunks[0][3] == "00:00:01"
    assert chunks[0][4] == "00:00:05"
    
    # Chunk 1 should be Sam Altman, but split because of length
    assert chunks[1][1] == "Sam Altman"
    assert chunks[1][3] == "00:00:10"
    
    # Word count bounding checks for Sam's chunks
    assert chunks[1][2] >= 600
    assert chunks[1][2] <= 850


def test_chunk_transcript_no_segments(db_path, tmp_path):
    # Empty transcript
    transcript_path = tmp_path / "empty.transcript.txt"
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write("")
        
    with patch("src.chunker.transcript_chunker.CHUNK_OUTPUT_DIR", str(tmp_path)):
        chunk_transcript("yt_test1", str(transcript_path), "Unknown", db_path)
        
    # Should exit gracefully without failing
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM chunks")
        assert cursor.fetchone()[0] == 0
