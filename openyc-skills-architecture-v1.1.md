# OpenYC Skills: Complete Technical Architecture Specification

**Version:** 1.1.0  
**Date:** 2026-07-16
**Status:** Implementation-Ready  
**Target:** AI Coding Agents (Claude Code, Cursor, Copilot, etc.)  

---

## 0. Non-Negotiable Constraints

1. **Manual Pipeline Only:** No scheduled GitHub Actions. Generation is triggered manually by maintainers via local CLI or `workflow_dispatch`.
2. **Zero Cost for End Users:** Consumers download static files from GitHub. No API keys, no runtime, no database, no embedding model downloads.
3. **BYOK for Contributors:** Forkers supply their own keys to regenerate or extend. Forks start from a cold state and must scope `--topic`/`--urls` carefully to avoid collisions with `main`.
4. **Exact Quote Fidelity:** Every YC attribution must be verbatim from source transcripts/articles. Fidelity is verified against *chunked* text (not raw HTML/VTT), because `markdownify` and paragraph-boundary splitting are known, documented lossy steps. No paraphrasing in attribution blocks.
5. **Narrow, Composable Skills:** Each skill covers one specific micro-topic. Skills reference each other via `related_skills` links populated in a deferred post-processing pass, never hallucinated by the synthesis LLM.
6. **Filter Signals:** `/` = category path filter. `%` = tag filter. Exact resolution algorithm specified in Section 11.
7. **No Runtime RAG / No Runtime Vector DB:** The published product contains only static files. The `SignalResolver` (Section 12) is a **build-time-only** tool used by maintainers to generate the `skills-index.json` and `similarity_matrix.json`. End-user agents consume these pre-computed indices directly.

---

## 1. System Overview

The OpenYC Skills is a static-file generator. It ingests content from Y Combinator's Library and YouTube channels, extracts actionable advice, clusters it into narrow principles, and emits versioned skill files (Markdown + YAML) and agent spec files (JSON). The output is a GitHub repository that AI agents consume directly.

**Architecture Pattern:** Batch ETL -> Static Site Generator -> Git Repository

**Core Loop (Manual Trigger):**
```
Discover -> Download -> Chunk -> Extract -> Cluster -> Synthesize -> Link -> Export -> Validate -> Commit -> Tag
```

Note the **Link** stage (Section 8.4) is a deferred pass that runs after all skills in a topic batch are synthesized. It populates `related_skills` using the pre-computed similarity matrix, never the LLM.

---

## 2. Exact Repository Structure

The repository MUST be initialized with this exact structure. No deviations.

```
Openyc-skills/
├── .github/
│   └── workflows/
│       └── validate.yml          # PR validation only. NO generation.
├── data/
│   ├── raw/
│   │   ├── library/              # HTML/Markdown of essays (gitignored)
│   │   └── youtube/              # JSON metadata + VTT transcripts (gitignored)
│   ├── chunks/
│   │   ├── library/              # JSON chunk files (gitignored)
│   │   └── youtube/              # JSON chunk files (gitignored)
│   ├── errors/                   # Failed LLM responses for manual review (gitignored)
│   ├── registry.db               # SQLite state machine (gitignored)
│   └── similarity_matrix.json    # Pre-computed skill similarities (COMMITTED)
├── skills/
│   ├── fundraising/
│   │   ├── seed-round-timing.md
│   │   ├── seed-round-valuation.md
│   │   └── investor-update-emails.md
│   ├── hiring/
│   ├── product/
│   ├── growth/
│   ├── culture/
│   └── ...                     # One directory per category (Section 6)
├── specs/
│   ├── mcp/                      # Model Context Protocol JSONs
│   ├── openai/                   # OpenAI function schemas
│   └── hermes/                   # Plain-text system prompt fragments
├── src/
│   ├── __init__.py
│   ├── config.py                 # Pydantic settings loader
│   ├── models.py                 # Pydantic data models
│   ├── ingest/
│   │   ├── __init__.py
│   │   ├── library_scraper.py    # Essay scraper
│   │   └── youtube_downloader.py # yt-dlp wrapper
│   ├── chunker/
│   │   ├── __init__.py
│   │   ├── essay_chunker.py
│   │   └── transcript_chunker.py
│   ├── forge/
│   │   ├── __init__.py
│   │   ├── batcher.py            # Selects 10-15 items per batch
│   │   ├── extractor.py          # LLM Call 1: Extract advice
│   │   ├── clusterer.py          # Local embedding + clustering
│   │   ├── synthesizer.py        # LLM Call 2: Generate skill
│   │   └── linker.py             # Deferred pass: populates related_skills
│   ├── exporter/
│   │   ├── __init__.py
│   │   ├── mcp_exporter.py
│   │   ├── openai_exporter.py
│   │   └── hermes_exporter.py
│   ├── validator/
│   │   ├── __init__.py
│   │   ├── quote_verifier.py     # Fuzzy match against chunks
│   │   ├── schema_validator.py   # Pydantic validation
│   │   └── hallucination_guard.py
│   ├── retrieval/                # Build-time only. NOT for end users.
│   │   ├── __init__.py
│   │   └── resolver.py           # Generates skills-index.json + similarity_matrix.json
│   └── cli.py                    # Single entry point: `python -m src.cli`
├── config/
│   ├── taxonomy.yml              # Exact topic tree
│   ├── providers.yml             # LLM provider configs
│   └── pipeline.yml              # Chunking, clustering, thresholds
├── scripts/
│   ├── setup.sh                  # One-command local setup
│   └── backfill.sh               # Historical content ingestion
├── docs/
│   ├── CONSUMPTION.md            # How to use skills in agents
│   ├── BYOK.md                   # Fork and run yourself
│   └── TAXONOMY.md               # Human-readable topic map
├── requirements.txt              # Exact pinned versions
├── pyproject.toml                # Project metadata + tool configs
├── .env.example                  # Template for local keys
├── .gitignore                    # Must ignore data/raw/, data/chunks/, data/registry.db, .env
├── skills-index.json             # Machine-readable index (COMMITTED, auto-generated)
└── README.md                     # Project overview + quickstart
```

**What is committed vs. gitignored:**
- **Committed:** `skills/`, `specs/`, `skills-index.json`, `data/similarity_matrix.json`, `src/`, `config/`, `docs/`, `scripts/`
- **Gitignored:** `data/raw/`, `data/chunks/`, `data/registry.db`, `data/errors/`, `.env`, `.venv/`

---

## 3. Technology Stack (Locked)

| Component | Exact Tool | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.11+ | All logic |
| Package Manager | `pip` | 24.x | Dependency management |
| Web Scraping | `requests` + `beautifulsoup4` | 2.32.x / 4.12.x | Essay HTML parsing |
| Video/Transcripts | `yt-dlp` | 2025.x | Download + caption extraction |
| Data Validation | `pydantic` | 2.9.x | Schema enforcement |
| YAML Parsing | `PyYAML` | 6.0.x | Config and frontmatter |
| Embeddings (Local) | `sentence-transformers` | 2.7.x | Clustering + similarity (maintainer-only) |
| Embedding Model | `all-MiniLM-L6-v2` | 1.0 | 384-dim, runs on CPU |
| Fuzzy Matching | `rapidfuzz` | 3.9.x | Quote verification |
| LLM Client | `openai` (OpenAI-compatible) | 1.40.x | Unified client for all providers |
| Templating | `Jinja2` | 3.1.x | Prompt templates |
| Database | `sqlite3` | Built-in | State tracking |
| Testing | `pytest` | 8.3.x | Unit tests |
| Linting | `ruff` | 0.6.x | Code formatting |

**No substitutions permitted.** If a tool is deprecated, the architecture must be updated explicitly.

---

## 4. Data Architecture

### 4.1 SQLite Schema (Exact)

File: `data/registry.db` (gitignored — maintainer-local only)

```sql
-- Content sources
CREATE TABLE content (
    content_id TEXT PRIMARY KEY,
    source_type TEXT NOT NULL CHECK(source_type IN ('library', 'youtube')),
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    speaker TEXT,
    designation TEXT,
    published_at TEXT,              -- ISO 8601 date
    content_hash TEXT NOT NULL,     -- SHA256 of raw text
    file_path TEXT NOT NULL,        -- Relative path in data/raw/
    state TEXT NOT NULL CHECK(state IN (
        'discovered',
        'downloaded',
        'chunked',
        'extracting',               -- NEW: items selected for a batch but not yet extracted
        'extracted',
        'clustered',
        'synthesized',
        'linked',                   -- NEW: deferred related_skills pass complete
        'validated',
        'published',
        'failed'
    )),
    topic_guess TEXT,               -- From taxonomy.yml
    retry_count INTEGER DEFAULT 0,
    last_processed TEXT,            -- ISO 8601 timestamp
    error_message TEXT
);

CREATE INDEX idx_content_state ON content(state);
CREATE INDEX idx_content_topic ON content(topic_guess);
CREATE INDEX idx_content_speaker ON content(speaker);

-- Individual chunks
CREATE TABLE chunks (
    chunk_id TEXT PRIMARY KEY,      -- {content_id}_{chunk_index:04d}
    content_id TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,   -- RENAMED from 'index' (SQL reserved word)
    text TEXT NOT NULL,
    word_count INTEGER NOT NULL,
    char_count INTEGER NOT NULL,
    speaker TEXT,
    timestamp_start TEXT,           -- HH:MM:SS or NULL for essays
    timestamp_end TEXT,
    FOREIGN KEY (content_id) REFERENCES content(content_id)
);

CREATE INDEX idx_chunks_content ON chunks(content_id);

-- Extracted advice items (output of Stage 1)
CREATE TABLE extracted_items (
    item_id TEXT PRIMARY KEY,       -- UUID4
    batch_id TEXT NOT NULL,         -- UUID4 of the batch
    chunk_id TEXT NOT NULL,
    in_batch_index INTEGER NOT NULL, -- NEW: stable 1-based index within the extraction prompt
    quote TEXT NOT NULL,
    speaker TEXT NOT NULL,
    designation TEXT,
    topic TEXT NOT NULL,
    source_url TEXT NOT NULL,
    is_framework INTEGER NOT NULL CHECK(is_framework IN (0, 1)),
    is_warning INTEGER NOT NULL CHECK(is_warning IN (0, 1)),
    extraction_date TEXT NOT NULL
);

CREATE INDEX idx_extracted_topic ON extracted_items(topic);
CREATE INDEX idx_extracted_batch ON extracted_items(batch_id);

-- Clusters (output of Stage 2)
CREATE TABLE clusters (
    cluster_id TEXT PRIMARY KEY,    -- UUID4
    batch_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    summary TEXT NOT NULL,
    item_count INTEGER NOT NULL,
    avg_similarity REAL,            -- NEW: average pairwise cosine similarity
    representative_quote TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Cluster membership
CREATE TABLE cluster_items (
    cluster_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    similarity_score REAL NOT NULL,
    PRIMARY KEY (cluster_id, item_id)
);

-- Skills registry
CREATE TABLE skills (
    skill_id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT '1.0.0',
    file_path TEXT NOT NULL,
    source_count INTEGER NOT NULL,
    quote_count INTEGER NOT NULL,
    related_skills TEXT,            -- JSON array of skill_ids (populated in deferred Link pass)
    computed_confidence REAL,       -- NEW: derived from cluster metrics, not LLM self-report
    state TEXT NOT NULL CHECK(state IN ('draft', 'validated', 'published')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_skills_state ON skills(state);

-- Usage tracking (for maintainer quota management)
CREATE TABLE usage_log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    batch_id TEXT,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    cost_estimate_usd REAL,
    call_type TEXT NOT NULL CHECK(call_type IN ('extract', 'synthesize', 'validate')),
    timestamp TEXT NOT NULL,
    success INTEGER NOT NULL CHECK(success IN (0, 1)),
    error_message TEXT
);

CREATE INDEX idx_usage_provider ON usage_log(provider, timestamp);
```

### 4.2 Content ID Generation (Deterministic, Collision-Resistant)

**Primary key `content_id` is derived from a hash of the full URL, NOT the slug.** This prevents collisions across different sections of ycombinator.com/library that share a slug, or essays republished under different paths.

- **Library essays:** `lib_{sha256(url)[:12]}` — 12 hex chars = 48 bits, collision probability negligible for this corpus. Keep the human-readable slug in a separate `display_slug` field (not in schema, computed on demand from `url`).
- **YouTube videos:** `yt_{video_id}` (11-char YouTube ID) — already globally unique.
- **Chunk IDs:** `{content_id}_{chunk_index:04d}`. Example: `yt_abc123def45_0003`

**Deduplication:** `url TEXT NOT NULL UNIQUE` is the real dedup key. If a URL is already in the table, skip re-ingestion regardless of `content_id`.

---

## 5. Content Ingestion Module

### 5.1 YC Library Essay Scraper

**File:** `src/ingest/library_scraper.py`

**Input:** None (reads from `config/pipeline.yml` for target URLs or manual URL list)
**Output:** Files in `data/raw/library/`, rows in `content` table

**Exact Behavior:**
1. Accept a list of URLs via CLI argument: `--urls url1 url2 url3`
2. For each URL:
   - HTTP GET with `requests`, timeout=30s
   - User-Agent: `OpenYC-Skills/1.0 (Research Project; contact@example.com)`
   - Parse with `BeautifulSoup4`
   - Extract `<article>` or `<main>` content. Fallback: `<div class="content">`
   - Remove: `<nav>`, `<footer>`, `<script>`, `<style>`, `<aside>`, ads, newsletter signup boxes
   - Convert to Markdown using `markdownify` (install: `pip install markdownify==0.13.x`)
   - Save to: `data/raw/library/{content_id}.md`
   - Compute SHA256 of the Markdown text
   - Insert into `content` table with state `downloaded`

**Speaker/Designation Extraction:**
- Look for byline pattern: `<span class="byline">` or `<p class="author">`
- If not found, check URL path for known authors (Paul Graham, Sam Altman, etc.) against a hardcoded mapping in `src/ingest/known_authors.py`
- If still unknown, set `speaker = NULL`, `designation = NULL` and set `state = 'discovered'` (not `downloaded`) so it is flagged for manual review before entering the pipeline

### 5.2 YouTube Downloader

**File:** `src/ingest/youtube_downloader.py`

**Tool:** `yt-dlp` (must be installed separately: `pip install yt-dlp`)

**Input:** Video URLs or Channel/Playlist URLs
**Output:** Files in `data/raw/youtube/`, rows in `content` table

**Exact Command Template:**
```python
import subprocess

def download_video(video_url: str, output_dir: str) -> dict:
    cmd = [
        "yt-dlp",
        "--write-subs",
        "--sub-langs", "en",
        "--sub-format", "json3",          # JSON format with timestamps
        "--skip-download",                # Do NOT download video files
        "--write-info-json",              # Metadata
        "--output", f"{output_dir}/%(id)s",
        video_url
    ]
    subprocess.run(cmd, check=True, timeout=300)
```

**Post-Processing:**
1. Read `{video_id}.info.json` to extract:
   - `title`
   - `uploader` (channel name)
   - `upload_date`
   - `description` (first 500 chars for speaker guessing)
2. Read `{video_id}.en.json3` to extract transcript segments
3. Convert JSON3 to plain text with timestamps for chunking
4. Speaker guessing from description:
   - Regex: `with ([A-Z][a-z]+ [A-Z][a-z]+)` or `([A-Z][a-z]+ [A-Z][a-z]+), (CEO|Founder|Partner|...)`
   - If multiple matches, store all in `speaker` as comma-separated string
   - Designation extracted from the same regex group
   - **Low-confidence flag:** If zero matches, set `speaker = NULL`, `designation = NULL`, and `state = 'discovered'` (not `downloaded`) for manual review
5. Save transcript as `{video_id}.transcript.txt` in `data/raw/youtube/`
6. Save metadata as `{video_id}.meta.json`
7. Insert into `content` table with state `downloaded` (or `discovered` if speaker is NULL)

---

## 6. Skill Taxonomy & Naming Convention

### 6.1 Category Tree (Exact)

Categories are directories under `skills/`. This tree is exhaustive. New categories require a PR to `config/taxonomy.yml`.

```yaml
taxonomy:
  fundraising:
    description: Raising capital from investors
    subcategories:
      - seed-round
      - series-a
      - pitch-deck
      - investor-relations
      - valuation
      - term-sheets
  hiring:
    description: Building the team
    subcategories:
      - first-hires
      - technical-hiring
      - culture-fit
      - compensation
      - firing
  product:
    description: Product development and management
    subcategories:
      - mvp
      - product-market-fit
      - user-research
      - roadmap
      - design
  growth:
    description: Acquiring and retaining users
    subcategories:
      - marketing
      - sales
      - retention
      - pricing
      - distribution
  culture:
    description: Company culture and operations
    subcategories:
      - mission
      - values
      - remote-work
      - communication
  strategy:
    description: High-level company decisions
    subcategories:
      - pivoting
      - competition
      - market-sizing
      - monetization
  founder-mental-models:
    description: Psychological and decision-making frameworks
    subcategories:
      - motivation
      - burnout
      - decision-making
      - leadership
  technical:
    description: Engineering and infrastructure
    subcategories:
      - architecture
      - scaling
      - security
      - ai-ml
```

### 6.2 Skill ID Naming Convention

Format: `yc-{category}-{subcategory}-{descriptor}`

Rules:
1. All lowercase
2. Words separated by hyphens
3. **Maximum 6 words after `yc-{category}`** (relaxed from 5 to match the regex and flagship example)
4. Descriptor must be specific enough that no two skills in the same subcategory share the same descriptor
5. Examples:
   - `yc-fundraising-seed-round-timing`
   - `yc-hiring-first-technical-hire`
   - `yc-product-mvp-no-code-approach`
   - `yc-founder-mental-models-default-alive-dead`

**Pydantic Regex (aligned with rule 3):**
```python
skill_id: str = Field(pattern=r'^yc-[a-z]+(-[a-z]+){1,6}$')
```

---

## 7. Chunking Engine

### 7.1 Essay Chunking

**File:** `src/chunker/essay_chunker.py`

**Algorithm:**
1. Read Markdown file
2. Split by level-2 headers (`## `)
3. Each header section becomes a candidate chunk
4. If candidate < 200 words, merge with next candidate until >= 200 words
5. If candidate > 800 words, split by paragraphs (`

`) and distribute evenly into sub-chunks of 400-600 words each
6. Overlap: Include the last sentence of the previous chunk at the start of the next chunk (for context continuity)
7. For each chunk, record:
   - `chunk_index`: sequential integer starting at 0 (RENAMED from `index`)
   - `text`: chunk content
   - `word_count`: `len(text.split())`
   - `char_count`: `len(text)`
   - `speaker`: from content table
   - `timestamp_start`: NULL
   - `timestamp_end`: NULL

### 7.2 Transcript Chunking

**File:** `src/chunker/transcript_chunker.py`

**Algorithm:**
1. Read JSON3 transcript or VTT
2. Group segments by speaker if speaker labels exist (VTT sometimes has `v:SpeakerName`)
3. Merge consecutive segments from the same speaker until the group reaches 400-800 words
4. If a single speaker monologue exceeds 800 words, split at the nearest sentence boundary after 600 words
5. For each chunk, record:
   - `chunk_index`: sequential integer (RENAMED from `index`)
   - `text`: merged segment text
   - `word_count`
   - `char_count`
   - `speaker`: from segment label or content metadata
   - `timestamp_start`: HH:MM:SS of first segment
   - `timestamp_end`: HH:MM:SS of last segment

### 7.3 Chunk Storage

Each chunk is saved as a JSON file:

```json
{
  "chunk_id": "yt_abc123def45_0003",
  "content_id": "yt_abc123def45",
  "chunk_index": 3,
  "text": "The best time to raise money is when you don't need it...",
  "word_count": 142,
  "char_count": 890,
  "speaker": "Paul Graham",
  "timestamp_start": "00:04:32",
  "timestamp_end": "00:05:15"
}
```

Path: `data/chunks/{source_type}/{content_id}_{chunk_index:04d}.json`

---

## 8. Pipeline Stages (Exact Execution Flow)

The pipeline is triggered by a single CLI command:

```bash
python -m src.cli forge --batch-size 15 --topic <topic>
```

### Stage 0: Batch Selection (`src/forge/batcher.py`)

**Input:** `--topic` (optional), `--batch-size` (default 15, max 20)
**Output:** List of `content_id`s, written to `batch_id` (UUID4)

**Algorithm:**
1. Query `content` table for items with `state = 'chunked'`
2. If `--topic` provided, filter `topic_guess = topic`
3. If no topic provided, select the topic with the most unprocessed chunks
4. Randomly select up to `--batch-size` items from that topic
5. If fewer than 5 items available, log warning and abort (minimum batch size = 5)
6. Update selected items' state to `extracting` (NEW intermediate state)
7. Return `batch_id` and list of `content_id`s

**Recovery from crashes:** A cron-like or manual reaper command `python -m src.cli reaper` checks for items with `state = 'extracting'` and `last_processed < now() - 2 hours`. If found, resets state to `chunked` and increments `retry_count`. If `retry_count > 3`, marks `failed`.

### Stage 1: Advice Extraction (`src/forge/extractor.py`)

**Input:** `batch_id`, list of chunks
**Output:** Rows in `extracted_items` table
**LLM Call:** Single call per batch

**Prompt Template (Jinja2):** `src/forge/prompts/extract.j2`

```jinja2
You are an expert research analyst extracting actionable startup advice from Y Combinator content.

TASK: Analyze the {{ chunks|length }} content segments below and extract EVERY piece of actionable advice, framework, mental model, or warning.

RULES:
1. Preserve quotes EXACTLY as written or spoken. Do not change a single word.
2. If the quote is truncated in the chunk, mark it as "partial" and include the full available text.
3. For each item, identify the speaker and their exact designation (e.g., "Paul Graham, Founder of YC").
4. Classify each item:
   - "framework": A repeatable mental model or methodology
   - "warning": A common mistake or pitfall
   - "advice": General actionable recommendation
   - "story": A specific company anecdote (extract the lesson, not the narrative)
5. Tag each item with ONE topic from this exact list: {{ topics|join(', ') }}
6. If multiple speakers disagree on the same topic, note the contradiction using the IN-BATCH INDEX numbers (1-based) shown below.

CONTENT SEGMENTS:
{% for chunk in chunks %}
--- SEGMENT {{ loop.index }} ---
In-Batch Index: {{ loop.index }}
Source: {{ chunk.content_id }}
URL: {{ chunk.url }}
Speaker: {{ chunk.speaker }}
Designation: {{ chunk.designation }}
Timestamp: {{ chunk.timestamp_start }} - {{ chunk.timestamp_end }}
Text:
{{ chunk.text }}

{% endfor %}

OUTPUT FORMAT: Return a single JSON object with this exact structure:
{
  "extracted_items": [
    {
      "in_batch_index": 1,
      "quote": "exact verbatim quote",
      "speaker": "Full Name",
      "designation": "Title, Organization",
      "source_id": "content_id",
      "source_url": "https://...",
      "timestamp": "00:04:32",
      "topic": "fundraising",
      "type": "framework",
      "context": "1-2 sentences of surrounding context",
      "is_partial": false
    }
  ],
  "contradictions": [
    {
      "topic": "fundraising",
      "in_batch_indices": [1, 3],
      "summary": "Speaker A says X, Speaker B says Y"
    }
  ]
}

CONSTRAINTS:
- Minimum 3 items per content segment if advice exists. Maximum 20 per segment.
- If a segment contains no actionable advice, return an empty items array for that segment but explain why in a "notes" field.
- Do not invent speakers. If speaker is unknown, use "Unknown Speaker" and flag for review.
- Use ONLY the In-Batch Index numbers (1, 2, 3...) to reference items in contradictions. Do NOT use UUIDs or made-up IDs.
```

**Processing:**
1. Load all chunks for the batch content IDs
2. Render prompt with Jinja2
3. Call LLM via provider rotation (Section 9)
4. Parse JSON response with `pydantic`
5. **Map `in_batch_index` to `chunk_id` and generate UUID4 `item_id` for each extracted item**
6. Insert each item into `extracted_items` table with `in_batch_index` preserved
7. Update content items' state to `extracted` (only after successful insertion)
8. Log usage to `usage_log`

### Stage 2: Clustering (`src/forge/clusterer.py`)

**Input:** `batch_id`, rows from `extracted_items`
**Output:** Rows in `clusters` and `cluster_items` tables
**No LLM call. Pure local computation.**

**Algorithm:**
1. Load `sentence-transformers` model: `all-MiniLM-L6-v2`
2. Embed each `quote` text: `model.encode(quotes, convert_to_tensor=True)`
3. Compute cosine similarity matrix
4. Clustering: Agglomerative clustering with `scikit-learn`:
   ```python
   from sklearn.cluster import AgglomerativeClustering

   clustering = AgglomerativeClustering(
       n_clusters=None,
       distance_threshold=0.18,      # Corresponds to ~0.82 cosine similarity
       metric='cosine',
       linkage='average'
   )
   labels = clustering.fit_predict(embeddings)
   ```
5. For each cluster:
   - Select the longest quote as `representative_quote`
   - Compute `avg_similarity`: average pairwise cosine similarity of all items in the cluster
   - Generate `summary` by concatenating all unique speaker names and the common theme
   - Insert into `clusters` table
   - Insert memberships into `cluster_items` with similarity scores
6. Reject clusters with < 2 items (insufficient consensus). These items return to the pool for future batches.
7. **Escape hatch for niche topics:** If an item has been rejected from clusters >= 3 times across different batches (tracked via `retry_count` on the parent content item), force it into a singleton cluster with `computed_confidence = 0.55` and flag `human_review: true`.
8. Mark batch state as `clustered`

### Stage 3: Skill Synthesis (`src/forge/synthesizer.py`)

**Input:** One `cluster_id` at a time
**Output:** One Markdown skill file in `skills/{category}/`
**LLM Call:** One call per cluster

**Prompt Template:** `src/forge/prompts/synthesize.j2`

```jinja2
You are creating a narrow, composable skill file for AI agents based on Y Combinator advice.

CLUSTER TOPIC: {{ topic }}
NUMBER OF SOURCE ITEMS: {{ items|length }}
AVERAGE PAIRWISE SIMILARITY: {{ avg_similarity }}

EXTRACTED QUOTES:
{% for item in items %}
{{ loop.index }}. "{{ item.quote }}"
   — {{ item.speaker }}, {{ item.designation }}
   Source: {{ item.source_url }} at {{ item.timestamp }}
   Type: {{ item.type }}

{% endfor %}

TASK:
1. Write a unified principle (2-4 sentences) that captures the consensus. If sources disagree, present the majority view and note the dissenting view.
2. Select the 2-3 strongest exact quotes to preserve verbatim.
3. Write a "Personalized Application" section: specific instructions for how an AI agent should apply this advice when a founder asks a related question. Include 2-3 contextual follow-up questions the agent should ask.
4. Identify 1-2 edge cases or exceptions.
5. List related skill IDs ONLY if you are absolutely certain they already exist in the repository. Use the taxonomy: yc-{category}-{subcategory}-{descriptor}. If unsure, leave empty array.

OUTPUT FORMAT: Return JSON with this exact structure:
{
  "skill_id": "yc-{{ topic }}-{{ descriptor }}",
  "name": "Human-Readable Skill Name",
  "category": "{{ category }}",
  "principle": "Unified principle text...",
  "quotes": [
    {
      "text": "exact quote",
      "speaker": "Name",
      "designation": "Title",
      "source_url": "https://...",
      "timestamp": "00:04:32"
    }
  ],
  "application": {
    "when_to_use": "Description of when this skill applies",
    "follow_up_questions": ["Question 1?", "Question 2?"],
    "actions": ["Action 1", "Action 2"]
  },
  "edge_cases": ["Edge case 1", "Edge case 2"],
  "related_skills": [],
  "confidence": 0.0
}

RULES:
- skill_id must follow pattern: yc-{category}-{descriptor} (max 6 words after category)
- Set confidence to 0.0. It will be overwritten by the pipeline based on cluster metrics.
- Do NOT invent quotes. Every quote must be from the EXTRACTED QUOTES list above.
- Do NOT invent speakers. Use only speakers from the extracted items.
- related_skills: ONLY include IDs you are 100% certain exist. Prefer empty array.
```

**Processing:**
1. Load cluster items
2. Determine `category` from `topic` using `config/taxonomy.yml` mapping
3. Generate `descriptor` by asking the LLM to suggest 3-5 words, then slugify
4. Ensure `skill_id` uniqueness: if exists in `skills` table, append `_v2`, `_v3`, etc.
5. Render prompt and call LLM
6. Parse JSON response
7. **Overwrite `confidence` with computed value:**
   ```python
   computed_confidence = min(0.99, max(0.55, 
       (avg_similarity * 0.5) + 
       (min(item_count, 10) / 10 * 0.3) + 
       (0.2 if not contradictions else 0.1)
   ))
   ```
   - `avg_similarity`: from `clusters.avg_similarity`
   - `item_count`: from `clusters.item_count`
   - `contradictions`: boolean from `extracted_items` table for this batch
8. Write Markdown file (Section 10) with `computed_confidence` in frontmatter
9. Insert into `skills` table with state `draft`, `related_skills = NULL` (populated later)

### Stage 4: Deferred Link Pass (`src/forge/linker.py`)

**Input:** All skills generated in the current batch/topic
**Output:** Updated `related_skills` in skill files and `skills` table
**No LLM call.**

**Algorithm:**
1. Load all newly synthesized skills for this batch
2. Load the pre-computed `data/similarity_matrix.json` (or compute it now if this is the first run)
3. For each new skill, find the top 3 most similar *existing* skills (by cosine similarity of embeddings) from the full repo
4. Verify each candidate `skill_id` actually exists as a file in `skills/`
5. Update the skill Markdown file's frontmatter `related_skills` field
6. Update the `skills` table row
7. Mark skill state as `linked` (intermediate state before validation)

**Why deferred:** The synthesis LLM cannot know which skills exist in the repo (especially forward references in the same batch). The similarity matrix is the single source of truth for relatedness.

---

## 9. LLM Provider Rotation & Quota Management

### 9.1 Configuration (`config/providers.yml`)

```yaml
providers:
  deepseek:
    api_key: ${DEEPSEEK_API_KEY}
    base_url: "https://api.deepseek.com/v1"
    model: "deepseek-chat"
    daily_token_limit: 1_000_000
    daily_request_limit: 100
    priority: 1
    timeout: 120
    max_retries: 3

  kimi:
    api_key: ${KIMI_API_KEY}
    base_url: "https://api.moonshot.cn/v1"
    model: "moonshot-v1-8k"
    daily_token_limit: 500_000
    daily_request_limit: 50
    priority: 2
    timeout: 120
    max_retries: 3

  glm:
    api_key: ${GLM_API_KEY}
    base_url: "https://open.bigmodel.cn/api/paas/v4"
    model: "glm-4-flash"
    daily_token_limit: 500_000
    daily_request_limit: 50
    priority: 3
    timeout: 120
    max_retries: 3

  gemini:
    api_key: ${GEMINI_API_KEY}
    base_url: "https://generativelanguage.googleapis.com/v1beta/openai/"
    model: "gemini-1.5-flash"
    daily_token_limit: 1_500_000
    daily_request_limit: 150
    priority: 4
    timeout: 120
    max_retries: 3

rotation_strategy:
  mode: "round_robin_quota"
  fallback_local: false

quotas:
  reset_utc_hour: 0
  buffer_percent: 10

validation:
  # The hallucination guard (Section 14.3) requires a reliable, fast model.
  # It does NOT rotate through the general pool. It uses this dedicated config.
  dedicated_validator:
    provider: "gemini"
    model: "gemini-1.5-flash"
    max_tokens: 2000
    temperature: 0.0
    fallback_behavior: "fail_open"
    # If Gemini quota is exhausted, validation skips the LLM-as-judge step
    # and relies only on fuzzy quote matching + schema validation (Section 14.1, 14.2).
    # A warning is logged: "LLM-as-judge skipped due to quota exhaustion."
```

### 9.2 Rotation Algorithm (`src/config.py` + `src/forge/llm_client.py`)

**Exact Implementation:**

```python
import os
from datetime import datetime, timezone
from typing import Optional
import openai

class LLMClient:
    def __init__(self, config_path: str = "config/providers.yml"):
        self.providers = self._load_providers(config_path)
        self.db_path = "data/registry.db"

    def get_provider(self, estimated_tokens: int = 10000) -> dict:
        """Select provider with most remaining quota."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        candidates = []
        for name, cfg in self.providers.items():
            if not cfg.get("api_key"):
                continue

            used = self._get_daily_usage(name, today)
            remaining_tokens = cfg["daily_token_limit"] - used["tokens"]
            remaining_requests = cfg["daily_request_limit"] - used["requests"]

            # 10% buffer
            effective_tokens = remaining_tokens * 0.9
            effective_requests = remaining_requests * 0.9

            if effective_tokens >= estimated_tokens and effective_requests >= 1:
                candidates.append({
                    "name": name,
                    "cfg": cfg,
                    "remaining": effective_tokens,
                    "priority": cfg["priority"]
                })

        if not candidates:
            raise RuntimeError("All providers exhausted. Wait for UTC midnight reset.")

        # Sort by priority first, then by remaining quota
        candidates.sort(key=lambda x: (x["priority"], -x["remaining"]))
        return candidates[0]

    def call(self, prompt: str, call_type: str, temperature: float = 0.3) -> str:
        provider = self.get_provider(estimated_tokens=len(prompt) // 4)
        cfg = provider["cfg"]

        client = openai.OpenAI(
            api_key=cfg["api_key"],
            base_url=cfg["base_url"],
            timeout=cfg["timeout"]
        )

        response = client.chat.completions.create(
            model=cfg["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=8000,
            response_format={"type": "json_object"}  # Force JSON where supported
        )

        # Log usage
        tokens = response.usage.total_tokens
        self._log_usage(provider["name"], cfg["model"], tokens, call_type, success=True)

        return response.choices[0].message.content
```

**Note:** If `response_format={"type": "json_object"}` is not supported by a provider, the prompt must include explicit JSON formatting instructions and the response is parsed with `json.loads()` inside a `try/except` block.

---

## 10. Skill File Specification (Exact Format)

**File Extension:** `.md`  
**Location:** `skills/{category}/{skill_id}.md`  
**Encoding:** UTF-8  
**Line Endings:** LF (`
`)

### 10.1 File Structure

```markdown
---
skill_id: yc-fundraising-seed-round-timing
name: Seed Round Timing
version: "1.0.0"
category: fundraising
tags:
  - seed
  - runway
  - leverage
  - investors
  - timing
source_count: 12
quote_count: 3
related_skills:
  - yc-fundraising-seed-round-valuation
  - yc-fundraising-investor-update-emails
  - yc-founder-mental-models-default-alive-dead
confidence: 0.92
provenance:
  batch_id: "550e8400-e29b-41d4-a716-446655440000"
  pipeline_run_date: "2026-07-12T00:00:00Z"
  github_run_url: ""
  sources:
    - content_id: "lib_a1b2c3d4e5f6"
      title: "How to convince investors"
      speaker: "Paul Graham"
      designation: "Founder of YC"
      url: "https://paulgraham.com/convince.html"
      contribution: "3 quotes, 1 framework"
    - content_id: "yt_abc123def45"
      title: "Office Hours: Fundraising"
      speaker: "Garry Tan"
      designation: "CEO of YC"
      url: "https://youtube.com/watch?v=abc123def45"
      contribution: "2 quotes, 1 warning"
validation:
  quote_verified: true
  schema_valid: true
  hallucination_check: true
  human_review: false
---

# Seed Round Timing

## Principle

The optimal time to raise a seed round is when you have 9-12 months of runway remaining and can demonstrate measurable momentum. Raising from a position of strength maximizes valuation and preserves founder equity.

## Verbatim Quotes

> "The best time to raise money is when you don't need it."
> — **Paul Graham**, Founder of YC
> Source: [How to convince investors](https://paulgraham.com/convince.html)

> "If you wait until you need money, you've already lost."
> — **Michael Seibel**, Partner at YC
> Source: [Office Hours: Fundraising](https://youtube.com/watch?v=abc123def45) at 00:04:32

> "Investors can smell desperation. When you're down to 2 months of runway, you have zero leverage."
> — **Garry Tan**, CEO of YC
> Source: [YC Office Hours](https://youtube.com/watch?v=def456ghi78) at 00:12:15

## Personalized Application

### When to Use This Skill

Activate this skill when a founder asks about:
- When to start fundraising
- How much runway they need before raising
- Whether to raise now or wait for more traction
- What to do if they have < 6 months of cash left

### Agent Protocol

1. **Assess Runway First**
   - Ask: "What is your current monthly burn rate and cash in bank?"
   - Calculate runway in months: `cash / burn`
   - If < 6 months: Flag as urgent. Advise bridge round or revenue focus before full seed process.
   - If 6-12 months: Advise starting investor conversations immediately. "The conversation before the ask."
   - If > 12 months: Advise building relationships but not formal pitching yet.

2. **Check Momentum Signals**
   - Ask: "Do you have 10+ paying customers / 100+ active users / week-over-week growth?"
   - If yes: Emphasize strength in positioning.
   - If no: Advise focusing on traction before raising, or targeting angels over institutions.

3. **Provide Contextual Warnings**
   - Never advise a founder with < 3 months runway to start a competitive seed process.
   - Suggest SAFE notes or convertible debt if speed is critical.

### Follow-Up Questions

- "How many months of runway do you currently have?"
- "What metrics can you show an investor today that you couldn't 3 months ago?"
- "Have you started building relationships with any investors, or is this a cold start?"

## Edge Cases

- **Pre-revenue AI startups:** May need to raise earlier based on technical milestones rather than revenue. Adjust timing advice to focus on demo readiness and team credibility.
- **Profitable bootstrapped companies:** May not need seed at all. This skill should trigger a discussion about whether dilution is necessary.
- **Market downturns:** In tight funding markets (e.g., 2022-2023), even 12 months runway may be insufficient. Advise extending runway to 18+ months if possible.

## Related Skills

- [yc-fundraising-seed-round-valuation](yc-fundraising-seed-round-valuation.md) — How to think about valuation when you do raise
- [yc-fundraising-investor-update-emails](yc-fundraising-investor-update-emails.md) — Maintaining warmth before the ask
- [yc-founder-mental-models-default-alive-dead](yc-founder-mental-models-default-alive-dead.md) — Runway calculation framework

## Fallback Behavior

If this skill does not match the user's query exactly, the agent MUST:
1. Return the 3 closest skills (by category proximity and tag overlap)
2. Provide advice based on the agent's general knowledge, NOT by inventing YC-specific quotes or attributing advice to YC speakers
3. Clearly state: "No specific YC skill exists for this exact question. Here is general advice, and related OpenYC Skills for context:"
```

### 10.2 YAML Frontmatter Schema (Pydantic)

```python
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime

class ProvenanceSource(BaseModel):
    content_id: str
    title: str
    speaker: Optional[str]
    designation: Optional[str]
    url: HttpUrl
    contribution: str

class Provenance(BaseModel):
    batch_id: str
    pipeline_run_date: datetime
    github_run_url: Optional[str] = ""
    sources: List[ProvenanceSource]

class Validation(BaseModel):
    quote_verified: bool
    schema_valid: bool
    hallucination_check: bool
    human_review: bool

class SkillFrontmatter(BaseModel):
    skill_id: str = Field(pattern=r'^yc-[a-z]+(-[a-z]+){1,6}$')
    name: str = Field(max_length=100)
    version: str = Field(default="1.0.0", pattern=r'^\d+\.\d+\.\d+$')
    category: str
    tags: List[str] = Field(min_length=1, max_length=10)
    source_count: int = Field(ge=1)
    quote_count: int = Field(ge=1)
    related_skills: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    provenance: Provenance
    validation: Validation
```

---

## 11. Spec File Specifications (Exact Formats)

### 11.1 MCP Spec (`specs/mcp/{skill_id}.json`)

For Claude Code and other MCP-compatible agents.

```json
{
  "name": "yc_fundraising_seed_round_timing",
  "description": "YC advice on optimal timing for seed fundraising. Sources: Paul Graham (Founder of YC), Michael Seibel (Partner at YC), Garry Tan (CEO of YC). Provides runway-based guidance and contextual follow-up questions.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "runway_months": {
        "type": "number",
        "description": "Current months of runway remaining"
      },
      "monthly_burn": {
        "type": "number",
        "description": "Monthly burn rate in USD"
      },
      "has_traction": {
        "type": "boolean",
        "description": "Whether the startup has measurable traction (paying customers, active users, growth)"
      },
      "question": {
        "type": "string",
        "description": "The founder's specific question about fundraising timing"
      }
    },
    "required": ["runway_months", "question"]
  },
  "handler": {
    "type": "file",
    "path": "skills/fundraising/yc-fundraising-seed-round-timing.md"
  },
  "tags": ["fundraising", "seed", "runway", "timing"],
  "fallback": {
    "mode": "closest_skills",
    "count": 3,
    "use_agent_knowledge": true,
    "invent_quotes": false
  }
}
```

### 11.2 OpenAI Function Spec (`specs/openai/{skill_id}.json`)

```json
{
  "type": "function",
  "function": {
    "name": "yc_fundraising_seed_round_timing",
    "description": "YC advice on optimal timing for seed fundraising. Sources: Paul Graham (Founder of YC), Michael Seibel (Partner at YC), Garry Tan (CEO of YC). Provides runway-based guidance and contextual follow-up questions.",
    "parameters": {
      "type": "object",
      "properties": {
        "runway_months": {
          "type": "number",
          "description": "Current months of runway remaining"
        },
        "monthly_burn": {
          "type": "number",
          "description": "Monthly burn rate in USD"
        },
        "has_traction": {
          "type": "boolean",
          "description": "Whether the startup has measurable traction"
        },
        "question": {
          "type": "string",
          "description": "The founder's specific question about fundraising timing"
        }
      },
      "required": ["runway_months", "question"]
    }
  },
  "metadata": {
    "skill_file": "skills/fundraising/yc-fundraising-seed-round-timing.md",
    "category": "fundraising",
    "tags": ["seed", "runway", "timing"],
    "fallback": {
      "mode": "closest_skills",
      "count": 3,
      "use_agent_knowledge": true,
      "invent_quotes": false
    }
  }
}
```

### 11.3 Hermes / Local Model Spec (`specs/hermes/{skill_id}.txt`)

Plain text system prompt fragment for local models (llama.cpp, Ollama, etc.).

```text
[SKILL: yc-fundraising-seed-round-timing]
NAME: Seed Round Timing
CATEGORY: fundraising
TAGS: seed, runway, leverage, investors, timing

PRINCIPLE: The optimal time to raise a seed round is when you have 9-12 months of runway remaining and can demonstrate measurable momentum. Raising from a position of strength maximizes valuation and preserves founder equity.

VERBATIM QUOTES:
- "The best time to raise money is when you don't need it." — Paul Graham, Founder of YC
- "If you wait until you need money, you've already lost." — Michael Seibel, Partner at YC
- "Investors can smell desperation." — Garry Tan, CEO of YC

WHEN TO USE: Founder asks about fundraising timing, runway, or leverage.

AGENT PROTOCOL:
1. Ask runway_months and monthly_burn first.
2. If < 6 months: Urgent. Suggest bridge or revenue focus.
3. If 6-12 months: Start conversations now.
4. If > 12 months: Build relationships, don't pitch yet.

FOLLOW-UP QUESTIONS:
- How many months of runway do you have?
- What metrics can you show today?
- Have you started investor relationships?

EDGE CASES:
- Pre-revenue AI: Raise on technical milestones, not revenue.
- Bootstrapped profitable: Discuss if dilution is necessary.
- Market downturn: Extend runway to 18+ months.

FALLBACK: If query does not match, return 3 closest skills and use general knowledge. DO NOT invent YC quotes.

RELATED SKILLS: yc-fundraising-seed-round-valuation, yc-fundraising-investor-update-emails, yc-founder-mental-models-default-alive-dead
[END SKILL]
```

---

## 12. Filter & Signal Resolution System (Build-Time Only)

### 12.1 Signal Prefixes

| Prefix | Meaning | Example | Resolution |
|--------|---------|---------|------------|
| `/` | Category path filter | `/fundraising` | List all skills in `skills/fundraising/` |
| `/` | Subcategory filter | `/fundraising/seed-round` | List skills matching `yc-fundraising-seed-round-*` |
| `%` | Tag filter | `%seed` | List skills where `seed` is in `tags` array |
| `%` | Multi-tag filter | `%seed,runway` | List skills where ALL listed tags are present (AND logic) |
| No prefix | Exact skill ID | `yc-fundraising-seed-round-timing` | Direct file lookup |
| No prefix | Fuzzy match | `fundraising timing` | Embedding similarity search (Section 13) |

### 12.2 Resolution Algorithm (`src/retrieval/resolver.py`)

**This module is build-time only.** It generates `skills-index.json` and `data/similarity_matrix.json`. End-user agents do NOT run this code.

```python
from typing import List, Optional
import os
import yaml

class SignalResolver:
    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = skills_dir
        self.skills_index = self._build_index()

    def resolve(self, query: str) -> dict:
        """
        Returns exact match, or list of candidates, or closest skills.
        """
        query = query.strip().lower()

        # 1. Exact skill ID match
        if query.startswith("yc-"):
            path = self._skill_id_to_path(query)
            if os.path.exists(path):
                return {"type": "exact", "skill": query, "path": path}

        # 2. Category filter /
        if query.startswith("/"):
            category_path = query[1:]  # Remove leading /
            full_path = os.path.join(self.skills_dir, category_path)
            if os.path.isdir(full_path):
                skills = self._list_skills_in_dir(full_path)
                return {"type": "category", "category": category_path, "skills": skills}
            else:
                # Partial category match
                return self._fuzzy_category_match(category_path)

        # 3. Tag filter %
        if query.startswith("%"):
            tags = [t.strip() for t in query[1:].split(",")]
            skills = self._filter_by_tags(tags)
            if skills:
                return {"type": "tags", "tags": tags, "skills": skills}
            else:
                return self._closest_by_tags(tags)

        # 4. Fuzzy text search (no prefix)
        return self._embedding_similarity(query, top_k=3)

    def _build_index(self) -> dict:
        """Pre-compute index of all skills."""
        index = {
            "by_id": {},
            "by_tag": {},
            "by_category": {},
            "embeddings": {}
        }
        for root, dirs, files in os.walk(self.skills_dir):
            for file in files:
                if file.endswith(".md"):
                    path = os.path.join(root, file)
                    fm = self._extract_frontmatter(path)
                    sid = fm["skill_id"]
                    index["by_id"][sid] = path

                    cat = fm["category"]
                    index["by_category"].setdefault(cat, []).append(sid)

                    for tag in fm.get("tags", []):
                        index["by_tag"].setdefault(tag, []).append(sid)

                    # Pre-compute embedding of skill name + description
                    text = f"{fm['name']}. {fm.get('description', '')}"
                    index["embeddings"][sid] = self._embed(text)
        return index

    def _embed(self, text: str) -> list:
        """Use local sentence-transformers."""
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return model.encode(text).tolist()

    def _embedding_similarity(self, query: str, top_k: int = 3) -> dict:
        query_vec = self._embed(query)
        scores = []
        for sid, vec in self.skills_index["embeddings"].items():
            sim = self._cosine_sim(query_vec, vec)
            scores.append((sid, sim))
        scores.sort(key=lambda x: x[1], reverse=True)
        return {
            "type": "closest",
            "query": query,
            "skills": [sid for sid, _ in scores[:top_k]],
            "similarities": [sim for _, sim in scores[:top_k]]
        }

    def _cosine_sim(self, a: list, b: list) -> float:
        import math
        dot = sum(x*y for x,y in zip(a,b))
        norm_a = math.sqrt(sum(x*x for x in a))
        norm_b = math.sqrt(sum(x*x for x in b))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0
```

### 12.3 Consumer Usage Examples

**In Claude Code:**
```
/yc-fundraising-seed-round-timing          # Exact skill
/yc /fundraising                            # Browse category
/yc %seed,runway                            # Tag search
/yc how to time my fundraise                # Fuzzy search -> returns closest 3
```

**In a generic agent with Hermes spec:**
The agent loads all `specs/hermes/*.txt` into context. When the user query is received, the agent scans for signal prefixes or looks up the pre-computed `skills-index.json`, then injects the matching skill text into the system prompt.

---

## 13. Retrieval & Closest-Match Engine

### 13.1 Pre-Computed Similarity Matrix

To avoid runtime vector DB, similarity is pre-computed at generation time by the maintainer.

**File:** `data/similarity_matrix.json` (committed to repo, regenerated after each batch by `src/retrieval/resolver.py`)

```json
{
  "version": "1.0.0",
  "generated_at": "2026-07-12T00:00:00Z",
  "skills": ["yc-fundraising-seed-round-timing", "yc-fundraising-seed-round-valuation", ...],
  "matrix": [
    [1.0, 0.85, 0.42, ...],
    [0.85, 1.0, 0.38, ...],
    ...
  ],
  "tag_index": {
    "seed": ["yc-fundraising-seed-round-timing", "yc-fundraising-seed-round-valuation"],
    "runway": ["yc-fundraising-seed-round-timing", "yc-founder-mental-models-default-alive-dead"]
  }
}
```

**Generation:** After each skill is synthesized, recompute embeddings for all skills and update the matrix. This is a local CPU operation (< 5 seconds for 100 skills).

**End-user agents consume `skills-index.json` and `data/similarity_matrix.json` directly.** They do NOT run `resolver.py` or load `sentence-transformers`.

### 13.2 Closest-Match Fallback Response

When no exact skill matches, the spec file instructs the agent to return:

```markdown
## Closest Matching Skills

No specific YC skill exists for this exact query. Here are the 3 most relevant skills:

1. **[yc-fundraising-seed-round-timing](skills/fundraising/yc-fundraising-seed-round-timing.md)** (Similarity: 0.87)
   - Relevance: Discusses runway and timing, which relates to your question about burn rate.

2. **[yc-fundraising-investor-update-emails](skills/fundraising/yc-fundraising-investor-update-emails.md)** (Similarity: 0.72)
   - Relevance: Communication with investors before a formal raise.

3. **[yc-founder-mental-models-default-alive-dead](skills/founder-mental-models/yc-founder-mental-models-default-alive-dead.md)** (Similarity: 0.68)
   - Relevance: Runway calculation and survival metrics.

## General Advice

Since no YC skill directly covers your specific situation, here is general advice based on standard startup practices:
[Agent uses its own training knowledge here — NOT YC-specific quotes]

**Important:** The above general advice is not sourced from Y Combinator content. For YC-backed guidance, review the related skills listed above.
```

---

## 14. Validation & Verification Suite

### 14.1 Quote Verification (`src/validator/quote_verifier.py`)

**Algorithm:**
1. Load skill file, extract all `> "..."` blockquotes
2. For each quote, load the source chunk from `data/chunks/`
3. Compute BOTH:
   - `rapidfuzz.fuzz.ratio(quote, chunk_text)` — strict, length-normalized
   - `rapidfuzz.fuzz.partial_ratio(quote, chunk_text)` — lenient, substring-friendly
4. **Pass criteria:**
   - `ratio >= 70` AND `partial_ratio >= 85` = PASS
   - `ratio < 70` but `partial_ratio >= 85` = WARNING (flag for human review)
   - `partial_ratio < 70` = FAIL (block commit)
5. If source chunk is not found (e.g., essay not chunked), search in `data/raw/` with same dual logic.

**Why dual:** `ratio()` catches rewording that happens to share words (a short exact substring inside a heavily reworded sentence). `partial_ratio()` catches truncation where the quote is a subset of a longer chunk. Both are needed for the "exact quote fidelity" constraint.

### 14.2 Schema Validation (`src/validator/schema_validator.py`)

**Algorithm:**
1. Parse YAML frontmatter with `PyYAML`
2. Validate against `SkillFrontmatter` Pydantic model
3. Check `skill_id` matches filename
4. Check `file_path` in frontmatter matches actual path
5. Check `related_skills` all exist as files in `skills/` (populated by deferred Link pass, Section 8.4)
6. Check `tags` are all lowercase, no spaces, max 20 chars each

### 14.3 Hallucination Guard (`src/validator/hallucination_guard.py`)

**Algorithm:**
1. Extract all `(Name, Designation)` pairs from the skill file
2. Cross-reference against `content` table speakers
3. If a speaker appears in a skill but NEVER in the batch sources for that skill, FAIL
4. Check that no advice sentence contains a year, dollar amount, or company name that is not present in the source chunks (unless explicitly marked as "general knowledge")
5. **LLM-as-judge (dedicated validator, NOT rotating pool):**
   - Uses the config block `validation.dedicated_validator` from `config/providers.yml` (Section 9.1)
   - Model: `gemini-1.5-flash` at `temperature: 0.0`
   - Prompt: "Does the 'Principle' section introduce any concepts not supported by the verbatim quotes?"
   - Must return `{"supported": true}`
   - **If Gemini quota is exhausted:** Skip this step, log warning "LLM-as-judge skipped due to quota exhaustion." Rely on steps 1-4 only. Do NOT substitute another provider for this safety-critical check.

### 14.4 GitHub Actions Validation (`.github/workflows/validate.yml`)

```yaml
name: Validate Skills
on:
  pull_request:
    paths:
      - 'skills/**'
      - 'specs/**'
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python -m src.validator.run --all
      - run: python -m pytest tests/validator/
```

**Validation Command:**
```bash
python -m src.validator.run --all
```

This checks every skill file in the repo against all three validation suites.

---

## 15. Git Workflow & Publishing

### 15.1 Branching Strategy

- `main`: Only validated, published skills. Protected branch.
- `forge/batch-{batch_id}`: Working branch for a single pipeline run.
- `draft/{skill_id}`: Individual skill drafts for human review.

### 15.2 Publishing Workflow (Manual)

```bash
# 1. Maintainer runs pipeline locally
python -m src.cli forge --topic fundraising --batch-size 15

# 2. Review generated files in skills/ and specs/
# 3. Run validation locally
python -m src.validator.run --all

# 4. Create branch and commit
git checkout -b forge/batch-$(date +%s)
git add skills/ specs/ data/similarity_matrix.json skills-index.json
git commit -m "forge: batch $(date +%Y-%m-%d) - fundraising"

# 5. Push and open PR
git push origin forge/batch-$(date +%s)
# Open PR via GitHub CLI or web

# 6. GitHub Actions runs validation automatically on PR
# 7. Maintainer reviews, merges if green
# 8. Tag release
git tag -a v1.0.0 -m "Release v1.0.0 - 50 skills"
git push origin v1.0.0
```

### 15.3 Release Artifacts

Each GitHub release includes:
- Source code (auto)
- `skills-bundle.zip` (all skills + specs, generated by CI)
- `skills-index.json` (machine-readable index of all skills with tags and categories)

---

## 16. Local Development Setup (Exact Commands)

### 16.1 Prerequisites

- Python 3.11 or 3.12
- Git
- `yt-dlp` (install via `pip install yt-dlp`)
- API keys for at least one provider (DeepSeek, Kimi, GLM, or Gemini)

### 16.2 Setup Script (`scripts/setup.sh`)

```bash
#!/bin/bash
set -e

echo "OpenYC Skills - Local Setup"

# 1. Clone
git clone https://github.com/yourname/Openyc-skills.git
cd Openyc-skills

# 2. Create venv
python3.11 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Download embedding model (cached locally)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# 5. Initialize database
python -m src.cli init-db

# 6. Copy environment template
cp .env.example .env

echo "Setup complete. Edit .env with your API keys."
echo "Run: python -m src.cli --help"
```

### 16.3 Environment File (`.env.example`)

```bash
# LLM Provider API Keys (at least one required for generation)
DEEPSEEK_API_KEY=sk-...
KIMI_API_KEY=sk-...
GLM_API_KEY=...
GEMINI_API_KEY=...

# Optional: GitHub token for PR creation
GITHUB_TOKEN=ghp_...

# Pipeline config
BATCH_SIZE=15
DEFAULT_TEMPERATURE=0.3
MAX_RETRIES=3
```

### 16.4 CLI Commands

```bash
# Initialize SQLite database
python -m src.cli init-db

# Ingest a single essay
python -m src.cli ingest-library --url https://paulgraham.com/convince.html

# Ingest a YouTube video
python -m src.cli ingest-youtube --url https://youtube.com/watch?v=abc123

# Chunk all downloaded content
python -m src.cli chunk --all

# Run forge pipeline for a topic
python -m src.cli forge --topic fundraising --batch-size 15

# Run the deferred link pass (populates related_skills)
python -m src.cli link --topic fundraising

# Validate all skills
python -m src.cli validate --all

# Export specs for all skills
python -m src.cli export --all

# Generate similarity matrix and skills-index.json (build-time only)
python -m src.cli index

# Reaper: reset stale 'extracting' items
python -m src.cli reaper

# Full backfill (run once for historical content)
python -m src.cli backfill --start-date 2020-01-01
```

---

## 17. BYOK Fork Setup

**File:** `docs/BYOK.md`

```markdown
# Bring Your Own Keys (BYOK)

If you want to regenerate skills or add new content sources:

1. Fork the repository on GitHub
2. Clone your fork locally
3. Run setup: `bash scripts/setup.sh`
4. Add your API keys to `.env` (see `.env.example`)
5. Ingest new content:
   ```bash
   python -m src.cli ingest-youtube --url <url>
   python -m src.cli chunk --all
   ```
6. Run forge:
   ```bash
   python -m src.cli forge --topic <topic> --batch-size 15
   python -m src.cli link --topic <topic>
   ```
7. Validate:
   ```bash
   python -m src.cli validate --all
   ```
8. Commit and push to your fork

**Cold Start Warning:**
`data/registry.db` is gitignored. A fresh clone has zero history of what's already been ingested/published on `main`. If you run `forge` without scoping `--topic` or `--urls`, you may regenerate `_v2` duplicates of existing skills. Always scope your first run to new content, or download the maintainer's `registry.db` snapshot from releases if available.

**Quota Management:**
The system tracks your daily usage in `data/registry.db`. Run:
```bash
python -m src.cli quota
```
To see remaining tokens per provider.

**Adding New Providers:**
Edit `config/providers.yml` and add a new block. The system will auto-detect it.
```

---

## 18. Security, Compliance & Attribution

### 18.1 robots.txt Compliance

- Respect YC's `robots.txt` at `https://www.ycombinator.com/robots.txt`
- Scrape rate: Max 1 request per 2 seconds
- Use `requests.Session()` with `time.sleep(2)` between requests
- Identify via User-Agent: `OpenYC-Skills/1.0 (Research Project; contact@example.com)`

### 18.2 YouTube Terms

- Only download captions/subtitles, not video content
- Use `yt-dlp --skip-download` exclusively
- Comply with YouTube API Terms of Service
- Do not redistribute raw transcript files publicly (keep in `data/`, gitignored)

### 18.3 Attribution Requirements

Every skill file MUST contain:
- Exact speaker name and designation
- Source URL
- Timestamp (for videos) or article URL
- Batch ID for provenance

Failure to attribute results in validation failure.

### 18.4 License & Legal Note

- Code: MIT License
- Generated skill content: CC BY-SA 4.0 (attribution required, share alike)
- Raw YC content: Not redistributed; used for research/commentary purposes
- **Legal review recommended:** The project reproduces verbatim quotes from YC content at scale. While this architecture is designed for research and commentary, fair use is fact-specific and jurisdiction-dependent. Consider obtaining legal review before commercial use or large-scale redistribution.

---

## 19. Error Handling Matrix

| Error | Stage | Exact Behavior | Recovery |
|-------|-------|---------------|----------|
| HTTP 429 (rate limit) | Ingest | Sleep 60s, retry max 3x, then mark `failed` | Manual retry with `--retry-failed` |
| LLM timeout | Extract | Switch to next provider, retry 2x, then abort batch | Reaper resets state to `chunked` |
| JSON parse failure | Extract | Log raw response to `data/errors/{batch_id}.json`, retry with temperature 0.1 | Manual review |
| Cluster size = 1 | Cluster | Item returned to pool, state reset to `chunked` | Escape hatch after 3 retries: force singleton with `human_review: true` |
| Quote verification FAIL | Validate | Skill state set to `failed`, file moved to `skills/_failed/` | Manual fix or regeneration |
| Hallucination detected | Validate | Skill state set to `failed`, PR blocked | Remove offending sentence, re-run synthesis |
| Duplicate skill_id | Synthesize | Append `_v2`, `_v3` automatically | None needed |
| Provider quota exhausted | Any LLM | Error message: "All providers exhausted. Wait for UTC midnight or add more keys." | Wait or add keys |
| Stale `extracting` state | Reaper | Reset to `chunked` after 2 hours | `python -m src.cli reaper` |

---

## 20. Appendix A: Exact Prompt Templates

### A.1 Extraction Prompt

See Section 8, Stage 1. File: `src/forge/prompts/extract.j2`

### A.2 Synthesis Prompt

See Section 8, Stage 3. File: `src/forge/prompts/synthesize.j2`

### A.3 Validation Prompt (LLM-as-judge)

```jinja2
You are a fact-checker verifying that a skill file accurately represents its source content.

SOURCE QUOTES:
{% for quote in quotes %}
{{ loop.index }}. "{{ quote.text }}" — {{ quote.speaker }}
{% endfor %}

SKILL PRINCIPLE:
{{ principle }}

SKILL APPLICATION:
{{ application }}

QUESTION: Does the Skill Principle or Application introduce any claims, numbers, company names, or advice that is NOT directly supported by the Source Quotes above?

RULES:
- Generalized principles that summarize the quotes are OK.
- Specific dollar amounts, company names, or years not in quotes are NOT OK.
- Advice attributed to a speaker must be traceable to a quote.

OUTPUT JSON:
{
  "supported": true/false,
  "issues": ["Issue 1", "Issue 2"],
  "confidence": 0.0-1.0
}
```

---

## 21. Appendix B: Database Schema (SQL)

See Section 4.1 for complete schema. Migration file: `src/migrations/001_init.sql`

---

## 22. Appendix C: Configuration Files

### C.1 `config/taxonomy.yml`

See Section 6.1.

### C.2 `config/providers.yml`

See Section 9.1.

### C.3 `config/pipeline.yml`

```yaml
chunking:
  essay:
    min_words: 200
    max_words: 800
    target_words: 600
    overlap_sentences: 1
    split_header: "## "

  transcript:
    min_words: 400
    max_words: 800
    target_words: 600
    merge_same_speaker: true
    split_on_speaker_change: true

clustering:
  embedding_model: "all-MiniLM-L6-v2"
  algorithm: "agglomerative"
  distance_threshold: 0.18
  metric: "cosine"
  linkage: "average"
  min_cluster_size: 2

extraction:
  min_items_per_chunk: 1
  max_items_per_chunk: 20
  temperature: 0.3
  max_tokens: 8000

synthesis:
  temperature: 0.3
  max_tokens: 8000
  min_confidence: 0.55
  max_quotes: 3

linking:
  max_related_skills: 3
  similarity_threshold: 0.65

validation:
  quote_fuzzy_ratio: 70
  quote_fuzzy_partial_ratio: 85
  quote_warning_threshold: 70
  hallucination_check: true

export:
  formats:
    - mcp
    - openai
    - hermes
```

---

## 23. Implementation Checklist

Use this checklist to verify the AI coding agent has implemented everything correctly:

- [ ] Repository structure matches Section 2 exactly (including `src/retrieval/`, `data/errors/`)
- [ ] SQLite schema from Section 4.1 is implemented without modification (`chunk_index`, `extracting`, `linked`, `computed_confidence`)
- [ ] Content IDs use SHA256 of full URL, not slug (Section 4.2)
- [ ] `yt-dlp` wrapper uses exact command from Section 5.2
- [ ] Chunking algorithms match Section 7 parameters exactly (`chunk_index` not `index`)
- [ ] Batch size is configurable but defaults to 15, minimum 5
- [ ] Extraction prompt uses `in_batch_index` for contradictions (Section 8.1)
- [ ] State machine includes `extracting` intermediate state with reaper recovery (Section 8.0)
- [ ] Clustering uses `AgglomerativeClustering` with exact parameters from Section 8.2
- [ ] Synthesis prompt sets `confidence: 0.0` and leaves `related_skills: []` (Section 8.3)
- [ ] Confidence is computed from cluster metrics, not LLM self-report (Section 8.3, step 7)
- [ ] Deferred Link pass (`src/forge/linker.py`) populates `related_skills` from similarity matrix (Section 8.4)
- [ ] Skill Markdown format matches Section 10.1 exactly (every section present)
- [ ] Pydantic models match Section 10.2 exactly (regex allows 6 words)
- [ ] MCP specs include `fallback` block with `use_agent_knowledge: true` and `invent_quotes: false`
- [ ] OpenAI specs include metadata with fallback rules
- [ ] Hermes specs include FALLBACK instruction
- [ ] Signal resolver is build-time only; `skills-index.json` and `similarity_matrix.json` are committed (Section 12, 13)
- [ ] Similarity matrix is pre-computed and committed (Section 13.1)
- [ ] Quote verifier uses BOTH `ratio >= 70` AND `partial_ratio >= 85` (Section 14.1)
- [ ] Hallucination guard uses dedicated validator config with `fail_open` fallback (Section 14.3)
- [ ] GitHub Actions only validates, does NOT generate (Section 14.4)
- [ ] `.gitignore` excludes `data/raw/`, `data/chunks/`, `data/registry.db`, `.env`
- [ ] `requirements.txt` pins exact versions from Section 3
- [ ] CLI entry point is `python -m src.cli` (Section 16.4)
- [ ] Reaper command exists: `python -m src.cli reaper` (Section 16.4)
- [ ] BYOK documentation exists at `docs/BYOK.md` with cold-start warning (Section 17)
- [ ] All source content is gitignored; only skills, specs, and pre-computed indices are published
- [ ] Legal note in Section 18.4 recommends review rather than asserting fair use

---

**End of Specification**