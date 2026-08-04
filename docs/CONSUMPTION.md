# Consuming YC Skills Forge

This guide is for AI agent developers who want to use the published skills. 

## Overview

All skills in this repository are static files (Markdown with YAML frontmatter) or spec files (JSON/TXT). There is **no runtime vector database, no API keys needed, and no dependencies to install**. Your AI agent framework simply reads these static files from disk or directly over HTTPS from GitHub.

## Export Formats

### 1. MCP Format (Claude Code)
The Model Context Protocol (MCP) format defines the skill as an exposed tool that Claude Code or other MCP-compatible frameworks can execute.

To use an MCP skill, load the JSON spec from `specs/mcp/{skill_id}.json`.

**Example Spec Structure:**
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

*Key Fields:*
- `inputSchema`: The parameters required to trigger the skill effectively.
- `handler`: Points your agent directly to the underlying markdown skill file to fetch the verbatim context.
- `tags`: Used to route contextual awareness.
- `fallback`: Essential safety guardrails defining the action if the skill misses the context.

### 2. OpenAI Format (GPT / Function Calling)
For developers integrating with the OpenAI API, the `specs/openai/{skill_id}.json` provides ready-to-use function schemas.

**Example Spec Structure:**
```json
{
  "type": "function",
  "function": {
    "name": "yc_fundraising_seed_round_timing",
    "description": "YC advice on optimal timing for seed fundraising.",
    "parameters": {
      "type": "object",
      "properties": {
        "runway_months": {
          "type": "number",
          "description": "Current months of runway remaining"
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

*Note on `metadata.fallback`:* This proprietary block instructs your framework's routing logic exactly how to respond when failing to resolve exact intent, identical to the MCP standard.

### 3. Hermes Format (Local Models)
For local model environments (like Ollama or llama.cpp) where function calling isn't strictly enforced, use the raw text embeddings defined in `specs/hermes/{skill_id}.txt`.

You simply concatenate `.txt` files into your system prompt.

**Example Spec Structure:**
```text
[SKILL: yc-fundraising-seed-round-timing]
NAME: Seed Round Timing
CATEGORY: fundraising
TAGS: seed, runway, leverage, investors, timing

PRINCIPLE: The optimal time to raise a seed round is when you have 9-12 months of runway remaining and can demonstrate measurable momentum.

VERBATIM QUOTES:
- "The best time to raise money is when you don't need it." — Paul Graham, Founder of YC

WHEN TO USE: Founder asks about fundraising timing, runway, or leverage.

AGENT PROTOCOL:
1. Ask runway_months and monthly_burn first.

FALLBACK: If query does not match, return 3 closest skills and use general knowledge. DO NOT invent YC quotes.

RELATED SKILLS: yc-fundraising-seed-round-valuation, yc-fundraising-investor-update-emails, yc-founder-mental-models-default-alive-dead
[END SKILL]
```

## Fallback Behavior (Critical)

Every spec defines a strict `fallback` block. If the user's prompt strays off-topic or doesn't match the loaded skill, your agent MUST obey the protocol:
1. Return the 3 closest skills via similarity routing.
2. Provide general advice from its own base knowledge.
3. **NEVER invent YC quotes or falsely attribute base-model knowledge to YC speakers.**

This protects against hallucinations and maintains the integrity of the verbatim knowledge base.

## Signal Resolution & Routing

You can dynamically search for skills using specific prefix rules:
- **Exact ID**: `yc-fundraising-seed-round-timing`
- **Category Filter**: `/fundraising`
- **Tag Filter**: `%seed,runway`
- **Fuzzy Search**: `fundraising timing`

### Parsing `skills-index.json`
To implement these resolutions without a vector DB, rely entirely on the pre-computed `skills-index.json` located in the root repository. It contains lookup tables mapping IDs (`by_id`), tags (`by_tag`), and categories (`by_category`) directly to their file paths and metadata. 

For fuzzy searching, load the complementary `data/similarity_matrix.json` and perform dot-product arithmetic against the pre-calculated tag/category coordinates!
