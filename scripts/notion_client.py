"""Notion API base client. All scripts import from here."""
import os
import re
import json
import hashlib
import time
from pathlib import Path
from typing import Optional
import requests
from dotenv import load_dotenv

_MAX_RETRIES = 3
_BASE_DELAY = 1.0  # seconds


def _request_with_retry(method: str, url: str, **kwargs) -> requests.Response:
    """Wrap requests with exponential backoff on 429 and 5xx responses."""
    last_response = None
    for attempt in range(_MAX_RETRIES + 1):
        r = requests.request(method, url, **kwargs)
        if r.status_code != 429 and r.status_code < 500:
            r.raise_for_status()
            return r
        last_response = r
        if attempt < _MAX_RETRIES:
            delay = (
                float(r.headers.get('Retry-After', _BASE_DELAY * (2 ** attempt)))
                if r.status_code == 429
                else _BASE_DELAY * (2 ** attempt)
            )
            time.sleep(delay)
    last_response.raise_for_status()
    return last_response  # unreachable; satisfies type checker

load_dotenv(Path(__file__).parent.parent / '.env')

NOTION_TOKEN = os.environ.get('NOTION_TOKEN', '')
BASE_URL = 'https://api.notion.com/v1'
HEADERS = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json',
}

_CACHE_DIR = Path(__file__).parent.parent / '.cache' / 'notion'
_CACHE_TTL = 600  # seconds — 10 minutes


def _cache_path(key: str) -> Path:
    return _CACHE_DIR / f"{key}.json"


def _cache_get(key: str) -> Optional[dict]:
    p = _cache_path(key)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
        if time.time() - data['ts'] > _CACHE_TTL:
            p.unlink(missing_ok=True)
            return None
        return data['payload']
    except Exception:
        return None


def _cache_set(key: str, payload) -> None:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _cache_path(key).write_text(json.dumps({'ts': time.time(), 'payload': payload}))


def _cache_bust(key: str) -> None:
    _cache_path(key).unlink(missing_ok=True)

DB_IDS = {
    'ai_daily_hits':        os.environ.get('NOTION_DB_AI_DAILY_HITS', ''),
    'github_trending':      os.environ.get('NOTION_DB_GITHUB_TRENDING', ''),
    'podcast_digest':       os.environ.get('NOTION_DB_PODCAST_DIGEST', ''),
    'course_digest':        os.environ.get('NOTION_DB_COURSE_DIGEST', ''),
    'marketing_projects':   os.environ.get('NOTION_DB_MARKETING_PROJECTS', ''),
    'marketing_assets':     os.environ.get('NOTION_DB_MARKETING_ASSETS', ''),
    'marketing_todos':      os.environ.get('NOTION_DB_MARKETING_TODOS', ''),
}

PAGE_IDS = {
    'marketing_plan_template': os.environ.get('NOTION_PAGE_MARKETING_PLAN_TEMPLATE', ''),
    'ai_command_center':       os.environ.get('NOTION_PAGE_AI_COMMAND_CENTER', ''),
}


def extract_page_id(url: str) -> str:
    """Extract and format a Notion page ID from any Notion URL."""
    clean = url.split('?')[0].split('#')[0]
    # Try dashed UUID format first (already formatted)
    match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', clean)
    if match:
        return match.group(1)
    # Find exactly 32 hex chars bounded by non-hex chars (handles Page-Title-<id> URLs)
    match = re.search(r'(?<![a-f0-9])([a-f0-9]{32})(?![a-f0-9])', clean)
    if match:
        raw = match.group(1)
        return f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"
    raise ValueError(f"Could not extract page ID from URL: {url}")


def get_page(page_id: str) -> dict:
    key = f"page_{page_id}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    r = _request_with_retry('GET', f"{BASE_URL}/pages/{page_id}", headers=HEADERS)
    result = r.json()
    _cache_set(key, result)
    return result


def get_page_blocks(page_id: str) -> list:
    key = f"blocks_{page_id}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    r = _request_with_retry('GET', f"{BASE_URL}/blocks/{page_id}/children", headers=HEADERS)
    result = r.json().get('results', [])
    _cache_set(key, result)
    return result


def query_database(db_id: str, filter_obj: Optional[dict] = None, sorts: Optional[list] = None) -> list:
    body = {}
    if filter_obj:
        body['filter'] = filter_obj
    if sorts:
        body['sorts'] = sorts
    h = hashlib.md5(json.dumps(body, sort_keys=True).encode()).hexdigest()[:8]
    key = f"db_{db_id}_{h}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    r = _request_with_retry('POST', f"{BASE_URL}/databases/{db_id}/query", headers=HEADERS, json=body)
    result = r.json().get('results', [])
    _cache_set(key, result)
    return result


def create_page(parent_db_id: str, properties: dict, children: Optional[list] = None) -> dict:
    body = {'parent': {'database_id': parent_db_id}, 'properties': properties}
    if children:
        body['children'] = children
    r = _request_with_retry('POST', f"{BASE_URL}/pages", headers=HEADERS, json=body)
    # bust all cached queries for this database so subsequent reads see the new page
    for p in _CACHE_DIR.glob(f"db_{parent_db_id}_*.json"):
        p.unlink(missing_ok=True)
    return r.json()


def update_page(page_id: str, properties: dict) -> dict:
    r = _request_with_retry('PATCH', f"{BASE_URL}/pages/{page_id}", headers=HEADERS, json={'properties': properties})
    _cache_bust(f"page_{page_id}")
    return r.json()


def append_blocks(page_id: str, children: list) -> dict:
    r = _request_with_retry('PATCH', f"{BASE_URL}/blocks/{page_id}/children", headers=HEADERS, json={'children': children})
    _cache_bust(f"blocks_{page_id}")
    return r.json()


# ── Property value helpers ────────────────────────────────────────────────────

def extract_text(prop: Optional[dict]) -> str:
    if not prop:
        return ''
    ptype = prop.get('type', '')
    if ptype == 'title':
        return ''.join(t.get('plain_text', '') for t in prop.get('title', []))
    if ptype == 'rich_text':
        return ''.join(t.get('plain_text', '') for t in prop.get('rich_text', []))
    if ptype == 'select':
        sel = prop.get('select')
        return sel.get('name', '') if sel else ''
    if ptype == 'multi_select':
        return ', '.join(o.get('name', '') for o in prop.get('multi_select', []))
    if ptype == 'url':
        return prop.get('url', '') or ''
    if ptype == 'date':
        d = prop.get('date')
        return d.get('start', '') if d else ''
    if ptype == 'checkbox':
        return str(prop.get('checkbox', False))
    return ''


def rich_text(content: str) -> list:
    return [{'type': 'text', 'text': {'content': content}}]


def title_prop(content: str) -> dict:
    return {'title': rich_text(content)}


def rich_text_prop(content: str) -> dict:
    return {'rich_text': rich_text(content)}


def select_prop(name: str) -> dict:
    return {'select': {'name': name}}


def multi_select_prop(names: list) -> dict:
    return {'multi_select': [{'name': n} for n in names]}


def relation_prop(page_ids: list) -> dict:
    return {'relation': [{'id': pid} for pid in page_ids]}


def status_prop(name: str) -> dict:
    return {'status': {'name': name}}


# ── Block helpers ─────────────────────────────────────────────────────────────

def paragraph_block(text: str) -> dict:
    return {'object': 'block', 'type': 'paragraph', 'paragraph': {'rich_text': rich_text(text)}}


def heading_block(text: str, level: int = 2) -> dict:
    h = f'heading_{level}'
    return {'object': 'block', 'type': h, h: {'rich_text': rich_text(text)}}


def divider_block() -> dict:
    return {'object': 'block', 'type': 'divider', 'divider': {}}


def bookmark_block(url: str) -> dict:
    return {'object': 'block', 'type': 'bookmark', 'bookmark': {'url': url}}


def text_to_blocks(text: str) -> list:
    """Split long text into paragraph blocks (Notion limit: 2000 chars per block)."""
    blocks = []
    for i in range(0, len(text), 1900):
        blocks.append(paragraph_block(text[i:i + 1900]))
    return blocks
