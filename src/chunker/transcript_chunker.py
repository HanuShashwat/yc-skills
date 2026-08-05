"""
Transcript chunker for YC Skills Forge.
"""

import logging
import os
import re
import sqlite3

from src.config import load_config
from src.models import ChunkData

logger = logging.getLogger(__name__)

CHUNK_OUTPUT_DIR = "data/chunks/youtube"


def get_word_count(text: str) -> int:
    """Get the word count of a string."""
    return len(text.split())


def parse_transcript_line(line: str) -> tuple[str | None, str | None, str]:
    """Parse a transcript line into timestamp, speaker, and text."""
    # Match [HH:MM:SS] Speaker: Text or [HH:MM:SS] Text
    m = re.match(r"^\[(\d{2}:\d{2}:\d{2})\]\s*(?:([A-Za-z\s]+):\s*)?(.*)", line)
    if m:
        ts = m.group(1)
        spk = m.group(2)
        text = m.group(3)
        return ts, spk, text
    return None, None, line


def chunk_transcript(
    content_id: str, file_path: str, default_speaker: str | None, db_path: str
) -> None:
    """
    Chunk a transcript according to the architecture specification.

    Args:
        content_id: The ID of the source content.
        file_path: The path to the plain text transcript file.
        default_speaker: The primary speaker to use if labels are missing.
        db_path: Path to the SQLite database.
    """
    config = load_config()
    chunk_config = config.pipeline.chunking.transcript

    max_words = chunk_config.max_words
    target_words = chunk_config.target_words
    merge_same_speaker = chunk_config.merge_same_speaker
    split_on_speaker_change = chunk_config.split_on_speaker_change

    segments = []

    # 1. Read transcript.
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ts, spk, text = parse_transcript_line(line)
            segments.append(
                {
                    "timestamp": ts,
                    "speaker": spk if spk else default_speaker,
                    "text": text,
                }
            )

    if not segments:
        logger.warning("No segments found in transcript for %s", content_id)
        return

    # 2 & 3. Group by speaker and merge.
    monologues = []
    current_monologue = []

    for seg in segments:
        if not current_monologue:
            current_monologue.append(seg)
        else:
            same_speaker = seg["speaker"] == current_monologue[-1]["speaker"]

            if same_speaker and merge_same_speaker:
                current_monologue.append(seg)
            elif not same_speaker and split_on_speaker_change:
                monologues.append(current_monologue)
                current_monologue = [seg]
            else:
                current_monologue.append(seg)

    if current_monologue:
        monologues.append(current_monologue)

    # 4. Split large monologues
    final_chunks = []
    for mono in monologues:
        mono_wc = sum(get_word_count(s["text"]) for s in mono)
        if mono_wc <= max_words:
            final_chunks.append(mono)
        else:
            current_sub = []
            current_wc = 0
            for seg in mono:
                current_sub.append(seg)
                current_wc += get_word_count(seg["text"])

                if current_wc >= target_words:
                    ends_with_boundary = bool(
                        re.search(r'[.!?]["\']?\s*$', seg["text"])
                    )
                    if ends_with_boundary or current_wc >= max_words:
                        final_chunks.append(current_sub)
                        current_sub = []
                        current_wc = 0
            if current_sub:
                final_chunks.append(current_sub)

    # 5. Save chunks
    os.makedirs(CHUNK_OUTPUT_DIR, exist_ok=True)

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            for i, chunk_segs in enumerate(final_chunks):
                if not chunk_segs:
                    continue

                chunk_index = i
                chunk_id = f"{content_id}_{chunk_index:04d}"
                text = " ".join(s["text"] for s in chunk_segs)
                word_count = get_word_count(text)
                char_count = len(text)
                speaker = chunk_segs[0]["speaker"]

                # Find start and end timestamps.
                timestamps = [s["timestamp"] for s in chunk_segs if s["timestamp"]]
                timestamp_start = timestamps[0] if timestamps else None
                timestamp_end = timestamps[-1] if timestamps else None

                chunk_data = ChunkData(
                    chunk_id=chunk_id,
                    content_id=content_id,
                    chunk_index=chunk_index,
                    text=text,
                    word_count=word_count,
                    char_count=char_count,
                    speaker=speaker,
                    timestamp_start=timestamp_start,
                    timestamp_end=timestamp_end,
                )

                json_path = os.path.join(CHUNK_OUTPUT_DIR, f"{chunk_id}.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    f.write(chunk_data.model_dump_json(indent=2))

                cursor.execute(
                    """
                    INSERT INTO chunks (
                        chunk_id, content_id, chunk_index, text, word_count, char_count, speaker, timestamp_start, timestamp_end
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        chunk_id,
                        content_id,
                        chunk_index,
                        text,
                        word_count,
                        char_count,
                        speaker,
                        timestamp_start,
                        timestamp_end,
                    ),
                )

            cursor.execute(
                "UPDATE content SET state = 'chunked' WHERE content_id = ?",
                (content_id,),
            )
            conn.commit()
            logger.info(
                "Successfully created %d chunks for %s", len(final_chunks), content_id
            )

    except sqlite3.Error as e:
        logger.error("Database error saving chunks for %s: %s", content_id, e)
        raise
