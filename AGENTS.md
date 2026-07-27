# AGENTS.md — YC Skills Forge

> **Authoritative operating manual for AI coding agents.**
> Derived from [`yc-skills-forge-architecture-v1.1.md`](yc-skills-forge-architecture-v1.1.md).
> Last updated: 2026-07-28.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Repository Organization](#3-repository-organization)
4. [Architectural Rules](#4-architectural-rules)
5. [Coding Standards](#5-coding-standards)
6. [Development Workflow](#6-development-workflow)
7. [Testing Expectations](#7-testing-expectations)
8. [Security Rules](#8-security-rules)
9. [Data Model and Persistence](#9-data-model-and-persistence)
10. [API Rules](#10-api-rules)
11. [File Modification Rules](#11-file-modification-rules)
12. [Dependency Policy](#12-dependency-policy)
13. [Documentation Policy](#13-documentation-policy)
14. [Agent Workflow](#14-agent-workflow)
15. [Common Pitfalls](#15-common-pitfalls)
16. [Decision Rules](#16-decision-rules)
17. [Completion Checklist](#17-completion-checklist)

---

## 1. Project Overview

### Purpose

YC Skills Forge is a **static-file generator** that ingests content from Y Combinator's Library and YouTube channels, extracts actionable startup advice, clusters it into narrow principles, and emits versioned skill files (Markdown + YAML frontmatter) and agent spec files (JSON). The output is a GitHub repository that AI agents consume directly — no runtime, no database, no API keys required by end users.

### High-Level Goals

- Convert YC knowledge into **narrow, composable skill files** usable by AI agents.
- Preserve **exact quote fidelity** — every attribution must be verbatim from source transcripts/articles.
- Provide **multiple spec formats** (MCP, OpenAI function schema, Hermes plain-text) so any agent framework can consume skills.
- Maintain a **zero-cost end-user experience** — consumers download static files from GitHub.
- Enable a **BYOK (Bring Your Own Keys)** model for contributors who want to regenerate or extend skills.

### Non-Goals

- **No runtime RAG / No runtime vector DB.** The published product is entirely static files.
- **No scheduled automation.** Generation is triggered manually by maintainers via local CLI or `workflow_dispatch`.
- **No paraphrasing in attribution blocks.** Quotes must be verbatim.
- **No end-user API keys or embedding model downloads.** The consumer experience is read-only static files.
- **No hallucinated `related_skills` links.** They are populated by a deferred post-processing pass using the similarity matrix, never by the synthesis LLM.

### Core Business Domain

Startup advice extraction and knowledge management — specifically Y Combinator ecosystem content.

### Success Criteria

- Every skill passes the three-layer validation suite (quote verification, schema validation, hallucination guard).
- `skills-index.json` and `data/similarity_matrix.json` are committed and up-to-date after each pipeline run.
- End-user agents can consume skills without installing any dependencies or running any code from this repo.

---

## 2. System Architecture

### Architectural Pattern

**Batch ETL → Static Site Generator → Git Repository**

### Core Loop (Manual Trigger)

```
Discover → Download → Chunk → Extract → Cluster → Synthesize → Link → Export → Validate → Commit → Tag
```

### Major Components and Responsibilities

| Component | Directory | Responsibility |
|-----------|-----------|----------------|
| **Ingest** | `src/ingest/` | Scrapes YC Library essays and downloads YouTube transcripts/metadata. |
| **Chunker** | `src/chunker/` | Splits raw content into sized chunks (200–800 words) with overlap. |
| **Forge** | `src/forge/` | Core pipeline: batch selection, LLM extraction, local clustering, LLM synthesis, deferred linking. |
| **Exporter** | `src/exporter/` | Generates MCP, OpenAI, and Hermes spec files from validated skills. |
| **Validator** | `src/validator/` | Quote verification (fuzzy match), schema validation (Pydantic), hallucination guard (LLM-as-judge). |
| **Retrieval** | `src/retrieval/` | **Build-time only.** Generates `skills-index.json` and `data/similarity_matrix.json`. |
| **CLI** | `src/cli.py` | Single entry point: `python -m src.cli`. |
| **Config** | `src/config.py` | Pydantic settings loader for all YAML config files. |
| **Models** | `src/models.py` | Pydantic data models for all domain objects. |

### Dependency Graph (Data Flow Direction)

```
CLI
 ├── Ingest (Library Scraper, YouTube Downloader)
 │    └── writes → data/raw/, content table
 ├── Chunker (Essay, Transcript)
 │    └── reads data/raw/ → writes data/chunks/, chunks table
 ├── Forge
 │    ├── Batcher → reads chunks table → selects batch
 │    ├── Extractor → LLM Call 1 → writes extracted_items table
 │    ├── Clusterer → local embeddings → writes clusters, cluster_items tables
 │    ├── Synthesizer → LLM Call 2 → writes skills/ files, skills table
 │    └── Linker → reads similarity_matrix.json → updates skills/ frontmatter
 ├── Exporter → reads skills/ → writes specs/
 ├── Validator → reads skills/, data/chunks/ → pass/fail
 └── Retrieval (Resolver) → reads skills/ → writes skills-index.json, similarity_matrix.json
```

### Request Lifecycle (Pipeline Run)

1. **Batch Selection** (`batcher.py`): Selects 5–20 content items with `state = 'chunked'`, scoped by `--topic`. Sets state to `extracting`.
2. **Extraction** (`extractor.py`): One LLM call per batch. Parses JSON response. Inserts into `extracted_items`. Sets state to `extracted`.
3. **Clustering** (`clusterer.py`): No LLM. Local `sentence-transformers` embeddings + `AgglomerativeClustering`. Writes `clusters` and `cluster_items`. Sets state to `clustered`.
4. **Synthesis** (`synthesizer.py`): One LLM call per cluster. Generates Markdown skill file. Computes confidence from cluster metrics (not LLM self-report). Sets state to `synthesized`.
5. **Linking** (`linker.py`): No LLM. Deferred pass using `similarity_matrix.json`. Populates `related_skills`. Sets state to `linked`.
6. **Export** (`exporter/`): Generates MCP, OpenAI, Hermes spec files.
7. **Validation** (`validator/`): Three checks — quote verification, schema validation, hallucination guard.
8. **Commit & Tag**: Manual git workflow on a `forge/batch-{batch_id}` branch.

### Trust Boundaries

- **LLM outputs are untrusted.** All LLM-generated content passes through the three-layer validation suite before publication.
- **`related_skills` are never LLM-generated.** They come from the pre-computed similarity matrix.
- **`confidence` is never LLM-generated.** It is computed from cluster metrics: `avg_similarity`, `item_count`, and contradiction presence.
- **Hallucination guard uses a dedicated validator model** (`gemini-1.5-flash` at `temperature: 0.0`), not the rotating pool.

### External Integrations

| External Service | Usage | Module |
|-----------------|-------|--------|
| YC Library (web) | Essay scraping | `src/ingest/library_scraper.py` |
| YouTube (via `yt-dlp`) | Transcript/metadata download | `src/ingest/youtube_downloader.py` |
| DeepSeek API | LLM extraction/synthesis (priority 1) | `src/forge/llm_client.py` |
| Kimi (Moonshot) API | LLM fallback (priority 2) | `src/forge/llm_client.py` |
| GLM (BigModel) API | LLM fallback (priority 3) | `src/forge/llm_client.py` |
| Gemini API | LLM fallback (priority 4) + dedicated validator | `src/forge/llm_client.py` |

### Cross-Cutting Concerns

- **State Machine**: The `content.state` column drives the pipeline. Each stage transitions state strictly forward (except reaper recovery).
- **LLM Provider Rotation**: Round-robin by priority with quota-aware fallback across all LLM stages.
- **Usage Tracking**: Every LLM call is logged to `usage_log` table with token counts and cost estimates.
- **Error Recovery**: Reaper command resets stale `extracting` states after 2 hours. Failed items are retried up to 3 times.

---

## 3. Repository Organization

### Directory Structure

```
yc-skills-forge/
├── .github/workflows/validate.yml   # PR validation ONLY — never generation
├── data/
│   ├── raw/library/                  # HTML/Markdown of essays (GITIGNORED)
│   ├── raw/youtube/                  # JSON metadata + VTT transcripts (GITIGNORED)
│   ├── chunks/library/               # JSON chunk files (GITIGNORED)
│   ├── chunks/youtube/               # JSON chunk files (GITIGNORED)
│   ├── errors/                       # Failed LLM responses (GITIGNORED)
│   ├── registry.db                   # SQLite state machine (GITIGNORED)
│   └── similarity_matrix.json        # Pre-computed skill similarities (COMMITTED)
├── skills/                           # One subdirectory per category
│   ├── fundraising/
│   ├── hiring/
│   ├── product/
│   ├── growth/
│   ├── culture/
│   ├── strategy/
│   ├── founder-mental-models/
│   └── technical/
├── specs/
│   ├── mcp/                          # Model Context Protocol JSONs
│   ├── openai/                       # OpenAI function schemas
│   └── hermes/                       # Plain-text system prompt fragments
├── src/
│   ├── __init__.py
│   ├── config.py                     # Pydantic settings loader
│   ├── models.py                     # Pydantic data models
│   ├── ingest/                       # Content ingestion (scraper, downloader)
│   ├── chunker/                      # Content chunking (essay, transcript)
│   ├── forge/                        # Core pipeline (batcher, extractor, clusterer, synthesizer, linker)
│   │   └── prompts/                  # Jinja2 prompt templates (extract.j2, synthesize.j2)
│   ├── exporter/                     # Spec file generators (mcp, openai, hermes)
│   ├── validator/                    # Validation suite (quote_verifier, schema_validator, hallucination_guard)
│   ├── retrieval/                    # Build-time index/matrix generation (resolver.py)
│   └── cli.py                        # Single entry point
├── config/
│   ├── taxonomy.yml                  # Exhaustive topic tree — new categories require PR
│   ├── providers.yml                 # LLM provider configs with quota settings
│   └── pipeline.yml                  # Chunking, clustering, threshold parameters
├── scripts/
│   ├── setup.sh                      # One-command local setup
│   └── backfill.sh                   # Historical content ingestion
├── docs/
│   ├── CONSUMPTION.md                # How to use skills in agents
│   ├── BYOK.md                       # Fork and run yourself
│   └── TAXONOMY.md                   # Human-readable topic map
├── requirements.txt                  # Exact pinned versions — no ranges
├── pyproject.toml                    # Project metadata + tool configs
├── .env.example                      # Template for API keys
├── .gitignore
├── skills-index.json                 # Machine-readable index (COMMITTED, auto-generated)
└── README.md
```

### Where New Code Belongs

| Type of Code | Location |
|-------------|----------|
| New pipeline stage | `src/forge/` (new module) |
| New ingestion source | `src/ingest/` (new module) |
| New export format | `src/exporter/` (new module) |
| New validation check | `src/validator/` (new module) |
| New CLI command | `src/cli.py` (new subcommand) |
| Prompt templates | `src/forge/prompts/` (new `.j2` file) |
| Pydantic models | `src/models.py` |
| Configuration schemas | `src/config.py` |
| Config files | `config/` (new `.yml` file) |

### Where Code Should NOT Be Added

- **`skills/`** — Auto-generated. Never write skill files by hand.
- **`specs/`** — Auto-generated by exporters. Never write spec files by hand.
- **`skills-index.json`** — Auto-generated by `src/retrieval/resolver.py`.
- **`data/similarity_matrix.json`** — Auto-generated by `src/retrieval/resolver.py`.
- **`data/raw/`**, **`data/chunks/`**, **`data/errors/`** — Pipeline artifacts, gitignored.
- **`.github/workflows/`** — Must ONLY contain validation. Never add generation workflows.

### Naming Conventions

- **Python files:** `snake_case.py`
- **Config files:** `snake_case.yml`
- **Skill files:** `{skill_id}.md` where `skill_id` follows pattern `yc-{category}-{subcategory}-{descriptor}` (all lowercase, hyphen-separated, max 6 words after `yc-{category}`)
- **Spec files:** `{skill_id}.json` (MCP, OpenAI) or `{skill_id}.txt` (Hermes)
- **Prompt templates:** `{stage_name}.j2` (Jinja2)
- **Chunk files:** `{content_id}_{chunk_index:04d}.json`
- **Content IDs:** `lib_{sha256(url)[:12]}` for library, `yt_{video_id}` for YouTube

---

## 4. Architectural Rules

### Layering Rules

The system has three layers with strict dependency direction:

```
Layer 1 (Data):    src/models.py, src/config.py, config/
Layer 2 (Logic):   src/ingest/, src/chunker/, src/forge/, src/exporter/, src/validator/, src/retrieval/
Layer 3 (Interface): src/cli.py
```

- **Layer 3 may import from Layer 2 and Layer 1.**
- **Layer 2 may import from Layer 1 only.**
- **Layer 1 may not import from Layer 2 or Layer 3.**
- **Layer 2 modules may not import from each other across stages** except through shared models and config. For example, `src/forge/extractor.py` may not directly import from `src/validator/`. The CLI orchestrates cross-stage data flow.

### Dependency Direction

All data flows forward through the pipeline stages:

```
Ingest → Chunker → Forge (Batch → Extract → Cluster → Synthesize → Link) → Export → Validate
```

No stage may call backward into a prior stage. The CLI is the single orchestrator.

### Allowed Imports

- Any module may import from `src/models.py` and `src/config.py`.
- Any module may import from Python stdlib and the locked dependency list (Section 3 of architecture doc).
- `src/forge/llm_client.py` is a shared utility importable by `extractor.py`, `synthesizer.py`, and `hallucination_guard.py`.

### Forbidden Imports

- **No circular imports.** The layer structure prevents these.
- **`src/retrieval/` must not be imported by any end-user-facing module.** It is build-time only.
- **`sentence-transformers` must not appear in any module outside `src/forge/clusterer.py`, `src/forge/linker.py`, and `src/retrieval/resolver.py`.** End users never load this model.
- **No direct `import openai` outside `src/forge/llm_client.py`.** All LLM access goes through the unified client.

### Separation of Concerns

- **LLM calls are isolated** in `extractor.py` (extraction), `synthesizer.py` (synthesis), and `hallucination_guard.py` (validation). No other module makes LLM calls.
- **Embedding computation is isolated** in `clusterer.py`, `linker.py`, and `resolver.py`. No other module loads `sentence-transformers`.
- **Database access is isolated** in the modules that own the relevant tables. Use the models layer for data transfer between modules.

### State Ownership

The `content.state` column is the single source of truth for pipeline progress. The valid state transitions are:

```
discovered → downloaded → chunked → extracting → extracted → clustered → synthesized → linked → validated → published
                                         ↓ (reaper after 2h)
                                      chunked
Any state → failed (on unrecoverable error)
```

- Only the module responsible for a stage may transition state forward.
- Only the reaper (`python -m src.cli reaper`) may transition `extracting → chunked`.
- Only a human or `--retry-failed` flag may recover from `failed`.

### Error Propagation

- Pipeline stages **abort the current batch** on unrecoverable errors and mark affected items `failed`.
- Recoverable errors (HTTP 429, LLM timeout) trigger retries up to `max_retries` (3), then mark `failed`.
- Raw LLM error responses are saved to `data/errors/{batch_id}.json` for manual review.
- Validation failures set skill state to `failed` and move the file to `skills/_failed/`.

### Data Ownership

| Data | Owner Module | Storage |
|------|-------------|---------|
| Raw content | `src/ingest/` | `data/raw/` + `content` table |
| Chunks | `src/chunker/` | `data/chunks/` + `chunks` table |
| Extracted items | `src/forge/extractor.py` | `extracted_items` table |
| Clusters | `src/forge/clusterer.py` | `clusters` + `cluster_items` tables |
| Skill files | `src/forge/synthesizer.py` | `skills/` directory + `skills` table |
| Related skills | `src/forge/linker.py` | `skills` table + skill file frontmatter |
| Spec files | `src/exporter/` | `specs/` directory |
| Index/matrix | `src/retrieval/resolver.py` | `skills-index.json` + `data/similarity_matrix.json` |
| Usage logs | `src/forge/llm_client.py` | `usage_log` table |

---

## 5. Coding Standards

### Language and Runtime

- **Python 3.11+** exclusively. No other languages.
- All logic runs as a CLI tool: `python -m src.cli`.

### Pydantic Models

- All domain objects MUST have a Pydantic model in `src/models.py`.
- Use Pydantic v2 (`pydantic >= 2.9.x`).
- Use `Field()` with constraints (pattern, min_length, max_length, ge, le) for all validated fields.
- Skill ID regex: `^yc-[a-z]+(-[a-z]+){1,6}$`.
- Version regex: `^\d+\.\d+\.\d+$`.

### LLM Interaction Patterns

- All LLM calls go through the unified `LLMClient` in `src/forge/llm_client.py`.
- Always request `response_format={"type": "json_object"}` where supported. Fall back to explicit JSON instructions in the prompt + `json.loads()` in a `try/except` block.
- Set `temperature=0.3` for extraction and synthesis. Set `temperature=0.0` for the hallucination guard.
- Always log usage to `usage_log` table after every call (success or failure).
- Never hardcode provider API keys. Read from environment variables via `config/providers.yml` substitution.

### Prompt Templates

- All prompts MUST be Jinja2 templates stored in `src/forge/prompts/`.
- Template variables must match the data models exactly.
- Never build prompts via string concatenation in Python code.

### Error Handling

- Use structured error types — do not raise bare `Exception`.
- Log raw LLM responses to `data/errors/{batch_id}.json` on parse failure.
- All HTTP requests must have explicit `timeout` (30s for scraping, 120s for LLM calls).
- Retry logic: max 3 retries for transient errors (HTTP 429, timeouts). Mark `failed` on exhaustion.
- On JSON parse failure from LLM: retry once with `temperature=0.1`, then fail.

### Configuration

- All thresholds, parameters, and tuning values live in `config/pipeline.yml`. Do not hardcode them in Python.
- Provider configs live in `config/providers.yml`.
- Taxonomy lives in `config/taxonomy.yml`.
- Use `src/config.py` (Pydantic settings) to load all config files.

### Async Patterns

- **No async code.** The pipeline is synchronous batch processing. Use `subprocess.run()` for `yt-dlp` calls. Use `requests` (not `aiohttp`) for HTTP.
- Rate-limit scraping with `time.sleep(2)` between requests.

### Naming Conventions (Python)

- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`
- Module-level loggers: `logger = logging.getLogger(__name__)`

### Documentation Expectations

- Every public function and class must have a docstring.
- Docstrings must describe inputs, outputs, side effects (database writes, file writes), and error conditions.
- Inline comments for non-obvious logic, especially in clustering parameters and confidence computation.

### Patterns to Avoid

- **No global mutable state.** Pass dependencies explicitly (config, db connection, LLM client).
- **No `import *`.** Always use explicit imports.
- **No f-string prompt construction.** Use Jinja2 templates.
- **No `print()` for logging.** Use the `logging` module.
- **No raw SQL string interpolation.** Use parameterized queries (`?` placeholders).
- **No inventing YC quotes.** Every quote must trace to a source chunk.
- **No LLM-generated `related_skills` or `confidence`.** These are computed post-hoc.

---

## 6. Development Workflow

### Prerequisites

- Python 3.11 or 3.12
- Git
- `yt-dlp` (installed via `pip install yt-dlp`)
- API keys for at least one LLM provider (DeepSeek, Kimi, GLM, or Gemini)

### Setup

```bash
# Clone and enter repo
git clone <repo-url>
cd yc-skills-forge

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

### Build / Run Commands

```bash
# Initialize SQLite database
python -m src.cli init-db

# Ingest content
python -m src.cli ingest-library --url <url>
python -m src.cli ingest-youtube --url <url>

# Chunk all downloaded content
python -m src.cli chunk --all

# Run forge pipeline
python -m src.cli forge --topic <topic> --batch-size 15

# Run deferred link pass
python -m src.cli link --topic <topic>

# Validate all skills
python -m src.cli validate --all

# Export specs
python -m src.cli export --all

# Generate index and similarity matrix
python -m src.cli index

# Reset stale extracting items
python -m src.cli reaper

# Check provider quota usage
python -m src.cli quota

# Historical backfill
python -m src.cli backfill --start-date 2020-01-01
```

### Lint / Format Commands

```bash
# Lint and format with ruff
ruff check src/
ruff format src/
```

### Test Commands

```bash
# Run all tests
python -m pytest

# Run validator tests only
python -m pytest tests/validator/

# Run with coverage
python -m pytest --cov=src
```

### Type Checking

Use **mypy** with the Pydantic plugin for static type checking. Mypy is preferred over pyright here because Pydantic v2 ships a first-party mypy plugin (`pydantic.mypy`) that validates `Field()` constraints, model inheritance, and config classes — all of which are central to this codebase.

```bash
# Run type checking
mypy src/ --strict
```

Add to `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.11"
strict = true
plugins = ["pydantic.mypy"]
warn_return_any = true
warn_unused_configs = true

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true
```

Add `mypy` to `requirements.txt` (pinned, e.g., `mypy==1.11.x`).

### Code Generation

There is no code generation step. Prompt templates are Jinja2 files interpreted at runtime.

### Git Workflow

1. **Branch from `main`:** `git checkout -b forge/batch-{batch_id}`
2. **Run pipeline locally** (ingest → chunk → forge → link → export → validate).
3. **Commit generated files:** `git add skills/ specs/ data/similarity_matrix.json skills-index.json`
4. **Push and open PR.** GitHub Actions runs validation automatically.
5. **Merge after green CI.** Maintainer reviews, merges if validation passes.
6. **Tag release:** `git tag -a v{X.Y.Z} -m "Release v{X.Y.Z} - N skills"`

---

## 7. Testing Expectations

### Required Tests by Change Type

| Change | Required Tests |
|--------|----------------|
| New pipeline stage | Unit tests for the stage logic, integration test with sample data |
| New Pydantic model | Model validation tests (valid and invalid inputs) |
| Changed chunking parameters | Tests with sample essays/transcripts verifying chunk size bounds |
| Changed clustering threshold | Tests verifying cluster quality with known embedding fixtures |
| New exporter | Tests verifying output matches spec format exactly |
| Changed validation logic | Tests with known-good and known-bad skill files |
| New CLI command | Smoke test exercising the command with `--help` and sample args |
| Changed prompt template | Manual review — template changes affect LLM output non-deterministically |

### Test Organization

```
tests/
├── test_models.py            # Pydantic model validation
├── test_config.py            # Config loading
├── ingest/
│   ├── test_library_scraper.py
│   └── test_youtube_downloader.py
├── chunker/
│   ├── test_essay_chunker.py
│   └── test_transcript_chunker.py
├── forge/
│   ├── test_batcher.py
│   ├── test_extractor.py
│   ├── test_clusterer.py
│   ├── test_synthesizer.py
│   └── test_linker.py
├── exporter/
│   ├── test_mcp_exporter.py
│   ├── test_openai_exporter.py
│   └── test_hermes_exporter.py
├── validator/
│   ├── test_quote_verifier.py
│   ├── test_schema_validator.py
│   └── test_hallucination_guard.py
└── retrieval/
    └── test_resolver.py
```

### Mocking Policy

- **Mock all LLM calls** in unit tests. Provide fixture JSON responses that match the expected schema.
- **Mock all HTTP calls** (scraping, YouTube) in unit tests. Use `responses` or `requests-mock`.
- **Do NOT mock** Pydantic validation, SQLite operations (use in-memory DB), or local embedding computation (use small fixture embeddings if `sentence-transformers` is too slow).

### Coverage Expectations

- Recommend 80% line coverage for `src/` excluding `cli.py`.

### Integration Testing

- The full pipeline can be integration-tested with a small fixture dataset (2–3 essays/transcripts).
- Integration tests should exercise the full flow: ingest → chunk → forge → link → export → validate.
- These tests require at least one LLM provider key and are expected to run manually, not in CI.

### Regression Testing

- If a validation rule is changed, re-run `python -m src.validator.run --all` against the full skills corpus to ensure no regressions.
- Keep a set of known-good skill files as golden fixtures in `tests/fixtures/`.

---

## 8. Security Rules

### Secrets Management

- **Never commit API keys.** They are stored in `.env` (gitignored) and referenced via `${VAR}` substitution in `config/providers.yml`.
- `.env.example` contains placeholders only (`sk-...`).
- Never log API keys, even partially. Log provider name and model, not the key.

### Input Validation

- All LLM responses are parsed through Pydantic models before any further processing. Reject malformed responses.
- All URLs provided to the scraper must be validated before HTTP requests.
- SQL queries use parameterized statements (`?` placeholders). **Never interpolate user input into SQL strings.**

### Scraping Compliance

- **Respect `robots.txt`** at `https://www.ycombinator.com/robots.txt`.
- **Rate limit:** Maximum 1 request per 2 seconds. Use `requests.Session()` with `time.sleep(2)`.
- **User-Agent:** `YC-Skills-Forge/1.0 (Research Project; contact@example.com)`
- **YouTube:** Only download captions/subtitles via `yt-dlp --skip-download`. Never download video files.

### Logging Sensitive Information

- Never log raw LLM prompts containing full chunk text to stdout in production. Write to `data/errors/` (gitignored) only on failure.
- Log token counts, cost estimates, and provider names — not prompt content.

### PII Handling

- Speaker names and designations are public information (YC speakers, public videos). No PII concerns for this data.
- Contact email in User-Agent (`contact@example.com`) is a placeholder. Maintainer should replace with a real address.

### Cryptography

- Content IDs use SHA256 for deterministic hashing of URLs: `lib_{sha256(url)[:12]}`. This is for collision resistance, not security.

### Security Boundaries

- **LLM outputs are untrusted.** The validation suite is the security boundary between LLM-generated content and published skills.
- **The hallucination guard uses a dedicated model** (`gemini-1.5-flash` at `temperature: 0.0`), never the rotating pool. If Gemini quota is exhausted, the LLM-as-judge step is skipped with a logged warning — it does NOT fall back to another provider for this safety-critical check.
- **Validation failure blocks publication.** A skill with `partial_ratio < 70` or a failed hallucination check is moved to `skills/_failed/` and the PR is blocked.

### License Compliance

- Code: MIT License.
- Generated skill content: CC BY-SA 4.0 (attribution required, share-alike).
- Raw YC content: Not redistributed; gitignored. Used for research/commentary purposes.
- **Legal review recommended** before commercial use — verbatim quote reproduction at scale has fair-use implications.

---

## 9. Data Model and Persistence

### Database

- **Engine:** SQLite 3 (Python stdlib `sqlite3`).
- **File:** `data/registry.db` (gitignored — maintainer-local only).
- **No migrations framework.** Schema initialization via `python -m src.cli init-db` which runs `src/migrations/001_init.sql`.

### Tables and Ownership

| Table | Owner | Purpose |
|-------|-------|---------|
| `content` | `src/ingest/` | Source content metadata and state machine |
| `chunks` | `src/chunker/` | Individual text chunks with word/char counts |
| `extracted_items` | `src/forge/extractor.py` | LLM-extracted advice items |
| `clusters` | `src/forge/clusterer.py` | Cluster metadata with avg_similarity |
| `cluster_items` | `src/forge/clusterer.py` | Cluster membership with similarity scores |
| `skills` | `src/forge/synthesizer.py` | Skill registry with computed_confidence |
| `usage_log` | `src/forge/llm_client.py` | LLM token/cost tracking |

### Schema Rules

- The schema is specified exactly in Section 4.1 of the architecture doc. **Do not modify column names, types, or constraints without updating the architecture doc.**
- `chunk_index` (not `index`) — `index` is a SQL reserved word.
- `in_batch_index` — 1-based integer index within the extraction prompt.
- `computed_confidence` — derived from cluster metrics, never from LLM self-report.
- `state` columns use CHECK constraints with exact enum values.

### Content ID Generation

- **Library essays:** `lib_{sha256(url)[:12]}` — deterministic, collision-resistant.
- **YouTube videos:** `yt_{video_id}` — YouTube's 11-char ID is globally unique.
- **Chunk IDs:** `{content_id}_{chunk_index:04d}` — e.g., `yt_abc123def45_0003`.
- **Deduplication:** The `url UNIQUE` constraint is the real dedup key. Skip re-ingestion if URL exists.

### Transaction Rules

- Each pipeline stage operates within a single SQLite transaction per batch.
- State transitions and data insertions must be atomic — if insertion fails, state must not advance.
- Use `BEGIN TRANSACTION` / `COMMIT` / `ROLLBACK` explicitly.

### Caching

- The `sentence-transformers` model `all-MiniLM-L6-v2` is cached locally after first download.
- `data/similarity_matrix.json` is a pre-computed cache of pairwise skill similarities. Regenerated after each batch.
- `skills-index.json` is a pre-computed index. Regenerated after each batch.

### Data Lifecycle

- Raw content (`data/raw/`) is retained locally for quote verification but never committed.
- Chunks (`data/chunks/`) are retained locally for the same reason.
- Error logs (`data/errors/`) are retained for manual review.
- The SQLite database is local-only. A fresh clone starts with no history (cold-start problem documented in BYOK).

---

## 10. API Rules

This project does not expose a runtime API. However, it generates **spec files** that describe skills as callable functions for AI agents.

### Spec Formats

| Format | Directory | Target |
|--------|-----------|--------|
| MCP | `specs/mcp/{skill_id}.json` | Claude Code, MCP-compatible agents |
| OpenAI | `specs/openai/{skill_id}.json` | OpenAI function-calling agents |
| Hermes | `specs/hermes/{skill_id}.txt` | Local models (llama.cpp, Ollama) |

### Spec Rules

- Every spec file MUST include a `fallback` block with `use_agent_knowledge: true` and `invent_quotes: false`.
- MCP specs use `inputSchema` with `type: "object"` and list `required` fields.
- OpenAI specs wrap the function in `{"type": "function", "function": {...}}` format with a `metadata` block.
- Hermes specs are plain text with `[SKILL: ...]` / `[END SKILL]` delimiters.
- All spec files are auto-generated by the exporter modules. Never edit them manually.

### Signal Resolution (Build-Time)

- `/` prefix → category path filter.
- `%` prefix → tag filter (AND logic for multiple comma-separated tags).
- `yc-` prefix → exact skill ID lookup.
- No prefix → fuzzy embedding similarity search (top 3 results).

### Backward Compatibility

- Skill IDs are permanent. Once published, a `skill_id` must not be reused for different content.
- Removing a skill requires a deprecation notice in the PR description.
- Spec schemas should maintain backward compatibility — add optional fields, do not remove required fields.

---

## 11. File Modification Rules

### Auto-Generated Files — NEVER Edit Manually

| File/Directory | Generator |
|----------------|-----------|
| `skills/**/*.md` | `src/forge/synthesizer.py` + `src/forge/linker.py` |
| `specs/mcp/**` | `src/exporter/mcp_exporter.py` |
| `specs/openai/**` | `src/exporter/openai_exporter.py` |
| `specs/hermes/**` | `src/exporter/hermes_exporter.py` |
| `skills-index.json` | `src/retrieval/resolver.py` |
| `data/similarity_matrix.json` | `src/retrieval/resolver.py` |

### Files That May Be Edited

| File | Owner | Notes |
|------|-------|-------|
| `src/**/*.py` | Developers | Source code — follow architectural rules |
| `config/taxonomy.yml` | Maintainer | New categories require a PR |
| `config/providers.yml` | Maintainer | API key template, provider config |
| `config/pipeline.yml` | Maintainer | Tuneable parameters |
| `src/forge/prompts/*.j2` | Developers | Prompt changes affect LLM output — test carefully |
| `requirements.txt` | Maintainer | Exact pinned versions, no ranges |
| `pyproject.toml` | Maintainer | Project metadata and tool configs |
| `.github/workflows/validate.yml` | Maintainer | Validation CI only |
| `docs/**` | Developers | Documentation |
| `README.md` | Developers | Project overview |
| `AGENTS.md` | Maintainer | This file |

### Vendor Code

There is no vendored code. All dependencies are installed via `pip`.

### Configuration Ownership

- **`config/taxonomy.yml`** is the exhaustive category tree. Adding a new category requires a PR that updates both the YAML and creates the corresponding `skills/{category}/` directory.
- **`config/providers.yml`** contains provider configurations with `${VAR}` placeholders. Actual keys are in `.env`.
- **`config/pipeline.yml`** contains all tuneable parameters (chunking sizes, clustering thresholds, validation thresholds).

---

## 12. Dependency Policy

### Locked Technology Stack

The technology stack is **locked**. The exact tools and versions are specified in the architecture doc (Section 3). No substitutions are permitted without an explicit architecture doc update.

| Dependency | Pinned Version | Purpose |
|-----------|---------------|---------|
| `requests` | 2.32.x | HTTP scraping |
| `beautifulsoup4` | 4.12.x | HTML parsing |
| `yt-dlp` | 2025.x | YouTube transcript download |
| `pydantic` | 2.9.x | Schema enforcement |
| `PyYAML` | 6.0.x | Config and frontmatter parsing |
| `sentence-transformers` | 2.7.x | Embeddings (build-time only) |
| `rapidfuzz` | 3.9.x | Quote verification |
| `openai` | 1.40.x | Unified LLM client |
| `Jinja2` | 3.1.x | Prompt templates |
| `pytest` | 8.3.x | Testing |
| `ruff` | 0.6.x | Linting/formatting |
| `markdownify` | 0.13.x | HTML → Markdown conversion |
| `scikit-learn` | *(version not specified)* | Agglomerative clustering |

### When New Dependencies Are Allowed

- A new dependency is allowed **only** when no existing library can fulfill the requirement.
- The dependency must be justified in the PR description.
- It must be pinned to an exact minor version in `requirements.txt`.
- It must not introduce a runtime requirement for end users (the published output is static files).

### Evaluation Criteria for New Dependencies

1. Is there an existing locked dependency that can do this?
2. Is it well-maintained (recent releases, active issue tracker)?
3. Does it have a compatible license (MIT, Apache 2.0, BSD preferred)?
4. Does it introduce heavy transitive dependencies?
5. Does it work on Python 3.11+ without native compilation issues?

### Package Management

- Use `pip` (24.x). No `poetry`, `conda`, or `pipenv`.
- `requirements.txt` pins exact versions. No version ranges.
- Virtual environment: `.venv/` (gitignored).

---

## 13. Documentation Policy

### When Documentation Must Be Updated

| Change | Documents to Update |
|--------|---------------------|
| New category added to taxonomy | `config/taxonomy.yml`, `docs/TAXONOMY.md` |
| New CLI command added | `README.md` (quickstart), `docs/BYOK.md` (if user-facing) |
| New export format added | `docs/CONSUMPTION.md` |
| Changed validation rules | This `AGENTS.md` file (Section 7, 8) |
| New pipeline stage | Architecture doc, this `AGENTS.md` |
| Changed provider config | `config/providers.yml`, `.env.example` |
| Changed skill file format | Architecture doc (Section 10), this `AGENTS.md` |

### Documents That Must Stay Synchronized

| Document | Synchronized With |
|----------|-------------------|
| `config/taxonomy.yml` | `skills/` directory structure, `docs/TAXONOMY.md` |
| `config/pipeline.yml` | Actual parameter values used in `src/` code |
| `requirements.txt` | Actual imports used in `src/` code |
| `docs/CONSUMPTION.md` | Spec file formats in `specs/` |
| `docs/BYOK.md` | CLI commands in `src/cli.py` |
| `skills-index.json` | Contents of `skills/` directory |
| `data/similarity_matrix.json` | All published skills |

---

## 14. Agent Workflow

### How to Approach a Task

1. **Read this `AGENTS.md` first.** It is the primary source of truth for repository-specific rules.
2. **Read the architecture doc** (`yc-skills-forge-architecture-v1.1.md`) for detailed specifications on the component you are modifying.
3. **Identify the component** your change belongs to (see Section 3: Repository Organization).
4. **Verify layering rules** — ensure your change respects the dependency direction (Section 4).
5. **Check if the file is auto-generated** — if so, modify the generator, not the output (Section 11).

### What to Read Before Editing

| File You Want to Edit | Read First |
|-----------------------|------------|
| Any `src/forge/` module | Architecture doc Sections 8, 9 (pipeline stages, LLM rotation) |
| Any `src/validator/` module | Architecture doc Section 14 (validation suite) |
| Any `src/ingest/` module | Architecture doc Section 5 (ingestion) |
| Any `src/chunker/` module | Architecture doc Section 7 (chunking engine) |
| Any `src/exporter/` module | Architecture doc Section 11 (spec formats) |
| `src/models.py` | Architecture doc Sections 4, 10 (schema, frontmatter) |
| `config/taxonomy.yml` | Architecture doc Section 6 (taxonomy) |
| `config/pipeline.yml` | Architecture doc Sections 7, 8, 14 (parameters) |
| Prompt templates (`*.j2`) | Architecture doc Sections 8, 20 (exact prompt specs) |

### How to Keep Changes Scoped

- Each PR should address one pipeline stage or one cross-cutting concern.
- Do not combine ingestion changes with validation changes.
- If a change requires modifying both the architecture doc and the code, note this in the PR description.
- Prefer adding new modules over modifying existing ones when adding functionality.

### When to Refactor

- When a module exceeds ~300 lines and has distinct responsibilities that can be separated.
- When you observe code duplication across modules that should share a utility function in `src/models.py` or `src/config.py`.
- When a function has more than 3 levels of nesting.

### When NOT to Refactor

- Do not refactor auto-generated files. Fix the generator instead.
- Do not refactor prompt templates for "cleanliness" — they are tuned for LLM output quality and changes have non-deterministic effects.
- Do not refactor the SQLite schema unless the architecture doc is updated first.
- Do not refactor during a bug fix PR — fix the bug only.

### How to Validate Changes

1. **Run linting:** `ruff check src/ && ruff format --check src/`
2. **Run tests:** `python -m pytest`
3. **Run validation:** `python -m src.validator.run --all`
4. **For pipeline changes:** Run the full pipeline with a scoped `--topic` on a small batch and verify the output skill files.
5. **For schema changes:** Validate all existing skill files still parse correctly.

### Before Considering Work Complete

Run the Completion Checklist in Section 17.

---

## 15. Common Pitfalls

### 1. Using `index` Instead of `chunk_index`

`index` is a SQL reserved word. The schema uses `chunk_index` everywhere. Using `index` will cause silent SQL errors or incorrect behavior.

### 2. Letting the LLM Generate `related_skills`

The synthesis prompt explicitly sets `related_skills: []` and `confidence: 0.0`. These are populated by the deferred Link pass (`linker.py`) and the confidence computation formula, respectively. If you see LLM output with populated `related_skills`, **discard them**.

### 3. Letting the LLM Self-Report Confidence

Confidence is **always** computed from cluster metrics:
```python
computed_confidence = min(0.99, max(0.55,
    (avg_similarity * 0.5) +
    (min(item_count, 10) / 10 * 0.3) +
    (0.2 if not contradictions else 0.1)
))
```
Never trust the LLM's `confidence` field.

### 4. Adding Scheduled GitHub Actions

The architecture explicitly forbids scheduled CI/CD. The `validate.yml` workflow runs on PRs only. Never add `schedule:` triggers.

### 5. Confusing Build-Time and End-User Code

`src/retrieval/resolver.py` is **build-time only**. End-user agents consume `skills-index.json` and `data/similarity_matrix.json` as static files. They never import or run `resolver.py`, `sentence-transformers`, or any Python from this repo.

### 6. Cold-Start Problem in Forks

A fresh clone has no `registry.db`. Running `forge` without `--topic` or `--urls` scoping may regenerate `_v2` duplicates of existing skills. Always scope the first run.

### 7. Duplicate Skill IDs

If a `skill_id` already exists in the `skills` table, the synthesizer appends `_v2`, `_v3`, etc. This is intentional but can be confusing. Do not "fix" this by overwriting existing skills.

### 8. Quote Verification Against Raw vs. Chunked Text

Quote fidelity is verified against **chunked** text, not raw HTML/VTT, because `markdownify` and paragraph-boundary splitting are documented lossy steps. If a quote fails verification against chunks, check `data/raw/` as a fallback — but the primary comparison is against chunks.

### 9. Hallucination Guard Provider Substitution

The hallucination guard uses **only** `gemini-1.5-flash` via the `dedicated_validator` config. If Gemini quota is exhausted, it **skips** the LLM-as-judge step and logs a warning. It does **not** fall back to another provider. Do not "fix" this by adding fallback providers for validation.

### 10. Modifying Published Skill IDs

Skill IDs are permanent identifiers. Once a skill is published to `main`, its `skill_id` must never change. Other skills may reference it in `related_skills`, and external agents may have cached references.

### 11. SQL Injection via String Formatting

All SQLite queries must use parameterized statements (`?`). Never use f-strings or `.format()` to build SQL queries, even with "trusted" internal data.

### 12. Forgetting to Update the Similarity Matrix

After synthesizing new skills, the `python -m src.cli index` command must be run to regenerate `skills-index.json` and `data/similarity_matrix.json`. Forgetting this causes stale `related_skills` in subsequent link passes.

---

## 16. Decision Rules

When facing ambiguity, resolve it using this hierarchy (highest priority first):

1. **Follow the Non-Negotiable Constraints** (Architecture doc Section 0). These are inviolable.
2. **Follow explicit instructions in this `AGENTS.md`.**
3. **Follow the architecture doc** (`yc-skills-forge-architecture-v1.1.md`).
4. **Follow established repository conventions** — look at existing code for patterns.
5. **Prefer consistency over novelty** — match existing style, naming, and patterns.
6. **Minimize the scope of changes** — do the minimum required to fulfill the task.
7. **Leave `TODO` comments instead of guessing** — if a design decision is unclear, mark it for human review.
8. **Prefer safety over convenience** — when in doubt, validate more, not less.
9. **Ask the maintainer** — if none of the above resolves the ambiguity, flag it in the PR description.

### Specific Decision Rules

| Situation | Decision |
|-----------|----------|
| Need a new dependency | Check if an existing locked dependency can do the job first |
| Need a new category | Add to `config/taxonomy.yml` and create `skills/{category}/` — requires PR |
| Need a new CLI command | Add a subcommand to `src/cli.py` — do not create a new entry point |
| LLM output is malformed | Retry once with `temperature=0.1`, then fail and log to `data/errors/` |
| Quote fails verification | Move skill to `skills/_failed/`, do not publish |
| Unsure if a change is backward-compatible | Assume it is not — add deprecation handling |
| Prompt template change | Test with at least 2 different providers before merging |

---

## 17. Completion Checklist

Before considering any task complete, verify each applicable item:

### Code Quality
- [ ] Code follows Python naming conventions (snake_case functions, PascalCase classes).
- [ ] No bare `Exception` raises — use structured error types.
- [ ] No `print()` statements — use `logging` module.
- [ ] No hardcoded API keys, file paths, or magic numbers.
- [ ] All new functions have docstrings.
- [ ] No `import *` anywhere.

### Architecture Compliance
- [ ] Change respects the layering rules (Layer 1 → 2 → 3).
- [ ] No forbidden imports (cross-stage, `sentence-transformers` in wrong module, direct `openai` import).
- [ ] State machine transitions follow the specified flow.
- [ ] LLM calls go through `LLMClient`, not direct `openai` calls.
- [ ] Auto-generated files are not manually edited.

### Testing
- [ ] `ruff check src/` passes with no errors.
- [ ] `ruff format --check src/` passes with no changes needed.
- [ ] `python -m pytest` passes.
- [ ] If pipeline logic changed: ran `python -m src.cli forge --topic <topic> --batch-size 5` on test data.
- [ ] If validation logic changed: ran `python -m src.validator.run --all`.

### Data Integrity
- [ ] SQL queries use parameterized statements (`?` placeholders).
- [ ] Content IDs use SHA256 of full URL (not slug).
- [ ] `chunk_index` is used (not `index`).
- [ ] `confidence` is computed from cluster metrics, not LLM output.
- [ ] `related_skills` are populated by the linker, not the synthesizer.

### Security
- [ ] No API keys in committed code or logs.
- [ ] Scraping respects rate limits (`time.sleep(2)` between requests).
- [ ] YouTube download uses `--skip-download` (captions only).
- [ ] Hallucination guard uses dedicated validator config.

### Documentation
- [ ] If new CLI commands added: `README.md` and `docs/BYOK.md` updated.
- [ ] If taxonomy changed: `config/taxonomy.yml` and `docs/TAXONOMY.md` updated.
- [ ] If spec format changed: `docs/CONSUMPTION.md` updated.
- [ ] If pipeline parameters changed: `config/pipeline.yml` reflects actual values.

### Git
- [ ] Changes are on a feature branch, not `main`.
- [ ] Commit message follows pattern: `{area}: {description}` (e.g., `forge: add retry logic for JSON parse failures`).
- [ ] Only relevant files are staged (no stray auto-generated files unless intentional).
- [ ] `.gitignore` still excludes `data/raw/`, `data/chunks/`, `data/registry.db`, `.env`.

---

*End of AGENTS.md*
