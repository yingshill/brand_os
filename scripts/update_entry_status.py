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
from notion_client import update_page, select_prop


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(json.dumps({'error': 'Usage: update_entry_status.py <page_id> <status>'}))
        sys.exit(1)
    try:
        page_id = sys.argv[1]
        status = sys.argv[2]
        update_page(page_id, {'Status': select_prop(status)})
        print(json.dumps({'updated': True, 'page_id': page_id, 'status': status}))
    except Exception as e:
        print(json.dumps({'error': str(e)}))
        sys.exit(1)
