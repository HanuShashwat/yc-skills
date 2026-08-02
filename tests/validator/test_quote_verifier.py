"""
Tests for Quote Verifier.
"""
import json
import pytest
from pathlib import Path

from src.validator.quote_verifier import QuoteVerifier

@pytest.fixture
def mock_config(monkeypatch):
    class Validation:
        quote_fuzzy_ratio = 70
        quote_fuzzy_partial_ratio = 85
        
    class Pipeline:
        validation = Validation()
        
    class MockConfig:
        pipeline = Pipeline()
        
    return MockConfig()

def setup_test_files(tmp_path: Path):
    chunks_dir = tmp_path / "chunks"
    chunks_dir.mkdir()
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    
    return chunks_dir, raw_dir, skills_dir

def create_skill_file(skills_dir: Path, skill_id: str, body: str) -> Path:
    frontmatter = Path("tests/fixtures/sample_frontmatter.yml").read_text(encoding="utf-8")
    skill_path = skills_dir / f"{skill_id}.md"
    skill_path.write_text("---\n" + frontmatter + "---\n" + body, encoding="utf-8")
    return skill_path

def create_chunk_file(chunks_dir: Path, content_id: str, chunk_index: int, text: str):
    file_path = chunks_dir / f"{content_id}_{chunk_index:04d}.json"
    file_path.write_text(json.dumps({"text": text}), encoding="utf-8")
    return file_path

def test_quote_exact_match_pass(tmp_path: Path, mock_config):
    """Test known-good quote (exact match → PASS)."""
    chunks_dir, raw_dir, skills_dir = setup_test_files(tmp_path)
    
    create_chunk_file(chunks_dir, "lib_a1b2c3d4e5f6", 1, "The best time to raise money is when you don't need it.")
    
    body = """
## Verbatim Quotes
> "The best time to raise money is when you don't need it."
> — **Paul Graham**, Founder of YC
> Source: [How to convince investors](https://paulgraham.com/convince.html)
"""
    skill_path = create_skill_file(skills_dir, "test1", body)
    
    verifier = QuoteVerifier(str(chunks_dir), str(raw_dir), mock_config)
    res = verifier.verify_skill(str(skill_path))
    
    assert res.status == "pass"
    assert len(res.quote_results) == 1
    assert res.quote_results[0].status == "pass"
    assert res.quote_results[0].best_ratio == 100.0

def test_quote_truncated_warning(tmp_path: Path, mock_config):
    """Test slightly truncated quote (high partial_ratio but low ratio → WARNING)."""
    chunks_dir, raw_dir, skills_dir = setup_test_files(tmp_path)
    
    # Source chunk is long, quote is short
    source_text = "Investors can smell desperation from a mile away. It's incredibly obvious to everyone in the room. When you're down to 2 months of runway, you have zero leverage. This means you will take bad terms."
    create_chunk_file(chunks_dir, "yt_abc123def45", 1, source_text)
    
    # Quote is truncated
    body = """
## Verbatim Quotes
> "When you're down to 2 months of runway, you have zero leverage."
> — **Garry Tan**, CEO of YC
> Source: [Office Hours](https://youtube.com/watch?v=abc123def45)
"""
    skill_path = create_skill_file(skills_dir, "test2", body)
    
    verifier = QuoteVerifier(str(chunks_dir), str(raw_dir), mock_config)
    res = verifier.verify_skill(str(skill_path))
    
    assert res.status == "warning"
    assert len(res.quote_results) == 1
    assert res.quote_results[0].status == "warning"
    assert res.quote_results[0].best_partial_ratio == 100.0
    assert res.quote_results[0].best_ratio < 70.0

def test_quote_fabricated_fail(tmp_path: Path, mock_config):
    """Test completely fabricated quote (both scores low → FAIL)."""
    chunks_dir, raw_dir, skills_dir = setup_test_files(tmp_path)
    
    create_chunk_file(chunks_dir, "lib_a1b2c3d4e5f6", 1, "Raise money early and often.")
    
    body = """
## Verbatim Quotes
> "You should definitely just raise a million dollars immediately."
> — **Fake**, fake
> Source: [Fake](https://paulgraham.com/convince.html)
"""
    skill_path = create_skill_file(skills_dir, "test3", body)
    
    verifier = QuoteVerifier(str(chunks_dir), str(raw_dir), mock_config)
    res = verifier.verify_skill(str(skill_path))
    
    assert res.status == "fail"
    assert len(res.quote_results) == 1
    assert res.quote_results[0].status == "fail"
    assert res.quote_results[0].best_partial_ratio < 70.0

def test_quote_formatting_differences(tmp_path: Path, mock_config):
    """Test quote with formatting differences (Markdown artifacts)."""
    chunks_dir, raw_dir, skills_dir = setup_test_files(tmp_path)
    
    create_chunk_file(chunks_dir, "lib_a1b2c3d4e5f6", 1, "The best time to **raise money** is when you *don't* need it.")
    
    # Quote lacks markdown formatting, but words are same.
    body = """
## Verbatim Quotes
> "The best time to raise money is when you don't need it."
> — **Paul Graham**, Founder of YC
> Source: [How to convince investors](https://paulgraham.com/convince.html)
"""
    skill_path = create_skill_file(skills_dir, "test4", body)
    
    verifier = QuoteVerifier(str(chunks_dir), str(raw_dir), mock_config)
    res = verifier.verify_skill(str(skill_path))
    
    # Due to "**" and "*", the ratio drops slightly but should remain passing or warning
    assert res.status in ["pass", "warning"]
    assert res.quote_results[0].best_partial_ratio > 85.0

def test_missing_chunk_fallback_to_raw(tmp_path: Path, mock_config):
    """Test missing chunk fallback to raw file search."""
    chunks_dir, raw_dir, skills_dir = setup_test_files(tmp_path)
    
    # No chunks created. Create raw file instead.
    raw_file = raw_dir / "lib_a1b2c3d4e5f6.md"
    raw_file.write_text("This is some raw file. It contains a lot of extra text that will bring the overall ratio down significantly below seventy percent. But embedded within it is the quote: The best time to raise money is when you don't need it. And then the text goes on for a while.", encoding="utf-8")
    
    body = """
## Verbatim Quotes
> "The best time to raise money is when you don't need it."
> — **Paul Graham**, Founder of YC
> Source: [How to convince investors](https://paulgraham.com/convince.html)
"""
    skill_path = create_skill_file(skills_dir, "test5", body)
    
    verifier = QuoteVerifier(str(chunks_dir), str(raw_dir), mock_config)
    res = verifier.verify_skill(str(skill_path))
    
    assert res.status == "warning"  # The text is longer in the raw file, so ratio < 70 but partial_ratio == 100
    assert res.quote_results[0].matched_chunk_id == "lib_a1b2c3d4e5f6.md"
    assert res.quote_results[0].best_partial_ratio == 100.0

def test_no_quotes_returns_warning(tmp_path: Path, mock_config):
    """Test skill file with zero quotes (warning, not error)."""
    chunks_dir, raw_dir, skills_dir = setup_test_files(tmp_path)
    
    body = """
## Principle
Some principle here.
"""
    skill_path = create_skill_file(skills_dir, "test6", body)
    
    verifier = QuoteVerifier(str(chunks_dir), str(raw_dir), mock_config)
    res = verifier.verify_skill(str(skill_path))
    
    assert res.status == "warning"
    assert len(res.quote_results) == 0
