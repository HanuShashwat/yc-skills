"""
Tests for YouTube downloader.
"""
import json
import os
import sqlite3
import subprocess
from unittest.mock import patch

import pytest

from src.ingest.youtube_downloader import (
    DownloaderError,
    _process_single_url,
    extract_video_id,
    guess_speaker,
    process_urls,
)


@pytest.fixture
def db_path(tmp_path):
    db_file = tmp_path / "test.db"
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
                last_processed TEXT
            );
            """
        )
    return str(db_file)


def test_extract_video_id():
    assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    with pytest.raises(ValueError):
        extract_video_id("https://example.com")


def test_guess_speaker():
    # Test Pattern 1
    assert guess_speaker("Some text with Paul Graham talking.") == ("Paul Graham", None)
    
    # Test Pattern 2
    assert guess_speaker("Featuring Sam Altman, CEO of YC.") == ("Sam Altman", "CEO")
    assert guess_speaker("Talk by Garry Tan, Partner at YC.") == ("Garry Tan", "Partner")
    
    # Test None
    assert guess_speaker("A random description with no names.") == (None, None)
    assert guess_speaker(None) == (None, None)


@patch("src.ingest.youtube_downloader.subprocess.run")
def test_process_single_url_success(mock_run, db_path, tmp_path):
    video_id = "test_vid"
    url = f"https://youtube.com/watch?v={video_id}"
    
    # Setup mock files that yt-dlp would create
    output_dir = str(tmp_path)
    
    info_json_path = os.path.join(output_dir, f"{video_id}.info.json")
    with open(info_json_path, "w") as f:
        json.dump({
            "title": "Startup Advice",
            "uploader": "Y Combinator",
            "upload_date": "20230101",
            "description": "A talk with Paul Graham about startups."
        }, f)
        
    json3_path = os.path.join(output_dir, f"{video_id}.en.json3")
    with open(json3_path, "w") as f:
        json.dump({
            "events": [
                {
                    "tStartMs": 61000,
                    "segs": [{"utf8": "Hello "}, {"utf8": "World"}]
                }
            ]
        }, f)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        _process_single_url(url, video_id, f"yt_{video_id}", cursor, output_dir)
        conn.commit()
        
    mock_run.assert_called_once()
    assert mock_run.call_args[0][0][:8] == [
        "yt-dlp", "--write-subs", "--sub-langs", "en", 
        "--sub-format", "json3", "--skip-download", "--write-info-json"
    ]
    
    # Verify outputs
    transcript_path = os.path.join(output_dir, f"{video_id}.transcript.txt")
    assert os.path.exists(transcript_path)
    with open(transcript_path, "r") as f:
        assert f.read() == "[00:01:01] Hello World"
        
    meta_path = os.path.join(output_dir, f"{video_id}.meta.json")
    assert os.path.exists(meta_path)
    with open(meta_path, "r") as f:
        meta = json.load(f)
        assert meta["speaker"] == "Paul Graham"
        assert meta["designation"] is None
        assert meta["upload_date"] == "2023-01-01"
        
    # Verify DB
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT state, file_path FROM content WHERE content_id=?", (f"yt_{video_id}",))
        row = cursor.fetchone()
        assert row[0] == "downloaded"
        assert row[1] == transcript_path


@patch("src.ingest.youtube_downloader.subprocess.run")
def test_process_single_url_missing_info(mock_run, db_path, tmp_path):
    video_id = "missing_info"
    url = f"https://youtube.com/watch?v={video_id}"
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        with pytest.raises(DownloaderError, match="Info JSON not found"):
            _process_single_url(url, video_id, f"yt_{video_id}", cursor, str(tmp_path))


@patch("src.ingest.youtube_downloader.subprocess.run")
def test_process_single_url_subprocess_error(mock_run, db_path, tmp_path):
    mock_run.side_effect = subprocess.CalledProcessError(1, ["yt-dlp"], stderr="Some error")
    
    video_id = "err_vid"
    url = f"https://youtube.com/watch?v={video_id}"
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        with pytest.raises(DownloaderError, match="yt-dlp failed"):
            _process_single_url(url, video_id, f"yt_{video_id}", cursor, str(tmp_path))


@patch("src.ingest.youtube_downloader.subprocess.run")
def test_process_urls_deduplication(mock_run, db_path, tmp_path):
    video_id = "dup_vid"
    url = f"https://youtube.com/watch?v={video_id}"
    content_id = f"yt_{video_id}"
    
    # Pre-insert
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO content (content_id, source_type, url, title, content_hash, file_path, state, last_processed) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (content_id, "youtube", url, "Title", "hash", "path", "downloaded", "now"))
        
    with patch("src.ingest.youtube_downloader.RAW_DATA_DIR", str(tmp_path)):
        process_urls([url], db_path)
        
    mock_run.assert_not_called()


@patch("src.ingest.youtube_downloader.subprocess.run")
def test_process_single_url_no_speaker_no_subs(mock_run, db_path, tmp_path):
    video_id = "no_speaker_vid"
    url = f"https://youtube.com/watch?v={video_id}"
    output_dir = str(tmp_path)
    
    info_json_path = os.path.join(output_dir, f"{video_id}.info.json")
    with open(info_json_path, "w") as f:
        json.dump({
            "title": "Random Video",
            "description": "Just some regular description without names."
        }, f)
        
    # Do not create json3 file to simulate no subtitles

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        _process_single_url(url, video_id, f"yt_{video_id}", cursor, output_dir)
        conn.commit()
        
    # Verify transcript is created but empty
    transcript_path = os.path.join(output_dir, f"{video_id}.transcript.txt")
    assert os.path.exists(transcript_path)
    with open(transcript_path, "r") as f:
        assert f.read() == ""
        
    # Verify DB state is discovered
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT state, speaker FROM content WHERE content_id=?", (f"yt_{video_id}",))
        row = cursor.fetchone()
        assert row[0] == "discovered"
        assert row[1] is None
