"""
Tests for Signal Resolver.
"""
import json
import pytest
from pathlib import Path
import math

from src.retrieval.resolver import SignalResolver, generate_index, generate_similarity_matrix

@pytest.fixture
def mock_embed(monkeypatch):
    def fake_embed(self, text: str):
        # Deterministic mock embedding based on text hash
        # We just want some vector to test cosine sim
        val = float(sum(ord(c) for c in text))
        return [val, val * 0.5, val * 0.1]
    
    monkeypatch.setattr(SignalResolver, "_embed", fake_embed)

def setup_test_files(tmp_path: Path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    
    # We create a few dummy skills
    # 1. yc-fundraising-seed-round-timing
    (skills_dir / "fundraising").mkdir()
    f1 = skills_dir / "fundraising" / "yc-fundraising-seed-round-timing.md"
    f1.write_text("""---
skill_id: "yc-fundraising-seed-round-timing"
name: "Seed Round Timing"
version: "1.0.0"
category: "fundraising"
tags: ["seed", "timing"]
source_count: 1
quote_count: 1
confidence: 0.9
related_skills: []
provenance:
  batch_id: "test"
  pipeline_run_date: "2026-07-01T00:00:00Z"
  sources: []
validation:
  quote_verified: true
  schema_valid: true
  hallucination_check: true
  human_review: false
---

## Principle
Timing is everything.
""", encoding="utf-8")

    # 2. yc-hiring-first-engineer
    (skills_dir / "hiring").mkdir()
    f2 = skills_dir / "hiring" / "yc-hiring-first-engineer.md"
    f2.write_text("""---
skill_id: "yc-hiring-first-engineer"
name: "First Engineer"
version: "1.0.0"
category: "hiring"
tags: ["hiring", "engineering"]
source_count: 1
quote_count: 1
confidence: 0.9
related_skills: []
provenance:
  batch_id: "test"
  pipeline_run_date: "2026-07-01T00:00:00Z"
  sources: []
validation:
  quote_verified: true
  schema_valid: true
  hallucination_check: true
  human_review: false
---

## Principle
Hire slowly.
""", encoding="utf-8")

    # 3. yc-fundraising-investor-update-emails
    f3 = skills_dir / "fundraising" / "yc-fundraising-investor-update-emails.md"
    f3.write_text("""---
skill_id: "yc-fundraising-investor-update-emails"
name: "Investor Update Emails"
version: "1.0.0"
category: "fundraising"
tags: ["seed", "update"]
source_count: 1
quote_count: 1
confidence: 0.9
related_skills: []
provenance:
  batch_id: "test"
  pipeline_run_date: "2026-07-01T00:00:00Z"
  sources: []
validation:
  quote_verified: true
  schema_valid: true
  hallucination_check: true
  human_review: false
---

## Principle
Send them monthly.
""", encoding="utf-8")

    return skills_dir

def test_exact_match(tmp_path, mock_embed):
    skills_dir = setup_test_files(tmp_path)
    resolver = SignalResolver(str(skills_dir))
    
    res = resolver.resolve("yc-fundraising-seed-round-timing")
    assert res["type"] == "exact"
    assert res["skill"] == "yc-fundraising-seed-round-timing"
    assert res["path"].endswith("yc-fundraising-seed-round-timing.md")
    
def test_category_filter(tmp_path, mock_embed):
    skills_dir = setup_test_files(tmp_path)
    resolver = SignalResolver(str(skills_dir))
    
    res = resolver.resolve("/fundraising")
    assert res["type"] == "category"
    assert res["category"] == "fundraising"
    assert len(res["skills"]) == 2
    assert "yc-fundraising-seed-round-timing" in res["skills"]
    assert "yc-fundraising-investor-update-emails" in res["skills"]
    
def test_tag_filter(tmp_path, mock_embed):
    skills_dir = setup_test_files(tmp_path)
    resolver = SignalResolver(str(skills_dir))
    
    # single tag
    res = resolver.resolve("%seed")
    assert res["type"] == "tags"
    assert len(res["skills"]) == 2
    
    # multi tag AND intersection
    res = resolver.resolve("%seed,timing")
    assert res["type"] == "tags"
    assert len(res["skills"]) == 1
    assert res["skills"][0] == "yc-fundraising-seed-round-timing"

def test_multi_tag_no_matches(tmp_path, mock_embed):
    skills_dir = setup_test_files(tmp_path)
    resolver = SignalResolver(str(skills_dir))
    
    res = resolver.resolve("%seed,engineering")
    assert res["type"] == "tags"
    assert len(res["skills"]) == 0

def test_fuzzy_embedding_search(tmp_path, mock_embed):
    skills_dir = setup_test_files(tmp_path)
    resolver = SignalResolver(str(skills_dir))
    
    res = resolver.resolve("How do I hire?")
    assert res["type"] == "closest"
    assert len(res["skills"]) == 3
    assert len(res["similarities"]) == 3
    assert all(isinstance(s, float) for s in res["similarities"])

def test_generate_index(tmp_path, mock_embed):
    skills_dir = setup_test_files(tmp_path)
    idx_path = tmp_path / "skills-index.json"
    
    generate_index(str(skills_dir), str(idx_path))
    
    assert idx_path.exists()
    data = json.loads(idx_path.read_text())
    assert "by_id" in data
    assert "by_category" in data
    assert "by_tag" in data
    assert "yc-fundraising-seed-round-timing" in data["by_id"]

def test_generate_similarity_matrix(tmp_path, mock_embed):
    skills_dir = setup_test_files(tmp_path)
    mat_path = tmp_path / "data" / "similarity_matrix.json"
    
    generate_similarity_matrix(str(skills_dir), str(mat_path))
    
    assert mat_path.exists()
    data = json.loads(mat_path.read_text())
    
    assert data["version"] == "1.0.0"
    assert len(data["skills"]) == 3
    
    matrix = data["matrix"]
    assert len(matrix) == 3
    assert len(matrix[0]) == 3
    
    # Diagonal is 1.0
    for i in range(3):
        assert matrix[i][i] == 1.0
        
    # Symmetric
    assert matrix[0][1] == matrix[1][0]
    
    assert "tag_index" in data
    assert "seed" in data["tag_index"]
