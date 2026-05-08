# Agent Logic: Decision Trees & Execution Flow

This document breaks down the agent's decision logic step-by-step, showing exactly what happens in each scenario.

---

## Master Decision Tree

When the agent is invoked (either by cron or manually), it starts here:

```
START: Agent Wakes Up
    │
    ├─ What triggered this?
    │
    ├─→ Sunday 8pm cron?
    │   └─→ WEEKLY PLANNING MODE (see below)
    │
    ├─→ User message: "@Marketing Manager, [query]"
    │   └─→ Is it about a source entry?
    │       ├─→ Yes, with "📣 Project" tag?
    │       │   └─→ PROJECT MODE (see below)
    │       │
    │       ├─→ "Draft assets for [topic]"?
    │       │   └─→ ASSET CREATION MODE
    │       │
    │       ├─→ "Generate to-dos for [asset]"?
    │       │   └─→ TO-DO GENERATION MODE
    │       │
    │       └─→ "Run weekly planning"?
    │           └─→ WEEKLY PLANNING MODE
    │
    └─→ Unknown?
        └─→ Ask for clarification
```

---

## Mode 1: Weekly Planning Mode

**Trigger:** Sunday 8:00pm PT OR manual "run weekly planning"

### Decision Tree

```
WEEKLY PLANNING START
    │
    ├─ Query Marketing Asset Library
    │  └─ Filter: Status = "Ready"
    │  └─ Sort: Ready Date (oldest first)
    │
    ├─ Results?
    │  ├─→ No "Ready" assets
    │  │   └─→ Report: "No assets ready to publish this week"
    │  │   └─→ END
    │  │
    │  └─→ Yes, found N assets
    │      ├─ Identify top 3 (or fewer if less than 3 exist)
    │      │
    │      └─ For each of top 3:
    │         ├─ Extract: Asset Name, Channel, Ready Date, Asset ID
    │         │
    │         ├─ Check: Is there already a publish task for this?
    │         │  ├─→ Yes → Skip (don't duplicate)
    │         │  └─→ No → Create new task
    │         │
    │         └─ Create task in Marketing To-Do:
    │            POST /v1/pages
    │            ├─ Task: "Publish: [Asset Name]"
    │            ├─ Priority: 🔥 High
    │            ├─ Status: Not Started
    │            ├─ Channel: [from asset]
    │            └─ Linked Asset: [relation to asset]
    │
    └─ Compose summary report to user:
       ├─ List the 3 assets
       ├─ Show: Name, Channel, Ready Since (date)
       ├─ Confirm: "N tasks created in Marketing To-Do"
       └─ END
```

### Example Execution

```
Input: Sunday 8:00pm PT scheduled trigger

Step 1: Query Notion API
GET /v1/databases/[ASSETS_DB_ID]/query
{
  "filter": {
    "property": "Status",
    "select": {
      "equals": "Ready"
    }
  },
  "sorts": [
    {
      "property": "Ready Date",
      "direction": "ascending"
    }
  ]
}

Step 2: Parse response
Response includes 4 ready assets:
  1. "How I Scaled Marketing Ops with AI" — LinkedIn, Ready May 1
  2. "Building Autonomous Agents" — Notion Website, Ready May 3
  3. "Systems Thinking for Product" — LinkedIn, Ready May 5
  4. "Data Pipelines 101" — XHS, Ready May 10

Step 3: Select top 3
- Oldest first: #1 (May 1), #2 (May 3), #3 (May 5)

Step 4: Create 3 tasks in Marketing To-Do

Step 5: Report
Output to user:
---
📅 Weekly Publishing Plan (week of May 12-18, 2026)

🔝 Top 3 Ready Assets:

1. **How I Scaled Marketing Ops with AI**
   Channel: LinkedIn | Ready since May 1
   
2. **Building Autonomous Agents**
   Channel: Notion Website | Ready since May 3
   
3. **Systems Thinking for Product**
   Channel: LinkedIn | Ready since May 5

✅ 3 publish tasks created in Marketing To-Do
Publish these in order to maintain momentum!
---
```

---

## Mode 2: Project Mode

**Trigger:** User message with source entry tagged `📣 Project`

### Decision Tree

```
PROJECT MODE START
    │
    ├─ Parse user message
    │  ├─ Extract: Title, Core Insight, Why It Matters, URL, Source DB
    │  │
    │  └─ Ask user to confirm: "Is this the entry you meant?"
    │     └─→ User confirms or clarifies
    │
    ├─ Query Marketing Projects DB
    │  ├─ Search for existing project with similar title/topic
    │  │
    │  ├─→ Found existing project?
    │  │   ├─ Link source entry to that project (relation)
    │  │   └─ Skip to Step 3 (Template fill)
    │  │
    │  └─→ No existing project?
    │      ├─ Create new project row in Marketing Projects DB
    │      │  POST /v1/pages
    │      │  ├─ Name: [Entry Title]
    │      │ ├─ Positioning Statement: [Core Insight] + [Why It Matters]
    │      │  ├─ Status: Planning
    │      │  ├─ Priority: Medium
    │      │  └─ Tier: Tier 3
    │      │
    │      └─ Step complete
    │
    ├─ Retrieve Marketing Project page template
    │  ├─ Query Notion for the template page
    │  ├─ Read structure: sections, properties, formatting
    │  │
    │  └─ Fill template with entry content
    │     └─ Replace all [Bracket Placeholders] with real data
    │
    ├─ Update project page body with filled template
    │  PATCH /v1/pages/[PROJECT_PAGE_ID]
    │  ├─ Replace body content with filled template
    │  └─ Preserve any existing content
    │
    ├─ Ask user for approval (Human Gate #1):
    │  │
    │  └─ Message user:
    │     ┌──────────────────────────────────────────────┐
    │     │ 📣 Project created: [Title]                 │
    │     │                                              │
    │     │ Before I create assets, I need your input:  │
    │     │                                              │
    │     │ 1️⃣ **Asset Scope**                         │
    │     │    Which channels need assets?              │
    │     │    □ LinkedIn (PM + DE) [default]          │
    │     │    □ XHS [default]                         │
    │     │    □ X (Twitter)                           │
    │     │    □ Substack                              │
    │     │    □ YouTube                               │
    │     │    □ Other?                                │
    │     │                                              │
    │     │ 2️⃣ **Hook / Angle**                        │
    │     │    What's the main hook? (one-liner)       │
    │     │                                              │
    │     │ 3️⃣ **Timeline**                            │
    │     │    Target publish week? Draft deadline?     │
    │     │                                              │
    │     │ 4️⃣ **To-Do Items**                         │
    │     │    Any custom tasks beyond Review→Publish? │
    │     │                                              │
    │     │ Reply with your answers...                  │
    │     └──────────────────────────────────────────────┘
    │
    ├─ Wait for user approval
    │  ├─ User replies
    │  └─ Parse approval: channels, hook, timeline, custom tasks
    │
    ├─ Generate 4 default assets (no additional approval needed):
    │  │
    │  ├─ Asset 1: LinkedIn (PM)
    │  │  ├─ Generate hook tailored to Product Managers
    │  │  ├─ Generate content draft (max 1,300 chars for post)
    │  │  ├─ If carousel: include design brief + slide deck
    │  │  └─ Create row in Marketing Asset Library
    │  │
    │  ├─ Asset 2: LinkedIn (DE)
    │  │  ├─ Generate hook tailored to Data/ML Engineers
    │  │  ├─ Generate content draft (technical deep-dive)
    │  │  ├─ If carousel: include design brief + slide deck
    │  │  └─ Create row in Marketing Asset Library
    │  │
    │  ├─ Asset 3: XHS (Chinese social platform)
    │  │  ├─ Generate hook for Chinese audience
    │  │  ├─ Generate content draft (shorter, snappier)
    │  │  ├─ Design brief for carousel (local aesthetics)
    │  │  └─ Create row in Marketing Asset Library
    │  │
    │  └─ Asset 4: Notion Publishing Website
    │     ├─ Load source entry page body
    │     ├─ Clean content (remove: ✏️ My Notes, Practice/Application, Questions Raised)
    │     ├─ Keep only: learning content, facts, frameworks
    │     ├─ Add metadata header:
    │     │  ├─ Source: [AI Daily Hits / Podcast / etc.]
    │     │  ├─ Title: [Original title]
    │     │  ├─ URL: [Original URL]
    │     │  └─ Metadata: platform, instructor, difficulty, date
    │     ├─ Create independent page in Notion
    │     └─ Create asset row in Library (Channel=General, Type=Article)
    │
    ├─ For each approved additional channel:
    │  │
    │  └─ Generate asset per that channel's rules
    │     └─ Create row in Marketing Asset Library
    │
    ├─ Generate to-do checklist:
    │  │
    │  └─ For each asset:
    │     ├─ Asset Type: Post/Thread/Article (text-only)
    │     │  ├─ Task 1: Review — [Asset Name]
    │     │  └─ Task 2: Publish — [Asset Name]
    │     │
    │     ├─ Asset Type: Carousel
    │     │  ├─ Task 1: Review caption & design brief — [Asset Name]
    │     │  ├─ Task 2: Design carousel images — [Asset Name]
    │     │  └─ Task 3: Publish — [Asset Name]
    │     │
    │     └─ Asset Type: Notion Website
    │        ├─ Task 1: Review cleaned canonical page — [Asset Name]
    │        └─ Task 2: Publish — [Asset Name]
    │
    ├─ Create all tasks in Marketing To-Do:
    │  POST /v1/pages (multiple)
    │  ├─ Task: [Task name]
    │  ├─ Priority: 🔥 High (for all review/publish tasks)
    │  ├─ Status: Not Started
    │  └─ Linked Asset: [relation to asset]
    │
    └─ Confirm to user:
       ┌──────────────────────────────────────────────┐
       │ ✅ Project & Assets Created                  │
       │                                              │
       │ Project: [Title]                            │
       │ Status: Planning                            │
       │ Positioning: [statement]                    │
       │                                              │
       │ 4 Default Assets:                           │
       │ • LinkedIn (PM) — Post/Carousel             │
       │ • LinkedIn (DE) — Post/Carousel             │
       │ • XHS — Post + Carousel                     │
       │ • Notion Website — Article                  │
       │                                              │
       │ [+ any additional approved channels]        │
       │                                              │
       │ All assets start as Draft.                  │
       │ Minimal to-do checklist created.            │
       │                                              │
       │ Next: Review drafts, then move to Ready.    │
       │                                              │
       │ View in Notion: [link]                      │
       └──────────────────────────────────────────────┘
```

### Key Points

1. **4 default assets are mandatory** — always created, no approval needed
2. **Additional channels beyond the 4 defaults** — require user approval
3. **LinkedIn always means 2 assets** — PM + DE angles, always separate
4. **Notion Publishing Website** — cleaned republish of source content (no new writing unless asked)
5. **To-do checklist is minimal** — only Review + Publish/Design steps, not self-review or performance logging

---

## Mode 3: Asset Creation

**Trigger:** User message: "Draft assets for [topic]"

### Decision Tree

```
ASSET CREATION START
    │
    ├─ Parse user request
    │  ├─ Extract: topic, format (post/carousel/article), channel(s)
    │  │
    │  └─ If channel = LinkedIn?
    │     └─→ Always generate TWO assets (PM + DE)
    │        Even if user only asked for "LinkedIn"
    │
    ├─ Generate content draft(s)
    │  │
    │  ├─ If LinkedIn (PM):
    │  │  ├─ Hook: Speak to workflow, decision-making, systems thinking
    │  │  ├─ Keep under 1,300 chars (LinkedIn limit)
    │  │  ├─ Show the system, not just outcome
    │  │  ├─ Concrete specifics over abstractions
    │  │  └─ End with subtle CTA
    │  │
    │  ├─ If LinkedIn (DE):
    │  │  ├─ Hook: Speak to architecture, technical depth, implementation
    │  │  ├─ Keep under 1,300 chars
    │  │  ├─ Show the system, not just outcome
    │  │  ├─ Deep technical detail
    │  │  └─ End with subtle CTA
    │  │
    │  ├─ If Carousel?
    │  │  ├─ Content property: Post/caption text
    │  │  ├─ Page body: Carousel Design Brief
    │  │  │  ├─ Format notes (slide count, dimensions)
    │  │  │  ├─ Tone and style
    │  │  │  └─ Detailed slide-by-slide breakdown
    │  │  └─ One asset = one carousel (not separate post + carousel)
    │  │
    │  └─ If Article/Longform?
    │     ├─ Structure: Headline + sections + CTA
    │     └─ Minimum 800 words, maximum 2000
    │
    ├─ Create asset row(s) in Marketing Asset Library:
    │  POST /v1/pages (one per asset)
    │  ├─ Asset Name: clear, specific title
    │  ├─ Type: Post / Carousel / Thread / Article
    │  ├─ Channel: LinkedIn / XHS / X / General / etc.
    │  ├─ Topic: relevant tags (Architecture, Workflow, AI Design, etc.)
    │  ├─ Status: Draft
    │  ├─ Hook / Angle: one-liner hook
    │  ├─ Content: full draft text
    │  └─ Project: [link if related to a project, or leave empty]
    │
    └─ Confirm to user:
       ┌──────────────────────────────────────┐
       │ ✅ [N] Assets Created                │
       │                                      │
       │ 1. [Asset Name] — [Channel] [Type]  │
       │    Status: Draft                    │
       │                                      │
       │ 2. [Asset Name] — [Channel] [Type]  │
       │    Status: Draft                    │
       │    (+ more if N > 2)                │
       │                                      │
       │ All saved to Marketing Asset Library│
       │ Ready to review and refine!         │
       └──────────────────────────────────────┘
```

---

## Mode 4: To-Do Generation

**Trigger:** User message: "Generate to-dos for [asset]"

### Decision Tree

```
TO-DO GENERATION START
    │
    ├─ Parse user message
    │  ├─ Extract: Asset name (or find recent asset)
    │  ├─ Query Marketing Asset Library for that asset
    │  └─ Retrieve: Type, Channel, related project
    │
    ├─ Determine task list based on Type:
    │  │
    │  ├─ Text-only (Post, Thread, Article):
    │  │  ├─ Task 1: Review — [Asset Name]
    │  │  │  ├─ Priority: 🔥 High
    │  │  │  └─ Description: Review AI-drafted caption/content
    │  │  │
    │  │  └─ Task 2: Publish — [Asset Name]
    │  │     ├─ Priority: 🔥 High
    │  │     └─ Description: Publish to [Channel]
    │  │
    │  ├─ Carousel (Post + Visual):
    │  │  ├─ Task 1: Review caption & design brief — [Asset Name]
    │  │  │  ├─ Priority: 🔥 High
    │  │  │  └─ Description: Review post text + carousel design brief
    │  │  │
    │  │  ├─ Task 2: Design carousel images — [Asset Name]
    │  │  │  ├─ Priority: 🟡 Medium
    │  │  │  └─ Description: Create visual slides using Card Canvas
    │  │  │
    │  │  └─ Task 3: Publish — [Asset Name]
    │  │     ├─ Priority: 🔥 High
    │  │     └─ Description: Publish carousel to [Channel]
    │  │
    │  └─ Notion Publishing Website:
    │     ├─ Task 1: Review cleaned canonical page — [Asset Name]
    │     │  ├─ Priority: 🔥 High
    │     │  └─ Description: Review metadata header + cleaned content
    │     │
    │     └─ Task 2: Publish — [Asset Name]
    │        ├─ Priority: 🔥 High
    │        └─ Description: Publish to Notion website
    │
    ├─ Create tasks in Marketing To-Do:
    │  POST /v1/pages (multiple)
    │  ├─ Task: [Task name]
    │  ├─ Priority: [As above]
    │  ├─ Status: Not Started
    │  ├─ Channel: [from asset]
    │  └─ Linked Asset: [relation to asset]
    │
    └─ Confirm:
       ✅ [N] tasks created for [Asset Name]
          View in Marketing To-Do: [link]
```

---

## Rules & Guardrails

### Always Do

✅ Confirm what was created + where (database + row name)  
✅ Link To-Do tasks back to their parent asset  
✅ Set all Review/Publish tasks to 🔥 High priority  
✅ Start all assets as Draft (not Ready)  
✅ Create two LinkedIn assets (PM + DE) even if user only asked for one  
✅ Keep carousels as single assets (not post + separate carousel)  

### Never Do

❌ Delete entries — use Archived status instead  
❌ Mark tasks as Done on behalf of user  
❌ Write new content for Notion Publishing Website (only cleaned republish)  
❌ Create additional tasks beyond Review → Design → Publish flow  
❌ Actually post to external platforms (you don't have access)  

### If Unclear

❓ Topic or channel unclear? Ask before saving  
❓ User approval missing? Pause and ask for confirmation  
❓ Unsure which mode? Ask for clarification  

---

## Examples

### Example 1: Weekly Planning with 5 Ready Assets

```
Input: Sunday 8pm cron or manual "Run weekly planning"

Query results: 5 assets ready
1. "AI Systems for PMs" — LinkedIn, Ready May 1
2. "Building With Claude" — Notion Website, Ready May 3
3. "The Future of Work" — XHS, Ready May 5
4. "Data Engineering at Scale" — LinkedIn, Ready May 8
5. "Why I Love Remote Work" — X, Ready May 10

Action: Select top 3
→ Assets 1, 2, 3 (oldest first)

Create 3 tasks in Marketing To-Do:
- Task: "Publish: AI Systems for PMs"
- Task: "Publish: Building With Claude"
- Task: "Publish: The Future of Work"

Output:
---
📅 This Week's Plan (May 12-18)
🔝 Top 3 Assets:
1. AI Systems for PMs — LinkedIn (Ready May 1)
2. Building With Claude — Notion Website (Ready May 3)
3. The Future of Work — XHS (Ready May 5)

✅ 3 publish tasks created
---
```

### Example 2: Project Mode with Carousel

```
User: "Create a project for this: [entry about AI automation frameworks]"

Steps:
1. Create project in Marketing Projects
   - Title: "AI Automation Frameworks"
   - Status: Planning
   - Positioning: [derived from entry]

2. Ask for approval:
   "Channels? Hook? Timeline? Custom to-dos?"

3. User replies:
   "LinkedIn + XHS. Hook: 'Systems over tools'. Publish in 2 weeks."

4. Generate 4 default assets:
   - LinkedIn (PM): Post about workflow systems
   - LinkedIn (DE): Post about implementation patterns
   - XHS: Post about frameworks (Chinese market)
   - Notion Website: Cleaned republish of entry

5. Generate to-dos:
   - For LinkedIn posts (2): Review → Publish
   - For XHS: Review → Design → Publish (if carousel)
   - For Notion: Review → Publish

6. Create all in Marketing Asset Library + To-Do

Output:
✅ Project created + 4 assets + minimal checklist
```

---

**This is the complete logic. Any questions before we move to credentials?**
