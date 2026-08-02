"""
Tests for MCP Spec Exporter.
"""
import json
import pytest
from pathlib import Path

from src.exporter.mcp_exporter import export_mcp, export_all_mcp

def test_export_mcp_valid_file(tmp_path: Path) -> None:
    """Test exporting a valid skill file to MCP spec."""
    fixture_path = "tests/fixtures/sample_skill.md"
    out_dir = tmp_path / "specs" / "mcp"
    
    out_file = export_mcp(fixture_path, str(out_dir))
    
    assert Path(out_file).exists()
    
    with open(out_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # Check name uses underscores
    assert data["name"] == "yc_fundraising_seed_round_timing"
    
    # Check handler path
    assert data["handler"]["path"] == "skills/fundraising/yc-fundraising-seed-round-timing.md"
    
    # Check tags match frontmatter
    assert data["tags"] == ["seed", "runway", "leverage", "investors", "timing"]
    
    # Check description
    assert "YC advice on Seed Round Timing" in data["description"]
    assert "Paul Graham (Founder of YC)" in data["description"]
    assert "Garry Tan (CEO of YC)" in data["description"]
    assert "optimal time to raise a seed round" in data["description"]
    
    # Check input schema
    assert "question" in data["inputSchema"]["properties"]
    assert "question" in data["inputSchema"]["required"]
    assert "runway_months" in data["inputSchema"]["properties"]
    
    # Check fallback block
    fallback = data.get("fallback")
    assert fallback is not None
    assert fallback["mode"] == "closest_skills"
    assert fallback["count"] == 3
    assert fallback["use_agent_knowledge"] is True
    assert fallback["invent_quotes"] is False

def test_export_mcp_missing_frontmatter(tmp_path: Path) -> None:
    """Test exporting a file with missing frontmatter raises ValueError."""
    bad_file = tmp_path / "bad.md"
    bad_file.write_text("# Just some markdown\nNo frontmatter here.")
    
    with pytest.raises(ValueError, match="Missing valid YAML frontmatter"):
        export_mcp(str(bad_file), str(tmp_path))

def test_export_mcp_invalid_frontmatter(tmp_path: Path) -> None:
    """Test exporting a file with invalid frontmatter schema raises ValueError."""
    bad_file = tmp_path / "invalid.md"
    bad_file.write_text("---\nbad_key: value\n---\n# Content")
    
    with pytest.raises(ValueError, match="Invalid frontmatter schema"):
        export_mcp(str(bad_file), str(tmp_path))

def test_export_all_mcp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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
    
    out_dir = tmp_path / "specs" / "mcp"
    
    # Ensure config enables mcp
    class MockConfig:
        class Pipeline:
            class Export:
                formats = ["mcp"]
            export = Export()
        pipeline = Pipeline()
        
    monkeypatch.setattr("src.exporter.mcp_exporter.load_config", lambda: MockConfig())
    
    generated = export_all_mcp(str(skills_dir), str(out_dir))
    
    assert len(generated) == 1
    assert "yc-fundraising-seed-round-timing.json" in generated[0]
