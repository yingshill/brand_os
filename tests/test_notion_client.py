"""Tests for notion_client.py — cache logic, property helpers, block helpers, extract_text."""
import json
import time
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import notion_client as nc


# ── extract_page_id ───────────────────────────────────────────────────────────

class TestExtractPageId:
    def test_standard_url(self):
        url = "https://www.notion.so/workspace/My-Page-66c5af5908c5428f82e9d153d9f0ae9e"
        pid = nc.extract_page_id(url)
        assert pid == "66c5af59-08c5-428f-82e9-d153d9f0ae9e"

    def test_url_with_query_params(self):
        url = "https://www.notion.so/66c5af5908c5428f82e9d153d9f0ae9e?v=abc"
        pid = nc.extract_page_id(url)
        assert pid == "66c5af59-08c5-428f-82e9-d153d9f0ae9e"

    def test_already_dashed_id(self):
        url = "https://www.notion.so/66c5af59-08c5-428f-82e9-d153d9f0ae9e"
        pid = nc.extract_page_id(url)
        assert pid == "66c5af59-08c5-428f-82e9-d153d9f0ae9e"

    def test_invalid_url_raises(self):
        with pytest.raises(ValueError):
            nc.extract_page_id("https://www.notion.so/no-id-here")


# ── Cache ─────────────────────────────────────────────────────────────────────

class TestCache:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        self.patcher = patch.object(nc, '_CACHE_DIR', Path(self.tmp))
        self.patcher.start()

    def teardown_method(self):
        self.patcher.stop()

    def test_cache_miss_returns_none(self):
        assert nc._cache_get("nonexistent_key") is None

    def test_cache_write_and_read(self):
        nc._cache_set("mykey", {"hello": "world"})
        result = nc._cache_get("mykey")
        assert result == {"hello": "world"}

    def test_cache_expired_returns_none(self):
        nc._cache_set("expkey", {"data": 1})
        # backdate the timestamp
        p = nc._cache_path("expkey")
        data = json.loads(p.read_text())
        data['ts'] = time.time() - nc._CACHE_TTL - 1
        p.write_text(json.dumps(data))
        assert nc._cache_get("expkey") is None

    def test_cache_bust_removes_file(self):
        nc._cache_set("bustkey", {"x": 1})
        assert nc._cache_get("bustkey") is not None
        nc._cache_bust("bustkey")
        assert nc._cache_get("bustkey") is None

    def test_cache_handles_corrupt_file(self):
        p = nc._cache_path("badkey")
        Path(self.tmp).mkdir(parents=True, exist_ok=True)
        p.write_text("not json")
        assert nc._cache_get("badkey") is None


# ── extract_text ──────────────────────────────────────────────────────────────

class TestExtractText:
    def test_title(self):
        prop = {'type': 'title', 'title': [{'plain_text': 'Hello'}]}
        assert nc.extract_text(prop) == 'Hello'

    def test_rich_text(self):
        prop = {'type': 'rich_text', 'rich_text': [{'plain_text': 'World'}]}
        assert nc.extract_text(prop) == 'World'

    def test_select(self):
        prop = {'type': 'select', 'select': {'name': 'Draft'}}
        assert nc.extract_text(prop) == 'Draft'

    def test_select_none(self):
        prop = {'type': 'select', 'select': None}
        assert nc.extract_text(prop) == ''

    def test_multi_select(self):
        prop = {'type': 'multi_select', 'multi_select': [{'name': 'AI'}, {'name': 'Design'}]}
        assert nc.extract_text(prop) == 'AI, Design'

    def test_url(self):
        prop = {'type': 'url', 'url': 'https://example.com'}
        assert nc.extract_text(prop) == 'https://example.com'

    def test_date(self):
        prop = {'type': 'date', 'date': {'start': '2026-05-09'}}
        assert nc.extract_text(prop) == '2026-05-09'

    def test_checkbox(self):
        prop = {'type': 'checkbox', 'checkbox': True}
        assert nc.extract_text(prop) == 'True'

    def test_none_input(self):
        assert nc.extract_text(None) == ''

    def test_empty_dict(self):
        assert nc.extract_text({}) == ''


# ── Property helpers ──────────────────────────────────────────────────────────

class TestPropertyHelpers:
    def test_title_prop(self):
        result = nc.title_prop("My Title")
        assert result == {'title': [{'type': 'text', 'text': {'content': 'My Title'}}]}

    def test_rich_text_prop(self):
        result = nc.rich_text_prop("Some text")
        assert result == {'rich_text': [{'type': 'text', 'text': {'content': 'Some text'}}]}

    def test_select_prop(self):
        assert nc.select_prop("Draft") == {'select': {'name': 'Draft'}}

    def test_multi_select_prop(self):
        result = nc.multi_select_prop(["AI", "Design"])
        assert result == {'multi_select': [{'name': 'AI'}, {'name': 'Design'}]}

    def test_relation_prop(self):
        result = nc.relation_prop(["id-1", "id-2"])
        assert result == {'relation': [{'id': 'id-1'}, {'id': 'id-2'}]}


# ── Block helpers ─────────────────────────────────────────────────────────────

class TestBlockHelpers:
    def test_paragraph_block(self):
        b = nc.paragraph_block("Hello")
        assert b['type'] == 'paragraph'
        assert b['paragraph']['rich_text'][0]['text']['content'] == 'Hello'

    def test_heading_block_level_2(self):
        b = nc.heading_block("Section", 2)
        assert b['type'] == 'heading_2'
        assert b['heading_2']['rich_text'][0]['text']['content'] == 'Section'

    def test_heading_block_level_3(self):
        b = nc.heading_block("Sub", 3)
        assert b['type'] == 'heading_3'

    def test_divider_block(self):
        assert nc.divider_block() == {'object': 'block', 'type': 'divider', 'divider': {}}

    def test_bookmark_block(self):
        b = nc.bookmark_block("https://example.com")
        assert b['type'] == 'bookmark'
        assert b['bookmark']['url'] == 'https://example.com'

    def test_text_to_blocks_short(self):
        blocks = nc.text_to_blocks("Short text")
        assert len(blocks) == 1
        assert blocks[0]['type'] == 'paragraph'

    def test_text_to_blocks_splits_long(self):
        long_text = "x" * 4000
        blocks = nc.text_to_blocks(long_text)
        assert len(blocks) == 3  # 4000 / 1900 = 3 chunks
        assert all(b['type'] == 'paragraph' for b in blocks)
