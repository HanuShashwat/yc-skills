"""
Skill Synthesis Stage (Stage 3).
"""
import logging
import os
import re
import sqlite3
from datetime import datetime, timezone

import yaml
from jinja2 import Environment, FileSystemLoader

from src.config import load_config
from src.forge.llm_client import LLMClient
from src.models import SynthesisResponse

logger = logging.getLogger(__name__)

FALLBACK_BEHAVIOR = """## Fallback Behavior

If this skill does not match the user's query exactly, the agent MUST:
1. Return the 3 closest skills (by category proximity and tag overlap)
2. Provide advice based on the agent's general knowledge, NOT by inventing YC-specific quotes or attributing advice to YC speakers
3. Clearly state: "No specific YC skill exists for this exact question. Here is general advice, and related YC skills for context:"
"""

def get_category_for_topic(topic: str) -> str:
    """Determine the top-level category for a given topic/subcategory."""
    config = load_config()
    for cat_name, cat_data in config.taxonomy.taxonomy.items():
        if topic == cat_name or topic in cat_data.subcategories:
            return cat_name
    return "general"

def slugify(text: str) -> str:
    """Convert text to a safe slug."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def ensure_unique_skill_id(base_id: str, db_path: str) -> str:
    """Ensure skill_id is unique by appending _v2, _v3 etc."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            current_id = base_id
            version = 1
            while True:
                cursor.execute("SELECT 1 FROM skills WHERE skill_id = ?", (current_id,))
                if not cursor.fetchone():
                    return current_id
                version += 1
                current_id = f"{base_id}_v{version}"
    except sqlite3.Error as e:
        logger.error("DB error checking skill_id uniqueness: %s", e)
        raise

def run_synthesis(cluster_id: str, db_path: str = "data/registry.db") -> None:
    """Run synthesis for a given cluster."""
    
    # 1. Load cluster items
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM clusters WHERE cluster_id = ?", (cluster_id,))
            cluster_row = cursor.fetchone()
            if not cluster_row:
                logger.warning("Cluster %s not found.", cluster_id)
                return
                
            cluster = dict(cluster_row)
            batch_id = cluster["batch_id"]
            
            cursor.execute("""
                SELECT e.quote, e.speaker, e.designation, e.source_url, 
                       ch.timestamp_start as timestamp, e.is_framework, e.is_warning
                FROM cluster_items ci
                JOIN extracted_items e ON ci.item_id = e.item_id
                JOIN chunks ch ON e.chunk_id = ch.chunk_id
                WHERE ci.cluster_id = ?
            """, (cluster_id,))
            items = []
            for row in cursor.fetchall():
                d = dict(row)
                if d["is_framework"]:
                    d["type"] = "framework"
                elif d["is_warning"]:
                    d["type"] = "warning"
                else:
                    d["type"] = "advice"
                items.append(d)
            
            # Fetch provenance sources
            cursor.execute("""
                SELECT c.content_id, c.title, c.speaker, c.designation, c.url, 
                       COUNT(e.item_id) as num_quotes
                FROM cluster_items ci
                JOIN extracted_items e ON ci.item_id = e.item_id
                JOIN chunks ch ON e.chunk_id = ch.chunk_id
                JOIN content c ON ch.content_id = c.content_id
                WHERE ci.cluster_id = ?
                GROUP BY c.content_id, c.title, c.speaker, c.designation, c.url
            """, (cluster_id,))
            source_rows = [dict(row) for row in cursor.fetchall()]
            
    except sqlite3.Error as e:
        logger.error("Database error loading cluster %s: %s", cluster_id, e)
        raise
        
    if not items:
        logger.warning("No extracted items found for cluster %s.", cluster_id)
        return

    # 2. Determine category
    topic = cluster["topic"]
    category = get_category_for_topic(topic)
    
    llm = LLMClient(db_path)
    
    # 3. Generate descriptor
    desc_prompt = (
        f"Suggest a 3-5 word descriptor for a startup advice skill about {topic}. "
        f"Summary: {cluster['summary']}. "
        f"Return ONLY the words, separated by hyphens (e.g. seed-round-timing)."
    )
    descriptor_raw = llm.call(
        desc_prompt, 
        call_type="synthesize", 
        temperature=0.3, 
        response_format_json=False, 
        batch_id=batch_id
    )
    
    # Ensure it's a valid string since call() returns Union[str, Dict]
    if isinstance(descriptor_raw, dict):
        # Fallback if LLM inexplicably returned dict
        descriptor_raw = list(descriptor_raw.values())[0] if descriptor_raw else "skill"
        
    descriptor = slugify(str(descriptor_raw))
    descriptor = "-".join(descriptor.split("-")[:6])
    
    # 4. Ensure skill_id uniqueness
    base_skill_id = f"yc-{category}-{descriptor}"
    skill_id = ensure_unique_skill_id(base_skill_id, db_path)
    
    # 5. Render prompt and call LLM
    env = FileSystemLoader("src/forge/prompts")
    jinja_env = Environment(loader=env)
    template = jinja_env.get_template("synthesize.j2")
    
    prompt = template.render(
        topic=topic,
        category=category,
        descriptor=descriptor,
        items=items,
        avg_similarity=cluster["avg_similarity"]
    )
    
    response_json = llm.call(
        prompt, 
        call_type="synthesize", 
        temperature=0.3, 
        response_format_json=True, 
        batch_id=batch_id
    )
    
    # Ensure it is a dict
    if not isinstance(response_json, dict):
        raise RuntimeError("LLM failed to return a JSON dictionary for synthesis.")
        
    # 6. Parse JSON response
    parsed = SynthesisResponse(**response_json)
    
    # Force skill_id to our uniquely verified one
    parsed.skill_id = skill_id
    
    # 7. Overwrite confidence with computed value
    # Ensure we never use LLM self-reported confidence.
    # Contradictions are not stored in DB, we treat them as False for now.
    contradictions = False
    avg_sim = cluster["avg_similarity"] or 0.0
    item_count = cluster["item_count"]
    
    is_escape_hatch = "HUMAN_REVIEW: TRUE" in cluster["summary"]
    
    if is_escape_hatch:
        computed_confidence = 0.55
    else:
        computed_confidence = min(0.99, max(0.55, 
            (avg_sim * 0.5) + 
            (min(item_count, 10) / 10.0 * 0.3) + 
            (0.2 if not contradictions else 0.1)
        ))
    
    # Ensure related_skills is ALWAYS empty
    parsed.related_skills = []
    
    # 8. Write Markdown file
    cat_dir = os.path.join("skills", category)
    os.makedirs(cat_dir, exist_ok=True)
    filepath = os.path.join(cat_dir, f"{skill_id}.md")
    
    sources = []
    for r in source_rows:
        sources.append({
            "content_id": r["content_id"],
            "title": r["title"],
            "speaker": r["speaker"],
            "designation": r["designation"],
            "url": r["url"],
            "contribution": f"{r['num_quotes']} quotes"
        })
        
    frontmatter = {
        "skill_id": skill_id,
        "name": parsed.name,
        "version": "1.0.0",
        "category": category,
        "tags": [slugify(topic), slugify(category)],
        "source_count": len(source_rows),
        "quote_count": len(items),
        "related_skills": [],
        "confidence": round(computed_confidence, 2),
        "provenance": {
            "batch_id": batch_id,
            "pipeline_run_date": datetime.now(timezone.utc).isoformat(),
            "github_run_url": None,
            "sources": sources
        },
        "validation": {
            "quote_verified": False,
            "schema_valid": False,
            "hallucination_check": False,
            "human_review": "HUMAN_REVIEW: TRUE" in cluster["summary"]
        }
    }
    
    md_lines = []
    md_lines.append("---")
    md_lines.append(yaml.dump(frontmatter, sort_keys=False, default_flow_style=False).strip())
    md_lines.append("---")
    md_lines.append("")
    md_lines.append(f"# {parsed.name}")
    md_lines.append("")
    md_lines.append("## Principle")
    md_lines.append("")
    md_lines.append(parsed.principle)
    md_lines.append("")
    
    md_lines.append("## Verbatim Quotes")
    md_lines.append("")
    for q in parsed.quotes:
        md_lines.append(f"> \"{q.get('text', '')}\"")
        speaker_line = f"> \u2014 **{q.get('speaker', '')}**"
        if q.get('designation'):
            speaker_line += f", {q['designation']}"
        md_lines.append(speaker_line)
        
        source_line = f"> Source: [{q.get('source_url', 'source')}]({q.get('source_url', '')})"
        if q.get('timestamp'):
            source_line += f" at {q['timestamp']}"
        md_lines.append(source_line)
        md_lines.append("")
        
    md_lines.append("## Personalized Application")
    md_lines.append("")
    
    if "when_to_use" in parsed.application:
        md_lines.append("### When to Use This Skill")
        md_lines.append("")
        md_lines.append(str(parsed.application["when_to_use"]))
        md_lines.append("")
        
    if "actions" in parsed.application:
        md_lines.append("### Agent Protocol")
        md_lines.append("")
        for action in parsed.application["actions"]:
            md_lines.append(f"1. {action}")
        md_lines.append("")
        
    if "follow_up_questions" in parsed.application:
        md_lines.append("### Follow-Up Questions")
        md_lines.append("")
        for fq in parsed.application["follow_up_questions"]:
            md_lines.append(f"- \"{fq}\"")
        md_lines.append("")
        
    md_lines.append("## Edge Cases")
    md_lines.append("")
    for ec in parsed.edge_cases:
        md_lines.append(f"- {ec}")
    md_lines.append("")
    
    md_lines.append("## Related Skills")
    md_lines.append("")
    # Empty for now, populated by linker
    md_lines.append("")
    
    md_lines.append(FALLBACK_BEHAVIOR)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
        
    # 9. Insert into skills table
    now_iso = datetime.now(timezone.utc).isoformat()
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO skills (
                    skill_id, category, name, version, file_path, source_count, quote_count,
                    related_skills, computed_confidence, state, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                skill_id, category, parsed.name, "1.0.0", filepath, len(source_rows), len(items),
                None, round(computed_confidence, 2), "draft", now_iso, now_iso
            ))
    except sqlite3.Error as e:
        logger.error("Failed to insert skill %s into db: %s", skill_id, e)
        raise
