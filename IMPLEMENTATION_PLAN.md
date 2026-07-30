# Implementation Plan — YC Skills Forge

> **Version:** 1.0.0
> **Date:** 2026-07-28
> **Source of Truth (WHAT):** [`yc-skills-forge-architecture-v1.1.md`](yc-skills-forge-architecture-v1.1.md)
> **Source of Truth (HOW):** [`AGENTS.md`](AGENTS.md)
> **Status:** Awaiting Approval

---

## Table of Contents

1. [Milestone Overview](#milestone-overview)
2. [Milestone 1 — Project Scaffolding](#milestone-1--project-scaffolding)
3. [Milestone 2 — Core Data Layer](#milestone-2--core-data-layer)
4. [Milestone 3 — Content Ingestion](#milestone-3--content-ingestion)
5. [Milestone 4 — Content Chunking](#milestone-4--content-chunking)
6. [Milestone 5 — Forge Foundation](#milestone-5--forge-foundation)
7. [Milestone 6 — Forge Extraction](#milestone-6--forge-extraction)
8. [Milestone 7 — Forge Clustering](#milestone-7--forge-clustering)
9. [Milestone 8 — Forge Synthesis & Linking](#milestone-8--forge-synthesis--linking)
10. [Milestone 9 — Exporters](#milestone-9--exporters)
11. [Milestone 10 — Validation Suite](#milestone-10--validation-suite)
12. [Milestone 11 — Retrieval & Indexing](#milestone-11--retrieval--indexing)
13. [Milestone 12 — CLI Assembly & Utilities](#milestone-12--cli-assembly--utilities)
14. [Milestone 13 — CI/CD, Documentation & Integration](#milestone-13--cicd-documentation--integration)
15. [Development Order](#development-order)
16. [Dependency Graph](#dependency-graph)
17. [Parallelization Opportunities](#parallelization-opportunities)
18. [Risk Areas](#risk-areas)
19. [Review Gates](#review-gates)
20. [Definition of Done](#definition-of-done)
21. [Recommended Git Strategy](#recommended-git-strategy)
22. [Task Manifest](#task-manifest)

---

## Milestone Overview

| # | Milestone | Tasks | Est. Sessions | Key Deliverable |
|---|-----------|-------|---------------|-----------------|
| M1 | Project Scaffolding | 3 | 3 | Empty repo with all directories, config, dependencies |
| M2 | Core Data Layer | 4 | 5 | Models, config loader, database schema, init-db |
| M3 | Content Ingestion | 4 | 5 | Library scraper, YouTube downloader, CLI commands |
| M4 | Content Chunking | 3 | 3 | Essay + transcript chunkers, CLI command |
| M5 | Forge Foundation | 4 | 5 | LLM client, prompt templates, batcher, reaper |
| M6 | Forge Extraction | 2 | 3 | Extractor + extraction pipeline |
| M7 | Forge Clustering | 2 | 3 | Clusterer with embeddings + agglomerative clustering |
| M8 | Forge Synthesis & Linking | 4 | 5 | Synthesizer, linker, confidence computation |
| M9 | Exporters | 4 | 4 | MCP, OpenAI, Hermes exporters + CLI |
| M10 | Validation Suite | 5 | 6 | Quote verifier, schema validator, hallucination guard |
| M11 | Retrieval & Indexing | 3 | 3 | Resolver, similarity matrix, skills-index.json |
| M12 | CLI Assembly & Utilities | 3 | 3 | Full CLI, quota, backfill |
| M13 | CI/CD, Docs & Integration | 5 | 6 | GitHub Actions, docs, scripts, E2E test |
| — | **TOTAL** | **46 + 13 reviews** | **~54** | — |

---

## Milestone 1 — Project Scaffolding

**Objective:** Create the exact repository structure, dependency manifest, and project metadata files so all subsequent tasks have a stable foundation.

**Deliverables:**
- Complete directory tree matching architecture doc Section 2
- `requirements.txt` with pinned versions
- `pyproject.toml` with tool configs (ruff, mypy, pytest)
- `.gitignore` with correct exclusions
- `.env.example` with placeholder keys
- Empty `__init__.py` files in all packages
- Empty `skills/{category}/` directories for all 8 categories
- Empty `specs/{format}/` directories

**Exit Criteria:**
- `pip install -r requirements.txt` succeeds in a clean venv
- `ruff check src/` passes (on the empty `__init__.py` files)
- `.gitignore` correctly excludes `data/raw/`, `data/chunks/`, `data/registry.db`, `data/errors/`, `.env`, `.venv/`

---

### Task M1-T1: Repository Directory Structure

| Field | Value |
|-------|-------|
| **Task ID** | `M1-T1` |
| **Title** | Create full repository directory structure |
| **Goal** | Create every directory and placeholder file specified in the architecture doc Section 2. |
| **Files to Create** | `src/__init__.py`, `src/ingest/__init__.py`, `src/chunker/__init__.py`, `src/forge/__init__.py`, `src/forge/prompts/.gitkeep`, `src/exporter/__init__.py`, `src/validator/__init__.py`, `src/retrieval/__init__.py`, `src/migrations/.gitkeep`, `skills/fundraising/.gitkeep`, `skills/hiring/.gitkeep`, `skills/product/.gitkeep`, `skills/growth/.gitkeep`, `skills/culture/.gitkeep`, `skills/strategy/.gitkeep`, `skills/founder-mental-models/.gitkeep`, `skills/technical/.gitkeep`, `specs/mcp/.gitkeep`, `specs/openai/.gitkeep`, `specs/hermes/.gitkeep`, `data/.gitkeep`, `docs/.gitkeep`, `scripts/.gitkeep`, `config/.gitkeep`, `tests/__init__.py`, `tests/ingest/__init__.py`, `tests/chunker/__init__.py`, `tests/forge/__init__.py`, `tests/exporter/__init__.py`, `tests/validator/__init__.py`, `tests/retrieval/__init__.py`, `tests/fixtures/.gitkeep` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `LICENSE` |
| **Dependencies** | None |
| **Inputs** | Architecture doc Section 2 (directory tree) |
| **Outputs** | Complete directory structure with placeholder files |
| **Acceptance Criteria** | Every directory from the architecture doc exists. All Python packages have `__init__.py`. All 8 skill categories have directories. All 3 spec format directories exist. |
| **Required Tests** | None (structural task) |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M1-T1 for the YC Skills Forge project.
>
> **Objective:** Create the full repository directory structure as specified in `yc-skills-forge-architecture-v1.1.md` Section 2. Create every directory and placeholder file (`__init__.py` for Python packages, `.gitkeep` for empty non-Python directories).
>
> **Files to create:** All `__init__.py` files for `src/`, `src/ingest/`, `src/chunker/`, `src/forge/`, `src/exporter/`, `src/validator/`, `src/retrieval/`, and corresponding `tests/` packages. All `skills/{category}/` directories (fundraising, hiring, product, growth, culture, strategy, founder-mental-models, technical). All `specs/{format}/` directories (mcp, openai, hermes). `data/`, `docs/`, `scripts/`, `config/`, `src/forge/prompts/`, `src/migrations/`, `tests/fixtures/`.
>
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `LICENSE`.
>
> **Rules:** Follow `AGENTS.md` strictly. Follow the architecture doc Section 2 exactly. All `__init__.py` files should be empty (no code). Use `.gitkeep` for empty non-Python directories. Do not write any production logic. Do not invent directories not in the architecture.
>
> **Self-review before completion:** Verify every directory from architecture doc Section 2 exists. Verify all Python packages have `__init__.py`. Stop after completing ONLY this task.

---

### Task M1-T2: Dependency Manifest & Project Config

| Field | Value |
|-------|-------|
| **Task ID** | `M1-T2` |
| **Title** | Create requirements.txt, pyproject.toml, .env.example |
| **Goal** | Define all project dependencies with exact pinned versions and configure development tools. |
| **Files to Create** | `requirements.txt`, `pyproject.toml`, `.env.example` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, existing `__init__.py` files |
| **Dependencies** | `M1-T1` |
| **Inputs** | Architecture doc Section 3 (technology stack), AGENTS.md Section 6 (type checking) |
| **Outputs** | Installable dependency manifest, project metadata, env template |
| **Acceptance Criteria** | `pip install -r requirements.txt` succeeds. `pyproject.toml` contains ruff, mypy, pytest, pydantic-mypy configs. `.env.example` contains all 4 provider key placeholders + GITHUB_TOKEN + pipeline config. |
| **Required Tests** | None (config task) |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M1-T2 for the YC Skills Forge project.
>
> **Objective:** Create `requirements.txt` with exact pinned versions from architecture doc Section 3. Create `pyproject.toml` with project metadata and tool configurations for ruff, mypy (with pydantic plugin), and pytest. Create `.env.example` with placeholder API keys.
>
> **requirements.txt must include:** requests==2.32.x, beautifulsoup4==4.12.x, yt-dlp==2025.x, pydantic==2.9.x, PyYAML==6.0.x, sentence-transformers==2.7.x, rapidfuzz==3.9.x, openai==1.40.x, Jinja2==3.1.x, pytest==8.3.x, ruff==0.6.x, markdownify==0.13.x, scikit-learn (pin to latest stable), mypy==1.11.x, pytest-cov. Pin to exact minor versions (e.g., `requests==2.32.3`). Use the latest patch for each minor.
>
> **pyproject.toml must include:** [tool.mypy] with strict=true, plugins=["pydantic.mypy"]; [tool.pydantic-mypy] with init_forbid_extra=true, init_typed=true; [tool.ruff] target-version="py311"; [tool.pytest.ini_options] with testpaths=["tests"].
>
> **.env.example must include:** DEEPSEEK_API_KEY, KIMI_API_KEY, GLM_API_KEY, GEMINI_API_KEY, GITHUB_TOKEN, BATCH_SIZE, DEFAULT_TEMPERATURE, MAX_RETRIES — all with placeholder values.
>
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, any `__init__.py`.
>
> **Rules:** Follow `AGENTS.md` Section 12 (Dependency Policy) strictly. No version ranges — exact pins only. Stop after completing ONLY this task.

---

### Task M1-T3: Git Configuration

| Field | Value |
|-------|-------|
| **Task ID** | `M1-T3` |
| **Title** | Create .gitignore |
| **Goal** | Ensure all gitignored paths from the architecture doc are excluded. |
| **Files to Create** | `.gitignore` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md` |
| **Dependencies** | `M1-T1` |
| **Inputs** | Architecture doc Section 2 (committed vs. gitignored) |
| **Outputs** | `.gitignore` with all required exclusions |
| **Acceptance Criteria** | `.gitignore` excludes: `data/raw/`, `data/chunks/`, `data/registry.db`, `data/errors/`, `.env`, `.venv/`, `__pycache__/`, `*.pyc`, `.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`. Does NOT exclude: `data/similarity_matrix.json`, `skills/`, `specs/`, `skills-index.json`. |
| **Required Tests** | None (config task) |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M1-T3 for the YC Skills Forge project.
>
> **Objective:** Create `.gitignore` that excludes exactly the paths specified in the architecture doc Section 2 (committed vs. gitignored). Also exclude standard Python artifacts.
>
> **Must exclude:** `data/raw/`, `data/chunks/`, `data/registry.db`, `data/errors/`, `.env`, `.venv/`, `__pycache__/`, `*.pyc`, `.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`, `*.egg-info/`, `dist/`, `build/`.
>
> **Must NOT exclude:** `data/similarity_matrix.json`, `skills/`, `specs/`, `skills-index.json`, `config/`, `src/`, `docs/`, `scripts/`.
>
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`.
>
> **Rules:** Follow `AGENTS.md` Section 17 (Completion Checklist — Git section). Stop after completing ONLY this task.

---

### M1 Review Task

| Field | Value |
|-------|-------|
| **Task ID** | `M1-R` |
| **Title** | Milestone 1 Review — Project Scaffolding |
| **Goal** | Verify scaffolding is complete and correct before proceeding. |

**Verification Checklist:**
- [x] Every directory from architecture doc Section 2 exists
- [x] All Python packages have `__init__.py`
- [x] All 8 skill categories have directories under `skills/`
- [x] `requirements.txt` pins exact versions for all dependencies in architecture doc Section 3
- [x] `pip install -r requirements.txt` succeeds in a clean Python 3.11 venv
- [x] `pyproject.toml` contains ruff, mypy, pytest configurations
- [x] `.gitignore` excludes correct paths
- [x] `.env.example` contains all required placeholders
- [x] `ruff check src/` passes
- [x] No production logic has been written
- [x] No files outside the architecture doc have been created

---

## Milestone 2 — Core Data Layer

**Objective:** Build Layer 1 (Data) — Pydantic models, configuration loader, database schema, and the `init-db` CLI command.

**Deliverables:**
- `src/models.py` with all Pydantic models
- `src/config.py` with Pydantic settings loader
- `config/taxonomy.yml`, `config/providers.yml`, `config/pipeline.yml`
- `src/migrations/001_init.sql` with complete SQLite schema
- Minimal `src/cli.py` with `init-db` subcommand
- Tests for models and config

**Exit Criteria:**
- All Pydantic models validate known-good and reject known-bad inputs
- `python -m src.cli init-db` creates `data/registry.db` with correct schema
- Config loader reads all 3 YAML files
- `ruff check src/` and `python -m pytest` pass

---

### Task M2-T1: Pydantic Data Models

| Field | Value |
|-------|-------|
| **Task ID** | `M2-T1` |
| **Title** | Implement all Pydantic models |
| **Goal** | Create every domain model specified in the architecture doc Sections 4, 8, and 10. |
| **Files to Create** | `src/models.py`, `tests/test_models.py` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `config/` |
| **Dependencies** | `M1-T2` (needs pydantic installed) |
| **Inputs** | Architecture doc Sections 4.1 (schema), 8 (extraction/synthesis response schemas), 10.2 (SkillFrontmatter) |
| **Outputs** | `src/models.py` with all models, `tests/test_models.py` with validation tests |
| **Acceptance Criteria** | Models include: `ProvenanceSource`, `Provenance`, `Validation`, `SkillFrontmatter`, `ExtractedItem`, `ExtractionResponse`, `Contradiction`, `SynthesisResponse`, `ClusterInfo`, `ChunkData`, `ContentRecord`, `UsageLogEntry`. Skill ID regex `^yc-[a-z]+(-[a-z]+){1,6}$` is enforced. Version regex `^\d+\.\d+\.\d+$` is enforced. All `Field()` constraints match the architecture doc. Tests cover valid inputs, invalid inputs, boundary cases. |
| **Required Tests** | `tests/test_models.py` — min 15 test cases covering valid/invalid skill IDs, version strings, confidence bounds (0.0–1.0), source_count ≥ 1, quote_count ≥ 1, tag constraints. |
| **Estimated Complexity** | M |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M2-T1 for the YC Skills Forge project.
>
> **Objective:** Create `src/models.py` containing all Pydantic v2 data models for the project. Create `tests/test_models.py` with comprehensive validation tests.
>
> **Models to implement (from architecture doc Sections 4.1, 8, 10.2):**
> - `ProvenanceSource` — content_id, title, speaker (optional), designation (optional), url (HttpUrl), contribution
> - `Provenance` — batch_id, pipeline_run_date (datetime), github_run_url (optional), sources (list)
> - `Validation` — quote_verified (bool), schema_valid (bool), hallucination_check (bool), human_review (bool)
> - `SkillFrontmatter` — skill_id (pattern `^yc-[a-z]+(-[a-z]+){1,6}$`), name (max_length=100), version (pattern `^\d+\.\d+\.\d+$`, default="1.0.0"), category, tags (1–10 items), source_count (ge=1), quote_count (ge=1), related_skills (list, default empty), confidence (0.0–1.0), provenance, validation
> - `ExtractedItem` — in_batch_index (int), quote, speaker, designation (optional), source_id, source_url, timestamp (optional), topic, type (framework/warning/advice/story), context, is_partial (bool)
> - `ExtractionResponse` — extracted_items (list), contradictions (list)
> - `Contradiction` — topic, in_batch_indices (list[int]), summary
> - `SynthesisResponse` — skill_id, name, category, principle, quotes (list), application (dict), edge_cases (list), related_skills (list), confidence (float)
> - `ChunkData` — chunk_id, content_id, chunk_index (int), text, word_count (int), char_count (int), speaker (optional), timestamp_start (optional), timestamp_end (optional)
> - `ContentRecord` — content_id, source_type, url, title, speaker (optional), designation (optional), state, topic_guess (optional)
> - `UsageLogEntry` — provider, model, batch_id (optional), prompt_tokens (int), completion_tokens (int), total_tokens (int), cost_estimate_usd (optional float), call_type, timestamp, success (bool), error_message (optional)
>
> **Constraints:** Use Pydantic v2. Use `Field()` with constraints everywhere. Every public class needs a docstring. No imports from Layer 2 or Layer 3. Follow `AGENTS.md` Section 5 (Coding Standards).
>
> **Tests must cover:** Valid skill IDs, invalid skill IDs (too many words, uppercase, no prefix), valid/invalid versions, confidence bounds, tag list length bounds, source_count/quote_count minimum enforcement, extraction response parsing, synthesis response parsing.
>
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `config/`.
>
> **Self-review:** Run `ruff check src/models.py` and `python -m pytest tests/test_models.py`. Stop after completing ONLY this task.

---

### Task M2-T2: Configuration Loader & YAML Files

| Field | Value |
|-------|-------|
| **Task ID** | `M2-T2` |
| **Title** | Implement config loader and all YAML configuration files |
| **Goal** | Create `src/config.py` with Pydantic settings classes and all 3 config YAML files. |
| **Files to Create** | `src/config.py`, `config/taxonomy.yml`, `config/providers.yml`, `config/pipeline.yml`, `tests/test_config.py` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py` |
| **Dependencies** | `M2-T1` |
| **Inputs** | Architecture doc Sections 6.1 (taxonomy), 9.1 (providers), Appendix C.3 (pipeline) |
| **Outputs** | Config loader and YAML files |
| **Acceptance Criteria** | `config/taxonomy.yml` matches architecture doc Section 6.1 exactly (8 categories, all subcategories). `config/providers.yml` matches Section 9.1 exactly (4 providers with `${VAR}` substitution). `config/pipeline.yml` matches Appendix C.3 exactly. `src/config.py` can load all 3 files and expose typed settings via Pydantic. Environment variable substitution works for provider API keys. |
| **Required Tests** | `tests/test_config.py` — config loading, taxonomy parsing, provider config with env var substitution (mocked), pipeline parameter access. Min 8 test cases. |
| **Estimated Complexity** | M |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M2-T2 for the YC Skills Forge project.
>
> **Objective:** Create `src/config.py` (Pydantic settings loader for all YAML config files), `config/taxonomy.yml` (exact topic tree from architecture doc Section 6.1), `config/providers.yml` (LLM provider configs from Section 9.1), `config/pipeline.yml` (chunking/clustering/validation parameters from Appendix C.3). Create `tests/test_config.py`.
>
> **`src/config.py` requirements:** Pydantic BaseSettings or custom loader classes. Must load all 3 YAML files. Must perform `${VAR}` substitution for environment variables in `providers.yml`. Must expose typed access to taxonomy categories, provider configs, and pipeline parameters. Must be importable by Layer 2 modules (`from src.config import ...`). No imports from Layer 2 or Layer 3.
>
> **YAML file contents:** Copy the exact structures from architecture doc Section 6.1 (taxonomy), Section 9.1 (providers), and Appendix C.3 (pipeline). Do not invent or modify any values.
>
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`.
>
> **Rules:** Follow `AGENTS.md` Section 5 (Configuration). All thresholds and parameters live in YAML files, not hardcoded in Python. Use `logging` module for any log output.
>
> **Self-review:** Run `ruff check src/config.py` and `python -m pytest tests/test_config.py`. Stop after completing ONLY this task.

---

### Task M2-T3: Database Schema & Migration

| Field | Value |
|-------|-------|
| **Task ID** | `M2-T3` |
| **Title** | Create SQLite schema migration file |
| **Goal** | Create the exact SQL schema from architecture doc Section 4.1. |
| **Files to Create** | `src/migrations/001_init.sql` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`, `src/config.py` |
| **Dependencies** | `M1-T1` |
| **Inputs** | Architecture doc Section 4.1 (exact SQL schema) |
| **Outputs** | SQL file that creates all 7 tables with correct columns, types, constraints, and indices |
| **Acceptance Criteria** | SQL contains CREATE TABLE statements for: `content`, `chunks`, `extracted_items`, `clusters`, `cluster_items`, `skills`, `usage_log`. All CHECK constraints match the architecture doc. All indices match. Column names use `chunk_index` (not `index`), `in_batch_index`, `computed_confidence`, `avg_similarity`. State enum includes `extracting` and `linked`. |
| **Required Tests** | None (SQL file — tested in M2-T4) |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M2-T3 for the YC Skills Forge project.
>
> **Objective:** Create `src/migrations/001_init.sql` containing the exact SQLite schema from architecture doc Section 4.1. Copy the SQL verbatim. Do not add, remove, or rename any columns.
>
> **Critical details:** The `content.state` CHECK constraint must include ALL states: 'discovered', 'downloaded', 'chunked', 'extracting', 'extracted', 'clustered', 'synthesized', 'linked', 'validated', 'published', 'failed'. Use `chunk_index` not `index`. Include `in_batch_index` in `extracted_items`. Include `computed_confidence` and `avg_similarity`. Include all CREATE INDEX statements.
>
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`, `src/config.py`.
>
> **Self-review:** Verify every table, column, constraint, and index matches Section 4.1 exactly. Stop after completing ONLY this task.

---

### Task M2-T4: CLI Scaffold & init-db Command

| Field | Value |
|-------|-------|
| **Task ID** | `M2-T4` |
| **Title** | Create CLI scaffold with init-db command |
| **Goal** | Create the minimal CLI entry point and the `init-db` subcommand that initializes the SQLite database. |
| **Files to Create** | `src/cli.py`, `src/__main__.py` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`, `src/config.py`, `src/migrations/001_init.sql` |
| **Dependencies** | `M2-T3` |
| **Inputs** | Architecture doc Section 16.4 (CLI commands), `src/migrations/001_init.sql` |
| **Outputs** | Working `python -m src.cli init-db` command |
| **Acceptance Criteria** | `python -m src.cli --help` shows available commands. `python -m src.cli init-db` creates `data/registry.db` by executing `src/migrations/001_init.sql`. Running `init-db` twice is idempotent (uses `CREATE TABLE IF NOT EXISTS` or checks for existing DB). CLI uses `argparse` or equivalent. Uses `logging` module, not `print()`. |
| **Required Tests** | Smoke test: `init-db` creates the database with correct tables (use in-memory SQLite in test). Min 3 test cases. |
| **Estimated Complexity** | M |
| **Estimated AI Sessions** | 2 |

**Execution Prompt:**

> You are implementing Task M2-T4 for the YC Skills Forge project.
>
> **Objective:** Create `src/cli.py` as the single CLI entry point using `argparse` (with subcommands). Implement the `init-db` subcommand that reads `src/migrations/001_init.sql` and executes it against `data/registry.db`. Create `src/__main__.py` to enable `python -m src.cli`.
>
> **`src/cli.py` requirements:** Use `argparse` with subparsers. The `init-db` command takes no arguments. It creates `data/` directory if missing, then runs the SQL migration. Use `logging` module for output. Handle the case where the DB already exists (idempotent). CLI is Layer 3 — it may import from Layer 1 and Layer 2.
>
> **`src/__main__.py`:** Simple entry point: `from src.cli import main; main()`.
>
> **Do NOT implement other CLI commands yet.** Leave stubs/comments for future commands but only implement `init-db`.
>
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`, `src/config.py`, `src/migrations/001_init.sql`.
>
> **Rules:** Follow `AGENTS.md` Sections 4 (layering), 5 (no print, use logging). No bare `Exception`. Use parameterized SQL.
>
> **Self-review:** Run `python -m src.cli init-db`, verify `data/registry.db` is created with all 7 tables. Run `ruff check src/cli.py`. Stop after completing ONLY this task.

---

### M2 Review Task

| Field | Value |
|-------|-------|
| **Task ID** | `M2-R` |
| **Title** | Milestone 2 Review — Core Data Layer |

**Verification Checklist:**
- [x] `src/models.py` contains all Pydantic models from the architecture doc
- [x] Skill ID regex `^yc-[a-z]+(-[a-z]+){1,6}$` is enforced
- [x] `src/config.py` loads all 3 YAML files with env var substitution
- [x] `config/taxonomy.yml` matches architecture doc Section 6.1 exactly
- [x] `config/providers.yml` matches architecture doc Section 9.1 exactly
- [x] `config/pipeline.yml` matches architecture doc Appendix C.3 exactly
- [x] `src/migrations/001_init.sql` matches architecture doc Section 4.1 exactly
- [x] `python -m src.cli init-db` works and is idempotent
- [x] `python -m pytest` passes all model and config tests
- [x] `ruff check src/` passes
- [x] No Layer 1 module imports from Layer 2 or Layer 3
- [x] All public functions have docstrings

---

## Milestone 3 — Content Ingestion

**Objective:** Build the ingestion layer that scrapes YC Library essays and downloads YouTube transcripts.

**Deliverables:**
- `src/ingest/library_scraper.py`
- `src/ingest/known_authors.py`
- `src/ingest/youtube_downloader.py`
- CLI commands: `ingest-library`, `ingest-youtube`
- Tests with mocked HTTP responses

**Exit Criteria:**
- Library scraper correctly extracts essay content and saves to `data/raw/library/`
- YouTube downloader correctly invokes `yt-dlp` and saves metadata/transcripts
- Content IDs use SHA256 of URL (library) and video ID (YouTube)
- Scraping respects rate limits (`time.sleep(2)`)
- All tests pass with mocked HTTP

---

### Task M3-T1: Known Authors Mapping

| Field | Value |
|-------|-------|
| **Task ID** | `M3-T1` |
| **Title** | Create known authors lookup |
| **Goal** | Create the hardcoded mapping of known YC authors for speaker identification. |
| **Files to Create** | `src/ingest/known_authors.py` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`, `src/config.py`, `src/cli.py` |
| **Dependencies** | `M1-T1` |
| **Inputs** | Architecture doc Section 5.1 (speaker extraction) |
| **Outputs** | Module with author → designation mapping |
| **Acceptance Criteria** | Contains at least: Paul Graham → "Founder of YC", Sam Altman → "Former President of YC", Michael Seibel → "Partner at YC", Garry Tan → "CEO of YC", Jessica Livingston → "Founding Partner of YC", Dalton Caldwell → "Managing Director of YC", Kevin Hale → "Partner at YC". Provides a `lookup_author(url: str) -> tuple[str | None, str | None]` function. |
| **Required Tests** | None (simple data module — tested via scraper tests) |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M3-T1 for the YC Skills Forge project.
>
> **Objective:** Create `src/ingest/known_authors.py` containing a hardcoded mapping of known YC authors/speakers to their designations, and a `lookup_author(url: str) -> tuple[str | None, str | None]` function that checks URL paths for known authors.
>
> **Authors to include:** Paul Graham (Founder of YC), Sam Altman (Former President of YC), Michael Seibel (Partner at YC), Garry Tan (CEO of YC), Jessica Livingston (Founding Partner of YC), Dalton Caldwell (Managing Director of YC), Kevin Hale (Partner at YC), Gustaf Alstromer (Partner at YC), Anu Hariharan (Partner at YC). Add any other well-known YC partners you are confident about.
>
> **Files you must NOT modify:** Any existing files.
>
> **Rules:** Follow `AGENTS.md`. Docstrings on all public functions. No imports from Layer 2 or Layer 3. Stop after completing ONLY this task.

---

### Task M3-T2: Library Scraper

| Field | Value |
|-------|-------|
| **Task ID** | `M3-T2` |
| **Title** | Implement YC Library essay scraper |
| **Goal** | Create the scraper that downloads and processes YC Library essays. |
| **Files to Create** | `src/ingest/library_scraper.py`, `tests/ingest/test_library_scraper.py` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`, `src/cli.py` |
| **Dependencies** | `M2-T1` (models), `M2-T2` (config), `M2-T4` (database), `M3-T1` (known_authors) |
| **Inputs** | Architecture doc Section 5.1 |
| **Outputs** | Working library scraper with tests |
| **Acceptance Criteria** | Accepts URL list. Downloads with `requests`, timeout=30s, User-Agent per spec. Parses with BeautifulSoup4, removes nav/footer/script/style/aside. Converts to Markdown with `markdownify`. Saves to `data/raw/library/{content_id}.md`. Computes SHA256 content hash. Generates content_id as `lib_{sha256(url)[:12]}`. Inserts into `content` table. Sets state to `downloaded` (or `discovered` if speaker is NULL). Rate-limits with `time.sleep(2)`. Uses speaker extraction with known_authors fallback. |
| **Required Tests** | `tests/ingest/test_library_scraper.py` — mock HTTP responses, verify content ID generation, verify SHA256 hashing, verify speaker extraction, verify rate limiting. Min 6 test cases. |
| **Estimated Complexity** | M |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M3-T2 for the YC Skills Forge project.
>
> **Objective:** Create `src/ingest/library_scraper.py` implementing the exact scraping behavior from architecture doc Section 5.1. Create `tests/ingest/test_library_scraper.py` with mocked HTTP responses.
>
> **Implementation details:** Accept a list of URLs. For each URL: HTTP GET with `requests`, timeout=30s, User-Agent: `YC-Skills-Forge/1.0 (Research Project; contact@example.com)`. Parse with BS4, extract `<article>` or `<main>` content (fallback: `<div class="content">`). Remove `<nav>`, `<footer>`, `<script>`, `<style>`, `<aside>`, ads, newsletter boxes. Convert to Markdown with `markdownify`. Save to `data/raw/library/{content_id}.md`. Compute SHA256 of Markdown text. Generate content_id: `lib_{sha256(url)[:12]}`. Insert into `content` table with state `downloaded`. If speaker is NULL after extraction → set state `discovered`. Rate-limit: `time.sleep(2)` between requests. Use `src/ingest/known_authors.py` for speaker fallback. URL deduplication: skip if URL already in `content` table.
>
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`, `src/cli.py`.
>
> **Rules:** Follow `AGENTS.md` Sections 5, 8. Use parameterized SQL. Use `logging` module. Mock all HTTP calls in tests. No bare `Exception`. Stop after completing ONLY this task.

---

### Task M3-T3: YouTube Downloader

| Field | Value |
|-------|-------|
| **Task ID** | `M3-T3` |
| **Title** | Implement YouTube transcript downloader |
| **Goal** | Create the downloader that uses `yt-dlp` to fetch captions and metadata. |
| **Files to Create** | `src/ingest/youtube_downloader.py`, `tests/ingest/test_youtube_downloader.py` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`, `src/cli.py` |
| **Dependencies** | `M2-T1`, `M2-T2`, `M2-T4` |
| **Inputs** | Architecture doc Section 5.2 |
| **Outputs** | Working YouTube downloader with tests |
| **Acceptance Criteria** | Accepts video URLs. Invokes `yt-dlp` via `subprocess.run()` with exact flags: `--write-subs`, `--sub-langs en`, `--sub-format json3`, `--skip-download`, `--write-info-json`, `--output`, timeout=300. Reads `{video_id}.info.json` for title, uploader, upload_date. Reads subtitle file for transcript segments. Converts to plain text with timestamps. Speaker guessing from description via regex. Saves transcript as `{video_id}.transcript.txt`, metadata as `{video_id}.meta.json`. Generates content_id: `yt_{video_id}`. Inserts into `content` table. Sets state `downloaded` or `discovered` (if speaker is NULL). |
| **Required Tests** | `tests/ingest/test_youtube_downloader.py` — mock `subprocess.run`, verify content ID generation, verify speaker regex extraction, verify file outputs. Min 5 test cases. |
| **Estimated Complexity** | M |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M3-T3 for the YC Skills Forge project.
>
> **Objective:** Create `src/ingest/youtube_downloader.py` implementing the exact behavior from architecture doc Section 5.2. Create `tests/ingest/test_youtube_downloader.py`.
>
> **Exact `yt-dlp` command:** `["yt-dlp", "--write-subs", "--sub-langs", "en", "--sub-format", "json3", "--skip-download", "--write-info-json", "--output", f"{output_dir}/%(id)s", video_url]`. Use `subprocess.run(cmd, check=True, timeout=300)`.
>
> **Post-processing:** Read `.info.json` for title, uploader, upload_date, description (first 500 chars). Read subtitle file for transcript segments. Convert to plain text with timestamps. Speaker guessing from description: regex `with ([A-Z][a-z]+ [A-Z][a-z]+)` or `([A-Z][a-z]+ [A-Z][a-z]+), (CEO|Founder|Partner|...)`. If zero matches → speaker=NULL, state=`discovered`. Save transcript and metadata files. Insert into `content` table.
>
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`, `src/cli.py`.
>
> **Rules:** Follow `AGENTS.md`. Use `subprocess.run()` (not async). Use `logging`. Mock subprocess in tests. Stop after completing ONLY this task.

---

### Task M3-T4: Ingestion CLI Commands

| Field | Value |
|-------|-------|
| **Task ID** | `M3-T4` |
| **Title** | Add ingest-library and ingest-youtube CLI commands |
| **Goal** | Wire the ingestion modules into the CLI. |
| **Files to Create** | None |
| **Files to Modify** | `src/cli.py` |
| **Files NOT to Modify** | `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`, `src/config.py`, `src/ingest/*.py` |
| **Dependencies** | `M3-T2`, `M3-T3` |
| **Inputs** | Architecture doc Section 16.4 |
| **Outputs** | Working `ingest-library --url <url>` and `ingest-youtube --url <url>` CLI commands |
| **Acceptance Criteria** | `python -m src.cli ingest-library --url <url>` calls the library scraper. `python -m src.cli ingest-youtube --url <url>` calls the YouTube downloader. Both accept `--urls url1 url2` for multiple URLs. Error messages are clear. `--help` works. |
| **Required Tests** | CLI smoke tests (help output, argument parsing). Min 2 test cases. |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M3-T4 for the YC Skills Forge project.
>
> **Objective:** Add `ingest-library` and `ingest-youtube` subcommands to `src/cli.py`.
>
> **`ingest-library`:** Accepts `--url <url>` (single URL) or `--urls url1 url2 ...` (multiple). Calls `library_scraper` functions. Logs results.
>
> **`ingest-youtube`:** Accepts `--url <url>` (single URL) or `--urls url1 url2 ...` (multiple). Calls `youtube_downloader` functions. Logs results.
>
> **Files you may modify:** `src/cli.py` ONLY.
>
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`, `src/config.py`, `src/ingest/*.py`.
>
> **Rules:** CLI is Layer 3 — may import from Layer 2 (ingest) and Layer 1 (models, config). Use `logging`. Handle errors gracefully. Stop after completing ONLY this task.

---

### M3 Review Task

| Field | Value |
|-------|-------|
| **Task ID** | `M3-R` |
| **Title** | Milestone 3 Review — Content Ingestion |

**Verification Checklist:**
- [x] Library scraper downloads and parses HTML correctly (tested with mocks)
- [x] Content IDs use `lib_{sha256(url)[:12]}` (not slug)
- [x] YouTube downloader uses exact `yt-dlp` command flags from architecture doc
- [x] Rate limiting: `time.sleep(2)` between scraping requests
- [x] User-Agent: `YC-Skills-Forge/1.0 (Research Project; contact@example.com)`
- [x] Speaker extraction with `known_authors.py` fallback
- [x] NULL speaker → state `discovered` (not `downloaded`)
- [x] URL deduplication enforced
- [x] CLI commands `ingest-library` and `ingest-youtube` work
- [x] All SQL uses parameterized queries
- [x] `python -m pytest` passes
- [x] `ruff check src/` passes

---

## Milestone 4 — Content Chunking

**Objective:** Build the chunking layer that splits raw content into sized chunks.

**Deliverables:**
- `src/chunker/essay_chunker.py`
- `src/chunker/transcript_chunker.py`
- CLI command: `chunk`
- Tests with sample content

**Exit Criteria:**
- Essay chunker respects 200–800 word bounds with overlap
- Transcript chunker groups by speaker and respects 400–800 word bounds
- Chunk IDs follow `{content_id}_{chunk_index:04d}` format
- Chunks are saved to `data/chunks/` as JSON and inserted into `chunks` table

---

### Task M4-T1: Essay Chunker

| Field | Value |
|-------|-------|
| **Task ID** | `M4-T1` |
| **Title** | Implement essay chunking algorithm |
| **Goal** | Create the essay chunker that splits Markdown essays into sized chunks. |
| **Files to Create** | `src/chunker/essay_chunker.py`, `tests/chunker/test_essay_chunker.py`, `tests/fixtures/sample_essay.md` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`, `src/cli.py` |
| **Dependencies** | `M2-T1`, `M2-T2` |
| **Inputs** | Architecture doc Section 7.1 |
| **Outputs** | Working essay chunker with tests |
| **Acceptance Criteria** | Splits by `## ` headers. Merges sections < 200 words with next. Splits sections > 800 words by paragraphs into 400–600 word sub-chunks. Overlap: includes last sentence of previous chunk at start of next. Records chunk_index (0-based), text, word_count, char_count, speaker, timestamp_start=NULL, timestamp_end=NULL. Saves JSON files to `data/chunks/library/`. Uses `chunk_index` naming (not `index`). |
| **Required Tests** | Tests with sample essay fixture: verify chunk count, word count bounds, overlap, chunk_index sequencing, JSON output format. Min 6 test cases. |
| **Estimated Complexity** | M |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M4-T1 for the YC Skills Forge project.
>
> **Objective:** Create `src/chunker/essay_chunker.py` implementing the exact algorithm from architecture doc Section 7.1. Create a sample essay fixture and tests.
>
> **Algorithm (exact):** 1) Read Markdown file. 2) Split by `## ` headers. 3) Each header section = candidate chunk. 4) If candidate < 200 words → merge with next until ≥ 200. 5) If candidate > 800 words → split by paragraphs (`\n\n`) into 400–600 word sub-chunks. 6) Overlap: include last sentence of previous chunk at start of next. 7) For each chunk record: chunk_index (sequential from 0), text, word_count (`len(text.split())`), char_count (`len(text)`), speaker (from content table), timestamp_start=NULL, timestamp_end=NULL.
>
> **Save format:** JSON files at `data/chunks/library/{content_id}_{chunk_index:04d}.json`. Also insert into `chunks` table. Parameters from `config/pipeline.yml`.
>
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`, `src/cli.py`.
>
> **Rules:** Follow `AGENTS.md`. Read chunking parameters from config, not hardcoded. Use `chunk_index` not `index`. Stop after completing ONLY this task.

---

### Task M4-T2: Transcript Chunker

| Field | Value |
|-------|-------|
| **Task ID** | `M4-T2` |
| **Title** | Implement transcript chunking algorithm |
| **Goal** | Create the transcript chunker that splits video transcripts into sized chunks. |
| **Files to Create** | `src/chunker/transcript_chunker.py`, `tests/chunker/test_transcript_chunker.py`, `tests/fixtures/sample_transcript.json` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`, `src/cli.py` |
| **Dependencies** | `M2-T1`, `M2-T2` |
| **Inputs** | Architecture doc Section 7.2 |
| **Outputs** | Working transcript chunker with tests |
| **Acceptance Criteria** | Reads JSON3 transcript or VTT. Groups by speaker labels. Merges consecutive same-speaker segments until 400–800 words. Splits monologues > 800 words at nearest sentence boundary after 600 words. Records chunk_index, text, word_count, char_count, speaker, timestamp_start (HH:MM:SS), timestamp_end. Saves JSON to `data/chunks/youtube/`. |
| **Required Tests** | Tests with sample transcript fixture: verify speaker grouping, word count bounds, timestamp preservation, chunk_index sequencing. Min 5 test cases. |
| **Estimated Complexity** | M |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M4-T2 for the YC Skills Forge project.
>
> **Objective:** Create `src/chunker/transcript_chunker.py` implementing the exact algorithm from architecture doc Section 7.2. Create a sample transcript fixture and tests.
>
> **Algorithm (exact):** 1) Read JSON3 transcript or VTT. 2) Group segments by speaker if labels exist. 3) Merge consecutive segments from same speaker until 400–800 words. 4) If monologue > 800 words → split at nearest sentence boundary after 600 words. 5) Record: chunk_index (sequential from 0), text, word_count, char_count, speaker, timestamp_start (HH:MM:SS of first segment), timestamp_end (HH:MM:SS of last segment).
>
> **Save format:** JSON files at `data/chunks/youtube/{content_id}_{chunk_index:04d}.json`. Also insert into `chunks` table.
>
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`, `src/cli.py`.
>
> **Rules:** Follow `AGENTS.md`. Parameters from config. Use `chunk_index`. Stop after completing ONLY this task.

---

### Task M4-T3: Chunk CLI Command

| Field | Value |
|-------|-------|
| **Task ID** | `M4-T3` |
| **Title** | Add chunk CLI command |
| **Goal** | Wire the chunking modules into the CLI. |
| **Files to Create** | None |
| **Files to Modify** | `src/cli.py` |
| **Files NOT to Modify** | `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/chunker/*.py`, `src/models.py` |
| **Dependencies** | `M4-T1`, `M4-T2` |
| **Inputs** | Architecture doc Section 16.4 |
| **Outputs** | Working `python -m src.cli chunk --all` command |
| **Acceptance Criteria** | `python -m src.cli chunk --all` chunks all content with state `downloaded`. Updates content state to `chunked` after successful chunking. Handles both library and YouTube content types. Logs progress. |
| **Required Tests** | CLI smoke test. Min 1 test case. |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M4-T3 for the YC Skills Forge project.
>
> **Objective:** Add the `chunk` subcommand to `src/cli.py`. It should accept `--all` flag to chunk all content with state `downloaded`. Route to essay_chunker for library content and transcript_chunker for YouTube content. Update content state to `chunked` after successful chunking.
>
> **Files you may modify:** `src/cli.py` ONLY.
>
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/chunker/*.py`, `src/models.py`.
>
> **Rules:** Follow `AGENTS.md`. State transition: `downloaded` → `chunked`. Stop after completing ONLY this task.

---

### M4 Review Task

| Field | Value |
|-------|-------|
| **Task ID** | `M4-R` |
| **Title** | Milestone 4 Review — Content Chunking |

**Verification Checklist:**
- [x] Essay chunker splits by `## ` headers
- [x] Word count bounds: essays 200–800, transcripts 400–800
- [x] Overlap: last sentence of previous chunk at start of next (essays)
- [x] Chunk IDs follow `{content_id}_{chunk_index:04d}` format
- [x] Uses `chunk_index` not `index`
- [x] Chunks saved as JSON to `data/chunks/{source_type}/`
- [x] Chunks inserted into `chunks` table
- [x] Content state transitions `downloaded` → `chunked`
- [x] Parameters read from `config/pipeline.yml`
- [x] `python -m pytest` passes
- [x] `ruff check src/` passes

---

## Milestone 5 — Forge Foundation

**Objective:** Build the shared infrastructure for the forge pipeline: LLM client, prompt templates, batch selector, and reaper.

**Deliverables:**
- `src/forge/llm_client.py` — unified LLM client with provider rotation
- `src/forge/prompts/extract.j2` and `src/forge/prompts/synthesize.j2`
- `src/forge/batcher.py` — batch selection logic
- Reaper logic and CLI command
- Tests with mocked LLM calls

**Exit Criteria:**
- LLM client rotates providers by priority with quota awareness
- Prompt templates render correctly with Jinja2
- Batcher selects correct items and transitions state to `extracting`
- Reaper resets stale `extracting` states

---

### Task M5-T1: LLM Client with Provider Rotation

| Field | Value |
|-------|-------|
| **Task ID** | `M5-T1` |
| **Title** | Implement unified LLM client with quota-aware provider rotation |
| **Goal** | Create the `LLMClient` class that manages provider rotation and usage logging. |
| **Files to Create** | `src/forge/llm_client.py`, `tests/forge/test_llm_client.py` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`, `src/cli.py` |
| **Dependencies** | `M2-T2` (config), `M2-T4` (database for usage_log) |
| **Inputs** | Architecture doc Section 9.2 |
| **Outputs** | Working LLM client with tests |
| **Acceptance Criteria** | `LLMClient.__init__` loads provider config from `config/providers.yml`. `get_provider(estimated_tokens)` selects by priority + remaining quota with 10% buffer. `call(prompt, call_type, temperature)` makes the LLM call via `openai.OpenAI()` with correct base_url, model, timeout. Logs usage to `usage_log` table (success and failure). Supports `response_format={"type": "json_object"}` with fallback. Handles provider exhaustion with clear error message. Handles retries for transient errors. |
| **Required Tests** | Mock `openai.OpenAI`. Test provider selection by priority, quota exhaustion fallback, usage logging, retry on timeout. Min 8 test cases. |
| **Estimated Complexity** | L |
| **Estimated AI Sessions** | 2 |

**Execution Prompt:**

> You are implementing Task M5-T1 for the YC Skills Forge project.
>
> **Objective:** Create `src/forge/llm_client.py` implementing the exact `LLMClient` class from architecture doc Section 9.2. This is the ONLY module that may `import openai`. Create tests.
>
> **Implementation:** `__init__` loads from `config/providers.yml`. `get_provider(estimated_tokens)` queries `usage_log` for today's usage per provider, computes remaining quota with 10% buffer, sorts by (priority, -remaining), returns best candidate. Raises `RuntimeError("All providers exhausted...")` if none available. `call(prompt, call_type, temperature=0.3)` creates `openai.OpenAI(api_key, base_url, timeout)`, calls `chat.completions.create`, logs to `usage_log`, returns response content. Use `response_format={"type": "json_object"}` where supported, fall back to prompt-based JSON extraction. Retry up to `max_retries` (from provider config) on transient errors (HTTP 429, timeouts). On JSON parse failure: retry once with `temperature=0.1`, then fail. Log raw error responses to `data/errors/`.
>
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`, `src/cli.py`.
>
> **Rules:** This is the ONLY place `import openai` is allowed. Follow `AGENTS.md` Section 5 (LLM Interaction Patterns). Never hardcode API keys. Use `logging`. Stop after completing ONLY this task.

---

### Task M5-T2: Prompt Templates

| Field | Value |
|-------|-------|
| **Task ID** | `M5-T2` |
| **Title** | Create Jinja2 prompt templates for extraction and synthesis |
| **Goal** | Create the exact prompt templates specified in the architecture doc. |
| **Files to Create** | `src/forge/prompts/extract.j2`, `src/forge/prompts/synthesize.j2`, `src/forge/prompts/validate.j2` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/forge/llm_client.py` |
| **Dependencies** | `M1-T1` (directory exists) |
| **Inputs** | Architecture doc Sections 8 (Stage 1, Stage 3), Section 20 (Appendix A) |
| **Outputs** | Three Jinja2 template files |
| **Acceptance Criteria** | `extract.j2` matches architecture doc Section 8, Stage 1 prompt exactly. `synthesize.j2` matches Section 8, Stage 3 prompt exactly. `validate.j2` matches Section 20, Appendix A.3 exactly. Template variables are consistent with Pydantic models. |
| **Required Tests** | None (template rendering tested via extractor/synthesizer tests) |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M5-T2 for the YC Skills Forge project.
>
> **Objective:** Create the exact Jinja2 prompt templates from the architecture doc. Copy the templates verbatim from the architecture spec — do not modify, improve, or paraphrase them.
>
> **`src/forge/prompts/extract.j2`:** Copy from architecture doc Section 8, Stage 1 (the extraction prompt template). Ensure template variables (`chunks`, `topics`, `loop.index`) are correct Jinja2 syntax.
>
> **`src/forge/prompts/synthesize.j2`:** Copy from architecture doc Section 8, Stage 3 (the synthesis prompt template). Ensure template variables (`topic`, `items`, `avg_similarity`) are correct.
>
> **`src/forge/prompts/validate.j2`:** Copy from architecture doc Section 20, Appendix A.3 (the validation/hallucination guard prompt). Ensure template variables (`quotes`, `principle`, `application`) are correct.
>
> **Files you must NOT modify:** Any Python files, `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`.
>
> **Rules:** Follow `AGENTS.md` Section 5 (Prompt Templates). Never build prompts via string concatenation. Stop after completing ONLY this task.

---

### Task M5-T3: Batch Selector

| Field | Value |
|-------|-------|
| **Task ID** | `M5-T3` |
| **Title** | Implement batch selection logic |
| **Goal** | Create the batcher that selects content items for processing. |
| **Files to Create** | `src/forge/batcher.py`, `tests/forge/test_batcher.py` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/forge/llm_client.py`, `src/cli.py` |
| **Dependencies** | `M2-T1`, `M2-T4` |
| **Inputs** | Architecture doc Section 8, Stage 0 |
| **Outputs** | Working batcher with tests |
| **Acceptance Criteria** | Queries `content` table for items with `state = 'chunked'`. Filters by `--topic` if provided. Selects topic with most unprocessed chunks if no topic specified. Randomly selects up to `batch_size` items. Aborts if fewer than 5 items available. Updates state to `extracting`. Returns `batch_id` (UUID4) and list of `content_id`s. |
| **Required Tests** | Test with in-memory SQLite: batch size enforcement (5 min, 20 max), topic filtering, state transition to `extracting`, abort on < 5 items. Min 5 test cases. |
| **Estimated Complexity** | M |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M5-T3 for the YC Skills Forge project.
>
> **Objective:** Create `src/forge/batcher.py` implementing batch selection from architecture doc Section 8, Stage 0. Create tests.
>
> **Algorithm:** 1) Query `content` for `state = 'chunked'`. 2) Filter by topic if `--topic` provided. 3) If no topic → pick topic with most unprocessed chunks. 4) Randomly select up to `batch_size` items (default 15, max 20). 5) If < 5 items → log warning, abort. 6) Set state → `extracting`, update `last_processed`. 7) Return `batch_id` (UUID4) and `content_id` list.
>
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/forge/llm_client.py`, `src/cli.py`.
>
> **Rules:** Follow `AGENTS.md`. Parameterized SQL. Atomic transaction. Stop after completing ONLY this task.

---

### Task M5-T4: Reaper Logic & CLI Command

| Field | Value |
|-------|-------|
| **Task ID** | `M5-T4` |
| **Title** | Implement reaper for stale extracting states |
| **Goal** | Create the reaper that recovers items stuck in `extracting` state. |
| **Files to Create** | `src/forge/reaper.py`, `tests/forge/test_reaper.py` |
| **Files to Modify** | `src/cli.py` |
| **Files NOT to Modify** | `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/forge/batcher.py` |
| **Dependencies** | `M2-T4`, `M5-T3` |
| **Inputs** | Architecture doc Section 8, Stage 0 (recovery from crashes) |
| **Outputs** | Working reaper logic + `python -m src.cli reaper` command |
| **Acceptance Criteria** | Finds items with `state = 'extracting'` and `last_processed < now() - 2 hours`. Resets their state to `chunked`. Increments `retry_count`. If `retry_count > 3` → marks `failed`. Logs all actions. CLI `reaper` command invokes this logic. |
| **Required Tests** | Test stale detection (mock timestamps), state reset, retry count increment, failure on retry > 3. Min 4 test cases. |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M5-T4 for the YC Skills Forge project.
>
> **Objective:** Create `src/forge/reaper.py` that recovers stale `extracting` items (architecture doc Section 8, Stage 0 — recovery). Add `reaper` subcommand to `src/cli.py`.
>
> **Logic:** Find items where `state = 'extracting'` AND `last_processed < now() - 2 hours`. Reset state → `chunked`, increment `retry_count`. If `retry_count > 3` → mark `failed`. Log each recovered item.
>
> **Files you may modify:** `src/cli.py` (add reaper subcommand).
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/forge/batcher.py`.
>
> **Rules:** Follow `AGENTS.md`. Parameterized SQL. Stop after completing ONLY this task.

---

### M5 Review Task

| Field | Value |
|-------|-------|
| **Task ID** | `M5-R` |
| **Title** | Milestone 5 Review — Forge Foundation |

**Verification Checklist:**
- [x] `LLMClient` is the ONLY module with `import openai`
- [x] Provider rotation follows priority order with quota awareness
- [x] Usage logged to `usage_log` table on every call (success and failure)
- [x] Prompt templates match architecture doc verbatim
- [x] Batcher enforces min batch size 5, max 20
- [x] Batcher transitions state `chunked` → `extracting`
- [x] Reaper recovers items after 2 hours, fails after 3 retries
- [x] No API keys hardcoded anywhere
- [x] All tests pass with mocked LLM calls
- [x] `ruff check src/` passes

---

## Milestone 6 — Forge Extraction

**Objective:** Build the extraction stage that uses an LLM to extract advice from content chunks.

**Deliverables:**
- `src/forge/extractor.py`
- Tests with fixture LLM responses

**Exit Criteria:**
- Extraction renders the Jinja2 prompt correctly
- LLM response is parsed into `ExtractedItem` models
- Items are inserted into `extracted_items` table
- Content state transitions `extracting` → `extracted`

---

### Task M6-T1: Extraction Logic

| Field | Value |
|-------|-------|
| **Task ID** | `M6-T1` |
| **Title** | Implement advice extraction pipeline |
| **Goal** | Create the extractor that makes one LLM call per batch and parses the response. |
| **Files to Create** | `src/forge/extractor.py`, `tests/forge/test_extractor.py`, `tests/fixtures/extraction_response.json` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `src/forge/llm_client.py`, `src/forge/prompts/extract.j2` |
| **Dependencies** | `M5-T1` (LLM client), `M5-T2` (prompt templates), `M5-T3` (batcher) |
| **Inputs** | Architecture doc Section 8, Stage 1 |
| **Outputs** | Working extractor with tests |
| **Acceptance Criteria** | Loads chunks for the batch content IDs from `chunks` table. Renders `extract.j2` with Jinja2. Calls LLM via `LLMClient.call()` with `call_type='extract'`, `temperature=0.3`. Parses JSON response with Pydantic `ExtractionResponse`. Maps `in_batch_index` to `chunk_id`, generates UUID4 `item_id`. Inserts into `extracted_items` table with `in_batch_index` preserved. Updates content state → `extracted` only after successful insertion. Handles JSON parse failures (log to `data/errors/`, retry with `temperature=0.1`). |
| **Required Tests** | Test with fixture response: parsing, DB insertion, state transition, error handling on malformed JSON. Min 6 test cases. |
| **Estimated Complexity** | L |
| **Estimated AI Sessions** | 2 |

**Execution Prompt:**

> You are implementing Task M6-T1 for the YC Skills Forge project.
>
> **Objective:** Create `src/forge/extractor.py` implementing architecture doc Section 8, Stage 1. Create a fixture LLM response and tests.
>
> **Processing flow:** 1) Load chunks for batch content IDs from `chunks` table. 2) Render `src/forge/prompts/extract.j2` with Jinja2 (pass chunks, topics from taxonomy). 3) Call `LLMClient.call(prompt, call_type='extract', temperature=0.3)`. 4) Parse JSON response with Pydantic `ExtractionResponse`. 5) Map `in_batch_index` to `chunk_id`, generate UUID4 `item_id`. 6) Insert into `extracted_items` table. 7) Update content state → `extracted`. 8) On JSON parse failure → log to `data/errors/{batch_id}.json`, retry with `temperature=0.1`.
>
> **Files you must NOT modify:** `AGENTS.md`, `src/forge/llm_client.py`, `src/forge/prompts/extract.j2`.
>
> **Rules:** Follow `AGENTS.md`. Use `LLMClient` (not direct openai). Atomic transactions. Never hardcode temperatures — read from config. Stop after completing ONLY this task.

---

### Task M6-T2: Forge CLI Command (Partial)

| Field | Value |
|-------|-------|
| **Task ID** | `M6-T2` |
| **Title** | Add forge CLI command (extraction only, to be extended later) |
| **Goal** | Wire batch selection + extraction into a single `forge` CLI command. |
| **Files to Modify** | `src/cli.py` |
| **Files NOT to Modify** | `AGENTS.md`, `src/forge/extractor.py`, `src/forge/batcher.py` |
| **Dependencies** | `M6-T1` |
| **Inputs** | Architecture doc Section 16.4 |
| **Outputs** | `python -m src.cli forge --topic <topic> --batch-size 15` runs batch selection + extraction |
| **Acceptance Criteria** | `forge` command accepts `--topic` (optional) and `--batch-size` (default 15). Calls batcher then extractor. Logs batch_id and results. Will be extended in M7 and M8 to include clustering, synthesis, and linking. |
| **Required Tests** | CLI smoke test. Min 1 test case. |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M6-T2 for the YC Skills Forge project.
>
> **Objective:** Add the `forge` subcommand to `src/cli.py`. Currently it should run batch selection + extraction only. It will be extended in later milestones.
>
> **`forge` command:** Accepts `--topic` (optional string) and `--batch-size` (int, default 15). Calls `batcher.select_batch()`, then `extractor.extract()` with the returned batch. Logs batch_id and summary.
>
> **Files you may modify:** `src/cli.py` ONLY.
> **Files you must NOT modify:** `AGENTS.md`, `src/forge/extractor.py`, `src/forge/batcher.py`.
>
> **Rules:** Follow `AGENTS.md`. Stop after completing ONLY this task.

---

### M6 Review Task

| Field | Value |
|-------|-------|
| **Task ID** | `M6-R` |
| **Title** | Milestone 6 Review — Forge Extraction |

**Verification Checklist:**
- [x] Extractor renders Jinja2 template (not f-string construction)
- [x] `in_batch_index` is preserved in `extracted_items` table
- [x] State transition: `extracting` → `extracted` (only after successful insertion)
- [x] JSON parse failures logged to `data/errors/` and retried with `temperature=0.1`
- [x] LLM called via `LLMClient`, not direct `openai`
- [x] `forge` CLI command works with `--topic` and `--batch-size`
- [x] All tests pass with mocked LLM
- [x] `ruff check src/` passes

---

## Milestone 7 — Forge Clustering

**Objective:** Build the clustering stage using local embeddings (no LLM).

**Deliverables:**
- `src/forge/clusterer.py`
- Tests with fixture embeddings

**Exit Criteria:**
- Uses `sentence-transformers` `all-MiniLM-L6-v2` for embeddings
- Uses `AgglomerativeClustering` with exact parameters from architecture doc
- Rejects clusters with < 2 items (escape hatch after 3 retries)
- Computes `avg_similarity` for each cluster

---

### Task M7-T1: Clustering Logic

| Field | Value |
|-------|-------|
| **Task ID** | `M7-T1` |
| **Title** | Implement clustering with embeddings and agglomerative clustering |
| **Goal** | Create the clusterer that groups extracted items by semantic similarity. |
| **Files to Create** | `src/forge/clusterer.py`, `tests/forge/test_clusterer.py` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `src/forge/llm_client.py`, `src/forge/extractor.py` |
| **Dependencies** | `M6-T1` (extracted_items exist), `M2-T2` (config) |
| **Inputs** | Architecture doc Section 8, Stage 2 |
| **Outputs** | Working clusterer with tests |
| **Acceptance Criteria** | Loads `sentence-transformers` model `all-MiniLM-L6-v2`. Embeds each `quote` text. Uses `AgglomerativeClustering(n_clusters=None, distance_threshold=0.18, metric='cosine', linkage='average')`. For each cluster: selects longest quote as `representative_quote`, computes `avg_similarity`, generates summary. Inserts into `clusters` and `cluster_items` tables. Rejects clusters with < 2 items (items return to pool). Escape hatch: after 3 retries → force singleton cluster with `computed_confidence = 0.55`, `human_review: true`. State → `clustered`. |
| **Required Tests** | Test with small fixture embeddings (or actual small model run): verify cluster formation, rejection of singletons, avg_similarity computation, escape hatch. Min 5 test cases. |
| **Estimated Complexity** | L |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M7-T1 for the YC Skills Forge project.
>
> **Objective:** Create `src/forge/clusterer.py` implementing the exact clustering algorithm from architecture doc Section 8, Stage 2. No LLM calls — pure local computation. Create tests.
>
> **Algorithm:** 1) Load `sentence-transformers` model `all-MiniLM-L6-v2`. 2) Embed each quote: `model.encode(quotes, convert_to_tensor=True)`. 3) Compute cosine similarity matrix. 4) `AgglomerativeClustering(n_clusters=None, distance_threshold=0.18, metric='cosine', linkage='average')`. 5) For each cluster: longest quote = `representative_quote`, compute `avg_similarity` (average pairwise cosine similarity), generate summary. 6) Insert into `clusters` and `cluster_items` tables. 7) Reject clusters with < 2 items. 8) Escape hatch: if item rejected ≥ 3 times → force singleton with `computed_confidence = 0.55`, `human_review: true`. 9) State → `clustered`.
>
> **`sentence-transformers` import is ONLY allowed in this module**, `src/forge/linker.py`, and `src/retrieval/resolver.py`.
>
> **Files you must NOT modify:** `AGENTS.md`, `src/forge/llm_client.py`, `src/forge/extractor.py`.
>
> **Rules:** Follow `AGENTS.md`. Parameters from `config/pipeline.yml`. Stop after completing ONLY this task.

---

### Task M7-T2: Extend Forge CLI to Include Clustering

| Field | Value |
|-------|-------|
| **Task ID** | `M7-T2` |
| **Title** | Extend forge CLI command to include clustering after extraction |
| **Goal** | Chain clustering after extraction in the forge command. |
| **Files to Modify** | `src/cli.py` |
| **Files NOT to Modify** | `AGENTS.md`, `src/forge/clusterer.py`, `src/forge/extractor.py` |
| **Dependencies** | `M7-T1` |
| **Outputs** | `forge` command now runs: batch → extract → cluster |
| **Acceptance Criteria** | `python -m src.cli forge` runs extraction then clustering. |
| **Required Tests** | None (existing CLI tests cover argument parsing) |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M7-T2. Extend the `forge` subcommand in `src/cli.py` to call the clusterer after extraction. The forge pipeline now runs: batcher → extractor → clusterer. Files you may modify: `src/cli.py` ONLY. Follow `AGENTS.md`. Stop after completing ONLY this task.

---

### M7 Review Task

| Field | Value |
|-------|-------|
| **Task ID** | `M7-R` |
| **Title** | Milestone 7 Review — Forge Clustering |

**Verification Checklist:**
- [x] No LLM calls in clusterer
- [x] Uses exact `AgglomerativeClustering` parameters from architecture doc
- [x] `sentence-transformers` import only in `clusterer.py`
- [x] Clusters with < 2 items rejected
- [x] Escape hatch after 3 retries with `computed_confidence = 0.55`
- [x] `avg_similarity` computed correctly
- [x] State transition: `extracted` → `clustered`
- [x] Tests pass
- [x] `ruff check src/` passes

---

## Milestone 8 — Forge Synthesis & Linking

**Objective:** Build the synthesis and deferred linking stages.

**Deliverables:**
- `src/forge/synthesizer.py`
- `src/forge/linker.py`
- Skill file generation in correct Markdown format
- Confidence computation from cluster metrics

**Exit Criteria:**
- Synthesizer generates correct Markdown skill files with YAML frontmatter
- Confidence is computed from cluster metrics, not LLM self-report
- `related_skills` are left empty by synthesizer
- Linker populates `related_skills` from similarity matrix
- Forge CLI runs the full pipeline

---

### Task M8-T1: Skill Synthesis

| Field | Value |
|-------|-------|
| **Task ID** | `M8-T1` |
| **Title** | Implement skill synthesis with LLM and confidence computation |
| **Goal** | Create the synthesizer that generates Markdown skill files from clusters. |
| **Files to Create** | `src/forge/synthesizer.py`, `tests/forge/test_synthesizer.py`, `tests/fixtures/synthesis_response.json` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `src/forge/llm_client.py`, `src/forge/prompts/synthesize.j2`, `src/forge/clusterer.py` |
| **Dependencies** | `M5-T1` (LLM client), `M5-T2` (prompt template), `M7-T1` (clusters exist) |
| **Inputs** | Architecture doc Section 8, Stage 3 and Section 10.1 |
| **Outputs** | Working synthesizer with tests |
| **Acceptance Criteria** | One LLM call per cluster via `LLMClient.call(call_type='synthesize', temperature=0.3)`. Renders `synthesize.j2`. Parses response with `SynthesisResponse`. Overwrites `confidence` with computed value: `min(0.99, max(0.55, (avg_similarity * 0.5) + (min(item_count, 10) / 10 * 0.3) + (0.2 if not contradictions else 0.1)))`. Overwrites `related_skills` with empty list. Generates `skill_id` from topic + descriptor, ensures uniqueness (append `_v2` if exists). Writes Markdown file matching Section 10.1 format exactly. Inserts into `skills` table with state `draft`, `related_skills = NULL`. State → `synthesized`. |
| **Required Tests** | Test with fixture response: Markdown format, confidence computation, skill_id uniqueness, frontmatter schema. Min 6 test cases. |
| **Estimated Complexity** | L |
| **Estimated AI Sessions** | 2 |

**Execution Prompt:**

> You are implementing Task M8-T1 for the YC Skills Forge project.
>
> **Objective:** Create `src/forge/synthesizer.py` implementing architecture doc Section 8, Stage 3 and Section 10.1 (skill file format). Create tests.
>
> **Critical rules:** 1) `confidence` is ALWAYS computed from cluster metrics, NEVER from LLM output. Formula: `min(0.99, max(0.55, (avg_similarity * 0.5) + (min(item_count, 10) / 10 * 0.3) + (0.2 if not contradictions else 0.1)))`. 2) `related_skills` ALWAYS set to empty list `[]` — populated later by linker. 3) Skill file Markdown format must match Section 10.1 exactly (YAML frontmatter with all fields, then sections: Principle, Verbatim Quotes, Personalized Application, Edge Cases, Related Skills, Fallback Behavior). 4) Skill ID uniqueness: append `_v2`, `_v3` if exists.
>
> **Files you must NOT modify:** `AGENTS.md`, `src/forge/llm_client.py`, `src/forge/prompts/synthesize.j2`, `src/forge/clusterer.py`.
>
> **Rules:** Follow `AGENTS.md` Section 15 (Common Pitfalls #2, #3). Stop after completing ONLY this task.

---

### Task M8-T2: Deferred Linking

| Field | Value |
|-------|-------|
| **Task ID** | `M8-T2` |
| **Title** | Implement deferred link pass for related_skills |
| **Goal** | Create the linker that populates `related_skills` from the similarity matrix. |
| **Files to Create** | `src/forge/linker.py`, `tests/forge/test_linker.py` |
| **Files to Modify** | None |
| **Files NOT to Modify** | `AGENTS.md`, `src/forge/synthesizer.py`, `src/forge/llm_client.py` |
| **Dependencies** | `M8-T1` (skills exist) |
| **Inputs** | Architecture doc Section 8, Stage 4 |
| **Outputs** | Working linker with tests |
| **Acceptance Criteria** | No LLM call. Loads newly synthesized skills. Loads or computes `data/similarity_matrix.json`. For each new skill: finds top 3 most similar existing skills (cosine similarity of embeddings). Verifies each candidate `skill_id` exists as a file. Updates skill Markdown frontmatter `related_skills`. Updates `skills` table. State → `linked`. |
| **Required Tests** | Test with fixture skills and embeddings: related skill selection, file existence verification, frontmatter update. Min 4 test cases. |
| **Estimated Complexity** | M |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M8-T2 for the YC Skills Forge project.
>
> **Objective:** Create `src/forge/linker.py` implementing architecture doc Section 8, Stage 4. No LLM call. Create tests.
>
> **Algorithm:** 1) Load newly synthesized skills. 2) Load `data/similarity_matrix.json` (or compute if first run). 3) For each new skill → embed its name+principle, find top 3 most similar existing skills by cosine similarity. 4) Verify each candidate `skill_id` exists as a file in `skills/`. 5) Update skill Markdown frontmatter `related_skills`. 6) Update `skills` table. 7) State → `linked`.
>
> **`sentence-transformers` import allowed here** (one of only 3 modules).
>
> **Files you must NOT modify:** `AGENTS.md`, `src/forge/synthesizer.py`, `src/forge/llm_client.py`.
>
> **Rules:** Follow `AGENTS.md`. `related_skills` come from similarity matrix ONLY, never LLM. Stop after completing ONLY this task.

---

### Task M8-T3: Complete Forge CLI Pipeline

| Field | Value |
|-------|-------|
| **Task ID** | `M8-T3` |
| **Title** | Extend forge CLI to run full pipeline + add link command |
| **Goal** | Complete the forge CLI to run all stages and add separate `link` command. |
| **Files to Modify** | `src/cli.py` |
| **Files NOT to Modify** | `AGENTS.md`, any `src/forge/*.py` module |
| **Dependencies** | `M8-T1`, `M8-T2` |
| **Outputs** | `forge` runs batch → extract → cluster → synthesize. `link --topic <topic>` runs linker separately. |
| **Acceptance Criteria** | `python -m src.cli forge --topic <topic> --batch-size 15` runs all 4 stages. `python -m src.cli link --topic <topic>` runs the deferred link pass independently. |
| **Required Tests** | CLI smoke tests. Min 2 test cases. |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M8-T3. Extend the `forge` subcommand in `src/cli.py` to chain: batcher → extractor → clusterer → synthesizer. Add a separate `link` subcommand that accepts `--topic` and runs the linker independently. Files you may modify: `src/cli.py` ONLY. Follow `AGENTS.md`. Stop after completing ONLY this task.

---

### Task M8-T4: Test Fixtures for Full Forge Pipeline

| Field | Value |
|-------|-------|
| **Task ID** | `M8-T4` |
| **Title** | Create golden fixture files for forge pipeline testing |
| **Goal** | Create test fixtures that enable end-to-end forge testing without live LLM calls. |
| **Files to Create** | `tests/fixtures/sample_skill.md`, `tests/fixtures/sample_frontmatter.yml`, `tests/fixtures/sample_similarity_matrix.json` |
| **Files to Modify** | None |
| **Files NOT to Modify** | All `src/` files |
| **Dependencies** | `M8-T1` |
| **Inputs** | Architecture doc Section 10.1 (skill file example), Section 13.1 (similarity matrix format) |
| **Outputs** | Golden fixture files |
| **Acceptance Criteria** | `sample_skill.md` matches the architecture doc Section 10.1 example exactly. `sample_frontmatter.yml` contains valid frontmatter that passes `SkillFrontmatter` Pydantic validation. `sample_similarity_matrix.json` matches Section 13.1 format. |
| **Required Tests** | None (fixtures used by other tests) |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M8-T4. Create golden test fixtures based on architecture doc examples. `tests/fixtures/sample_skill.md` should be the exact skill file example from Section 10.1. `tests/fixtures/sample_frontmatter.yml` should contain valid YAML frontmatter. `tests/fixtures/sample_similarity_matrix.json` should match Section 13.1 format. Do not modify any `src/` files. Stop after completing ONLY this task.

---

### M8 Review Task

| Field | Value |
|-------|-------|
| **Task ID** | `M8-R` |
| **Title** | Milestone 8 Review — Forge Synthesis & Linking |

**Verification Checklist:**
- [x] Confidence computed from cluster metrics, not LLM output
- [x] `related_skills` set to `[]` by synthesizer, populated by linker only
- [x] Skill files match Section 10.1 format exactly
- [x] Linker uses similarity matrix, not LLM
- [x] Skill ID uniqueness enforced (appends `_v2`, `_v3`)
- [x] `forge` CLI runs full pipeline: batch → extract → cluster → synthesize
- [x] `link` CLI runs deferred linking separately
- [x] State transitions: `clustered` → `synthesized` → `linked`
- [x] Golden fixtures pass Pydantic validation
- [x] All tests pass

---

## Milestone 9 — Exporters

**Objective:** Build all three spec file exporters.

**Deliverables:**
- `src/exporter/mcp_exporter.py`
- `src/exporter/openai_exporter.py`
- `src/exporter/hermes_exporter.py`
- CLI command: `export`

**Exit Criteria:**
- Each exporter generates spec files matching architecture doc Sections 11.1–11.3 exactly
- All specs include `fallback` block with `invent_quotes: false`

---

### Task M9-T1: MCP Exporter

| Field | Value |
|-------|-------|
| **Task ID** | `M9-T1` |
| **Title** | Implement MCP spec file exporter |
| **Files to Create** | `src/exporter/mcp_exporter.py`, `tests/exporter/test_mcp_exporter.py` |
| **Dependencies** | `M8-T4` (fixture skill file) |
| **Inputs** | Architecture doc Section 11.1 |
| **Acceptance Criteria** | Reads skill Markdown files, generates JSON matching Section 11.1 format. Includes `inputSchema`, `handler`, `tags`, `fallback` with `invent_quotes: false`. Saves to `specs/mcp/{skill_id}.json`. |
| **Required Tests** | Verify output JSON structure, fallback block presence, path correctness. Min 3 test cases. |
| **Estimated Complexity** | M |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M9-T1 for the YC Skills Forge project.
>
> **Objective:** Create `src/exporter/mcp_exporter.py` that reads skill Markdown files from the `skills/` directory, parses their YAML frontmatter and Markdown body, and generates MCP (Model Context Protocol) spec JSON files. Create `tests/exporter/test_mcp_exporter.py` with comprehensive tests.
>
> **Exact output JSON structure (from architecture doc Section 11.1):** Each generated file must match this template:
> ```json
> {
>   "name": "{skill_id with hyphens replaced by underscores}",
>   "description": "YC advice on {topic}. Sources: {speaker1} ({designation1}), {speaker2} ({designation2}). {summary of what the skill provides}.",
>   "inputSchema": {
>     "type": "object",
>     "properties": { ... derived from skill's Personalized Application section ... },
>     "required": [ ... ]
>   },
>   "handler": {
>     "type": "file",
>     "path": "skills/{category}/{skill_id}.md"
>   },
>   "tags": [ ... from frontmatter tags ... ],
>   "fallback": {
>     "mode": "closest_skills",
>     "count": 3,
>     "use_agent_knowledge": true,
>     "invent_quotes": false
>   }
> }
> ```
>
> **Implementation details:**
> 1. Create a function `export_mcp(skill_path: str, output_dir: str = "specs/mcp") -> str` that processes a single skill file and returns the output path.
> 2. Create a function `export_all_mcp(skills_dir: str = "skills", output_dir: str = "specs/mcp") -> list[str]` that processes all `.md` files recursively under `skills/`.
> 3. Parse YAML frontmatter using `PyYAML`. Extract `skill_id`, `name`, `category`, `tags`, and `provenance.sources` for the description.
> 4. Generate `inputSchema` properties from the skill's "When to Use This Skill" and "Follow-Up Questions" sections. Include a `question` property (type: string, required) at minimum.
> 5. The `handler.path` must be the relative path from repository root: `skills/{category}/{skill_id}.md`.
> 6. The `fallback` block is MANDATORY and must contain exactly: `mode: "closest_skills"`, `count: 3`, `use_agent_knowledge: true`, `invent_quotes: false`.
> 7. Output file: `specs/mcp/{skill_id}.json` with 2-space indented JSON.
> 8. Create `specs/mcp/` directory if it doesn't exist.
>
> **Files to create:** `src/exporter/mcp_exporter.py`, `tests/exporter/test_mcp_exporter.py`.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/forge/*.py`, `src/models.py`, `src/cli.py`.
>
> **Rules:** Follow `AGENTS.md` Sections 4 (layering — exporter is Layer 2, may import from Layer 1 only), 5 (coding standards). Use `logging` module, not `print()`. Docstrings on all public functions. No bare `Exception`. Read export formats from `config/pipeline.yml` (`export.formats` list) to verify MCP is enabled.
>
> **Tests must cover:** Valid skill file → correct JSON output structure, `fallback` block presence and exact values, `handler.path` correctness, `name` field uses underscores not hyphens, `tags` array matches frontmatter, missing frontmatter fields → graceful error. Min 3 test cases. Use the `tests/fixtures/sample_skill.md` fixture from M8-T4.
>
> **Self-review before completion:** Run `ruff check src/exporter/mcp_exporter.py` and `python -m pytest tests/exporter/test_mcp_exporter.py`. Verify the output JSON matches the architecture doc Section 11.1 example. Stop after completing ONLY this task.

---

### Task M9-T2: OpenAI Exporter

| Field | Value |
|-------|-------|
| **Task ID** | `M9-T2` |
| **Title** | Implement OpenAI function schema exporter |
| **Files to Create** | `src/exporter/openai_exporter.py`, `tests/exporter/test_openai_exporter.py` |
| **Dependencies** | `M8-T4` |
| **Inputs** | Architecture doc Section 11.2 |
| **Acceptance Criteria** | Output matches `{"type": "function", "function": {...}}` format with `metadata` block including `fallback`. Saves to `specs/openai/{skill_id}.json`. |
| **Required Tests** | Verify JSON structure, metadata block, fallback rules. Min 3 test cases. |
| **Estimated Complexity** | M |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M9-T2 for the YC Skills Forge project.
>
> **Objective:** Create `src/exporter/openai_exporter.py` that reads skill Markdown files and generates OpenAI function schema JSON files. Create `tests/exporter/test_openai_exporter.py` with comprehensive tests.
>
> **Exact output JSON structure (from architecture doc Section 11.2):** Each generated file must match this template:
> ```json
> {
>   "type": "function",
>   "function": {
>     "name": "{skill_id with hyphens replaced by underscores}",
>     "description": "YC advice on {topic}. Sources: {speaker1} ({designation1}), ...",
>     "parameters": {
>       "type": "object",
>       "properties": { ... derived from skill content ... },
>       "required": [ ... ]
>     }
>   },
>   "metadata": {
>     "skill_file": "skills/{category}/{skill_id}.md",
>     "category": "{category}",
>     "tags": [ ... from frontmatter ... ],
>     "fallback": {
>       "mode": "closest_skills",
>       "count": 3,
>       "use_agent_knowledge": true,
>       "invent_quotes": false
>     }
>   }
> }
> ```
>
> **Implementation details:**
> 1. Create a function `export_openai(skill_path: str, output_dir: str = "specs/openai") -> str` that processes a single skill file.
> 2. Create a function `export_all_openai(skills_dir: str = "skills", output_dir: str = "specs/openai") -> list[str]` that processes all skills.
> 3. The top-level object MUST have `"type": "function"` as the first key — this is the OpenAI function calling schema standard.
> 4. The `function.parameters` block mirrors the MCP `inputSchema` — generate properties from the skill's usage triggers and follow-up questions. Always include a `question` property (type: string, required).
> 5. The `metadata` block is a non-standard extension containing: `skill_file` (relative path), `category`, `tags`, and `fallback`.
> 6. The `metadata.fallback` block MUST contain exactly: `mode: "closest_skills"`, `count: 3`, `use_agent_knowledge: true`, `invent_quotes: false`.
> 7. Output file: `specs/openai/{skill_id}.json` with 2-space indented JSON.
>
> **Files to create:** `src/exporter/openai_exporter.py`, `tests/exporter/test_openai_exporter.py`.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/forge/*.py`, `src/models.py`, `src/cli.py`.
>
> **Rules:** Follow `AGENTS.md` Sections 4, 5. Layer 2 module — may import from Layer 1 only. Use `logging`, docstrings on all public functions. No bare `Exception`. Consider sharing utility functions with `mcp_exporter.py` (e.g., frontmatter parsing) via an `__init__.py` or a shared helper — but do not import from MCP exporter directly.
>
> **Tests must cover:** Valid skill file → correct JSON structure with `type: function` wrapper, `metadata.fallback` block presence and exact values, `metadata.skill_file` correctness, `function.name` uses underscores, `metadata.tags` matches frontmatter. Min 3 test cases.
>
> **Self-review before completion:** Run `ruff check src/exporter/openai_exporter.py` and `python -m pytest tests/exporter/test_openai_exporter.py`. Verify the output JSON matches the architecture doc Section 11.2 example. Stop after completing ONLY this task.

---

### Task M9-T3: Hermes Exporter

| Field | Value |
|-------|-------|
| **Task ID** | `M9-T3` |
| **Title** | Implement Hermes plain-text exporter |
| **Files to Create** | `src/exporter/hermes_exporter.py`, `tests/exporter/test_hermes_exporter.py` |
| **Dependencies** | `M8-T4` |
| **Inputs** | Architecture doc Section 11.3 |
| **Acceptance Criteria** | Output is plain text with `[SKILL: ...]` / `[END SKILL]` delimiters. Includes FALLBACK instruction: `DO NOT invent YC quotes`. Saves to `specs/hermes/{skill_id}.txt`. |
| **Required Tests** | Verify text format, delimiter presence, fallback instruction. Min 3 test cases. |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M9-T3 for the YC Skills Forge project.
>
> **Objective:** Create `src/exporter/hermes_exporter.py` that reads skill Markdown files and generates plain-text system prompt fragments for local models (llama.cpp, Ollama, etc.). Create `tests/exporter/test_hermes_exporter.py` with comprehensive tests.
>
> **Exact output text format (from architecture doc Section 11.3):** Each generated file must match this template:
> ```text
> [SKILL: {skill_id}]
> NAME: {name}
> CATEGORY: {category}
> TAGS: {comma-separated tags}
>
> PRINCIPLE: {principle text from ## Principle section}
>
> VERBATIM QUOTES:
> - "{quote1}" — {speaker1}, {designation1}
> - "{quote2}" — {speaker2}, {designation2}
> ...
>
> WHEN TO USE: {summary from ## Personalized Application > ### When to Use This Skill}
>
> AGENT PROTOCOL:
> 1. {step1}
> 2. {step2}
> ...
>
> FOLLOW-UP QUESTIONS:
> - {question1}
> - {question2}
> ...
>
> EDGE CASES:
> - {edge_case1}
> - {edge_case2}
> ...
>
> FALLBACK: If query does not match, return 3 closest skills and use general knowledge. DO NOT invent YC quotes.
>
> RELATED SKILLS: {comma-separated related_skills from frontmatter}
> [END SKILL]
> ```
>
> **Implementation details:**
> 1. Create a function `export_hermes(skill_path: str, output_dir: str = "specs/hermes") -> str` that processes a single skill file.
> 2. Create a function `export_all_hermes(skills_dir: str = "skills", output_dir: str = "specs/hermes") -> list[str]` that processes all skills.
> 3. Parse the Markdown body to extract content from each section: `## Principle`, `## Verbatim Quotes`, `## Personalized Application`, `## Edge Cases`, `## Related Skills`.
> 4. For VERBATIM QUOTES: extract blockquotes (`> "..."`) and their attribution lines (`> — **Speaker**, Designation`).
> 5. For AGENT PROTOCOL: extract the numbered steps from `### Agent Protocol` subsection.
> 6. For FOLLOW-UP QUESTIONS: extract from `### Follow-Up Questions` subsection.
> 7. The FALLBACK line is MANDATORY and must read exactly: `FALLBACK: If query does not match, return 3 closest skills and use general knowledge. DO NOT invent YC quotes.`
> 8. The `[SKILL: ...]` and `[END SKILL]` delimiters are required — they enable agents to parse skill boundaries when multiple specs are concatenated into a single system prompt.
> 9. Output file: `specs/hermes/{skill_id}.txt` (plain text, UTF-8, LF line endings).
>
> **Files to create:** `src/exporter/hermes_exporter.py`, `tests/exporter/test_hermes_exporter.py`.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/forge/*.py`, `src/models.py`, `src/cli.py`.
>
> **Rules:** Follow `AGENTS.md` Sections 4, 5. Layer 2 module. Use `logging`. Docstrings on all public functions. No bare `Exception`. The output is `.txt` not `.json` — this is the only exporter that produces non-JSON output.
>
> **Tests must cover:** Valid skill file → correct text output with all sections present, `[SKILL: ...]` / `[END SKILL]` delimiters present, FALLBACK line contains exact `DO NOT invent YC quotes` text, VERBATIM QUOTES section correctly extracts quotes and attributions, RELATED SKILLS line matches frontmatter. Min 3 test cases.
>
> **Self-review before completion:** Run `ruff check src/exporter/hermes_exporter.py` and `python -m pytest tests/exporter/test_hermes_exporter.py`. Compare a generated output file against the architecture doc Section 11.3 example line by line. Stop after completing ONLY this task.

---

### Task M9-T4: Export CLI Command

| Field | Value |
|-------|-------|
| **Task ID** | `M9-T4` |
| **Title** | Add export CLI command |
| **Files to Modify** | `src/cli.py` |
| **Dependencies** | `M9-T1`, `M9-T2`, `M9-T3` |
| **Acceptance Criteria** | `python -m src.cli export --all` generates specs in all 3 formats for all skills. |
| **Required Tests** | CLI smoke test. Min 1 test case. |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M9-T4 for the YC Skills Forge project.
>
> **Objective:** Add the `export` subcommand to `src/cli.py` that generates spec files in all three formats (MCP, OpenAI, Hermes) for skill files.
>
> **CLI interface:**
> - `python -m src.cli export --all` — export all skills in `skills/` to all 3 formats.
> - `python -m src.cli export --format mcp` — export only MCP format.
> - `python -m src.cli export --format openai` — export only OpenAI format.
> - `python -m src.cli export --format hermes` — export only Hermes format.
> - `python -m src.cli export --skill-id <id>` — export a single skill to all formats.
>
> **Implementation details:**
> 1. Add `export` subparser to the argparse CLI in `src/cli.py`.
> 2. Accept `--all` flag (boolean), `--format` (optional, choices: mcp/openai/hermes), `--skill-id` (optional string).
> 3. When `--all` is specified: scan `skills/` recursively for `.md` files, call all three exporters for each.
> 4. When `--format` is specified: call only the matching exporter.
> 5. When `--skill-id` is specified: find the skill file by ID and export only that skill.
> 6. Log summary: number of skills exported, number of spec files generated, output directories.
> 7. Import from `src/exporter/mcp_exporter`, `src/exporter/openai_exporter`, `src/exporter/hermes_exporter`.
> 8. Create output directories (`specs/mcp/`, `specs/openai/`, `specs/hermes/`) if they don't exist.
>
> **Files you may modify:** `src/cli.py` ONLY.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/exporter/*.py`, `src/models.py`.
>
> **Rules:** CLI is Layer 3 — may import from Layer 2 (exporters) and Layer 1 (models, config). Use `logging` for output. Handle errors gracefully (e.g., missing skill files, invalid frontmatter). The `--help` text should clearly explain what each flag does.
>
> **Self-review before completion:** Run `python -m src.cli export --help` and verify the help text is clear. Run `ruff check src/cli.py`. Stop after completing ONLY this task.

---

### M9 Review Task

| Field | Value |
|-------|-------|
| **Task ID** | `M9-R` |
| **Title** | Milestone 9 Review — Exporters |

**Verification Checklist:**
- [ ] MCP JSON matches architecture doc Section 11.1
- [ ] OpenAI JSON matches Section 11.2
- [ ] Hermes text matches Section 11.3
- [ ] All specs include `fallback` with `invent_quotes: false`
- [ ] `export --all` generates specs for all skill files
- [ ] No manual editing of `specs/` directory
- [ ] Tests pass

---

## Milestone 10 — Validation Suite

**Objective:** Build the three-layer validation suite.

**Deliverables:**
- `src/validator/quote_verifier.py`
- `src/validator/schema_validator.py`
- `src/validator/hallucination_guard.py`
- `src/validator/run.py` (entry point for `python -m src.validator.run`)
- CLI command: `validate`

**Exit Criteria:**
- Quote verifier uses dual fuzzy matching (ratio ≥ 70 AND partial_ratio ≥ 85)
- Schema validator uses Pydantic models
- Hallucination guard uses dedicated Gemini validator (not rotating pool)
- Failed skills are moved to `skills/_failed/`

---

### Task M10-T1: Quote Verifier

| Field | Value |
|-------|-------|
| **Task ID** | `M10-T1` |
| **Title** | Implement fuzzy quote verification |
| **Files to Create** | `src/validator/quote_verifier.py`, `tests/validator/test_quote_verifier.py` |
| **Dependencies** | `M8-T4` (fixture skill file) |
| **Inputs** | Architecture doc Section 14.1 |
| **Acceptance Criteria** | Extracts all blockquotes from skill files. Computes `rapidfuzz.fuzz.ratio` AND `rapidfuzz.fuzz.partial_ratio` against source chunks. Pass: ratio ≥ 70 AND partial_ratio ≥ 85. Warning: ratio < 70 but partial_ratio ≥ 85. Fail: partial_ratio < 70. Falls back to `data/raw/` if chunk not found. |
| **Required Tests** | Test with known-good quotes (pass), slightly modified quotes (warning), fabricated quotes (fail). Min 5 test cases. |
| **Estimated Complexity** | M |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M10-T1 for the YC Skills Forge project.
>
> **Objective:** Create `src/validator/quote_verifier.py` implementing the dual fuzzy match quote verification algorithm from architecture doc Section 14.1. Create `tests/validator/test_quote_verifier.py` with comprehensive tests.
>
> **Algorithm (exact, from architecture doc Section 14.1):**
> 1. Load a skill file and extract all blockquotes matching the pattern `> "..."` (lines starting with `>` that contain quoted text).
> 2. For each extracted quote, identify the source content_id from the skill's `provenance.sources` frontmatter.
> 3. Load the corresponding source chunks from `data/chunks/` (JSON files matching `{content_id}_*.json`).
> 4. For each quote, compute BOTH similarity scores against the chunk text:
>    - `rapidfuzz.fuzz.ratio(quote, chunk_text)` — strict, length-normalized Levenshtein similarity.
>    - `rapidfuzz.fuzz.partial_ratio(quote, chunk_text)` — lenient, finds best matching substring.
> 5. Compare each quote against ALL chunks from its source and take the BEST match.
> 6. **Decision thresholds (from `config/pipeline.yml` validation section):**
>    - `ratio >= 70` AND `partial_ratio >= 85` → **PASS** (quote is verified)
>    - `ratio < 70` BUT `partial_ratio >= 85` → **WARNING** (possible truncation or minor formatting change — flag for human review)
>    - `partial_ratio < 70` → **FAIL** (quote cannot be verified — block commit)
> 7. **Fallback:** If no chunk files exist for a source content_id, search in `data/raw/` (the full Markdown or transcript file) with the same dual fuzzy logic.
>
> **Why dual matching:** `ratio()` catches rewording that happens to share words. `partial_ratio()` catches truncation where the quote is a subset of a longer chunk. Both are needed for the exact quote fidelity constraint.
>
> **Implementation details:**
> 1. Create a class `QuoteVerifier` with `__init__(self, chunks_dir, raw_dir, config)` and `verify_skill(self, skill_path) -> QuoteVerificationResult`.
> 2. `QuoteVerificationResult` should contain: `skill_id`, `status` (pass/warning/fail), `quote_results` (list of per-quote results with quote text, best_ratio, best_partial_ratio, matched_chunk_id, status).
> 3. Read validation thresholds from `config/pipeline.yml` (`validation.quote_fuzzy_ratio: 70`, `validation.quote_fuzzy_partial_ratio: 85`) — do NOT hardcode them.
> 4. Handle edge cases: skill file with zero quotes (warning, not error), chunk directory missing (fall back to raw), quote with special characters or line breaks.
>
> **Files to create:** `src/validator/quote_verifier.py`, `tests/validator/test_quote_verifier.py`.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/forge/*.py`, `src/models.py`, `src/cli.py`.
>
> **Rules:** Follow `AGENTS.md` Sections 4 (layering — validator is Layer 2), 5 (coding standards), 8 (security — this is a trust boundary component). Use `logging`. Docstrings on all public functions. No bare `Exception`. Import `rapidfuzz` only in this module. Read thresholds from config, not hardcoded.
>
> **Tests must cover:** Known-good quote from fixture (exact match → PASS), slightly truncated quote (high partial_ratio but low ratio → WARNING), completely fabricated quote (both scores low → FAIL), quote with formatting differences (Markdown artifacts), missing chunk fallback to raw. Min 5 test cases. Use `tests/fixtures/sample_skill.md` as a fixture.
>
> **Self-review before completion:** Run `ruff check src/validator/quote_verifier.py` and `python -m pytest tests/validator/test_quote_verifier.py`. Verify threshold values match `config/pipeline.yml`. Stop after completing ONLY this task.

---

### Task M10-T2: Schema Validator

| Field | Value |
|-------|-------|
| **Task ID** | `M10-T2` |
| **Title** | Implement Pydantic schema validation for skill files |
| **Files to Create** | `src/validator/schema_validator.py`, `tests/validator/test_schema_validator.py` |
| **Dependencies** | `M2-T1` (Pydantic models), `M8-T4` (fixture skill file) |
| **Inputs** | Architecture doc Section 14.2 |
| **Acceptance Criteria** | Parses YAML frontmatter with PyYAML. Validates against `SkillFrontmatter` model. Checks skill_id matches filename. Checks related_skills all exist as files. Checks tags constraints. |
| **Required Tests** | Test with valid frontmatter, invalid skill_id, missing required fields, broken related_skills. Min 5 test cases. |
| **Estimated Complexity** | M |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M10-T2 for the YC Skills Forge project.
>
> **Objective:** Create `src/validator/schema_validator.py` implementing the Pydantic-based schema validation from architecture doc Section 14.2. Create `tests/validator/test_schema_validator.py` with comprehensive tests.
>
> **Algorithm (exact, from architecture doc Section 14.2):**
> 1. Read the skill Markdown file and extract the YAML frontmatter (content between `---` delimiters at the top of the file).
> 2. Parse the YAML with `PyYAML` (`yaml.safe_load`).
> 3. Validate the parsed YAML against the `SkillFrontmatter` Pydantic model from `src/models.py`. This enforces:
>    - `skill_id` matches regex `^yc-[a-z]+(-[a-z]+){1,6}$`
>    - `version` matches regex `^\d+\.\d+\.\d+$`
>    - `tags` has 1–10 items
>    - `source_count >= 1`, `quote_count >= 1`
>    - `confidence` is between 0.0 and 1.0
>    - `provenance` and `validation` sub-objects are valid
> 4. Check that `skill_id` matches the filename (e.g., `yc-fundraising-seed-round-timing.md` → skill_id must be `yc-fundraising-seed-round-timing`).
> 5. Check that every entry in `related_skills` exists as an actual `.md` file in the `skills/` directory tree. If a related skill ID doesn't correspond to an existing file, flag it as FAIL.
> 6. Check that all `tags` are lowercase, contain no spaces, and are max 20 characters each.
> 7. Check that `category` from frontmatter matches the parent directory name (e.g., file in `skills/fundraising/` → category must be `fundraising`).
>
> **Implementation details:**
> 1. Create a class `SchemaValidator` with `__init__(self, skills_dir, config)` and `validate_skill(self, skill_path) -> SchemaValidationResult`.
> 2. `SchemaValidationResult` should contain: `skill_id`, `status` (pass/fail), `errors` (list of validation error messages), `warnings` (list).
> 3. On Pydantic `ValidationError`: capture all error messages and return them in the result — do not raise.
> 4. Handle edge cases: malformed YAML (not valid YAML at all), missing frontmatter delimiters, empty frontmatter, filename with wrong extension.
>
> **Files to create:** `src/validator/schema_validator.py`, `tests/validator/test_schema_validator.py`.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/models.py`, `src/forge/*.py`, `src/cli.py`.
>
> **Rules:** Follow `AGENTS.md` Sections 4, 5. Layer 2 module — may import `SkillFrontmatter` from `src/models.py` (Layer 1). Use `logging`. Docstrings on all public functions. No bare `Exception`. Import Pydantic `ValidationError` for structured error handling.
>
> **Tests must cover:** Valid frontmatter from fixture → PASS, invalid skill_id (uppercase, too many words, missing yc- prefix) → FAIL with specific error, missing required fields (source_count, quote_count) → FAIL, broken related_skills (references non-existent skill) → FAIL, tags validation (uppercase tag, tag with spaces, tag > 20 chars) → FAIL, category mismatch between frontmatter and directory → FAIL, skill_id mismatch with filename → FAIL. Min 5 test cases.
>
> **Self-review before completion:** Run `ruff check src/validator/schema_validator.py` and `python -m pytest tests/validator/test_schema_validator.py`. Verify all Pydantic constraints from `src/models.py` are actually exercised by the tests. Stop after completing ONLY this task.

---

### Task M10-T3: Hallucination Guard

| Field | Value |
|-------|-------|
| **Task ID** | `M10-T3` |
| **Title** | Implement LLM-as-judge hallucination guard |
| **Files to Create** | `src/validator/hallucination_guard.py`, `tests/validator/test_hallucination_guard.py` |
| **Dependencies** | `M5-T1` (LLM client), `M5-T2` (validate.j2 template) |
| **Inputs** | Architecture doc Section 14.3 |
| **Acceptance Criteria** | Cross-references speakers against `content` table. Checks for unsupported claims (years, dollar amounts, company names not in source chunks). LLM-as-judge: uses ONLY `dedicated_validator` config (gemini-1.5-flash, temperature=0.0). If Gemini quota exhausted: skip LLM check, log warning, rely on steps 1–4 only. Does NOT fall back to another provider. Returns `{"supported": true/false}`. |
| **Required Tests** | Test speaker verification, claim checking, LLM judge (mocked), quota exhaustion fallback. Min 5 test cases. |
| **Estimated Complexity** | L |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M10-T3 for the YC Skills Forge project.
>
> **Objective:** Create `src/validator/hallucination_guard.py` implementing the multi-step hallucination detection algorithm from architecture doc Section 14.3. This is a **security-critical** component — a trust boundary between LLM-generated content and published output. Create `tests/validator/test_hallucination_guard.py` with comprehensive tests.
>
> **Algorithm (exact, from architecture doc Section 14.3):**
> 1. **Speaker Verification:** Extract all `(Name, Designation)` pairs from the skill file (from `> — **Name**, Designation` attribution lines). Cross-reference each speaker against the `content` table in `data/registry.db`. If a speaker appears in a skill but NEVER appears in the batch sources for that skill, return FAIL.
> 2. **Source Cross-Reference:** For each `content_id` in the skill's `provenance.sources`, verify it exists in the `content` table and has a non-null `speaker` field matching the attributed speaker.
> 3. **Unsupported Claims Detection:** Scan the `## Principle` and `## Personalized Application` sections for specific factual claims: years (e.g., "2022"), dollar amounts (e.g., "$1M"), company names, and percentages. For each such claim, verify it appears in at least one of the source chunks from `data/chunks/`. Flag unverified specific claims as potential hallucinations.
> 4. **LLM-as-Judge (dedicated validator, NOT rotating pool):** Send the skill's principle, application, and quotes to the LLM with the prompt from `src/forge/prompts/validate.j2`. The prompt asks: "Does the Principle or Application introduce any claims not supported by the Source Quotes?"
>
> **CRITICAL SECURITY CONSTRAINTS for LLM-as-Judge (step 4):**
> - Uses ONLY the `validation.dedicated_validator` config block from `config/providers.yml`.
> - Provider: `gemini`, Model: `gemini-1.5-flash`, Temperature: `0.0`, Max tokens: `2000`.
> - This does NOT use the rotating provider pool. Do NOT call `LLMClient.get_provider()` with the normal rotation logic.
> - Instead, create a separate method or client instance that reads only the `dedicated_validator` config and calls Gemini directly.
> - **If Gemini quota is exhausted:** SKIP the LLM-as-judge step entirely. Log a warning: `"LLM-as-judge skipped due to quota exhaustion."` Rely on steps 1–3 only. Do NOT substitute another provider. This is the `fallback_behavior: "fail_open"` strategy.
> - The LLM must return JSON: `{"supported": true/false, "issues": [...], "confidence": 0.0-1.0}`. If `supported` is `false`, the skill FAILS validation.
>
> **Implementation details:**
> 1. Create a class `HallucinationGuard` with `__init__(self, db_path, chunks_dir, config)` and `check_skill(self, skill_path) -> HallucinationCheckResult`.
> 2. `HallucinationCheckResult` should contain: `skill_id`, `status` (pass/fail/skipped), `speaker_check` (pass/fail), `claim_check` (pass/fail with flagged claims), `llm_check` (pass/fail/skipped with issues list).
> 3. Import `LLMClient` from `src/forge/llm_client.py` — this is explicitly allowed for the hallucination guard per AGENTS.md Section 4.
> 4. Render the validation prompt using Jinja2 from `src/forge/prompts/validate.j2`.
> 5. Use parameterized SQL queries for all database access.
>
> **Files to create:** `src/validator/hallucination_guard.py`, `tests/validator/test_hallucination_guard.py`.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/forge/llm_client.py`, `src/forge/prompts/validate.j2`, `src/models.py`, `src/cli.py`.
>
> **Rules:** Follow `AGENTS.md` Sections 4 (layering — hallucination_guard is the ONLY validator module allowed to import `LLMClient`), 5 (coding standards), 8 (security). This is a TRUST BOUNDARY — the hallucination guard is the last line of defense before publishing. Use `logging`. Docstrings. No bare `Exception`. Parameterized SQL.
>
> **Tests must cover:** Valid skill with matching speakers → speaker check PASS, skill with unknown speaker not in batch sources → FAIL, skill with unsupported year claim → claim check FAIL, mocked LLM returning `{"supported": true}` → PASS, mocked LLM returning `{"supported": false, "issues": [...]}` → FAIL, mocked Gemini quota exhaustion → LLM check SKIPPED (but steps 1-3 still run), verify the guard does NOT fall back to another provider. Min 5 test cases.
>
> **Self-review before completion:** Run `ruff check src/validator/hallucination_guard.py` and `python -m pytest tests/validator/test_hallucination_guard.py`. Verify the dedicated_validator config is read correctly from `config/providers.yml`. Verify NO fallback to other providers occurs. Stop after completing ONLY this task.

---

### Task M10-T4: Validator Runner

| Field | Value |
|-------|-------|
| **Task ID** | `M10-T4` |
| **Title** | Create validator runner entry point |
| **Files to Create** | `src/validator/run.py` |
| **Dependencies** | `M10-T1`, `M10-T2`, `M10-T3` |
| **Acceptance Criteria** | `python -m src.validator.run --all` runs all 3 validators against all skill files. Reports pass/warn/fail per skill. Moves failed skills to `skills/_failed/`. Creates `skills/_failed/` if it doesn't exist. Returns exit code 0 if all pass, 1 if any fail. |
| **Required Tests** | None (integration — tested by validators) |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M10-T4 for the YC Skills Forge project.
>
> **Objective:** Create `src/validator/run.py` as the unified entry point that orchestrates all three validators. This file must be runnable as `python -m src.validator.run --all`.
>
> **Implementation details:**
> 1. Create a `main()` function that accepts CLI arguments via `argparse`.
> 2. Accept `--all` flag (validate all skills in `skills/`) and `--skill-id <id>` (validate a single skill).
> 3. For each skill file being validated, run all three validators IN ORDER:
>    a. **Schema validation** (fast, no IO beyond file read) — run first to catch malformed files early.
>    b. **Quote verification** (requires `data/chunks/` access) — run second.
>    c. **Hallucination guard** (requires DB access and potentially LLM call) — run last (most expensive).
> 4. If any validator returns FAIL for a skill: set the skill's state to `failed` in the `skills` DB table, move the file to `skills/_failed/{skill_id}.md`. Create the `skills/_failed/` directory if it doesn't exist.
> 5. Print a summary table to stdout (via logging) showing each skill and its validation status:
>    ```
>    Skill ID                              | Schema | Quotes | Hallucination | Result
>    yc-fundraising-seed-round-timing      | PASS   | PASS   | PASS          | ✓ PASS
>    yc-hiring-first-engineer              | PASS   | WARN   | SKIP          | ⚠ WARNING
>    yc-product-mvp-scope                  | FAIL   | -      | -             | ✗ FAIL
>    ```
> 6. Return exit code 0 if ALL skills pass (warnings are OK), exit code 1 if ANY skill fails.
> 7. Add `if __name__ == "__main__":` block so the file is runnable as a module.
>
> **Files to create:** `src/validator/run.py`.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/validator/quote_verifier.py`, `src/validator/schema_validator.py`, `src/validator/hallucination_guard.py`, `src/cli.py`.
>
> **Rules:** Follow `AGENTS.md` Sections 4, 5. This is a Layer 2 module that orchestrates other Layer 2 modules (validators). Use `logging` for output. Use `shutil.move()` for moving failed files. Handle the case where `skills/` is empty gracefully. Parameterized SQL for DB state updates.
>
> **Self-review before completion:** Run `ruff check src/validator/run.py`. Verify `python -m src.validator.run --help` shows correct usage. Stop after completing ONLY this task.

---

### Task M10-T5: Validate CLI Command

| Field | Value |
|-------|-------|
| **Task ID** | `M10-T5` |
| **Title** | Add validate CLI command |
| **Files to Modify** | `src/cli.py` |
| **Dependencies** | `M10-T4` |
| **Acceptance Criteria** | `python -m src.cli validate --all` invokes the validator runner. |
| **Required Tests** | CLI smoke test. |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M10-T5 for the YC Skills Forge project.
>
> **Objective:** Add the `validate` subcommand to the CLI entry point at `src/cli.py`.
>
> **CLI interface:**
> - `python -m src.cli validate --all` — validates all skill files in `skills/` using all 3 validators.
> - `python -m src.cli validate --skill-id <id>` — validates a single skill.
>
> **Implementation details:**
> 1. Add `validate` subparser to the argparse CLI.
> 2. Accept `--all` flag (boolean) and `--skill-id` (optional string). At least one must be provided.
> 3. Import and call `src/validator/run.py`'s main validation function, passing the arguments through.
> 4. Propagate the exit code from the validator runner — if validation fails, the CLI should exit with code 1.
> 5. Add clear `--help` text: "Validate skill files against the three-layer validation suite (schema, quotes, hallucination guard)."
>
> **Files you may modify:** `src/cli.py` ONLY.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/validator/*.py`, `src/models.py`.
>
> **Rules:** CLI is Layer 3 — may import from Layer 2 (validator) and Layer 1. Use `logging`. Handle the case where `--all` and `--skill-id` are both missing with a clear error message.
>
> **Self-review before completion:** Run `python -m src.cli validate --help` and verify the help text. Run `ruff check src/cli.py`. Stop after completing ONLY this task.

---

### M10 Review Task

| Field | Value |
|-------|-------|
| **Task ID** | `M10-R` |
| **Title** | Milestone 10 Review — Validation Suite |

**Verification Checklist:**
- [ ] Quote verifier uses BOTH `ratio ≥ 70` AND `partial_ratio ≥ 85`
- [ ] Schema validator uses Pydantic `SkillFrontmatter` model
- [ ] Hallucination guard uses dedicated validator config ONLY
- [ ] Hallucination guard skips (not falls back) on quota exhaustion
- [ ] Failed skills moved to `skills/_failed/`
- [ ] `validate --all` returns correct exit code
- [ ] No cross-stage imports in validator modules (except `LLMClient` for hallucination guard, which is explicitly allowed)
- [ ] All tests pass

---

## Milestone 11 — Retrieval & Indexing

**Objective:** Build the build-time-only retrieval system.

**Deliverables:**
- `src/retrieval/resolver.py`
- `skills-index.json` generation
- `data/similarity_matrix.json` generation
- CLI command: `index`

**Exit Criteria:**
- Resolver generates correct index and similarity matrix
- Signal resolution works for all prefix types (`/`, `%`, `yc-`, fuzzy)
- This module is build-time only — never imported by end-user code

---

### Task M11-T1: Signal Resolver & Index Generation

| Field | Value |
|-------|-------|
| **Task ID** | `M11-T1` |
| **Title** | Implement signal resolver and index/matrix generator |
| **Files to Create** | `src/retrieval/resolver.py`, `tests/retrieval/test_resolver.py` |
| **Dependencies** | `M8-T4` (fixture skills) |
| **Inputs** | Architecture doc Sections 12.2, 13.1 |
| **Acceptance Criteria** | `SignalResolver` class with `resolve(query)` method. Supports: exact skill ID lookup, `/` category filter, `%` tag filter (AND logic), fuzzy embedding search. `_build_index()` scans all skill files, extracts frontmatter, builds by_id, by_tag, by_category, embeddings indices. Generates `skills-index.json` and `data/similarity_matrix.json` in correct format (Section 13.1). `sentence-transformers` import allowed here. |
| **Required Tests** | Test each resolution type (exact, category, tag, fuzzy). Test index generation format. Min 6 test cases. |
| **Estimated Complexity** | L |
| **Estimated AI Sessions** | 2 |

**Execution Prompt:**

> You are implementing Task M11-T1 for the YC Skills Forge project.
>
> **Objective:** Create `src/retrieval/resolver.py` implementing the build-time-only signal resolution system from architecture doc Sections 12.2 and 13.1. This module generates `skills-index.json` (committed to repo root) and `data/similarity_matrix.json` (committed to `data/`). Create `tests/retrieval/test_resolver.py` with comprehensive tests.
>
> **CRITICAL CONSTRAINT: This module is BUILD-TIME ONLY.** End-user agents NEVER run this code. They consume the pre-computed `skills-index.json` and `data/similarity_matrix.json` as static files. No other `src/` module may import from `src/retrieval/`. This is the only module (along with `clusterer.py` and `linker.py`) allowed to import `sentence-transformers`.
>
> **`SignalResolver` class (from architecture doc Section 12.2):**
> 1. `__init__(self, skills_dir: str = "skills")` — calls `_build_index()` to pre-compute all indices.
> 2. `resolve(self, query: str) -> dict` — resolves a query using the following priority:
>    a. **Exact skill ID match:** If query starts with `yc-`, look up directly in `by_id` index. Return `{"type": "exact", "skill": skill_id, "path": path}`.
>    b. **Category filter `/`:** If query starts with `/`, strip the prefix and look up in `by_category` index. If the path is a directory, list all skills in it. Return `{"type": "category", "category": category_path, "skills": [...]}`.
>    c. **Tag filter `%`:** If query starts with `%`, split by commas, look up each tag in `by_tag` index, AND the results (intersection). Return `{"type": "tags", "tags": [...], "skills": [...]}`.
>    d. **Fuzzy embedding search (no prefix):** Embed the query with `sentence-transformers`, compute cosine similarity against all skill embeddings, return top 3. Return `{"type": "closest", "query": query, "skills": [...], "similarities": [...]}`.
> 3. `_build_index(self) -> dict` — walks `skills/` recursively, parses YAML frontmatter from each `.md` file, builds four indices: `by_id` (skill_id → path), `by_tag` (tag → [skill_ids]), `by_category` (category → [skill_ids]), `embeddings` (skill_id → embedding vector). Embeds `name + principle` text for each skill.
> 4. `_embed(self, text: str) -> list` — uses `SentenceTransformer('all-MiniLM-L6-v2').encode(text).tolist()`. Cache the model instance to avoid reloading.
> 5. `_cosine_sim(self, a: list, b: list) -> float` — manual cosine similarity computation.
>
> **`skills-index.json` generation:**
> Create a function `generate_index(skills_dir: str = "skills", output_path: str = "skills-index.json")` that writes the index to the repo root. The format should include: all skill IDs, their categories, tags, and file paths.
>
> **`data/similarity_matrix.json` generation (from architecture doc Section 13.1):**
> Create a function `generate_similarity_matrix(skills_dir: str = "skills", output_path: str = "data/similarity_matrix.json")` that writes the matrix. The exact format:
> ```json
> {
>   "version": "1.0.0",
>   "generated_at": "2026-07-12T00:00:00Z",
>   "skills": ["yc-fundraising-seed-round-timing", ...],
>   "matrix": [[1.0, 0.85, ...], [0.85, 1.0, ...], ...],
>   "tag_index": {"seed": ["yc-fundraising-seed-round-timing", ...], ...}
> }
> ```
> The matrix is an NxN cosine similarity matrix where N is the number of skills. `skills` is the ordered list of skill IDs that corresponds to matrix row/column indices. `tag_index` maps each tag to all skill IDs that have that tag.
>
> **Files to create:** `src/retrieval/resolver.py`, `tests/retrieval/test_resolver.py`.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/forge/*.py`, `src/validator/*.py`, `src/models.py`, `src/cli.py`.
>
> **Rules:** Follow `AGENTS.md` Sections 4 (layering — retrieval is Layer 2, build-time only, must NOT be imported by other Layer 2 modules), 5 (coding standards). `sentence-transformers` import is allowed in this module. Use `logging`. Docstrings on all public functions. No bare `Exception`. Cache the `SentenceTransformer` model instance to avoid reloading on every call.
>
> **Tests must cover:** Exact skill ID resolution (existing ID → exact match), category filter resolution (`/fundraising` → list of skills), tag filter resolution (`%seed,runway` → AND intersection), multi-tag filter with no matches → empty list, fuzzy embedding search → returns top 3 with similarities, `skills-index.json` output format verification, `data/similarity_matrix.json` output format verification (matrix dimensions match skill count, diagonal is 1.0, symmetric). Min 6 test cases. Use fixture skill files from M8-T4.
>
> **Self-review before completion:** Run `ruff check src/retrieval/resolver.py` and `python -m pytest tests/retrieval/test_resolver.py`. Verify no other `src/` module imports from `src/retrieval/`. Stop after completing ONLY this task.

---

### Task M11-T2: Index CLI Command

| Field | Value |
|-------|-------|
| **Task ID** | `M11-T2` |
| **Title** | Add index CLI command |
| **Files to Modify** | `src/cli.py` |
| **Dependencies** | `M11-T1` |
| **Acceptance Criteria** | `python -m src.cli index` generates `skills-index.json` and `data/similarity_matrix.json`. |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M11-T2 for the YC Skills Forge project.
>
> **Objective:** Add the `index` subcommand to the CLI entry point at `src/cli.py` that generates the pre-computed similarity index and matrix.
>
> **CLI interface:**
> - `python -m src.cli index` — generates both `skills-index.json` (repo root) and `data/similarity_matrix.json`.
>
> **Implementation details:**
> 1. Add `index` subparser to the argparse CLI. This command takes no required arguments.
> 2. Import `generate_index` and `generate_similarity_matrix` from `src/retrieval/resolver.py`.
> 3. Call both functions in sequence. Log the number of skills indexed and output file paths.
> 4. Create `data/` directory if it doesn't exist.
> 5. Add `--help` text: "Generate skills-index.json and data/similarity_matrix.json from all published skills. This is a build-time operation."
> 6. Log a warning if no skill files are found in `skills/`.
>
> **Important context:** This command MUST be run after synthesizing new skills (`forge`) and before committing. The generated files are committed to the repository. Forgetting to run `index` causes stale `related_skills` in subsequent link passes (see AGENTS.md Section 15, Common Pitfall #12).
>
> **Files you may modify:** `src/cli.py` ONLY.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/retrieval/resolver.py`, `src/models.py`.
>
> **Rules:** CLI is Layer 3 — may import from Layer 2 (retrieval) and Layer 1. Use `logging`. Note: this is the ONLY place in the CLI that imports from `src/retrieval/`.
>
> **Self-review before completion:** Run `python -m src.cli index --help` and verify the help text. Run `ruff check src/cli.py`. Stop after completing ONLY this task.

---

### M11 Review Task

| Field | Value |
|-------|-------|
| **Task ID** | `M11-R` |
| **Title** | Milestone 11 Review — Retrieval & Indexing |

**Verification Checklist:**
- [ ] `src/retrieval/` is NOT imported by any other `src/` module (build-time only)
- [ ] `skills-index.json` format matches architecture doc
- [ ] `data/similarity_matrix.json` format matches Section 13.1
- [ ] Signal resolution works for all prefix types
- [ ] `sentence-transformers` import only in allowed modules
- [ ] Tests pass

---

## Milestone 12 — CLI Assembly & Utilities

**Objective:** Complete the CLI with remaining utility commands.

**Deliverables:**
- `quota` CLI command
- `backfill` CLI command
- Final CLI review and polish

**Exit Criteria:**
- All CLI commands from architecture doc Section 16.4 are implemented
- `python -m src.cli --help` shows all commands

---

### Task M12-T1: Quota Command

| Field | Value |
|-------|-------|
| **Task ID** | `M12-T1` |
| **Title** | Implement quota CLI command |
| **Files to Modify** | `src/cli.py` |
| **Dependencies** | `M5-T1` (usage_log exists) |
| **Acceptance Criteria** | `python -m src.cli quota` displays remaining tokens/requests per provider for today. Reads from `usage_log` table and `config/providers.yml`. |
| **Required Tests** | Min 1 test case with seeded usage data. |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M12-T1 for the YC Skills Forge project.
>
> **Objective:** Add the `quota` subcommand to the CLI at `src/cli.py` that displays current LLM provider quota usage and remaining capacity.
>
> **CLI interface:**
> - `python -m src.cli quota` — displays quota usage for all providers for today (UTC).
>
> **Implementation details:**
> 1. Add `quota` subparser to the argparse CLI. This command takes no arguments.
> 2. Connect to `data/registry.db` and query the `usage_log` table for today's date (UTC: `datetime.now(timezone.utc).strftime("%Y-%m-%d")`).
> 3. For each provider, compute:
>    - Total tokens used today: `SUM(total_tokens) WHERE provider = ? AND date(timestamp) = ?`
>    - Total requests today: `COUNT(*) WHERE provider = ? AND date(timestamp) = ?`
>    - Successful calls: `COUNT(*) WHERE provider = ? AND date(timestamp) = ? AND success = 1`
>    - Failed calls: `COUNT(*) WHERE provider = ? AND date(timestamp) = ? AND success = 0`
> 4. Load provider config from `config/providers.yml` to get `daily_token_limit` and `daily_request_limit` for each provider.
> 5. Compute remaining capacity with 10% buffer (matching the `LLMClient.get_provider()` logic): `effective_remaining = (daily_limit - used) * 0.9`.
> 6. Display a formatted table:
>    ```
>    Provider    | Tokens Used  | Token Limit  | Remaining | Requests | Req Limit | Status
>    ------------|--------------|--------------|-----------|----------|-----------|-------
>    deepseek    | 45,000       | 500,000      | 409,500   | 12       | 100       | ✓ OK
>    kimi        | 0            | 1,000,000    | 900,000   | 0        | 100       | ✓ OK
>    glm         | 480,000      | 500,000      | 18,000    | 48       | 50        | ⚠ LOW
>    gemini      | 1,500,000    | 1,500,000    | 0         | 150      | 150       | ✗ EXHAUSTED
>    ```
> 7. Status thresholds: `OK` if > 20% remaining, `LOW` if 1-20% remaining, `EXHAUSTED` if 0% remaining.
> 8. After the table, display: `Quotas reset at UTC midnight. Current UTC time: {now}`.
> 9. If `data/registry.db` doesn't exist, print a helpful error: "Database not found. Run 'python -m src.cli init-db' first."
>
> **Files you may modify:** `src/cli.py` ONLY.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/forge/llm_client.py`, `src/models.py`.
>
> **Rules:** CLI is Layer 3. Use `logging` for output. Use parameterized SQL queries. Handle the case where `usage_log` is empty (first run) gracefully — show all providers with 0 usage.
>
> **Tests must cover:** Seeded `usage_log` data → correct computation of remaining quota, empty usage_log → all providers show full quota, provider with exhausted quota shows correct status. Min 1 test case with in-memory SQLite.
>
> **Self-review before completion:** Run `python -m src.cli quota --help` and verify the help text. Run `ruff check src/cli.py`. Stop after completing ONLY this task.

---

### Task M12-T2: Backfill Command

| Field | Value |
|-------|-------|
| **Task ID** | `M12-T2` |
| **Title** | Implement backfill CLI command |
| **Files to Modify** | `src/cli.py` |
| **Dependencies** | `M3-T4` (ingestion commands exist) |
| **Acceptance Criteria** | `python -m src.cli backfill --start-date 2020-01-01` ingests historical content. Accepts `--start-date` parameter. |
| **Required Tests** | CLI smoke test. |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M12-T2 for the YC Skills Forge project.
>
> **Objective:** Add the `backfill` subcommand to the CLI at `src/cli.py` that orchestrates historical content ingestion for bulk processing of YC content.
>
> **CLI interface:**
> - `python -m src.cli backfill --start-date 2020-01-01` — ingest all known YC Library essays and YouTube videos published since the given date.
> - `python -m src.cli backfill --start-date 2020-01-01 --source library` — library essays only.
> - `python -m src.cli backfill --start-date 2020-01-01 --source youtube` — YouTube videos only.
>
> **Implementation details:**
> 1. Add `backfill` subparser to the argparse CLI.
> 2. Accept `--start-date` (required, format: YYYY-MM-DD), `--source` (optional, choices: library/youtube, default: both).
> 3. For library backfill: this is a placeholder that logs the intent and suggests the user provide a list of URLs (since the YC Library doesn't have a public date-based API). Log: "Library backfill requires a URL list. Use 'ingest-library --urls' with a file of URLs."
> 4. For YouTube backfill: this is a placeholder that logs the intent and suggests using YouTube channel URLs or playlist URLs with `ingest-youtube`. Log: "YouTube backfill: use 'ingest-youtube --url <playlist_url>' for bulk ingestion."
> 5. The backfill command is primarily an orchestration wrapper — it validates the date format, logs the scope, and delegates to the existing ingest commands.
> 6. Validate that `--start-date` is a valid date and is not in the future.
> 7. Log a summary of what would be backfilled and the date range.
>
> **Files you may modify:** `src/cli.py` ONLY.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, `src/ingest/*.py`, `src/models.py`.
>
> **Rules:** CLI is Layer 3. Use `logging`. Validate date format with `datetime.strptime`. Handle invalid dates gracefully with a clear error message. The `--help` text should explain the cold-start warning from architecture doc Section 17: "Warning: A fresh clone has no registry.db history. Scope your first run to avoid duplicating existing skills."
>
> **Self-review before completion:** Run `python -m src.cli backfill --help` and verify the help text includes the cold-start warning. Run `ruff check src/cli.py`. Stop after completing ONLY this task.

---

### Task M12-T3: CLI Final Review & Polish

| Field | Value |
|-------|-------|
| **Task ID** | `M12-T3` |
| **Title** | Final CLI review — verify all commands, help text, error handling |
| **Files to Modify** | `src/cli.py` |
| **Dependencies** | All previous CLI tasks |
| **Acceptance Criteria** | `python -m src.cli --help` shows all commands: `init-db`, `ingest-library`, `ingest-youtube`, `chunk`, `forge`, `link`, `validate`, `export`, `index`, `reaper`, `quota`, `backfill`. Each command has `--help` text. Error handling is consistent. |
| **Required Tests** | Comprehensive CLI smoke tests for all commands. Min 12 test cases (1 per command). |
| **Estimated Complexity** | M |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M12-T3 for the YC Skills Forge project.
>
> **Objective:** Perform a final review and polish of `src/cli.py` to ensure all 12 CLI commands are present, correctly wired, have consistent help text, and handle errors gracefully. Create `tests/test_cli.py` with comprehensive smoke tests for every command.
>
> **Complete list of 12 required commands (from architecture doc Section 16.4):**
> 1. `init-db` — Initialize SQLite database
> 2. `ingest-library --url <url>` — Ingest a YC Library essay
> 3. `ingest-youtube --url <url>` — Ingest a YouTube video transcript
> 4. `chunk --all` — Chunk all downloaded content
> 5. `forge --topic <topic> --batch-size 15` — Run the forge pipeline
> 6. `link --topic <topic>` — Run the deferred link pass
> 7. `validate --all` — Validate all skill files
> 8. `export --all` — Export specs in all formats
> 9. `index` — Generate similarity matrix and skills-index.json
> 10. `reaper` — Reset stale extracting items
> 11. `quota` — Display provider quota usage
> 12. `backfill --start-date YYYY-MM-DD` — Historical content ingestion
>
> **Review checklist:**
> 1. Verify all 12 commands exist as subparsers.
> 2. Verify each command has a descriptive `help=` string.
> 3. Verify each command's arguments have correct types, defaults, and `help=` text.
> 4. Verify error handling is consistent: no bare `Exception`, all errors log descriptive messages.
> 5. Verify all imports follow layering rules (CLI is Layer 3 → may import Layer 2 and Layer 1).
> 6. Verify no `print()` statements — all output goes through `logging`.
> 7. Verify `python -m src.cli --help` shows all 12 commands with descriptions.
> 8. Add a top-level description to the argparse ArgumentParser: "YC Skills Forge — Static skill file generator for AI agents."
>
> **Test file `tests/test_cli.py`:**
> Write smoke tests that verify:
> 1. `python -m src.cli --help` exits with code 0 and contains all 12 command names.
> 2. Each command's `--help` exits with code 0 (no import errors).
> 3. `init-db` creates the database (with in-memory SQLite or temp dir).
> 4. Commands that require the database (forge, validate, quota, reaper) print a clear error if DB doesn't exist.
> 5. Invalid arguments (e.g., `forge --batch-size abc`) produce clear error messages.
> Min 12 test cases (1 per command for `--help` verification).
>
> **Files you may modify:** `src/cli.py`.
> **Files to create:** `tests/test_cli.py`.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, any `src/` module other than `src/cli.py`.
>
> **Rules:** Follow `AGENTS.md` Sections 4, 5, 17 (Completion Checklist). Use `subprocess.run` or `argparse` parsing in tests to verify CLI behavior. No bare `Exception`. Consistent `logging` usage.
>
> **Self-review before completion:** Run `python -m src.cli --help` and verify all 12 commands appear. Run `ruff check src/cli.py` and `python -m pytest tests/test_cli.py`. Stop after completing ONLY this task.

---

### M12 Review Task

| Field | Value |
|-------|-------|
| **Task ID** | `M12-R` |
| **Title** | Milestone 12 Review — CLI Assembly |

**Verification Checklist:**
- [ ] All 12 CLI commands present and working
- [ ] `--help` text is clear for every command
- [ ] Error handling is consistent (no bare Exception)
- [ ] CLI is Layer 3 — imports from Layer 2 and Layer 1 only
- [ ] No duplicate or conflicting subcommands

---

## Milestone 13 — CI/CD, Documentation & Integration

**Objective:** Finalize the project with CI/CD, documentation, scripts, and end-to-end validation.

**Deliverables:**
- `.github/workflows/validate.yml`
- `README.md`, `docs/CONSUMPTION.md`, `docs/BYOK.md`, `docs/TAXONOMY.md`
- `scripts/setup.sh`, `scripts/backfill.sh`
- End-to-end integration test

**Exit Criteria:**
- CI workflow validates skills on PR (never generates)
- Documentation covers consumption, BYOK, and taxonomy
- Setup script works for fresh clone
- Full pipeline can be run end-to-end on fixture data

---

### Task M13-T1: GitHub Actions Validation Workflow

| Field | Value |
|-------|-------|
| **Task ID** | `M13-T1` |
| **Title** | Create PR validation GitHub Actions workflow |
| **Files to Create** | `.github/workflows/validate.yml` |
| **Dependencies** | `M10-T4` (validator runner) |
| **Inputs** | Architecture doc Section 14.4 |
| **Acceptance Criteria** | Triggers on PR to paths `skills/**` and `specs/**`. Runs on `ubuntu-latest` with Python 3.11. Installs dependencies. Runs `python -m src.validator.run --all` and `python -m pytest tests/validator/`. Does NOT generate any skills or specs. No `schedule:` triggers. |
| **Required Tests** | None (CI config) |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M13-T1 for the YC Skills Forge project.
>
> **Objective:** Create `.github/workflows/validate.yml` — the ONLY GitHub Actions workflow for this project. It validates skill and spec files on pull requests. It NEVER generates, synthesizes, or modifies any content.
>
> **Exact YAML content (from architecture doc Section 14.4):**
> ```yaml
> name: Validate Skills
> on:
>   pull_request:
>     paths:
>       - 'skills/**'
>       - 'specs/**'
> jobs:
>   validate:
>     runs-on: ubuntu-latest
>     steps:
>       - uses: actions/checkout@v4
>       - uses: actions/setup-python@v5
>         with:
>           python-version: '3.11'
>       - run: pip install -r requirements.txt
>       - run: python -m src.validator.run --all
>       - run: python -m pytest tests/validator/
> ```
>
> **CRITICAL CONSTRAINTS (from architecture doc Section 0 and AGENTS.md Section 15, Pitfall #4):**
> 1. **No `schedule:` triggers.** The architecture explicitly forbids scheduled CI/CD. This workflow triggers on PRs only.
> 2. **No `workflow_dispatch` for generation.** While `workflow_dispatch` is acceptable for validation, NEVER add a generation step.
> 3. **No `push:` trigger to `main`.** The workflow runs on PRs only.
> 4. **Path filtering is mandatory:** The workflow ONLY runs when files under `skills/**` or `specs/**` are changed. It does NOT run on code changes to `src/`.
> 5. **The workflow runs validation and tests ONLY.** It must not: run `forge`, `export`, `index`, `link`, or any pipeline stage. It must not write to the repository. It must not generate any files.
> 6. **Python 3.11 specifically** — not 3.12 or `3.x`.
>
> **Additional best practices to include:**
> - Add `pip install --upgrade pip` before `pip install -r requirements.txt`.
> - Add a linting step: `ruff check src/` before validation.
> - Consider adding `--tb=short` to pytest for cleaner CI output.
>
> **Files to create:** `.github/workflows/validate.yml`.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, any `src/` file.
>
> **Rules:** Follow `AGENTS.md` Sections 7 (Testing), 15 (Common Pitfall #4 — no scheduled GitHub Actions). This is the ONLY workflow file allowed in `.github/workflows/`. If any other workflow exists, flag it for removal.
>
> **Self-review before completion:** Verify the YAML is valid. Verify there are NO `schedule:` triggers. Verify it only runs on PR, only on `skills/**` and `specs/**` paths. Verify it does NOT run any pipeline commands. Stop after completing ONLY this task.

---

### Task M13-T2: README & Project Documentation

| Field | Value |
|-------|-------|
| **Task ID** | `M13-T2` |
| **Title** | Create README.md with project overview and quickstart |
| **Files to Create** | `README.md` |
| **Dependencies** | `M12-T3` (all CLI commands finalized) |
| **Acceptance Criteria** | Includes: project purpose, quickstart guide, CLI command reference, architecture overview, contribution guidelines, license info. References `docs/` for detailed guides. |
| **Required Tests** | None |
| **Estimated Complexity** | M |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M13-T2 for the YC Skills Forge project.
>
> **Objective:** Create (or update) `README.md` as the primary entry point for the repository. It should give a reader complete understanding of what the project does, how to set it up, how to use it, and where to find detailed documentation.
>
> **Sections to include (in this order):**
> 1. **Project Title & Badges:** "YC Skills Forge" with brief tagline: "A static-file generator that converts Y Combinator knowledge into composable skill files for AI agents."
> 2. **Overview:** Based on architecture doc Section 1. Explain: what it does (ingests YC content, extracts advice, clusters into skills, emits static files), who it's for (AI agents — Claude, GPT, local models), what makes it different (zero-cost static files, exact quote fidelity, no runtime dependencies).
> 3. **How It Works:** Brief description of the pipeline: Discover → Download → Chunk → Extract → Cluster → Synthesize → Link → Export → Validate → Commit → Tag. Include the ASCII diagram from architecture doc Section 1.
> 4. **For AI Agent Consumers:** Link to `docs/CONSUMPTION.md`. Brief example of loading a skill. Mention all 3 spec formats (MCP, OpenAI, Hermes).
> 5. **Quickstart (Contributors):** Based on architecture doc Section 16.2. Include: prerequisites (Python 3.11+, Git, yt-dlp), setup steps (clone, venv, pip install, model download, init-db, .env), first pipeline run example.
> 6. **CLI Command Reference:** Table of all 12 commands from Section 16.4 with brief descriptions and example usage.
> 7. **Project Structure:** Simplified directory tree showing key directories and their purpose.
> 8. **Skill File Format:** Brief example of a skill file (from Section 10.1), linking to full spec.
> 9. **Contributing:** Link to `AGENTS.md` for coding agents, brief human contribution guidelines, mention PR validation workflow.
> 10. **License:** MIT for code, CC BY-SA 4.0 for generated skill content. Include the legal review note from architecture doc Section 18.4.
> 11. **Links:** `docs/CONSUMPTION.md`, `docs/BYOK.md`, `docs/TAXONOMY.md`, `AGENTS.md`.
>
> **Files to create (or update):** `README.md`.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, any `src/` file.
>
> **Rules:** Follow `AGENTS.md` Section 13 (Documentation Policy). If a `README.md` already exists with meaningful content, update it rather than overwriting. Use proper Markdown formatting with headers, code blocks, and tables. Include the cold-start warning from architecture doc Section 17 in the quickstart section. Do NOT include any API keys or credentials.
>
> **Self-review before completion:** Read the README end-to-end as if you were a new user. Verify all CLI commands match Section 16.4. Verify quickstart steps match Section 16.2. Verify license info matches Section 18.4. Stop after completing ONLY this task.

---

### Task M13-T3: Detailed Documentation

| Field | Value |
|-------|-------|
| **Task ID** | `M13-T3` |
| **Title** | Create CONSUMPTION.md, BYOK.md, TAXONOMY.md |
| **Files to Create** | `docs/CONSUMPTION.md`, `docs/BYOK.md`, `docs/TAXONOMY.md` |
| **Dependencies** | `M9-T4` (exporters), `M12-T3` (CLI) |
| **Inputs** | Architecture doc Sections 11 (specs), 17 (BYOK), 6.1 (taxonomy) |
| **Acceptance Criteria** | `CONSUMPTION.md` explains how to use skills with Claude, OpenAI, and local models. `BYOK.md` matches architecture doc Section 17 including cold-start warning. `TAXONOMY.md` documents the category tree from `config/taxonomy.yml`. |
| **Required Tests** | None |
| **Estimated Complexity** | M |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M13-T3 for the YC Skills Forge project.
>
> **Objective:** Create three detailed documentation files in `docs/`. Each document serves a different audience and must be comprehensive enough to be used without reading the architecture doc.
>
> **File 1: `docs/CONSUMPTION.md`**
> Audience: AI agent developers who want to USE the published skills.
> Content must include:
> 1. **Overview:** Skills are static Markdown files with YAML frontmatter. No runtime, no API keys, no dependencies needed.
> 2. **MCP Format (Claude Code):** How to load specs from `specs/mcp/`. Example of using a skill in Claude Code. Explain the `inputSchema`, `handler`, `tags`, and `fallback` fields. Show the exact JSON structure from architecture doc Section 11.1.
> 3. **OpenAI Format (GPT / Function Calling):** How to load specs from `specs/openai/`. Example of registering a skill as a function tool. Show the exact JSON structure from architecture doc Section 11.2. Explain the `metadata.fallback` block.
> 4. **Hermes Format (Local Models):** How to load specs from `specs/hermes/`. Example of concatenating `.txt` files into a system prompt. Show the `[SKILL: ...]` / `[END SKILL]` delimiter format from architecture doc Section 11.3.
> 5. **Fallback Behavior:** Explain the fallback protocol: return 3 closest skills, use agent's own knowledge, NEVER invent YC quotes. This is critical for agent safety.
> 6. **Signal Resolution:** How to query skills: exact ID (`yc-fundraising-...`), category filter (`/fundraising`), tag filter (`%seed,runway`), fuzzy search. Explain that resolution uses the pre-computed `skills-index.json` and `data/similarity_matrix.json`.
> 7. **skills-index.json:** How to parse and use the machine-readable index file.
>
> **File 2: `docs/BYOK.md`**
> Audience: Contributors who want to fork and generate their own skills.
> Content must match architecture doc Section 17 exactly, including:
> 1. **Fork & Setup:** Step-by-step (fork, clone, setup.sh, .env).
> 2. **Ingest New Content:** `ingest-library` and `ingest-youtube` examples.
> 3. **Run Forge:** `forge --topic <topic> --batch-size 15`, then `link --topic <topic>`.
> 4. **Validate & Export:** `validate --all`, `export --all`, `index`.
> 5. **Cold-Start Warning (CRITICAL):** `data/registry.db` is gitignored. A fresh clone has no history. Running `forge` without scoping `--topic` or `--urls` may regenerate `_v2` duplicates of existing skills. Always scope the first run.
> 6. **Quota Management:** `python -m src.cli quota` to check usage.
> 7. **Adding New Providers:** Edit `config/providers.yml` and add a new block.
> 8. **Adding New Categories:** Add to `config/taxonomy.yml`, create `skills/{category}/` directory, update `docs/TAXONOMY.md`.
>
> **File 3: `docs/TAXONOMY.md`**
> Audience: Both consumers and contributors.
> Content must document the complete category tree from `config/taxonomy.yml`:
> 1. **Overview:** Skills are organized into 8 categories, each with subcategories.
> 2. **Category Tree:** Render the full taxonomy as a readable tree with descriptions for each category and subcategory. The 8 categories are: fundraising, hiring, product, growth, culture, strategy, founder-mental-models, technical.
> 3. **How Skills Map to Categories:** Explain that `skill_id` starts with `yc-{category}-...` and files live in `skills/{category}/`.
> 4. **Adding New Categories:** Requires a PR modifying `config/taxonomy.yml`, creating the directory, and updating this doc.
>
> **Files to create:** `docs/CONSUMPTION.md`, `docs/BYOK.md`, `docs/TAXONOMY.md`.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, any `src/` file, `config/taxonomy.yml`.
>
> **Rules:** Follow `AGENTS.md` Section 13 (Documentation Policy — these docs must stay synchronized with their source files). Use proper Markdown formatting. Include code blocks for all CLI commands and JSON/YAML examples. The cold-start warning in BYOK.md is non-negotiable — it must be prominently displayed (use an admonition or bold text).
>
> **Self-review before completion:** Read each doc as if you were the target audience with no prior context. Verify all CLI commands match Section 16.4. Verify spec format examples match Sections 11.1–11.3. Verify the taxonomy matches `config/taxonomy.yml`. Stop after completing ONLY this task.

---

### Task M13-T4: Setup & Backfill Scripts

| Field | Value |
|-------|-------|
| **Task ID** | `M13-T4` |
| **Title** | Create setup.sh and backfill.sh scripts |
| **Files to Create** | `scripts/setup.sh`, `scripts/backfill.sh` |
| **Dependencies** | `M12-T3` |
| **Inputs** | Architecture doc Sections 16.2, 16.4 |
| **Acceptance Criteria** | `scripts/setup.sh` matches architecture doc Section 16.2 (clone, venv, pip install, model download, init-db, copy .env). `scripts/backfill.sh` invokes `python -m src.cli backfill`. Both are executable (`chmod +x`). |
| **Required Tests** | None (shell scripts) |
| **Estimated Complexity** | S |
| **Estimated AI Sessions** | 1 |

**Execution Prompt:**

> You are implementing Task M13-T4 for the YC Skills Forge project.
>
> **Objective:** Create two shell scripts in the `scripts/` directory. These are convenience wrappers for local development setup and historical data backfill.
>
> **File 1: `scripts/setup.sh` (exact content from architecture doc Section 16.2):**
> ```bash
> #!/bin/bash
> set -e
>
> echo "YC Skills Forge - Local Setup"
>
> # 1. Clone (skip if already in repo)
> if [ ! -d ".git" ]; then
>   git clone https://github.com/yourname/yc-skills-forge.git
>   cd yc-skills-forge
> fi
>
> # 2. Create venv
> python3.11 -m venv .venv
> source .venv/bin/activate
>
> # 3. Install dependencies
> pip install --upgrade pip
> pip install -r requirements.txt
>
> # 4. Download embedding model (cached locally)
> python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
>
> # 5. Initialize database
> python -m src.cli init-db
>
> # 6. Copy environment template
> if [ ! -f ".env" ]; then
>   cp .env.example .env
>   echo "Created .env from template. Edit it with your API keys."
> else
>   echo ".env already exists. Skipping copy."
> fi
>
> echo ""
> echo "Setup complete!"
> echo "Next steps:"
> echo "  1. Edit .env with your API keys"
> echo "  2. Run: python -m src.cli --help"
> ```
>
> **File 2: `scripts/backfill.sh`:**
> ```bash
> #!/bin/bash
> set -e
>
> # Backfill historical YC content
> # Usage: bash scripts/backfill.sh [start-date]
> # Example: bash scripts/backfill.sh 2020-01-01
>
> START_DATE=${1:-"2020-01-01"}
>
> echo "YC Skills Forge - Historical Backfill"
> echo "Start date: $START_DATE"
> echo ""
>
> # Activate venv if not active
> if [ -z "$VIRTUAL_ENV" ]; then
>   source .venv/bin/activate
> fi
>
> python -m src.cli backfill --start-date "$START_DATE"
> ```
>
> **Implementation details:**
> 1. Both scripts must start with `#!/bin/bash` and `set -e` (exit on error).
> 2. `setup.sh` must match the architecture doc Section 16.2 steps exactly: clone, venv, pip install, model download, init-db, copy .env.
> 3. Add defensive checks: skip clone if `.git` exists, skip `.env` copy if `.env` already exists.
> 4. `backfill.sh` accepts an optional positional argument for start date, defaults to `2020-01-01`.
> 5. `backfill.sh` activates the venv if not already active.
>
> **Files to create:** `scripts/setup.sh`, `scripts/backfill.sh`.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, any `src/` file.
>
> **Rules:** Follow `AGENTS.md`. Shell scripts only (bash). Use `set -e` for safety. Include comments explaining each step. Use `echo` for user-facing output (these are shell scripts, not Python — `logging` doesn't apply here).
>
> **Self-review before completion:** Verify `setup.sh` steps match architecture doc Section 16.2 exactly. Verify both scripts have `#!/bin/bash` and `set -e`. Verify `backfill.sh` delegates to the CLI command correctly. Stop after completing ONLY this task.

---

### Task M13-T5: End-to-End Integration Test

| Field | Value |
|-------|-------|
| **Task ID** | `M13-T5` |
| **Title** | Create end-to-end pipeline integration test |
| **Files to Create** | `tests/test_integration.py` |
| **Dependencies** | All previous milestones |
| **Acceptance Criteria** | Tests the full pipeline with fixture data and mocked LLM calls: init-db → ingest (mock HTTP) → chunk → forge (mock LLM) → link → export → validate (mock LLM for hallucination guard). Verifies: skill files are created in correct format, spec files are generated, similarity matrix is created, validation passes. |
| **Required Tests** | 1 comprehensive integration test with all pipeline stages. |
| **Estimated Complexity** | L |
| **Estimated AI Sessions** | 2 |

**Execution Prompt:**

> You are implementing Task M13-T5 for the YC Skills Forge project.
>
> **Objective:** Create `tests/test_integration.py` — a comprehensive end-to-end integration test that exercises the full pipeline from ingestion to validation using fixture data and mocked external calls. This test proves the entire system works together.
>
> **Pipeline stages to test (in order):**
> 1. **init-db:** Create an in-memory (or temp dir) SQLite database with the full schema.
> 2. **Ingest (library):** Mock `requests.get()` to return a sample HTML essay. Verify content is saved to `data/raw/library/` and inserted into `content` table with state `downloaded`.
> 3. **Chunk:** Run the essay chunker on the ingested content. Verify chunks are created in `data/chunks/library/` and inserted into `chunks` table. Verify content state transitions to `chunked`.
> 4. **Forge — Batch:** Run the batcher. Verify batch_id is generated, content state transitions to `extracting`.
> 5. **Forge — Extract:** Mock `LLMClient.call()` to return a fixture `ExtractionResponse` JSON. Verify extracted items are inserted into `extracted_items` table. Verify content state transitions to `extracted`.
> 6. **Forge — Cluster:** Run the clusterer (with real `sentence-transformers` if available, or mock the embeddings). Verify clusters are created in `clusters` and `cluster_items` tables. Verify `avg_similarity` is computed.
> 7. **Forge — Synthesize:** Mock `LLMClient.call()` to return a fixture `SynthesisResponse` JSON. Verify skill Markdown file is created in `skills/{category}/`. Verify `confidence` is computed from cluster metrics (NOT from LLM response). Verify `related_skills` is empty `[]`.
> 8. **Link:** Run the linker (mock or use real embeddings). Verify `related_skills` is populated in the skill file frontmatter.
> 9. **Export:** Run all 3 exporters. Verify spec files are generated in `specs/mcp/`, `specs/openai/`, `specs/hermes/`. Verify MCP JSON has `fallback.invent_quotes: false`. Verify Hermes text has `DO NOT invent YC quotes`.
> 10. **Validate:** Run the validator suite. Mock the hallucination guard's LLM call. Verify quote verification passes (quotes match fixture chunks). Verify schema validation passes. Verify the skill is NOT moved to `skills/_failed/`.
>
> **Test structure:**
> ```python
> import tempfile
> import os
> import pytest
>
> class TestFullPipeline:
>     @pytest.fixture(autouse=True)
>     def setup_temp_workspace(self, tmp_path):
>         # Create temp dirs mirroring repo structure
>         # Set up in-memory or temp SQLite DB
>         # Create necessary config files
>         ...
>
>     def test_full_pipeline_produces_valid_skill(self):
>         # Run all 10 stages in sequence
>         # Assert final state is correct
>         ...
> ```
>
> **Mocking requirements:**
> - `requests.get` — return fixture HTML for library scraper.
> - `subprocess.run` — return fixture output for yt-dlp (if YouTube path is tested).
> - `LLMClient.call` — return fixture JSON responses for extraction, synthesis, and hallucination guard.
> - `SentenceTransformer.encode` — optionally mock if model download is impractical in CI. If mocking, return consistent numpy arrays of correct dimensionality (384 for all-MiniLM-L6-v2).
>
> **Fixture data to use:**
> - `tests/fixtures/sample_skill.md` (from M8-T4) for validation reference.
> - `tests/fixtures/extraction_response.json` (from M6-T1) for extraction mock.
> - `tests/fixtures/synthesis_response.json` (from M8-T1) for synthesis mock.
> - Create a `tests/fixtures/sample_essay.html` if one doesn't exist.
>
> **Assertions to verify:**
> - Skill file exists at expected path under `skills/{category}/`.
> - Skill file YAML frontmatter passes `SkillFrontmatter` Pydantic validation.
> - `confidence` is in range [0.55, 0.99] and was NOT taken from LLM response.
> - `related_skills` is a non-empty list (after linking).
> - 3 spec files exist (MCP JSON, OpenAI JSON, Hermes TXT).
> - `skills-index.json` exists and contains the skill ID.
> - `data/similarity_matrix.json` exists and has correct dimensions.
> - No files in `skills/_failed/` (validation passed).
> - Database state is consistent: content state progressed through all stages.
>
> **Files to create:** `tests/test_integration.py`.
> **Files you must NOT modify:** `AGENTS.md`, `yc-skills-forge-architecture-v1.1.md`, any `src/` file.
>
> **Rules:** Follow `AGENTS.md` Section 7 (Testing). This test must be SELF-CONTAINED — no API keys, no network access, no external dependencies beyond the locked requirements. Use `pytest` fixtures and `tmp_path` for isolation. Use `unittest.mock.patch` for mocking. The test must be deterministic and repeatable.
>
> **Self-review before completion:** Run `python -m pytest tests/test_integration.py -v` and verify it passes. Verify no network calls are made (check for unmocked HTTP or subprocess calls). Verify the test runs in < 60 seconds (excluding model download). Stop after completing ONLY this task.

---

### M13 Review Task

| Field | Value |
|-------|-------|
| **Task ID** | `M13-R` |
| **Title** | Milestone 13 Review — CI/CD, Documentation & Integration |

**Verification Checklist:**
- [ ] GitHub Actions workflow validates only, never generates
- [ ] No `schedule:` triggers in any workflow
- [ ] README has quickstart and CLI reference
- [ ] `docs/CONSUMPTION.md` covers all 3 spec formats
- [ ] `docs/BYOK.md` includes cold-start warning
- [ ] `docs/TAXONOMY.md` matches `config/taxonomy.yml`
- [ ] Setup script matches architecture doc Section 16.2
- [ ] E2E integration test passes with mocked externals
- [ ] All `python -m pytest` tests pass
- [ ] `ruff check src/` passes
- [ ] `ruff format --check src/` passes

---

## Development Order

The milestones are ordered to respect the strict dependency chain of the pipeline architecture:

1. **M1 (Scaffolding)** — Must come first. Every subsequent task depends on the directory structure and installed dependencies.
2. **M2 (Core Data Layer)** — Layer 1 (models, config, database) is the foundation that all Layer 2 modules import from. Building it second ensures no circular dependencies.
3. **M3 (Ingestion)** — The pipeline starts with content acquisition. Ingestion writes to `data/raw/` and the `content` table, which chunking reads.
4. **M4 (Chunking)** — Depends on ingested raw content. Produces the chunks that the forge pipeline consumes.
5. **M5 (Forge Foundation)** — The LLM client, prompt templates, and batcher are shared infrastructure used by extraction, synthesis, and validation.
6. **M6 (Extraction)** → **M7 (Clustering)** → **M8 (Synthesis & Linking)** — These follow the exact pipeline order: extract → cluster → synthesize → link. Each stage's output is the next stage's input.
7. **M9 (Exporters)** — Exporters read skill files, which must exist. Depends on M8.
8. **M10 (Validation)** — Validators read skill files and chunks. Depends on M8 (skills exist) and M4 (chunks exist). Placed after exporters because validation is the final gate before publication.
9. **M11 (Retrieval)** — Build-time indexing depends on having skills to index. Placed late because it's a post-processing step.
10. **M12 (CLI Assembly)** — Final CLI polish after all modules are implemented.
11. **M13 (CI/CD, Docs, Integration)** — Wrap-up milestone that depends on everything being implemented.

---

## Dependency Graph

```
M1 (Scaffolding)
 └── M2 (Core Data Layer)
      ├── M3 (Ingestion) ──── M4 (Chunking)
      │                              │
      └── M5 (Forge Foundation) ─────┤
           │                         │
           M6 (Extraction) ──────────┘
           │
           M7 (Clustering)
           │
           M8 (Synthesis & Linking)
           │
           ├── M9 (Exporters)
           ├── M10 (Validation)
           └── M11 (Retrieval)
                │
                M12 (CLI Assembly)
                │
                M13 (CI/CD, Docs, Integration)
```

---

## Parallelization Opportunities

The following task groups can be executed simultaneously by different AI agents:

| Parallel Group | Tasks | Rationale |
|---------------|-------|-----------|
| **Group A** | `M3-T1` + `M3-T2` | Known authors and library scraper are independent |
| **Group B** | `M4-T1` + `M4-T2` | Essay and transcript chunkers are independent |
| **Group C** | `M5-T1` + `M5-T2` + `M5-T3` | LLM client, prompt templates, and batcher are independent |
| **Group D** | `M9-T1` + `M9-T2` + `M9-T3` | All 3 exporters are independent |
| **Group E** | `M10-T1` + `M10-T2` + `M10-T3` | All 3 validators are independent |
| **Group F** | `M13-T1` + `M13-T2` + `M13-T3` + `M13-T4` | CI, README, docs, and scripts are independent |

> **Warning:** Agents in the same parallel group must NOT modify the same files. In particular, only ONE agent may modify `src/cli.py` at any time.

---

## Risk Areas

| Risk | Component | Severity | Mitigation |
|------|-----------|----------|------------|
| **LLM response format instability** | `src/forge/extractor.py`, `src/forge/synthesizer.py` | High | Extensive retry logic, JSON parse error handling, temperature fallback. Test with multiple fixture responses. |
| **Embedding model download size** | `src/forge/clusterer.py` | Medium | `all-MiniLM-L6-v2` is ~80MB. First test run will be slow. Document in setup instructions. |
| **Scraping target changes** | `src/ingest/library_scraper.py` | Medium | HTML structure of YC Library may change. Use defensive selectors with fallbacks. |
| **yt-dlp version drift** | `src/ingest/youtube_downloader.py` | Medium | `yt-dlp` updates frequently. Pin version in requirements. Test with real URLs periodically. |
| **Clustering quality** | `src/forge/clusterer.py` | High | `distance_threshold=0.18` is a sensitive parameter. Wrong value produces too many or too few clusters. Validate with known datasets. |
| **Quote verification false positives** | `src/validator/quote_verifier.py` | Medium | `markdownify` introduces formatting differences. Dual fuzzy matching mitigates but doesn't eliminate this. |
| **Provider API rate limits** | `src/forge/llm_client.py` | Medium | Free-tier providers have strict limits. Quota tracking and rotation mitigate. |
| **Cold-start fork problem** | CLI / Documentation | Low | Documented in BYOK. Mitigated by `--topic` scoping. |

**Recommendation:** Implement M6 (Extraction) and M7 (Clustering) as isolated milestones with extra test coverage, as they contain the highest-risk logic.

---

## Review Gates

| Gate | After Milestone | Focus |
|------|----------------|-------|
| **Gate 1: Foundation** | M2 | Layer 1 complete. Models validate. Config loads. DB initializes. |
| **Gate 2: Data Pipeline** | M4 | Content flows from URL → raw file → chunks. All state transitions work. |
| **Gate 3: Core Pipeline** | M8 | Full forge pipeline produces skill files. Confidence computed correctly. Related skills linked. |
| **Gate 4: Output Quality** | M10 | Validation suite catches bad skills. Exporters produce correct specs. |
| **Gate 5: Release Ready** | M13 | CI/CD works. Docs complete. E2E test passes. |

Each gate requires:
1. All milestone tests passing (`python -m pytest`)
2. Lint clean (`ruff check src/`)
3. No architectural violations (layering, forbidden imports)
4. Review of the milestone's review task checklist

---

## Definition of Done

### Per Task

- All files specified in "Files to Create" exist with correct content
- All acceptance criteria are met
- All required tests pass
- `ruff check src/` passes
- No files outside "Files to Modify" were changed
- No files in "Files NOT to Modify" were touched
- All public functions have docstrings
- No `print()` statements, bare `Exception`, `import *`, or hardcoded API keys

### Per Milestone

- All tasks in the milestone are Done
- The milestone's Review Task checklist is fully checked
- `python -m pytest` passes (full test suite)
- `ruff check src/` and `ruff format --check src/` pass
- No regressions in previously passing tests
- Milestone deliverables match architecture doc

### Entire Project

- All 13 milestones are Done
- All 5 review gates passed
- `python -m src.cli --help` shows all 12 commands
- Full E2E integration test passes
- `python -m pytest --cov=src` shows ≥ 80% coverage (excluding `cli.py`)
- All documentation (`README.md`, `docs/`, `AGENTS.md`) is complete and synchronized
- `.github/workflows/validate.yml` triggers correctly on PRs
- Repository structure matches architecture doc Section 2 exactly
- No TODO comments remain in production code (only in AGENTS.md if applicable)
- A maintainer can clone, set up, and run the full pipeline successfully

---

## Recommended Git Strategy

### Branch Naming

```
main                         # Protected. Only validated, published content.
scaffold/initial-setup       # M1 tasks
core/data-layer              # M2 tasks
feature/ingestion            # M3 tasks
feature/chunking             # M4 tasks
feature/forge-foundation     # M5 tasks
feature/forge-extraction     # M6 tasks
feature/forge-clustering     # M7 tasks
feature/forge-synthesis      # M8 tasks
feature/exporters            # M9 tasks
feature/validation           # M10 tasks
feature/retrieval            # M11 tasks
feature/cli-assembly         # M12 tasks
release/docs-cicd            # M13 tasks
```

### Commit Frequency

- **One commit per task.** Each task is atomic and should be committed independently.
- **Commit message format:** `{area}: {task-id} — {description}` (e.g., `forge: M6-T1 — implement advice extraction pipeline`)

### Pull Request Strategy

- **One PR per milestone.** Each milestone branch is merged into `main` after the review gate passes.
- PR description must include:
  - Milestone objective
  - List of tasks completed
  - Test results (`pytest` output)
  - Lint results (`ruff check` output)
  - Any deviations from the plan (with justification)

### Tagging Strategy

```
v0.1.0    # After M2 — Core data layer complete
v0.2.0    # After M4 — Data pipeline (ingest + chunk) complete
v0.3.0    # After M8 — Forge pipeline complete
v0.4.0    # After M10 — Validation suite complete
v0.5.0    # After M12 — CLI complete
v1.0.0    # After M13 — First full release
```

---

## Task Manifest

### Execution Order Checklist

```
Milestone 1 — Project Scaffolding
  [ ] M1-T1  Create full repository directory structure
  [ ] M1-T2  Create requirements.txt, pyproject.toml, .env.example
  [ ] M1-T3  Create .gitignore
  [ ] M1-R   Milestone 1 Review

Milestone 2 — Core Data Layer
  [ ] M2-T1  Implement all Pydantic models
  [ ] M2-T2  Implement config loader and YAML files
  [ ] M2-T3  Create SQLite schema migration file
  [ ] M2-T4  Create CLI scaffold with init-db command
  [ ] M2-R   Milestone 2 Review

Milestone 3 — Content Ingestion
  [ ] M3-T1  Create known authors lookup
  [ ] M3-T2  Implement library scraper
  [ ] M3-T3  Implement YouTube downloader
  [ ] M3-T4  Add ingest CLI commands
  [ ] M3-R   Milestone 3 Review

Milestone 4 — Content Chunking
  [ ] M4-T1  Implement essay chunker
  [ ] M4-T2  Implement transcript chunker
  [ ] M4-T3  Add chunk CLI command
  [ ] M4-R   Milestone 4 Review

Milestone 5 — Forge Foundation
  [ ] M5-T1  Implement LLM client with provider rotation
  [ ] M5-T2  Create Jinja2 prompt templates
  [ ] M5-T3  Implement batch selector
  [ ] M5-T4  Implement reaper logic and CLI command
  [ ] M5-R   Milestone 5 Review

Milestone 6 — Forge Extraction
  [ ] M6-T1  Implement extraction logic
  [ ] M6-T2  Add forge CLI command (partial)
  [ ] M6-R   Milestone 6 Review

Milestone 7 — Forge Clustering
  [ ] M7-T1  Implement clustering logic
  [ ] M7-T2  Extend forge CLI to include clustering
  [ ] M7-R   Milestone 7 Review

Milestone 8 — Forge Synthesis & Linking
  [ ] M8-T1  Implement skill synthesis
  [ ] M8-T2  Implement deferred linking
  [ ] M8-T3  Complete forge CLI pipeline + link command
  [ ] M8-T4  Create golden fixture files
  [ ] M8-R   Milestone 8 Review

Milestone 9 — Exporters
  [ ] M9-T1  Implement MCP exporter
  [ ] M9-T2  Implement OpenAI exporter
  [ ] M9-T3  Implement Hermes exporter
  [ ] M9-T4  Add export CLI command
  [ ] M9-R   Milestone 9 Review

Milestone 10 — Validation Suite
  [ ] M10-T1  Implement quote verifier
  [ ] M10-T2  Implement schema validator
  [ ] M10-T3  Implement hallucination guard
  [ ] M10-T4  Create validator runner
  [ ] M10-T5  Add validate CLI command
  [ ] M10-R   Milestone 10 Review

Milestone 11 — Retrieval & Indexing
  [ ] M11-T1  Implement signal resolver and index generation
  [ ] M11-T2  Add index CLI command
  [ ] M11-R   Milestone 11 Review

Milestone 12 — CLI Assembly & Utilities
  [ ] M12-T1  Implement quota command
  [ ] M12-T2  Implement backfill command
  [ ] M12-T3  CLI final review and polish
  [ ] M12-R   Milestone 12 Review

Milestone 13 — CI/CD, Documentation & Integration
  [ ] M13-T1  Create GitHub Actions validation workflow
  [ ] M13-T2  Create README
  [ ] M13-T3  Create detailed documentation (CONSUMPTION, BYOK, TAXONOMY)
  [ ] M13-T4  Create setup and backfill scripts
  [ ] M13-T5  Create end-to-end integration test
  [ ] M13-R   Milestone 13 Review (FINAL)
```

---

*End of Implementation Plan*
