"""
Schema Validator for OpenYC Skills.
Validates skill frontmatter using Pydantic constraints and custom rules.
"""

import logging
from pathlib import Path
from typing import List
import yaml
from pydantic import BaseModel, ValidationError

from src.models import SkillFrontmatter
from src.config import load_config

logger = logging.getLogger(__name__)


class SchemaValidationResult(BaseModel):
    """Result of validating a skill's schema."""

    skill_id: str
    status: str
    errors: List[str]
    warnings: List[str]


class SchemaValidator:
    """Validates skill markdown files against the SkillFrontmatter schema and structural rules."""

    def __init__(self, skills_dir: str = "skills", config=None):
        self.skills_dir = Path(skills_dir)
        self.config = config or load_config()

    def validate_skill(self, skill_path: str) -> SchemaValidationResult:
        """
        Validate a skill file against Pydantic schema and structural constraints.
        """
        path = Path(skill_path)
        skill_id = path.stem
        errors = []
        warnings = []

        if path.suffix != ".md":
            errors.append(f"Invalid file extension '{path.suffix}'. Must be '.md'.")
            return SchemaValidationResult(
                skill_id=skill_id, status="fail", errors=errors, warnings=warnings
            )

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            errors.append(f"Could not read file: {e}")
            return SchemaValidationResult(
                skill_id=skill_id, status="fail", errors=errors, warnings=warnings
            )

        parts = content.split("---")
        if len(parts) < 3 or not content.startswith("---"):
            errors.append("Missing valid YAML frontmatter delimiters '---'.")
            return SchemaValidationResult(
                skill_id=skill_id, status="fail", errors=errors, warnings=warnings
            )

        try:
            frontmatter_dict = yaml.safe_load(parts[1])
        except Exception as e:
            errors.append(f"Malformed YAML frontmatter: {e}")
            return SchemaValidationResult(
                skill_id=skill_id, status="fail", errors=errors, warnings=warnings
            )

        if not frontmatter_dict:
            errors.append("Empty YAML frontmatter.")
            return SchemaValidationResult(
                skill_id=skill_id, status="fail", errors=errors, warnings=warnings
            )

        # 1. Pydantic validation
        frontmatter = None
        try:
            frontmatter = SkillFrontmatter(**frontmatter_dict)
        except ValidationError as e:
            for err in e.errors():
                loc = ".".join(str(loc_item) for loc_item in err["loc"])
                msg = err["msg"]
                errors.append(f"{loc}: {msg}")

        # If Pydantic failed, we can't do the rest properly if they depend on valid fields
        if not frontmatter:
            return SchemaValidationResult(
                skill_id=skill_id, status="fail", errors=errors, warnings=warnings
            )

        # 2. skill_id matches filename
        if frontmatter.skill_id != skill_id:
            errors.append(
                f"skill_id '{frontmatter.skill_id}' does not match filename '{skill_id}'."
            )

        # 3. category matches parent directory name
        parent_dir = path.parent.name
        if frontmatter.category != parent_dir:
            errors.append(
                f"category '{frontmatter.category}' does not match parent directory '{parent_dir}'."
            )

        # 4. related_skills exist as .md files
        for rel_id in frontmatter.related_skills:
            # Check if this skill exists anywhere in skills_dir
            found = list(self.skills_dir.rglob(f"{rel_id}.md"))
            if not found:
                errors.append(
                    f"related_skill '{rel_id}' does not correspond to an existing .md file."
                )

        # 5. tags validation: lowercase, no spaces, max 20 chars
        for tag in frontmatter.tags:
            if tag != tag.lower():
                errors.append(f"tag '{tag}' must be lowercase.")
            if " " in tag:
                errors.append(f"tag '{tag}' must not contain spaces.")
            if len(tag) > 20:
                errors.append(f"tag '{tag}' must be 20 characters or less.")

        status = "fail" if errors else "pass"
        return SchemaValidationResult(
            skill_id=skill_id, status=status, errors=errors, warnings=warnings
        )
