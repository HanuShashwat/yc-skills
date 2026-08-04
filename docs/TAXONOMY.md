# YC Skills Taxonomy

## Overview

The YC Skills Forge ecosystem enforces a strict mathematical separation of all startup advice across 8 foundational categories. 

Each generated skill explicitly maps its `skill_id` namespace directly to its parent category, following the pattern `yc-{category}-{descriptor}`. Correspondingly, physical file assets natively live within `skills/{category}/`.

If you are a consumer querying the index via a Category Filter (`/category`), or a contributor forging new material, you must adhere strictly to this pre-defined ontology.

## Category Tree

### 1. fundraising
*Raising capital from investors*
- `seed-round`
- `series-a`
- `pitch-deck`
- `investor-relations`
- `valuation`
- `term-sheets`

### 2. hiring
*Building the team*
- `first-hires`
- `technical-hiring`
- `culture-fit`
- `compensation`
- `firing`

### 3. product
*Product development and management*
- `mvp`
- `product-market-fit`
- `user-research`
- `roadmap`
- `design`

### 4. growth
*Acquiring and retaining users*
- `marketing`
- `sales`
- `retention`
- `pricing`
- `distribution`

### 5. culture
*Company culture and operations*
- `mission`
- `values`
- `remote-work`
- `communication`

### 6. strategy
*High-level company decisions*
- `pivoting`
- `competition`
- `market-sizing`
- `monetization`

### 7. founder-mental-models
*Psychological and decision-making frameworks*
- `motivation`
- `burnout`
- `decision-making`
- `leadership`

### 8. technical
*Engineering and infrastructure*
- `architecture`
- `scaling`
- `security`
- `ai-ml`

## Adding New Categories

The taxonomy is hardcoded to prevent sprawl and overlap. If you are a contributor and your forged content falls explicitly outside these boundaries, it requires a Pull Request expanding the taxonomy manually. 

To add a new category:
1. Modify `config/taxonomy.yml` directly.
2. Create the corresponding physical output directory: `mkdir skills/{category}/`.
3. Update this `docs/TAXONOMY.md` file reflecting your changes for downstream agents and consumers.
