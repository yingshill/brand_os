"""Tests for create_project.py — fuzzy title matching, find-or-create logic."""
import pytest
from unittest.mock import patch, MagicMock
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import create_project as cp


MOCK_PAGE = {
    'id': 'proj-id-001',
    'url': 'https://www.notion.so/proj-id-001',
    'properties': {
        'Name': {'type': 'title', 'title': [{'plain_text': 'MCP is the new API'}]},
    }
}


class TestFindExistingProject:
    @patch('create_project.DB_IDS', {'marketing_projects': ''})
    def test_returns_none_when_db_id_missing(self):
        result = cp.find_existing_project("anything")
        assert result is None

    @patch('create_project.query_database', return_value=[MOCK_PAGE])
    @patch('create_project.DB_IDS', {'marketing_projects': 'real-db-id'})
    def test_finds_exact_title_match(self, mock_db):
        result = cp.find_existing_project("MCP is the new API")
        assert result['id'] == 'proj-id-001'

    @patch('create_project.query_database', return_value=[MOCK_PAGE])
    @patch('create_project.DB_IDS', {'marketing_projects': 'real-db-id'})
    def test_finds_partial_title_match(self, mock_db):
        result = cp.find_existing_project("MCP is the new")
        assert result['id'] == 'proj-id-001'

    @patch('create_project.query_database', return_value=[MOCK_PAGE])
    @patch('create_project.DB_IDS', {'marketing_projects': 'real-db-id'})
    def test_returns_none_when_no_match(self, mock_db):
        result = cp.find_existing_project("Completely different title")
        assert result is None


class TestCreateProject:
    @patch('create_project.find_existing_project', return_value=MOCK_PAGE)
    def test_returns_linked_when_project_exists(self, mock_find):
        result = cp.create_project({'title': 'MCP is the new API', 'positioning': 'p'})
        assert result['action'] == 'linked'
        assert result['project_id'] == 'proj-id-001'

    @patch('create_project.find_existing_project', return_value=None)
    @patch('create_project.create_page', return_value={'id': 'new-proj-id', 'url': 'https://notion.so/new'})
    @patch('create_project.DB_IDS', {'marketing_projects': 'real-db-id'})
    def test_creates_new_when_not_found(self, mock_create, mock_find):
        result = cp.create_project({'title': 'New Project', 'positioning': 'A new positioning'})
        assert result['action'] == 'created'
        assert result['project_id'] == 'new-proj-id'
        assert result['title'] == 'New Project'

    @patch('create_project.DB_IDS', {'marketing_projects': ''})
    def test_raises_when_db_id_missing(self):
        with pytest.raises(ValueError, match="NOTION_DB_MARKETING_PROJECTS"):
            cp.create_project({'title': 'x', 'positioning': 'y'})
