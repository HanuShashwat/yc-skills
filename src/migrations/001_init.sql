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
