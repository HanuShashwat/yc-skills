import pytest
from datetime import datetime
from pydantic import ValidationError
from src.models import (
    SkillFrontmatter,
    Provenance,
    Validation,
    ExtractionResponse,
    ExtractedItem,
    Contradiction,
    SynthesisResponse,
)

def test_valid_skill_id():
    """Test valid skill IDs matching the pattern."""
    valid_ids = [
        "yc-fundraising-basics",
        "yc-product-market-fit-metrics",
        "yc-culture-hiring-first-engineer-tips",
    ]
    for skill_id in valid_ids:
        # Create a valid SkillFrontmatter to verify ID validation passes
        SkillFrontmatter(
            skill_id=skill_id,
            name="Test Skill",
            category="test",
            tags=["tag1"],
            source_count=1,
            quote_count=1,
            confidence=0.5,
            provenance=Provenance(
                batch_id="test",
                pipeline_run_date=datetime.now(),
                sources=[]
            ),
            validation=Validation(
                quote_verified=True, schema_valid=True,
                hallucination_check=True, human_review=True
            )
        )

def test_invalid_skill_ids():
    """Test invalid skill IDs (uppercase, too many words, no prefix)."""
    invalid_ids = [
        "YC-fundraising-basics",  # uppercase
        "fundraising-basics",     # missing yc-
        "yc-a-b-c-d-e-f-g-h-i",   # too many parts
        "yc-fundraising_basics",  # underscore
    ]
    for skill_id in invalid_ids:
        with pytest.raises(ValidationError):
            SkillFrontmatter(
                skill_id=skill_id,
                name="Test",
                category="test",
                tags=["t"],
                source_count=1,
                quote_count=1,
                confidence=0.5,
                provenance=Provenance(batch_id="t", pipeline_run_date=datetime.now(), sources=[]),
                validation=Validation(quote_verified=True, schema_valid=True, hallucination_check=True, human_review=True)
            )

def test_valid_invalid_versions():
    """Test version pattern constraints."""
    # valid
    SkillFrontmatter(
        skill_id="yc-test-skill", name="Test", version="1.0.0", category="c", tags=["t"],
        source_count=1, quote_count=1, confidence=0.5,
        provenance=Provenance(batch_id="t", pipeline_run_date=datetime.now(), sources=[]),
        validation=Validation(quote_verified=True, schema_valid=True, hallucination_check=True, human_review=True)
    )
    
    # invalid
    for version in ["1.0", "v1.0.0", "1.0.0-beta", "a.b.c"]:
        with pytest.raises(ValidationError):
            SkillFrontmatter(
                skill_id="yc-test-skill", name="Test", version=version, category="c", tags=["t"],
                source_count=1, quote_count=1, confidence=0.5,
                provenance=Provenance(batch_id="t", pipeline_run_date=datetime.now(), sources=[]),
                validation=Validation(quote_verified=True, schema_valid=True, hallucination_check=True, human_review=True)
            )

def test_confidence_bounds():
    """Test confidence is between 0.0 and 1.0."""
    with pytest.raises(ValidationError):
        SkillFrontmatter(
            skill_id="yc-test-skill", name="T", category="c", tags=["t"], source_count=1, quote_count=1,
            confidence=-0.1,
            provenance=Provenance(batch_id="t", pipeline_run_date=datetime.now(), sources=[]),
            validation=Validation(quote_verified=True, schema_valid=True, hallucination_check=True, human_review=True)
        )
    with pytest.raises(ValidationError):
        SkillFrontmatter(
            skill_id="yc-test-skill", name="T", category="c", tags=["t"], source_count=1, quote_count=1,
            confidence=1.1,
            provenance=Provenance(batch_id="t", pipeline_run_date=datetime.now(), sources=[]),
            validation=Validation(quote_verified=True, schema_valid=True, hallucination_check=True, human_review=True)
        )

def test_tag_list_length_bounds():
    """Test tags list has between 1 and 10 items."""
    # 0 tags
    with pytest.raises(ValidationError):
        SkillFrontmatter(
            skill_id="yc-test-skill", name="T", category="c", tags=[], source_count=1, quote_count=1,
            confidence=0.5,
            provenance=Provenance(batch_id="t", pipeline_run_date=datetime.now(), sources=[]),
            validation=Validation(quote_verified=True, schema_valid=True, hallucination_check=True, human_review=True)
        )
    # 11 tags
    with pytest.raises(ValidationError):
        SkillFrontmatter(
            skill_id="yc-test-skill", name="T", category="c", tags=[str(i) for i in range(11)], source_count=1, quote_count=1,
            confidence=0.5,
            provenance=Provenance(batch_id="t", pipeline_run_date=datetime.now(), sources=[]),
            validation=Validation(quote_verified=True, schema_valid=True, hallucination_check=True, human_review=True)
        )

def test_source_and_quote_count_minimum():
    """Test source_count and quote_count ge=1."""
    with pytest.raises(ValidationError):
        SkillFrontmatter(
            skill_id="yc-test-skill", name="T", category="c", tags=["t"], source_count=0, quote_count=1,
            confidence=0.5,
            provenance=Provenance(batch_id="t", pipeline_run_date=datetime.now(), sources=[]),
            validation=Validation(quote_verified=True, schema_valid=True, hallucination_check=True, human_review=True)
        )
    with pytest.raises(ValidationError):
        SkillFrontmatter(
            skill_id="yc-test-skill", name="T", category="c", tags=["t"], source_count=1, quote_count=0,
            confidence=0.5,
            provenance=Provenance(batch_id="t", pipeline_run_date=datetime.now(), sources=[]),
            validation=Validation(quote_verified=True, schema_valid=True, hallucination_check=True, human_review=True)
        )

def test_extraction_response_parsing():
    """Test valid extraction response."""
    response = ExtractionResponse(
        extracted_items=[
            ExtractedItem(
                in_batch_index=0,
                quote="Build something people want.",
                speaker="Paul Graham",
                source_id="pg_123",
                source_url="http://example.com/pg",
                topic="Product",
                type="advice",
                context="Essay on startups",
                is_partial=False
            )
        ],
        contradictions=[
            Contradiction(
                topic="fundraising",
                in_batch_indices=[0, 1],
                summary="Conflicting advice on valuation."
            )
        ]
    )
    assert len(response.extracted_items) == 1
    assert len(response.contradictions) == 1

def test_synthesis_response_parsing():
    """Test valid synthesis response."""
    response = SynthesisResponse(
        skill_id="yc-product-build",
        name="Build what people want",
        category="product",
        principle="Always talk to users",
        quotes=[{"text": "Talk to users", "speaker": "PG", "source_url": "http"}],
        application={"step1": "do this"},
        edge_cases=["If enterprise"],
        related_skills=["yc-fundraising-seed"],
        confidence=0.9
    )
    assert response.confidence == 0.9
    assert response.skill_id == "yc-product-build"
