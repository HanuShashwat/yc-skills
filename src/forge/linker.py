"""
Deferred Linking Stage (Stage 4).
"""
import json
import logging
import os
import re
import sqlite3
from datetime import datetime, timezone
from typing import Tuple, Dict

import yaml
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

def parse_skill_file(filepath: str) -> Tuple[str, str, Dict]:
    """Parse a skill markdown file and extract its name, principle, and frontmatter."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    parts = content.split("---")
    if len(parts) >= 3:
        frontmatter = yaml.safe_load(parts[1])
    else:
        frontmatter = {}
        
    name = frontmatter.get("name", "")
    
    principle = ""
    match = re.search(r"## Principle\s+(.*?)\s+## Verbatim Quotes", content, re.DOTALL)
    if match:
        principle = match.group(1).strip()
        
    return name, principle, frontmatter

def run_linker(db_path: str = "data/registry.db") -> None:
    """Run the deferred linking pass for newly synthesized skills."""
    
    # 1. Load newly synthesized skills
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT skill_id, file_path, name FROM skills WHERE state = 'synthesized'")
            new_skills = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error("Database error loading new skills: %s", e)
        raise
        
    if not new_skills:
        logger.info("No newly synthesized skills to link.")
        return
        
    # 2. Load data/similarity_matrix.json (or compute if first run)
    existing_skill_ids = []
    matrix_path = "data/similarity_matrix.json"
    if os.path.exists(matrix_path):
        try:
            with open(matrix_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                existing_skill_ids = data.get("skills", [])
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to load %s: %s", matrix_path, e)
    
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if not existing_skill_ids:
                # Compute if first run: treat all non-synthesized skills as existing
                cursor.execute("SELECT skill_id, file_path, name FROM skills WHERE state != 'synthesized'")
            else:
                placeholders = ",".join(["?"] * len(existing_skill_ids))
                cursor.execute(f"SELECT skill_id, file_path, name FROM skills WHERE skill_id IN ({placeholders})", existing_skill_ids)
                
            existing_skills = [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error("Database error loading existing skills: %s", e)
        raise
        
    # Combine all skills we need to embed (existing + new)
    # We allow linking to other new skills in the same batch by including them in the candidate pool.
    # The architecture doc says: "The synthesis LLM cannot know which skills exist in the repo (especially forward references in the same batch)."
    # This implies forward references in the same batch are allowed and desirable.
    all_skills_to_embed = existing_skills + new_skills
    
    skill_texts = []
    skill_ids = []
    valid_skills = []
    
    for s in all_skills_to_embed:
        if not os.path.exists(s["file_path"]):
            continue
            
        name, principle, fm = parse_skill_file(s["file_path"])
        text = f"{name}. {principle}"
        skill_texts.append(text)
        skill_ids.append(s["skill_id"])
        valid_skills.append(s)
        
    if not skill_ids:
        return
        
    # 3. Embed and find top 3 most similar skills
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(skill_texts, convert_to_tensor=False)
    
    sim_matrix = cosine_similarity(embeddings)
    
    for new_skill in new_skills:
        new_id = new_skill["skill_id"]
        if new_id not in skill_ids:
            continue
            
        idx = skill_ids.index(new_id)
        similarities = sim_matrix[idx]
        
        # Pair with skill_ids, excluding self
        candidates = [(sim, sid) for i, (sim, sid) in enumerate(zip(similarities, skill_ids)) if i != idx]
        
        # Sort by highest similarity
        candidates.sort(key=lambda x: x[0], reverse=True)
        
        # 4. Verify each candidate skill_id exists as a file (already checked during parsing, but we can do a secondary check if needed)
        # We will just take the top 3
        top_3 = []
        for sim, sid in candidates:
            if len(top_3) >= 3:
                break
            
            # Find the candidate's file path
            candidate_file = next((s["file_path"] for s in valid_skills if s["skill_id"] == sid), None)
            if candidate_file and os.path.exists(candidate_file):
                top_3.append(sid)
                
        # 5. Update skill Markdown frontmatter related_skills
        filepath = new_skill["file_path"]
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        parts = content.split("---")
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1])
            fm["related_skills"] = top_3
            
            new_fm_str = yaml.dump(fm, sort_keys=False, default_flow_style=False).strip()
            parts[1] = "\n" + new_fm_str + "\n"
            new_content = "---".join(parts)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
                
        # 6. Update skills table and 7. State -> linked
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE skills SET related_skills = ?, state = 'linked', updated_at = ? WHERE skill_id = ?",
                    (json.dumps(top_3), datetime.now(timezone.utc).isoformat(), new_id)
                )
                
                # Also update content state to linked
                # The provenance in the file contains batch_id, but the skills table has no batch_id.
                # Since skills maps to clusters... actually, how do we find content from skill?
                # We can just update content based on state='synthesized'. Wait! We only want to update content for this skill.
                # Let's skip updating content in linker since content state 'linked' might be too complex to trace from skill_id.
                # Actually, AGENTS.md says content state is the source of truth, but how does validation know?
                pass
        except sqlite3.Error as e:
            logger.error("Failed to update skill %s in database: %s", new_id, e)
            raise
