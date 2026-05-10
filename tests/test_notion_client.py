"""Tests for notion_client.py — cache logic, retry logic, property helpers, block helpers, extract_text."""
import json
import time
import tempfile
import pytest
import requests
from pathlib import Path
from unittest.mock import patch, MagicMock, call
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import notion_client as nc


# ── Retry logic ──────────────────────────────────────────────────────────────

def _make_response(status_code, headers=None, json_data=None):
    r = MagicMock()
    r.status_code = status_code
    r.headers = headers or {}
    r.json.return_value = json_data or {}
    if status_code >= 400:
        r.raise_for_status.side_effect = requests.HTTPError(response=r)
    else:
        r.raise_for_status.return_value = None
    return r


class TestRetryLogic:
    @patch('notion_client.time.sleep')
    @patch('notion_client.requests.request')
    def test_success_on_first_attempt(self, mock_req, mock_sleep):
        mock_req.return_value = _make_response(200)
        result = nc._request_with_retry('GET', 'https://example.com')
        assert result.status_code == 200
        mock_sleep.assert_not_called()

    @patch('notion_client.time.sleep')
    @patch('notion_client.requests.request')
    def test_retries_on_429_then_succeeds(self, mock_req, mock_sleep):
        mock_req.side_effect = [_make_response(429), _make_response(429), _make_response(200)]
        result = nc._request_with_retry('GET', 'https://example.com')
        assert result.status_code == 200
        assert mock_req.call_count == 3
        assert mock_sleep.call_count == 2

    @patch('notion_client.time.sleep')
    @patch('notion_client.requests.request')
    def test_raises_after_max_retries_on_429(self, mock_req, mock_sleep):
        mock_req.side_effect = [_make_response(429)] * (nc._MAX_RETRIES + 1)
        with pytest.raises(requests.HTTPError):
            nc._request_with_retry('GET', 'https://example.com')
        assert mock_req.call_count == nc._MAX_RETRIES + 1
        assert mock_sleep.call_count == nc._MAX_RETRIES

    @patch('notion_client.time.sleep')
    @patch('notion_client.requests.request')
    def test_retries_on_500_then_succeeds(self, mock_req, mock_sleep):
        mock_req.side_effect = [_make_response(500), _make_response(200)]
        result = nc._request_with_retry('GET', 'https://example.com')
        assert result.status_code == 200
        assert mock_req.call_count == 2
        mock_sleep.assert_called_once()

    @patch('notion_client.time.sleep')
    @patch('notion_client.requests.request')
    def test_no_retry_on_400(self, mock_req, mock_sleep):
        mock_req.return_value = _make_response(400)
        with pytest.raises(requests.HTTPError):
            nc._request_with_retry('GET', 'https://example.com')
        assert mock_req.call_count == 1
        mock_sleep.assert_not_called()

    @patch('notion_client.time.sleep')
    @patch('notion_client.requests.request')
    def test_uses_retry_after_header(self, mock_req, mock_sleep):
        mock_req.side_effect = [
            _make_response(429, headers={'Retry-After': '7'}),
            _make_response(200),
        ]
        nc._request_with_retry('GET', 'https://example.com')
        mock_sleep.assert_called_once_with(7.0)

    @patch('notion_client.time.sleep')
    @patch('notion_client.requests.request')
    def test_exponential_backoff_on_500(self, mock_req, mock_sleep):
        mock_req.side_effect = [
            _make_response(500),
            _make_response(500),
            _make_response(200),
        ]
        nc._request_with_retry('GET', 'https://example.com')
        assert mock_sleep.call_args_list == [call(nc._BASE_DELAY * 1), call(nc._BASE_DELAY * 2)]


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


# ── query_database pagination ────────────────────────────────────────────────

class TestQueryDatabasePagination:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        self.patcher = patch.object(nc, '_CACHE_DIR', Path(self.tmp))
        self.patcher.start()

    def teardown_method(self):
        self.patcher.stop()

    def _mock_response(self, results, has_more=False, next_cursor=None):
        r = MagicMock()
        r.status_code = 200
        r.raise_for_status.return_value = None
        r.json.return_value = {'results': results, 'has_more': has_more, 'next_cursor': next_cursor}
        return r

    @patch('notion_client._request_with_retry')
    def test_single_page_returns_all_results(self, mock_req):
        mock_req.return_value = self._mock_response([{'id': 'a'}, {'id': 'b'}])
        result = nc.query_database('db-id')
        assert result == [{'id': 'a'}, {'id': 'b'}]
        assert mock_req.call_count == 1

    @patch('notion_client._request_with_retry')
    def test_follows_pagination_cursor(self, mock_req):
        mock_req.side_effect = [
            self._mock_response([{'id': 'a'}, {'id': 'b'}], has_more=True, next_cursor='cursor-1'),
            self._mock_response([{'id': 'c'}], has_more=False),
        ]
        result = nc.query_database('db-id')
        assert result == [{'id': 'a'}, {'id': 'b'}, {'id': 'c'}]
        assert mock_req.call_count == 2
        # second call must include start_cursor
        second_call_body = mock_req.call_args_list[1][1]['json']
        assert second_call_body['start_cursor'] == 'cursor-1'

    @patch('notion_client._request_with_retry')
    def test_accumulates_three_pages(self, mock_req):
        mock_req.side_effect = [
            self._mock_response([{'id': str(i)} for i in range(100)], has_more=True, next_cursor='cur-1'),
            self._mock_response([{'id': str(i)} for i in range(100, 200)], has_more=True, next_cursor='cur-2'),
            self._mock_response([{'id': str(i)} for i in range(200, 250)], has_more=False),
        ]
        result = nc.query_database('db-id')
        assert len(result) == 250
        assert mock_req.call_count == 3

    @patch('notion_client._request_with_retry')
    def test_cache_hit_skips_api(self, mock_req):
        mock_req.return_value = self._mock_response([{'id': 'x'}])
        nc.query_database('db-id')
        nc.query_database('db-id')
        assert mock_req.call_count == 1  # second call served from cache


# ── update_page cache busting ─────────────────────────────────────────────────

class TestUpdatePageCacheBusting:
    def setup_method(self):
        self.tmp = tempfile.mkdtemp()
        self.patcher = patch.object(nc, '_CACHE_DIR', Path(self.tmp))
        self.patcher.start()

    def teardown_method(self):
        self.patcher.stop()

    @patch('notion_client._request_with_retry')
    def test_busts_page_cache_only_when_no_parent_db(self, mock_req):
        mock_req.return_value = MagicMock(status_code=200, json=lambda: {})
        nc._cache_set('page_abc', {'data': 1})
        nc.update_page('abc', {})
        assert nc._cache_get('page_abc') is None

    @patch('notion_client._request_with_retry')
    def test_busts_db_cache_when_parent_db_id_provided(self, mock_req):
        mock_req.return_value = MagicMock(status_code=200, json=lambda: {})
        db_id = 'db123456789012345678901234567890'
        nc._cache_set(f'db_{db_id}_abcd1234', {'results': []})
        nc._cache_set(f'db_{db_id}_efgh5678', {'results': []})
        nc._cache_set('page_abc', {'data': 1})
        nc.update_page('abc', {}, parent_db_id=db_id)
        assert nc._cache_get(f'db_{db_id}_abcd1234') is None
        assert nc._cache_get(f'db_{db_id}_efgh5678') is None
        assert nc._cache_get('page_abc') is None

    @patch('notion_client._request_with_retry')
    def test_does_not_bust_other_db_caches(self, mock_req):
        mock_req.return_value = MagicMock(status_code=200, json=lambda: {})
        other_db = 'other0000000000000000000000000000'
        nc._cache_set(f'db_{other_db}_abcd1234', {'results': []})
        nc.update_page('abc', {}, parent_db_id='db123456789012345678901234567890')
        assert nc._cache_get(f'db_{other_db}_abcd1234') is not None


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
