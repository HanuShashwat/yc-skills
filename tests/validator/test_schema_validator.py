"""
Tests for Schema Validator.
"""
import yaml
from pathlib import Path
import pytest
from copy import deepcopy

from src.validator.schema_validator import SchemaValidator

def setup_test_files(tmp_path: Path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    
    # Create related skills to satisfy existence check
    (skills_dir / "yc-fundraising-seed-round-valuation.md").write_text("---")
    (skills_dir / "yc-fundraising-investor-update-emails.md").write_text("---")
    (skills_dir / "yc-founder-mental-models-default-alive-dead.md").write_text("---")
    
    # Read the valid sample frontmatter
    sample_yml = Path("tests/fixtures/sample_frontmatter.yml").read_text(encoding="utf-8")
    sample_data = yaml.safe_load(sample_yml)
    
    return skills_dir, sample_data

def create_skill(skills_dir: Path, skill_id: str, category: str, data: dict) -> Path:
    cat_dir = skills_dir / category
    cat_dir.mkdir(exist_ok=True)
    skill_path = cat_dir / f"{skill_id}.md"
    content = "---\n" + yaml.safe_dump(data) + "---\n\nBody"
    skill_path.write_text(content, encoding="utf-8")
    return skill_path

def test_valid_schema_pass(tmp_path):
    skills_dir, sample_data = setup_test_files(tmp_path)
    skill_path = create_skill(skills_dir, "yc-fundraising-seed-round-timing", "fundraising", sample_data)
    
    validator = SchemaValidator(str(skills_dir))
    res = validator.validate_skill(str(skill_path))
    
    assert res.status == "pass"
    assert len(res.errors) == 0

def test_invalid_skill_id_fail(tmp_path):
    skills_dir, sample_data = setup_test_files(tmp_path)
    data = deepcopy(sample_data)
    # missing yc- prefix and uppercase
    data["skill_id"] = "FUNDRAISING-seed"
    skill_path = create_skill(skills_dir, "FUNDRAISING-seed", "fundraising", data)
    
    validator = SchemaValidator(str(skills_dir))
    res = validator.validate_skill(str(skill_path))
    
    assert res.status == "fail"
    assert any("skill_id" in err for err in res.errors)

def test_missing_required_fields_fail(tmp_path):
    skills_dir, sample_data = setup_test_files(tmp_path)
    data = deepcopy(sample_data)
    del data["source_count"]
    del data["quote_count"]
    skill_path = create_skill(skills_dir, "yc-fundraising-seed-round-timing", "fundraising", data)
    
    validator = SchemaValidator(str(skills_dir))
    res = validator.validate_skill(str(skill_path))
    
    assert res.status == "fail"
    assert any("source_count" in err for err in res.errors)
    assert any("quote_count" in err for err in res.errors)

def test_broken_related_skills_fail(tmp_path):
    skills_dir, sample_data = setup_test_files(tmp_path)
    data = deepcopy(sample_data)
    data["related_skills"].append("yc-does-not-exist")
    skill_path = create_skill(skills_dir, "yc-fundraising-seed-round-timing", "fundraising", data)
    
    validator = SchemaValidator(str(skills_dir))
    res = validator.validate_skill(str(skill_path))
    
    assert res.status == "fail"
    assert any("yc-does-not-exist" in err for err in res.errors)

def test_tags_validation_fail(tmp_path):
    skills_dir, sample_data = setup_test_files(tmp_path)
    data = deepcopy(sample_data)
    data["tags"] = ["UPPERCASE", "has spaces", "this-tag-is-way-too-long-for-validation"]
    skill_path = create_skill(skills_dir, "yc-fundraising-seed-round-timing", "fundraising", data)
    
    validator = SchemaValidator(str(skills_dir))
    res = validator.validate_skill(str(skill_path))
    
    assert res.status == "fail"
    err_str = " ".join(res.errors)
    assert "lowercase" in err_str
    assert "spaces" in err_str
    assert "20 characters" in err_str

def test_category_mismatch_fail(tmp_path):
    skills_dir, sample_data = setup_test_files(tmp_path)
    data = deepcopy(sample_data)
    # category in frontmatter is fundraising, but directory is hiring
    skill_path = create_skill(skills_dir, "yc-fundraising-seed-round-timing", "hiring", data)
    
    validator = SchemaValidator(str(skills_dir))
    res = validator.validate_skill(str(skill_path))
    
    assert res.status == "fail"
    assert any("category 'fundraising' does not match parent directory 'hiring'" in err for err in res.errors)

def test_skill_id_mismatch_filename_fail(tmp_path):
    skills_dir, sample_data = setup_test_files(tmp_path)
    data = deepcopy(sample_data)
    data["skill_id"] = "yc-fundraising-seed-round-timing"
    # creating file with a different name
    skill_path = create_skill(skills_dir, "yc-fundraising-different", "fundraising", data)
    
    validator = SchemaValidator(str(skills_dir))
    res = validator.validate_skill(str(skill_path))
    
    assert res.status == "fail"
    assert any("does not match filename" in err for err in res.errors)

def test_malformed_yaml(tmp_path):
    skills_dir, sample_data = setup_test_files(tmp_path)
    cat_dir = skills_dir / "fundraising"
    cat_dir.mkdir(exist_ok=True)
    skill_path = cat_dir / "yc-fundraising-seed-round-timing.md"
    skill_path.write_text("---\n[invalid yaml\n---\nBody", encoding="utf-8")
    
    validator = SchemaValidator(str(skills_dir))
    res = validator.validate_skill(str(skill_path))
    
    assert res.status == "fail"
    assert any("Malformed YAML" in err for err in res.errors)
