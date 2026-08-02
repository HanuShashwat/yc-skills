"""
MCP (Model Context Protocol) Spec Exporter for YC Skills Forge.
Reads generated skills and exports MCP JSON spec files.
"""
import os
import json
import logging
import re
from typing import List
from pathlib import Path
import yaml
from pydantic import ValidationError

from src.config import load_config
from src.models import SkillFrontmatter

logger = logging.getLogger(__name__)

def export_mcp(skill_path: str, output_dir: str = "specs/mcp") -> str:
    """
    Process a single skill file and generate its MCP spec JSON.
    
    Args:
        skill_path: Path to the skill Markdown file.
        output_dir: Directory where the MCP spec should be written.
        
    Returns:
        Path to the generated JSON file.
        
    Raises:
        ValueError: If the skill file cannot be parsed or is invalid.
    """
    try:
        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.error("Failed to read file %s: %s", skill_path, e)
        raise ValueError(f"Could not read {skill_path}: {e}") from e

    # Split frontmatter
    parts = content.split("---")
    if len(parts) < 3:
        raise ValueError(f"Missing valid YAML frontmatter in {skill_path}")
        
    try:
        frontmatter_dict = yaml.safe_load(parts[1])
    except Exception as e:
        raise ValueError(f"Failed to parse YAML frontmatter in {skill_path}: {e}") from e
        
    if not frontmatter_dict:
        raise ValueError(f"Empty YAML frontmatter in {skill_path}")
        
    # Validate with Pydantic model
    try:
        frontmatter = SkillFrontmatter(**frontmatter_dict)
    except ValidationError as e:
        raise ValueError(f"Invalid frontmatter schema in {skill_path}: {e}") from e
        
    # Parse markdown body
    body = "---".join(parts[2:])
    
    # Extract Principle section for summary
    principle_match = re.search(r"## Principle\s+(.+?)(?=## |\Z)", body, re.DOTALL)
    if principle_match:
        summary = principle_match.group(1).strip()
    else:
        summary = "A precise skill providing YC guidance and verifiable quotes"
        
    # Extract properties for inputSchema based on When to Use This Skill and Follow-Up Questions
    # We will build a basic static schema since extracting dynamic properties reliably from prose is LLM territory.
    input_properties = {
        "question": {
            "type": "string",
            "description": f"The specific question or context regarding {frontmatter.name} to evaluate against this skill."
        }
    }
    
    # Simple keyword based extraction from 'Follow-Up Questions'
    follow_up_match = re.search(r"### Follow-Up Questions\s+(.+?)(?=## |\Z)", body, re.DOTALL)
    if follow_up_match:
        questions_text = follow_up_match.group(1).strip()
        if "runway" in questions_text.lower():
            input_properties["runway_months"] = {
                "type": "integer",
                "description": "Current runway in months (if known)"
            }
        if "burn" in questions_text.lower():
            input_properties["monthly_burn"] = {
                "type": "number",
                "description": "Current monthly burn rate (if known)"
            }
    
    input_schema = {
        "type": "object",
        "properties": input_properties,
        "required": ["question"]
    }
    
    mcp_name = frontmatter.skill_id.replace("-", "_")
    
    speaker_details = []
    for s in frontmatter.provenance.sources:
        speaker = s.speaker or "Unknown"
        desig = s.designation or "Unknown"
        speaker_details.append(f"{speaker} ({desig})")
        
    sources_str = ", ".join(speaker_details)
    
    description = f"YC advice on {frontmatter.name}. Sources: {sources_str}. {summary}."
    
    handler_path = f"skills/{frontmatter.category}/{frontmatter.skill_id}.md"
    
    mcp_json = {
        "name": mcp_name,
        "description": description,
        "inputSchema": input_schema,
        "handler": {
            "type": "file",
            "path": handler_path
        },
        "tags": frontmatter.tags,
        "fallback": {
            "mode": "closest_skills",
            "count": 3,
            "use_agent_knowledge": True,
            "invent_quotes": False
        }
    }
    
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{frontmatter.skill_id}.json")
    
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(mcp_json, f, indent=2)
    except Exception as e:
        raise ValueError(f"Failed to write output to {out_path}: {e}") from e
        
    return out_path

def export_all_mcp(skills_dir: str = "skills", output_dir: str = "specs/mcp") -> List[str]:
    """
    Process all .md files in the skills directory and generate MCP spec JSONs.
    
    Args:
        skills_dir: Base directory containing skill Markdown files.
        output_dir: Directory where MCP specs should be written.
        
    Returns:
        List of generated JSON file paths.
    """
    config = load_config()
    if "mcp" not in config.pipeline.export.formats:
        logger.info("MCP export is disabled in config/pipeline.yml. Skipping.")
        return []
        
    generated_files = []
    skills_path = Path(skills_dir)
    for p in skills_path.rglob("*.md"):
        try:
            out = export_mcp(str(p), output_dir)
            generated_files.append(out)
        except ValueError as e:
            logger.warning("Skipping %s: %s", p, e)
            
    return generated_files
