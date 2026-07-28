"""
Configuration loader for YC Skills Forge.
"""

import os
import re
import yaml
from typing import Dict, List, Any
from pydantic import BaseModel


# Taxonomy Models
class TaxonomyCategory(BaseModel):
    description: str
    subcategories: List[str]

class TaxonomyConfig(BaseModel):
    taxonomy: Dict[str, TaxonomyCategory]

# Provider Models
class ProviderConfig(BaseModel):
    api_key: str
    base_url: str
    model: str
    daily_token_limit: int
    daily_request_limit: int
    priority: int
    timeout: int
    max_retries: int

class RotationStrategyConfig(BaseModel):
    mode: str
    fallback_local: bool

class QuotasConfig(BaseModel):
    reset_utc_hour: int
    buffer_percent: int

class DedicatedValidatorConfig(BaseModel):
    provider: str
    model: str
    max_tokens: int
    temperature: float
    fallback_behavior: str

class ValidationConfig(BaseModel):
    dedicated_validator: DedicatedValidatorConfig

class ProvidersConfig(BaseModel):
    providers: Dict[str, ProviderConfig]
    rotation_strategy: RotationStrategyConfig
    quotas: QuotasConfig
    validation: ValidationConfig

# Pipeline Models
class ChunkingEssayConfig(BaseModel):
    min_words: int
    max_words: int
    target_words: int
    overlap_sentences: int
    split_header: str

class ChunkingTranscriptConfig(BaseModel):
    min_words: int
    max_words: int
    target_words: int
    merge_same_speaker: bool
    split_on_speaker_change: bool

class ChunkingConfig(BaseModel):
    essay: ChunkingEssayConfig
    transcript: ChunkingTranscriptConfig

class ClusteringConfig(BaseModel):
    embedding_model: str
    algorithm: str
    distance_threshold: float
    metric: str
    linkage: str
    min_cluster_size: int

class ExtractionConfig(BaseModel):
    min_items_per_chunk: int
    max_items_per_chunk: int
    temperature: float
    max_tokens: int

class SynthesisConfig(BaseModel):
    temperature: float
    max_tokens: int
    min_confidence: float
    max_quotes: int

class LinkingConfig(BaseModel):
    max_related_skills: int
    similarity_threshold: float

class PipelineValidationConfig(BaseModel):
    quote_fuzzy_ratio: int
    quote_fuzzy_partial_ratio: int
    quote_warning_threshold: int
    hallucination_check: bool

class ExportConfig(BaseModel):
    formats: List[str]

class PipelineConfig(BaseModel):
    chunking: ChunkingConfig
    clustering: ClusteringConfig
    extraction: ExtractionConfig
    synthesis: SynthesisConfig
    linking: LinkingConfig
    validation: PipelineValidationConfig
    export: ExportConfig


# Main App Config
class AppConfig(BaseModel):
    taxonomy: TaxonomyConfig
    providers: ProvidersConfig
    pipeline: PipelineConfig

def _replace_env_vars(data: Any) -> Any:
    """Recursively replace ${VAR} with environment variables."""
    if isinstance(data, dict):
        return {k: _replace_env_vars(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_replace_env_vars(v) for v in data]
    elif isinstance(data, str):
        def replacer(match: re.Match) -> str:
            var_name = match.group(1)
            return os.getenv(var_name, f"${{{var_name}}}")
        return re.sub(r"\$\{([A-Za-z0-9_]+)\}", replacer, data)
    else:
        return data

def load_config(
    taxonomy_path: str = "config/taxonomy.yml",
    providers_path: str = "config/providers.yml",
    pipeline_path: str = "config/pipeline.yml",
) -> AppConfig:
    """Load all configurations from YAML files."""
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        taxonomy_data = yaml.safe_load(f)
    
    with open(providers_path, "r", encoding="utf-8") as f:
        providers_data = yaml.safe_load(f)
        providers_data = _replace_env_vars(providers_data)
        
    with open(pipeline_path, "r", encoding="utf-8") as f:
        pipeline_data = yaml.safe_load(f)
        
    return AppConfig(
        taxonomy=TaxonomyConfig(**taxonomy_data),
        providers=ProvidersConfig(**providers_data),
        pipeline=PipelineConfig(**pipeline_data)
    )
