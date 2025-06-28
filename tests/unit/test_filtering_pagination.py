"""
Unit tests for filtering and pagination functionality.
"""

import pytest
from unittest.mock import Mock


@pytest.mark.unit
class TestFilteringLogic:
    """Test the core filtering logic."""
    
    def test_status_filter_applied(self, app_module, multiple_application_data):
        """Test filtering by status 'Applied'."""
        filters = {'status': 'Applied', 'category': 'all', 'search': ''}
        pagination = {'page': 0, 'size': 10}
        
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        
        assert result['filtered_items'] == 1
        assert result['page_data'][0]['company_name'] == 'Tech Corp A'
        assert result['page_data'][0]['status'] == 'Applied'
    
    def test_status_filter_online_assessment(self, app_module, multiple_application_data):
        """Test filtering by status 'Online Assessment'."""
        filters = {'status': 'Online Assessment', 'category': 'all', 'search': ''}
        pagination = {'page': 0, 'size': 10}
        
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        
        assert result['filtered_items'] == 1
        assert result['page_data'][0]['company_name'] == 'Data Inc B'
        assert result['page_data'][0]['status'] == 'Online Assessment'
    
    def test_status_filter_interviewing(self, app_module, multiple_application_data):
        """Test filtering by status containing 'Interviewing'."""
        filters = {'status': 'Interviewing: 1st round', 'category': 'all', 'search': ''}
        pagination = {'page': 0, 'size': 10}
        
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        
        assert result['filtered_items'] == 1
        assert result['page_data'][0]['company_name'] == 'ML Company C'
        assert 'Interviewing' in result['page_data'][0]['status']
    
    def test_status_filter_all(self, app_module, multiple_application_data):
        """Test filtering with 'all' status shows all items."""
        filters = {'status': 'all', 'category': 'all', 'search': ''}
        pagination = {'page': 0, 'size': 10}
        
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        
        assert result['filtered_items'] == 5
        assert len(result['page_data']) == 5
    
    def test_category_filter_swe(self, app_module, multiple_application_data):
        """Test filtering by category 'SWE'."""
        filters = {'status': 'all', 'category': 'SWE', 'search': ''}
        pagination = {'page': 0, 'size': 10}
        
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        
        assert result['filtered_items'] == 2  # Tech Corp A and Startup E
        swe_companies = {item['company_name'] for item in result['page_data']}
        assert 'Tech Corp A' in swe_companies
        assert 'Startup E' in swe_companies
    
    def test_category_filter_ds(self, app_module, multiple_application_data):
        """Test filtering by category 'DS'."""
        filters = {'status': 'all', 'category': 'DS', 'search': ''}
        pagination = {'page': 0, 'size': 10}
        
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        
        assert result['filtered_items'] == 1
        assert result['page_data'][0]['company_name'] == 'Data Inc B'
        assert result['page_data'][0]['category'] == 'DS'
    
    def test_search_filter_company_name(self, app_module, multiple_application_data):
        """Test search filtering by company name."""
        filters = {'status': 'all', 'category': 'all', 'search': 'Tech Corp'}
        pagination = {'page': 0, 'size': 10}
        
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        
        assert result['filtered_items'] == 1
        assert result['page_data'][0]['company_name'] == 'Tech Corp A'
    
    def test_search_filter_job_title(self, app_module, multiple_application_data):
        """Test search filtering by job title."""
        filters = {'status': 'all', 'category': 'all', 'search': 'Data Scientist'}
        pagination = {'page': 0, 'size': 10}
        
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        
        assert result['filtered_items'] == 1
        assert result['page_data'][0]['job_title'] == 'Data Scientist'
    
    def test_search_filter_case_insensitive(self, app_module, multiple_application_data):
        """Test search filtering is case insensitive."""
        filters = {'status': 'all', 'category': 'all', 'search': 'STARTUP'}
        pagination = {'page': 0, 'size': 10}
        
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        
        assert result['filtered_items'] == 1
        assert result['page_data'][0]['company_name'] == 'Startup E'
    
    def test_combined_filters(self, app_module, multiple_application_data):
        """Test combining multiple filters."""
        filters = {'status': 'Applied', 'category': 'SWE', 'search': ''}
        pagination = {'page': 0, 'size': 10}
        
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        
        assert result['filtered_items'] == 1
        assert result['page_data'][0]['company_name'] == 'Tech Corp A'
        assert result['page_data'][0]['status'] == 'Applied'
        assert result['page_data'][0]['category'] == 'SWE'
    
    def test_no_matches_filter(self, app_module, multiple_application_data):
        """Test filtering with no matches."""
        filters = {'status': 'all', 'category': 'all', 'search': 'NonexistentCompany'}
        pagination = {'page': 0, 'size': 10}
        
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        
        assert result['filtered_items'] == 0
        assert len(result['page_data']) == 0


@pytest.mark.unit  
class TestPaginationLogic:
    """Test the core pagination logic."""
    
    def test_pagination_first_page(self, app_module, multiple_application_data):
        """Test pagination on first page."""
        filters = {'status': 'all', 'category': 'all', 'search': ''}
        pagination = {'page': 0, 'size': 2}
        
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        
        assert result['filtered_items'] == 5
        assert len(result['page_data']) == 2
        assert result['current_page'] == 0
        assert result['total_pages'] == 3  # ceil(5/2) = 3
        assert result['has_next'] is True
        assert result['has_prev'] is False
    
    def test_pagination_middle_page(self, app_module, multiple_application_data):
        """Test pagination on middle page."""
        filters = {'status': 'all', 'category': 'all', 'search': ''}
        pagination = {'page': 1, 'size': 2}
        
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        
        assert result['filtered_items'] == 5
        assert len(result['page_data']) == 2
        assert result['current_page'] == 1
        assert result['total_pages'] == 3
        assert result['has_next'] is True
        assert result['has_prev'] is True
    
    def test_pagination_last_page(self, app_module, multiple_application_data):
        """Test pagination on last page."""
        filters = {'status': 'all', 'category': 'all', 'search': ''}
        pagination = {'page': 2, 'size': 2}
        
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        
        assert result['filtered_items'] == 5
        assert len(result['page_data']) == 1  # Last page has only 1 item
        assert result['current_page'] == 2
        assert result['total_pages'] == 3
        assert result['has_next'] is False
        assert result['has_prev'] is True
    
    def test_pagination_page_size_changes(self, app_module, multiple_application_data):
        """Test different page sizes."""
        filters = {'status': 'all', 'category': 'all', 'search': ''}
        
        # Test page size 1
        pagination = {'page': 0, 'size': 1}
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        assert len(result['page_data']) == 1
        assert result['total_pages'] == 5
        
        # Test page size 10 (larger than data)
        pagination = {'page': 0, 'size': 10}
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        assert len(result['page_data']) == 5
        assert result['total_pages'] == 1
    
    def test_pagination_out_of_bounds(self, app_module, multiple_application_data):
        """Test pagination with out of bounds page number."""
        filters = {'status': 'all', 'category': 'all', 'search': ''}
        pagination = {'page': 10, 'size': 2}  # Page 10 doesn't exist
        
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        
        # Should handle gracefully
        assert result['filtered_items'] == 5
        assert len(result['page_data']) == 0  # No data on non-existent page
        assert result['current_page'] == 10
        assert result['total_pages'] == 3
    
    def test_pagination_with_filters(self, app_module, multiple_application_data):
        """Test pagination combined with filters."""
        filters = {'status': 'all', 'category': 'SWE', 'search': ''}
        pagination = {'page': 0, 'size': 1}
        
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        
        assert result['filtered_items'] == 2  # 2 SWE entries
        assert len(result['page_data']) == 1  # Page size is 1
        assert result['total_pages'] == 2  # ceil(2/1) = 2
        assert result['page_data'][0]['category'] == 'SWE'


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases in filtering and pagination."""
    
    def test_empty_data(self, app_module):
        """Test filtering and pagination with empty data."""
        filters = {'status': 'all', 'category': 'all', 'search': ''}
        pagination = {'page': 0, 'size': 10}
        
        result = app_module.apply_filters_and_pagination([], filters, pagination)
        
        assert result['filtered_items'] == 0
        assert len(result['page_data']) == 0
        assert result['total_pages'] == 0
        assert result['has_next'] is False
        assert result['has_prev'] is False
    
    def test_none_values_in_data(self, app_module):
        """Test handling of None values in data."""
        data_with_nones = [
            {
                'company_name': 'Test Corp',
                'job_title': None,
                'category': 'SWE',
                'status': 'Applied',
                'date_applied': '2024-01-15'
            }
        ]
        
        filters = {'status': 'all', 'category': 'all', 'search': 'Test'}
        pagination = {'page': 0, 'size': 10}
        
        result = app_module.apply_filters_and_pagination(
            data_with_nones, filters, pagination
        )
        
        # Should handle None values gracefully
        assert result['filtered_items'] >= 0
    
    def test_malformed_pagination_params(self, app_module, multiple_application_data):
        """Test handling of malformed pagination parameters."""
        filters = {'status': 'all', 'category': 'all', 'search': ''}
        
        # Test negative page
        pagination = {'page': -1, 'size': 2}
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        assert result['current_page'] == -1  # Should handle gracefully
        
        # Test zero page size
        pagination = {'page': 0, 'size': 0}
        result = app_module.apply_filters_and_pagination(
            multiple_application_data, filters, pagination
        )
        # Should handle gracefully without crashing
        assert 'page_data' in result 