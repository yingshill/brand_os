"""Tests for update_entry_status.py — status update, parent DB ID extraction."""
import pytest
from unittest.mock import patch, MagicMock
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import update_entry_status as ues

MOCK_PAGE_WITH_PARENT = {
    'id': 'page-abc',
    'parent': {'type': 'database_id', 'database_id': 'aaaaaaaa-bbbb-cccc-dddd-eeeeffff0000'},
}

MOCK_PAGE_NO_PARENT = {
    'id': 'page-abc',
    'parent': {'type': 'workspace'},
}


class TestUpdateEntryStatus:
    @patch('update_entry_status.update_page')
    @patch('update_entry_status.get_page', return_value=MOCK_PAGE_WITH_PARENT)
    def test_calls_update_page_with_correct_status(self, mock_get, mock_update):
        mock_update.return_value = {}
        ues.update_entry_status('page-abc', 'In Progress')
        mock_update.assert_called_once()
        _, props, *_ = mock_update.call_args[0]
        assert props == {'Status': {'select': {'name': 'In Progress'}}}

    @patch('update_entry_status.update_page')
    @patch('update_entry_status.get_page', return_value=MOCK_PAGE_WITH_PARENT)
    def test_passes_parent_db_id(self, mock_get, mock_update):
        mock_update.return_value = {}
        ues.update_entry_status('page-abc', 'In Progress')
        kwargs = mock_update.call_args[1]
        # dashes stripped from database_id
        assert kwargs.get('parent_db_id') == 'aaaaaaaabbbbccccddddeeeeffff0000'

    @patch('update_entry_status.update_page')
    @patch('update_entry_status.get_page', return_value=MOCK_PAGE_NO_PARENT)
    def test_passes_none_when_no_parent_db(self, mock_get, mock_update):
        mock_update.return_value = {}
        ues.update_entry_status('page-abc', 'Done')
        kwargs = mock_update.call_args[1]
        assert kwargs.get('parent_db_id') is None

    @patch('update_entry_status.update_page')
    @patch('update_entry_status.get_page', return_value=MOCK_PAGE_WITH_PARENT)
    def test_returns_updated_true(self, mock_get, mock_update):
        mock_update.return_value = {}
        result = ues.update_entry_status('page-abc', 'In Progress')
        assert result == {'updated': True, 'page_id': 'page-abc', 'status': 'In Progress'}
