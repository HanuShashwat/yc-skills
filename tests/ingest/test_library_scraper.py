"""
Tests for Library Scraper.
"""
import hashlib
import sqlite3
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.ingest.library_scraper import ScraperError, _process_single_url, process_urls


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
                content_hash TEXT NOT NULL,
                file_path TEXT NOT NULL,
                state TEXT NOT NULL,
                last_processed TEXT
            );
            """
        )
    return str(db_file)


@pytest.fixture
def mock_html():
    return """
    <html>
        <head><title>Test Essay</title></head>
        <body>
            <nav>Nav content</nav>
            <article>
                <h1>Test Essay</h1>
                <p>This is a great essay.</p>
                <div class="ad">Buy stuff</div>
            </article>
            <footer>Footer content</footer>
        </body>
    </html>
    """

@pytest.fixture
def mock_html_main():
    return """
    <html>
        <head><title>Another Essay</title></head>
        <body>
            <main>
                <h1>Another Essay</h1>
                <p>Main content here.</p>
                <script>alert('bad');</script>
            </main>
        </body>
    </html>
    """

@pytest.fixture
def mock_html_fallback():
    return """
    <html>
        <head><title>Fallback Essay</title></head>
        <body>
            <div class="content">
                <p>Fallback content.</p>
                <aside>Aside content</aside>
            </div>
        </body>
    </html>
    """

@pytest.fixture
def mock_html_no_content():
    return """
    <html>
        <head><title>No Content Essay</title></head>
        <body>
            <div>No valid content node.</div>
        </body>
    </html>
    """


@patch("src.ingest.library_scraper.time.sleep")
@patch("src.ingest.library_scraper.requests.get")
def test_process_single_url_article(mock_get, mock_sleep, db_path, tmp_path, mock_html):
    """Test extracting from an <article> node."""
    mock_response = MagicMock()
    mock_response.content = mock_html.encode("utf-8")
    mock_get.return_value = mock_response

    url = "https://www.ycombinator.com/library/pg-test-essay"
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        _process_single_url(url, cursor, str(tmp_path))
        conn.commit()

    # Verify HTTP request
    mock_get.assert_called_once_with(url, headers={"User-Agent": "OpenYC-Skills/1.0 (Research Project; contact@example.com)"}, timeout=30)

    # Verify ID generation
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    expected_content_id = f"lib_{url_hash}"

    # Verify markdown was written (without <nav>, <footer>, <div class="ad">)
    file_path = tmp_path / f"{expected_content_id}.md"
    assert file_path.exists()
    
    with open(file_path, "r", encoding="utf-8") as f:
        md_text = f.read()
    
    assert "Test Essay" in md_text
    assert "This is a great essay." in md_text
    assert "Nav content" not in md_text
    assert "Buy stuff" not in md_text
    assert "Footer content" not in md_text

    # Verify hash
    expected_hash = hashlib.sha256(md_text.encode("utf-8")).hexdigest()

    # Verify DB
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT content_id, state, content_hash, speaker, designation FROM content")
        row = cursor.fetchone()

    assert row is not None
    assert row[0] == expected_content_id
    assert row[1] == "downloaded"  # PG should be found
    assert row[2] == expected_hash
    assert row[3] == "Paul Graham"
    assert row[4] == "Founder of YC"


@patch("src.ingest.library_scraper.time.sleep")
@patch("src.ingest.library_scraper.requests.get")
def test_process_urls_deduplication_and_rate_limiting(mock_get, mock_sleep, db_path, tmp_path, mock_html):
    """Test rate limiting and that duplicates are skipped."""
    mock_response = MagicMock()
    mock_response.content = mock_html.encode("utf-8")
    mock_get.return_value = mock_response

    url = "https://www.ycombinator.com/library/pg-test-essay"
    
    # Inject URL into DB first
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO content (content_id, source_type, url, title, content_hash, file_path, state, last_processed) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       ("dummy_id", "library", url, "Title", "hash", "path", "downloaded", "now"))

    with patch("src.ingest.library_scraper.RAW_DATA_DIR", str(tmp_path)):
        process_urls([url, "https://www.ycombinator.com/library/new-essay"], db_path)

    # get should only be called for the new url, since the first is a duplicate
    mock_get.assert_called_once_with("https://www.ycombinator.com/library/new-essay", headers={"User-Agent": "OpenYC-Skills/1.0 (Research Project; contact@example.com)"}, timeout=30)
    mock_sleep.assert_called_once_with(2)


@patch("src.ingest.library_scraper.time.sleep")
@patch("src.ingest.library_scraper.requests.get")
def test_process_single_url_main(mock_get, mock_sleep, db_path, tmp_path, mock_html_main):
    """Test extracting from a <main> node."""
    mock_response = MagicMock()
    mock_response.content = mock_html_main.encode("utf-8")
    mock_get.return_value = mock_response

    url = "https://www.ycombinator.com/library/unknown-author-essay"
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        _process_single_url(url, cursor, str(tmp_path))
        conn.commit()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT state, speaker FROM content WHERE url=?", (url,))
        row = cursor.fetchone()

    # Unknown author so speaker should be None and state should be discovered
    assert row[1] is None
    assert row[0] == "discovered"

    # Verify script was removed
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    content_id = f"lib_{url_hash}"
    file_path = tmp_path / f"{content_id}.md"
    with open(file_path, "r", encoding="utf-8") as f:
        md_text = f.read()
    assert "alert('bad');" not in md_text


@patch("src.ingest.library_scraper.time.sleep")
@patch("src.ingest.library_scraper.requests.get")
def test_process_single_url_fallback(mock_get, mock_sleep, db_path, tmp_path, mock_html_fallback):
    """Test extracting from a <div class='content'> node."""
    mock_response = MagicMock()
    mock_response.content = mock_html_fallback.encode("utf-8")
    mock_get.return_value = mock_response

    url = "https://www.ycombinator.com/library/sam-altman-essay"
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        _process_single_url(url, cursor, str(tmp_path))
        conn.commit()

    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    content_id = f"lib_{url_hash}"
    file_path = tmp_path / f"{content_id}.md"
    with open(file_path, "r", encoding="utf-8") as f:
        md_text = f.read()
    
    assert "Fallback content" in md_text
    assert "Aside content" not in md_text

    # Verify DB
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT speaker, state FROM content WHERE url=?", (url,))
        row = cursor.fetchone()
    
    assert row[0] == "Sam Altman"
    assert row[1] == "downloaded"


@patch("src.ingest.library_scraper.time.sleep")
@patch("src.ingest.library_scraper.requests.get")
def test_process_single_url_no_content(mock_get, mock_sleep, db_path, tmp_path, mock_html_no_content):
    """Test when no valid content node is found."""
    mock_response = MagicMock()
    mock_response.content = mock_html_no_content.encode("utf-8")
    mock_get.return_value = mock_response

    url = "https://www.ycombinator.com/library/empty-essay"
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        with pytest.raises(ScraperError):
            _process_single_url(url, cursor, str(tmp_path))


@patch("src.ingest.library_scraper.time.sleep")
@patch("src.ingest.library_scraper.requests.get")
def test_process_urls_handles_request_exception(mock_get, mock_sleep, db_path, tmp_path):
    """Test that RequestException doesn't crash process_urls."""
    mock_get.side_effect = requests.RequestException("Network error")

    with patch("src.ingest.library_scraper.RAW_DATA_DIR", str(tmp_path)):
        # Should not raise exception
        process_urls(["https://www.ycombinator.com/library/error-essay"], db_path)
    
    # DB should remain empty
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM content")
        assert cursor.fetchone()[0] == 0
