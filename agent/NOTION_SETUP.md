# Notion Integration Setup for Claude Code Agent

This guide explains how to set up the Notion API integration so the Claude Code agent can read/write to your databases.

## Step 1: Create a Notion Integration

1. Go to https://www.notion.com/my-integrations
2. Click **+ New integration**
3. Name it: `Marketing Manager Agent`
4. Select your workspace
5. Grant capabilities:
   - ✅ Read content
   - ✅ Update content
   - ✅ Insert content
6. Copy the **Internal Integration Token** (save this securely)

## Step 2: Share Databases with the Integration

For each of your 6 databases, you need to:

1. Open the database in Notion
2. Click **Share** (top right)
3. Search for your integration name: `Marketing Manager Agent`
4. Click to add it (grant Full access)
5. Copy the **Database ID** from the URL

### Finding Database IDs

In Notion, database URLs look like:
```
https://www.notion.so/[workspace-name]/[DATABASE_ID]?v=[view_id]
```

Extract the `DATABASE_ID` (32 characters, no dashes).

## Step 3: Collect All Database IDs

You need 6 database IDs:

### Source Databases (Read-only)
- [ ] `AI Daily Hits` — `db_id_here`
- [ ] `GitHub Daily Trending` — `db_id_here`
- [ ] `Podcast & Video Digest` — `db_id_here`
- [ ] `Course Digest` — `db_id_here`

### Output Databases (Read + Write)
- [ ] `📁 Projects → 📣 Marketing Projects` — `db_id_here`
- [ ] `📦 Marketing Asset Library` — `db_id_here`
- [ ] `✅ Marketing To-Do` — `db_id_here`

## Step 4: Configure Claude Code

You have two options:

### Option A: Environment Variables (Recommended)

In Claude Code settings (or via `/update-config`), add:

```json
{
  "env": {
    "NOTION_TOKEN": "secret_your_integration_token_here",
    "NOTION_AI_HITS_ID": "db_id_here",
    "NOTION_GITHUB_ID": "db_id_here",
    "NOTION_PODCAST_ID": "db_id_here",
    "NOTION_COURSE_ID": "db_id_here",
    "NOTION_PROJECTS_ID": "db_id_here",
    "NOTION_ASSETS_ID": "db_id_here",
    "NOTION_TODOS_ID": "db_id_here"
  }
}
```

### Option B: .env File in Repo

Create `.env` in your repo root:

```
NOTION_TOKEN=secret_your_integration_token_here
NOTION_AI_HITS_ID=db_id_here
NOTION_GITHUB_ID=db_id_here
NOTION_PODCAST_ID=db_id_here
NOTION_COURSE_ID=db_id_here
NOTION_PROJECTS_ID=db_id_here
NOTION_ASSETS_ID=db_id_here
NOTION_TODOS_ID=db_id_here
```

⚠️ **Don't commit this file to GitHub!** Add to `.gitignore`:

```
.env
.env.local
```

## Step 5: Test the Integration

In Claude Code, run a test query:

```bash
curl -H "Authorization: Bearer $NOTION_TOKEN" \
  https://api.notion.com/v1/databases/[NOTION_ASSETS_ID] \
  -H "Notion-Version: 2022-06-28"
```

If you get a successful response, the integration is set up correctly.

## Step 6: Ready to Schedule

Once configured, you can now:

1. Set up the weekly schedule
2. Test a manual run
3. Monitor logs for any Notion API errors

See `CLAUDE_CODE_SETUP.md` for scheduling instructions.

## Troubleshooting

### 401 Unauthorized
- Check your NOTION_TOKEN is correct
- Verify it's an Internal Integration Token (not API key)
- Ensure it's not expired

### 404 Not Found
- Double-check your database IDs (they should be 32 characters)
- Verify the database was shared with the integration
- Try re-sharing with Full access

### 403 Forbidden
- The integration doesn't have permission to that database
- Go back to Step 2 and re-share the database

### Queries succeed but no results
- Check the database ID is correct
- Verify the database has the expected properties/columns
- Check filters (Status = Ready, etc.) match your actual data

---

## Database Schema Verification

Before scheduling, verify your databases have these properties:

### Marketing Asset Library (Output)
- `Asset Name` (Title)
- `Type` (Select: Post, Carousel, Thread, Article, etc.)
- `Channel` (Select: LinkedIn, XHS, X, General, etc.)
- `Status` (Select: Draft, Ready, Published, Archived)
- `Hook / Angle` (Text)
- `Content` (Text/Rich text)
- `Topic` (Multi-select)
- `Project` (Relation → Marketing Projects)
- `Created` (Date)
- `Ready Date` (Date) — optional, used for sorting

### Marketing To-Do (Output)
- `Task` (Title)
- `Priority` (Select: 🔥 High, 🟡 Medium, 🔵 Low)
- `Status` (Select: Not Started, In Progress, Done)
- `Channel` (Select)
- `Linked Asset` (Relation → Marketing Asset Library)

### 📣 Marketing Projects (Output)
- `Name` (Title)
- `Positioning Statement` (Rich text)
- `Status` (Select: Planning, In Progress, Live, Archived)
- `Priority` (Select: 🔥 High, 🟡 Medium, 🔵 Low)
- `Tier` (Select: Tier 1, Tier 2, Tier 3)

### Source Databases
- `Title` (or `Name`)
- `Core Insight` (Text/Rich text)
- `Why It Matters` (Text/Rich text)
- `URL` (URL)
- `Status` (Select)
- `Output` (Multi-select or Text) — should include `📣 Project` tag
- `Project` (Relation) — optional, used for linking

---

**Next:** See `CLAUDE_CODE_SETUP.md` for scheduling the agent.
