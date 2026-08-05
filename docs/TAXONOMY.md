# OpenYC Skills Taxonomy — Complete Category & Subcategory Reference

> **The authoritative map of how all startup advice skills are organized. Every skill in this repository belongs to exactly one category and maps to one or more subcategories.**

---

## Table of Contents

1. [What Is the Taxonomy?](#what-is-the-taxonomy)
2. [How the Taxonomy Works](#how-the-taxonomy-works)
3. [How Skill IDs Map to the Taxonomy](#how-skill-ids-map-to-the-taxonomy)
4. [Complete Category Tree](#complete-category-tree)
   - [1. fundraising](#1-fundraising)
   - [2. hiring](#2-hiring)
   - [3. product](#3-product)
   - [4. growth](#4-growth)
   - [5. culture](#5-culture)
   - [6. strategy](#6-strategy)
   - [7. founder-mental-models](#7-founder-mental-models)
   - [8. technical](#8-technical)
5. [How Categories Map to Files and Directories](#how-categories-map-to-files-and-directories)
6. [How to Query Skills by Category or Subcategory](#how-to-query-skills-by-category-or-subcategory)
7. [Choosing the Right Category for New Content](#choosing-the-right-category-for-new-content)
8. [Adding New Categories (Contributor Guide)](#adding-new-categories-contributor-guide)
9. [Adding New Subcategories](#adding-new-subcategories)
10. [Why the Taxonomy Is Locked](#why-the-taxonomy-is-locked)
11. [Cross-Category Skills](#cross-category-skills)
12. [Taxonomy vs. Tags — What's the Difference?](#taxonomy-vs-tags--whats-the-difference)
13. [Complete Reference Table](#complete-reference-table)

---

## What Is the Taxonomy?

The taxonomy is the **fixed organizational structure** that determines how every skill in OpenYC Skills is categorized and filed. Think of it like a filing cabinet with 8 labeled drawers, where each drawer has several labeled folders inside it.

- **Categories** = the 8 drawers (e.g., `fundraising`, `hiring`, `product`)
- **Subcategories** = the folders inside each drawer (e.g., `seed-round`, `series-a`, `pitch-deck` inside `fundraising`)

Every skill belongs to exactly **one category**. The subcategory is embedded in the skill's unique ID and determines what specific topic the skill covers.

---

## How the Taxonomy Works

The taxonomy is defined in a single YAML configuration file: `config/taxonomy.yml`. This file is the **single source of truth** — all skill generation, validation, and routing uses this file to determine valid categories and subcategories.

Here's how the taxonomy connects to everything in the project:

| Component | How It Uses the Taxonomy |
|-----------|------------------------|
| **Skill IDs** | Every skill ID starts with `yc-{category}-` (e.g., `yc-fundraising-seed-round-timing`) |
| **File paths** | Skills live in `skills/{category}/` directories (e.g., `skills/fundraising/`) |
| **Spec files** | Specs live in `specs/{format}/{skill_id}.json` or `.txt` |
| **`skills-index.json`** | The `by_category` lookup maps categories to skill IDs |
| **Category filter** | Consumers can filter skills by category using the `/` prefix (e.g., `/fundraising`) |
| **Pipeline** | The `--topic` flag in the forge CLI command accepts category or subcategory names |
| **Validation** | Schema validation checks that the `category` field is one of the 8 valid categories |

---

## How Skill IDs Map to the Taxonomy

Every skill has a unique ID that follows this pattern:

```
yc-{category}-{subcategory}-{descriptor}
```

Let's break this down with examples:

| Skill ID | Category | Subcategory | Descriptor |
|----------|----------|-------------|------------|
| `yc-fundraising-seed-round-timing` | `fundraising` | `seed-round` | `timing` |
| `yc-fundraising-seed-round-valuation` | `fundraising` | `seed-round` | `valuation` |
| `yc-hiring-first-technical-hire` | `hiring` | `first-hires` | `technical-hire` |
| `yc-product-mvp-no-code-approach` | `product` | `mvp` | `no-code-approach` |
| `yc-founder-mental-models-default-alive-dead` | `founder-mental-models` | (embedded) | `default-alive-dead` |

**Rules:**
- All lowercase
- Words separated by hyphens
- Maximum 6 words after `yc-{category}`
- Must match the regex: `^yc-[a-z]+(-[a-z]+){1,6}$`
- Each skill ID must be unique across the entire repository

---

## Complete Category Tree

Below is the complete taxonomy with detailed explanations of what each category and subcategory covers, along with example skill topics.

---

### 1. fundraising

**Description:** Raising capital from investors — everything from seed rounds to Series A and beyond.

**Directory:** `skills/fundraising/`

| Subcategory | What It Covers | Example Skill Topics |
|-------------|---------------|---------------------|
| `seed-round` | Raising an initial seed round: timing, sizing, investor targeting, SAFE notes | When to raise, how much to raise, seed round benchmarks |
| `series-a` | Raising a Series A: metrics needed, lead investors, board seats | Series A readiness checklist, metrics for Series A |
| `pitch-deck` | Creating and delivering investor pitch decks: structure, storytelling, demo days | Pitch deck structure, demo day presentation tips |
| `investor-relations` | Managing relationships with investors: updates, communication, board management | Monthly investor updates, managing board expectations |
| `valuation` | Startup valuation: how to think about it, negotiation, cap tables | Seed valuation ranges, dilution math, cap table basics |
| `term-sheets` | Understanding and negotiating term sheets: key clauses, red flags | Pro-rata rights, liquidation preferences, anti-dilution |

**When to use this category:** Any time the content is about getting money from investors, managing investor relationships, or financial structure of fundraising.

---

### 2. hiring

**Description:** Building the team — finding, evaluating, compensating, and sometimes parting ways with team members.

**Directory:** `skills/hiring/`

| Subcategory | What It Covers | Example Skill Topics |
|-------------|---------------|---------------------|
| `first-hires` | Making your first 1-10 hires as a startup: who to hire first, where to find them | First engineer hire, first sales hire, hiring from your network |
| `technical-hiring` | Hiring engineers and technical roles: interviewing, evaluating, competing with big tech | Technical interview process, competing with FAANG for talent |
| `culture-fit` | Evaluating and maintaining cultural alignment in hiring | Culture-add vs culture-fit, values-based interviewing |
| `compensation` | Startup compensation: salary, equity, vesting, benchmarks | Equity splits, vesting schedules, competing on compensation |
| `firing` | When and how to let people go: performance management, difficult conversations | When to fire fast, handling performance issues |

**When to use this category:** Any time the content is about people — hiring, managing, compensating, or terminating team members.

---

### 3. product

**Description:** Product development and management — from MVP to product-market fit and beyond.

**Directory:** `skills/product/`

| Subcategory | What It Covers | Example Skill Topics |
|-------------|---------------|---------------------|
| `mvp` | Building a Minimum Viable Product: what to build, what to skip, launch strategy | MVP scope, launching early, "do things that don't scale" |
| `product-market-fit` | Finding and measuring product-market fit | Signs of PMF, measuring PMF, pivoting to find PMF |
| `user-research` | Talking to users, conducting interviews, gathering feedback | Customer interviews, user feedback loops, surveys |
| `roadmap` | Product roadmap and prioritization: what to build next | Feature prioritization frameworks, saying no to features |
| `design` | Product design, UX, and user experience principles | Simple design, user onboarding, first-time user experience |

**When to use this category:** Any time the content is about what you're building, who you're building it for, and how to make it better.

---

### 4. growth

**Description:** Acquiring and retaining users — marketing, sales, pricing, and distribution strategies.

**Directory:** `skills/growth/`

| Subcategory | What It Covers | Example Skill Topics |
|-------------|---------------|---------------------|
| `marketing` | Startup marketing: channels, messaging, brand building | Content marketing, SEO for startups, launch marketing |
| `sales` | Selling your product: enterprise sales, B2B sales processes | First 10 customers, enterprise sales cycle, sales hiring |
| `retention` | Keeping users: churn reduction, engagement, activation | Reducing churn, activation metrics, user engagement loops |
| `pricing` | Pricing strategy: models, tiers, experimentation | Pricing psychology, freemium vs paid, pricing experiments |
| `distribution` | Distribution channels and partnerships | Channel partnerships, platform distribution, viral loops |

**When to use this category:** Any time the content is about getting more users, keeping them, or making money from them.

---

### 5. culture

**Description:** Company culture and operations — mission, values, internal communication, and work style.

**Directory:** `skills/culture/`

| Subcategory | What It Covers | Example Skill Topics |
|-------------|---------------|---------------------|
| `mission` | Defining and communicating company mission and purpose | Mission statement crafting, mission-driven hiring |
| `values` | Establishing and living by company values | Defining core values, values in practice vs on paper |
| `remote-work` | Remote and distributed team management | Remote culture, async communication, remote onboarding |
| `communication` | Internal communication: meetings, updates, transparency | All-hands meetings, internal communication tools, radical transparency |

**When to use this category:** Any time the content is about how the company works internally — its identity, values, communication style, or operational practices.

---

### 6. strategy

**Description:** High-level company decisions — pivoting, competition, market analysis, and business models.

**Directory:** `skills/strategy/`

| Subcategory | What It Covers | Example Skill Topics |
|-------------|---------------|---------------------|
| `pivoting` | When and how to pivot: recognizing failure, changing direction | Signs you need to pivot, types of pivots, pivot case studies |
| `competition` | Competitive strategy: differentiation, moats, market positioning | Building moats, handling competition, first-mover advantage |
| `market-sizing` | Market analysis: TAM/SAM/SOM, market selection, timing | Market sizing for investors, choosing your market |
| `monetization` | Business models and revenue strategy | Monetization models, when to monetize, B2B vs B2C economics |

**When to use this category:** Any time the content is about big-picture strategic decisions that affect the company's direction.

---

### 7. founder-mental-models

**Description:** Psychological and decision-making frameworks — the mindset, habits, and mental models that help founders make better decisions.

**Directory:** `skills/founder-mental-models/`

| Subcategory | What It Covers | Example Skill Topics |
|-------------|---------------|---------------------|
| `motivation` | Founder motivation: why to start, staying motivated, intrinsic drive | Founder-market fit, missionary vs mercenary founders |
| `burnout` | Managing stress and avoiding burnout | Founder burnout, work-life balance, mental health |
| `decision-making` | Decision-making frameworks and cognitive biases | First principles thinking, reversible vs irreversible decisions |
| `leadership` | Leadership skills, management, and personal growth | CEO transitions, leadership styles, delegation |

**When to use this category:** Any time the content is about the founder as a person — their psychology, decision-making, well-being, or personal growth.

---

### 8. technical

**Description:** Engineering and infrastructure — technical decisions, architecture, scaling, and security.

**Directory:** `skills/technical/`

| Subcategory | What It Covers | Example Skill Topics |
|-------------|---------------|---------------------|
| `architecture` | System architecture and technical design decisions | Monolith vs microservices, tech stack choices, technical debt |
| `scaling` | Scaling infrastructure and engineering teams | Scaling databases, handling traffic spikes, scaling the team |
| `security` | Security practices and data protection | Security basics for startups, handling data breaches |
| `ai-ml` | AI and machine learning in startups | AI product strategy, ML infrastructure, when to use AI |

**When to use this category:** Any time the content is about engineering, technology choices, infrastructure, or technical strategy.

---

## How Categories Map to Files and Directories

Here's exactly how the taxonomy maps to the file system:

```
config/taxonomy.yml          ← The source of truth for all categories
    ↓
skills/
├── fundraising/             ← One directory per category
│   ├── yc-fundraising-seed-round-timing.md
│   ├── yc-fundraising-seed-round-valuation.md
│   └── yc-fundraising-investor-update-emails.md
├── hiring/
│   └── yc-hiring-first-technical-hire.md
├── product/
│   └── yc-product-mvp-no-code-approach.md
├── growth/
├── culture/
├── strategy/
├── founder-mental-models/
│   └── yc-founder-mental-models-default-alive-dead.md
└── technical/

specs/
├── mcp/                     ← One spec per skill per format
│   ├── yc-fundraising-seed-round-timing.json
│   └── ...
├── openai/
│   ├── yc-fundraising-seed-round-timing.json
│   └── ...
└── hermes/
    ├── yc-fundraising-seed-round-timing.txt
    └── ...
```

**Key rule:** The category in the skill's `skill_id` MUST match the directory it's in. A skill with `category: fundraising` MUST be in `skills/fundraising/`.

---

## How to Query Skills by Category or Subcategory

### For Consumers (reading `skills-index.json`)

```python
import json

with open("skills-index.json") as f:
    index = json.load(f)

# Get all skills in a category
fundraising_skills = index["by_category"]["fundraising"]
# Returns: ["yc-fundraising-seed-round-timing", "yc-fundraising-seed-round-valuation", ...]

# Get all skills in a subcategory (filter by ID prefix)
seed_round_skills = [
    skill_id for skill_id in index["by_category"]["fundraising"]
    if "seed-round" in skill_id
]
```

### For Consumers (using the signal filter prefix)

Use the `/` prefix to filter by category:

```
/fundraising              → All skills in the fundraising category
/fundraising/seed-round   → Skills matching yc-fundraising-seed-round-*
/hiring                   → All skills in the hiring category
/technical/ai-ml          → Skills matching yc-technical-ai-ml-*
```

### For Contributors (using the CLI)

```bash
# Run the forge for a specific topic (category or subcategory)
python -m src.cli forge --topic "fundraising" --batch-size 15
python -m src.cli forge --topic "pricing" --batch-size 10

# Link skills for a specific topic
python -m src.cli link --topic "fundraising"
```

---

## Choosing the Right Category for New Content

When you ingest new content, the pipeline tries to guess the topic based on keywords and the taxonomy. But sometimes content spans multiple categories. Here's how to decide:

### Decision Flowchart

```
Is the content primarily about getting money from investors?
  → YES: fundraising

Is it about finding, hiring, managing, or firing people?
  → YES: hiring

Is it about what you're building and who uses it?
  → YES: product

Is it about getting more users or making more money?
  → YES: growth

Is it about how the company operates internally?
  → YES: culture

Is it about big-picture company direction?
  → YES: strategy

Is it about the founder's mindset or personal growth?
  → YES: founder-mental-models

Is it about engineering, infrastructure, or technology?
  → YES: technical
```

### When Content Spans Multiple Categories

Sometimes YC advice touches on multiple topics. For example, "How hiring affects fundraising." In these cases:

1. **Choose the PRIMARY category** — what is the core actionable advice about?
2. **Use tags** from other categories to enable cross-category discovery
3. **Let the `related_skills` field** (computed automatically) link to skills in other categories

Example: A skill about "how your hiring plan affects your pitch deck" would be:
- **Category:** `fundraising` (the advice is actionable for fundraising)
- **Tags:** `["pitch-deck", "hiring", "team", "headcount"]`
- **Related skills:** Might include a `hiring/` skill automatically via similarity matrix

---

## Adding New Categories (Contributor Guide)

The taxonomy is intentionally locked to 8 categories to prevent overlap and sprawl. However, if you genuinely need a new category:

### Step 1: Verify It's Truly Needed

Before proposing a new category, ask yourself:
- Does this topic fit into ANY existing category or subcategory?
- Could it be a new subcategory under an existing category instead?
- Is there enough YC content on this topic to justify a full category?

### Step 2: Modify `config/taxonomy.yml`

```yaml
taxonomy:
  # ... existing categories ...

  your-new-category:
    description: A clear, brief description of what this covers
    subcategories:
      - subcategory-one
      - subcategory-two
      - subcategory-three
```

### Step 3: Create the Directory

```bash
mkdir skills/your-new-category/
```

### Step 4: Update This File

Add a new section to this `docs/TAXONOMY.md` documenting your category, its subcategories, what they cover, and example skill topics.

### Step 5: Submit a Pull Request

New categories **require a Pull Request** for community review. They cannot be added unilaterally.

---

## Adding New Subcategories

Adding a new subcategory is less restrictive than adding a new category, but still requires updating the taxonomy:

1. Add the subcategory to the appropriate category in `config/taxonomy.yml`
2. Update this `docs/TAXONOMY.md` file
3. No new directory is needed — subcategories don't have their own directories; skills are organized by category only

---

## Why the Taxonomy Is Locked

The taxonomy is intentionally restrictive for several important reasons:

1. **Prevents overlap:** Without clear boundaries, skills about "pricing strategy" could end up in `growth/`, `strategy/`, or `product/`. The fixed taxonomy forces a consistent decision.

2. **Enables reliable routing:** AI agents using the `/category` filter depend on a stable, known set of categories. Adding new categories changes the routing surface.

3. **Prevents sprawl:** Left unchecked, categories would multiply (e.g., `legal`, `accounting`, `sales-ops`, `devops`, `data-science`). This dilutes the focus on core startup advice.

4. **Maintains quality:** Each category should have substantial YC content. Categories with only 1-2 skills don't add enough value to justify the organizational overhead.

---

## Cross-Category Skills

Some skills naturally relate to topics in other categories. The taxonomy handles this through two mechanisms:

### 1. Tags (Human-Readable Cross-References)

Skills can have tags from any topic, not just their own category. For example, a `fundraising` skill about "how hiring plans affect your pitch" might have tags like `["pitch-deck", "hiring", "team"]`. The `%hiring` tag filter would surface this skill even though it's in the `fundraising` category.

### 2. Related Skills (Computed Cross-References)

The `related_skills` field in each skill is computed automatically using cosine similarity of embeddings. This field can link to skills in ANY category. For example, `yc-fundraising-seed-round-timing` might have a related skill of `yc-founder-mental-models-default-alive-dead` because they both discuss runway.

---

## Taxonomy vs. Tags — What's the Difference?

| Feature | Taxonomy (Category) | Tags |
|---------|---------------------|------|
| **What it is** | A hierarchical tree of 8 categories with subcategories | A flat list of 1-10 keywords per skill |
| **How many per skill** | Exactly 1 category | 1 to 10 tags |
| **Defined where** | `config/taxonomy.yml` | In each skill's YAML frontmatter |
| **Controls file location** | Yes — `skills/{category}/` | No |
| **Controls skill ID** | Yes — `yc-{category}-...` | No |
| **Can cross categories** | No — each skill is in exactly one category | Yes — tags can reference any topic |
| **How to query** | `/fundraising` (category filter) | `%seed,runway` (tag filter) |
| **Who defines them** | Project maintainers (locked taxonomy) | The LLM during synthesis (from the taxonomy + context) |

**In short:** The category is the skill's "home address." Tags are keywords that help discover it from different angles.

---

## Complete Reference Table

Here is the entire taxonomy in one table for quick reference:

| Category | Description | Subcategories | Directory |
|----------|-------------|---------------|-----------|
| `fundraising` | Raising capital from investors | `seed-round`, `series-a`, `pitch-deck`, `investor-relations`, `valuation`, `term-sheets` | `skills/fundraising/` |
| `hiring` | Building the team | `first-hires`, `technical-hiring`, `culture-fit`, `compensation`, `firing` | `skills/hiring/` |
| `product` | Product development & management | `mvp`, `product-market-fit`, `user-research`, `roadmap`, `design` | `skills/product/` |
| `growth` | Acquiring and retaining users | `marketing`, `sales`, `retention`, `pricing`, `distribution` | `skills/growth/` |
| `culture` | Company culture & operations | `mission`, `values`, `remote-work`, `communication` | `skills/culture/` |
| `strategy` | High-level company decisions | `pivoting`, `competition`, `market-sizing`, `monetization` | `skills/strategy/` |
| `founder-mental-models` | Psychological & decision-making frameworks | `motivation`, `burnout`, `decision-making`, `leadership` | `skills/founder-mental-models/` |
| `technical` | Engineering & infrastructure | `architecture`, `scaling`, `security`, `ai-ml` | `skills/technical/` |

**Total:** 8 categories, 38 subcategories.

**Source of truth:** `config/taxonomy.yml`
