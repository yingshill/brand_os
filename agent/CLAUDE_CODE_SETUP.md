# Claude Code Scheduled Agent Setup

This document explains how to run the Marketing Manager as a Claude Code scheduled agent instead of a Notion custom agent.

## Quick Start

### 1. Prerequisites
- Claude Code with access to Notion integration
- A Notion integration token with database read/write permissions
- Your workspace ID and database IDs for:
  - 4 source databases (AI Daily Hits, GitHub Daily Trending, Podcast & Video Digest, Course Digest)
  - 3 output databases (Marketing Projects, Marketing Asset Library, Marketing To-Do)

### 2. Set Up Environment Variables

In your Claude Code settings, add:

```json
{
  "NOTION_TOKEN": "your_notion_integration_token",
  "NOTION_DB_SOURCES": {
    "ai_daily_hits": "database_id_here",
    "github_trending": "database_id_here",
    "podcast_digest": "database_id_here",
    "course_digest": "database_id_here"
  },
  "NOTION_DB_OUTPUTS": {
    "marketing_projects": "database_id_here",
    "marketing_assets": "database_id_here",
    "marketing_todos": "database_id_here"
  }
}
```

### 3. Schedule the Agent

#### Weekly Planning (Sundays 8pm PT)

```bash
/schedule "Run weekly marketing planning" --cron "0 20 * * 0" --tz "America/Los_Angeles"
```

Then paste the full agent prompt from `MARKETING_MANAGER_AGENT.md`.

#### On-Demand (Test First)

Run manually to test:
```bash
/schedule --run "Run weekly marketing planning"
```

### 4. Agent Modes

The agent runs in different modes based on context:

- **Weekly Planning Mode** — Sunday 8pm cron job, surfaces top 3 ready assets
- **Project Mode** — When you query it with a source entry tagged `📣 Project`
- **Asset Creation Mode** — When you ask it to draft assets for a specific topic
- **To-Do Generation Mode** — When you ask it to create a production checklist

## How It Works

1. **Scheduled trigger** → Agent wakes up on Sunday 8pm PT (or on-demand)
2. **Query Notion** → Reads Marketing Asset Library for `Status = Ready` entries
3. **Generate tasks** → Creates publish tasks in Marketing To-Do
4. **Report back** → Summarizes the week's plan

## Manual Triggers

You can invoke the agent manually by running:

```bash
/schedule --run "Run weekly marketing planning"
```

Or by mentioning the agent in a message with a query like:
```
@Marketing Manager, generate assets for this topic: [source entry details]
```

## Disabling the Schedule

To stop the scheduled run:

```bash
/schedule --list
/schedule --delete <schedule_id>
```

## Monitoring & Logs

Claude Code logs are available in your session. Check the output after each run to ensure:
- ✅ Notion databases were queried successfully
- ✅ Tasks were created (or none needed)
- ✅ No errors encountered

## Next Steps

1. Copy your database IDs from Notion
2. Add them to your environment
3. Run a test manually
4. Set up the weekly schedule
5. Monitor the first 2-3 runs

---

**See also:**
- `MARKETING_MANAGER_AGENT.md` — Full agent prompt
- `../INSTRUCTIONS.md` — Complete agent behavior specification
