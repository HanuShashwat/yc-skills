"""
Pydantic v2 data models for OpenYC Skills.
"""

from typing import List, Optional, Dict, Literal, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class ProvenanceSource(BaseModel):
    """Source material contributing to a skill."""

    content_id: str = Field(..., description="ID of the source content")
    title: str = Field(..., description="Title of the source")
    speaker: Optional[str] = Field(None, description="Speaker name if applicable")
    designation: Optional[str] = Field(None, description="Speaker designation or title")
    url: HttpUrl = Field(..., description="URL of the source")
    contribution: str = Field(..., description="Description of the contribution")


class Provenance(BaseModel):
    """Provenance tracking for a generated skill."""

    batch_id: str = Field(..., description="ID of the batch run")
    pipeline_run_date: datetime = Field(..., description="Date the pipeline was run")
    github_run_url: Optional[str] = Field("", description="GitHub Actions run URL")
    sources: List[ProvenanceSource] = Field(
        default_factory=list, description="List of sources"
    )


class Validation(BaseModel):
    """Validation status for a skill."""

    quote_verified: bool = Field(..., description="Quotes verified against source")
    schema_valid: bool = Field(..., description="Schema passed validation")
    hallucination_check: bool = Field(..., description="Passed hallucination check")
    human_review: bool = Field(..., description="Passed human review")


class SkillFrontmatter(BaseModel):
    """Frontmatter schema for generated skill files."""

    skill_id: str = Field(
        ..., pattern=r"^yc-[a-z]+(-[a-z]+){1,6}$", description="Unique skill identifier"
    )
    name: str = Field(..., max_length=100, description="Skill name")
    version: str = Field(
        default="1.0.0", pattern=r"^\d+\.\d+\.\d+$", description="Skill version"
    )
    category: str = Field(..., description="Skill category")
    tags: List[str] = Field(
        ..., min_length=1, max_length=10, description="Tags associated with the skill"
    )
    source_count: int = Field(..., ge=1, description="Number of unique sources")
    quote_count: int = Field(..., ge=1, description="Number of quotes extracted")
    related_skills: List[str] = Field(
        default_factory=list, description="List of related skill IDs"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score of synthesis"
    )
    provenance: Provenance = Field(..., description="Provenance information")
    validation: Validation = Field(..., description="Validation results")


class ExtractedItem(BaseModel):
    """Individual item extracted from a source chunk."""

    in_batch_index: int = Field(..., description="Index within the extraction batch")
    quote: str = Field(..., description="Exact verbatim quote")
    speaker: str = Field(..., description="Speaker of the quote")
    designation: Optional[str] = Field(None, description="Speaker designation")
    source_id: str = Field(..., description="Content ID of the source")
    source_url: HttpUrl = Field(..., description="URL to the source chunk or video")
    timestamp: Optional[str] = Field(None, description="Video timestamp if applicable")
    topic: str = Field(..., description="Topic of the extracted item")
    type: Literal["framework", "warning", "advice", "story"] = Field(
        ..., description="Type of extraction"
    )
    context: str = Field(..., description="Context of the quote")
    is_partial: bool = Field(..., description="Whether the extraction is partial")


class Contradiction(BaseModel):
    """Contradiction identified during extraction."""

    topic: str = Field(..., description="Topic of the contradiction")
    in_batch_indices: List[int] = Field(..., description="Indices of conflicting items")
    summary: str = Field(..., description="Summary of the contradiction")


class ExtractionResponse(BaseModel):
    """Complete response from the extraction LLM."""

    extracted_items: List[ExtractedItem] = Field(
        default_factory=list, description="Extracted items"
    )
    contradictions: List[Contradiction] = Field(
        default_factory=list, description="Identified contradictions"
    )


class SynthesisResponse(BaseModel):
    """Complete response from the synthesis LLM."""

    skill_id: str = Field(
        ...,
        pattern=r"^yc-[a-z]+(-[a-z]+){1,6}$",
        description="Generated skill identifier",
    )
    name: str = Field(..., max_length=100, description="Skill name")
    category: str = Field(..., description="Skill category")
    principle: str = Field(..., description="Core principle taught by the skill")
    quotes: List[Dict[str, str]] = Field(
        default_factory=list, description="Quotes supporting the principle"
    )
    application: Dict[str, Any] = Field(
        default_factory=dict, description="How to apply the skill"
    )
    edge_cases: List[str] = Field(
        default_factory=list, description="Edge cases or exceptions"
    )
    related_skills: List[str] = Field(
        default_factory=list, description="Related skill IDs"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class ChunkData(BaseModel):
    """Data chunk from source material."""

    chunk_id: str = Field(..., description="Unique chunk ID")
    content_id: str = Field(..., description="Source content ID")
    chunk_index: int = Field(..., description="Index of the chunk in the content")
    text: str = Field(..., description="Text content of the chunk")
    word_count: int = Field(..., description="Number of words")
    char_count: int = Field(..., description="Number of characters")
    speaker: Optional[str] = Field(None, description="Speaker name")
    timestamp_start: Optional[str] = Field(None, description="Start timestamp")
    timestamp_end: Optional[str] = Field(None, description="End timestamp")


class ContentRecord(BaseModel):
    """Record of a source content item."""

    content_id: str = Field(..., description="Unique content ID")
    source_type: str = Field(..., description="Type of source (library, youtube)")
    url: HttpUrl = Field(..., description="Source URL")
    title: str = Field(..., description="Source title")
    speaker: Optional[str] = Field(None, description="Primary speaker")
    designation: Optional[str] = Field(None, description="Primary speaker designation")
    state: str = Field(..., description="Pipeline state (e.g., downloaded, chunked)")
    topic_guess: Optional[str] = Field(None, description="Initial topic classification")


class UsageLogEntry(BaseModel):
    """Log entry for LLM provider usage."""

    provider: str = Field(..., description="LLM provider name")
    model: str = Field(..., description="Model identifier")
    batch_id: Optional[str] = Field(None, description="Associated batch ID")
    prompt_tokens: int = Field(..., description="Number of prompt tokens")
    completion_tokens: int = Field(..., description="Number of completion tokens")
    total_tokens: int = Field(..., description="Total tokens used")
    cost_estimate_usd: Optional[float] = Field(
        None, description="Estimated cost in USD"
    )
    call_type: str = Field(..., description="Type of call (e.g., extract, synthesize)")
    timestamp: datetime = Field(..., description="Timestamp of the API call")
    success: bool = Field(..., description="Whether the call succeeded")
    error_message: Optional[str] = Field(None, description="Error message if failed")
