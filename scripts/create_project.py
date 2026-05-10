"""
Create or find a Marketing Project in Notion.

Usage:
    python scripts/create_project.py <<'JSON'
    {
      "title": "Project Title",
      "positioning": "One-sentence positioning statement"
    }
    JSON

Output: JSON with project_id, project_url, action (created | linked).
"""
import sys
import json
import os
sys.path.insert(0, os.path.dirname(__file__))
from notion_client import (
    query_database, create_page, extract_text, classify_error, DB_IDS,
    title_prop, rich_text_prop, select_prop,
)


def find_existing_project(title: str) -> dict:
    db_id = DB_IDS['marketing_projects']
    if not db_id:
        return None
    pages = query_database(db_id)
    title_lower = title.lower().strip()
    for page in pages:
        props = page.get('properties', {})
        existing = extract_text(
            props.get('Name') or props.get('Title') or {}
        ).lower().strip()
        if existing and (title_lower in existing or existing in title_lower):
            return page
    return None


def create_project(data: dict) -> dict:
    db_id = DB_IDS['marketing_projects']
    if not db_id:
        raise ValueError("NOTION_DB_MARKETING_PROJECTS is not set in .env")

    title = data.get('title', '').strip()
    positioning = data.get('positioning', '').strip()

    existing = find_existing_project(title)
    if existing:
        return {
            'action': 'linked',
            'project_id': existing['id'],
            'project_url': existing.get('url', ''),
            'title': title,
        }

    page = create_page(db_id, {
        'Name': title_prop(title),
        'Positioning Statement': rich_text_prop(positioning),
        'Status': select_prop('Planning'),
        'Priority': select_prop('🟡 Medium'),
        'Tier': select_prop('🔵 Tier 3'),
    })

    return {
        'action': 'created',
        'project_id': page['id'],
        'project_url': page.get('url', ''),
        'title': title,
    }


if __name__ == '__main__':
    try:
        data = json.loads(sys.stdin.read())
        result = create_project(data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({'error': str(e), 'kind': classify_error(e)}))
        sys.exit(1)
