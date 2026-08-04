# YC Skills Forge

> A static-file generator that converts Y Combinator knowledge into composable skill files for AI agents.

## Overview

**YC Skills Forge** is a static-file generator designed specifically for the AI era. It programmatically ingests content from Y Combinator's Library and YouTube channels, extracts actionable startup advice, clusters it into narrow principles, and emits highly structured, versioned skill files (Markdown + YAML) and agent spec files (JSON). 

The output is this very GitHub repository, which AI agents (like Claude Code, Cursor, Copilot, or local models) can consume directly.

**What makes this different?**
- **Zero-Cost & Serverless:** Consumers download static files directly from GitHub. There is no API to pay for, no runtime vector database to host, and no embedding models to download.
- **Exact Quote Fidelity:** Every attribution is strictly verbatim from source transcripts or articles. There is no paraphrasing in the attribution blocks.
- **Composable Skills:** Each skill covers a hyper-specific micro-topic and mathematically links to `related_skills` using pre-computed similarities.

## How It Works

The forge operates as a Batch ETL pipeline transitioning into a Static Site Generator, all stored entirely in Git.

**Core Loop (Manual Trigger):**
```
Discover -> Download -> Chunk -> Extract -> Cluster -> Synthesize -> Link -> Export -> Validate -> Commit -> Tag
```

**Architecture Pattern:** Batch ETL -> Static Site Generator -> Git Repository

## For AI Agent Consumers

Agent frameworks can consume skills in one of three standardized formats:
1. **MCP (Model Context Protocol)**
2. **OpenAI Function Schemas**
3. **Hermes Plain-Text Prompts**

**Brief Example of Loading a Skill:**
Agents can read the pre-computed `skills-index.json` or `data/similarity_matrix.json` to find relevant skills, then directly fetch the `.md` or spec files they need to contextually load the exact startup advice required for the user's task.

For complete consumption guidelines, please read [docs/CONSUMPTION.md](docs/CONSUMPTION.md).

## Quickstart (Contributors)

> **Warning:** A fresh clone has no `registry.db` history. Scope your first run (using `--topic` or explicit URLs) to avoid duplicating existing skills.

### Prerequisites
- **Python 3.11** (Strict requirement)
- **Git**
- **yt-dlp** (installed via pip)
- API keys for at least one LLM provider (DeepSeek, Kimi, GLM, or Gemini)

### Setup Steps
```bash
# Clone and enter repo
git clone https://github.com/HanuShashwat/yc-skills.git
cd yc-skills

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download embedding model (cached locally)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Initialize database
python -m src.cli init-db

# Copy and fill in API keys
cp .env.example .env
```

### First Pipeline Run Example
```bash
# 1. Ingest
python -m src.cli ingest-youtube --url "https://www.youtube.com/watch?v=..."
# 2. Chunk
python -m src.cli chunk --all
# 3. Forge
python -m src.cli forge --topic "pricing" --batch-size 15
# 4. Link & Export & Validate
python -m src.cli link --topic "pricing"
python -m src.cli export --all
python -m src.cli validate --all
# 5. Index
python -m src.cli index
```

## CLI Command Reference

All CLI commands are executed via `python -m src.cli <command>`.

| Command | Description | Example Usage |
|---------|-------------|---------------|
| `init-db` | Initialize SQLite database (`data/registry.db`). | `python -m src.cli init-db` |
| `ingest-library` | Ingest a YC Library essay. | `python -m src.cli ingest-library --url <url>` |
| `ingest-youtube` | Ingest a YouTube video transcript. | `python -m src.cli ingest-youtube --url <url>` |
| `chunk` | Chunk all downloaded content into chunks. | `python -m src.cli chunk --all` |
| `forge` | Run the core forge pipeline (extract -> cluster -> synthesize). | `python -m src.cli forge --topic "hiring" --batch-size 15` |
| `link` | Run the deferred link pass to populate `related_skills`. | `python -m src.cli link --topic "hiring"` |
| `validate` | Validate skill files against the 3-layer validation suite. | `python -m src.cli validate --all` |
| `export` | Export specs in MCP, OpenAI, and Hermes formats. | `python -m src.cli export --all` |
| `index` | Generate similarity matrix and `skills-index.json`. | `python -m src.cli index` |
| `reaper` | Reset stale extracting items caught in failed runs. | `python -m src.cli reaper` |
| `quota` | Display provider quota usage and remaining capacity. | `python -m src.cli quota` |
| `backfill` | Historical bulk content ingestion from a start date. | `python -m src.cli backfill --start-date 2020-01-01` |

## Project Structure

```
yc-skills-forge/
├── .github/workflows/validate.yml   # PR validation ONLY — never generation
├── config/                          # YAML Configuration (providers, taxonomy, pipeline)
├── data/                            # Local maintainer state (DB, raw files, chunks)
├── docs/                            # Extensive project documentation
├── skills/                          # GENERATED: Markdown skill files organized by category
├── specs/                           # GENERATED: Output specs (mcp, openai, hermes)
├── src/                             # Core Python application logic
└── tests/                           # Unit and integration tests
```

## Skill File Format

All skill files are generated in Markdown with structured YAML frontmatter.

**Example:**
```yaml
---
skill_id: yc-fundraising-seed-round-timing
version: 1.0.0
category: fundraising
tags: ["seed", "timing", "traction"]
source_count: 3
quote_count: 5
confidence: 0.92
related_skills:
  - id: yc-fundraising-investor-updates
    similarity: 0.88
---
# Seed Round Timing

## The Principle
Raise money when you can convince investors, not when you need it...
```

## Contributing

- **For AI Agents:** Please read and strictly adhere to [AGENTS.md](AGENTS.md).
- **For Human Contributors:** Feel free to open issues or PRs. Note that all PRs are subject to our strict `.github/workflows/validate.yml` pipeline which runs schema validation, quote verification, and hallucination checks.
- If you're looking to run this yourself, see [BYOK.md](docs/BYOK.md).

## License

- **Code:** [MIT License](LICENSE)
- **Generated Skill Content:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

> **Legal Review Note:** YC Library essays and YouTube transcripts are publicly available. YC Skills Forge extracts short, attributed snippets (fair use) and synthesizes the underlying principles. No full essays or transcripts are reproduced in the generated skills. By using the BYOK model, contributors act as the operator. 

## Important Links

- [Consumption Guide](docs/CONSUMPTION.md)
- [Bring Your Own Keys (BYOK)](docs/BYOK.md)
- [Taxonomy Map](docs/TAXONOMY.md)
- [AGENTS.md (Operating Manual for AI)](AGENTS.md)
