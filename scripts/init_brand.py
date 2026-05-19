"""
Scaffold a new brand directory under brands/<name>/ with config and DNA
templates.

Per-brand config.json holds ONLY brand-specific stuff:
- `page_ids.brand_project`: the row in the Projects DB that represents this brand
  (used as the `Project` relation target on every Marketing Project row)
- `db_ids`: optional source DBs unique to this brand

Foundational marketing DBs (Marketing Projects / Asset Library / To-Do) are
global and read from .env — they are NOT per-brand.

Visual identity is owned by DesignLore (separate project) — no STYLE.json here.

Usage:
    python scripts/init_brand.py "<brand_name>" ["Display Name"]

Output: JSON with paths created and a checklist of IDs to fill in.
"""
import sys
import json
import re
from pathlib import Path

BRANDS_DIR = Path(__file__).parent.parent / 'brands'

CONFIG_TEMPLATE = {
    "name": None,
    "notion": {
        "db_ids": {},
        "page_ids": {
            "brand_project": "",
        },
    },
}

DNA_TEMPLATE = """# Brand DNA: {display}

## Voice & Tone
- (Describe how this brand speaks.)

## Target Audience
- (Who is this for?)

## Core Keywords
- (Recurring themes and phrases.)

## Visual Identity
- Visual identity: `DesignLore/{slug}/` (separate repo — single source of truth for logo, palette, type, themes).
- Do not hand-edit visual tokens here.

## Notion Hook
- This brand maps to one row in the Projects DB. Its page ID goes in
  `config.json` → `notion.page_ids.brand_project`. Every Marketing Project for
  this brand will set its `Project` relation to that row.
"""


def slugify(name: str) -> str:
    slug = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
    return slug or 'brand'


def init_brand(name: str, display: str = None) -> dict:
    slug = slugify(name)
    display = display or name
    target = BRANDS_DIR / slug

    if target.exists():
        raise ValueError(f"Brand '{slug}' already exists at {target}")

    target.mkdir(parents=True)

    config = json.loads(json.dumps(CONFIG_TEMPLATE))
    config['name'] = display
    (target / 'config.json').write_text(json.dumps(config, indent=2) + '\n')

    (target / 'DNA.md').write_text(DNA_TEMPLATE.format(display=display, slug=slug))

    return {
        'brand': slug,
        'display_name': display,
        'path': str(target),
        'next_steps': [
            f"Create one row in the Projects DB for '{display}' and paste its page ID into {target / 'config.json'} → notion.page_ids.brand_project",
            f"Write voice and audience guidance in {target / 'DNA.md'}",
            f"Create DesignLore/{slug}/ in the DesignLore repo for visual identity (logo, palette, type, themes) — not in this repo",
            "Run: python scripts/list_brands.py to confirm config health",
        ],
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Usage: python init_brand.py "<brand_name>" ["Display Name"]'}))
        sys.exit(1)
    try:
        name = sys.argv[1]
        display = sys.argv[2] if len(sys.argv) > 2 else None
        print(json.dumps(init_brand(name, display), indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({'error': str(e)}))
        sys.exit(1)
