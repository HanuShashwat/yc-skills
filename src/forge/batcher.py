"""
Batch selector for YC Skills Forge.
"""
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class BatchSelectionError(Exception):
    """Exception raised for errors in the batch selection process."""
    pass


def select_batch(db_path: str = "data/registry.db", topic: Optional[str] = None, batch_size: int = 15) -> Tuple[str, List[str]]:
    """
    Selects a batch of content items for advice extraction.
    
    Algorithm:
    1. Query content for state = 'chunked'.
    2. Filter by topic if provided.
    3. If no topic -> pick topic with most unprocessed chunks.
    4. Randomly select up to batch_size items (bound 5-20).
    5. If < 5 items -> log warning, abort.
    6. Set state -> 'extracting', update last_processed.
    7. Return batch_id and content_id list.
    """
    batch_size = min(max(batch_size, 5), 20)  # Bound between 5 and 20

    try:
        with sqlite3.connect(db_path) as conn:
            # Use EXCLUSIVE isolation level to ensure atomic transactions
            conn.isolation_level = "EXCLUSIVE"
            cursor = conn.cursor()
            
            target_topic = topic
            if not target_topic:
                # Pick the topic with the most unprocessed chunks
                cursor.execute("""
                    SELECT topic_guess, COUNT(*) as cnt 
                    FROM content 
                    WHERE state = 'chunked' AND topic_guess IS NOT NULL
                    GROUP BY topic_guess 
                    ORDER BY cnt DESC 
                    LIMIT 1
                """)
                result = cursor.fetchone()
                if not result:
                    logger.warning("No unextracted content found.")
                    raise BatchSelectionError("No unextracted content found.")
                target_topic = result[0]
                
            # Randomly select up to batch_size items
            cursor.execute("""
                SELECT content_id 
                FROM content 
                WHERE state = 'chunked' AND topic_guess = ?
                ORDER BY RANDOM()
                LIMIT ?
            """, (target_topic, batch_size))
            
            content_ids = [row[0] for row in cursor.fetchall()]
            
            if len(content_ids) < 5:
                logger.warning("Only %d items found for topic '%s'. Minimum batch size is 5. Aborting.", len(content_ids), target_topic)
                raise BatchSelectionError(f"Insufficient items for topic '{target_topic}' (found {len(content_ids)}, need 5).")
                
            batch_id = str(uuid.uuid4())
            now_iso = datetime.now(timezone.utc).isoformat()
            
            # Update state to extracting
            placeholders = ",".join("?" * len(content_ids))
            update_query = f"""
                UPDATE content 
                SET state = 'extracting', last_processed = ?
                WHERE content_id IN ({placeholders})
            """
            params = [now_iso] + content_ids
            cursor.execute(update_query, params)
            
            logger.info("Selected batch %s with %d items for topic '%s'", batch_id, len(content_ids), target_topic)
            return batch_id, content_ids
            
    except sqlite3.Error as e:
        logger.error("Database error during batch selection: %s", e)
        raise
