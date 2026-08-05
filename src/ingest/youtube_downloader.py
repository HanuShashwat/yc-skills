"""
YouTube downloader for OpenOpenYC Skills.
"""

import hashlib
import json
import logging
import os
import re
import sqlite3
import subprocess
from datetime import datetime
from typing import List, Tuple, Optional
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)

RAW_DATA_DIR = "data/raw/youtube"


class DownloaderError(Exception):
    """Base exception for YouTube downloader errors."""

    pass


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from URL."""
    parsed = urlparse(url)
    if "youtu.be" in parsed.netloc:
        return parsed.path.lstrip("/")
    if "youtube.com" in parsed.netloc:
        vid = parse_qs(parsed.query).get("v", [None])[0]
        if vid:
            return vid
    raise ValueError(f"Invalid YouTube URL: {url}")


def guess_speaker(description: str) -> Tuple[Optional[str], Optional[str]]:
    """Guess speaker and designation from description using regex."""
    if not description:
        return None, None

    # Pattern 1: with First Last
    m = re.search(r"with ([A-Z][a-z]+ [A-Z][a-z]+)", description)
    if m:
        return m.group(1), None

    # Pattern 2: First Last, Title
    m2 = re.search(
        r"([A-Z][a-z]+ [A-Z][a-z]+), (CEO|Founder|Partner|Co-founder|President|Managing Director|Director)",
        description,
    )
    if m2:
        return m2.group(1), m2.group(2)

    return None, None


def convert_json3_to_text(json3_path: str, output_path: str) -> str:
    """Convert json3 subtitles to plain text with timestamps."""
    with open(json3_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    transcript_text = []
    events = data.get("events", [])
    for event in events:
        if "segs" not in event:
            continue
        start_ms = event.get("tStartMs", 0)
        seconds = start_ms // 1000
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        timestamp = f"[{h:02d}:{m:02d}:{s:02d}]"

        text = "".join(seg.get("utf8", "") for seg in event["segs"]).strip()
        if text and text != "\n":
            transcript_text.append(f"{timestamp} {text}")

    plain_text = "\n".join(transcript_text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(plain_text)

    return plain_text


def process_urls(urls: List[str], db_path: str) -> None:
    """Process a list of YouTube URLs."""
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            for url in urls:
                try:
                    video_id = extract_video_id(url)
                    content_id = f"yt_{video_id}"

                    cursor.execute(
                        "SELECT content_id FROM content WHERE content_id = ?",
                        (content_id,),
                    )
                    if cursor.fetchone() is not None:
                        logger.info(
                            "Content ID %s already exists, skipping: %s",
                            content_id,
                            url,
                        )
                        continue

                    _process_single_url(url, video_id, content_id, cursor, RAW_DATA_DIR)
                    conn.commit()
                except Exception as e:
                    logger.error("Error processing %s: %s", url, e)

    except sqlite3.Error as e:
        logger.error("Database error: %s", e)


def _process_single_url(
    url: str, video_id: str, content_id: str, cursor: sqlite3.Cursor, output_dir: str
) -> None:
    """Download and process a single YouTube URL."""
    logger.info("Downloading YouTube metadata and subtitles for: %s", url)

    cmd = [
        "yt-dlp",
        "--write-subs",
        "--sub-langs",
        "en",
        "--sub-format",
        "json3",
        "--skip-download",
        "--write-info-json",
        "--output",
        f"{output_dir}/%(id)s",
        url,
    ]

    try:
        subprocess.run(cmd, check=True, timeout=300, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        logger.error("yt-dlp failed: %s", e.stderr)
        raise DownloaderError(f"yt-dlp failed for {url}") from e
    except subprocess.TimeoutExpired as e:
        logger.error("yt-dlp timed out for %s", url)
        raise DownloaderError(f"yt-dlp timed out for {url}") from e

    info_path = os.path.join(output_dir, f"{video_id}.info.json")
    if not os.path.exists(info_path):
        raise DownloaderError(f"Info JSON not found at {info_path}")

    with open(info_path, "r", encoding="utf-8") as f:
        info = json.load(f)

    title = info.get("title", "Unknown Title")
    uploader = info.get("uploader")
    upload_date_raw = info.get("upload_date")
    upload_date = (
        f"{upload_date_raw[:4]}-{upload_date_raw[4:6]}-{upload_date_raw[6:]}"
        if upload_date_raw and len(upload_date_raw) == 8
        else None
    )
    description = info.get("description", "")
    description_preview = description[:500] if description else ""

    speaker, designation = guess_speaker(description_preview)

    sub_path_json3 = os.path.join(output_dir, f"{video_id}.en.json3")
    transcript_text = ""
    transcript_path = os.path.join(output_dir, f"{video_id}.transcript.txt")
    if os.path.exists(sub_path_json3):
        transcript_text = convert_json3_to_text(sub_path_json3, transcript_path)
    else:
        logger.warning("No English subtitles found for %s", video_id)
        with open(transcript_path, "w", encoding="utf-8") as f:
            pass

    meta_path = os.path.join(output_dir, f"{video_id}.meta.json")
    meta_data = {
        "title": title,
        "uploader": uploader,
        "upload_date": upload_date,
        "description_preview": description_preview,
        "speaker": speaker,
        "designation": designation,
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, indent=2, ensure_ascii=False)

    content_hash = hashlib.sha256(transcript_text.encode("utf-8")).hexdigest()
    state = "discovered" if speaker is None else "downloaded"
    now_iso = datetime.utcnow().isoformat()

    cursor.execute(
        """
        INSERT INTO content (
            content_id, source_type, url, title, speaker, designation, published_at,
            content_hash, file_path, state, last_processed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            content_id,
            "youtube",
            url,
            title,
            speaker,
            designation,
            upload_date,
            content_hash,
            transcript_path,
            state,
            now_iso,
        ),
    )
    logger.info(
        "Successfully processed YouTube video %s (content_id: %s)", url, content_id
    )
