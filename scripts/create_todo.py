"""
Create task(s) in Marketing To-Do.

Todo names follow the deterministic convention:
    "Review — {asset_name}"
    "Publish — {asset_name}"
    "Design carousel — {asset_name}"
    "Review cleaned canonical page — {asset_name}"

Usage — single task:
    python scripts/create_todo.py <<'JSON'
    {"task": "Review — MCP is the new API — LinkedIn (PM)", "priority": "🔥 High", "channel": "LinkedIn", "asset_id": "..."}
    JSON

Usage — batch:
    python scripts/create_todo.py <<'JSON'
    [{"task": "Review — ...", ...}, {"task": "Publish — ...", ...}]
    JSON

JSON shape (single):
    {
      "task": "Review — {asset_name}",
      "priority": "🔥 High | 🟡 Medium",
      "channel": "LinkedIn",
      "asset_id": "optional asset page ID"
    }

Output: JSON with task_id, task name, action (created | existing) — or list of same.
"""
import sys
import json
import os
sys.path.insert(0, os.path.dirname(__file__))
from notion_client import (
    query_database, create_page, classify_error, DB_IDS,
    title_prop, select_prop, relation_prop, status_prop,
)


def find_existing_todo(task: str) -> dict | None:
    db_id = DB_IDS['marketing_todos']
    if not db_id:
        return None
    pages = query_database(db_id, filter_obj={
        'property': 'Task',
        'title': {'equals': task},
    })
    return pages[0] if pages else None


def create_todo(data: dict) -> dict:
    db_id = DB_IDS['marketing_todos']
    if not db_id:
        raise ValueError("NOTION_DB_MARKETING_TODOS is not set in .env")

    task = data['task']

    existing = find_existing_todo(task)
    if existing:
        return {
            'action': 'existing',
            'task_id': existing['id'],
            'task': task,
            'priority': data.get('priority', '🔥 High'),
        }

    properties = {
        'Task': title_prop(task),
        'Priority': select_prop(data.get('priority', '🔥 High')),
        'Status': status_prop('Not Started'),
    }

    if data.get('channel'):
        properties['Channel'] = select_prop(data['channel'])

    if data.get('asset_id'):
        properties['Linked Asset'] = relation_prop([data['asset_id']])

    page = create_page(db_id, properties)

    return {
        'action': 'created',
        'task_id': page['id'],
        'task': task,
        'priority': data.get('priority', '🔥 High'),
    }


if __name__ == '__main__':
    try:
        raw = json.loads(sys.stdin.read())
        if isinstance(raw, list):
            result = [create_todo(item) for item in raw]
        else:
            result = create_todo(raw)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({'error': str(e), 'kind': classify_error(e)}))
        sys.exit(1)
