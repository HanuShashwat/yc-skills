"""
Tests for deferred linking stage.
"""
import json
import sqlite3
import sys
from unittest.mock import patch, MagicMock

import numpy as np
import pytest
import yaml

# Mock modules that might not be installed
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['sklearn'] = MagicMock()
sys.modules['sklearn.metrics'] = MagicMock()
sys.modules['sklearn.metrics.pairwise'] = MagicMock()

from src.forge.linker import parse_skill_file, run_linker  # noqa: E402

@pytest.fixture
def db_path(tmp_path):
    db_file = tmp_path / "test_linker.db"
    with sqlite3.connect(db_file) as conn:
        conn.executescript(
            """
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
    return str(db_file)

@pytest.fixture
def skill_files(tmp_path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    
    skill_data = [
        ("yc-skill-1", "synthesized", "Skill 1", "Principle 1"),
        ("yc-skill-2", "published", "Skill 2", "Principle 2"),
        ("yc-skill-3", "published", "Skill 3", "Principle 3"),
        ("yc-skill-4", "published", "Skill 4", "Principle 4"),
        ("yc-skill-5", "published", "Skill 5", "Principle 5")
    ]
    
    files = {}
    for sid, state, name, principle in skill_data:
        filepath = skills_dir / f"{sid}.md"
        fm = {
            "skill_id": sid,
            "name": name,
            "related_skills": []
        }
        content = f"---\n{yaml.dump(fm, sort_keys=False, default_flow_style=False).strip()}\n---\n\n# {name}\n\n## Principle\n\n{principle}\n\n## Verbatim Quotes\n"
        filepath.write_text(content, encoding="utf-8")
        files[sid] = (str(filepath), state, name)
        
    return files

def test_parse_skill_file(skill_files):
    filepath = skill_files["yc-skill-1"][0]
    name, principle, fm = parse_skill_file(filepath)
    assert name == "Skill 1"
    assert principle == "Principle 1"
    assert fm["skill_id"] == "yc-skill-1"

@patch("src.forge.linker.cosine_similarity")
@patch("src.forge.linker.SentenceTransformer")
def test_run_linker_success(mock_st_class, mock_cosine, db_path, skill_files, tmp_path):
    # Setup DB
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        for sid, (filepath, state, name) in skill_files.items():
            cursor.execute(
                "INSERT INTO skills (skill_id, category, name, file_path, source_count, quote_count, state, created_at, updated_at) VALUES (?, 'cat', ?, ?, 1, 1, ?, 'd', 'd')",
                (sid, name, filepath, state)
            )
            
    # Mock SentenceTransformer
    mock_model = MagicMock()
    mock_st_class.return_value = mock_model
    mock_model.encode.return_value = np.zeros((5, 384)) # Dummy embeddings
    
    # Mock Cosine Similarity
    # Order of skills processed: existing (2, 3, 4, 5) then new (1) -> 5 skills total
    # We want skill 1 to be similar to 2, 3, 4 (top 3)
    # The order of all_skills_to_embed list will be existing_skills + new_skills
    # So index 4 is skill 1
    # Let's mock a deterministic matrix
    # sim_matrix[4] corresponds to skill 1
    sim_matrix = np.array([
        [1.0, 0.1, 0.2, 0.3, 0.9], # 2
        [0.1, 1.0, 0.1, 0.2, 0.8], # 3
        [0.2, 0.1, 1.0, 0.3, 0.7], # 4
        [0.3, 0.2, 0.3, 1.0, 0.1], # 5
        [0.9, 0.8, 0.7, 0.1, 1.0], # 1 (new skill)
    ])
    mock_cosine.return_value = sim_matrix
    
    run_linker(db_path)
    
    # Verify file updated
    filepath = skill_files["yc-skill-1"][0]
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    fm = yaml.safe_load(content.split("---")[1])
    # The highest are 2 (idx 0), 3 (idx 1), 4 (idx 2)
    # The IDs of existing skills in DB query order: 
    # The query is `SELECT ... WHERE state != 'draft'` without ORDER BY.
    # We can't guarantee order of 2, 3, 4, 5. But SQLite will likely return insertion order.
    # We expect some 3 skills. Let's just check length.
    assert len(fm["related_skills"]) == 3
    
    # Check DB update
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT state, related_skills FROM skills WHERE skill_id = 'yc-skill-1'")
        row = cursor.fetchone()
        assert row[0] == "linked"
        related = json.loads(row[1])
        assert len(related) == 3


@patch("src.forge.linker.SentenceTransformer")
def test_run_linker_no_new_skills(mock_st_class, db_path):
    run_linker(db_path)
    mock_st_class.assert_not_called()


@patch("src.forge.linker.cosine_similarity")
@patch("src.forge.linker.SentenceTransformer")
def test_run_linker_file_missing(mock_st_class, mock_cosine, db_path, skill_files):
    # Setup DB where new skill file is missing
    missing_path = "non_existent.md"
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO skills (skill_id, category, name, file_path, source_count, quote_count, state, created_at, updated_at) VALUES (?, 'cat', ?, ?, 1, 1, ?, 'd', 'd')",
            ("yc-skill-missing", "Missing", missing_path, "synthesized")
        )
        
    run_linker(db_path)
    
    # State should remain synthesized because the file doesn't exist
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT state FROM skills WHERE skill_id = 'yc-skill-missing'")
        row = cursor.fetchone()
        assert row[0] == "synthesized"


@patch("src.forge.linker.cosine_similarity")
@patch("src.forge.linker.SentenceTransformer")
def test_run_linker_missing_candidate_file(mock_st_class, mock_cosine, db_path, skill_files):
    # Setup DB where candidate file is missing
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # Insert 1 new skill and 1 existing skill with missing file
        filepath_new = skill_files["yc-skill-1"][0]
        cursor.execute(
            "INSERT INTO skills (skill_id, category, name, file_path, source_count, quote_count, state, created_at, updated_at) VALUES (?, 'cat', ?, ?, 1, 1, ?, 'd', 'd')",
            ("yc-skill-1", "Skill 1", filepath_new, "synthesized")
        )
        cursor.execute(
            "INSERT INTO skills (skill_id, category, name, file_path, source_count, quote_count, state, created_at, updated_at) VALUES (?, 'cat', ?, ?, 1, 1, ?, 'd', 'd')",
            ("yc-skill-bad", "Skill Bad", "missing_bad.md", "published")
        )
        
    mock_model = MagicMock()
    mock_st_class.return_value = mock_model
    mock_model.encode.return_value = np.zeros((1, 384)) # only new skill is valid
    
    mock_cosine.return_value = np.array([[1.0]])
    
    run_linker(db_path)
    
    # Verify related_skills is empty because the only candidate was missing its file
    filepath = skill_files["yc-skill-1"][0]
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    fm = yaml.safe_load(content.split("---")[1])
    assert fm["related_skills"] == []

