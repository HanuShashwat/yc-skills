"""
Signal Resolver for OpenYC Skills.
Build-time module to generate static indices and similarity matrices.
"""

import json
import logging
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

from src.exporter.utils import parse_skill_file

logger = logging.getLogger(__name__)


class SignalResolver:
    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = Path(skills_dir)
        self._model = None
        self.index = self._build_index()

    @property
    def model(self):
        if self._model is None:
            # Lazy load to save memory and time if just generating static index without embeddings
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._model

    def _embed(self, text: str) -> List[float]:
        """Embed text using sentence-transformers."""
        return self.model.encode(text).tolist()

    def _cosine_sim(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def _build_index(self) -> Dict[str, Any]:
        """Build the in-memory index from the skills directory."""
        index = {"by_id": {}, "by_tag": {}, "by_category": {}, "embeddings": {}}

        if not self.skills_dir.exists():
            return index

        for path in self.skills_dir.rglob("*.md"):
            if path.parent.name == "_failed":
                continue

            try:
                frontmatter, body = parse_skill_file(str(path))
            except Exception as e:
                logger.warning("Failed to parse skill file %s: %s", path, e)
                continue

            skill_id = frontmatter.skill_id

            # populate by_id
            index["by_id"][skill_id] = {
                "path": str(path).replace(os.sep, "/"),
                "category": frontmatter.category,
                "tags": frontmatter.tags,
                "name": frontmatter.name,
            }

            # populate by_category
            cat = frontmatter.category
            if cat not in index["by_category"]:
                index["by_category"][cat] = []
            index["by_category"][cat].append(skill_id)

            # populate by_tag
            for tag in frontmatter.tags:
                if tag not in index["by_tag"]:
                    index["by_tag"][tag] = []
                index["by_tag"][tag].append(skill_id)

            # populate embeddings
            # Embed name + principle text
            # Extract principle from body
            principle = ""
            current = False
            for line in body.splitlines():
                if line.startswith("## Principle"):
                    current = True
                    continue
                elif line.startswith("## "):
                    current = False

                if current and line.strip():
                    principle += line + "\n"

            text_to_embed = f"{frontmatter.name}. {principle.strip()}"
            index["embeddings"][skill_id] = self._embed(text_to_embed)

        return index

    def resolve(self, query: str) -> Dict[str, Any]:
        """Resolve a query to matching skills."""
        query = query.strip()

        # Exact match
        if query.startswith("yc-"):
            if query in self.index["by_id"]:
                return {
                    "type": "exact",
                    "skill": query,
                    "path": self.index["by_id"][query]["path"],
                }
            return {"type": "exact", "skill": query, "path": None}

        # Category filter
        if query.startswith("/"):
            category = query[1:]
            return {
                "type": "category",
                "category": category,
                "skills": self.index["by_category"].get(category, []),
            }

        # Tag filter
        if query.startswith("%"):
            tags = [t.strip() for t in query[1:].split(",") if t.strip()]
            if not tags:
                return {"type": "tags", "tags": [], "skills": []}

            matched_skills = set(self.index["by_tag"].get(tags[0], []))
            for tag in tags[1:]:
                matched_skills.intersection_update(self.index["by_tag"].get(tag, []))

            return {"type": "tags", "tags": tags, "skills": list(matched_skills)}

        # Fuzzy embedding search
        query_emb = self._embed(query)
        results = []
        for skill_id, emb in self.index["embeddings"].items():
            sim = self._cosine_sim(query_emb, emb)
            results.append((sim, skill_id))

        results.sort(reverse=True)
        top_3 = results[:3]

        return {
            "type": "closest",
            "query": query,
            "skills": [s for _, s in top_3],
            "similarities": [sim for sim, _ in top_3],
        }


def generate_index(
    skills_dir: str = "skills", output_path: str = "skills-index.json"
) -> None:
    """Generate the static skills index JSON file."""
    resolver = SignalResolver(skills_dir)

    # We strip out embeddings to keep it lightweight
    output_index = {
        "by_id": resolver.index["by_id"],
        "by_category": resolver.index["by_category"],
        "by_tag": resolver.index["by_tag"],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_index, f, indent=2)
    logger.info("Generated %s", output_path)


def generate_similarity_matrix(
    skills_dir: str = "skills", output_path: str = "data/similarity_matrix.json"
) -> None:
    """Generate the static similarity matrix JSON file."""
    resolver = SignalResolver(skills_dir)

    skills = sorted(list(resolver.index["embeddings"].keys()))
    n = len(skills)

    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        emb_i = resolver.index["embeddings"][skills[i]]
        for j in range(n):
            if i == j:
                matrix[i][j] = 1.0
            elif i < j:
                emb_j = resolver.index["embeddings"][skills[j]]
                sim = resolver._cosine_sim(emb_i, emb_j)
                matrix[i][j] = round(sim, 4)
                matrix[j][i] = round(sim, 4)

    output = {
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "skills": skills,
        "matrix": matrix,
        "tag_index": resolver.index["by_tag"],
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, separators=(",", ":"))
    logger.info("Generated %s", output_path)
