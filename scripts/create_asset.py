"""
Create an asset row in the Marketing Asset Library.

Usage:
    python scripts/create_asset.py '<json>'

JSON input:
    {
      "asset_name": "...",
      "type": "Post | Carousel | Thread | Article | Case Study | Video",
      "channel": "LinkedIn | XHS | X | General | Substack | YouTube",
      "hook": "one-liner hook",
      "content": "full draft text",
      "topic": ["Workflow", "AI Design"],
      "project_id": "optional project page ID",
      "carousel_brief": "optional design brief text",
      "slides": [{"title": "Slide 1 — Hook", "content": "..."}]
    }

Output: JSON with asset_id, asset_url, asset_name.
"""
import sys
import json
import os
sys.path.insert(0, os.path.dirname(__file__))
from notion_client import (
    create_page, DB_IDS,
    title_prop, rich_text_prop, select_prop, multi_select_prop, relation_prop, status_prop,
    heading_block, paragraph_block, divider_block, bookmark_block, text_to_blocks,
)

CARD_CANVAS_URL = 'https://www.cardcanvas.app/'


def create_asset(data: dict) -> dict:
    db_id = DB_IDS['marketing_assets']
    if not db_id:
        raise ValueError("NOTION_DB_MARKETING_ASSETS is not set in .env")

    properties = {
        'Asset Name': title_prop(data['asset_name']),
        'Type': select_prop(data.get('type', 'Post')),
        'Channel': select_prop(data.get('channel', 'LinkedIn')),
        'Status': status_prop('Draft'),
    }

    if data.get('hook'):
        properties['Hook / Angle'] = rich_text_prop(data['hook'])

    content = data.get('content', '')
    if content:
        # Notion rich_text property limit: 2000 chars — truncate with note if needed
        if len(content) > 1900:
            properties['Content'] = rich_text_prop(content[:1900])
        else:
            properties['Content'] = rich_text_prop(content)

    if data.get('topic'):
        topics = data['topic'] if isinstance(data['topic'], list) else [data['topic']]
        properties['Topic'] = multi_select_prop(topics)

    if data.get('project_id'):
        properties['Project'] = relation_prop([data['project_id']])

    # Build page body blocks
    children = []

    if content:
        children.append(heading_block('Content', 2))
        children.extend(text_to_blocks(content))
        children.append(divider_block())

    if data.get('carousel_brief'):
        children.append(heading_block('Carousel Design Brief', 2))
        children.extend(text_to_blocks(data['carousel_brief']))
        children.append(paragraph_block('Design tool:'))
        children.append(bookmark_block(CARD_CANVAS_URL))
        children.append(divider_block())

    if data.get('slides'):
        children.append(heading_block('Slide Deck', 2))
        for slide in data['slides']:
            children.append(heading_block(slide.get('title', ''), 3))
            children.extend(text_to_blocks(slide.get('content', '')))

    page = create_page(db_id, properties, children if children else None)

    return {
        'asset_id': page['id'],
        'asset_url': page.get('url', ''),
        'asset_name': data['asset_name'],
        'channel': data.get('channel', ''),
        'type': data.get('type', 'Post'),
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Provide JSON as argument'}))
        sys.exit(1)
    try:
        data = json.loads(sys.argv[1])
        result = create_asset(data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({'error': str(e)}))
        sys.exit(1)
