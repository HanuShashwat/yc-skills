"""
Scraper for YC Library essays.
"""

import hashlib
import logging
import os
import sqlite3
import time
from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify

from src.ingest.known_authors import lookup_author

logger = logging.getLogger(__name__)

USER_AGENT = "OpenYC-Skills/1.0 (Research Project; contact@example.com)"
TIMEOUT = 30
RAW_DATA_DIR = "data/raw/library"


class ScraperError(Exception):
    """Base exception for scraper errors."""

    pass


def process_urls(urls: List[str], db_path: str) -> None:
    """
    Process a list of YC Library essay URLs.

    Args:
        urls: List of URLs to scrape.
        db_path: Path to the SQLite database.
    """
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            for url in urls:
                # Deduplication check
                cursor.execute("SELECT content_id FROM content WHERE url = ?", (url,))
                if cursor.fetchone() is not None:
                    logger.info("URL already exists in database, skipping: %s", url)
                    continue

                # Rate limiting
                time.sleep(2)

                try:
                    _process_single_url(url, cursor, RAW_DATA_DIR)
                    conn.commit()
                except requests.RequestException as e:
                    logger.error("Failed to download %s: %s", url, e)
                except ScraperError as e:
                    logger.error("Scraping error for %s: %s", url, e)
                except Exception as e:
                    logger.error("Unexpected error processing %s: %s", url, e)

    except sqlite3.Error as e:
        logger.error("Database error: %s", e)


def _process_single_url(url: str, cursor: sqlite3.Cursor, output_dir: str) -> None:
    """
    Process a single URL.

    Args:
        url: URL to scrape.
        cursor: SQLite cursor.
        output_dir: Directory to save the raw markdown.
    """
    logger.info("Downloading: %s", url)
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=TIMEOUT)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    # Try finding title
    title_tag = soup.find("title")
    title = title_tag.text.strip() if title_tag else "Unknown Title"

    # Extract main content
    content_node = (
        soup.find("article") or soup.find("main") or soup.find("div", class_="content")
    )
    if not content_node:
        raise ScraperError(
            "Could not find main content node (<article>, <main>, or <div class='content'>)"
        )

    # Remove unwanted tags
    unwanted_selectors = [
        "nav",
        "footer",
        "script",
        "style",
        "aside",
        ".ad",
        ".advertisement",
        ".newsletter-box",
        "#newsletter",
    ]
    for selector in unwanted_selectors:
        for node in content_node.select(selector):
            node.decompose()

    # Convert to markdown
    md_text = markdownify(str(content_node)).strip()

    # Hashes and IDs
    content_hash = hashlib.sha256(md_text.encode("utf-8")).hexdigest()
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    content_id = f"lib_{url_hash}"

    # Save to file
    file_path = os.path.join(output_dir, f"{content_id}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(md_text)

    # Extract speaker
    speaker, designation = lookup_author(url)

    state = "discovered" if not speaker else "downloaded"
    now_iso = datetime.utcnow().isoformat()

    # Insert into database
    cursor.execute(
        """
        INSERT INTO content (
            content_id, source_type, url, title, speaker, designation,
            content_hash, file_path, state, last_processed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            content_id,
            "library",
            url,
            title,
            speaker,
            designation,
            content_hash,
            file_path,
            state,
            now_iso,
        ),
    )
    logger.info("Successfully processed %s (content_id: %s)", url, content_id)
