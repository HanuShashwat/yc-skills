"""
Tests for clustering stage.
"""
import sqlite3
import sys
from unittest.mock import patch, MagicMock
import numpy as np
import pytest

# Mock modules that might not be installed
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['sklearn'] = MagicMock()
sys.modules['sklearn.cluster'] = MagicMock()
sys.modules['sklearn.metrics'] = MagicMock()
sys.modules['sklearn.metrics.pairwise'] = MagicMock()

# Now we can import
from src.forge.clusterer import run_clustering  # noqa: E402


@pytest.fixture
def db_path(tmp_path):
    db_file = tmp_path / "test_cluster.db"
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
                topic_guess TEXT,
                retry_count INTEGER DEFAULT 0,
                last_processed TEXT,
                error_message TEXT
            );
            
            CREATE TABLE chunks (
                chunk_id TEXT PRIMARY KEY,
                content_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                word_count INTEGER NOT NULL,
                char_count INTEGER NOT NULL,
                speaker TEXT,
                timestamp_start TEXT,
                timestamp_end TEXT,
                FOREIGN KEY (content_id) REFERENCES content(content_id)
            );
            
            CREATE TABLE extracted_items (
                item_id TEXT PRIMARY KEY,
                batch_id TEXT NOT NULL,
                chunk_id TEXT NOT NULL,
                in_batch_index INTEGER NOT NULL,
                quote TEXT NOT NULL,
                speaker TEXT NOT NULL,
                designation TEXT,
                topic TEXT NOT NULL,
                source_url TEXT NOT NULL,
                is_framework INTEGER NOT NULL CHECK(is_framework IN (0, 1)),
                is_warning INTEGER NOT NULL CHECK(is_warning IN (0, 1)),
                extraction_date TEXT NOT NULL
            );
            
            CREATE TABLE clusters (
                cluster_id TEXT PRIMARY KEY,
                batch_id TEXT NOT NULL,
                topic TEXT NOT NULL,
                summary TEXT NOT NULL,
                item_count INTEGER NOT NULL,
                avg_similarity REAL,
                representative_quote TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            
            CREATE TABLE cluster_items (
                cluster_id TEXT NOT NULL,
                item_id TEXT NOT NULL,
                similarity_score REAL NOT NULL,
                PRIMARY KEY (cluster_id, item_id)
            );
            """
        )
    return str(db_file)


@pytest.fixture
def setup_data(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # 3 contents
        cursor.execute("INSERT INTO content (content_id, source_type, url, title, content_hash, file_path, state, retry_count) VALUES ('c1', 'library', 'u1', 't1', 'h1', 'p1', 'extracted', 0)")
        cursor.execute("INSERT INTO content (content_id, source_type, url, title, content_hash, file_path, state, retry_count) VALUES ('c2', 'library', 'u2', 't2', 'h2', 'p2', 'extracted', 0)")
        # c3 has retry_count = 3 (for escape hatch)
        cursor.execute("INSERT INTO content (content_id, source_type, url, title, content_hash, file_path, state, retry_count) VALUES ('c3', 'library', 'u3', 't3', 'h3', 'p3', 'extracted', 3)")
        
        # chunks
        cursor.execute("INSERT INTO chunks (chunk_id, content_id, chunk_index, text, word_count, char_count) VALUES ('ch1', 'c1', 0, 'text', 10, 50)")
        cursor.execute("INSERT INTO chunks (chunk_id, content_id, chunk_index, text, word_count, char_count) VALUES ('ch2', 'c2', 0, 'text', 10, 50)")
        cursor.execute("INSERT INTO chunks (chunk_id, content_id, chunk_index, text, word_count, char_count) VALUES ('ch3', 'c3', 0, 'text', 10, 50)")
        
        # extracted items
        cursor.execute("INSERT INTO extracted_items (item_id, batch_id, chunk_id, in_batch_index, quote, speaker, topic, source_url, is_framework, is_warning, extraction_date) VALUES ('i1', 'b1', 'ch1', 1, 'Quote A', 'S1', 'fundraising', 'u', 0, 0, 'd')")
        cursor.execute("INSERT INTO extracted_items (item_id, batch_id, chunk_id, in_batch_index, quote, speaker, topic, source_url, is_framework, is_warning, extraction_date) VALUES ('i2', 'b1', 'ch1', 2, 'Quote B', 'S1', 'fundraising', 'u', 0, 0, 'd')")
        cursor.execute("INSERT INTO extracted_items (item_id, batch_id, chunk_id, in_batch_index, quote, speaker, topic, source_url, is_framework, is_warning, extraction_date) VALUES ('i3', 'b1', 'ch2', 1, 'Quote C', 'S2', 'fundraising', 'u', 0, 0, 'd')")
        cursor.execute("INSERT INTO extracted_items (item_id, batch_id, chunk_id, in_batch_index, quote, speaker, topic, source_url, is_framework, is_warning, extraction_date) VALUES ('i4', 'b1', 'ch3', 1, 'Quote D', 'S3', 'fundraising', 'u', 0, 0, 'd')")
        
        conn.commit()
    return db_path


class DummyModel:
    def encode(self, quotes, convert_to_tensor=False):
        # We want i1 and i2 to cluster together (distance < threshold).
        # We want i3 to be far from i1 and i2 (distance > threshold).
        # We want i4 to be far from everyone, but it has retry_count=3, so escape hatch.
        # Threshold is 0.18.
        # Vector A = [1, 0, 0]
        # Vector B = [0.99, 0.1, 0] -> cosine sim to A is ~0.995 (dist = 0.005)
        # Vector C = [0, 1, 0] -> cosine sim to A, B is ~0 (dist = 1.0)
        # Vector D = [0, 0, 1] -> cosine sim to A, B, C is ~0 (dist = 1.0)
        
        embeddings = []
        for q in quotes:
            if q == 'Quote A':
                embeddings.append([1.0, 0.0, 0.0])
            elif q == 'Quote B':
                embeddings.append([0.99, 0.1, 0.0])
            elif q == 'Quote C':
                embeddings.append([0.0, 1.0, 0.0])
            elif q == 'Quote D':
                embeddings.append([0.0, 0.0, 1.0])
            else:
                embeddings.append([0.0, 0.0, 0.0])
        return np.array(embeddings)


@patch("src.forge.clusterer.get_model")
@patch("src.forge.clusterer.cosine_similarity")
@patch("src.forge.clusterer.AgglomerativeClustering")
def test_run_clustering(mock_agg, mock_cosine, mock_get_model, setup_data):
    mock_get_model.return_value = DummyModel()
    
    # Mock cosine similarity matrix
    mock_cosine.return_value = np.array([
        [1.0, 0.995, 0.0, 0.0],
        [0.995, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ])
    
    # Mock clustering labels
    # i1, i2 -> cluster 0
    # i3 -> cluster 1 (will be rejected because size < 2)
    # i4 -> cluster 2 (escape hatch because size < 2 and retry_count=3)
    mock_clustering_instance = MagicMock()
    mock_clustering_instance.fit_predict.return_value = np.array([0, 0, 1, 2])
    mock_agg.return_value = mock_clustering_instance
    
    run_clustering("b1", setup_data)
    
    with sqlite3.connect(setup_data) as conn:
        cursor = conn.cursor()
        
        # i1 and i2 should form a cluster (c1 content should be 'clustered')
        # i3 should be rejected (c2 content should be 'chunked' and retry_count=1)
        # i4 should use escape hatch (c3 content should be 'clustered')
        
        cursor.execute("SELECT content_id, state, retry_count FROM content ORDER BY content_id")
        rows = cursor.fetchall()
        assert rows[0] == ("c1", "clustered", 0)  # i1, i2 successful
        assert rows[1] == ("c2", "chunked", 1)    # i3 rejected -> pool
        assert rows[2] == ("c3", "clustered", 3)  # i4 escape hatch
        
        cursor.execute("SELECT summary, item_count, avg_similarity FROM clusters")
        clusters = cursor.fetchall()
        
        assert len(clusters) == 2
        
        cluster_sizes = sorted([c[1] for c in clusters])
        assert cluster_sizes == [1, 2]
        
        for summary, item_count, avg_sim in clusters:
            if item_count == 1:
                assert "HUMAN_REVIEW: TRUE" in summary
                assert "CONFIDENCE: 0.55" in summary
                assert avg_sim == 1.0
            else:
                assert "HUMAN_REVIEW" not in summary
                assert avg_sim > 0.9  # approx 0.995

def test_run_clustering_empty(db_path):
    run_clustering("b_empty", db_path)
