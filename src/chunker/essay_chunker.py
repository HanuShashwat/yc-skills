"""
Essay chunker for YC Skills Forge.
"""

import logging
import os
import re
import sqlite3
from typing import List

from src.config import load_config
from src.models import ChunkData

logger = logging.getLogger(__name__)

CHUNK_OUTPUT_DIR = "data/chunks/library"


def get_sentences(text: str) -> List[str]:
    """Split text into sentences using a simple regex heuristic."""
    # Split by punctuation (.!?) followed by whitespace or end of string
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text.strip())
    # Fallback to simple split if the lookahead doesn't match perfectly
    if len(sentences) <= 1:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


def get_paragraphs(text: str) -> List[str]:
    """Split text into paragraphs."""
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def get_word_count(text: str) -> int:
    """Get the word count of a string."""
    return len(text.split())


def chunk_essay(
    content_id: str, markdown_text: str, speaker: str | None, db_path: str
) -> None:
    """
    Chunk an essay according to the architecture specification.

    Args:
        content_id: The ID of the source content.
        markdown_text: The full markdown text of the essay.
        speaker: The speaker of the essay, if known.
        db_path: Path to the SQLite database.
    """
    config = load_config()
    chunk_config = config.pipeline.chunking.essay

    split_header = chunk_config.split_header
    min_words = chunk_config.min_words
    max_words = chunk_config.max_words
    target_words = chunk_config.target_words
    overlap_sentences = chunk_config.overlap_sentences

    # 1 & 2 & 3. Split by split_header. Each section is a candidate chunk.
    pattern = rf"^{re.escape(split_header)}"
    parts = re.split(pattern, markdown_text, flags=re.MULTILINE)

    candidate_chunks = []
    if parts[0].strip():
        candidate_chunks.append(parts[0].strip())
    for p in parts[1:]:
        candidate_chunks.append((split_header + p).strip())

    if not candidate_chunks:
        logger.warning("No content found for %s", content_id)
        return

    # 4. Merge candidates < 200 words
    merged_chunks = []
    current_merged = ""
    for chunk in candidate_chunks:
        if not current_merged:
            current_merged = chunk
        else:
            if get_word_count(current_merged) < min_words:
                current_merged += "\n\n" + chunk
            else:
                merged_chunks.append(current_merged)
                current_merged = chunk

    if current_merged:
        merged_chunks.append(current_merged)

    # Backward merge the last chunk if it's too small and we have a previous chunk
    # (Though prompt just says "merge with next until >= 200", usually the last piece gets stranded)
    if len(merged_chunks) > 1 and get_word_count(merged_chunks[-1]) < min_words:
        last = merged_chunks.pop()
        merged_chunks[-1] += "\n\n" + last

    # 5. Split candidates > 800 words
    final_chunks = []
    for chunk in merged_chunks:
        if get_word_count(chunk) > max_words:
            paragraphs = get_paragraphs(chunk)
            sub_chunk = ""
            for p in paragraphs:
                if not sub_chunk:
                    sub_chunk = p
                else:
                    if get_word_count(sub_chunk) + get_word_count(p) > target_words:
                        final_chunks.append(sub_chunk)
                        sub_chunk = p
                    else:
                        sub_chunk += "\n\n" + p
            if sub_chunk:
                final_chunks.append(sub_chunk)
        else:
            final_chunks.append(chunk)

    # 6. Apply overlap
    overlapped_chunks = []
    prev_last_sentence = ""

    for chunk in final_chunks:
        text = chunk
        if prev_last_sentence and overlap_sentences > 0:
            text = prev_last_sentence + " " + text

        overlapped_chunks.append(text)

        sentences = get_sentences(
            chunk
        )  # Take from original chunk, not overlapped text
        if sentences:
            prev_last_sentence = " ".join(sentences[-overlap_sentences:])
        else:
            prev_last_sentence = ""

    # 7. Save records and insert into DB
    os.makedirs(CHUNK_OUTPUT_DIR, exist_ok=True)

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            for i, chunk_text in enumerate(overlapped_chunks):
                chunk_index = i
                chunk_id = f"{content_id}_{chunk_index:04d}"
                word_count = get_word_count(chunk_text)
                char_count = len(chunk_text)

                chunk_data = ChunkData(
                    chunk_id=chunk_id,
                    content_id=content_id,
                    chunk_index=chunk_index,
                    text=chunk_text,
                    word_count=word_count,
                    char_count=char_count,
                    speaker=speaker,
                    timestamp_start=None,
                    timestamp_end=None,
                )

                # Save to JSON file
                json_path = os.path.join(CHUNK_OUTPUT_DIR, f"{chunk_id}.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    f.write(chunk_data.model_dump_json(indent=2))

                # Insert into database
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
                        chunk_text,
                        word_count,
                        char_count,
                        speaker,
                        None,
                        None,
                    ),
                )

            # Update state in content table
            cursor.execute(
                "UPDATE content SET state = 'chunked' WHERE content_id = ?",
                (content_id,),
            )
            conn.commit()
            logger.info(
                "Successfully created %d chunks for %s",
                len(overlapped_chunks),
                content_id,
            )

    except sqlite3.Error as e:
        logger.error("Database error saving chunks for %s: %s", content_id, e)
        raise
