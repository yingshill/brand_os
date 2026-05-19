"""
List every brand under brands/ and report config health.

Foundational marketing DBs (Marketing Projects / Asset Library / To-Do) are
global — sourced from .env — so they are checked once, not per-brand.

Per-brand checks:
- DNA.md exists
- `page_ids.brand_project` is set (the row in the Projects DB representing
  this brand; used as the `Project` relation target on every Marketing Project
  row written for this brand)

Visual identity is owned by DesignLore (separate project) — not validated here.

Usage:
    python scripts/list_brands.py [--brand <name>]

Exit code: 0 if global foundationals are set AND every brand is healthy; 1 otherwise.
"""
import sys
import json
import os
import argparse
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from notion_client import list_brands, load_brand_config, FOUNDATIONAL_DB_KEYS

FOUNDATIONAL_ENV_VARS = [
    'NOTION_DB_MARKETING_PROJECTS',
    'NOTION_DB_MARKETING_ASSETS',
    'NOTION_DB_MARKETING_TODOS',
]
BRANDS_DIR = Path(__file__).parent.parent / 'brands'


def inspect_global() -> dict:
    missing = [v for v in FOUNDATIONAL_ENV_VARS if not os.environ.get(v)]
    return {
        'foundational_env_vars_set': not missing,
        'missing_env_vars': missing,
    }


def inspect_brand(name: str) -> dict:
    brand_dir = BRANDS_DIR / name
    config = load_brand_config(name)
    db_ids = config.get('db_ids', {})
    page_ids = config.get('page_ids', {})

    has_dna = (brand_dir / 'DNA.md').exists()
    has_brand_project = bool(page_ids.get('brand_project'))
    source_dbs = [k for k in db_ids if k not in FOUNDATIONAL_DB_KEYS and db_ids.get(k)]

    return {
        'brand': name,
        'has_config': (brand_dir / 'config.json').exists(),
        'has_dna': has_dna,
        'brand_project_set': has_brand_project,
        'configured_source_db_ids': source_dbs,
        'healthy': has_dna and has_brand_project,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--brand', default=None,
                        help='Inspect a single brand (default: all)')
    args = parser.parse_args()

    targets = [args.brand] if args.brand else list_brands()
    global_report = inspect_global()
    brand_reports = [inspect_brand(b) for b in targets]
    report = {'global': global_report, 'brands': brand_reports}
    print(json.dumps(report, indent=2, ensure_ascii=False))

    ok = global_report['foundational_env_vars_set'] and all(r['healthy'] for r in brand_reports)
    sys.exit(0 if ok else 1)
