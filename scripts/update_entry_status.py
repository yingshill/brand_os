"""
Update the Status property of a Notion page (source entry).

Usage:
    python scripts/update_entry_status.py <page_id> <status>

Example:
    python scripts/update_entry_status.py abc123... "In Progress"
"""
import sys
import json
import os
sys.path.insert(0, os.path.dirname(__file__))
from notion_client import get_page, update_page, select_prop, classify_error


def update_entry_status(page_id: str, status: str) -> dict:
    # get_page is a cache hit in normal workflow (fetch_entry ran earlier)
    page = get_page(page_id)
    parent_db_id = page.get('parent', {}).get('database_id', '').replace('-', '') or None
    update_page(page_id, {'Status': select_prop(status)}, parent_db_id=parent_db_id)
    return {'updated': True, 'page_id': page_id, 'status': status}


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(json.dumps({'error': 'Usage: update_entry_status.py <page_id> <status>'}))
        sys.exit(1)
    try:
        result = update_entry_status(sys.argv[1], sys.argv[2])
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({'error': str(e), 'kind': classify_error(e)}))
        sys.exit(1)
