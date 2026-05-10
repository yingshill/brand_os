"""
Fetch a source entry from Notion by URL.

Usage:
    python scripts/fetch_entry.py "<notion_url>"

Output: JSON with entry details.
"""
import sys
import json
import os
sys.path.insert(0, os.path.dirname(__file__))
from notion_client import extract_page_id, get_page, extract_text, classify_error, DB_IDS


SOURCE_DBS = ['ai_daily_hits', 'github_trending', 'podcast_digest', 'course_digest']

TITLE_KEYS = ['Name', 'Title', 'title', 'name']
CORE_INSIGHT_KEYS = ['Core Insight', 'Core insight', 'core_insight']
WHY_MATTERS_KEYS = ['Why It Matters', 'Why it matters', 'why_it_matters']
URL_KEYS = ['URL', 'url', 'Source URL', 'Link']


def _first(props: dict, keys: list) -> str:
    for k in keys:
        if k in props:
            return extract_text(props[k])
    return ''


def identify_source_db(page: dict) -> str:
    parent = page.get('parent', {})
    db_id = parent.get('database_id', '').replace('-', '')
    for name in SOURCE_DBS:
        known = DB_IDS.get(name, '').replace('-', '')
        if known and known == db_id:
            return name
    return 'unknown'


def fetch_entry(url: str) -> dict:
    page_id = extract_page_id(url)
    page = get_page(page_id)
    props = page.get('properties', {})

    return {
        'page_id': page_id,
        'page_url': page.get('url', url),
        'source_db': identify_source_db(page),
        'title': _first(props, TITLE_KEYS),
        'core_insight': _first(props, CORE_INSIGHT_KEYS),
        'why_it_matters': _first(props, WHY_MATTERS_KEYS),
        'source_url': _first(props, URL_KEYS),
        'status': extract_text(props.get('Status', {})),
        'output': extract_text(props.get('Output', {})),
        'all_properties': list(props.keys()),
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Usage: python fetch_entry.py "<notion_url>"'}))
        sys.exit(1)
    try:
        result = fetch_entry(sys.argv[1])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({'error': str(e), 'kind': classify_error(e)}))
        sys.exit(1)
