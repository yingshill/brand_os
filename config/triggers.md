# Triggers

The agent fires on five triggers, all backed by the Notion integration.

| # | Type | When | Status |
|---|---|---|---|
| 1 | `notion.agent.mentioned` | User @-mentions the agent in any context | ✅ Enabled |
| 2 | `recurrence` (weekly) | Sunday 20:00 America/Los_Angeles | ✅ Enabled |
| 3 | `notion.page.updated` (Asset Library — Status = Ready) | Asset moves to `Ready` | ⏸️ Disabled |
| 4 | `notion.page.updated` (Source DBs — Done This Week ✅ + Output contains `🎨 Visualize`) | Visualize handoff (read-only watch) | ✅ Enabled |
| 5 | `notion.page.updated` (Projects — Output contains `📣 Project`) | Project Mode entry point | ✅ Enabled |

## Trigger 1 — `notion.agent.mentioned`

User-initiated. Fires whenever the agent is mentioned in a page or comment. The agent decides which mode to enter based on context.

## Trigger 2 — Sunday weekly recurrence

```json
{
  "type": "recurrence",
  "frequency": "week",
  "interval": 1,
  "weekdays": ["SU"],
  "hour": 20,
  "minute": 0,
  "timezone": "America/Los_Angeles"
}
```

Drives [📅 Weekly Planning Mode](../docs/06-weekly-planning.md).

## Trigger 3 — Asset Library `Ready` (currently disabled)

Watches the Asset Library data source for entries whose `Status` becomes `Ready`. Disabled today because weekly planning mode handles `Ready → Publish` task generation in batch on Sundays.

## Trigger 4 — Visualize handoff watch

Filter:

- `Done This Week` checkbox = true **AND**
- `Output` contains `🎨 Visualize`

This watches for the Brain Agent's signal but the Marketing Manager does not write — it's read-only context for understanding the publishing pipeline.

## Trigger 5 — Project Mode entry point

Filter on the Projects data source:

- `Output` contains `📣 Project`

Fires [📣 Project Mode](../docs/02-project-mode.md).

## Notes on enable / disable

Disabled triggers are kept in config (not deleted) so the trigger ID remains stable when re-enabled. Toggling vs deleting matters for downstream automations that reference trigger URLs.
