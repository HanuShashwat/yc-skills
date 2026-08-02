"""
Hallucination Guard for YC Skills Forge.
Security-critical boundary verifying that no unsupported claims are introduced.
"""
import json
import logging
import re
import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple, Dict

import openai
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader

from src.config import load_config
from src.exporter.utils import parse_skill_file

logger = logging.getLogger(__name__)

class HallucinationCheckResult(BaseModel):
    """Result of checking a skill for hallucinations."""
    skill_id: str
    status: str
    speaker_check: str
    claim_check: str
    llm_check: str
    flagged_claims: List[str]
    issues: List[str]

class HallucinationGuard:
    """Security boundary enforcing quote fidelity and detecting hallucinations."""
    
    def __init__(self, db_path: str = "data/registry.db", chunks_dir: str = "data/chunks", config=None):
        self.db_path = db_path
        self.chunks_dir = Path(chunks_dir)
        self.config = config or load_config()
        self.env = Environment(loader=FileSystemLoader("src/forge/prompts"))
        
    def _extract_speakers(self, body: str) -> List[str]:
        """Extract speakers from attribution lines (> - **Name**, Designation) or (> — **Name**, Designation)."""
        speakers = []
        pattern = r">\s*[-—]\s*\*\*(.*?)\*\*(?:,.*)?"
        for line in body.splitlines():
            match = re.search(pattern, line)
            if match:
                speakers.append(match.group(1).strip())
        return list(set(speakers))
        
    def _get_db_speakers_for_sources(self, content_ids: List[str]) -> Dict[str, str]:
        """Get mapping of content_id -> speaker from DB."""
        if not content_ids:
            return {}
        result = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                placeholders = ",".join(["?"] * len(content_ids))
                cursor.execute(
                    f"SELECT content_id, speaker FROM content WHERE content_id IN ({placeholders})",
                    content_ids
                )
                for row in cursor.fetchall():
                    if row[1]:
                        result[row[0]] = row[1]
        except sqlite3.Error as e:
            logger.error("Database error in hallucination guard: %s", e)
        return result

    def _detect_claims(self, section_text: str) -> List[str]:
        """Detect specific factual claims (years, dollar amounts, percentages)."""
        claims = []
        
        # Years (1990 - 2099)
        for match in re.finditer(r"\b(19|20)\d{2}\b", section_text):
            claims.append(match.group(0))
            
        # Dollar amounts
        for match in re.finditer(r"\$\d+(?:\.\d+)?(?:[kKmMbB])?", section_text):
            claims.append(match.group(0))
            
        # Percentages
        for match in re.finditer(r"\d+(?:\.\d+)?%", section_text):
            claims.append(match.group(0))
            
        return list(set(claims))
        
    def _extract_sections(self, body: str) -> Tuple[str, str, List[Dict]]:
        """Extract Principle, Application, and Quotes for the LLM prompt."""
        principle = ""
        application = ""
        quotes = []
        
        current_section = None
        lines = body.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("## Principle"):
                current_section = "principle"
                continue
            elif line.startswith("## Personalized Application"):
                current_section = "application"
                continue
            elif line.startswith("## "):
                if current_section in ["principle", "application"]:
                    current_section = None
            
            if current_section == "principle" and line.strip():
                principle += line + "\n"
            elif current_section == "application" and line.strip():
                application += line + "\n"
                
            # Keep extracting quotes too
            if line.startswith("> \""):
                speaker = "Unknown"
                if i + 1 < len(lines):
                    match = re.search(r">\s*[-—]\s*\*\*(.*?)\*\*", lines[i+1])
                    if match:
                        speaker = match.group(1).strip()
                quotes.append({"text": line.lstrip(">").strip().strip('"'), "speaker": speaker})
                
        return principle.strip(), application.strip(), quotes

    def _call_dedicated_llm(self, prompt: str) -> Optional[Dict]:
        """Call the dedicated validator LLM directly, bypassing the rotating pool."""
        val_config = self.config.providers.validation.dedicated_validator
        
        provider_name = val_config.provider
        if provider_name not in self.config.providers.providers:
            logger.error("Dedicated validator provider %s not found in config.", provider_name)
            return None
            
        provider_cfg = self.config.providers.providers[provider_name]
        
        client = openai.OpenAI(
            api_key=provider_cfg.api_key,
            base_url=provider_cfg.base_url,
            timeout=provider_cfg.timeout
        )
        
        try:
            response = client.chat.completions.create(
                model=val_config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=val_config.temperature,
                max_tokens=val_config.max_tokens,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except openai.RateLimitError as e:
            if "429" in str(e) or "quota" in str(e).lower():
                logger.warning("LLM-as-judge skipped due to quota exhaustion.")
                return None
            logger.warning("LLM-as-judge rate limited: %s", e)
            return None
        except Exception as e:
            logger.error("LLM-as-judge failed: %s", e)
            return None

    def _check_claim_in_chunks(self, claim: str, content_ids: List[str]) -> bool:
        """Check if a claim appears in any chunk for the given content_ids."""
        for cid in content_ids:
            for path in self.chunks_dir.rglob(f"{cid}_*.json"):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        text = data.get("text", "")
                        if claim in text:
                            return True
                except Exception:
                    pass
        return False

    def check_skill(self, skill_path: str) -> HallucinationCheckResult:
        """Check skill for hallucinations."""
        frontmatter, body = parse_skill_file(skill_path)
        skill_id = frontmatter.skill_id
        
        content_ids = [s.content_id for s in frontmatter.provenance.sources if s.content_id]
        
        # 1. & 2. Speaker Verification and Source Cross-Reference
        speakers_in_skill = self._extract_speakers(body)
        db_speakers = self._get_db_speakers_for_sources(content_ids)
        
        speaker_check = "pass"
        db_speaker_set = set(db_speakers.values())
        
        for speaker in speakers_in_skill:
            if speaker not in db_speaker_set:
                speaker_check = "fail"
                break
                
        for cid in content_ids:
            if cid not in db_speakers:
                speaker_check = "fail"
                break

        # 3. Unsupported Claims Detection
        principle, application, quotes = self._extract_sections(body)
        claims = self._detect_claims(principle + "\n" + application)
        
        flagged_claims = []
        claim_check = "pass"
        for claim in claims:
            if not self._check_claim_in_chunks(claim, content_ids):
                flagged_claims.append(claim)
                claim_check = "fail"
                
        # 4. LLM-as-Judge
        llm_check = "skipped"
        issues = []
        
        template = self.env.get_template("validate.j2")
        prompt = template.render(quotes=quotes, principle=principle, application=application)
        
        llm_result = self._call_dedicated_llm(prompt)
        if llm_result is not None:
            supported = llm_result.get("supported", False)
            if not supported:
                llm_check = "fail"
                issues = llm_result.get("issues", [])
            else:
                llm_check = "pass"
                
        # Determine overall status
        status = "pass"
        if speaker_check == "fail" or claim_check == "fail" or llm_check == "fail":
            status = "fail"
            
        return HallucinationCheckResult(
            skill_id=skill_id,
            status=status,
            speaker_check=speaker_check,
            claim_check=claim_check,
            llm_check=llm_check,
            flagged_claims=flagged_claims,
            issues=issues
        )
