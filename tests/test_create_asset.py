"""Tests for create_asset.py — property building, content truncation, block construction."""
import pytest
from unittest.mock import patch, call
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import create_asset as ca


MOCK_CREATED_PAGE = {'id': 'asset-id-001', 'url': 'https://notion.so/asset-001'}


class TestCreateAsset:
    BASE_DATA = {
        'asset_name': 'Test Post',
        'type': 'Post',
        'channel': 'LinkedIn',
        'hook': 'This is the hook',
        'content': 'This is the content body.',
        'topic': ['AI', 'Workflow'],
    }

    @patch('create_asset.create_page', return_value=MOCK_CREATED_PAGE)
    @patch('create_asset.DB_IDS', {'marketing_assets': 'real-db-id'})
    def test_returns_expected_fields(self, mock_create):
        result = ca.create_asset(self.BASE_DATA)
        assert result['asset_id'] == 'asset-id-001'
        assert result['asset_name'] == 'Test Post'
        assert result['channel'] == 'LinkedIn'
        assert result['type'] == 'Post'

    @patch('create_asset.create_page', return_value=MOCK_CREATED_PAGE)
    @patch('create_asset.DB_IDS', {'marketing_assets': 'real-db-id'})
    def test_topic_as_string_wrapped_in_list(self, mock_create):
        data = {**self.BASE_DATA, 'topic': 'AI'}
        ca.create_asset(data)
        props = mock_create.call_args[0][1]
        assert props['Topic'] == {'multi_select': [{'name': 'AI'}]}

    @patch('create_asset.create_page', return_value=MOCK_CREATED_PAGE)
    @patch('create_asset.DB_IDS', {'marketing_assets': 'real-db-id'})
    def test_content_truncated_at_1900_chars(self, mock_create):
        data = {**self.BASE_DATA, 'content': 'x' * 2000}
        ca.create_asset(data)
        props = mock_create.call_args[0][1]
        content_val = props['Content']['rich_text'][0]['text']['content']
        assert len(content_val) == 1900

    @patch('create_asset.create_page', return_value=MOCK_CREATED_PAGE)
    @patch('create_asset.DB_IDS', {'marketing_assets': 'real-db-id'})
    def test_project_id_added_as_relation(self, mock_create):
        data = {**self.BASE_DATA, 'project_id': 'proj-123'}
        ca.create_asset(data)
        props = mock_create.call_args[0][1]
        assert props['Project'] == {'relation': [{'id': 'proj-123'}]}

    @patch('create_asset.create_page', return_value=MOCK_CREATED_PAGE)
    @patch('create_asset.DB_IDS', {'marketing_assets': 'real-db-id'})
    def test_no_children_when_no_content(self, mock_create):
        data = {'asset_name': 'Empty', 'type': 'Post', 'channel': 'LinkedIn'}
        ca.create_asset(data)
        children = mock_create.call_args[0][2]
        assert children is None

    @patch('create_asset.create_page', return_value=MOCK_CREATED_PAGE)
    @patch('create_asset.DB_IDS', {'marketing_assets': 'real-db-id'})
    def test_carousel_brief_adds_children(self, mock_create):
        data = {**self.BASE_DATA, 'carousel_brief': 'Design brief here'}
        ca.create_asset(data)
        children = mock_create.call_args[0][2]
        assert children is not None
        types = [b['type'] for b in children]
        assert 'heading_2' in types
        assert 'bookmark' in types

    @patch('create_asset.create_page', return_value=MOCK_CREATED_PAGE)
    @patch('create_asset.DB_IDS', {'marketing_assets': 'real-db-id'})
    def test_slides_added_as_heading3_blocks(self, mock_create):
        data = {**self.BASE_DATA, 'slides': [
            {'title': 'Slide 1 — Hook', 'content': 'Hook text'},
            {'title': 'Slide 2 — Body', 'content': 'Body text'},
        ]}
        ca.create_asset(data)
        children = mock_create.call_args[0][2]
        assert children is not None
        h3_blocks = [b for b in children if b['type'] == 'heading_3']
        assert len(h3_blocks) == 2

    @patch('create_asset.DB_IDS', {'marketing_assets': ''})
    def test_raises_when_db_id_missing(self):
        with pytest.raises(ValueError, match="NOTION_DB_MARKETING_ASSETS"):
            ca.create_asset(self.BASE_DATA)
