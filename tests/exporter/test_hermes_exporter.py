"""
Tests for Hermes Spec Exporter.
"""
import pytest
from pathlib import Path

from src.exporter.hermes_exporter import export_hermes, export_all_hermes

def test_export_hermes_valid_file(tmp_path: Path) -> None:
    """Test exporting a valid skill file to Hermes spec."""
    fixture_path = "tests/fixtures/sample_skill.md"
    out_dir = tmp_path / "specs" / "hermes"
    
    out_file = export_hermes(fixture_path, str(out_dir))
    
    assert Path(out_file).exists()
    
    with open(out_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Check delimiters
    assert content.startswith("[SKILL: yc-fundraising-seed-round-timing]")
    assert "[END SKILL]" in content
    
    # Check sections present
    assert "NAME: Seed Round Timing" in content
    assert "CATEGORY: fundraising" in content
    assert "TAGS: seed, runway, leverage, investors, timing" in content
    assert "PRINCIPLE: The optimal time to raise a seed round" in content
    assert "WHEN TO USE: Activate this skill when a founder asks about:" in content
    assert "EDGE CASES:" in content
    assert "- **Pre-revenue AI startups:**" in content
    
    # Check FALLBACK exact string
    assert "FALLBACK: If query does not match, return 3 closest skills and use general knowledge. DO NOT invent YC quotes." in content
    
    # Check verbatim quotes extraction
    assert '- "The best time to raise money is when you don\'t need it." — Paul Graham, Founder of YC' in content
    assert '- "If you wait until you need money, you\'ve already lost." — Michael Seibel, Partner at YC' in content
    
    # Check related skills
    assert "RELATED SKILLS: yc-fundraising-seed-round-valuation, yc-fundraising-investor-update-emails, yc-founder-mental-models-default-alive-dead" in content
    
    # Check agent protocol extracted numbered steps
    assert "1. **Assess Runway First**" in content
    assert "2. **Check Momentum Signals**" in content
    
def test_export_hermes_missing_frontmatter(tmp_path: Path) -> None:
    """Test exporting a file with missing frontmatter raises ValueError."""
    bad_file = tmp_path / "bad.md"
    bad_file.write_text("# Just some markdown\nNo frontmatter here.", encoding="utf-8")
    
    with pytest.raises(ValueError, match="Missing valid YAML frontmatter"):
        export_hermes(str(bad_file), str(tmp_path))

def test_export_all_hermes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test exporting all valid skills in a directory."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    
    # Copy fixture to skills dir
    fixture_path = Path("tests/fixtures/sample_skill.md")
    dest_path = skills_dir / "sample_skill.md"
    dest_path.write_text(fixture_path.read_text(encoding="utf-8"), encoding="utf-8")
    
    # Create invalid file to ensure it's skipped gracefully
    bad_file = skills_dir / "bad.md"
    bad_file.write_text("no frontmatter", encoding="utf-8")
    
    out_dir = tmp_path / "specs" / "hermes"
    
    # Ensure config enables hermes
    class MockConfig:
        class Pipeline:
            class Export:
                formats = ["hermes"]
            export = Export()
        pipeline = Pipeline()
        
    monkeypatch.setattr("src.exporter.hermes_exporter.load_config", lambda: MockConfig())
    
    generated = export_all_hermes(str(skills_dir), str(out_dir))
    
    assert len(generated) == 1
    assert "yc-fundraising-seed-round-timing.txt" in generated[0]
