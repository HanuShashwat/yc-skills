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
- [ ] Every directory from architecture doc Section 2 exists
- [ ] All Python packages have `__init__.py`
- [ ] All 8 skill categories have directories under `skills/`
- [ ] `requirements.txt` pins exact versions for all dependencies in architecture doc Section 3
- [ ] `pip install -r requirements.txt` succeeds in a clean Python 3.11 venv
- [ ] `pyproject.toml` contains ruff, mypy, pytest configurations
- [ ] `.gitignore` excludes correct paths
- [ ] `.env.example` contains all required placeholders
- [ ] `ruff check src/` passes
- [ ] No production logic has been written
- [ ] No files outside the architecture doc have been created

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
- [ ] `src/models.py` contains all Pydantic models from the architecture doc
- [ ] Skill ID regex `^yc-[a-z]+(-[a-z]+){1,6}$` is enforced
- [ ] `src/config.py` loads all 3 YAML files with env var substitution
- [ ] `config/taxonomy.yml` matches architecture doc Section 6.1 exactly
- [ ] `config/providers.yml` matches architecture doc Section 9.1 exactly
- [ ] `config/pipeline.yml` matches architecture doc Appendix C.3 exactly
- [ ] `src/migrations/001_init.sql` matches architecture doc Section 4.1 exactly
- [ ] `python -m src.cli init-db` works and is idempotent
- [ ] `python -m pytest` passes all model and config tests
- [ ] `ruff check src/` passes
- [ ] No Layer 1 module imports from Layer 2 or Layer 3
- [ ] All public functions have docstrings

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
- [ ] Library scraper downloads and parses HTML correctly (tested with mocks)
- [ ] Content IDs use `lib_{sha256(url)[:12]}` (not slug)
- [ ] YouTube downloader uses exact `yt-dlp` command flags from architecture doc
- [ ] Rate limiting: `time.sleep(2)` between scraping requests
- [ ] User-Agent: `YC-Skills-Forge/1.0 (Research Project; contact@example.com)`
- [ ] Speaker extraction with `known_authors.py` fallback
- [ ] NULL speaker → state `discovered` (not `downloaded`)
- [ ] URL deduplication enforced
- [ ] CLI commands `ingest-library` and `ingest-youtube` work
- [ ] All SQL uses parameterized queries
- [ ] `python -m pytest` passes
- [ ] `ruff check src/` passes

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
- [ ] Essay chunker splits by `## ` headers
- [ ] Word count bounds: essays 200–800, transcripts 400–800
- [ ] Overlap: last sentence of previous chunk at start of next (essays)
- [ ] Chunk IDs follow `{content_id}_{chunk_index:04d}` format
- [ ] Uses `chunk_index` not `index`
- [ ] Chunks saved as JSON to `data/chunks/{source_type}/`
- [ ] Chunks inserted into `chunks` table
- [ ] Content state transitions `downloaded` → `chunked`
- [ ] Parameters read from `config/pipeline.yml`
- [ ] `python -m pytest` passes
- [ ] `ruff check src/` passes

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
- [ ] `LLMClient` is the ONLY module with `import openai`
- [ ] Provider rotation follows priority order with quota awareness
- [ ] Usage logged to `usage_log` table on every call (success and failure)
- [ ] Prompt templates match architecture doc verbatim
- [ ] Batcher enforces min batch size 5, max 20
- [ ] Batcher transitions state `chunked` → `extracting`
- [ ] Reaper recovers items after 2 hours, fails after 3 retries
- [ ] No API keys hardcoded anywhere
- [ ] All tests pass with mocked LLM calls
- [ ] `ruff check src/` passes

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
- [ ] Extractor renders Jinja2 template (not f-string construction)
- [ ] `in_batch_index` is preserved in `extracted_items` table
- [ ] State transition: `extracting` → `extracted` (only after successful insertion)
- [ ] JSON parse failures logged to `data/errors/` and retried with `temperature=0.1`
- [ ] LLM called via `LLMClient`, not direct `openai`
- [ ] `forge` CLI command works with `--topic` and `--batch-size`
- [ ] All tests pass with mocked LLM
- [ ] `ruff check src/` passes

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
- [ ] No LLM calls in clusterer
- [ ] Uses exact `AgglomerativeClustering` parameters from architecture doc
- [ ] `sentence-transformers` import only in `clusterer.py`
- [ ] Clusters with < 2 items rejected
- [ ] Escape hatch after 3 retries with `computed_confidence = 0.55`
- [ ] `avg_similarity` computed correctly
- [ ] State transition: `extracted` → `clustered`
- [ ] Tests pass
- [ ] `ruff check src/` passes

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
- [ ] Confidence computed from cluster metrics, not LLM output
- [ ] `related_skills` set to `[]` by synthesizer, populated by linker only
- [ ] Skill files match Section 10.1 format exactly
- [ ] Linker uses similarity matrix, not LLM
- [ ] Skill ID uniqueness enforced (appends `_v2`, `_v3`)
- [ ] `forge` CLI runs full pipeline: batch → extract → cluster → synthesize
- [ ] `link` CLI runs deferred linking separately
- [ ] State transitions: `clustered` → `synthesized` → `linked`
- [ ] Golden fixtures pass Pydantic validation
- [ ] All tests pass

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

> You are implementing Task M9-T1. Create `src/exporter/mcp_exporter.py` that reads skill Markdown files and generates MCP spec JSON files matching architecture doc Section 11.1 exactly. Every spec must include the `fallback` block with `use_agent_knowledge: true` and `invent_quotes: false`. Save to `specs/mcp/{skill_id}.json`. Create tests. Files you must NOT modify: `AGENTS.md`, `src/forge/*.py`. Follow `AGENTS.md`. Stop after completing ONLY this task.

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

> You are implementing Task M9-T2. Create `src/exporter/openai_exporter.py` generating OpenAI function schema JSONs matching architecture doc Section 11.2. Include `metadata.fallback` with `invent_quotes: false`. Save to `specs/openai/{skill_id}.json`. Create tests. Follow `AGENTS.md`. Stop after completing ONLY this task.

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

> You are implementing Task M9-T3. Create `src/exporter/hermes_exporter.py` generating plain-text system prompt fragments matching architecture doc Section 11.3. Use `[SKILL: ...]` / `[END SKILL]` delimiters. Include FALLBACK instruction. Save to `specs/hermes/{skill_id}.txt`. Create tests. Follow `AGENTS.md`. Stop after completing ONLY this task.

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

> You are implementing Task M9-T4. Add the `export` subcommand to `src/cli.py` that accepts `--all` and calls all three exporters (MCP, OpenAI, Hermes) for every skill file in `skills/`. Files you may modify: `src/cli.py` ONLY. Follow `AGENTS.md`. Stop after completing ONLY this task.

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

> You are implementing Task M10-T1. Create `src/validator/quote_verifier.py` implementing the dual fuzzy match algorithm from architecture doc Section 14.1. Use `rapidfuzz.fuzz.ratio` AND `rapidfuzz.fuzz.partial_ratio`. Thresholds: ratio ≥ 70 AND partial_ratio ≥ 85 = PASS. ratio < 70 but partial_ratio ≥ 85 = WARNING. partial_ratio < 70 = FAIL. Fallback to `data/raw/` if chunk not found. Create tests with known-good, modified, and fabricated quotes. Follow `AGENTS.md`. Stop after completing ONLY this task.

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

> You are implementing Task M10-T2. Create `src/validator/schema_validator.py` implementing architecture doc Section 14.2. Parse YAML frontmatter, validate against `SkillFrontmatter` Pydantic model. Check skill_id matches filename, related_skills exist as files, tags are lowercase/no spaces/max 20 chars. Create tests. Follow `AGENTS.md`. Stop after completing ONLY this task.

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

> You are implementing Task M10-T3. Create `src/validator/hallucination_guard.py` implementing architecture doc Section 14.3. CRITICAL: The hallucination guard uses ONLY the `dedicated_validator` config from `providers.yml` (gemini-1.5-flash at temperature=0.0). It does NOT use the rotating provider pool. If Gemini quota is exhausted, SKIP the LLM-as-judge step and log a warning — do NOT fall back to another provider. This is a security boundary. Import `LLMClient` from `src/forge/llm_client.py` but use the dedicated validator config. Create tests. Follow `AGENTS.md`. Stop after completing ONLY this task.

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

> You are implementing Task M10-T4. Create `src/validator/run.py` as the entry point for `python -m src.validator.run --all`. It should run all 3 validators (quote, schema, hallucination) against all skill files in `skills/`. Report results per skill. Move failed skills to `skills/_failed/`. Exit code 0 = all pass, 1 = any fail. Follow `AGENTS.md`. Stop after completing ONLY this task.

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

> You are implementing Task M10-T5. Add the `validate` subcommand to `src/cli.py` that accepts `--all` and invokes `src/validator/run.py`. Files you may modify: `src/cli.py` ONLY. Follow `AGENTS.md`. Stop after completing ONLY this task.

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

> You are implementing Task M11-T1. Create `src/retrieval/resolver.py` implementing architecture doc Sections 12.2 and 13.1. This is a BUILD-TIME ONLY module. It generates `skills-index.json` and `data/similarity_matrix.json`. Implement the `SignalResolver` class with `resolve(query)` supporting all 4 resolution types. `sentence-transformers` import is allowed here. Create tests. Follow `AGENTS.md`. Stop after completing ONLY this task.

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

> You are implementing Task M11-T2. Add the `index` subcommand to `src/cli.py` that invokes `src/retrieval/resolver.py` to generate `skills-index.json` and `data/similarity_matrix.json`. Files you may modify: `src/cli.py` ONLY. Follow `AGENTS.md`. Stop after completing ONLY this task.

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

> You are implementing Task M12-T1. Add the `quota` subcommand to `src/cli.py` that queries `usage_log` for today's usage and displays remaining quota per provider. Files you may modify: `src/cli.py` ONLY. Follow `AGENTS.md`. Stop after completing ONLY this task.

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

> You are implementing Task M12-T2. Add the `backfill` subcommand to `src/cli.py` that accepts `--start-date` and orchestrates historical content ingestion. Files you may modify: `src/cli.py` ONLY. Follow `AGENTS.md`. Stop after completing ONLY this task.

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

> You are implementing Task M12-T3. Review `src/cli.py` and ensure all 12 commands are present with correct arguments, help text, and error handling. Run `python -m src.cli --help` and verify output. Add any missing commands. Write comprehensive CLI smoke tests. Files you may modify: `src/cli.py` ONLY. Follow `AGENTS.md`. Stop after completing ONLY this task.

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

> You are implementing Task M13-T1. Create `.github/workflows/validate.yml` matching architecture doc Section 14.4 exactly. Triggers on PR to `skills/**` and `specs/**`. Runs validation and tests ONLY — never generation. No `schedule:` triggers. Follow `AGENTS.md`. Stop after completing ONLY this task.

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

> You are implementing Task M13-T2. Create `README.md` with project overview, quickstart guide, CLI command reference, and links to detailed docs. Base content on architecture doc Section 1 (overview) and Section 16 (setup). Include license info (MIT for code, CC BY-SA 4.0 for generated content). Follow `AGENTS.md`. Do NOT overwrite the existing README if one exists with meaningful content — update it instead. Stop after completing ONLY this task.

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

> You are implementing Task M13-T3. Create `docs/CONSUMPTION.md` (how to use skills in agents — cover MCP, OpenAI, Hermes formats), `docs/BYOK.md` (fork and run yourself — based on architecture doc Section 17, include cold-start warning), `docs/TAXONOMY.md` (human-readable category tree from `config/taxonomy.yml`). Follow `AGENTS.md` Section 13 (Documentation Policy). Stop after completing ONLY this task.

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

> You are implementing Task M13-T4. Create `scripts/setup.sh` matching architecture doc Section 16.2 exactly. Create `scripts/backfill.sh` that wraps the backfill CLI command. Both scripts must have `#!/bin/bash` and `set -e`. Follow `AGENTS.md`. Stop after completing ONLY this task.

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

> You are implementing Task M13-T5. Create `tests/test_integration.py` that exercises the full pipeline end-to-end with fixture data. Mock ALL external calls (HTTP requests, LLM calls, yt-dlp subprocess). Use in-memory SQLite. Verify: skill files created in correct Markdown format, spec files generated in all 3 formats, similarity matrix generated, validation passes. This test should be self-contained and not require any API keys or network access. Follow `AGENTS.md`. Stop after completing ONLY this task.

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
