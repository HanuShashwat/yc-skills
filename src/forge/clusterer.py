"""
Clustering stage for OpenYC Skills.
Groups extracted advice into clusters using local sentence-transformers.
"""

import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any

from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity

from src.config import load_config

logger = logging.getLogger(__name__)

# Global model cache to avoid reloading
_MODEL = None


def get_model(model_name: str) -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        logger.info("Loading sentence-transformers model %s...", model_name)
        _MODEL = SentenceTransformer(model_name)
    return _MODEL


def run_clustering(batch_id: str, db_path: str = "data/registry.db") -> None:
    """
    Runs the clustering stage for a batch of extracted items.
    """
    config = load_config()
    model_name = config.pipeline.clustering.embedding_model
    distance_threshold = config.pipeline.clustering.distance_threshold
    metric = config.pipeline.clustering.metric
    linkage = config.pipeline.clustering.linkage
    min_cluster_size = config.pipeline.clustering.min_cluster_size

    # 1. Fetch extracted_items and their retry_counts
    items: List[Dict[str, Any]] = []
    content_ids = set()

    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT 
                    e.item_id, 
                    e.quote, 
                    e.speaker, 
                    e.topic, 
                    c.content_id, 
                    c.retry_count
                FROM extracted_items e
                JOIN chunks ch ON e.chunk_id = ch.chunk_id
                JOIN content c ON ch.content_id = c.content_id
                WHERE e.batch_id = ?
            """,
                (batch_id,),
            )

            for row in cursor.fetchall():
                items.append(dict(row))
                content_ids.add(row["content_id"])

    except sqlite3.Error as e:
        logger.error("Database error while loading extracted items: %s", e)
        raise

    if not items:
        logger.warning("No extracted items found for batch %s.", batch_id)
        # Update content states anyway if possible?
        return

    # 2. Embed quotes
    model = get_model(model_name)
    quotes = [item["quote"] for item in items]
    embeddings = model.encode(quotes, convert_to_tensor=False)

    # 3. Compute pairwise cosine similarity matrix
    # cosine_similarity expects 2D array, embeddings is 2D
    sim_matrix = cosine_similarity(embeddings)

    # 4. AgglomerativeClustering
    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distance_threshold,
        metric=metric,
        linkage=linkage,
    )
    labels = clustering.fit_predict(embeddings)

    # Group items by cluster label
    clusters_dict: Dict[int, List[int]] = {}
    for idx, label in enumerate(labels):
        if label not in clusters_dict:
            clusters_dict[label] = []
        clusters_dict[label].append(idx)

    now_iso = datetime.now(timezone.utc).isoformat()

    successful_content_ids = set(content_ids)
    rejected_content_ids = set()

    db_clusters = []
    db_cluster_items = []

    for label, item_indices in clusters_dict.items():
        is_escape_hatch = False

        # Check if it should be rejected
        if len(item_indices) < min_cluster_size:
            # It's a singleton (or smaller than min_cluster_size)
            # Check escape hatch: all items in this cluster must have retry_count >= 3
            # In a singleton, there's only 1 item.
            can_escape = all(items[idx]["retry_count"] >= 3 for idx in item_indices)
            if can_escape:
                is_escape_hatch = True
                logger.info(
                    "Cluster %d (size %d) is using escape hatch (retry >= 3)",
                    label,
                    len(item_indices),
                )
            else:
                # Reject this cluster
                logger.info(
                    "Cluster %d (size %d) rejected. Returning items to pool.",
                    label,
                    len(item_indices),
                )
                for idx in item_indices:
                    rejected_content_ids.add(items[idx]["content_id"])
                    if items[idx]["content_id"] in successful_content_ids:
                        successful_content_ids.remove(items[idx]["content_id"])
                continue

        # Cluster is accepted (either >= min_cluster_size or escape hatch)
        cluster_id = str(uuid.uuid4())

        # Compute summary
        topic = items[item_indices[0]]["topic"]
        speakers = list(set(items[idx]["speaker"] for idx in item_indices))
        summary = f"{topic.title()} advice from {', '.join(speakers)}"
        if is_escape_hatch:
            summary += " [HUMAN_REVIEW: TRUE, CONFIDENCE: 0.55]"

        # Select representative quote (longest)
        longest_quote = ""
        for idx in item_indices:
            if len(items[idx]["quote"]) > len(longest_quote):
                longest_quote = items[idx]["quote"]

        # Compute avg_similarity
        if len(item_indices) > 1:
            # Average pairwise cosine similarity of all items in the cluster
            total_sim = 0.0
            pairs = 0
            for i in range(len(item_indices)):
                for j in range(i + 1, len(item_indices)):
                    idx_i = item_indices[i]
                    idx_j = item_indices[j]
                    total_sim += sim_matrix[idx_i, idx_j]
                    pairs += 1
            avg_sim = total_sim / pairs
        else:
            avg_sim = 1.0  # Singleton

        db_clusters.append(
            (
                cluster_id,
                batch_id,
                topic,
                summary,
                len(item_indices),
                float(avg_sim),
                longest_quote,
                now_iso,
            )
        )

        for idx in item_indices:
            db_cluster_items.append(
                (
                    cluster_id,
                    items[idx]["item_id"],
                    float(
                        sim_matrix[item_indices[0], idx]
                    ),  # Just store similarity to the first item for now, or 1.0 if self
                )
            )

    # Database transaction
    try:
        with sqlite3.connect(db_path) as conn:
            conn.isolation_level = "EXCLUSIVE"
            cursor = conn.cursor()

            # Insert clusters
            cursor.executemany(
                """
                INSERT INTO clusters (
                    cluster_id, batch_id, topic, summary, item_count, avg_similarity, representative_quote, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                db_clusters,
            )

            # Insert cluster items
            cursor.executemany(
                """
                INSERT INTO cluster_items (
                    cluster_id, item_id, similarity_score
                ) VALUES (?, ?, ?)
            """,
                db_cluster_items,
            )

            # Update states
            if successful_content_ids:
                placeholders = ",".join("?" * len(successful_content_ids))
                cursor.execute(
                    f"""
                    UPDATE content 
                    SET state = 'clustered'
                    WHERE content_id IN ({placeholders})
                """,
                    list(successful_content_ids),
                )

            # Any item currently 'extracted' but not successful should be rejected (back to 'chunked')
            cursor.execute("SELECT content_id FROM content WHERE state = 'extracted'")
            all_extracted = set(row[0] for row in cursor.fetchall())
            rejected_content_ids.update(all_extracted - successful_content_ids)

            if rejected_content_ids:
                placeholders = ",".join("?" * len(rejected_content_ids))
                cursor.execute(
                    f"""
                    UPDATE content 
                    SET state = 'chunked', retry_count = retry_count + 1
                    WHERE content_id IN ({placeholders})
                """,
                    list(rejected_content_ids),
                )

    except sqlite3.Error as e:
        logger.error("Database error during cluster insertion: %s", e)
        raise
