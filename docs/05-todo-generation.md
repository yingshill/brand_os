# ✅ To-Do Generation Mode

When a new asset is added or when asked to generate a production checklist for an asset.

## Default tasks — text-only assets (Post, Thread, Article)

| # | Task | Priority | Owner notes |
|---|---|---|---|
| 1 | **Review — [Asset Name]** | 🔥 High | Human reviews the AI-drafted caption/post in the Content property |
| 2 | **Publish — [Asset Name]** | 🔥 High | Human |

## Carousel / Diagram assets — post + carousel = single asset with both text + visuals

| # | Task | Priority | Owner notes |
|---|---|---|---|
| 1 | **Review caption & design brief — [Asset Name]** | 🔥 High | Human reviews AI-drafted caption (Content property) and carousel design brief + slide decks (page body) |
| 2 | **Design carousel images — [Asset Name]** | 🟡 Medium | Human creates the actual visual slides/images using [Card Canvas](https://www.cardcanvas.app/) from the design brief in the page body |
| 3 | **Publish — [Asset Name]** | 🔥 High | Human |

## Notion Publishing Website assets

| # | Task | Priority | Owner notes |
|---|---|---|---|
| 1 | **Review cleaned canonical page — [Asset Name]** | 🔥 High | Human reviews the cleaned source duplicate (metadata header + content) |
| 2 | **Publish — [Asset Name]** | 🔥 High | Human |

## Ownership model

| Actor | Responsible for |
|---|---|
| **AI** | Post/caption draft (Content property), carousel design brief (page body), Notion Publishing Website page (cleaned source duplicate with metadata header) |
| **Human** | Reviews all AI output, creates actual carousel images, publishes |

> Keep the task list minimal. Do not add self-review or 48h performance log tasks — those are the human's responsibility.
