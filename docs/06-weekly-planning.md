# 📅 Weekly Planning Mode

Runs when asked to run weekly planning, or automatically on the Sunday recurrence trigger (8:00pm America/Los_Angeles).

## Steps

1. **Query the Marketing Asset Library** for all entries with `Status = Ready`.
2. **Surface the top 3 assets** to publish that week, prioritizing:
   - Oldest `Ready` date first
   - LinkedIn and X / Twitter content over longer-form pieces
3. **For each selected asset, create a corresponding task** in **Marketing To-Do** with:

   | Property | Value |
   |---|---|
   | **Task** | `Publish: [Asset Name]` |
   | **Priority** | 🔥 High |
   | **Status** | Not Started |
   | **Channel** | Matching the asset's channel |
   | **Linked Asset** | Linked to the asset entry |

4. **Summarize the week's publishing plan** to the user.

## Trigger details

See [`config/triggers.md`](../config/triggers.md) for the recurrence configuration. Default cadence: weekly, Sunday, 20:00 PT.
