"""
Tests for OpenAI Function Schema Exporter.
"""
import json
import pytest
from pathlib import Path

from src.exporter.openai_exporter import export_openai, export_all_openai

def test_export_openai_valid_file(tmp_path: Path) -> None:
    """Test exporting a valid skill file to OpenAI spec."""
    fixture_path = "tests/fixtures/sample_skill.md"
    out_dir = tmp_path / "specs" / "openai"
    
    out_file = export_openai(fixture_path, str(out_dir))
    
    assert Path(out_file).exists()
    
    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Check top-level type
    assert data["type"] == "function"
    
    func = data["function"]
    
    # Check name uses underscores
    assert func["name"] == "yc_fundraising_seed_round_timing"
    
    # Check metadata skill_file path
    assert data["metadata"]["skill_file"] == "skills/fundraising/yc-fundraising-seed-round-timing.md"
    
    # Check metadata tags match frontmatter
    assert data["metadata"]["tags"] == ["seed", "runway", "leverage", "investors", "timing"]
    
    # Check description
    assert "YC advice on Seed Round Timing" in func["description"]
    assert "Paul Graham (Founder of YC)" in func["description"]
    assert "Garry Tan (CEO of YC)" in func["description"]
    assert "optimal time to raise a seed round" in func["description"]
    
    # Check function parameters schema
    assert "question" in func["parameters"]["properties"]
    assert "question" in func["parameters"]["required"]
    assert "runway_months" in func["parameters"]["properties"]
    
    # Check fallback block
    fallback = data["metadata"].get("fallback")
    assert fallback is not None
    assert fallback["mode"] == "closest_skills"
    assert fallback["count"] == 3
    assert fallback["use_agent_knowledge"] is True
    assert fallback["invent_quotes"] is False

def test_export_openai_missing_frontmatter(tmp_path: Path) -> None:
    """Test exporting a file with missing frontmatter raises ValueError."""
    bad_file = tmp_path / "bad.md"
    bad_file.write_text("# Just some markdown\nNo frontmatter here.")
    
    with pytest.raises(ValueError, match="Missing valid YAML frontmatter"):
        export_openai(str(bad_file), str(tmp_path))

def test_export_all_openai(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test exporting all valid skills in a directory."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    
    # Copy fixture to skills dir
    fixture_path = Path("tests/fixtures/sample_skill.md")
    dest_path = skills_dir / "sample_skill.md"
    dest_path.write_text(fixture_path.read_text())
    
    # Create invalid file to ensure it's skipped gracefully
    bad_file = skills_dir / "bad.md"
    bad_file.write_text("no frontmatter")
    
    out_dir = tmp_path / "specs" / "openai"
    
    # Ensure config enables openai
    class MockConfig:
        class Pipeline:
            class Export:
                formats = ["openai"]
            export = Export()
        pipeline = Pipeline()
        
    monkeypatch.setattr("src.exporter.openai_exporter.load_config", lambda: MockConfig())
    
    generated = export_all_openai(str(skills_dir), str(out_dir))
    
    assert len(generated) == 1
    assert "yc-fundraising-seed-round-timing.json" in generated[0]
