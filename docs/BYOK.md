# Bring Your Own Keys (BYOK) Guide

> **A step-by-step guide for contributors who want to fork this repository, ingest their own YC content, and generate new skills.**

---

## Table of Contents

1. [What This Guide Covers](#what-this-guide-covers)
2. [How the BYOK Model Works](#how-the-byok-model-works)
3. [Prerequisites](#prerequisites)
4. [Step 1: Fork & Clone](#step-1-fork--clone)
5. [Step 2: Set Up Your Python Environment](#step-2-set-up-your-python-environment)
6. [Step 3: Install Dependencies](#step-3-install-dependencies)
7. [Step 4: Download the Embedding Model](#step-4-download-the-embedding-model)
8. [Step 5: Initialize the Database](#step-5-initialize-the-database)
9. [Step 6: Configure Your API Keys](#step-6-configure-your-api-keys)
10. [Understanding the Cold-Start Problem](#understanding-the-cold-start-problem)
11. [Ingesting New Content](#ingesting-new-content)
12. [Running the Forge Pipeline](#running-the-forge-pipeline)
13. [Validating Your Skills](#validating-your-skills)
14. [Exporting Spec Files](#exporting-spec-files)
15. [Generating the Index](#generating-the-index)
16. [Quota Management](#quota-management)
17. [Adding New LLM Providers](#adding-new-llm-providers)
18. [Adding New Categories](#adding-new-categories)
19. [Submitting Your Contribution (Pull Request)](#submitting-your-contribution-pull-request)
20. [Troubleshooting Common Issues](#troubleshooting-common-issues)
21. [Complete Workflow Cheat Sheet](#complete-workflow-cheat-sheet)

---

## What This Guide Covers

This guide walks you through the entire process of:

1. **Setting up** a local development environment from scratch
2. **Ingesting** new YC content (Library essays or YouTube videos)
3. **Running the pipeline** to generate new skill files
4. **Validating** the generated skills
5. **Submitting** your contributions back to the main repository

By the end, you'll have generated new skill files locally and be ready to open a pull request.

---

## How the BYOK Model Works

"BYOK" stands for **Bring Your Own Keys**. Here's why:

- The pipeline uses **Large Language Models (LLMs)** to extract advice from YC content and synthesize skill files. These LLM calls cost money (or consume API quota).
- Instead of the project paying for everyone's LLM usage, each contributor supplies their own API keys. You sign up with one or more LLM providers, get your own API key, and use your own quota.
- The project supports **4 LLM providers:** DeepSeek, Kimi (Moonshot), GLM (BigModel), and Gemini. You only need **at least one** — the system will use whichever you have available.

**Cost estimate:** A typical batch of 15 content items costs approximately $0.01–$0.10 in API usage, depending on the provider.

---

## Prerequisites

Before you begin, make sure you have the following installed on your computer:

| Requirement | Version | Why It's Needed | How to Check if You Have It |
|-------------|---------|----------------|---------------------------|
| **Python** | 3.11 or 3.12 (3.11 recommended) | All project code is Python | Run: `python --version` or `python3.11 --version` |
| **Git** | Any recent version | Version control, cloning the repo | Run: `git --version` |
| **pip** | 24.x+ (will be upgraded) | Python package manager | Comes with Python |

You also need **at least one LLM API key** from any of these providers:

| Provider | Sign-Up Link | Free Tier? |
|----------|-------------|------------|
| DeepSeek | [platform.deepseek.com](https://platform.deepseek.com/) | Yes, generous free quota |
| Kimi (Moonshot) | [platform.moonshot.cn](https://platform.moonshot.cn/) | Yes |
| GLM (BigModel) | [open.bigmodel.cn](https://open.bigmodel.cn/) | Yes |
| Gemini (Google) | [ai.google.dev](https://ai.google.dev/) | Yes, generous free quota |

> **Tip:** If you're unsure which to pick, start with **Gemini** — it has the largest free quota (1,500,000 tokens/day and 150 requests/day) and is used for both generation and the dedicated validation step.

---

## Step 1: Fork & Clone

### Why Fork?

Forking creates your own copy of the repository on GitHub, so you can make changes without affecting the main project. After you're done, you'll submit a pull request to merge your changes back.

### How to Fork

1. Go to the repository: `https://github.com/HanuShashwat/yc-skills`
2. Click the **"Fork"** button in the top right
3. This creates a copy at `https://github.com/YOUR_USERNAME/yc-skills`

### How to Clone Your Fork

```bash
# Clone YOUR fork (replace YOUR_USERNAME with your GitHub username)
git clone https://github.com/YOUR_USERNAME/yc-skills.git
cd yc-skills
```

---

## Step 2: Set Up Your Python Environment

A **virtual environment** is an isolated Python installation that keeps this project's dependencies separate from everything else on your computer. This prevents version conflicts.

```bash
# Create a virtual environment using Python 3.11
python3.11 -m venv .venv
```

> **Note:** On Windows, you may need to use `python` instead of `python3.11` if Python 3.11 is your default.

### Activate the Virtual Environment

You need to activate the virtual environment every time you open a new terminal to work on this project.

**On Linux or macOS:**
```bash
source .venv/bin/activate
```

**On Windows (Command Prompt):**
```cmd
.venv\Scripts\activate
```

**On Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**How to know it's working:** Your terminal prompt should now show `(.venv)` at the beginning:
```
(.venv) $ _
```

---

## Step 3: Install Dependencies

With your virtual environment activated, install all required Python packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs all the libraries the project needs, including:
- `requests` and `beautifulsoup4` — for scraping YC Library essays
- `yt-dlp` — for downloading YouTube transcripts
- `sentence-transformers` — for computing text embeddings (used in clustering)
- `pydantic` — for data validation
- `openai` — the unified client for all LLM providers (they all use OpenAI-compatible APIs)
- `rapidfuzz` — for fuzzy string matching (quote verification)
- `Jinja2` — for prompt templates
- And more (see `requirements.txt` for the full list)

**Expected time:** 1–3 minutes depending on your internet speed.

---

## Step 4: Download the Embedding Model

The clustering step uses a local machine learning model called `all-MiniLM-L6-v2` to convert text into 384-dimensional vectors. This model runs entirely on your CPU — no GPU needed.

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

**What this does:** Downloads approximately 90MB of model weights and caches them locally. This only needs to be done once — subsequent runs use the cached version.

**If you see errors:** Make sure you've activated your virtual environment and installed requirements.txt first.

---

## Step 5: Initialize the Database

The project uses a local SQLite database (`data/registry.db`) to track the state of every piece of content through the pipeline.

```bash
python -m src.cli init-db
```

**What this does:**
- Creates the `data/` directory if it doesn't exist
- Creates `data/registry.db` with 7 tables: `content`, `chunks`, `extracted_items`, `clusters`, `cluster_items`, `skills`, `usage_log`
- This command is **idempotent** — running it multiple times is safe; it won't overwrite existing data

**You can verify it worked:**
```bash
# Check the database exists
ls data/registry.db

# (Optional) Check the tables were created
python -c "import sqlite3; conn = sqlite3.connect('data/registry.db'); print([row[0] for row in conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall()])"
```

Expected output:
```
['content', 'chunks', 'extracted_items', 'clusters', 'cluster_items', 'skills', 'usage_log']
```

---

## Step 6: Configure Your API Keys

### Copy the Template

```bash
cp .env.example .env
```

### Edit Your `.env` File

Open `.env` in your text editor and replace the placeholder values with your real API keys:

```bash
# .env file — DO NOT commit this to Git!

# LLM Provider API Keys (you need at least ONE)
DEEPSEEK_API_KEY=sk-your-real-deepseek-key-here
KIMI_API_KEY=sk-your-real-kimi-key-here
GLM_API_KEY=your-real-glm-key-here
GEMINI_API_KEY=your-real-gemini-key-here

# Optional: GitHub token for automatic PR creation
GITHUB_TOKEN=ghp_your-token-here

# Pipeline defaults (usually fine as-is)
BATCH_SIZE=15
DEFAULT_TEMPERATURE=0.3
MAX_RETRIES=3
```

**Important:**
- You only need **at least one** LLM API key. Leave the others as the placeholder value if you don't have them — the system will skip unavailable providers.
- The `.env` file is **gitignored** — it will never be uploaded to GitHub. Your keys are safe.
- If you have a Gemini key, that's especially useful because the hallucination guard (validation step 3) uses Gemini specifically.

---

## Understanding the Cold-Start Problem

> **⚠️ CRITICAL: Read this before running the pipeline for the first time.**

### The Problem

The file `data/registry.db` is **gitignored** — it does NOT come with the repository when you clone it. This means your fresh database has **zero knowledge** of what content has already been ingested and what skills have already been published on the main branch.

### Why This Matters

If you run `python -m src.cli forge` without specifying `--topic` or specific URLs, the system might:
1. Select content that was already processed by another contributor
2. Generate duplicate versions of skills that already exist (e.g., `yc-fundraising-seed-round-timing_v2`)
3. Create confusion and wasted API quota

### The Solution

**Always scope your first run** to specific new content you're adding:

```bash
# GOOD: Specific URLs you're adding
python -m src.cli ingest-youtube --url "https://www.youtube.com/watch?v=YOUR_NEW_VIDEO"
python -m src.cli chunk --all
python -m src.cli forge --topic "fundraising" --batch-size 15

# BAD: Running forge without scoping
python -m src.cli forge                     # <-- DON'T DO THIS on first run
python -m src.cli forge --batch-size 100    # <-- DON'T DO THIS on first run
```

### Additional Safeguards

- Check the existing `skills/` directory to see what skills already exist before generating new ones
- Use `--topic` flag to limit processing to the topic you're working on
- If available, download the maintainer's `registry.db` snapshot from GitHub Releases

---

## Ingesting New Content

### Ingesting a YC Library Essay

YC Library essays are blog posts published on `ycombinator.com/library/`. To ingest one:

```bash
python -m src.cli ingest-library --url "https://www.ycombinator.com/library/example-essay-slug"
```

**What happens behind the scenes:**
1. Downloads the page HTML using `requests` (with a 30-second timeout)
2. Identifies itself with User-Agent: `YC-Skills-Forge/1.0 (Research Project; contact@example.com)`
3. Parses the HTML with BeautifulSoup4, extracting the article body
4. Removes navigation, footer, scripts, styles, ads, and newsletter boxes
5. Converts to Markdown using `markdownify`
6. Saves to `data/raw/library/{content_id}.md`
7. Computes a SHA256 hash of the content
8. Generates content ID: `lib_` + first 12 characters of SHA256(url)
9. Tries to identify the speaker using `src/ingest/known_authors.py`
10. Inserts into the `content` database table with state `downloaded` (or `discovered` if speaker couldn't be identified)
11. Waits 2 seconds before processing the next URL (rate limiting)

**Ingesting multiple essays at once:**
```bash
python -m src.cli ingest-library --urls \
    "https://www.ycombinator.com/library/essay-1" \
    "https://www.ycombinator.com/library/essay-2" \
    "https://www.ycombinator.com/library/essay-3"
```

### Ingesting a YouTube Video

YC has several YouTube channels with startup advice videos. To ingest one:

```bash
python -m src.cli ingest-youtube --url "https://www.youtube.com/watch?v=VIDEO_ID"
```

**What happens behind the scenes:**
1. Runs `yt-dlp` as a subprocess with these exact flags:
   - `--write-subs` — download subtitle files
   - `--sub-langs en` — only English subtitles
   - `--sub-format json3` — JSON format with timestamps
   - `--skip-download` — do NOT download the video file
   - `--write-info-json` — download metadata
2. Reads the metadata JSON for title, uploader, upload date, and description
3. Reads the subtitle file for transcript segments
4. Tries to identify the speaker from the video description using regex patterns
5. Saves transcript as `{video_id}.transcript.txt` and metadata as `{video_id}.meta.json` in `data/raw/youtube/`
6. Generates content ID: `yt_{video_id}` (the 11-character YouTube video ID)
7. Inserts into the `content` database table

**Important:** Only English-language subtitles are downloaded. If a video has no English captions, the transcript will be empty and the content will need manual review.

---

## Running the Forge Pipeline

The "forge" is the core of the pipeline. It takes chunked content and transforms it into skill files through three main stages: extraction, clustering, and synthesis.

### Step 1: Chunk All Downloaded Content

Before running the forge, you need to chunk all content that has been downloaded but not yet chunked:

```bash
python -m src.cli chunk --all
```

This processes all content with state `downloaded` → splits into chunks → saves to `data/chunks/` → updates state to `chunked`.

### Step 2: Run the Forge

```bash
python -m src.cli forge --topic "your-topic-here" --batch-size 15
```

**Parameters explained:**

| Parameter | Required? | Default | What It Does |
|-----------|-----------|---------|--------------|
| `--topic` | Recommended | Auto-selects topic with most unprocessed content | Limits processing to content matching this topic |
| `--batch-size` | No | 15 | How many content items to process (min: 5, max: 20) |

**What the forge does internally:**

1. **Batch Selection:** Queries the database for up to `--batch-size` content items with state `chunked` and matching `--topic`. If fewer than 5 items are available, it aborts (not enough data for a meaningful batch). Sets state to `extracting`.

2. **Extraction (LLM Call #1):** Loads all chunks for the batch, renders the extraction prompt template (`src/forge/prompts/extract.j2`), calls the LLM, parses the JSON response, and inserts extracted items into the `extracted_items` table. Sets state to `extracted`.

3. **Clustering (No LLM):** Embeds all extracted quotes using the local `all-MiniLM-L6-v2` model, then uses Agglomerative Clustering to group similar items. Clusters with fewer than 2 items are rejected. Sets state to `clustered`.

4. **Synthesis (LLM Call #2):** For each cluster, renders the synthesis prompt template (`src/forge/prompts/synthesize.j2`), calls the LLM, parses the JSON response, computes confidence from cluster metrics (NOT from the LLM), and writes the Markdown skill file to `skills/{category}/`. Sets state to `synthesized`.

### Step 3: Populate Related Skills

After synthesis, run the deferred link pass to populate the `related_skills` field:

```bash
python -m src.cli link --topic "your-topic-here"
```

This uses the pre-computed similarity matrix to find the top 3 most similar existing skills for each new skill. It updates both the skill file's YAML frontmatter and the database.

---

## Validating Your Skills

Every skill must pass the three-layer validation suite before it can be published:

```bash
python -m src.cli validate --all
```

### What Gets Checked

| Check | What It Does | Pass Criteria |
|-------|-------------|---------------|
| **Quote Verification** | Fuzzy-matches each quote against the source chunk | `ratio ≥ 70` AND `partial_ratio ≥ 85` |
| **Schema Validation** | Validates YAML frontmatter against Pydantic model | All required fields present and valid |
| **Hallucination Guard** | Cross-references speakers and uses LLM-as-judge | No invented speakers, quotes, or facts |

### If Validation Fails

- The offending skill is moved to `skills/_failed/` for your manual review
- The skill's state is set to `failed` in the database
- You can fix the issue and re-run validation

### Common Validation Failures

| Error | Cause | Fix |
|-------|-------|-----|
| Quote verification FAIL | LLM paraphrased a quote instead of using verbatim text | Re-run synthesis or manually correct the quote |
| Schema validation FAIL | Missing required field or invalid format | Check the YAML frontmatter against the expected format |
| Hallucination detected | LLM invented a speaker or fact not in the sources | Remove the fabricated content and re-validate |

---

## Exporting Spec Files

After validation, generate spec files in all three formats:

```bash
python -m src.cli export --all
```

This creates:
- `specs/mcp/{skill_id}.json` — for Claude Code and MCP-compatible agents
- `specs/openai/{skill_id}.json` — for GPT and OpenAI API integrations
- `specs/hermes/{skill_id}.txt` — for local models (Ollama, llama.cpp)

Each spec file wraps the skill's content in the format that specific AI framework expects.

---

## Generating the Index

After exporting, regenerate the machine-readable index files:

```bash
python -m src.cli index
```

This generates/updates two files:
1. **`skills-index.json`** (repo root) — Maps skill IDs, tags, and categories to file paths. Used by AI agents to find skills.
2. **`data/similarity_matrix.json`** — Pre-computed cosine similarity between all skills. Used for fuzzy search and related_skills population.

Both files are committed to the repository.

---

## Quota Management

The pipeline tracks your daily API usage in `data/registry.db`. Each LLM provider has daily token and request limits.

### Check Your Quota

```bash
python -m src.cli quota
```

This shows:
- How many tokens you've used today for each provider
- How many requests you've made
- How much capacity remains

### Quota Limits (Defaults)

| Provider | Daily Token Limit | Daily Request Limit | Priority |
|----------|-------------------|---------------------|----------|
| DeepSeek | 1,000,000 | 100 | 1 (first choice) |
| Kimi | 500,000 | 50 | 2 |
| GLM | 500,000 | 50 | 3 |
| Gemini | 1,500,000 | 150 | 4 |

### How Rotation Works

The system automatically picks the best available provider:
1. Checks remaining quota for each provider (with a 10% buffer)
2. Selects the available provider with the highest priority (lowest number)
3. If all providers are exhausted, it raises an error

**Quotas reset at UTC midnight (00:00 UTC).**

### If You're Running Low

- Wait until UTC midnight for quotas to reset
- Add another provider's API key to your `.env` file
- Reduce `--batch-size` to use fewer tokens per run

---

## Adding New LLM Providers

If you want to use a provider not currently listed, you can add it by editing `config/providers.yml`:

```yaml
providers:
  # ... existing providers ...

  my_new_provider:
    api_key: ${MY_NEW_PROVIDER_API_KEY}
    base_url: "https://api.newprovider.com/v1"
    model: "their-model-name"
    daily_token_limit: 500_000
    daily_request_limit: 50
    priority: 5                # Lower number = higher priority
    timeout: 120
    max_retries: 3
```

Then add your API key to `.env`:
```bash
MY_NEW_PROVIDER_API_KEY=your-key-here
```

**Requirements for new providers:**
- Must support the OpenAI-compatible chat completions API (`/chat/completions` endpoint)
- Must support JSON response format (either via `response_format` parameter or through prompt instructions)

---

## Adding New Categories

Skills are organized into 8 fixed categories. If your content genuinely doesn't fit any existing category, you can propose a new one:

### Step 1: Modify `config/taxonomy.yml`

Add your new category and subcategories:

```yaml
taxonomy:
  # ... existing categories ...

  your-new-category:
    description: Brief description of what this covers
    subcategories:
      - subcategory-one
      - subcategory-two
      - subcategory-three
```

### Step 2: Create the Directory

```bash
mkdir skills/your-new-category/
```

### Step 3: Update Documentation

Update `docs/TAXONOMY.md` to document your new category.

### Step 4: Submit as a Pull Request

New categories require explicit approval via a PR — they can't be added silently.

> **Important:** Before proposing a new category, carefully check whether your content fits into an existing category or subcategory. The taxonomy is intentionally kept small to prevent sprawl and overlap.

---

## Submitting Your Contribution (Pull Request)

After you've generated, validated, and exported your skills:

### Step 1: Create a Branch

```bash
git checkout -b forge/batch-$(date +%s)
# On Windows PowerShell:
# git checkout -b "forge/batch-$(Get-Date -UFormat %s)"
```

### Step 2: Stage the Generated Files

Only commit the files that are meant to be shared:

```bash
git add skills/ specs/ data/similarity_matrix.json skills-index.json
```

**Do NOT commit:**
- `data/registry.db` (your local state)
- `data/raw/` (raw source content)
- `data/chunks/` (intermediate files)
- `.env` (your secret API keys)

### Step 3: Commit and Push

```bash
git commit -m "forge: batch $(date +%Y-%m-%d) - topic-name"
git push origin HEAD
```

### Step 4: Open a Pull Request on GitHub

1. Go to your fork on GitHub
2. Click "Compare & pull request"
3. Describe what content you ingested and what skills were generated
4. Submit the PR

### Step 5: Wait for CI Validation

GitHub Actions automatically runs the validation suite on your PR:
- Schema validation
- Quote verification
- (Hallucination guard may require a Gemini key in CI)

If validation fails, fix the issues and push again.

---

## Troubleshooting Common Issues

### "ModuleNotFoundError: No module named 'src'"

**Cause:** You're running the command from the wrong directory, or your virtual environment isn't activated.

**Fix:**
```bash
cd /path/to/yc-skills           # Make sure you're in the project root
source .venv/bin/activate        # Activate the virtual environment
python -m src.cli init-db        # Try again
```

### "All providers exhausted. Wait for UTC midnight reset."

**Cause:** All configured LLM providers have used up their daily quota.

**Fix:** Wait until UTC midnight, add another provider's API key, or reduce your batch size.

### "Minimum batch size is 5. Only N items available."

**Cause:** Not enough content with state `chunked` for the specified topic.

**Fix:** Ingest more content for that topic:
```bash
python -m src.cli ingest-youtube --url "https://youtube.com/watch?v=..."
python -m src.cli chunk --all
```

### "yt-dlp: command not found"

**Cause:** yt-dlp isn't installed or isn't in your PATH.

**Fix:**
```bash
pip install yt-dlp
```

### "sqlite3.OperationalError: no such table: content"

**Cause:** The database hasn't been initialized.

**Fix:**
```bash
python -m src.cli init-db
```

### Items stuck in "extracting" state

**Cause:** A previous pipeline run crashed mid-extraction.

**Fix:**
```bash
python -m src.cli reaper
```
This resets items stuck in `extracting` for over 2 hours back to `chunked` so they can be reprocessed.

---

## Complete Workflow Cheat Sheet

Here's the entire contributor workflow in one quick reference:

```bash
# === ONE-TIME SETUP ===
git clone https://github.com/YOUR_USERNAME/yc-skills.git
cd yc-skills
python3.11 -m venv .venv
source .venv/bin/activate                   # or .venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
python -m src.cli init-db
cp .env.example .env
# Edit .env with your real API keys

# === FOR EACH NEW BATCH ===
# 1. Ingest content
python -m src.cli ingest-youtube --url "https://youtube.com/watch?v=..."
# or: python -m src.cli ingest-library --url "https://ycombinator.com/library/..."

# 2. Chunk
python -m src.cli chunk --all

# 3. Forge (extract + cluster + synthesize)
python -m src.cli forge --topic "your-topic" --batch-size 15

# 4. Link (populate related_skills)
python -m src.cli link --topic "your-topic"

# 5. Export (MCP + OpenAI + Hermes specs)
python -m src.cli export --all

# 6. Validate (3-layer check)
python -m src.cli validate --all

# 7. Index (update skills-index.json + similarity matrix)
python -m src.cli index

# 8. Commit & push
git checkout -b forge/batch-$(date +%s)
git add skills/ specs/ data/similarity_matrix.json skills-index.json
git commit -m "forge: batch $(date +%Y-%m-%d) - topic-name"
git push origin HEAD
# Open PR on GitHub
```
