"""
Reaper for YC Skills Forge.
Recovers stale items stuck in the 'extracting' state.
"""

import logging
import sqlite3
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


def run_reaper(db_path: str = "data/registry.db") -> int:
    """
    Finds items in 'extracting' state older than 2 hours.
    Resets them to 'chunked' and increments retry_count.
    If retry_count > 3, marks them as 'failed'.

    Returns the number of items recovered/failed.
    """
    threshold_time = datetime.now(timezone.utc) - timedelta(hours=2)
    threshold_iso = threshold_time.isoformat()

    recovered_count = 0
    try:
        with sqlite3.connect(db_path) as conn:
            conn.isolation_level = "EXCLUSIVE"
            cursor = conn.cursor()

            # Find stale items
            cursor.execute(
                "SELECT content_id, retry_count, last_processed FROM content WHERE state = 'extracting' AND last_processed < ?",
                (threshold_iso,),
            )
            stale_items = cursor.fetchall()

            if not stale_items:
                logger.info("Reaper found no stale items in 'extracting' state.")
                return 0

            logger.info(
                "Reaper found %d stale item(s). Processing...", len(stale_items)
            )

            for content_id, retry_count, last_processed in stale_items:
                # Handle possible null retry_count
                current_retry = retry_count if retry_count is not None else 0
                new_retry = current_retry + 1

                if new_retry > 3:
                    new_state = "failed"
                    logger.warning(
                        "Item %s failed %d times. Marking as 'failed'.",
                        content_id,
                        new_retry,
                    )
                else:
                    new_state = "chunked"
                    logger.info(
                        "Recovering item %s (retry %d/3) to 'chunked' state.",
                        content_id,
                        new_retry,
                    )

                cursor.execute(
                    "UPDATE content SET state = ?, retry_count = ? WHERE content_id = ?",
                    (new_state, new_retry, content_id),
                )
                recovered_count += 1

            return recovered_count

    except sqlite3.Error as e:
        logger.error("Database error during reaper execution: %s", e)
        raise
