# 🤝 Alignment with the Brain Agent

The Marketing Manager and the AI Intelligence Brain Agent share the workspace but do not overlap.

## Boundary

| Agent | Owns |
|---|---|
| **🤖 Brain Agent** | Signal scouting · database row creation in the four signal databases · `🎨 Visualize` page-body visualization drafts |
| **🌐 Marketing Manager** | Everything that happens after the human sets `📣 Project` — creating/updating a row in **📣 Marketing Projects**, optionally linking the source entry, and generating downstream marketing assets + to-dos |

## Handoff signal

The `Output` property on each source entry is the explicit handoff:

- `🎨 Visualize` → Brain Agent
- `📣 Project` → Marketing Manager

Neither agent acts on the other's signal.

## Why no overlap

Clear ownership prevents:

- Duplicate writes to the same row
- Conflicting drafts of the same asset
- Ambiguity about whose responsibility a downstream artifact is

If a request blurs the boundary, the Marketing Manager defers to the human to clarify which agent should run.
