# Bring Your Own Keys (BYOK) Guide

This guide is for contributors who want to fork the repository, ingest their own content from YC, and generate new skills using the Forge.

## ⚠️ Cold-Start Warning (CRITICAL)

**`data/registry.db` is gitignored.** A fresh clone has zero history of what's already been ingested and published on `main`. 

If you run `forge` without scoping `--topic` or `--urls`, you may unintentionally regenerate duplicate versions (`_v2`, `_v3`) of existing skills already built by other contributors.

**Always scope your first run** to the new content you are actively ingesting.

## 1. Fork & Setup

1. **Fork and clone** the repository to your local machine.
2. Initialize a Python 3.11 virtual environment.
3. Install dependencies and initialize the DB:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   
   # Download the local embedding model
   python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   
   # Initialize SQLite database
   python -m src.cli init-db
   ```
4. Copy `.env.example` to `.env` and configure your API keys.

## 2. Ingest New Content

Download raw content from the YC Library or YC YouTube channels:

**Library Essays:**
```bash
python -m src.cli ingest-library --url "https://www.ycombinator.com/library/example-essay"
```

**YouTube Transcripts:**
```bash
python -m src.cli ingest-youtube --url "https://www.youtube.com/watch?v=exampleID"
```

## 3. Run Forge

Chunk the freshly ingested content, and then execute the core Forge pipeline scoped specifically to your topic.

```bash
# Chunk all newly downloaded content
python -m src.cli chunk --all

# Run the Forge (Extraction, Clustering, Synthesis)
python -m src.cli forge --topic "pricing" --batch-size 15

# Populate the related_skills frontmatter graph
python -m src.cli link --topic "pricing"
```

## 4. Validate & Export

Once your skills are synthesized in `skills/`, they must pass the strict three-layer validation suite (schema check, quote verification, and hallucination guard) before exporting formats and generating the index.

```bash
# 1. Validate all skills
python -m src.cli validate --all

# 2. Export specs (MCP, OpenAI, Hermes)
python -m src.cli export --all

# 3. Update indices and similarity matrix
python -m src.cli index
```

If validation fails, the offending skill will automatically be moved to `skills/_failed/` for your manual review.

## 5. Quota Management

The LLM pipeline tracks your daily API usage locally in `data/registry.db`. You can view your remaining capacity and tokens used at any time:

```bash
python -m src.cli quota
```

## 6. Adding New Providers

If you want to use an LLM provider not currently listed, simply open `config/providers.yml` and add a new block. The system will auto-detect it. Make sure you also define your API key matching the new provider block inside your `.env` file!

## 7. Adding New Categories

Skills are grouped strictly by categories. If your content requires a brand-new category (beyond the 8 default ones):
1. Add the category and its subcategories to `config/taxonomy.yml`.
2. Create the physical directory: `mkdir skills/{category}/`.
3. Update `docs/TAXONOMY.md` to document your addition for other consumers.
