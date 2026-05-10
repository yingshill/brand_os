"""Tests for fetch_entry.py — field extraction, source DB identification."""
import pytest
from unittest.mock import patch
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import fetch_entry as fe


MOCK_PAGE = {
    'id': '66c5af59-08c5-428f-82e9-d153d9f0ae9e',
    'url': 'https://www.notion.so/66c5af5908c5428f82e9d153d9f0ae9e',
    'parent': {'type': 'database_id', 'database_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'},
    'properties': {
        'Name': {'type': 'title', 'title': [{'plain_text': 'MCP is the new API'}]},
        'Core Insight': {'type': 'rich_text', 'rich_text': [{'plain_text': 'MCP standardises tool calling'}]},
        'Why It Matters': {'type': 'rich_text', 'rich_text': [{'plain_text': 'Interoperability across agents'}]},
        'URL': {'type': 'url', 'url': 'https://example.com/source'},
        'Status': {'type': 'select', 'select': {'name': 'New'}},
        'Output': {'type': 'select', 'select': None},
    }
}


class TestFirst:
    def test_returns_first_matching_key(self):
        props = {'Name': {'type': 'title', 'title': [{'plain_text': 'Hello'}]}}
        assert fe._first(props, ['Title', 'Name']) == 'Hello'

    def test_skips_missing_keys(self):
        props = {'Name': {'type': 'title', 'title': [{'plain_text': 'Hello'}]}}
        assert fe._first(props, ['Missing', 'Name']) == 'Hello'

    def test_returns_empty_when_no_match(self):
        assert fe._first({}, ['Title', 'Name']) == ''


class TestIdentifySourceDb:
    def test_known_db_matched(self):
        page = {'parent': {'database_id': 'aaaa-aaaa'}}
        with patch.dict('notion_client.DB_IDS', {'ai_daily_hits': 'aaaa-aaaa'}):
            result = fe.identify_source_db(page)
        assert result == 'ai_daily_hits'

    def test_unknown_db_returns_unknown(self):
        page = {'parent': {'database_id': 'zzzzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzzz'}}
        result = fe.identify_source_db(page)
        assert result == 'unknown'

    def test_ignores_dashes_in_comparison(self):
        page = {'parent': {'database_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'}}
        with patch.dict('notion_client.DB_IDS', {'ai_daily_hits': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'.replace('a', 'a')}):
            with patch.dict('notion_client.DB_IDS', {'ai_daily_hits': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'[:32]}):
                result = fe.identify_source_db(page)
        assert result in ('ai_daily_hits', 'unknown')


class TestFetchEntry:
    @patch('fetch_entry.get_page', return_value=MOCK_PAGE)
    @patch('fetch_entry.extract_page_id', return_value='66c5af59-08c5-428f-82e9-d153d9f0ae9e')
    def test_returns_expected_fields(self, mock_pid, mock_page):
        result = fe.fetch_entry('https://www.notion.so/66c5af5908c5428f82e9d153d9f0ae9e')
        assert result['title'] == 'MCP is the new API'
        assert result['core_insight'] == 'MCP standardises tool calling'
        assert result['why_it_matters'] == 'Interoperability across agents'
        assert result['source_url'] == 'https://example.com/source'
        assert result['status'] == 'New'
        assert result['output'] == ''
        assert 'Name' in result['all_properties']

    @patch('fetch_entry.get_page', return_value=MOCK_PAGE)
    @patch('fetch_entry.extract_page_id', return_value='66c5af59-08c5-428f-82e9-d153d9f0ae9e')
    def test_page_id_returned(self, mock_pid, mock_page):
        result = fe.fetch_entry('https://www.notion.so/66c5af5908c5428f82e9d153d9f0ae9e')
        assert result['page_id'] == '66c5af59-08c5-428f-82e9-d153d9f0ae9e'
