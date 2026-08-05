"""
Extraction stage for YC Skills Forge.
Extracts actionable advice from content chunks using an LLM.
"""

import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import List

from jinja2 import Environment, FileSystemLoader
from pydantic import ValidationError

from src.config import load_config
from src.forge.llm_client import LLMClient
from src.models import ExtractionResponse

logger = logging.getLogger(__name__)


def run_extraction(
    batch_id: str, content_ids: List[str], db_path: str = "data/registry.db"
) -> None:
    """
    Runs the extraction stage for a batch of content items.

    1) Loads chunks for batch content IDs.
    2) Renders extract.j2 prompt.
    3) Calls LLM to extract advice.
    4) Parses JSON response.
    5) Inserts into extracted_items table.
    6) Updates content state to 'extracted'.
    """
    if not content_ids:
        logger.warning("No content IDs provided for extraction batch %s", batch_id)
        return

    config = load_config()
    topics = list(config.taxonomy.taxonomy.keys())
    temperature = config.pipeline.extraction.temperature

    chunks_data = []
    chunk_id_map = {}  # Maps in_batch_index (1-based) to chunk_id

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            placeholders = ",".join("?" * len(content_ids))

            # Fetch chunks and join with content to get url, speaker, designation
            query = f"""
                SELECT 
                    ch.chunk_id, 
                    ch.content_id, 
                    c.url, 
                    c.speaker, 
                    c.designation, 
                    ch.timestamp_start, 
                    ch.timestamp_end, 
                    ch.text
                FROM chunks ch
                JOIN content c ON ch.content_id = c.content_id
                WHERE ch.content_id IN ({placeholders})
                ORDER BY ch.content_id, ch.chunk_index
            """
            cursor.execute(query, content_ids)
            rows = cursor.fetchall()

            if not rows:
                logger.warning(
                    "No chunks found for the given content IDs in batch %s.", batch_id
                )
                return

            # Build chunks_data list
            for i, row in enumerate(rows, start=1):
                chunk_id, cid, url, speaker, designation, ts_start, ts_end, text = row
                chunk_id_map[i] = chunk_id
                chunks_data.append(
                    {
                        "chunk_id": chunk_id,
                        "content_id": cid,
                        "url": url,
                        "speaker": speaker or "Unknown Speaker",
                        "designation": designation or "Unknown Designation",
                        "timestamp_start": ts_start,
                        "timestamp_end": ts_end,
                        "text": text,
                    }
                )

    except sqlite3.Error as e:
        logger.error("Database error while loading chunks: %s", e)
        raise

    env = Environment(loader=FileSystemLoader("src/forge/prompts"))
    template = env.get_template("extract.j2")
    prompt = template.render(chunks=chunks_data, topics=topics)

    llm = LLMClient()
    response_text = None
    extraction = None

    def parse_response(text: str) -> ExtractionResponse:
        try:
            data = json.loads(text)
            return ExtractionResponse(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(f"Parse error: {e}")

    try:
        response_text = llm.call(
            prompt=prompt, call_type="extract", temperature=temperature
        )
        extraction = parse_response(response_text)
    except Exception as e:
        logger.warning(
            "Failed initial extraction parsing for batch %s: %s", batch_id, e
        )
        if response_text:
            os.makedirs("data/errors", exist_ok=True)
            error_file = f"data/errors/{batch_id}.json"
            try:
                with open(error_file, "w", encoding="utf-8") as f:
                    f.write(response_text)
                logger.info("Saved raw failed response to %s", error_file)
            except IOError as io_e:
                logger.error("Failed to write error file: %s", io_e)

        logger.info("Retrying extraction with temperature 0.1...")
        try:
            response_text = llm.call(
                prompt=prompt, call_type="extract", temperature=0.1
            )
            extraction = parse_response(response_text)
        except Exception as retry_e:
            logger.error("Retry failed for batch %s: %s", batch_id, retry_e)
            raise

    if not extraction:
        logger.error("Extraction resulted in None for batch %s", batch_id)
        return

    now_iso = datetime.now(timezone.utc).isoformat()

    try:
        with sqlite3.connect(db_path) as conn:
            conn.isolation_level = "EXCLUSIVE"
            cursor = conn.cursor()

            for item in extraction.extracted_items:
                chunk_id = chunk_id_map.get(item.in_batch_index)
                if not chunk_id:
                    logger.warning(
                        "LLM returned invalid in_batch_index %d. Skipping item.",
                        item.in_batch_index,
                    )
                    continue

                item_id = str(uuid.uuid4())
                is_framework = 1 if item.type == "framework" else 0
                is_warning = 1 if item.type == "warning" else 0

                cursor.execute(
                    """
                    INSERT INTO extracted_items (
                        item_id, batch_id, chunk_id, in_batch_index, quote, speaker, 
                        designation, topic, source_url, is_framework, is_warning, extraction_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item_id,
                        batch_id,
                        chunk_id,
                        item.in_batch_index,
                        item.quote,
                        item.speaker,
                        item.designation,
                        item.topic,
                        str(item.source_url),
                        is_framework,
                        is_warning,
                        now_iso,
                    ),
                )

            # Update content state to 'extracted'
            placeholders = ",".join("?" * len(content_ids))
            update_query = f"""
                UPDATE content 
                SET state = 'extracted'
                WHERE content_id IN ({placeholders})
            """
            cursor.execute(update_query, content_ids)

            logger.info(
                "Successfully extracted %d items for batch %s",
                len(extraction.extracted_items),
                batch_id,
            )

    except sqlite3.Error as e:
        logger.error("Database error during extraction insertion: %s", e)
        raise
