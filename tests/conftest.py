"""
Shared test fixtures for ATS Dashboard test suite.
"""

import os
import sys
import sqlite3
import tempfile
import pytest
from unittest.mock import patch
from contextlib import contextmanager

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.data_service import DataService
from config.constants import CATEGORIES, STATUSES


@pytest.fixture(scope="session")
def app_module():
    """Import the redesigned app module."""
    import app as app
    return app


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    # Use in-memory database
    conn = sqlite3.connect(":memory:")
    
    # Create the tables
    conn.execute('''
        CREATE TABLE applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            job_title TEXT NOT NULL,
            application_url TEXT,
            date_applied TEXT NOT NULL,
            category TEXT,
            status TEXT NOT NULL,
            notes TEXT,
            last_updated TEXT
        )
    ''')
    
    conn.execute('''
        CREATE TABLE status_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY(application_id) REFERENCES applications(id)
        )
    ''')
    
    conn.commit()
    yield conn
    conn.close()


@pytest.fixture
def data_service(in_memory_db):
    """Create a DataService instance with in-memory database."""
    service = DataService()
    # Mock the database manager's get_connection method to use our in-memory database
    with patch.object(service.db, 'get_connection', return_value=in_memory_db):
        # Also need to set the db_path to avoid file creation
        service.db.db_path = ":memory:"
        yield service


@pytest.fixture
def sample_application_data():
    """Provide sample application data for testing."""
    return {
        'company_name': 'Test Corporation',
        'job_title': 'Software Engineer',
        'application_url': 'https://test-corp.com/careers',
        'date_applied': '2024-01-15',
        'category': 'SWE',
        'status': 'Applied',
        'notes': 'Test application entry'
    }


@pytest.fixture
def multiple_application_data():
    """Provide multiple application data entries for testing."""
    return [
        {
            'company_name': 'Tech Corp A',
            'job_title': 'Frontend Engineer',
            'application_url': 'https://techcorpa.com/jobs',
            'date_applied': '2024-01-10',
            'category': 'SWE',
            'status': 'Applied',
            'notes': 'Frontend role'
        },
        {
            'company_name': 'Data Inc B',
            'job_title': 'Data Scientist',
            'application_url': 'https://datainc.com/careers',
            'date_applied': '2024-01-12',
            'category': 'DS',
            'status': 'Online Assessment',
            'notes': 'Data science position'
        },
        {
            'company_name': 'ML Company C',
            'job_title': 'Machine Learning Engineer',
            'application_url': 'https://mlcompany.com/jobs',
            'date_applied': '2024-01-14',
            'category': 'MLE',
            'status': 'Interviewing: 1st round',
            'notes': 'ML engineering role'
        },
        {
            'company_name': 'Finance Corp D',
            'job_title': 'Quantitative Analyst',
            'application_url': 'https://financecorp.com/careers',
            'date_applied': '2024-01-16',
            'category': 'Quant Analyst',
            'status': 'Rejected',
            'notes': 'Quant position'
        },
        {
            'company_name': 'Startup E',
            'job_title': 'Full Stack Developer',
            'application_url': 'https://startup-e.com/jobs',
            'date_applied': '2024-01-18',
            'category': 'SWE',
            'status': 'Offer',
            'notes': 'Full stack role at startup'
        }
    ]


@pytest.fixture
def populated_data_service(data_service, multiple_application_data):
    """Data service populated with test data."""
    for app_data in multiple_application_data:
        data_service.add_application(app_data)
    return data_service


@pytest.fixture
def temp_db_file():
    """Create a temporary database file for integration tests."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@contextmanager
def mock_database_path(db_path):
    """Context manager to mock database path in environment."""
    with patch.dict(os.environ, {'ATS_DB_PATH': db_path}):
        yield


@pytest.fixture
def mock_dash_app():
    """Mock Dash app for callback testing."""
    from dash import Dash
    app = Dash(__name__)
    return app


# Pytest markers for organizing tests
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "database: Database tests")
    config.addinivalue_line("markers", "callbacks: Callback tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "requires_browser: Tests requiring browser")


# Pytest collection hooks
def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Mark tests based on directory structure
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
            item.add_marker(pytest.mark.requires_browser)
        elif "database" in str(item.fspath):
            item.add_marker(pytest.mark.database)
        elif "callbacks" in str(item.fspath):
            item.add_marker(pytest.mark.callbacks)
        
        # Mark slow tests
        if any(keyword in item.name.lower() for keyword in ['performance', 'load', 'stress', 'large']):
            item.add_marker(pytest.mark.slow) 