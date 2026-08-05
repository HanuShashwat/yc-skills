import os
import shutil
import sqlite3
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import numpy as np

from src.cli import (
    init_db,
    ingest_library_cmd,
    chunk_cmd,
    forge_cmd,
    link_cmd,
    export_cmd,
    validate_cmd,
    index_cmd,
)
import src.ingest.library_scraper



FIXTURES_DIR = Path(__file__).parent / "fixtures"

@pytest.fixture
def setup_workspace(tmp_path, monkeypatch):
    """Sets up a complete isolated workspace for the integration test."""
    # 1. Change CWD to the tmp_path so all relative paths resolve here
    monkeypatch.chdir(tmp_path)
    
    # 2. Copy config directory
    src_config = Path(__file__).parent.parent / "config"
    dst_config = tmp_path / "config"
    shutil.copytree(src_config, dst_config)
    
    # 2b. Copy prompts directory
    src_prompts = Path(__file__).parent.parent / "src" / "forge" / "prompts"
    dst_prompts = tmp_path / "src" / "forge" / "prompts"
    shutil.copytree(src_prompts, dst_prompts)
    
    # 3. Initialize DB in tmp_path
    db_path = tmp_path / "data" / "registry.db"
    
    monkeypatch.setattr("src.cli.DB_PATH", str(db_path))
    monkeypatch.setattr("src.cli.MIGRATION_PATH", str(Path(__file__).parent.parent / "src" / "migrations" / "001_init.sql"))
    
    # Initialize DB schema
    args = MagicMock()
    init_db(args)
    
    yield tmp_path, db_path

def test_full_pipeline_produces_valid_skill(setup_workspace):
    tmp_path, db_path = setup_workspace
    
    # --- MOCKS ---
    # 1. Mock requests for ingest
    mock_html = (FIXTURES_DIR / "sample_essay.html").read_text(encoding="utf-8")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = mock_html
    mock_response.content = mock_html.encode("utf-8")
    
    # 2. Mock LLM
    extraction_json = (FIXTURES_DIR / "extraction_response.json").read_text(encoding="utf-8")
    synthesis_json = (FIXTURES_DIR / "synthesis_response.json").read_text(encoding="utf-8")
    
    def mock_llm_call(*args, **kwargs):
        call_type = kwargs.get("call_type")
        if call_type == "extract":
            return extraction_json
        if call_type == "synthesize" and not kwargs.get("response_format_json", True):
            return "seed round timing"
        if call_type == "synthesize":
            import json
            return json.loads(synthesis_json)
        # Default fallback for hallucination guard etc
        return '{"supported": true, "issues": [], "confidence": 1.0}'
    
    # 3. Mock Embeddings
    def mock_encode(sentences, *args, **kwargs):
        # Return a simple deterministic vector for each sentence
        # 384 is the dim for all-MiniLM-L6-v2
        if isinstance(sentences, str):
            return np.ones(384, dtype=np.float32)
        return np.ones((len(sentences), 384), dtype=np.float32)
    
    with patch("src.ingest.library_scraper.requests.get", return_value=mock_response), \
         patch("src.ingest.library_scraper.lookup_author", return_value=("Garry Tan", "CEO of YC")), \
         patch("src.forge.llm_client.LLMClient.call", side_effect=mock_llm_call), \
         patch("src.forge.clusterer.SentenceTransformer") as MockST:
         
        # Setup the mock encode
        mock_instance = MagicMock()
        mock_instance.encode.side_effect = mock_encode
        MockST.return_value = mock_instance
        
        # --- RUN PIPELINE ---
        
        # 1. Ingest 5 items to satisfy batcher minimum
        for i in range(5):
            args = MagicMock()
            args.url = f"https://www.ycombinator.com/library/test-essay-{i}"
            ingest_library_cmd(args)

        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM content WHERE state = 'downloaded'")
            count = cur.fetchone()[0]
            assert count == 5
            
        # 2. Chunk
        args = MagicMock()
        args.all = True
        chunk_cmd(args)
        
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT state FROM content")
            state = cur.fetchone()[0]
            assert state == "chunked"
            # Manually set topic_guess for the batcher
            cur.execute("UPDATE content SET topic_guess = 'fundraising'")
            conn.commit()
            
        # 3. Forge (Batch, Extract, Cluster, Synthesize)
        args = MagicMock()
        args.topic = "fundraising"
        args.batch_size = 15
        forge_cmd(args)
        
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT state, COUNT(*) FROM content GROUP BY state")
            states = dict(cur.fetchall())
            assert states.get("synthesized", 0) == 2
            assert states.get("chunked", 0) == 3
            
            # Verify Skill file created
            skill_dir = Path("skills") / "fundraising"
            print("\nSKILL DIR FILES:")
            for f in skill_dir.glob("*.md"):
                print(" -", f.name)
            skill_file = skill_dir / "yc-fundraising-seed-round-timing.md"
            assert skill_file.exists()
            # Cleanup the generated file will happen later
            pass
        
        # 4. Link
        args = MagicMock()
        args.topic = "fundraising"
        link_cmd(args)
        
        with sqlite3.connect(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT state, COUNT(*) FROM content GROUP BY state")
            states = dict(cur.fetchall())
            assert states.get("linked", 0) == 2
            assert states.get("chunked", 0) == 3
            
        # Verify related_skills populated (can just check text)
        skill_content = skill_file.read_text(encoding="utf-8")
        assert "related_skills:" in skill_content
        
        args = MagicMock()
        args.all = True
        args.skill_id = None
        args.format = None
        export_cmd(args)
        
        mcp_spec = tmp_path / "specs" / "mcp" / "yc-fundraising-seed-round-timing.json"
        openai_spec = tmp_path / "specs" / "openai" / "yc-fundraising-seed-round-timing.json"
        hermes_spec = tmp_path / "specs" / "hermes" / "yc-fundraising-seed-round-timing.txt"
        
        assert mcp_spec.exists()
        assert openai_spec.exists()
        assert hermes_spec.exists()
        
        # Verify MCP fallback
        mcp_data = json.loads(mcp_spec.read_text(encoding="utf-8"))
        assert mcp_data["fallback"]["invent_quotes"] is False
        
        # Verify Hermes fallback
        hermes_data = hermes_spec.read_text(encoding="utf-8")
        assert "DO NOT invent YC quotes" in hermes_data
        
        # 6. Validate
        args = MagicMock()
        args.all = True
        args.skill_id = None
        # We need to catch SystemExit because validate_cmd exits if failure. If it passes, it shouldn't exit with 1.
        # But wait, validate_cmd sets sys.exit(1) on failure. On success, it might just return.
        try:
            validate_cmd(args)
        except SystemExit as e:
            # We expect no exit or exit 0
            assert e.code == 0
            
        # Assert not moved to failed
        failed_dir = tmp_path / "skills" / "_failed"
        if failed_dir.exists():
            assert not list(failed_dir.iterdir()), "Validation failed, file moved to _failed/"
            
        # 7. Index
        args = MagicMock()
        index_cmd(args)
        
        index_file = tmp_path / "skills-index.json"
        matrix_file = tmp_path / "data" / "similarity_matrix.json"
        
        assert index_file.exists()
        assert matrix_file.exists()
        
        # Verify index contains our skill
        index_data = json.loads(index_file.read_text(encoding="utf-8"))
        assert "yc-fundraising-seed-round-timing" in index_data["by_id"]
