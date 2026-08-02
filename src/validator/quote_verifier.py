"""
Quote Verifier for YC Skills Forge.
Performs dual fuzzy matching to verify quote fidelity against source chunks.
"""
import json
import logging
import re
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from pydantic import BaseModel
from rapidfuzz import fuzz

from src.config import load_config
from src.exporter.utils import parse_skill_file

logger = logging.getLogger(__name__)

class QuoteResult(BaseModel):
    """Result of verifying a single quote."""
    quote_text: str
    best_ratio: float
    best_partial_ratio: float
    matched_chunk_id: Optional[str]
    status: str

class QuoteVerificationResult(BaseModel):
    """Overall result of verifying all quotes in a skill."""
    skill_id: str
    status: str
    quote_results: List[QuoteResult]

class QuoteVerifier:
    """Verifies verbatim quotes against source chunks."""
    
    def __init__(self, chunks_dir: str = "data/chunks", raw_dir: str = "data/raw", config=None):
        self.chunks_dir = Path(chunks_dir)
        self.raw_dir = Path(raw_dir)
        self.config = config or load_config()
        
        # Read thresholds from config
        val_config = self.config.pipeline.validation
        self.ratio_threshold = val_config.quote_fuzzy_ratio
        self.partial_threshold = val_config.quote_fuzzy_partial_ratio
        
    def _extract_quotes(self, body: str) -> List[Tuple[str, str]]:
        """
        Extract quotes and their source URLs from markdown body.
        Returns a list of tuples: (quote_text, source_url)
        """
        quotes = []
        lines = body.splitlines()
        current_block = []
        blocks = []
        
        for line in lines:
            if line.startswith(">"):
                current_block.append(line)
            else:
                if current_block:
                    blocks.append(current_block)
                    current_block = []
        if current_block:
            blocks.append(current_block)
            
        for block_lines in blocks:
            first_line = block_lines[0].lstrip(">").strip()
            if first_line.startswith('"'):
                quote_text = first_line.strip('"')
                
                # Try to extract URL from source line
                url = ""
                full_text = "\n".join(block_lines)
                source_match = re.search(r'Source:\s*\[.*?\]\((.*?)\)', full_text)
                if source_match:
                    url = source_match.group(1).strip()
                    
                quotes.append((quote_text, url))
        return quotes

    def _get_content_ids(self, sources: List, target_url: str) -> List[str]:
        """
        Find content_id(s) matching the target_url, or return all if url not found/matched.
        """
        content_ids = []
        if target_url:
            for source in sources:
                if source.url == target_url and source.content_id:
                    content_ids.append(source.content_id)
                    
        # If no specific match, return all content_ids to search broadly
        if not content_ids:
            for source in sources:
                if source.content_id:
                    content_ids.append(source.content_id)
                    
        return content_ids

    def _load_chunks(self, content_id: str) -> Dict[str, str]:
        """
        Load all chunks for a given content_id. 
        Returns dict of chunk_id -> chunk_text.
        """
        chunks = {}
        # Search in library and youtube subdirs
        for path in self.chunks_dir.rglob(f"{content_id}_*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    chunks[path.name] = data.get("text", "")
            except Exception as e:
                logger.warning("Failed to read chunk %s: %s", path, e)
        return chunks
        
    def _load_raw(self, content_id: str) -> Dict[str, str]:
        """
        Fallback to load raw content for a given content_id.
        """
        raw_content = {}
        for path in self.raw_dir.rglob(f"{content_id}*"):
            if path.is_file() and path.suffix in [".md", ".txt", ".json", ".vtt"]:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        if path.suffix == ".json":
                            # Note: maybe it's metadata, but we'll try reading its string representation just in case
                            raw_content[path.name] = f.read()
                        else:
                            raw_content[path.name] = f.read()
                except Exception as e:
                    logger.warning("Failed to read raw file %s: %s", path, e)
        return raw_content

    def verify_skill(self, skill_path: str) -> QuoteVerificationResult:
        """
        Verify all quotes in a skill file against source chunks.
        """
        frontmatter, body = parse_skill_file(skill_path)
        quotes = self._extract_quotes(body)
        
        if not quotes:
            logger.warning("No quotes found in %s", skill_path)
            return QuoteVerificationResult(
                skill_id=frontmatter.skill_id,
                status="warning",
                quote_results=[]
            )
            
        results = []
        overall_status = "pass"
        
        for quote_text, source_url in quotes:
            content_ids = self._get_content_ids(frontmatter.provenance.sources, source_url)
            
            best_ratio = 0.0
            best_partial = 0.0
            best_chunk_id = None
            
            for cid in content_ids:
                texts_to_search = self._load_chunks(cid)
                if not texts_to_search:
                    texts_to_search = self._load_raw(cid)
                    
                for file_id, text in texts_to_search.items():
                    if not text:
                        continue
                        
                    ratio = fuzz.ratio(quote_text, text)
                    partial = fuzz.partial_ratio(quote_text, text)
                    
                    if partial > best_partial or (partial == best_partial and ratio > best_ratio):
                        best_partial = partial
                        best_ratio = ratio
                        best_chunk_id = file_id
                        
            # Evaluate against thresholds
            if best_ratio >= self.ratio_threshold and best_partial >= self.partial_threshold:
                status = "pass"
            elif best_ratio < self.ratio_threshold and best_partial >= self.partial_threshold:
                status = "warning"
                if overall_status == "pass":
                    overall_status = "warning"
            else:
                status = "fail"
                overall_status = "fail"
                
            results.append(QuoteResult(
                quote_text=quote_text,
                best_ratio=best_ratio,
                best_partial_ratio=best_partial,
                matched_chunk_id=best_chunk_id,
                status=status
            ))
            
        return QuoteVerificationResult(
            skill_id=frontmatter.skill_id,
            status=overall_status,
            quote_results=results
        )
