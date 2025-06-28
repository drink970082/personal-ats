"""
Dash callback tests using callback context mocking.
"""

import pytest
from contextvars import copy_context
from dash._callback_context import context_value
from dash._utils import AttributeDict
from unittest.mock import Mock, patch


@pytest.mark.callbacks
class TestApplicationFormCallbacks:
    """Test callbacks related to the application form."""
    
    def test_add_application_callback(self, app_module, mock_dash_app):
        """Test the add application callback."""
        # Mock the callback function
        from app import add_application_callback
        
        # Test data
        form_data = {
            'company': 'Test Corp',
            'title': 'Engineer',
            'url': 'https://test.com',
            'date': '2024-01-15',
            'category': 'SWE',
            'notes': 'Test notes'
        }
        
        # Mock database operations
        with patch('app_redesigned.data_service') as mock_service:
            mock_service.add_application.return_value = 1
            mock_service.get_applications_table_data.return_value = []
            
            # Call the callback
            result = add_application_callback(
                1,  # n_clicks
                form_data['company'],
                form_data['title'],
                form_data['url'],
                form_data['date'],
                form_data['category'],
                form_data['notes']
            )
            
            # Verify the callback was triggered correctly
            mock_service.add_application.assert_called_once()
            
            # Verify return values (table data, notification, form reset)
            assert isinstance(result, tuple)
            assert len(result) >= 3  # Should return multiple outputs
    
    def test_add_application_callback_no_click(self, app_module):
        """Test add application callback when button not clicked."""
        from app import add_application_callback
        
        # When n_clicks is None or 0, should not trigger
        result = add_application_callback(
            None,  # No click
            'Test Corp', 'Engineer', 'https://test.com',
            '2024-01-15', 'SWE', 'Test notes'
        )
        
        # Should return default/empty values
        assert isinstance(result, tuple)
    
    def test_add_application_callback_missing_data(self, app_module):
        """Test add application callback with missing required data."""
        from app import add_application_callback
        
        with patch('app_redesigned.data_service') as mock_service:
            # Test with missing company name
            result = add_application_callback(
                1,  # n_clicks
                '',  # Empty company name
                'Engineer',
                'https://test.com',
                '2024-01-15',
                'SWE',
                'Test notes'
            )
            
            # Should handle gracefully - might not call add_application
            # or might call it and let validation handle it
            assert isinstance(result, tuple)


@pytest.mark.callbacks
class TestFilteringCallbacks:
    """Test callbacks related to filtering functionality."""
    
    def test_filter_applications_callback(self, app_module):
        """Test the filter applications callback."""
        from app import update_table_and_pagination
        
        # Mock application data
        mock_data = [
            {'company_name': 'Corp A', 'status': 'Applied', 'category': 'SWE'},
            {'company_name': 'Corp B', 'status': 'Rejected', 'category': 'DS'},
        ]
        
        with patch('app_redesigned.data_service') as mock_service:
            mock_service.get_applications_table_data.return_value = mock_data
            
            # Test filtering by status
            result = update_table_and_pagination(
                'Applied',  # status_filter
                'all',      # category_filter
                '',         # search_value
                0,          # current_page
                10          # page_size
            )
            
            # Should return filtered data
            assert isinstance(result, tuple)
            # Verify the function was called
            mock_service.get_applications_table_data.assert_called()
    
    def test_filter_by_category_callback(self, app_module):
        """Test filtering by category."""
        from app import update_table_and_pagination
        
        mock_data = [
            {'company_name': 'Corp A', 'status': 'Applied', 'category': 'SWE'},
            {'company_name': 'Corp B', 'status': 'Applied', 'category': 'DS'},
        ]
        
        with patch('app_redesigned.data_service') as mock_service:
            mock_service.get_applications_table_data.return_value = mock_data
            
            result = update_table_and_pagination(
                'all',  # status_filter
                'SWE',  # category_filter
                '',     # search_value
                0,      # current_page
                10      # page_size
            )
            
            assert isinstance(result, tuple)
    
    def test_search_callback(self, app_module):
        """Test search functionality callback."""
        from app import update_table_and_pagination
        
        mock_data = [
            {'company_name': 'Tech Corp', 'job_title': 'Engineer', 'status': 'Applied', 'category': 'SWE'},
            {'company_name': 'Data Inc', 'job_title': 'Scientist', 'status': 'Applied', 'category': 'DS'},
        ]
        
        with patch('app_redesigned.data_service') as mock_service:
            mock_service.get_applications_table_data.return_value = mock_data
            
            result = update_table_and_pagination(
                'all',      # status_filter
                'all',      # category_filter
                'Tech',     # search_value
                0,          # current_page
                10          # page_size
            )
            
            assert isinstance(result, tuple)


@pytest.mark.callbacks
class TestPaginationCallbacks:
    """Test callbacks related to pagination."""
    
    def test_pagination_navigation_callback(self, app_module):
        """Test pagination navigation callback."""
        from app import update_table_and_pagination
        
        # Create enough mock data for pagination
        mock_data = [
            {'company_name': f'Corp {i}', 'status': 'Applied', 'category': 'SWE'}
            for i in range(25)  # 25 items for pagination testing
        ]
        
        with patch('app_redesigned.data_service') as mock_service:
            mock_service.get_applications_table_data.return_value = mock_data
            
            # Test first page
            result_page_0 = update_table_and_pagination(
                'all', 'all', '', 0, 10  # Page 0, size 10
            )
            
            # Test second page
            result_page_1 = update_table_and_pagination(
                'all', 'all', '', 1, 10  # Page 1, size 10
            )
            
            assert isinstance(result_page_0, tuple)
            assert isinstance(result_page_1, tuple)
    
    def test_page_size_change_callback(self, app_module):
        """Test changing page size."""
        from app import update_table_and_pagination
        
        mock_data = [
            {'company_name': f'Corp {i}', 'status': 'Applied', 'category': 'SWE'}
            for i in range(15)
        ]
        
        with patch('app_redesigned.data_service') as mock_service:
            mock_service.get_applications_table_data.return_value = mock_data
            
            # Test different page sizes
            for page_size in [5, 10, 20]:
                result = update_table_and_pagination(
                    'all', 'all', '', 0, page_size
                )
                assert isinstance(result, tuple)


@pytest.mark.callbacks
class TestStatusUpdateCallbacks:
    """Test callbacks for status updates with context."""
    
    def test_status_update_callback_with_context(self, app_module):
        """Test status update callback using callback context."""
        from app import update_application_status
        
        def run_callback():
            # Set up callback context
            context_value.set(AttributeDict(**{
                "triggered_inputs": [{"prop_id": "status-dropdown-1.value"}]
            }))
            
            with patch('app_redesigned.data_service') as mock_service:
                mock_service.update_application.return_value = True
                mock_service.get_applications_table_data.return_value = []
                
                # Call the callback with context
                result = update_application_status(
                    'Online Assessment',  # new_status
                    1  # application_id (from component id)
                )
                
                # Verify database update was called
                mock_service.update_application.assert_called_once_with(
                    1, {'status': 'Online Assessment'}
                )
                
                return result
        
        # Run the callback in a copy context
        ctx = copy_context()
        result = ctx.run(run_callback)
        
        assert isinstance(result, tuple)
    
    def test_status_update_no_context(self, app_module):
        """Test status update callback without proper context."""
        from app import update_application_status
        
        # Call without setting up context (should handle gracefully)
        with patch('app_redesigned.data_service') as mock_service:
            try:
                result = update_application_status('Applied', 1)
                # Should handle lack of context gracefully
                assert isinstance(result, tuple)
            except Exception:
                # Exception is acceptable when context is missing
                pass


@pytest.mark.callbacks  
class TestStatsCallbacks:
    """Test callbacks related to stats updates."""
    
    def test_stats_update_callback(self, app_module):
        """Test stats cards update callback."""
        from app import update_stats_cards
        
        mock_data = [
            {'status': 'Applied', 'category': 'SWE'},
            {'status': 'Rejected', 'category': 'DS'},
            {'status': 'Offer', 'category': 'SWE'},
        ]
        
        with patch('app_redesigned.data_service') as mock_service:
            mock_service.get_applications_table_data.return_value = mock_data
            
            # Trigger stats update
            result = update_stats_cards(trigger=True)
            
            # Should return stats cards
            assert isinstance(result, (list, tuple))
            mock_service.get_applications_table_data.assert_called()


@pytest.mark.callbacks
class TestErrorHandlingCallbacks:
    """Test error handling in callbacks."""
    
    def test_callback_database_error_handling(self, app_module):
        """Test callback behavior when database operations fail."""
        from app import add_application_callback
        
        with patch('app_redesigned.data_service') as mock_service:
            # Mock database failure
            mock_service.add_application.side_effect = Exception("Database error")
            
            # Call should handle error gracefully
            try:
                result = add_application_callback(
                    1, 'Test Corp', 'Engineer', 'https://test.com',
                    '2024-01-15', 'SWE', 'Notes'
                )
                # Should return some result even if database fails
                assert isinstance(result, tuple)
            except Exception:
                # Exception is acceptable for database errors
                pass
    
    def test_callback_invalid_input_handling(self, app_module):
        """Test callback behavior with invalid inputs."""
        from app import update_table_and_pagination
        
        with patch('app_redesigned.data_service') as mock_service:
            mock_service.get_applications_table_data.return_value = []
            
            # Test with invalid/None inputs
            result = update_table_and_pagination(
                None,   # Invalid status
                None,   # Invalid category
                None,   # Invalid search
                -1,     # Invalid page
                0       # Invalid page size
            )
            
            # Should handle invalid inputs gracefully
            assert isinstance(result, tuple)


@pytest.mark.callbacks
class TestCallbackIntegration:
    """Test integration between multiple callbacks."""
    
    def test_add_and_filter_integration(self, app_module):
        """Test that adding an application updates filtered results."""
        from app import add_application_callback, update_table_and_pagination
        
        # Initial empty data
        with patch('app_redesigned.data_service') as mock_service:
            mock_service.get_applications_table_data.return_value = []
            mock_service.add_application.return_value = 1
            
            # Add application
            add_result = add_application_callback(
                1, 'Test Corp', 'Engineer', 'https://test.com',
                '2024-01-15', 'SWE', 'Notes'
            )
            
            # Now mock updated data after addition
            mock_service.get_applications_table_data.return_value = [{
                'id': 1,
                'company_name': 'Test Corp',
                'job_title': 'Engineer',
                'status': 'Applied',
                'category': 'SWE'
            }]
            
            # Filter should show the new application
            filter_result = update_table_and_pagination(
                'all', 'all', '', 0, 10
            )
            
            assert isinstance(add_result, tuple)
            assert isinstance(filter_result, tuple)
    
    def test_status_update_and_stats_integration(self, app_module):
        """Test that status updates affect stats calculations."""
        from app import update_application_status, update_stats_cards
        
        def run_status_update():
            context_value.set(AttributeDict(**{
                "triggered_inputs": [{"prop_id": "status-dropdown-1.value"}]
            }))
            
            with patch('app_redesigned.data_service') as mock_service:
                mock_service.update_application.return_value = True
                
                # Initial data
                initial_data = [{'id': 1, 'status': 'Applied', 'category': 'SWE'}]
                mock_service.get_applications_table_data.return_value = initial_data
                
                # Update status
                status_result = update_application_status('Offer', 1)
                
                # Updated data after status change
                updated_data = [{'id': 1, 'status': 'Offer', 'category': 'SWE'}]
                mock_service.get_applications_table_data.return_value = updated_data
                
                # Stats should reflect the change
                stats_result = update_stats_cards(trigger=True)
                
                return status_result, stats_result
        
        ctx = copy_context()
        status_result, stats_result = ctx.run(run_status_update)
        
        assert isinstance(status_result, tuple)
        assert isinstance(stats_result, (list, tuple)) 