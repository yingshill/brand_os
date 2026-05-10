"""
Create task(s) in Marketing To-Do.

Usage — single task:
    python scripts/create_todo.py <<'JSON'
    {"task": "Review — Asset Name", "priority": "🔥 High", "channel": "LinkedIn", "asset_id": "..."}
    JSON

Usage — batch:
    python scripts/create_todo.py <<'JSON'
    [{"task": "Review — Asset A", ...}, {"task": "Publish — Asset A", ...}]
    JSON

JSON shape (single):
    {
      "task": "Review — Asset Name",
      "priority": "🔥 High | 🟡 Medium",
      "channel": "LinkedIn",
      "asset_id": "optional asset page ID"
    }

Output: JSON with task_id and task name (or list of same).
"""
import sys
import json
import os
sys.path.insert(0, os.path.dirname(__file__))
from notion_client import (
    create_page, DB_IDS,
    title_prop, select_prop, relation_prop, status_prop,
)


def create_todo(data: dict) -> dict:
    db_id = DB_IDS['marketing_todos']
    if not db_id:
        raise ValueError("NOTION_DB_MARKETING_TODOS is not set in .env")

    properties = {
        'Task': title_prop(data['task']),
        'Priority': select_prop(data.get('priority', '🔥 High')),
        'Status': status_prop('Not Started'),
    }

    if data.get('channel'):
        properties['Channel'] = select_prop(data['channel'])

    if data.get('asset_id'):
        properties['Linked Asset'] = relation_prop([data['asset_id']])

    page = create_page(db_id, properties)

    return {
        'task_id': page['id'],
        'task': data['task'],
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
        print(json.dumps({'error': str(e)}))
        sys.exit(1)
