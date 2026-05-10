"""Tests for create_todo.py — single and batch todo creation, optional fields."""
import pytest
from unittest.mock import patch
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import create_todo as ct


MOCK_PAGE = {'id': 'todo-id-001', 'url': 'https://notion.so/todo-001'}


class TestCreateTodo:
    @patch('create_todo.create_page', return_value=MOCK_PAGE)
    @patch('create_todo.DB_IDS', {'marketing_todos': 'real-db-id'})
    def test_returns_expected_fields(self, mock_create):
        result = ct.create_todo({'task': 'Review — Test Post', 'priority': '🔥 High'})
        assert result['task_id'] == 'todo-id-001'
        assert result['task'] == 'Review — Test Post'
        assert result['priority'] == '🔥 High'

    @patch('create_todo.create_page', return_value=MOCK_PAGE)
    @patch('create_todo.DB_IDS', {'marketing_todos': 'real-db-id'})
    def test_default_priority_is_high(self, mock_create):
        result = ct.create_todo({'task': 'Review — Test'})
        assert result['priority'] == '🔥 High'

    @patch('create_todo.create_page', return_value=MOCK_PAGE)
    @patch('create_todo.DB_IDS', {'marketing_todos': 'real-db-id'})
    def test_channel_added_when_provided(self, mock_create):
        ct.create_todo({'task': 'Review', 'channel': 'LinkedIn'})
        props = mock_create.call_args[0][1]
        assert props['Channel'] == {'select': {'name': 'LinkedIn'}}

    @patch('create_todo.create_page', return_value=MOCK_PAGE)
    @patch('create_todo.DB_IDS', {'marketing_todos': 'real-db-id'})
    def test_channel_omitted_when_not_provided(self, mock_create):
        ct.create_todo({'task': 'Review'})
        props = mock_create.call_args[0][1]
        assert 'Channel' not in props

    @patch('create_todo.create_page', return_value=MOCK_PAGE)
    @patch('create_todo.DB_IDS', {'marketing_todos': 'real-db-id'})
    def test_asset_id_added_as_relation(self, mock_create):
        ct.create_todo({'task': 'Review', 'asset_id': 'asset-123'})
        props = mock_create.call_args[0][1]
        assert props['Linked Asset'] == {'relation': [{'id': 'asset-123'}]}

    @patch('create_todo.create_page', return_value=MOCK_PAGE)
    @patch('create_todo.DB_IDS', {'marketing_todos': 'real-db-id'})
    def test_status_always_not_started(self, mock_create):
        ct.create_todo({'task': 'Review'})
        props = mock_create.call_args[0][1]
        assert props['Status'] == {'status': {'name': 'Not Started'}}

    @patch('create_todo.DB_IDS', {'marketing_todos': ''})
    def test_raises_when_db_id_missing(self):
        with pytest.raises(ValueError, match="NOTION_DB_MARKETING_TODOS"):
            ct.create_todo({'task': 'Review'})


class TestCreateTodoBatch:
    @patch('create_todo.create_page', return_value=MOCK_PAGE)
    @patch('create_todo.DB_IDS', {'marketing_todos': 'real-db-id'})
    def test_batch_returns_list(self, mock_create):
        items = [
            {'task': 'Review — Post A', 'priority': '🔥 High'},
            {'task': 'Design — Carousel B', 'priority': '🟡 Medium'},
            {'task': 'Publish — Post A', 'priority': '🔥 High'},
        ]
        results = [ct.create_todo(item) for item in items]
        assert len(results) == 3
        assert mock_create.call_count == 3
