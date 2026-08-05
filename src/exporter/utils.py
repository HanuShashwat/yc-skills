"""
Utility functions for skill exporters.
"""

import re
import yaml
from typing import Tuple, Dict, Any
from pydantic import ValidationError

from src.models import SkillFrontmatter


def parse_skill_file(skill_path: str) -> Tuple[SkillFrontmatter, str]:
    """
    Parse a skill Markdown file into its frontmatter and body.

    Args:
        skill_path: Path to the skill file.

    Returns:
        Tuple of (SkillFrontmatter, body_text).

    Raises:
        ValueError: If file cannot be read, lacks frontmatter, or has invalid schema.
    """
    try:
        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        raise ValueError(f"Could not read {skill_path}: {e}") from e

    parts = content.split("---")
    if len(parts) < 3:
        raise ValueError(f"Missing valid YAML frontmatter in {skill_path}")

    try:
        frontmatter_dict = yaml.safe_load(parts[1])
    except Exception as e:
        raise ValueError(
            f"Failed to parse YAML frontmatter in {skill_path}: {e}"
        ) from e

    if not frontmatter_dict:
        raise ValueError(f"Empty YAML frontmatter in {skill_path}")

    try:
        frontmatter = SkillFrontmatter(**frontmatter_dict)
    except ValidationError as e:
        raise ValueError(f"Invalid frontmatter schema in {skill_path}: {e}") from e

    body = "---".join(parts[2:])
    return frontmatter, body


def extract_skill_metadata(frontmatter: SkillFrontmatter, body: str) -> Dict[str, Any]:
    """
    Extract common metadata (summary, input properties, description) from a skill.

    Args:
        frontmatter: Parsed SkillFrontmatter.
        body: Markdown body of the skill.

    Returns:
        Dictionary containing extracted metadata.
    """
    # Extract Principle section for summary
    principle_match = re.search(r"## Principle\s+(.+?)(?=## |\Z)", body, re.DOTALL)
    if principle_match:
        summary = principle_match.group(1).strip()
    else:
        summary = "A precise skill providing YC guidance and verifiable quotes"

    input_properties = {
        "question": {
            "type": "string",
            "description": f"The specific question or context regarding {frontmatter.name} to evaluate against this skill.",
        }
    }

    follow_up_match = re.search(
        r"### Follow-Up Questions\s+(.+?)(?=## |\Z)", body, re.DOTALL
    )
    if follow_up_match:
        questions_text = follow_up_match.group(1).strip()
        if "runway" in questions_text.lower():
            input_properties["runway_months"] = {
                "type": "integer",
                "description": "Current runway in months (if known)",
            }
        if "burn" in questions_text.lower():
            input_properties["monthly_burn"] = {
                "type": "number",
                "description": "Current monthly burn rate (if known)",
            }

    speaker_details = []
    for s in frontmatter.provenance.sources:
        speaker = s.speaker or "Unknown"
        desig = s.designation or "Unknown"
        speaker_details.append(f"{speaker} ({desig})")

    sources_str = ", ".join(speaker_details)
    description = f"YC advice on {frontmatter.name}. Sources: {sources_str}. {summary}."

    return {
        "summary": summary,
        "input_properties": input_properties,
        "description": description,
    }
