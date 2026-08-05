# Consuming OpenOpenYC Skills — A Complete Guide

> **How to use OpenOpenYC Skills in your AI agent, chatbot, or application. No Python installation, no API keys, no database — just static files from GitHub.**

---

## Table of Contents

1. [Who Is This Guide For?](#who-is-this-guide-for)
2. [The Core Idea](#the-core-idea)
3. [What You're Getting](#what-youre-getting)
4. [Getting the Files](#getting-the-files)
5. [Understanding Skill Files (`.md`)](#understanding-skill-files-md)
6. [Understanding Spec Files](#understanding-spec-files)
7. [Export Format 1: MCP (Model Context Protocol)](#export-format-1-mcp-model-context-protocol)
8. [Export Format 2: OpenAI Function Schema](#export-format-2-openai-function-schema)
9. [Export Format 3: Hermes Plain-Text (Local Models)](#export-format-3-hermes-plain-text-local-models)
10. [Finding Skills — Signal Resolution & Routing](#finding-skills--signal-resolution--routing)
11. [Using `skills-index.json` for Lookups](#using-skills-indexjson-for-lookups)
12. [Using `similarity_matrix.json` for Fuzzy Search](#using-similarity_matrixjson-for-fuzzy-search)
13. [Fallback Behavior — The Most Important Rule](#fallback-behavior--the-most-important-rule)
14. [Integration Examples](#integration-examples)
15. [Understanding Skill Metadata Fields](#understanding-skill-metadata-fields)
16. [Frequently Asked Questions](#frequently-asked-questions)

---

## Who Is This Guide For?

This guide is for **AI agent developers** who want to give their AI agent the ability to provide startup advice backed by Y Combinator content. This includes:

- **Chatbot builders** — adding startup advice to a chatbot or virtual assistant
- **AI agent frameworks** — building agents with Claude Code, Cursor, Copilot, or custom frameworks
- **Local model users** — running Ollama, llama.cpp, or similar on your own machine
- **Application developers** — integrating YC advice into a startup toolkit or platform

**You do NOT need to:**
- Install Python
- Run any code from this repository
- Have any API keys
- Set up any database
- Download any machine learning models

Everything you need is a set of static files that you download (or clone) from GitHub.

---

## The Core Idea

OpenOpenYC Skills publishes structured, verified startup advice as **static files** in this GitHub repository. Your AI agent reads these files and uses them to answer founders' questions with accurate, well-attributed YC advice.

Here's the mental model:

```
┌─────────────────────┐      ┌──────────────────┐      ┌───────────────────┐
│  This GitHub Repo   │      │   Your AI Agent   │      │   End User        │
│                     │      │                   │      │   (a Founder)     │
│  • skills/*.md      │─────→│  Loads skill      │─────→│  Asks: "When      │
│  • specs/*.json     │      │  files at startup │      │  should I raise   │
│  • skills-index.json│      │  or on-demand     │      │  my seed round?"  │
│  • similarity_matrix│      │                   │      │                   │
└─────────────────────┘      └──────────────────┘      └───────────────────┘
```

There is no API call back to this repository. No server. No runtime dependency. Your agent has the knowledge locally.

---

## What You're Getting

When you download or clone this repository, the files relevant to you as a consumer are:

| File/Directory | What It Contains | When to Use It |
|---------------|-----------------|----------------|
| `skills/{category}/{skill_id}.md` | The actual skill content — principle, verbatim quotes, application instructions, edge cases | When you want the full knowledge content |
| `specs/mcp/{skill_id}.json` | MCP (Model Context Protocol) spec | If your agent uses Claude Code or MCP-compatible frameworks |
| `specs/openai/{skill_id}.json` | OpenAI function-calling spec | If your agent uses GPT or the OpenAI API |
| `specs/hermes/{skill_id}.txt` | Plain-text system prompt fragment | If your agent runs on a local model (Ollama, llama.cpp) |
| `skills-index.json` | Machine-readable index of ALL skills | For looking up skills by ID, category, or tag |
| `data/similarity_matrix.json` | Pre-computed similarity scores between all skills | For fuzzy/semantic skill search |

**You can ignore everything else** (`src/`, `config/`, `data/raw/`, `data/chunks/`, etc.). Those are for contributors who generate skills, not for consumers who use them.

---

## Getting the Files

### Option 1: Clone the Entire Repository

```bash
git clone https://github.com/HanuShashwat/openyc-skills.git
```

Then access files at `openyc-skills/skills/`, `openyc-skills/specs/`, etc.

### Option 2: Download a Release Bundle

Check the [Releases page](https://github.com/HanuShashwat/openyc-skills/releases) for `skills-bundle.zip` containing all skills, specs, and index files.

### Option 3: Fetch Individual Files via GitHub Raw URLs

You can fetch any file directly over HTTPS:

```
https://raw.githubusercontent.com/HanuShashwat/openyc-skills/main/skills/fundraising/yc-fundraising-seed-round-timing.md
https://raw.githubusercontent.com/HanuShashwat/openyc-skills/main/specs/mcp/yc-fundraising-seed-round-timing.json
https://raw.githubusercontent.com/HanuShashwat/openyc-skills/main/skills-index.json
```

This is useful for agents that load skills on-demand without cloning the full repo.

---

## Understanding Skill Files (`.md`)

Skill files are the core knowledge units. Each one is a Markdown document with YAML frontmatter at the top. Here's a fully annotated example:

```yaml
---
# IDENTITY: What is this skill?
skill_id: yc-fundraising-seed-round-timing     # Unique identifier
name: Seed Round Timing                         # Human-readable name
version: "1.0.0"                                # Version (semantic versioning)
category: fundraising                           # One of 8 categories

# DISCOVERY: How to find this skill
tags:
  - seed            # Tag for filtering
  - runway          # Tag for filtering
  - timing          # Tag for filtering

# QUALITY METRICS
source_count: 12    # Number of source documents that contributed
quote_count: 3      # Number of verbatim quotes included
confidence: 0.92    # 0.0 to 1.0, computed from cluster consensus metrics

# RELATIONSHIPS: What other skills are related?
related_skills:
  - id: yc-fundraising-seed-round-valuation
    similarity: 0.88      # Cosine similarity (0.0 to 1.0)

# PROVENANCE: Where did this content come from?
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

# VALIDATION: Has this passed quality checks?
validation:
  quote_verified: true        # Fuzzy-matched against source
  schema_valid: true          # Passed Pydantic schema validation
  hallucination_check: true   # Passed LLM-as-judge fact check
  human_review: false         # Not flagged for human review
---
```

**Below the frontmatter** is the actual skill content in Markdown:

| Section | Purpose |
|---------|---------|
| `# Skill Name` | Title heading |
| `## Principle` | 2-4 sentence unified principle distilled from multiple sources |
| `## Verbatim Quotes` | Exact quotes from YC speakers with full attribution (name, title, source URL, timestamp) |
| `## Personalized Application` | Instructions for how an AI agent should apply this advice, including follow-up questions to ask |
| `## Edge Cases` | Situations where this advice needs modification |
| `## Related Skills` | Links to related skill files with descriptions |
| `## Fallback Behavior` | What to do when the user's question doesn't exactly match this skill |

---

## Understanding Spec Files

Spec files are **wrappers around skill files** that format the skill's metadata for specific AI agent frameworks. They contain routing information, input schemas, and fallback rules — but the actual knowledge content lives in the skill `.md` file.

The spec file tells your agent framework:
1. **What parameters to collect** from the user (e.g., `runway_months`, `question`)
2. **Where to find the full knowledge** (path to the skill `.md` file)
3. **What tags to use** for routing
4. **What to do** if the skill doesn't match the user's question (fallback behavior)

---

## Export Format 1: MCP (Model Context Protocol)

**File location:** `specs/mcp/{skill_id}.json`

**Used by:** Claude Code, and any agent framework that supports the Model Context Protocol.

**What is MCP?** The Model Context Protocol (MCP) is a standard for defining "tools" that AI agents can invoke. Each MCP spec defines a tool with a name, description, input schema, and handler.

### Example MCP Spec

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

### Field-by-Field Explanation

| Field | What It Means |
|-------|---------------|
| `name` | The tool name (hyphens replaced with underscores for function-name compatibility) |
| `description` | Human-readable description including the YC speakers whose advice is included |
| `inputSchema` | JSON Schema defining what parameters the agent should collect from the user before invoking this skill |
| `inputSchema.properties` | The individual parameters — each has a type and description |
| `inputSchema.required` | Which parameters must be provided (others are optional) |
| `handler.type` | Always `"file"` — the skill content is in a static file |
| `handler.path` | Relative path to the skill Markdown file |
| `tags` | Used for routing — match user queries to relevant skills |
| `fallback.mode` | `"closest_skills"` — when the query doesn't match, return the N closest skills |
| `fallback.count` | How many closest skills to return (3) |
| `fallback.use_agent_knowledge` | `true` — the agent CAN use its own general knowledge alongside skill content |
| `fallback.invent_quotes` | `false` — the agent must NEVER fabricate YC quotes |

### How to Use MCP Specs in Practice

1. Load the MCP JSON spec as a tool definition in your MCP-compatible agent
2. When the user asks a question matching the skill's tags/description, the agent collects the `required` parameters
3. The agent reads the skill file at `handler.path` for the full content
4. The agent formulates its response using the skill's principle, quotes, and application instructions

---

## Export Format 2: OpenAI Function Schema

**File location:** `specs/openai/{skill_id}.json`

**Used by:** GPT, and any application using the OpenAI API's function calling feature.

### Example OpenAI Spec

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

### Field-by-Field Explanation

| Field | What It Means |
|-------|---------------|
| `type` | Always `"function"` — this is an OpenAI function definition |
| `function.name` | The function name your agent framework will call |
| `function.description` | Description the LLM uses to decide when to invoke this function |
| `function.parameters` | JSON Schema for the function's input parameters |
| `metadata.skill_file` | Path to the full skill Markdown file (not part of the OpenAI spec standard — it's our custom metadata) |
| `metadata.category` | The skill's category for routing |
| `metadata.tags` | Tags for discovery |
| `metadata.fallback` | Same fallback rules as MCP — what to do when the query doesn't match |

### How to Use OpenAI Specs in Practice

**Example Python code using the OpenAI API:**

```python
import json
import openai

# 1. Load the spec file
with open("specs/openai/yc-fundraising-seed-round-timing.json") as f:
    tool_spec = json.load(f)

# 2. Load the skill content
with open(tool_spec["metadata"]["skill_file"]) as f:
    skill_content = f.read()

# 3. Add the tool to your OpenAI API call
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": f"You are a startup advisor. Use this knowledge:\n\n{skill_content}"},
        {"role": "user", "content": "I have 4 months of runway. Should I raise now?"}
    ],
    tools=[tool_spec],  # Pass the spec as a tool definition
    tool_choice="auto"
)
```

---

## Export Format 3: Hermes Plain-Text (Local Models)

**File location:** `specs/hermes/{skill_id}.txt`

**Used by:** Local models like Ollama, llama.cpp, and any environment where you inject knowledge via system prompts rather than function calling.

### Example Hermes Spec

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

### How to Use Hermes Specs in Practice

Simply concatenate the `.txt` files you want into your system prompt:

```python
import os

# Load all Hermes skill specs
skills_text = ""
hermes_dir = "specs/hermes/"
for filename in os.listdir(hermes_dir):
    if filename.endswith(".txt"):
        with open(os.path.join(hermes_dir, filename)) as f:
            skills_text += f.read() + "\n\n"

# Use as system prompt
system_prompt = f"""You are a startup advisor powered by Y Combinator knowledge.
Use the following skills to answer founder questions:

{skills_text}

IMPORTANT RULES:
- Only use quotes marked as VERBATIM QUOTES. Never invent new YC quotes.
- Follow the AGENT PROTOCOL for each matching skill.
- If no skill matches, say so and use your general knowledge clearly labeled as such.
"""

# Now pass system_prompt to your local model
```

### Key Differences Between Hermes and MCP/OpenAI

| Feature | MCP / OpenAI | Hermes |
|---------|-------------|--------|
| Format | JSON with structured schemas | Plain text |
| Function calling | Supported via `inputSchema`/`parameters` | Not applicable — injected into system prompt |
| Best for | Cloud API-based agents (Claude, GPT) | Local models without function calling |
| How skills are loaded | On-demand via tool invocation | All at once via system prompt concatenation |
| Structured parameters | Yes (typed properties with descriptions) | No — the AGENT PROTOCOL section describes what to ask |

---

## Finding Skills — Signal Resolution & Routing

When your AI agent receives a user question, it needs to find the right skill(s) to answer it. There are four ways to search:

### 1. Exact ID Lookup

If you know the exact skill ID:

```
yc-fundraising-seed-round-timing
```

→ Directly look up the file at `skills/fundraising/yc-fundraising-seed-round-timing.md`

### 2. Category Filter (prefix: `/`)

To list all skills in a category:

```
/fundraising
```

→ Returns all skills in the `skills/fundraising/` directory

You can also filter by subcategory:

```
/fundraising/seed-round
```

→ Returns skills matching `yc-fundraising-seed-round-*`

### 3. Tag Filter (prefix: `%`)

To find skills by tags:

```
%seed
```

→ Returns all skills where `seed` is in the `tags` array

For multiple tags (AND logic — ALL tags must be present):

```
%seed,runway
```

→ Returns only skills tagged with BOTH `seed` AND `runway`

### 4. Fuzzy/Semantic Search (no prefix)

For natural language queries:

```
fundraising timing
```

→ Returns the 3 most similar skills based on embedding similarity

This requires using the `data/similarity_matrix.json` for pre-computed similarity scores.

---

## Using `skills-index.json` for Lookups

The `skills-index.json` file in the repository root is the machine-readable index of all skills. It contains three lookup tables:

```json
{
  "version": "1.0.0",
  "generated_at": "2026-07-12T00:00:00Z",
  "skill_count": 50,
  "by_id": {
    "yc-fundraising-seed-round-timing": {
      "path": "skills/fundraising/yc-fundraising-seed-round-timing.md",
      "category": "fundraising",
      "tags": ["seed", "runway", "timing"],
      "name": "Seed Round Timing",
      "confidence": 0.92
    }
  },
  "by_tag": {
    "seed": ["yc-fundraising-seed-round-timing", "yc-fundraising-seed-round-valuation"],
    "runway": ["yc-fundraising-seed-round-timing", "yc-founder-mental-models-default-alive-dead"]
  },
  "by_category": {
    "fundraising": [
      "yc-fundraising-seed-round-timing",
      "yc-fundraising-seed-round-valuation",
      "yc-fundraising-investor-update-emails"
    ],
    "hiring": [
      "yc-hiring-first-technical-hire"
    ]
  }
}
```

### How to Use It

**Looking up a skill by ID:**
```python
import json

with open("skills-index.json") as f:
    index = json.load(f)

skill_info = index["by_id"].get("yc-fundraising-seed-round-timing")
if skill_info:
    print(f"Found: {skill_info['name']} at {skill_info['path']}")
    # Load the skill file
    with open(skill_info["path"]) as f:
        skill_content = f.read()
```

**Finding skills by tag:**
```python
# Find all skills tagged with "seed"
seed_skills = index["by_tag"].get("seed", [])
# Returns: ["yc-fundraising-seed-round-timing", "yc-fundraising-seed-round-valuation"]
```

**Finding skills by category:**
```python
# Find all fundraising skills
fundraising_skills = index["by_category"].get("fundraising", [])
```

**Multi-tag AND filter:**
```python
# Find skills tagged with BOTH "seed" AND "runway"
seed_skills = set(index["by_tag"].get("seed", []))
runway_skills = set(index["by_tag"].get("runway", []))
both_tags = seed_skills & runway_skills  # Set intersection = AND logic
```

---

## Using `similarity_matrix.json` for Fuzzy Search

The `data/similarity_matrix.json` file contains pre-computed cosine similarity scores between every pair of skills. This allows fuzzy/semantic search without needing any machine learning libraries.

### Structure

```json
{
  "version": "1.0.0",
  "generated_at": "2026-07-12T00:00:00Z",
  "skills": [
    "yc-fundraising-seed-round-timing",
    "yc-fundraising-seed-round-valuation",
    "yc-founder-mental-models-default-alive-dead"
  ],
  "matrix": [
    [1.0, 0.85, 0.42],
    [0.85, 1.0, 0.38],
    [0.42, 0.38, 1.0]
  ],
  "tag_index": {
    "seed": ["yc-fundraising-seed-round-timing", "yc-fundraising-seed-round-valuation"],
    "runway": ["yc-fundraising-seed-round-timing", "yc-founder-mental-models-default-alive-dead"]
  }
}
```

### How to Read the Matrix

The `matrix` is a 2D array where `matrix[i][j]` is the cosine similarity between `skills[i]` and `skills[j]`.

- `1.0` = identical (a skill compared to itself)
- `0.85` = very similar (closely related topics)
- `0.42` = somewhat related
- `0.0` = completely unrelated

### Finding the Closest Skills to a Given Skill

```python
import json

with open("data/similarity_matrix.json") as f:
    sim = json.load(f)

# Find the 3 most similar skills to a given skill
target_skill = "yc-fundraising-seed-round-timing"
target_idx = sim["skills"].index(target_skill)

# Get similarities and sort by descending similarity
similarities = []
for i, skill_id in enumerate(sim["skills"]):
    if i != target_idx:  # Skip self
        similarities.append((skill_id, sim["matrix"][target_idx][i]))

similarities.sort(key=lambda x: x[1], reverse=True)
top_3 = similarities[:3]

for skill_id, score in top_3:
    print(f"  {skill_id}: {score:.2f}")
```

---

## Fallback Behavior — The Most Important Rule

> **Every spec file defines strict fallback rules. Your agent MUST obey them.**

When a user's question doesn't exactly match any loaded skill, your agent must follow this protocol:

### Step 1: Return the 3 Closest Skills

Use the similarity matrix or the tag index to find the 3 most related skills. Present them to the user:

```markdown
## Closest Matching Skills

No specific YC skill exists for this exact query. Here are the 3 most relevant skills:

1. **yc-fundraising-seed-round-timing** (Similarity: 0.87)
   - Discusses runway and timing for seed fundraising.

2. **yc-fundraising-investor-update-emails** (Similarity: 0.72)
   - Communication with investors before a formal raise.

3. **yc-founder-mental-models-default-alive-dead** (Similarity: 0.68)
   - Runway calculation and survival metrics.
```

### Step 2: Provide General Advice (Labeled Clearly)

The agent CAN use its own training knowledge to help the user, but it must be clearly distinguished from YC-sourced content:

```markdown
## General Advice

Since no YC skill directly covers your specific situation, here is general
advice based on standard startup practices:

[Agent's own knowledge here]

**Important:** The above general advice is NOT sourced from Y Combinator
content. For YC-backed guidance, review the related skills listed above.
```

### Step 3: NEVER Invent YC Quotes

This is the most critical rule. Your agent must **never**:
- Make up a quote and attribute it to a YC speaker
- Paraphrase a real quote and present it as verbatim
- Attribute general knowledge to a specific YC person

**Wrong:** *As Paul Graham says, "You should always raise money when you have traction."*
(If this exact quote doesn't appear in a skill file, the agent invented it.)

**Right:** *Paul Graham has spoken about the importance of timing in fundraising. For his exact advice, see the skill "yc-fundraising-seed-round-timing".*

---

## Integration Examples

### Example: Claude Code with MCP

1. Load all MCP specs from `specs/mcp/`
2. Register them as tools in your MCP server
3. When the user asks a startup question, Claude selects the matching tool
4. Your handler reads the skill file and returns the content

### Example: GPT with Function Calling

```python
import json
import os
import openai

# Load all OpenAI specs as tools
tools = []
for filename in os.listdir("specs/openai/"):
    if filename.endswith(".json"):
        with open(f"specs/openai/{filename}") as f:
            tools.append(json.load(f))

# Chat with function calling
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "I have 4 months of runway. Should I raise my seed round?"}
    ],
    tools=tools,
    tool_choice="auto"
)

# If a tool was called, load the skill content
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    skill_id = tool_call.function.name.replace("_", "-")

    # Find the skill file path from the spec metadata
    with open(f"specs/openai/{skill_id}.json") as f:
        spec = json.load(f)
    skill_path = spec["metadata"]["skill_file"]

    # Load and return the skill content
    with open(skill_path) as f:
        skill_content = f.read()

    print(f"Using skill: {skill_id}")
    print(skill_content)
```

### Example: Ollama with Hermes Specs

```python
import os
import ollama

# Load all Hermes skills into a single system prompt
skills_text = ""
for filename in sorted(os.listdir("specs/hermes/")):
    if filename.endswith(".txt"):
        with open(f"specs/hermes/{filename}") as f:
            skills_text += f.read() + "\n\n"

system_prompt = f"""You are a YC-powered startup advisor.

RULES:
1. Use ONLY the verbatim quotes provided below. NEVER invent YC quotes.
2. Follow the AGENT PROTOCOL for each matching skill.
3. If no skill matches, say "No specific YC skill covers this" and use general knowledge.

LOADED SKILLS:
{skills_text}"""

# Chat with the local model
response = ollama.chat(
    model="llama3",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "When should I raise my seed round?"}
    ]
)

print(response["message"]["content"])
```

---

## Understanding Skill Metadata Fields

Here's a complete reference for every field in a skill's YAML frontmatter:

| Field | Type | Required? | Description |
|-------|------|-----------|-------------|
| `skill_id` | string | Yes | Unique identifier. Pattern: `yc-{category}-{descriptor}`. Regex: `^yc-[a-z]+(-[a-z]+){1,6}$` |
| `name` | string | Yes | Human-readable name. Max 100 characters. |
| `version` | string | Yes | Semantic version. Pattern: `X.Y.Z`. Default: `"1.0.0"`. |
| `category` | string | Yes | One of the 8 taxonomy categories. |
| `tags` | list[string] | Yes | 1 to 10 lowercase tags for filtering. |
| `source_count` | integer | Yes | Number of source documents (≥ 1). |
| `quote_count` | integer | Yes | Number of verbatim quotes (≥ 1). |
| `confidence` | float | Yes | 0.0 to 1.0. Computed from cluster metrics (NOT from LLM self-assessment). Higher = more consensus among sources. |
| `related_skills` | list | No | Top 3 most similar skills by cosine similarity. Each entry has `id` and `similarity`. |
| `provenance` | object | Yes | Where this skill came from — batch ID, date, and list of sources. |
| `provenance.batch_id` | string | Yes | UUID of the pipeline batch that created this skill. |
| `provenance.pipeline_run_date` | string | Yes | ISO 8601 timestamp of when the pipeline ran. |
| `provenance.sources` | list | Yes | List of source documents with content_id, title, speaker, designation, URL, and contribution. |
| `validation` | object | Yes | Results of the three-layer validation suite. |
| `validation.quote_verified` | boolean | Yes | Whether all quotes passed fuzzy matching against source content. |
| `validation.schema_valid` | boolean | Yes | Whether the frontmatter passed Pydantic schema validation. |
| `validation.hallucination_check` | boolean | Yes | Whether the skill passed the LLM-as-judge fact check. |
| `validation.human_review` | boolean | Yes | Whether this skill was flagged for manual human review. |

---

## Frequently Asked Questions

### Q: Do I need Python to use skills in my AI agent?
**No.** Skills are static Markdown and JSON files. You can read them with any programming language.

### Q: How many skills are available?
Check `skills-index.json` — the `skill_count` field tells you the total.

### Q: How often are new skills added?
Skills are added manually by contributors. There's no fixed schedule. Watch the repository or check Releases for updates.

### Q: Can I use only some skills, not all of them?
**Yes.** Pick and choose the skills relevant to your use case. The `by_category` and `by_tag` lookups in `skills-index.json` help you filter.

### Q: What if a skill has low confidence (e.g., 0.55)?
Low confidence means fewer sources corroborated the advice, or sources disagreed. The skill is still valid but should be treated as less authoritative. Consider pairing it with related higher-confidence skills.

### Q: Can I modify skill files for my own use?
**Yes,** but if you redistribute modified skills, you must comply with the CC BY-SA 4.0 license (attribution required, share alike).

### Q: What's the difference between `skills-index.json` and `similarity_matrix.json`?
- `skills-index.json` is a **lookup table** — find skills by ID, tag, or category
- `similarity_matrix.json` is a **relationship matrix** — find how similar any two skills are to each other

### Q: Do I need to implement all three spec formats?
**No.** Use the format that matches your AI framework:
- Claude Code → MCP
- GPT/OpenAI API → OpenAI
- Local models → Hermes
- Custom framework → Read skill `.md` files directly

### Q: What happens if I can't find a matching skill?
Follow the fallback behavior: return the 3 closest skills, use general knowledge clearly labeled as such, and NEVER invent YC quotes.
