# Operations Guide: Human-in-the-Loop Branding

This system is designed as a **Multi-Brand OS** where the AI handles the "heavy lifting" of drafting, and the Human acts as the **Creative Director** and **Strategist**.

---

## 🏗️ Your Role as the Human

### 1. The Creative Director (Project Approval)
When you paste a Notion URL, the agent starts **Project Mode**.
- **Role:** Review the "Hook" and "Visual Style".
- **Action:** Don't just say "yes". Refine the angle. Tell the agent: *"Make the hook more provocative for the DE audience"* or *"The visual should be more blueprint-like."*

### 2. The Data Provider (Analytics Sync)
The AI cannot see your social media dashboards.
- **Role:** Every week, spend 5 minutes fetching Likes/Views from LinkedIn/XHS.
- **Action:** Run `sync analytics` in Claude Code. This data is the "fuel" for the growth engine.

### 3. The Strategist (Post-Mortem & DNA)
- **Role:** Review the winning patterns.
- **Action:** Run `run post-mortem` once a month. If a brand is pivoting, update its `DNA.md` manually to reflect the new voice.

---

## 📈 Refining the Growth Strategy

To scale your businesses, follow this **Signal-to-Growth** loop:

### Phase 1: Signal Scouting
- **Input:** Don't just save everything. Find "High-Signal" content in your Source DBs (AI Daily Hits, etc.).
- **Goal:** Find content that bridges your expertise with your audience's current pain point.

### Phase 2: Brand Alignment
- **Check:** Before starting a project, ask yourself: *"Does this support the current goal of Brand X?"*
- **Automation:** The `DNA.md` acts as a filter. If the content doesn't fit the DNA, the agent will struggle to draft it well—that's your cue to skip or pivot.

### Phase 3: Distribution Maximization
- **Strategy:** One Signal → 5 Assets.
- **Leverage:** Use the **LinkedIn Dual-Audience** rule (PM/DE) to hit two different psychological profiles with the same technical insight.

### Phase 4: The Feedback Loop (The "Production-Grade" Edge)
- **Strategy:** Data-Driven Identity.
- **Cycle:** Sync Analytics → Run Post-Mortem → Update DNA.
- **Result:** Over time, your `DNA.md` becomes a refined "Formula for Success" for each specific brand.

---

## 🛠️ Operational Commands

| Objective | Command in Claude Code |
| :--- | :--- |
| **Start Content Pipeline** | Paste any Notion Page URL |
| **Check Pipeline Status** | `"List published assets for [brand]"` |
| **Sync Real Performance** | `"Sync analytics"` |
| **Analyze Success** | `"Run post-mortem"` |
| **Switch Brand** | `"Use brand [brand_name]"` |

---

## 🚀 Growth Milestones

1.  **Level 1 (Current):** You are drafting content 10x faster.
2.  **Level 2:** You are generating on-brand visuals automatically.
3.  **Level 3:** Your DNA is evolving based on real performance data.
4.  **Level 4 (Goal):** You manage 3+ brands in < 2 hours of human work per week.
