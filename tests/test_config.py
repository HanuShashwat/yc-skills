import os
import pytest
from src.config import load_config, _replace_env_vars

def test_env_var_replacement():
    """Test recursive environment variable replacement."""
    os.environ["TEST_VAR"] = "secret_key"
    data = {"key": "${TEST_VAR}", "nested": [{"k": "${TEST_VAR}"}]}
    result = _replace_env_vars(data)
    assert result["key"] == "secret_key"
    assert result["nested"][0]["k"] == "secret_key"
    del os.environ["TEST_VAR"]

def test_unresolved_env_var():
    """Test missing environment variable fallback to literal."""
    data = {"key": "${MISSING_VAR}"}
    result = _replace_env_vars(data)
    assert result["key"] == "${MISSING_VAR}"

def test_taxonomy_loading():
    """Test loading of taxonomy config."""
    config = load_config()
    assert "fundraising" in config.taxonomy.taxonomy
    assert "seed-round" in config.taxonomy.taxonomy["fundraising"].subcategories
    assert len(config.taxonomy.taxonomy) == 8

def test_providers_loading(monkeypatch):
    """Test loading of providers config with env var substitution."""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test_deepseek")
    monkeypatch.setenv("KIMI_API_KEY", "test_kimi")
    monkeypatch.setenv("GLM_API_KEY", "test_glm")
    monkeypatch.setenv("GEMINI_API_KEY", "test_gemini")
    
    config = load_config()
    assert config.providers.providers["deepseek"].api_key == "test_deepseek"
    assert config.providers.providers["kimi"].api_key == "test_kimi"
    assert config.providers.providers["glm"].api_key == "test_glm"
    assert config.providers.providers["gemini"].api_key == "test_gemini"
    assert config.providers.rotation_strategy.mode == "round_robin_quota"

def test_pipeline_loading():
    """Test loading of pipeline config."""
    config = load_config()
    assert config.pipeline.chunking.essay.min_words == 200
    assert config.pipeline.clustering.embedding_model == "all-MiniLM-L6-v2"
    assert config.pipeline.extraction.temperature == 0.3
    assert config.pipeline.validation.hallucination_check is True
    assert "mcp" in config.pipeline.export.formats

def test_invalid_yaml_path():
    """Test loading handles missing files by raising error."""
    with pytest.raises(FileNotFoundError):
        load_config(taxonomy_path="config/missing.yml")
