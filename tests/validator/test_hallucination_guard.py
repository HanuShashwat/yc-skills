"""
Tests for Hallucination Guard.
"""
import sqlite3
import pytest
from pathlib import Path
import json

from src.validator.hallucination_guard import HallucinationGuard

@pytest.fixture
def mock_config(monkeypatch):
    class ProviderConfig:
        api_key = "fake_key"
        base_url = "fake_url"
        timeout = 30
        
    class DedicatedValidator:
        provider = "gemini"
        model = "gemini-1.5-flash"
        temperature = 0.0
        max_tokens = 2000
        fallback_behavior = "fail_open"
        
    class ValidationConfig:
        dedicated_validator = DedicatedValidator()
        
    class ProvidersConfig:
        providers = {"gemini": ProviderConfig()}
        validation = ValidationConfig()
        
    class MockConfig:
        providers = ProvidersConfig()
        
    return MockConfig()

def setup_test_files(tmp_path: Path):
    db_path = tmp_path / "registry.db"
    chunks_dir = tmp_path / "chunks"
    chunks_dir.mkdir()
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    
    # Initialize mock database
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE content (content_id TEXT, speaker TEXT)")
        cursor.execute("INSERT INTO content VALUES ('lib_a1b2c3d4e5f6', 'Paul Graham')")
        cursor.execute("INSERT INTO content VALUES ('yt_abc123def45', 'Garry Tan')")
        conn.commit()
        
    return db_path, chunks_dir, skills_dir

def create_skill(skills_dir: Path, skill_id: str, body: str) -> Path:
    frontmatter = Path("tests/fixtures/sample_frontmatter.yml").read_text(encoding="utf-8")
    skill_path = skills_dir / f"{skill_id}.md"
    skill_path.write_text("---\n" + frontmatter + "---\n" + body, encoding="utf-8")
    return skill_path

def create_chunk(chunks_dir: Path, content_id: str, index: int, text: str):
    file_path = chunks_dir / f"{content_id}_{index:04d}.json"
    file_path.write_text(json.dumps({"text": text}), encoding="utf-8")
    
@pytest.fixture
def mock_llm(monkeypatch):
    class MockResponse:
        def __init__(self, content):
            self.content = content
            
        class Choice:
            def __init__(self, content):
                self.message = type('Message', (), {'content': content})
                
        @property
        def choices(self):
            return [self.Choice(self.content)]
            
    def make_mock(supported=True, issues=None):
        issues = issues or []
        resp_json = json.dumps({"supported": supported, "issues": issues, "confidence": 0.9})
        
        def mock_create(*args, **kwargs):
            return MockResponse(resp_json)
            
        monkeypatch.setattr("openai.resources.chat.completions.Completions.create", mock_create)
        
    return make_mock

@pytest.fixture
def mock_llm_rate_limit(monkeypatch):
    def mock_create(*args, **kwargs):
        import openai
        raise openai.RateLimitError(
            message="429 Quota exhausted",
            response=None,
            body=None
        )
    monkeypatch.setattr("openai.resources.chat.completions.Completions.create", mock_create)

def test_valid_skill_pass(tmp_path, mock_config, mock_llm):
    mock_llm(supported=True)
    db_path, chunks_dir, skills_dir = setup_test_files(tmp_path)
    
    body = """
## Principle
Always be raising.

## Verbatim Quotes
> "The best time to raise money is when you don't need it."
> — **Paul Graham**, Founder of YC
> Source: [How to convince investors](https://paulgraham.com/convince.html)

## Personalized Application
Do it in 2024.
"""
    skill_path = create_skill(skills_dir, "test1", body)
    create_chunk(chunks_dir, "lib_a1b2c3d4e5f6", 1, "The best time to raise money is when you don't need it. Do it in 2024.")
    
    guard = HallucinationGuard(str(db_path), str(chunks_dir), mock_config)
    res = guard.check_skill(str(skill_path))
    
    assert res.status == "pass"
    assert res.speaker_check == "pass"
    assert res.claim_check == "pass"
    assert res.llm_check == "pass"
    
def test_unknown_speaker_fail(tmp_path, mock_config, mock_llm):
    mock_llm(supported=True)
    db_path, chunks_dir, skills_dir = setup_test_files(tmp_path)
    
    body = """
## Verbatim Quotes
> "You should raise a million dollars immediately."
> — **Fake Speaker**, fake
> Source: [Fake](https://paulgraham.com/convince.html)
"""
    skill_path = create_skill(skills_dir, "test2", body)
    
    guard = HallucinationGuard(str(db_path), str(chunks_dir), mock_config)
    res = guard.check_skill(str(skill_path))
    
    assert res.status == "fail"
    assert res.speaker_check == "fail"
    
def test_unsupported_claim_fail(tmp_path, mock_config, mock_llm):
    mock_llm(supported=True)
    db_path, chunks_dir, skills_dir = setup_test_files(tmp_path)
    
    body = """
## Principle
You must raise $5M in 2025.

## Verbatim Quotes
> "The best time to raise money is when you don't need it."
> — **Paul Graham**, Founder of YC
"""
    skill_path = create_skill(skills_dir, "test3", body)
    create_chunk(chunks_dir, "lib_a1b2c3d4e5f6", 1, "The best time to raise money is when you don't need it.") # No mention of $5M or 2025
    
    guard = HallucinationGuard(str(db_path), str(chunks_dir), mock_config)
    res = guard.check_skill(str(skill_path))
    
    assert res.status == "fail"
    assert res.claim_check == "fail"
    assert "$5M" in res.flagged_claims or "2025" in res.flagged_claims
    
def test_llm_judge_fail(tmp_path, mock_config, mock_llm):
    mock_llm(supported=False, issues=["Unverifiable advice"])
    db_path, chunks_dir, skills_dir = setup_test_files(tmp_path)
    
    body = """
## Principle
Always be raising.

## Verbatim Quotes
> "The best time to raise money is when you don't need it."
> — **Paul Graham**, Founder of YC
"""
    skill_path = create_skill(skills_dir, "test4", body)
    create_chunk(chunks_dir, "lib_a1b2c3d4e5f6", 1, "The best time to raise money is when you don't need it.")
    
    guard = HallucinationGuard(str(db_path), str(chunks_dir), mock_config)
    res = guard.check_skill(str(skill_path))
    
    assert res.status == "fail"
    assert res.llm_check == "fail"
    assert "Unverifiable advice" in res.issues
    
def test_llm_rate_limit_skip(tmp_path, mock_config, mock_llm_rate_limit):
    db_path, chunks_dir, skills_dir = setup_test_files(tmp_path)
    
    body = """
## Principle
Always be raising.

## Verbatim Quotes
> "The best time to raise money is when you don't need it."
> — **Paul Graham**, Founder of YC
"""
    skill_path = create_skill(skills_dir, "test5", body)
    create_chunk(chunks_dir, "lib_a1b2c3d4e5f6", 1, "The best time to raise money is when you don't need it.")
    
    guard = HallucinationGuard(str(db_path), str(chunks_dir), mock_config)
    res = guard.check_skill(str(skill_path))
    
    # It should pass overall because speaker & claims pass, and LLM is skipped
    assert res.status == "pass"
    assert res.llm_check == "skipped"
