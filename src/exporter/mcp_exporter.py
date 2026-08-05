"""
MCP (Model Context Protocol) Spec Exporter for OpenOpenYC Skills.
Reads generated skills and exports MCP JSON spec files.
"""

import os
import json
import logging
from typing import List
from pathlib import Path

from src.config import load_config
from src.exporter.utils import parse_skill_file, extract_skill_metadata

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
    frontmatter, body = parse_skill_file(skill_path)
    metadata = extract_skill_metadata(frontmatter, body)

    input_schema = {
        "type": "object",
        "properties": metadata["input_properties"],
        "required": ["question"],
    }

    mcp_name = frontmatter.skill_id.replace("-", "_")

    handler_path = f"skills/{frontmatter.category}/{frontmatter.skill_id}.md"

    mcp_json = {
        "name": mcp_name,
        "description": metadata["description"],
        "inputSchema": input_schema,
        "handler": {"type": "file", "path": handler_path},
        "tags": frontmatter.tags,
        "fallback": {
            "mode": "closest_skills",
            "count": 3,
            "use_agent_knowledge": True,
            "invent_quotes": False,
        },
    }

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{frontmatter.skill_id}.json")

    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(mcp_json, f, indent=2)
    except Exception as e:
        raise ValueError(f"Failed to write output to {out_path}: {e}") from e

    return out_path


def export_all_mcp(
    skills_dir: str = "skills", output_dir: str = "specs/mcp"
) -> List[str]:
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
