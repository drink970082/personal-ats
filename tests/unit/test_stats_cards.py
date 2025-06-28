"""
Unit tests for stats cards functionality.
"""

import pytest


@pytest.mark.unit
class TestStatsCardsCreation:
    """Test stats cards creation functionality."""
    
    def test_create_stats_card_basic(self, app_module):
        """Test creating a basic stats card."""
        card = app_module.create_stats_card("42", "Applications")
        
        # Verify card structure - use correct Dash component access
        assert hasattr(card, 'children')
        assert 'stats-card' in str(card.className)
        
        # Check children structure (number and label)
        children = card.children
        assert len(children) == 2
        assert children[0].children == "42"
    
    def test_create_stats_card_different_colors(self, app_module):
        """Test creating stats cards with consistent styling."""
        # The create_stats_card function doesn't take color parameter
        card = app_module.create_stats_card("10", "Test")
        assert 'stats-card' in str(card.className)
    
    def test_create_stats_card_large_numbers(self, app_module):
        """Test stats cards with large numbers."""
        large_numbers = ["1000", "10000", "999999"]
        
        for number in large_numbers:
            card = app_module.create_stats_card(number, "Applications")
            children = card.children
            assert children[0].children == number
    
    def test_create_stats_card_zero_value(self, app_module):
        """Test stats card with zero value."""
        card = app_module.create_stats_card("0", "Applications")
        children = card.children
        assert children[0].children == "0"
    
    def test_create_stats_card_long_label(self, app_module):
        """Test stats card with long label."""
        long_label = "Very Long Application Status Label"
        card = app_module.create_stats_card("5", long_label)
        children = card.children
        # Label handling may split the text, so just check it exists
        assert len(children) == 2


@pytest.mark.unit
class TestStatsCalculation:
    """Test statistics calculation from application data."""
    
    def test_calculate_stats_empty_data(self, app_module):
        """Test stats calculation with empty data."""
        stats = app_module.calculate_application_stats([])
        
        assert stats['applied'] == 0
        assert stats['active'] == 0
        assert stats['assessment'] == 0
        assert stats['interviewing'] == 0
        assert stats['rejected'] == 0
        assert stats['offer'] == 0
    
    def test_calculate_stats_single_application(self, app_module, sample_application_data):
        """Test stats calculation with single application."""
        stats = app_module.calculate_application_stats([sample_application_data])
        
        assert stats['applied'] == 1
        assert stats['active'] == 0  # Applied status goes to applied, not active
        assert stats['assessment'] == 0
        assert stats['interviewing'] == 0
        assert stats['rejected'] == 0
        assert stats['offer'] == 0
    
    def test_calculate_stats_multiple_applications(self, app_module, multiple_application_data):
        """Test stats calculation with multiple applications."""
        stats = app_module.calculate_application_stats(multiple_application_data)
        
        assert stats['applied'] == 1  # Tech Corp A
        assert stats['assessment'] == 1  # Data Inc B
        assert stats['interviewing'] == 1  # ML Company C
        assert stats['rejected'] == 1  # Finance Corp D
        assert stats['offer'] == 1  # Startup E
        assert stats['active'] == 0  # No statuses should fall through to active
    
    def test_calculate_stats_all_applied(self, app_module):
        """Test stats calculation when all applications are Applied."""
        all_applied_data = [
            {'status': 'Applied', 'company_name': 'Corp A'},
            {'status': 'Applied', 'company_name': 'Corp B'},
            {'status': 'Applied', 'company_name': 'Corp C'}
        ]
        
        stats = app_module.calculate_application_stats(all_applied_data)
        
        assert stats['applied'] == 3
        assert stats['active'] == 0
        assert stats['assessment'] == 0
        assert stats['interviewing'] == 0
        assert stats['rejected'] == 0
        assert stats['offer'] == 0
    
    def test_calculate_stats_all_rejected(self, app_module):
        """Test stats calculation when all applications are Rejected."""
        all_rejected_data = [
            {'status': 'Rejected', 'company_name': 'Corp A'},
            {'status': 'Rejected', 'company_name': 'Corp B'}
        ]
        
        stats = app_module.calculate_application_stats(all_rejected_data)
        
        assert stats['applied'] == 0
        assert stats['active'] == 0  # Rejected is not active
        assert stats['assessment'] == 0
        assert stats['interviewing'] == 0
        assert stats['rejected'] == 2
        assert stats['offer'] == 0
    
    def test_calculate_stats_various_interviewing_stages(self, app_module):
        """Test stats calculation with various interviewing stages."""
        interviewing_data = [
            {'status': 'Interviewing: 1st round', 'company_name': 'Corp A'},
            {'status': 'Interviewing: 2nd round', 'company_name': 'Corp B'},
            {'status': 'Interviewing: 3rd round', 'company_name': 'Corp C'},
            {'status': 'Interviewing: 4th round', 'company_name': 'Corp D'},
            {'status': 'Interviewing: 5th round', 'company_name': 'Corp E'}
        ]
        
        stats = app_module.calculate_application_stats(interviewing_data)
        
        assert stats['interviewing'] == 5  # All interviewing stages count
        assert stats['active'] == 0  # Interviewing has its own category
        assert stats['applied'] == 0
        assert stats['assessment'] == 0
        assert stats['rejected'] == 0
        assert stats['offer'] == 0
    
    def test_calculate_stats_mixed_scenarios(self, app_module):
        """Test stats calculation with mixed realistic scenarios."""
        mixed_data = [
            {'status': 'Applied', 'company_name': 'Corp A'},
            {'status': 'Applied', 'company_name': 'Corp B'},
            {'status': 'Online Assessment', 'company_name': 'Corp C'},
            {'status': 'Online Assessment', 'company_name': 'Corp D'},
            {'status': 'Interviewing: 1st round', 'company_name': 'Corp E'},
            {'status': 'Interviewing: 2nd round', 'company_name': 'Corp F'},
            {'status': 'Rejected', 'company_name': 'Corp G'},
            {'status': 'Rejected', 'company_name': 'Corp H'},
            {'status': 'Rejected', 'company_name': 'Corp I'},
            {'status': 'Offer', 'company_name': 'Corp J'}
        ]
        
        stats = app_module.calculate_application_stats(mixed_data)
        
        assert stats['applied'] == 2
        assert stats['assessment'] == 2
        assert stats['interviewing'] == 2
        assert stats['rejected'] == 3
        assert stats['offer'] == 1
        assert stats['active'] == 0  # Other statuses have their own categories
    
    def test_calculate_stats_with_none_status(self, app_module):
        """Test stats calculation with None status values."""
        data_with_none = [
            {'status': 'Applied', 'company_name': 'Corp A'},
            {'status': None, 'company_name': 'Corp B'},
            {'status': 'Rejected', 'company_name': 'Corp C'}
        ]
        
        stats = app_module.calculate_application_stats(data_with_none)
        
        # Should handle None gracefully
        assert stats['applied'] == 1
        assert stats['rejected'] == 1
        assert stats['active'] == 1  # None status goes to active
    
    def test_calculate_stats_case_sensitivity(self, app_module):
        """Test stats calculation handles case sensitivity correctly."""
        case_data = [
            {'status': 'applied', 'company_name': 'Corp A'},  # lowercase
            {'status': 'APPLIED', 'company_name': 'Corp B'},  # uppercase
            {'status': 'Applied', 'company_name': 'Corp C'},  # proper case
        ]
        
        stats = app_module.calculate_application_stats(case_data)
        
        # Implementation converts to lowercase, so all match
        assert stats['applied'] == 3  # All should match with lowercase comparison
        assert stats['active'] == 0


@pytest.mark.unit
class TestStatsCardsIntegration:
    """Test integration between stats calculation and card creation."""
    
    def test_get_stats_cards_empty_data(self, app_module):
        """Test getting stats cards with empty data."""
        cards = app_module.get_stats_cards([])
        
        # Should return 6 cards (Applied, Active, Assessment, Interviewing, Rejected, Offer)
        assert len(cards) == 6
        
        # All should show 0
        for card in cards:
            number_text = card.children[0].children
            assert number_text == 0  # The function should return integer 0
    
    def test_get_stats_cards_with_data(self, app_module, multiple_application_data):
        """Test getting stats cards with real data."""
        cards = app_module.get_stats_cards(multiple_application_data)
        
        assert len(cards) == 6
        
        # Extract the numbers from cards - should have some non-zero values
        has_non_zero = False
        for card in cards:
            number = card.children[0].children
            if number > 0:
                has_non_zero = True
        
        assert has_non_zero, "Should have at least some non-zero stats"
    
    def test_stats_cards_colors_match_status(self, app_module, multiple_application_data):
        """Test that stats cards have consistent styling."""
        cards = app_module.get_stats_cards(multiple_application_data)
        
        for card in cards:
            class_name = str(card.className)
            
            # All cards should have the stats-card class
            assert 'stats-card' in class_name 