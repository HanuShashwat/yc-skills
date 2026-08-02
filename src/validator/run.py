"""
Unified Validator Runner for YC Skills Forge.
Orchestrates schema validation, quote verification, and hallucination guard.
"""
import argparse
import logging
import os
import shutil
import sqlite3
import sys
from pathlib import Path

from src.validator.schema_validator import SchemaValidator
from src.validator.quote_verifier import QuoteVerifier
from src.validator.hallucination_guard import HallucinationGuard

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def update_skill_state(db_path: str, skill_id: str, state: str) -> None:
    """Update the state of a skill in the database."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # Fails safely if table doesn't exist in testing
            cursor.execute(
                "UPDATE skills SET state = ? WHERE skill_id = ?",
                (state, skill_id)
            )
            conn.commit()
    except sqlite3.Error as e:
        # It's okay if table doesn't exist, we just log debug (to not clutter the output table)
        logger.debug("Failed to update skill state in DB: %s", e)

def move_to_failed(skill_path: Path, skill_id: str) -> None:
    """Move a failed skill file to the _failed directory."""
    failed_dir = Path("skills") / "_failed"
    if skill_path.parent.name == "_failed":
        return
    
    os.makedirs(failed_dir, exist_ok=True)
    dest = failed_dir / f"{skill_id}.md"
    try:
        shutil.move(str(skill_path), str(dest))
    except Exception as e:
        logger.error("Failed to move %s to %s: %s", skill_id, failed_dir, e)

def main() -> None:
    """Main entry point for validator runner."""
    parser = argparse.ArgumentParser(description="Run YC Skills Forge Validators")
    parser.add_argument("--all", action="store_true", help="Validate all skills in skills/")
    parser.add_argument("--skill-id", type=str, help="Validate a single skill by ID")
    
    args = parser.parse_args()
    
    if not args.all and not args.skill_id:
        logger.error("Must specify either --all or --skill-id")
        sys.exit(1)
        
    skills_dir = Path("skills")
    db_path = "data/registry.db"
    
    if not skills_dir.exists():
        logger.info("skills/ directory does not exist. Nothing to validate.")
        sys.exit(0)
        
    skill_files = []
    if args.skill_id:
        found = list(skills_dir.rglob(f"{args.skill_id}.md"))
        if not found:
            logger.error("Skill %s not found.", args.skill_id)
            sys.exit(1)
        skill_files = found
    else:
        # Ignore skills in _failed
        skill_files = [f for f in skills_dir.rglob("*.md") if f.parent.name != "_failed"]
        
    if not skill_files:
        logger.info("No skill files found to validate.")
        sys.exit(0)
        
    schema_validator = SchemaValidator(str(skills_dir))
    quote_verifier = QuoteVerifier()
    hallucination_guard = HallucinationGuard(db_path=db_path)
    
    logger.info("%-37s | %-6s | %-6s | %-13s | Result", "Skill ID", "Schema", "Quotes", "Hallucination")
    
    any_failed = False
    
    for skill_file in skill_files:
        skill_id = skill_file.stem
        
        schema_status = "-"
        quote_status = "-"
        hallucination_status = "-"
        overall_result = "✓ PASS"
        
        # 1. Schema Validation
        schema_res = schema_validator.validate_skill(str(skill_file))
        schema_status = "PASS" if schema_res.status == "pass" else ("FAIL" if schema_res.status == "fail" else "WARN")
        
        if schema_res.status == "fail":
            overall_result = "✗ FAIL"
            any_failed = True
            update_skill_state(db_path, skill_id, "failed")
            move_to_failed(skill_file, skill_id)
        else:
            # 2. Quote Verification
            quote_res = quote_verifier.verify_skill(str(skill_file))
            quote_status = "PASS" if quote_res.status == "pass" else ("FAIL" if quote_res.status == "fail" else "WARN")
            
            if quote_res.status == "fail":
                overall_result = "✗ FAIL"
                any_failed = True
                update_skill_state(db_path, skill_id, "failed")
                move_to_failed(skill_file, skill_id)
            else:
                # 3. Hallucination Guard
                halluc_res = hallucination_guard.check_skill(str(skill_file))
                if halluc_res.status == "pass":
                    hallucination_status = "PASS"
                elif halluc_res.status == "skipped":
                    hallucination_status = "SKIP"
                elif halluc_res.status == "fail":
                    hallucination_status = "FAIL"
                else:
                    hallucination_status = "WARN"
                    
                if halluc_res.status == "fail":
                    overall_result = "✗ FAIL"
                    any_failed = True
                    update_skill_state(db_path, skill_id, "failed")
                    move_to_failed(skill_file, skill_id)
                elif quote_status == "WARN" or hallucination_status == "WARN" or schema_status == "WARN":
                    overall_result = "⚠ WARNING"
                    
        logger.info("%-37s | %-6s | %-6s | %-13s | %s", skill_id, schema_status, quote_status, hallucination_status, overall_result)
        
    if any_failed:
        sys.exit(1)
    else:
        sys.exit(0)
        
if __name__ == "__main__":
    main()
