# 🧭 Quick Decision Tree

Use before writing anything.

```mermaid
flowchart TD
    Q1{"Is 📣 Project<br/>present?"}
    Q1 -->|No| N1["Only draft assets if explicitly requested.<br/>Otherwise do nothing."]
    Q1 -->|Yes| Q2

    Q2{"Has user approved<br/>scope + angle +<br/>timeline + checklist?"}
    Q2 -->|No| N2["Ask for approval.<br/>Do NOT create asset/to-do rows yet."]
    Q2 -->|Yes| Q3

    Q3{"Is it LinkedIn?"}
    Q3 -->|Yes| L["Always create 2 assets:<br/>LinkedIn (PM) + LinkedIn (DE)"]
    Q3 -->|No| C["Create assets per approved scope"]

    L --> D["Plus the 4 default assets<br/>(no approval needed):<br/>LinkedIn PM, LinkedIn DE,<br/>XHS, Notion Publishing Website"]
    C --> D
```

## Decision rules in plain text

1. **Is `📣 Project` present?**
   - **No** → Only draft assets if explicitly requested; otherwise do nothing.
   - **Yes** → Continue.
2. **Has the user approved asset scope + angle + timeline + checklist?**
   - **No** → Ask for approval (do not create asset/to-do rows yet).
   - **Yes** → Create assets, then generate minimal to-dos.
3. **Is it LinkedIn?**
   - **Yes** → Always create **two assets**: LinkedIn (PM) + LinkedIn (DE).
   - **No** → Create assets per approved scope.
4. **4 default assets (always created, no approval needed):**
   - LinkedIn (PM)
   - LinkedIn (DE)
   - XHS
   - Notion Publishing Website
