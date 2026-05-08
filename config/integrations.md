# Integrations & permissions

The agent has a single Notion integration with the following access matrix.

## Notion integration

| Surface | Action | Purpose |
|---|---|---|
| Web search | Allow | Lookup external context for drafts |
| 📦 Marketing Asset Library | Edit | Create / update asset rows |
| ✅ Marketing To-Do | Edit | Create / update production tasks |
| 📁 Projects (📣 Marketing Projects data source) | Edit | Create / update marketing project rows |
| 🏛️ AI Command Center | View | Read for context, append to Agent Performance Insights |
| 🧠 AI Daily Hits (source DB) | View | Read source entries flagged 📣 Project |
| 📈 GitHub Daily Trending (source DB) | View | Read source entries flagged 📣 Project |
| 🎙️ Podcast & Video Digest (source DB) | View | Read source entries flagged 📣 Project |
| 📖 Course Digest (source DB) | Edit | Read source entries flagged 📣 Project; update Status when relation column missing |
| 🗺️ Topic Hub | View | Read for asset topic resolution |
| 📋 Marketing Plan Template | View | Load template structure for project page bodies |
| Additional reference pages (workspace context) | View / Edit | As granted on agent setup |

> Specific page/database URLs are intentionally omitted from this repo — they live in the agent's actual configuration in Notion. This file documents the *access model*, not workspace identifiers.

## Why view-only on the source DBs

The Marketing Manager **reads** source entries to build assets but does not modify them — except setting `Status = In Progress` when `📣 Project` is set. Course Digest is currently `Edit` because it's the only source DB with the `Project` relation column maintained by this agent. As other source DBs gain the column, their access widens.
