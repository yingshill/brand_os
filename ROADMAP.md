# Roadmap — Signal to Asset

| Symbol | Meaning |
|---|---|
| ✅ | Done |
| 🔄 | In progress |
| 🔲 | Backlog |

---

## Done

- ✅ Core Python scripts — `notion_client`, `fetch_entry`, `create_project`, `create_asset`, `create_todo`, `update_entry_status`, `weekly_planning`
- ✅ Agent instructions — `CLAUDE.md` (Project Mode, Asset Mode, To-Do Mode, Weekly Planning Mode)
- ✅ README with badges and repo structure
- ✅ Portfolio artifact — Architecture diagram (Notion Light + Dark Tech)

---

## Active

- 🔄 **Live credentials** — fill `.env` with `NOTION_TOKEN` + all DB IDs
- 🔄 **End-to-end live test** — paste a real source URL, run Project Mode, confirm assets land in Notion

---

## Backlog

### Features

- 🔲 Connect **Marketing Projects** DB to integration in Notion (`...` → Connections → signal-to-asset), then run `test_run.py` to confirm 13/13

### Production hardening

| # | Item | File(s) affected | Priority |
|---|---|---|---|
| P1 | ~~**Shell injection** — pipe JSON via stdin instead of `sys.argv` to prevent breakage when content contains single quotes~~ ✅ | all scripts + CLAUDE.md | Critical |
| P2 | ~~**Idempotency** — check for existing `(project_id, channel, type)` before creating asset; check `(asset_id, task_name)` before creating todo~~ ✅ | `create_asset.py`, `create_todo.py` | Critical |
| P3 | ~~**Retry logic** — exponential backoff on 429 + 5xx in `notion_client.py`~~ ✅ | `notion_client.py` | Critical |
| P4 | ~~**Cache invalidation gap** — `update_page` must also bust `db_{parent_db_id}_*` caches, not just the page cache~~ ✅ | `notion_client.py`, `update_entry_status.py` | High |
| P5 | **Pagination** — `query_database` doesn't follow `has_more` cursor; silently misses results beyond 100 rows | `notion_client.py` | High |
| P6 | **Run audit log** — append `logs/runs.jsonl` per run (timestamp, project_id, asset_ids, todo_ids) | new `logs/` dir | High |
| P7 | **Silent content truncation** — warn user when content is truncated in the Notion property field | `create_asset.py` | Medium |
| P8 | **Error categorization** — distinguish 400 schema errors vs 429 rate limits vs network errors in script output | all scripts | Medium |
| P9 | **Approval gate** — re-ask only the ambiguous answer instead of accepting a freeform 4-in-1 reply | `CLAUDE.md` | Medium |
| P10 | **Mode detection disambiguation** — add explicit confirmation step before starting full pipeline from a URL | `CLAUDE.md` | Low |

### Portfolio artifacts

#### Demo Video / GIF 🔲

60–90 second screen recording of Project Mode running end-to-end.

**Shot list:**
1. Open Claude Code in the project directory
2. Paste a Notion source entry URL
3. Agent fetches entry, shows title / core insight / confirmation prompt
4. Type approval — channels, hook, timeline
5. Agent generates drafts, runs scripts, confirms assets created
6. Cut to Notion — show finished asset rows in Marketing Asset Library

**Format options:**
- GIF (looping, no audio) — GitHub embeds, README
- MP4 with captions — LinkedIn, portfolio hero

**Placement:**
- [ ] Portfolio website — hero section
- [ ] LinkedIn — "I built an agent that does X" launch post
- [ ] GitHub profile README — GIF embed
- [ ] signal-to-asset README — replace mermaid diagram

**Decisions before recording:**
- [ ] Narration or silent + captions?
- [ ] Real Notion data or clean example data?
- [ ] Tool: QuickTime + Gifski (GIF) or Loom (MP4)

**Blocked by:** live credentials + successful end-to-end test

---

## Portfolio artifacts tracker

| Artifact | Status | Themes | Placement |
|---|---|---|---|
| Architecture diagram | ✅ | Notion Light · Dark Tech | Portfolio · LinkedIn · GitHub README · GitHub profile |
| Code walkthrough carousel | ✅ | Notion Light | LinkedIn · GitHub README · Portfolio |
| Case study | ✅ | Notion Light | Portfolio · LinkedIn · GitHub README |
| Demo video / GIF | 🔲 backlog | — | Portfolio hero · LinkedIn · GitHub README · GitHub profile |

**Artifact files:**

| Artifact | Theme | Folder |
|---|---|---|
| Architecture diagram | Notion Light | `artifacts/architecture-diagram/notion-light/` |
| Architecture diagram | Dark Tech | `artifacts/architecture-diagram/dark-tech/` |
| Code walkthrough carousel | Notion Light | `artifacts/code-walkthrough-carousel/notion-light/` |
| Case study | Notion Light | `artifacts/case-study/notion-light/` |

Each folder: `index.html` (self-contained portal) + `diagram.svg` (raw, embeddable).

---

## Open questions

- [ ] Portfolio website — domain and stack? (affects video embed format)
- [ ] GitHub profile README — exists already, or needs to be created?
- [ ] Notion recording data — real entries or clean example data?
