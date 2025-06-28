"""
Integration tests between different components of the ATS system.
"""

import pytest
import tempfile
import os
from unittest.mock import patch
import time


@pytest.mark.integration
class TestDataServiceIntegration:
    """Test integration between data service and application logic."""
    
    def test_data_service_and_constants_integration(self, data_service):
        """Test data service works with defined constants."""
        from config.constants import CATEGORIES, STATUSES
        
        # Test that all categories can be stored
        for category in CATEGORIES:
            app_data = {
                'company_name': f'{category} Corp',
                'job_title': 'Engineer',
                'date_applied': '2024-01-15',
                'category': category,
                'status': 'Applied'
            }
            
            app_id = data_service.add_application(app_data)
            assert app_id is not None
            
            # Verify category was stored correctly
            applications = data_service.get_applications_table_data()
            found_app = next((app for app in applications if app['id'] == app_id), None)
            assert found_app is not None
            assert found_app['category'] == category
    
    def test_data_service_and_filtering_logic_integration(self, populated_data_service, app_module):
        """Test data service data works with filtering logic."""
        # Get all data from populated service
        all_data = populated_data_service.get_applications_table_data()
        
        # Test various filters work with real database data
        filters_to_test = [
            {'status': 'Applied', 'category': 'all', 'search': ''},
            {'status': 'all', 'category': 'SWE', 'search': ''},
            {'status': 'all', 'category': 'all', 'search': 'Tech'},
        ]
        
        for filters in filters_to_test:
            pagination = {'page': 0, 'size': 10}
            result = app_module.apply_filters_and_pagination(all_data, filters, pagination)
            
            # Should return valid pagination result
            assert 'filtered_items' in result
            assert 'page_data' in result
            assert 'total_pages' in result
            assert isinstance(result['page_data'], list)
    
    def test_status_history_integration_across_components(self, data_service):
        """Test status history integration across different components."""
        # Add application
        app_data = {
            'company_name': 'History Integration Corp',
            'job_title': 'Engineer',
            'date_applied': '2024-01-15',
            'category': 'SWE',
            'status': 'Applied'
        }
        
        app_id = data_service.add_application(app_data)
        
        # Progress through different statuses
        status_progression = [
            'Online Assessment',
            'Interviewing: 1st round',
            'Interviewing: 2nd round',
            'Offer'
        ]
        
        for status in status_progression:
            success = data_service.update_application(app_id, {'status': status})
            assert success is True
            time.sleep(0.01)  # Ensure different timestamps
        
        # Verify history integration
        history = data_service.get_status_history(app_id)
        
        # Should have initial status + all updates
        assert len(history) >= len(status_progression) + 1
        
        # Verify chronological order and content
        status_values = [entry['status'] for entry in history]
        assert 'Applied' in status_values
        for status in status_progression:
            assert status in status_values
        
        # Verify current application status matches last update
        applications = data_service.get_applications_table_data()
        current_app = next((app for app in applications if app['id'] == app_id), None)
        assert current_app['status'] == status_progression[-1]


@pytest.mark.integration
class TestFilteringAndPaginationIntegration:
    """Test integration between filtering and pagination systems."""
    
    def test_filters_and_pagination_consistency(self, app_module, multiple_application_data):
        """Test that filtering and pagination work consistently together."""
        # Test with different page sizes and filters
        test_scenarios = [
            ({'status': 'all', 'category': 'SWE', 'search': ''}, 1),
            ({'status': 'all', 'category': 'SWE', 'search': ''}, 2),
            ({'status': 'all', 'category': 'all', 'search': ''}, 3),
        ]
        
        for filters, page_size in test_scenarios:
            pagination = {'page': 0, 'size': page_size}
            result = app_module.apply_filters_and_pagination(
                multiple_application_data, filters, pagination
            )
            
            # Verify pagination math is correct
            assert result['total_pages'] == ((result['filtered_items'] + page_size - 1) // page_size)
            assert len(result['page_data']) <= page_size
            
            # Test different pages for consistency
            if result['total_pages'] > 1:
                pagination['page'] = 1
                page2_result = app_module.apply_filters_and_pagination(
                    multiple_application_data, filters, pagination
                )
                
                # Same filter should give same total count on different pages
                assert page2_result['filtered_items'] == result['filtered_items']
                assert page2_result['total_pages'] == result['total_pages']
    
    def test_search_and_category_filter_integration(self, app_module, multiple_application_data):
        """Test that search and category filters work together."""
        # Combined filter: search for 'Corp' in SWE category
        filters = {'status': 'all', 'category': 'SWE', 'search': 'Corp'}
        pagination = {'page': 0, 'size': 10}
        
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        
        # Should return SWE applications with 'Corp' in name
        for item in result['page_data']:
            assert item['category'] == 'SWE'
            assert 'Corp' in item['company_name']
    
    def test_status_filter_and_pagination_edge_cases(self, app_module):
        """Test edge cases in status filtering with pagination."""
        # Create data where filter results in exactly page boundaries
        test_data = [
            {'company_name': f'Status Corp {i}', 'status': 'Applied', 'category': 'SWE'}
            for i in range(5)
        ] + [
            {'company_name': f'Other Corp {i}', 'status': 'Rejected', 'category': 'SWE'}
            for i in range(3)
        ]
        
        # Filter for 'Applied' with page size 3 (should give 2 pages)
        filters = {'status': 'Applied', 'category': 'all', 'search': ''}
        pagination = {'page': 0, 'size': 3}
        
        result = app_module.apply_filters_and_pagination(test_data, filters, pagination)
        
        assert result['filtered_items'] == 5
        assert result['total_pages'] == 2  # ceil(5/3) = 2
        assert len(result['page_data']) == 3  # First page has 3 items
        
        # Test second page
        pagination['page'] = 1
        page2_result = app_module.apply_filters_and_pagination(test_data, filters, pagination)
        
        assert len(page2_result['page_data']) == 2  # Second page has 2 items


@pytest.mark.integration
class TestStatsIntegration:
    """Test integration between stats calculation and application data."""
    
    def test_stats_calculation_with_real_data_service(self, populated_data_service, app_module):
        """Test stats calculation with real data from data service."""
        # Get real data from populated service
        applications = populated_data_service.get_applications_table_data()
        
        # Calculate stats using app module
        stats = app_module.calculate_application_stats(applications)
        
        # Verify stats make sense
        assert stats['total'] == len(applications)
        assert stats['total'] >= stats['applied']
        assert stats['total'] >= stats['rejected']
        assert stats['total'] >= stats['offer']
        
        # Active should be non-terminal statuses
        expected_active = sum(1 for app in applications 
                            if app['status'] not in ['Rejected', 'Offer'])
        assert stats['active'] == expected_active
    
    def test_stats_cards_generation_integration(self, populated_data_service, app_module):
        """Test integration between stats calculation and card generation."""
        applications = populated_data_service.get_applications_table_data()
        
        # Generate stats cards
        cards = app_module.get_stats_cards(applications)
        
        # Should have multiple cards
        assert len(cards) >= 6
        
        # Each card should have proper structure
        for card in cards:
            assert 'type' in card
            assert 'props' in card
            assert 'children' in card['props']
            
            # Should have number and label
            children = card['props']['children']
            assert len(children) >= 2
            
            # Number should be numeric string
            number_text = children[0]['props']['children']
            assert number_text.isdigit()
    
    def test_stats_update_after_status_changes(self, data_service, app_module):
        """Test that stats update correctly after status changes."""
        # Add application
        app_data = {
            'company_name': 'Stats Update Corp',
            'job_title': 'Engineer',
            'date_applied': '2024-01-15',
            'category': 'SWE',
            'status': 'Applied'
        }
        
        app_id = data_service.add_application(app_data)
        
        # Get initial stats
        applications = data_service.get_applications_table_data()
        initial_stats = app_module.calculate_application_stats(applications)
        
        # Update status
        data_service.update_application(app_id, {'status': 'Offer'})
        
        # Get updated stats
        updated_applications = data_service.get_applications_table_data()
        updated_stats = app_module.calculate_application_stats(updated_applications)
        
        # Stats should have changed appropriately
        assert updated_stats['applied'] == initial_stats['applied'] - 1
        assert updated_stats['offer'] == initial_stats['offer'] + 1
        assert updated_stats['active'] == initial_stats['active'] - 1  # Offer is not active


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test error handling across integrated components."""
    
    def test_data_service_error_handling_with_filtering(self, app_module):
        """Test filtering gracefully handles data service errors."""
        # Test with None data (simulating data service error)
        filters = {'status': 'all', 'category': 'all', 'search': ''}
        pagination = {'page': 0, 'size': 10}
        
        # Should handle None data gracefully
        result = app_module.apply_filters_and_pagination(None, filters, pagination)
        
        # Should return safe defaults
        assert 'filtered_items' in result
        assert 'page_data' in result
        assert isinstance(result['page_data'], list)
    
    def test_malformed_data_handling_across_components(self, app_module):
        """Test handling of malformed data across different components."""
        # Create malformed data
        malformed_data = [
            {'company_name': 'Good Corp', 'status': 'Applied'},  # Missing fields
            {'status': 'Applied'},  # Missing company_name
            {},  # Empty record
            None,  # None record
        ]
        
        # Should handle malformed data gracefully
        filters = {'status': 'all', 'category': 'all', 'search': ''}
        pagination = {'page': 0, 'size': 10}
        
        result = app_module.apply_filters_and_pagination(malformed_data, filters, pagination)
        
        # Should not crash and return valid structure
        assert isinstance(result, dict)
        assert 'page_data' in result
        assert isinstance(result['page_data'], list)
    
    def test_database_and_stats_error_integration(self, app_module):
        """Test stats calculation with problematic database data."""
        # Test with various problematic data scenarios
        problematic_data = [
            {'status': None, 'company_name': 'Corp A'},
            {'status': '', 'company_name': 'Corp B'},
            {'status': 'InvalidStatus', 'company_name': 'Corp C'},
        ]
        
        # Stats calculation should handle gracefully
        stats = app_module.calculate_application_stats(problematic_data)
        
        # Should return valid stats structure
        assert isinstance(stats, dict)
        assert 'total' in stats
        assert 'applied' in stats
        assert all(isinstance(v, int) for v in stats.values())


@pytest.mark.integration
class TestPerformanceIntegration:
    """Test performance across integrated components."""
    
    @pytest.mark.slow
    def test_large_dataset_integration_performance(self, data_service, app_module):
        """Test performance with large dataset across components."""
        import time
        
        # Add large dataset
        start_time = time.time()
        
        for i in range(100):
            app_data = {
                'company_name': f'Performance Corp {i}',
                'job_title': f'Engineer {i}',
                'date_applied': '2024-01-15',
                'category': 'SWE',
                'status': 'Applied'
            }
            data_service.add_application(app_data)
        
        data_creation_time = time.time() - start_time
        
        # Test filtering performance
        filter_start_time = time.time()
        applications = data_service.get_applications_table_data()
        
        filters = {'status': 'all', 'category': 'SWE', 'search': 'Performance'}
        pagination = {'page': 0, 'size': 10}
        
        result = app_module.apply_filters_and_pagination(applications, filters, pagination)
        
        filter_duration = time.time() - filter_start_time
        
        # Performance assertions
        assert data_creation_time < 10.0  # 10 seconds for 100 records
        assert filter_duration < 1.0  # 1 second for filtering
        assert result['filtered_items'] == 100  # All should match
    
    def test_concurrent_access_integration(self, data_service):
        """Test concurrent access patterns across components."""
        import threading
        
        def add_applications(thread_id):
            for i in range(10):
                app_data = {
                    'company_name': f'Concurrent Corp {thread_id}-{i}',
                    'job_title': 'Engineer',
                    'date_applied': '2024-01-15',
                    'category': 'SWE',
                    'status': 'Applied'
                }
                data_service.add_application(app_data)
        
        # Create multiple threads
        threads = []
        for thread_id in range(3):
            thread = threading.Thread(target=add_applications, args=(thread_id,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify data integrity
        applications = data_service.get_applications_table_data()
        concurrent_apps = [app for app in applications if 'Concurrent Corp' in app['company_name']]
        
        # Should have all applications from all threads
        assert len(concurrent_apps) == 30  # 3 threads × 10 applications 