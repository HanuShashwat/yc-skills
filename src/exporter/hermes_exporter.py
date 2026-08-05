"""
Hermes Spec Exporter for OpenOpenYC Skills.
Reads generated skills and exports plain-text system prompt fragments.
"""

import os
import logging
import re
from typing import List
from pathlib import Path

from src.config import load_config
from src.exporter.utils import parse_skill_file

logger = logging.getLogger(__name__)


def export_hermes(skill_path: str, output_dir: str = "specs/hermes") -> str:
    """
    Process a single skill file and generate its Hermes plain-text spec.

    Args:
        skill_path: Path to the skill Markdown file.
        output_dir: Directory where the Hermes spec should be written.

    Returns:
        Path to the generated txt file.

    Raises:
        ValueError: If the skill file cannot be parsed or is invalid.
    """
    frontmatter, body = parse_skill_file(skill_path)

    # Extract Principle section
    principle_match = re.search(r"## Principle\s+(.+?)(?=## |\Z)", body, re.DOTALL)
    principle_text = principle_match.group(1).strip() if principle_match else ""

    # Extract Verbatim Quotes
    quotes_match = re.search(r"## Verbatim Quotes\s+(.+?)(?=## |\Z)", body, re.DOTALL)
    quotes_text = ""
    if quotes_match:
        raw_quotes = quotes_match.group(1).strip()
        quote_blocks = raw_quotes.split("\n\n")
        formatted_quotes = []
        for block in quote_blocks:
            lines = [
                line.lstrip(">").strip()
                for line in block.split("\n")
                if line.strip().startswith(">")
            ]
            if len(lines) >= 2:
                quote = lines[0].strip('"')
                attr_line = lines[1]
                # Remove weird characters like ?" or leading dashes
                attr_line = re.sub(r"^[^\w\*]+", "", attr_line)
                attr_match = re.search(r"\*\*(.+?)\*\*,\s*(.+)", attr_line)
                if attr_match:
                    speaker = attr_match.group(1).strip()
                    designation = attr_match.group(2).strip()
                    formatted_quotes.append(f'- "{quote}" — {speaker}, {designation}')

        if formatted_quotes:
            quotes_text = "\n".join(formatted_quotes)

    # Extract When to Use This Skill
    when_match = re.search(
        r"### When to Use This Skill\s+(.+?)(?=### |## |\Z)", body, re.DOTALL
    )
    when_to_use_text = when_match.group(1).strip() if when_match else ""
    when_to_use_str = re.sub(r"\s+", " ", when_to_use_text).strip()

    # Extract Agent Protocol
    protocol_match = re.search(
        r"### Agent Protocol\s+(.+?)(?=### |## |\Z)", body, re.DOTALL
    )
    protocol_text = protocol_match.group(1).strip() if protocol_match else ""
    protocol_steps = [
        line.strip()
        for line in protocol_text.split("\n")
        if re.match(r"^\d+\.", line.strip())
    ]
    protocol_str = "\n".join(protocol_steps)

    # Extract Follow-Up Questions
    questions_match = re.search(
        r"### Follow-Up Questions\s+(.+?)(?=### |## |\Z)", body, re.DOTALL
    )
    questions_str = questions_match.group(1).strip() if questions_match else ""

    # Extract Edge Cases
    edge_cases_match = re.search(r"## Edge Cases\s+(.+?)(?=## |\Z)", body, re.DOTALL)
    edge_cases_str = edge_cases_match.group(1).strip() if edge_cases_match else ""

    tags_str = ", ".join(frontmatter.tags)
    related_skills_str = ", ".join(frontmatter.related_skills)

    output_lines = [
        f"[SKILL: {frontmatter.skill_id}]",
        f"NAME: {frontmatter.name}",
        f"CATEGORY: {frontmatter.category}",
        f"TAGS: {tags_str}",
        "",
        f"PRINCIPLE: {principle_text}",
        "",
        "VERBATIM QUOTES:",
        quotes_text if quotes_text else "- No quotes available",
        "",
        f"WHEN TO USE: {when_to_use_str}",
        "",
        "AGENT PROTOCOL:",
        protocol_str if protocol_str else "1. Consult general knowledge",
        "",
        "FOLLOW-UP QUESTIONS:",
        questions_str,
        "",
        "EDGE CASES:",
        edge_cases_str,
        "",
        "FALLBACK: If query does not match, return 3 closest skills and use general knowledge. DO NOT invent YC quotes.",
        "",
        f"RELATED SKILLS: {related_skills_str}",
        "[END SKILL]",
    ]

    output_text = "\n".join(output_lines) + "\n"

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{frontmatter.skill_id}.txt")

    try:
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(output_text)
    except Exception as e:
        raise ValueError(f"Failed to write output to {out_path}: {e}") from e

    return out_path


def export_all_hermes(
    skills_dir: str = "skills", output_dir: str = "specs/hermes"
) -> List[str]:
    """
    Process all .md files in the skills directory and generate Hermes spec files.

    Args:
        skills_dir: Base directory containing skill Markdown files.
        output_dir: Directory where Hermes specs should be written.

    Returns:
        List of generated txt file paths.
    """
    config = load_config()
    if "hermes" not in config.pipeline.export.formats:
        logger.info("Hermes export is disabled in config/pipeline.yml. Skipping.")
        return []

    generated_files = []
    skills_path = Path(skills_dir)
    for p in skills_path.rglob("*.md"):
        try:
            out = export_hermes(str(p), output_dir)
            generated_files.append(out)
        except ValueError as e:
            logger.warning("Skipping %s: %s", p, e)

    return generated_files
