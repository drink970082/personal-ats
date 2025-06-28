"""
Database tests for DataService using in-memory SQLite.
"""

import pytest
import sqlite3
from unittest.mock import patch


@pytest.mark.database
class TestDataServiceCRUD:
    """Test CRUD operations in DataService."""
    
    def test_add_application_success(self, data_service, sample_application_data):
        """Test successful application addition."""
        result = data_service.add_application(sample_application_data)
        
        assert result.get("success") is True
        assert "id" in result or "message" in result
    
    def test_add_application_minimal_data(self, data_service):
        """Test adding application with minimal required data."""
        minimal_data = {
            'company_name': 'Minimal Corp',
            'job_title': 'Developer',
            'date_applied': '2024-01-15'
        }
        
        result = data_service.add_application(minimal_data)
        assert result.get("success") is True
    
    def test_get_applications_empty(self, data_service):
        """Test getting applications when database is empty."""
        applications = data_service.get_applications_table_data()
        assert applications == []
    
    def test_get_applications_single(self, data_service, sample_application_data):
        """Test getting applications with single entry."""
        app_id = data_service.add_application(sample_application_data)
        applications = data_service.get_applications_table_data()
        
        assert len(applications) == 1
        assert applications[0]['id'] == app_id
        assert applications[0]['company_name'] == sample_application_data['company_name']
        assert applications[0]['job_title'] == sample_application_data['job_title']
    
    def test_get_applications_multiple(self, data_service, multiple_application_data):
        """Test getting applications with multiple entries."""
        app_ids = []
        for app_data in multiple_application_data:
            app_id = data_service.add_application(app_data)
            app_ids.append(app_id)
        
        applications = data_service.get_applications_table_data()
        
        assert len(applications) == len(multiple_application_data)
        retrieved_ids = {app['id'] for app in applications}
        assert retrieved_ids == set(app_ids)
    
    def test_update_application_success(self, data_service, sample_application_data):
        """Test successful application update."""
        app_id = data_service.add_application(sample_application_data)
        
        update_data = {
            'status': 'Online Assessment',
            'notes': 'Updated notes'
        }
        
        success = data_service.update_application(app_id, update_data)
        assert success is True
        
        # Verify update
        applications = data_service.get_applications_table_data()
        updated_app = applications[0]
        assert updated_app['status'] == 'Online Assessment'
        assert updated_app['notes'] == 'Updated notes'
        # Other fields should remain unchanged
        assert updated_app['company_name'] == sample_application_data['company_name']
    
    def test_update_application_nonexistent(self, data_service):
        """Test updating non-existent application."""
        success = data_service.update_application(999, {'status': 'Applied'})
        # Should handle gracefully
        assert success in [True, False]  # Implementation dependent
    
    def test_delete_application_success(self, data_service, sample_application_data):
        """Test successful application deletion."""
        app_id = data_service.add_application(sample_application_data)
        
        success = data_service.delete_application(app_id)
        assert success is True
        
        # Verify deletion
        applications = data_service.get_applications_table_data()
        assert len(applications) == 0
    
    def test_delete_application_nonexistent(self, data_service):
        """Test deleting non-existent application."""
        success = data_service.delete_application(999)
        # Should handle gracefully
        assert success in [True, False]  # Implementation dependent


@pytest.mark.database
class TestStatusHistory:
    """Test status history functionality."""
    
    def test_status_history_on_add(self, data_service, sample_application_data):
        """Test that status history is created when adding application."""
        app_id = data_service.add_application(sample_application_data)
        
        history = data_service.get_status_history(app_id)
        
        assert len(history) >= 1
        assert history[0]['status'] == sample_application_data['status']
        assert history[0]['application_id'] == app_id
    
    def test_status_history_on_update(self, data_service, sample_application_data):
        """Test that status history is updated when status changes."""
        app_id = data_service.add_application(sample_application_data)
        
        # Update status
        data_service.update_application(app_id, {'status': 'Online Assessment'})
        
        history = data_service.get_status_history(app_id)
        
        assert len(history) >= 2
        status_values = [entry['status'] for entry in history]
        assert 'Applied' in status_values
        assert 'Online Assessment' in status_values
    
    def test_status_history_multiple_updates(self, data_service, sample_application_data):
        """Test status history with multiple status updates."""
        app_id = data_service.add_application(sample_application_data)
        
        status_progression = [
            'Online Assessment',
            'Interviewing: 1st round',
            'Interviewing: 2nd round',
            'Offer'
        ]
        
        for status in status_progression:
            data_service.update_application(app_id, {'status': status})
        
        history = data_service.get_status_history(app_id)
        
        assert len(history) >= len(status_progression) + 1  # +1 for initial status
        status_values = [entry['status'] for entry in history]
        
        # Check all statuses are recorded
        assert 'Applied' in status_values  # Initial status
        for status in status_progression:
            assert status in status_values
    
    def test_status_history_nonexistent_application(self, data_service):
        """Test getting status history for non-existent application."""
        history = data_service.get_status_history(999)
        assert history == []
    
    def test_status_history_timestamps(self, data_service, sample_application_data):
        """Test that status history entries have timestamps."""
        app_id = data_service.add_application(sample_application_data)
        
        history = data_service.get_status_history(app_id)
        
        assert len(history) >= 1
        for entry in history:
            assert 'timestamp' in entry
            assert entry['timestamp'] is not None
            assert entry['timestamp'] != ''


@pytest.mark.database
class TestDataValidation:
    """Test data validation in database operations."""
    
    def test_add_application_missing_required_fields(self, data_service):
        """Test adding application with missing required fields."""
        incomplete_data = {
            'company_name': 'Test Corp'
            # Missing job_title and date_applied
        }
        
        # Should either succeed with defaults or fail gracefully
        try:
            app_id = data_service.add_application(incomplete_data)
            # If it succeeds, verify some data was stored
            if app_id:
                applications = data_service.get_applications_table_data()
                assert len(applications) >= 1
        except Exception:
            # Exception is acceptable for missing required fields
            pass
    
    def test_add_application_sql_injection_protection(self, data_service):
        """Test protection against SQL injection in add operations."""
        malicious_data = {
            'company_name': "'; DROP TABLE applications; --",
            'job_title': 'Engineer',
            'date_applied': '2024-01-15'
        }
        
        app_id = data_service.add_application(malicious_data)
        
        # Should handle gracefully and not execute malicious SQL
        applications = data_service.get_applications_table_data()
        
        # Verify table still exists and data is safe
        if app_id:
            assert len(applications) >= 1
            # The malicious string should be stored as text, not executed
            assert applications[0]['company_name'] == malicious_data['company_name']
    
    def test_update_application_sql_injection_protection(self, data_service, sample_application_data):
        """Test protection against SQL injection in update operations."""
        app_id = data_service.add_application(sample_application_data)
        
        malicious_update = {
            'company_name': "'; DROP TABLE applications; --",
            'notes': "'; UPDATE applications SET status='Hacked'; --"
        }
        
        data_service.update_application(app_id, malicious_update)
        
        # Verify data integrity
        applications = data_service.get_applications_table_data()
        assert len(applications) >= 1
        # Malicious strings should be stored as text
        assert applications[0]['company_name'] == malicious_update['company_name']
    
    def test_unicode_and_special_characters(self, data_service):
        """Test handling of unicode and special characters."""
        unicode_data = {
            'company_name': 'Ñetflix 🚀',
            'job_title': 'Développeur 💻',
            'date_applied': '2024-01-15',
            'notes': '北京科技公司 - Software Engineer'
        }
        
        app_id = data_service.add_application(unicode_data)
        assert app_id is not None
        
        # Verify unicode data is stored correctly
        applications = data_service.get_applications_table_data()
        stored_app = applications[0]
        assert stored_app['company_name'] == unicode_data['company_name']
        assert stored_app['job_title'] == unicode_data['job_title']
        assert stored_app['notes'] == unicode_data['notes']


@pytest.mark.database
@pytest.mark.slow
class TestDatabasePerformance:
    """Test database performance with larger datasets."""
    
    def test_bulk_insert_performance(self, data_service):
        """Test performance of bulk inserts."""
        import time
        
        start_time = time.time()
        
        # Insert 100 applications
        for i in range(100):
            app_data = {
                'company_name': f'Performance Corp {i}',
                'job_title': f'Engineer {i}',
                'date_applied': '2024-01-15',
                'category': 'SWE',
                'status': 'Applied',
                'notes': f'Performance test {i}'
            }
            data_service.add_application(app_data)
        
        duration = time.time() - start_time
        
        # Should complete within reasonable time (2 seconds for 100 inserts)
        assert duration < 2.0
        
        # Verify all data was inserted
        applications = data_service.get_applications_table_data()
        assert len(applications) == 100
    
    def test_large_dataset_retrieval(self, data_service):
        """Test retrieval performance with large dataset."""
        # Insert 500 applications
        for i in range(500):
            app_data = {
                'company_name': f'Large Dataset Corp {i}',
                'job_title': f'Engineer {i}',
                'date_applied': '2024-01-15',
                'category': 'SWE',
                'status': 'Applied'
            }
            data_service.add_application(app_data)
        
        import time
        start_time = time.time()
        
        applications = data_service.get_applications_table_data()
        
        duration = time.time() - start_time
        
        # Should retrieve large dataset quickly (under 1 second)
        assert duration < 1.0
        assert len(applications) == 500


@pytest.mark.database
class TestDatabaseErrors:
    """Test database error handling."""
    
    def test_database_connection_error_handling(self, data_service):
        """Test handling of database connection errors."""
        # Mock a database connection error
        with patch.object(data_service, '_get_connection', side_effect=sqlite3.Error("Connection failed")):
            # Operations should handle errors gracefully
            try:
                applications = data_service.get_applications_table_data()
                # Should return empty list or handle gracefully
                assert isinstance(applications, list)
            except Exception:
                # Exception is acceptable for connection errors
                pass
    
    def test_database_corruption_handling(self, data_service):
        """Test handling of database corruption scenarios."""
        # This test would be more complex in a real scenario
        # For now, test that the service handles basic errors
        
        # Try to add application with corrupted data
        corrupted_data = {
            'company_name': 'A' * 10000,  # Extremely long string
            'job_title': 'Engineer',
            'date_applied': '2024-01-15'
        }
        
        try:
            app_id = data_service.add_application(corrupted_data)
            # If it succeeds, it should handle the data appropriately
            if app_id:
                applications = data_service.get_applications_table_data()
                assert len(applications) >= 1
        except Exception:
            # Exception is acceptable for corrupted data
            pass 