# OpenOpenYC Skills

> **A static-file generator that converts Y Combinator startup advice into composable skill files that AI agents can use directly.**

---

## Table of Contents

1. [What Is This Project?](#what-is-this-project)
2. [Key Concepts Explained](#key-concepts-explained)
3. [Who Is This For?](#who-is-this-for)
4. [How It Works — The Big Picture](#how-it-works--the-big-picture)
5. [The Pipeline — Step by Step](#the-pipeline--step-by-step)
6. [For AI Agent Consumers (Using the Skills)](#for-ai-agent-consumers-using-the-skills)
7. [Quickstart for Contributors](#quickstart-for-contributors)
8. [CLI Command Reference](#cli-command-reference)
9. [Project Structure Explained](#project-structure-explained)
10. [Understanding Skill Files](#understanding-skill-files)
11. [Understanding Spec Files](#understanding-spec-files)
12. [The Taxonomy (How Skills Are Organized)](#the-taxonomy-how-skills-are-organized)
13. [How the LLM Provider System Works](#how-the-llm-provider-system-works)
14. [How Validation Works](#how-validation-works)
15. [The State Machine](#the-state-machine)
16. [Configuration Files Explained](#configuration-files-explained)
17. [What Gets Committed vs. What Stays Local](#what-gets-committed-vs-what-stays-local)
18. [Contributing](#contributing)
19. [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)
20. [License & Legal](#license--legal)
21. [Important Links](#important-links)

---

## What Is This Project?

**OpenOpenYC Skills** takes the publicly available startup advice from [Y Combinator](https://www.ycombinator.com/) — their blog posts (called "Library essays") and YouTube videos — and turns that advice into structured, machine-readable files that AI agents (like ChatGPT, Claude, Cursor, Copilot, or local models running on your laptop) can use.

### A Simple Analogy

Think of it like this:

1. **YC publishes a video** where Paul Graham says: *"The best time to raise money is when you don't need it."*
2. **OpenOpenYC Skills downloads that video's transcript**, extracts that quote and its context, groups it with similar advice from other YC videos/essays, and then creates a **structured "skill file"** — a Markdown document with YAML metadata.
3. **An AI agent** (like Claude Code or a GPT) can load that skill file and use it to give founders accurate, well-attributed advice about fundraising timing.

### What Makes This Different From a Regular Blog Post?

| Feature | Regular Blog Post | OpenOpenYC Skills Skill |
|---------|------------------|-----------------------|
| Format | Free-form prose for humans | Structured Markdown + YAML for both humans AND machines |
| Attribution | "YC says..." (vague) | Exact verbatim quotes with speaker name, title, source URL, and timestamp |
| Usability by AI | AI has to search the internet | AI loads a static file directly — no internet needed |
| Relationships | None | Each skill links to 3 related skills via math (cosine similarity) |
| Cost to Use | Free | Free — zero API keys, zero databases, zero hosting costs |
| Verification | Trust the author | Every quote is verified against source transcripts using fuzzy matching |

### The Three Core Promises

1. **Zero Cost for Consumers:** You download static files from GitHub. No API keys needed. No database to run. No embedding models to install.
2. **Exact Quote Fidelity:** Every quote attributed to a YC speaker is *verbatim* from the original transcript or essay. No paraphrasing. Ever. This is enforced by automated validation.
3. **Composable Skills:** Each skill covers one narrow micro-topic (e.g., "seed round timing") and mathematically links to related skills, so an AI agent can chain them together.

---

## Key Concepts Explained

If you're new to this project, here are the important terms you'll encounter:

| Term | What It Means |
|------|---------------|
| **Skill file** | A Markdown document (`.md`) with YAML frontmatter at the top. It contains one specific piece of startup advice, the verbatim quotes backing it up, and instructions for how an AI agent should apply it. Lives in `skills/{category}/`. |
| **Spec file** | A JSON or TXT file that wraps a skill in a format a specific AI framework understands. There are 3 formats: MCP (for Claude), OpenAI (for GPT), Hermes (for local models like Ollama). Lives in `specs/`. |
| **Frontmatter** | The metadata block at the top of a Markdown file, wrapped in `---`. It contains fields like `skill_id`, `category`, `tags`, `confidence`, etc. |
| **Taxonomy** | The fixed organizational tree of 8 categories (fundraising, hiring, product, growth, culture, strategy, founder-mental-models, technical) and their subcategories. Defined in `config/taxonomy.yml`. |
| **Pipeline** | The automated sequence of steps that transforms raw YC content into validated skill files. |
| **Forge** | The core part of the pipeline that does the heavy lifting: extracting advice, clustering similar items, and synthesizing skill files. |
| **Chunk** | A segment of text (200–800 words) created by splitting a long essay or transcript into manageable pieces for the LLM to process. |
| **LLM** | Large Language Model — the AI model (like DeepSeek, Gemini, etc.) that reads chunks and extracts advice from them. |
| **BYOK** | "Bring Your Own Keys" — contributors supply their own LLM API keys to run the pipeline. |
| **`skills-index.json`** | A machine-readable JSON file in the repo root that maps every skill's ID, tags, and category to its file path. AI agents use this to find skills. |
| **`similarity_matrix.json`** | A pre-computed matrix of how similar every skill is to every other skill. Used to populate the `related_skills` field. Lives in `data/`. |
| **`registry.db`** | A local SQLite database that tracks what content has been ingested, chunked, extracted, etc. It is **not** uploaded to GitHub — it stays on the contributor's machine. |

---

## Who Is This For?

This project serves **three distinct audiences**:

### 1. AI Agent Developers (Consumers)
You want to give your AI agent startup advice capabilities. You download skill files and/or spec files from this GitHub repo and load them into your agent. You never run any Python code from this repo.

→ **Start here:** [Consumption Guide](docs/CONSUMPTION.md)

### 2. Contributors (Generators)
You want to add new YC content to the project — ingesting new videos or essays, generating new skills, and submitting pull requests. You need your own LLM API keys.

→ **Start here:** [BYOK Guide](docs/BYOK.md)

### 3. AI Coding Agents (like Claude Code, Cursor, Copilot)
You are an AI agent working on this codebase. You should follow the strict rules in `AGENTS.md`.

→ **Start here:** [AGENTS.md](AGENTS.md)

---

## How It Works — The Big Picture

The project follows a **Batch ETL → Static Site Generator → Git Repository** pattern. Here's what that means in plain English:

1. **Batch ETL (Extract-Transform-Load):** We download YC content in batches, transform it through several processing stages (chunking, extracting advice, clustering, synthesizing), and load the results into skill files.
2. **Static Site Generator:** The output is a set of static files (Markdown, JSON, TXT) — no running server, no database, no API.
3. **Git Repository:** Everything is version-controlled. Consumers just clone or download from GitHub.

### The Core Pipeline (Visual Overview)

```
┌──────────┐    ┌──────────┐    ┌─────────┐    ┌──────────┐    ┌──────────┐
│ DISCOVER │───→│ DOWNLOAD │───→│  CHUNK  │───→│ EXTRACT  │───→│ CLUSTER  │
│          │    │          │    │         │    │ (LLM #1) │    │ (Local)  │
└──────────┘    └──────────┘    └─────────┘    └──────────┘    └──────────┘
                                                                     │
     ┌──────────┐    ┌──────────┐    ┌─────────┐    ┌──────────┐     │
     │  COMMIT  │←───│ VALIDATE │←───│ EXPORT  │←───│   LINK   │←────┘
     │  & TAG   │    │          │    │         │    │ (Local)  │
     └──────────┘    └──────────┘    └─────────┘    └──────────┘
                                                         │
                                                    ┌──────────┐
                                                    │SYNTHESIZE│
                                                    │ (LLM #2) │
                                                    └──────────┘
```

**Important:** This pipeline is **manually triggered** by a human maintainer running CLI commands on their local machine. There are no automated scheduled runs.

---

## The Pipeline — Step by Step

Here is exactly what happens at each stage, explained so a beginner can follow along:

### Stage 0: Discover & Download (Ingestion)

**What happens:** You tell the system about a YC essay URL or YouTube video URL. It downloads the content and saves it locally.

**For Library essays:**
- Downloads the HTML page using the `requests` library
- Strips out navigation, footer, scripts, ads, etc.
- Converts the cleaned HTML to Markdown using `markdownify`
- Saves the Markdown file to `data/raw/library/`
- Tries to identify the speaker/author (e.g., "Paul Graham, Founder of YC") using a built-in lookup table (`src/ingest/known_authors.py`)

**For YouTube videos:**
- Uses `yt-dlp` (a popular video tool) to download *only* the English subtitles/captions — **it does NOT download the video itself**
- Saves the transcript as a text file and metadata as JSON to `data/raw/youtube/`
- Tries to identify the speaker from the video description using regex patterns

**Content ID generation:**
- Library essays: `lib_` + first 12 characters of the SHA256 hash of the URL. Example: `lib_a1b2c3d4e5f6`
- YouTube videos: `yt_` + the 11-character YouTube video ID. Example: `yt_abc123def45`

**CLI command:**
```bash
python -m src.cli ingest-library --url "https://www.ycombinator.com/library/some-essay"
python -m src.cli ingest-youtube --url "https://www.youtube.com/watch?v=abc123def45"
```

### Stage 1: Chunking

**What happens:** Long essays and transcripts are split into smaller pieces called "chunks" (200–800 words each). This is necessary because LLMs have input size limits and work better with focused content.

**For essays:**
- Split by `## ` headers (Markdown level-2 headers)
- If a section is too short (< 200 words), merge it with the next section
- If a section is too long (> 800 words), split it by paragraphs into 400–600 word pieces
- Add one sentence of overlap between chunks for context continuity

**For transcripts:**
- Group consecutive segments from the same speaker
- Merge until 400–800 words
- If a single speaker talks for more than 800 words, split at the nearest sentence boundary after 600 words
- Preserve timestamps (HH:MM:SS)

**Output:** JSON chunk files saved to `data/chunks/library/` or `data/chunks/youtube/`, and rows inserted into the `chunks` table of `registry.db`.

**CLI command:**
```bash
python -m src.cli chunk --all
```

### Stage 2: Extraction (LLM Call #1)

**What happens:** An LLM reads a batch of chunks (5–20 items) and extracts every piece of actionable advice, including the exact verbatim quotes, speaker names, and topic classifications.

**How it works:**
1. The **Batcher** selects 5–20 content items with state `chunked`, optionally filtered by `--topic`
2. All chunks from those items are combined into a single prompt using a Jinja2 template (`src/forge/prompts/extract.j2`)
3. The LLM is called once for the whole batch
4. The response is a JSON object containing extracted items, each with:
   - The exact verbatim quote
   - Speaker name and designation
   - Source URL and timestamp
   - Topic classification (from the taxonomy)
   - Type: `framework`, `warning`, `advice`, or `story`
5. If sources contradict each other, the LLM notes the contradiction

**CLI command:**
```bash
python -m src.cli forge --topic "fundraising" --batch-size 15
# (This runs extraction, clustering, AND synthesis in sequence)
```

### Stage 3: Clustering (Local, No LLM)

**What happens:** The extracted advice items are grouped into clusters of similar items. This is done entirely on your local machine using embeddings — no LLM call needed.

**How it works:**
1. Each extracted quote is converted to a 384-dimensional vector using the `all-MiniLM-L6-v2` embedding model (from `sentence-transformers`)
2. Agglomerative clustering groups items where cosine similarity ≥ 0.82 (distance threshold 0.18)
3. Clusters with fewer than 2 items are rejected (not enough consensus) — those items go back to the pool for future batches
4. Each cluster gets an `avg_similarity` score (average pairwise cosine similarity of all items in the cluster)

**Why cluster?** Multiple YC speakers often say similar things about the same topic. Clustering ensures we synthesize a unified skill from multiple corroborating sources, not just one person's opinion.

### Stage 4: Synthesis (LLM Call #2)

**What happens:** For each cluster, an LLM generates a structured skill file in Markdown + YAML format.

**How it works:**
1. All extracted quotes in the cluster are sent to the LLM with a synthesis prompt (`src/forge/prompts/synthesize.j2`)
2. The LLM writes:
   - A unified principle (2–4 sentences)
   - Selects the 2–3 strongest verbatim quotes to preserve
   - Application instructions for AI agents
   - Edge cases and exceptions
3. **The pipeline overrides two things the LLM produces:**
   - **`confidence`** is NOT from the LLM — it's computed mathematically from cluster metrics (avg_similarity, item_count, contradiction presence)
   - **`related_skills`** is set to an empty array — it will be filled in the next step

**Confidence formula:**
```python
confidence = min(0.99, max(0.55,
    (avg_similarity * 0.5) +
    (min(item_count, 10) / 10 * 0.3) +
    (0.2 if not contradictions else 0.1)
))
```

### Stage 5: Linking (Local, No LLM)

**What happens:** After all skills in a batch are synthesized, a separate pass populates the `related_skills` field using the pre-computed similarity matrix.

**How it works:**
1. Load the `data/similarity_matrix.json` (or compute it if this is the first run)
2. For each new skill, find the top 3 most similar existing skills by cosine similarity
3. Only include a related skill if:
   - Its similarity is above the threshold (0.65, from `config/pipeline.yml`)
   - It actually exists as a file in `skills/`
4. Update the skill file's YAML frontmatter with the related skill IDs

**Why deferred?** The LLM can't know which other skills exist in the repository, especially ones created in the same batch. So we use math instead of guessing.

**CLI command:**
```bash
python -m src.cli link --topic "fundraising"
```

### Stage 6: Export

**What happens:** For each validated skill, three spec files are generated in different formats for different AI frameworks.

| Format | File Location | Who Uses It |
|--------|---------------|-------------|
| MCP (Model Context Protocol) | `specs/mcp/{skill_id}.json` | Claude Code, MCP-compatible agents |
| OpenAI Function Schema | `specs/openai/{skill_id}.json` | GPT, OpenAI API users |
| Hermes Plain-Text | `specs/hermes/{skill_id}.txt` | Local models (Ollama, llama.cpp) |

**CLI command:**
```bash
python -m src.cli export --all
```

### Stage 7: Validation

**What happens:** Every generated skill is checked against a three-layer validation suite before it can be published.

| Layer | What It Checks | Tool Used |
|-------|---------------|-----------|
| 1. Quote Verification | Is each quote actually present in the source transcript/essay? | `rapidfuzz` fuzzy string matching |
| 2. Schema Validation | Does the YAML frontmatter match the required format? | `pydantic` model validation |
| 3. Hallucination Guard | Did the LLM make up any facts, speakers, or quotes? | LLM-as-judge (Gemini at temperature 0.0) |

If validation fails, the skill is moved to `skills/_failed/` for manual review.

**CLI command:**
```bash
python -m src.cli validate --all
```

### Stage 8: Index Generation

**What happens:** After all skills are validated, two index files are regenerated:

1. **`skills-index.json`** (repo root) — A lookup table mapping skill IDs, tags, and categories to file paths
2. **`data/similarity_matrix.json`** — A matrix of cosine similarities between all skills

These files are committed to the repo so that consumers can use them without running any code.

**CLI command:**
```bash
python -m src.cli index
```

### Stage 9: Commit & Tag

**What happens:** The maintainer commits the generated files and opens a pull request.

```bash
git checkout -b forge/batch-$(date +%s)
git add skills/ specs/ data/similarity_matrix.json skills-index.json
git commit -m "forge: batch $(date +%Y-%m-%d) - fundraising"
git push origin HEAD
# Open PR on GitHub → GitHub Actions runs validation → merge if green
```

---

## For AI Agent Consumers (Using the Skills)

If you're building an AI agent and want to use OpenOpenYC Skills's startup advice, you **do not** need to install Python, run any pipelines, or have API keys.

### What You Do

1. **Clone or download this repository** (or just the files you need)
2. **Read `skills-index.json`** to find skills relevant to your use case
3. **Load the skill file** (from `skills/{category}/{skill_id}.md`) or **load the spec file** (from `specs/{format}/{skill_id}.json` or `.txt`) into your agent's context

### Finding Skills

You can search for skills using these patterns:

| Search Type | Pattern | Example | What It Does |
|------------|---------|---------|--------------|
| Exact ID | `yc-fundraising-seed-round-timing` | Direct lookup | Finds the exact skill file |
| Category filter | `/fundraising` | Lists all | Returns all skills in the fundraising category |
| Tag filter | `%seed,runway` | AND logic | Returns skills tagged with BOTH "seed" AND "runway" |
| Fuzzy search | `fundraising timing` | Similarity | Returns the 3 most similar skills using embeddings |

All of these can be resolved using `skills-index.json` (for exact, category, and tag lookups) and `data/similarity_matrix.json` (for fuzzy similarity search).

### For detailed instructions, see the [Consumption Guide](docs/CONSUMPTION.md).

---

## Quickstart for Contributors

> **⚠️ Cold-Start Warning:** A fresh clone has no `registry.db` — the local database that tracks what has already been processed. If you run `forge` without scoping `--topic` or specifying exact URLs, you may regenerate duplicate versions of skills that already exist. **Always scope your first run** to specific new content.

### Prerequisites

| Requirement | Why It's Needed | How to Get It |
|-------------|----------------|---------------|
| **Python 3.11** | The project requires exactly Python 3.11+ | Download from [python.org](https://www.python.org/downloads/) |
| **Git** | Version control | Download from [git-scm.com](https://git-scm.com/) |
| **yt-dlp** | Downloads YouTube transcripts | Installed via `pip install yt-dlp` (included in requirements.txt) |
| **At least 1 LLM API key** | Needed to extract advice and synthesize skills | Sign up at [DeepSeek](https://platform.deepseek.com/), [Gemini](https://ai.google.dev/), or others |

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/HanuShashwat/openyc-skills.git
cd openyc-skills

# 2. Create a Python virtual environment
#    (This isolates the project's dependencies from your system Python)
python3.11 -m venv .venv

# 3. Activate the virtual environment
#    On Linux/macOS:
source .venv/bin/activate
#    On Windows (Command Prompt):
.venv\Scripts\activate
#    On Windows (PowerShell):
.venv\Scripts\Activate.ps1

# 4. Install all Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Download the embedding model
#    (This downloads ~90MB to your local cache on first run. It's used for
#     clustering similar quotes — it runs on your CPU, no GPU needed.)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# 6. Initialize the SQLite database
#    (Creates data/registry.db with all the necessary tables)
python -m src.cli init-db

# 7. Set up your API keys
#    Copy the template and edit it with your real keys:
cp .env.example .env
#    Then open .env in your editor and replace the placeholder values.
```

### Your First Pipeline Run

```bash
# 1. Ingest a YouTube video
python -m src.cli ingest-youtube --url "https://www.youtube.com/watch?v=VIDEO_ID_HERE"

# 2. Chunk the downloaded content
python -m src.cli chunk --all

# 3. Run the forge (extraction + clustering + synthesis)
#    Always specify --topic to avoid generating duplicates!
python -m src.cli forge --topic "fundraising" --batch-size 15

# 4. Populate related_skills links
python -m src.cli link --topic "fundraising"

# 5. Export to MCP, OpenAI, and Hermes formats
python -m src.cli export --all

# 6. Validate all skills
python -m src.cli validate --all

# 7. Regenerate the index and similarity matrix
python -m src.cli index
```

### For the complete contributor guide, see [BYOK Guide](docs/BYOK.md).

---

## CLI Command Reference

All commands are run via `python -m src.cli <command>`. You can always run `python -m src.cli --help` to see available commands.

| Command | What It Does | Example |
|---------|-------------|---------|
| `init-db` | Creates the SQLite database (`data/registry.db`) with all necessary tables. Safe to run multiple times (idempotent). | `python -m src.cli init-db` |
| `ingest-library` | Downloads a YC Library essay, extracts the text, and registers it in the database. | `python -m src.cli ingest-library --url https://paulgraham.com/startupideas.html` |
| `ingest-youtube` | Downloads a YouTube video's transcript and metadata (NOT the video itself). | `python -m src.cli ingest-youtube --url https://youtube.com/watch?v=abc123` |
| `chunk` | Splits all downloaded content into sized chunks (200–800 words). | `python -m src.cli chunk --all` |
| `forge` | Runs the core pipeline: batch selection → LLM extraction → clustering → LLM synthesis. | `python -m src.cli forge --topic "hiring" --batch-size 15` |
| `link` | Populates the `related_skills` field in skill files using the similarity matrix. | `python -m src.cli link --topic "hiring"` |
| `validate` | Runs the 3-layer validation suite (quote verification, schema validation, hallucination guard). | `python -m src.cli validate --all` |
| `export` | Generates spec files in MCP, OpenAI, and Hermes formats. | `python -m src.cli export --all` |
| `index` | Regenerates `skills-index.json` and `data/similarity_matrix.json`. | `python -m src.cli index` |
| `reaper` | Resets items stuck in `extracting` state for over 2 hours (e.g., after a crash). | `python -m src.cli reaper` |
| `quota` | Shows how many API tokens/requests you've used today for each LLM provider. | `python -m src.cli quota` |
| `backfill` | Bulk ingests historical content from a given start date. | `python -m src.cli backfill --start-date 2020-01-01` |

---

## Project Structure Explained

Here's what every directory and key file in the project does:

```
openyc-skills/
│
├── .github/workflows/
│   └── validate.yml              # GitHub Actions: runs validation on PRs
│                                   (ONLY validates — never generates skills)
│
├── config/                        # All configuration files (YAML)
│   ├── taxonomy.yml               # The 8 categories and their subcategories
│   ├── providers.yml              # LLM provider settings (API endpoints, quotas)
│   └── pipeline.yml               # Chunking/clustering/validation parameters
│
├── data/                          # Local data (mostly GITIGNORED — see below)
│   ├── raw/library/               # Downloaded essay Markdown files (gitignored)
│   ├── raw/youtube/               # Downloaded transcripts + metadata (gitignored)
│   ├── chunks/library/            # Chunked essay JSON files (gitignored)
│   ├── chunks/youtube/            # Chunked transcript JSON files (gitignored)
│   ├── errors/                    # Failed LLM responses for debugging (gitignored)
│   ├── registry.db                # SQLite state machine database (gitignored)
│   └── similarity_matrix.json     # Pre-computed skill similarities (COMMITTED)
│
├── skills/                        # GENERATED skill files organized by category
│   ├── fundraising/               #   e.g., yc-fundraising-seed-round-timing.md
│   ├── hiring/
│   ├── product/
│   ├── growth/
│   ├── culture/
│   ├── strategy/
│   ├── founder-mental-models/
│   └── technical/
│
├── specs/                         # GENERATED spec files for AI agent frameworks
│   ├── mcp/                       # Model Context Protocol JSON specs
│   ├── openai/                    # OpenAI function schema JSON specs
│   └── hermes/                    # Plain-text specs for local models
│
├── src/                           # All Python source code
│   ├── cli.py                     # THE single entry point: python -m src.cli
│   ├── config.py                  # Loads and validates config YAML files
│   ├── models.py                  # Pydantic data models for all domain objects
│   ├── __main__.py                # Enables `python -m src.cli` to work
│   ├── ingest/                    # Downloads content from YC Library & YouTube
│   │   ├── library_scraper.py     # Scrapes essays from YC website
│   │   ├── youtube_downloader.py  # Downloads transcripts via yt-dlp
│   │   └── known_authors.py       # Hardcoded YC speaker lookup table
│   ├── chunker/                   # Splits content into sized chunks
│   │   ├── essay_chunker.py       # Splits essays by headers
│   │   └── transcript_chunker.py  # Splits transcripts by speaker
│   ├── forge/                     # The core pipeline (the "forge")
│   │   ├── batcher.py             # Selects batches of 5-20 items
│   │   ├── extractor.py           # LLM Call #1: extracts advice from chunks
│   │   ├── clusterer.py           # Groups similar advice using embeddings
│   │   ├── synthesizer.py         # LLM Call #2: creates skill files
│   │   ├── linker.py              # Populates related_skills from similarity matrix
│   │   ├── llm_client.py          # Unified LLM client with provider rotation
│   │   └── prompts/               # Jinja2 prompt templates
│   │       ├── extract.j2         # Prompt for advice extraction
│   │       └── synthesize.j2      # Prompt for skill synthesis
│   ├── exporter/                  # Generates spec files from skills
│   │   ├── mcp_exporter.py        # MCP format (Claude)
│   │   ├── openai_exporter.py     # OpenAI format (GPT)
│   │   └── hermes_exporter.py     # Hermes format (local models)
│   ├── validator/                 # Three-layer validation suite
│   │   ├── quote_verifier.py      # Fuzzy matching of quotes against sources
│   │   ├── schema_validator.py    # Pydantic schema validation
│   │   └── hallucination_guard.py # LLM-as-judge for fact-checking
│   └── retrieval/                 # Build-time-only index generation
│       └── resolver.py            # Generates skills-index.json + similarity_matrix
│
├── tests/                         # Unit and integration tests
│
├── scripts/                       # Helper shell scripts
│   ├── setup.sh                   # One-command local setup
│   └── backfill.sh                # Historical content ingestion
│
├── docs/                          # Documentation
│   ├── CONSUMPTION.md             # Guide for AI agent consumers
│   ├── BYOK.md                    # Guide for contributors
│   └── TAXONOMY.md                # The full category/subcategory tree
│
├── AGENTS.md                      # Rules for AI coding agents working on this code
├── requirements.txt               # Python dependencies (exact pinned versions)
├── pyproject.toml                 # Project metadata + tool configs (ruff, mypy, pytest)
├── .env.example                   # Template for API keys
├── .gitignore                     # Lists files not uploaded to GitHub
├── skills-index.json              # Machine-readable skill index (auto-generated, COMMITTED)
├── LICENSE                        # MIT License (code), CC BY-SA 4.0 (skill content)
└── README.md                      # This file
```

---

## Understanding Skill Files

Every skill is a Markdown file with YAML frontmatter. Here's a complete annotated example:

```yaml
---
# === IDENTITY ===
skill_id: yc-fundraising-seed-round-timing     # Unique ID: yc-{category}-{descriptor}
name: Seed Round Timing                         # Human-readable name (max 100 chars)
version: "1.0.0"                                # Semantic versioning

# === CLASSIFICATION ===
category: fundraising                           # Must be one of the 8 taxonomy categories
tags:                                           # 1-10 lowercase tags for filtering
  - seed
  - runway
  - leverage
  - investors
  - timing

# === METRICS ===
source_count: 12                                # How many source documents contributed
quote_count: 3                                  # Number of verbatim quotes included
confidence: 0.92                                # 0.0-1.0, computed from cluster metrics (NOT from LLM)

# === RELATIONSHIPS ===
related_skills:                                 # Top 3 most similar skills (by cosine similarity)
  - id: yc-fundraising-seed-round-valuation
    similarity: 0.88
  - id: yc-fundraising-investor-update-emails
    similarity: 0.76

# === PROVENANCE (Where did this come from?) ===
provenance:
  batch_id: "550e8400-e29b-41d4-a716-446655440000"
  pipeline_run_date: "2026-07-12T00:00:00Z"
  sources:
    - content_id: "lib_a1b2c3d4e5f6"
      title: "How to convince investors"
      speaker: "Paul Graham"
      designation: "Founder of YC"
      url: "https://paulgraham.com/convince.html"
      contribution: "3 quotes, 1 framework"

# === VALIDATION STATUS ===
validation:
  quote_verified: true                          # Passed fuzzy matching against source
  schema_valid: true                            # Passed Pydantic schema validation
  hallucination_check: true                     # Passed LLM-as-judge fact check
  human_review: false                           # Not flagged for human review
---

# Seed Round Timing

## Principle

The optimal time to raise a seed round is when you have 9-12 months of runway
remaining and can demonstrate measurable momentum.

## Verbatim Quotes

> "The best time to raise money is when you don't need it."
> — **Paul Graham**, Founder of YC
> Source: [How to convince investors](https://paulgraham.com/convince.html)

> "If you wait until you need money, you've already lost."
> — **Michael Seibel**, Partner at YC
> Source: [Office Hours: Fundraising](https://youtube.com/watch?v=abc123) at 00:04:32

## Personalized Application

### When to Use This Skill
Activate when a founder asks about fundraising timing, runway, or leverage.

### Agent Protocol
1. Ask: "What is your current monthly burn rate and cash in bank?"
2. Calculate runway: cash / burn
3. If < 6 months: Flag urgent. Suggest bridge round.
4. If 6-12 months: Start investor conversations now.
5. If > 12 months: Build relationships, don't pitch yet.

### Follow-Up Questions
- "How many months of runway do you currently have?"
- "What metrics can you show an investor today?"

## Edge Cases
- Pre-revenue AI startups may raise on technical milestones, not revenue.
- Profitable bootstrapped companies may not need seed at all.

## Fallback Behavior
If this skill doesn't match the user's query, return the 3 closest skills.
NEVER invent YC quotes. Use general knowledge with clear attribution.
```

### Skill ID Naming Convention

All skill IDs follow this pattern: `yc-{category}-{subcategory}-{descriptor}`

- All lowercase
- Words separated by hyphens
- Maximum 6 words after `yc-{category}`
- Must be unique across the entire repository

**Valid examples:**
- `yc-fundraising-seed-round-timing`
- `yc-hiring-first-technical-hire`
- `yc-product-mvp-no-code-approach`
- `yc-founder-mental-models-default-alive-dead`

**Invalid examples:**
- `yc-Fundraising-Seed` (uppercase not allowed)
- `fundraising-seed-round-timing` (missing `yc-` prefix)
- `yc-fundraising-how-to-perfectly-time-your-seed-round-fundraising-effort` (too many words)

---

## Understanding Spec Files

Spec files are auto-generated wrappers around skill files, formatted for specific AI frameworks. Here are the three formats:

### 1. MCP Format (for Claude Code)
- **File:** `specs/mcp/{skill_id}.json`
- **Contains:** `inputSchema` (parameters the agent should collect), `handler` (path to skill file), `tags`, `fallback` behavior
- **Used by:** Claude Code and other MCP-compatible frameworks

### 2. OpenAI Format (for GPT / Function Calling)
- **File:** `specs/openai/{skill_id}.json`
- **Contains:** OpenAI-compatible function definition with `parameters`, `metadata` (skill file path, category, fallback rules)
- **Used by:** GPT and OpenAI API integrations

### 3. Hermes Format (for Local Models)
- **File:** `specs/hermes/{skill_id}.txt`
- **Contains:** Plain text meant to be concatenated into a system prompt. No JSON parsing needed.
- **Used by:** Ollama, llama.cpp, and other local model environments

### For detailed spec file examples and integration code, see [Consumption Guide](docs/CONSUMPTION.md).

---

## The Taxonomy (How Skills Are Organized)

All skills are organized into exactly **8 categories**, each with subcategories:

| # | Category | Description | Subcategories |
|---|----------|-------------|---------------|
| 1 | `fundraising` | Raising capital from investors | seed-round, series-a, pitch-deck, investor-relations, valuation, term-sheets |
| 2 | `hiring` | Building the team | first-hires, technical-hiring, culture-fit, compensation, firing |
| 3 | `product` | Product development & management | mvp, product-market-fit, user-research, roadmap, design |
| 4 | `growth` | Acquiring and retaining users | marketing, sales, retention, pricing, distribution |
| 5 | `culture` | Company culture & operations | mission, values, remote-work, communication |
| 6 | `strategy` | High-level company decisions | pivoting, competition, market-sizing, monetization |
| 7 | `founder-mental-models` | Psychological & decision-making frameworks | motivation, burnout, decision-making, leadership |
| 8 | `technical` | Engineering & infrastructure | architecture, scaling, security, ai-ml |

The taxonomy is defined in `config/taxonomy.yml` and is intentionally locked to prevent sprawl. Adding a new category requires a pull request.

### For the complete taxonomy reference, see [Taxonomy Map](docs/TAXONOMY.md).

---

## How the LLM Provider System Works

The project supports **4 LLM providers** that it rotates through based on availability and remaining quota:

| Priority | Provider | Model | Daily Token Limit | Daily Request Limit |
|----------|----------|-------|-------------------|---------------------|
| 1 (first choice) | DeepSeek | `deepseek-chat` | 1,000,000 | 100 |
| 2 | Kimi (Moonshot) | `moonshot-v1-8k` | 500,000 | 50 |
| 3 | GLM (BigModel) | `glm-4-flash` | 500,000 | 50 |
| 4 | Gemini | `gemini-1.5-flash` | 1,500,000 | 150 |

**How rotation works:**
1. When an LLM call is needed, the system checks each provider's remaining daily quota (tokens and requests)
2. It picks the available provider with the highest priority (lowest number) that has enough remaining quota
3. If all providers are exhausted, it raises an error: *"All providers exhausted. Wait for UTC midnight reset."*
4. A 10% buffer is kept to avoid hitting exact limits

**Special rule for validation:** The hallucination guard (validation step 3) uses a **dedicated Gemini instance** at `temperature: 0.0` — it does NOT rotate through the general provider pool. If Gemini quota runs out, this check is skipped (fail-open behavior), and a warning is logged.

**Configuration:** Provider settings are in `config/providers.yml`. API keys come from environment variables defined in your `.env` file.

---

## How Validation Works

Every generated skill must pass **three independent checks** before it can be published:

### Layer 1: Quote Verification (`src/validator/quote_verifier.py`)

**Purpose:** Ensures every verbatim quote in a skill file actually appears in the source transcript or essay.

**How it works:**
- Extracts all blockquotes (`> "..."`) from the skill file
- For each quote, loads the source chunk from `data/chunks/`
- Computes two fuzzy match scores using `rapidfuzz`:
  - `ratio`: Strict, length-normalized comparison (catches rewording)
  - `partial_ratio`: Lenient, substring-friendly comparison (catches truncation)
- **PASS:** `ratio ≥ 70` AND `partial_ratio ≥ 85`
- **WARNING:** `ratio < 70` but `partial_ratio ≥ 85` (flagged for human review)
- **FAIL:** `partial_ratio < 70` (blocks publication)

### Layer 2: Schema Validation (`src/validator/schema_validator.py`)

**Purpose:** Ensures the YAML frontmatter has all required fields in the correct format.

**Checks:**
- Validates against the `SkillFrontmatter` Pydantic model
- `skill_id` matches the regex `^yc-[a-z]+(-[a-z]+){1,6}$`
- `version` matches `^\d+\.\d+\.\d+$`
- `confidence` is between 0.0 and 1.0
- `tags` has 1–10 items, all lowercase
- `source_count ≥ 1` and `quote_count ≥ 1`
- `skill_id` matches the filename
- All `related_skills` entries actually exist as files in `skills/`

### Layer 3: Hallucination Guard (`src/validator/hallucination_guard.py`)

**Purpose:** Catches cases where the LLM invented facts, speakers, or quotes.

**Checks (in order):**
1. Cross-references all speaker names in the skill against the `content` table
2. Verifies no speaker appears in a skill who isn't in the batch sources
3. Checks for years, dollar amounts, or company names not present in source chunks
4. **LLM-as-judge:** Sends the skill's principle and quotes to Gemini (`temperature: 0.0`) asking: *"Does the Principle introduce any concepts not supported by the verbatim quotes?"*
   - If Gemini says `{"supported": false}`, the skill fails
   - If Gemini quota is exhausted, this check is skipped with a warning (layers 1-3 still apply)

---

## The State Machine

Every piece of content in the database has a `state` field that tracks where it is in the pipeline. States always move forward (with two exceptions):

```
discovered → downloaded → chunked → extracting → extracted → clustered
                                                                  ↓
            failed ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← synthesized
              ↑                                                    ↓
              ← ← ← ← ← ← ← ← (any state on error)         linked
                                                                  ↓
                                                             validated
                                                                  ↓
                                                             published
```

**Special transitions:**
- `extracting → chunked`: The **reaper** command resets items stuck in `extracting` for over 2 hours (e.g., after a crash). Run `python -m src.cli reaper`.
- `any state → failed`: On unrecoverable errors. Items can be manually retried with `--retry-failed`.

---

## Configuration Files Explained

All tunable parameters live in YAML files under `config/`. **Nothing is hardcoded in Python.**

### `config/taxonomy.yml`
Defines the 8 categories and their subcategories. This is the authoritative source for skill organization.

### `config/providers.yml`
Defines the 4 LLM providers, their API endpoints, models, daily limits, and rotation strategy. API keys are read from environment variables using `${VAR_NAME}` syntax.

### `config/pipeline.yml`
Contains all the numeric parameters for the pipeline:
- **Chunking:** min/max word counts, overlap settings
- **Clustering:** embedding model, distance threshold, minimum cluster size
- **Extraction/Synthesis:** LLM temperature, max tokens
- **Linking:** max related skills, similarity threshold
- **Validation:** fuzzy match thresholds
- **Export:** which formats to generate

---

## What Gets Committed vs. What Stays Local

This is important because some files are generated locally but NOT uploaded to GitHub:

| Path | Committed to Git? | Why? |
|------|--------------------|------|
| `skills/` | ✅ Yes | These are the main output — what consumers use |
| `specs/` | ✅ Yes | Spec files for AI frameworks |
| `skills-index.json` | ✅ Yes | Machine-readable skill lookup |
| `data/similarity_matrix.json` | ✅ Yes | Pre-computed similarities for consumers |
| `src/` | ✅ Yes | Source code |
| `config/` | ✅ Yes | Configuration |
| `docs/` | ✅ Yes | Documentation |
| `data/raw/` | ❌ No (gitignored) | Raw downloaded content (copyright concerns) |
| `data/chunks/` | ❌ No (gitignored) | Intermediate processing files |
| `data/registry.db` | ❌ No (gitignored) | Local state machine (each contributor has their own) |
| `data/errors/` | ❌ No (gitignored) | Failed LLM responses for debugging |
| `.env` | ❌ No (gitignored) | Contains your secret API keys |

---

## Contributing

### For Human Contributors

1. Fork the repository
2. Follow the [BYOK Guide](docs/BYOK.md) to set up your local environment
3. Ingest new content and run the pipeline
4. Open a pull request — GitHub Actions will automatically run validation
5. A maintainer reviews and merges if all checks pass

### For AI Coding Agents

Read and strictly follow [AGENTS.md](AGENTS.md). It contains comprehensive rules about:
- Layer architecture and import restrictions
- Coding standards (Pydantic models, error handling, logging)
- Testing requirements
- What files you may and may not modify

---

## Frequently Asked Questions (FAQ)

### Q: Do I need API keys to USE the skills in my AI agent?
**No.** Consumers download static files from GitHub. No API keys, no database, no code execution needed.

### Q: Do I need API keys to GENERATE new skills?
**Yes.** You need at least one LLM provider API key (DeepSeek, Kimi, GLM, or Gemini). See [BYOK Guide](docs/BYOK.md).

### Q: Why is `registry.db` not committed to the repo?
Because each contributor has their own local pipeline state. The database tracks what YOU have ingested and processed. It's specific to your local machine. If you need history context, you could download a snapshot from GitHub Releases (when available).

### Q: What happens if the LLM makes up a fake quote?
The three-layer validation suite catches this:
1. Quote verification fuzzy-matches against the actual source transcript
2. Hallucination guard cross-references speakers and facts against source data
3. If either fails, the skill is moved to `skills/_failed/` and cannot be published

### Q: Can I add a new category like "legal" or "fundraising-strategy"?
Only via a pull request that modifies `config/taxonomy.yml`. The taxonomy is locked to prevent sprawl and overlap. See [Taxonomy Map](docs/TAXONOMY.md).

### Q: Why are there 4 LLM providers instead of just one?
To avoid rate limits and single points of failure. The system rotates through providers by priority, falling back to the next when one runs out of daily quota.

### Q: How is `confidence` calculated?
It's computed mathematically from cluster metrics — NOT from the LLM's self-assessment:
```python
confidence = min(0.99, max(0.55,
    (avg_similarity * 0.5) +           # How similar are the source quotes?
    (min(item_count, 10) / 10 * 0.3) + # How many sources back this up?
    (0.2 if no contradictions else 0.1) # Do sources agree or disagree?
))
```

### Q: What Python version do I need?
Python 3.11 or 3.12. Earlier versions are not supported.

### Q: How do I check my remaining API quota?
Run `python -m src.cli quota` to see tokens used and remaining for each provider today.

---

## License & Legal

- **Code:** [MIT License](LICENSE) — do whatever you want with the code.
- **Generated Skill Content:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) — attribution required, share alike.

> **Legal Review Note:** YC Library essays and YouTube transcripts are publicly available. OpenOpenYC Skills extracts short, attributed snippets (fair use) and synthesizes the underlying principles. No full essays or transcripts are reproduced in the generated skills. Raw content files are gitignored and never published. By using the BYOK model, contributors act as the operator. Legal review is recommended before commercial use.

---

## Important Links

| Document | Description |
|----------|-------------|
| [Consumption Guide](docs/CONSUMPTION.md) | How to use skills in your AI agent (for consumers) |
| [BYOK Guide](docs/BYOK.md) | How to fork, set up, and generate new skills (for contributors) |
| [Taxonomy Map](docs/TAXONOMY.md) | The complete category and subcategory tree |
| [AGENTS.md](AGENTS.md) | Operating manual for AI coding agents working on this codebase |
| [Architecture Spec](openopenyc-skills-architecture-v1.1.md) | The full technical architecture document |
| [Implementation Plan](IMPLEMENTATION_PLAN.md) | Detailed task-by-task build plan |
