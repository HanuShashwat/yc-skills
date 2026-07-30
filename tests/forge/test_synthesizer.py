"""
Tests for synthesizer stage.
"""
import os
import sqlite3
from unittest.mock import patch, MagicMock

import pytest
import yaml

from src.forge.synthesizer import (
    run_synthesis, 
    ensure_unique_skill_id, 
    slugify, 
    get_category_for_topic
)

@pytest.fixture
def db_path(tmp_path):
    db_file = tmp_path / "test_synth.db"
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
            
            CREATE TABLE skills (
                skill_id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                name TEXT NOT NULL,
                version TEXT NOT NULL DEFAULT '1.0.0',
                file_path TEXT NOT NULL,
                source_count INTEGER NOT NULL,
                quote_count INTEGER NOT NULL,
                related_skills TEXT,
                computed_confidence REAL,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        
        # Insert test data
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO content (content_id, source_type, url, title, content_hash, file_path, state) VALUES ('c1', 'library', 'u1', 't1', 'h1', 'p1', 'clustered')")
        cursor.execute("INSERT INTO chunks (chunk_id, content_id, chunk_index, text, word_count, char_count) VALUES ('ch1', 'c1', 0, 'text', 10, 50)")
        cursor.execute("INSERT INTO extracted_items (item_id, batch_id, chunk_id, in_batch_index, quote, speaker, topic, source_url, is_framework, is_warning, extraction_date) VALUES ('i1', 'b1', 'ch1', 1, 'Quote A', 'S1', 'fundraising', 'u', 0, 0, 'd')")
        
        cursor.execute("INSERT INTO clusters (cluster_id, batch_id, topic, summary, item_count, avg_similarity, representative_quote, created_at) VALUES ('clu1', 'b1', 'seed-round', 'Summary', 2, 0.9, 'Quote A', '2026-07-31')")
        cursor.execute("INSERT INTO cluster_items (cluster_id, item_id, similarity_score) VALUES ('clu1', 'i1', 1.0)")
        
        # Second cluster for escape hatch testing
        cursor.execute("INSERT INTO clusters (cluster_id, batch_id, topic, summary, item_count, avg_similarity, representative_quote, created_at) VALUES ('clu2', 'b2', 'hiring', 'Summary HUMAN_REVIEW: TRUE', 1, 1.0, 'Quote A', '2026-07-31')")
        cursor.execute("INSERT INTO cluster_items (cluster_id, item_id, similarity_score) VALUES ('clu2', 'i1', 1.0)")
        
        conn.commit()
        
    return str(db_file)


def test_slugify():
    assert slugify("Seed Round Timing") == "seed-round-timing"
    assert slugify("  test @#$ STRING  ") == "test-string"


def test_get_category_for_topic():
    # 'seed-round' is a subcategory of 'fundraising'
    assert get_category_for_topic("seed-round") == "fundraising"
    assert get_category_for_topic("fundraising") == "fundraising"
    assert get_category_for_topic("unknown-topic") == "general"


def test_ensure_unique_skill_id(db_path):
    assert ensure_unique_skill_id("yc-test", db_path) == "yc-test"
    
    with sqlite3.connect(db_path) as conn:
        conn.execute("INSERT INTO skills (skill_id, category, name, file_path, source_count, quote_count, computed_confidence, state, created_at, updated_at) VALUES ('yc-test', 'c', 'n', 'f', 1, 1, 1.0, 'draft', 'd', 'd')")
    
    assert ensure_unique_skill_id("yc-test", db_path) == "yc-test_v2"


@patch("src.forge.synthesizer.LLMClient")
def test_run_synthesis_success(mock_llm_client_cls, db_path):
    mock_llm = MagicMock()
    mock_llm_client_cls.return_value = mock_llm
    
    def side_effect(prompt, call_type, temperature, response_format_json, batch_id):
        if not response_format_json:
            return "amazing-descriptor"
        return {
            "skill_id": "yc-a-b",
            "name": "Amazing Skill",
            "category": "fundraising",
            "principle": "This is a principle.",
            "quotes": [
                {
                    "text": "Quote A",
                    "speaker": "S1",
                    "source_url": "u1"
                }
            ],
            "application": {
                "when_to_use": "When testing",
                "actions": ["Act 1"],
                "follow_up_questions": ["Q1?"]
            },
            "edge_cases": ["Edge 1"],
            "related_skills": ["this-should-be-ignored"],
            "confidence": 0.99
        }
    
    mock_llm.call.side_effect = side_effect
    
    run_synthesis("clu1", db_path)
    
    # Verify file created
    expected_path = os.path.join("skills", "fundraising", "yc-fundraising-amazing-descriptor.md")
    assert os.path.exists(expected_path)
    
    with open(expected_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check Markdown format
    assert "## Principle" in content
    assert "This is a principle." in content
    assert "## Verbatim Quotes" in content
    assert "> \"Quote A\"" in content
    assert "## Related Skills" in content
    assert "## Fallback Behavior" in content
    
    # Check frontmatter
    parts = content.split("---")
    assert len(parts) >= 3
    fm = yaml.safe_load(parts[1])
    assert fm["skill_id"] == "yc-fundraising-amazing-descriptor"
    assert fm["related_skills"] == []
    
    # Confidence formula: min(0.99, max(0.55, 0.9*0.5 + (2/10*0.3) + 0.2))
    # 0.45 + 0.06 + 0.2 = 0.71
    assert abs(fm["confidence"] - 0.71) < 0.01
    
    # DB state
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM skills WHERE skill_id = 'yc-fundraising-amazing-descriptor'")
        row = cursor.fetchone()
        assert row is not None


@patch("src.forge.synthesizer.LLMClient")
def test_run_synthesis_escape_hatch(mock_llm_client_cls, db_path):
    mock_llm = MagicMock()
    mock_llm_client_cls.return_value = mock_llm
    
    def side_effect(prompt, call_type, temperature, response_format_json, batch_id):
        if not response_format_json:
            return "hatch"
        return {
            "skill_id": "yc-a-b",
            "name": "Hatch",
            "category": "hiring",
            "principle": "P",
            "quotes": [],
            "application": {},
            "edge_cases": [],
            "related_skills": [],
            "confidence": 0.0
        }
    
    mock_llm.call.side_effect = side_effect
    
    run_synthesis("clu2", db_path)
    
    # Expected conf: avg_sim=1.0, count=1, contra=False
    # 1.0*0.5 + 0.1*0.3 + 0.2 = 0.5 + 0.03 + 0.2 = 0.73
    # Wait, the instruction says "force singleton with computed_confidence = 0.55" for escape hatch!
    # Let's check frontmatter for human_review: True
    
    expected_path = os.path.join("skills", "hiring", "yc-hiring-hatch.md")
    with open(expected_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    fm = yaml.safe_load(content.split("---")[1])
    assert fm["validation"]["human_review"] is True
    assert fm["confidence"] == 0.55


@patch("src.forge.synthesizer.LLMClient")
def test_run_synthesis_llm_fails(mock_llm_client_cls, db_path):
    mock_llm = MagicMock()
    mock_llm_client_cls.return_value = mock_llm
    
    # If JSON is broken or not returned
    mock_llm.call.return_value = "Not JSON"
    
    with pytest.raises(RuntimeError):
        run_synthesis("clu1", db_path)
