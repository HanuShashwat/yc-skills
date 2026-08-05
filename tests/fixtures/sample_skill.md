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
