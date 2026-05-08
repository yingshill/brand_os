# Claude Code Agent: Marketing Manager

This folder contains the setup and configuration for running the Marketing Manager as a **Claude Code scheduled agent** instead of a Notion custom agent.

## What You'll Find Here

| File | Purpose |
|------|---------|
| `CLAUDE_CODE_SETUP.md` | How to set up and schedule the agent in Claude Code |
| `MARKETING_MANAGER_AGENT.md` | Full agent prompt (copy this into `/schedule`) |
| `NOTION_SETUP.md` | How to get Notion API token and database IDs |
| `README.md` | This file |

## Quick Start (5 minutes)

### 1. Get Your Notion Integration Token

1. Visit https://www.notion.com/my-integrations
2. Create a new integration: `Marketing Manager Agent`
3. Grant read + write permissions
4. Copy the **Internal Integration Token**

### 2. Get Your Database IDs

Go to each of your 6 databases, open the URL, and extract the database ID:

```
https://www.notion.so/[workspace]/[DATABASE_ID]?v=[view_id]
                                ↑
                        This 32-char code
```

Database IDs you need:
- AI Daily Hits
- GitHub Daily Trending  
- Podcast & Video Digest
- Course Digest
- 📣 Marketing Projects
- 📦 Marketing Asset Library
- ✅ Marketing To-Do

### 3. Set Up Environment Variables

In Claude Code, add to your settings:

```json
{
  "env": {
    "NOTION_TOKEN": "your_token_here",
    "NOTION_AI_HITS_ID": "...",
    "NOTION_GITHUB_ID": "...",
    "NOTION_PODCAST_ID": "...",
    "NOTION_COURSE_ID": "...",
    "NOTION_PROJECTS_ID": "...",
    "NOTION_ASSETS_ID": "...",
    "NOTION_TODOS_ID": "..."
  }
}
```

### 4. Test the Agent

In Claude Code, run the agent prompt manually first:

Copy the full prompt from `MARKETING_MANAGER_AGENT.md` and run it in a Claude Code session to verify it connects to Notion.

### 5. Schedule It

Once tested, set up the weekly schedule:

```bash
/schedule "Weekly Marketing Plan" --cron "0 20 * * 0" --tz "America/Los_Angeles"
```

Then paste the agent prompt.

## How It Works

**Weekly Planning (Sunday 8pm PT):**
1. Agent queries `Marketing Asset Library` for `Status = Ready`
2. Identifies top 3 assets to publish
3. Creates `Publish: [Asset Name]` tasks in `Marketing To-Do`
4. Reports the week's plan

**On-Demand Modes:**
- **Project Mode** — Draft a full marketing project + assets
- **Asset Creation** — Generate drafts for any channel/format
- **To-Do Generation** — Create production checklists

## Cost Comparison

| Method | Monthly Cost | Setup Time |
|--------|-------------|-----------|
| Notion Business + Agent | $20-25 | Already done |
| **Claude Code + API** | **$0.30-1.50** | 5-10 min |

You save ~$240/year by switching to Claude Code scheduling with Claude API.

## Troubleshooting

**Agent can't connect to Notion:**
- Verify `NOTION_TOKEN` is set correctly
- Check database was shared with the integration
- See `NOTION_SETUP.md` for detailed help

**No tasks created on Sunday:**
- Check Claude Code logs for errors
- Manually test the agent prompt first
- Verify `Status = Ready` assets exist in your library

**Database not found:**
- Verify database ID is 32 characters
- Re-share the database with the integration

## Next Steps

1. ✅ Get Notion token + database IDs (see `NOTION_SETUP.md`)
2. ✅ Configure environment in Claude Code
3. ✅ Test agent manually
4. ✅ Set up weekly schedule
5. ✅ Monitor first 2-3 runs
6. ✅ Cancel Notion Business subscription (optional)

---

**Questions?** See the full documentation:
- `CLAUDE_CODE_SETUP.md` — Detailed setup
- `../../INSTRUCTIONS.md` — Complete behavior spec
- `../../docs/` — Mode-by-mode guides
