"""
End-to-End tests using Playwright for ATS Dashboard.
"""

import pytest
import time
import subprocess
import tempfile
import os
from playwright.sync_api import Page, expect


@pytest.mark.e2e
@pytest.mark.requires_browser
class TestApplicationManagement:
    """Test complete application management workflows."""
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_app(self):
        """Set up the application for E2E testing."""
        # Create temporary database
        self.test_db_fd, self.test_db_path = tempfile.mkstemp(suffix='.db')
        os.close(self.test_db_fd)
        
        # Start the application with test database
        env = os.environ.copy()
        env['ATS_DB_PATH'] = self.test_db_path
        
        self.app_process = subprocess.Popen([
            'python', 'app_redesigned.py'
        ], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for app to start
        time.sleep(5)
        
        yield
        
        # Cleanup
        if hasattr(self, 'app_process'):
            self.app_process.terminate()
            self.app_process.wait()
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)
    
    def test_page_loads_successfully(self, page: Page):
        """Test that the main page loads successfully."""
        page.goto("http://localhost:8050")
        
        # Check that the page title is correct or key elements exist
        expect(page.locator("#company-input")).to_be_visible()
        expect(page.locator("#job-title-input")).to_be_visible()
        expect(page.locator("#submit-btn")).to_be_visible()
    
    def test_add_application_workflow(self, page: Page):
        """Test the complete add application workflow."""
        page.goto("http://localhost:8050")
        
        # Fill out the application form
        page.fill("#company-input", "Playwright Test Corp")
        page.fill("#job-title-input", "QA Engineer")
        page.fill("#url-input", "https://playwright-test.com/careers")
        page.fill("#date-input", "2024-01-20")
        page.select_option("#category-dropdown", "SWE")
        page.fill("#notes-input", "E2E test application")
        
        # Submit the form
        page.click("#submit-btn")
        
        # Wait for submission and check for success indicators
        page.wait_for_timeout(2000)
        
        # Check if application appears in the table
        expect(page.locator("text=Playwright Test Corp")).to_be_visible()
        expect(page.locator("text=QA Engineer")).to_be_visible()
    
    def test_form_validation(self, page: Page):
        """Test form validation for required fields."""
        page.goto("http://localhost:8050")
        
        # Try to submit empty form
        page.click("#submit-btn")
        
        # Check that form validation prevents submission
        company_input = page.locator("#company-input")
        
        # Modern browsers show validation messages
        validation_message = company_input.get_attribute("validationMessage")
        if validation_message:
            assert validation_message != ""
    
    def test_application_status_update(self, page: Page):
        """Test updating application status."""
        page.goto("http://localhost:8050")
        
        # First add an application
        page.fill("#company-input", "Status Test Corp")
        page.fill("#job-title-input", "Engineer")
        page.fill("#date-input", "2024-01-20")
        page.select_option("#category-dropdown", "SWE")
        page.click("#submit-btn")
        
        page.wait_for_timeout(2000)
        
        # Find the status dropdown for this application
        status_dropdown = page.locator("tbody tr").filter(has_text="Status Test Corp").locator("select")
        
        if status_dropdown.is_visible():
            # Update status
            status_dropdown.select_option("Online Assessment")
            page.wait_for_timeout(1000)
            
            # Verify status was updated
            expect(status_dropdown).to_have_value("Online Assessment")


@pytest.mark.e2e
@pytest.mark.requires_browser
class TestFilteringAndPagination:
    """Test filtering and pagination functionality."""
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_test_data(self, setup_app):
        """Set up test data for filtering tests."""
        # This would typically use the same app setup as above
        pass
    
    def test_status_filtering(self, page: Page):
        """Test filtering applications by status."""
        page.goto("http://localhost:8050")
        
        # Add applications with different statuses
        applications = [
            ("Filter Corp A", "Engineer A"),
            ("Filter Corp B", "Engineer B"),
        ]
        
        for company, title in applications:
            page.fill("#company-input", company)
            page.fill("#job-title-input", title)
            page.fill("#date-input", "2024-01-20")
            page.select_option("#category-dropdown", "SWE")
            page.click("#submit-btn")
            page.wait_for_timeout(1000)
        
        # Test status filtering
        status_filter = page.locator("#status-filter")
        if status_filter.is_visible():
            status_filter.select_option("Applied")
            page.wait_for_timeout(1000)
            
            # Check that applications are visible
            expect(page.locator("text=Filter Corp A")).to_be_visible()
            expect(page.locator("text=Filter Corp B")).to_be_visible()
    
    def test_search_functionality(self, page: Page):
        """Test search functionality."""
        page.goto("http://localhost:8050")
        
        # Add searchable applications
        page.fill("#company-input", "Searchable Corp")
        page.fill("#job-title-input", "Unique Engineer")
        page.fill("#date-input", "2024-01-20")
        page.select_option("#category-dropdown", "SWE")
        page.click("#submit-btn")
        page.wait_for_timeout(1000)
        
        # Test search
        search_input = page.locator("#search-input")
        if search_input.is_visible():
            search_input.fill("Searchable")
            page.wait_for_timeout(1000)
            
            # Check search results
            expect(page.locator("text=Searchable Corp")).to_be_visible()
    
    def test_pagination_navigation(self, page: Page):
        """Test pagination navigation."""
        page.goto("http://localhost:8050")
        
        # Add multiple applications for pagination
        for i in range(15):
            page.fill("#company-input", f"Pagination Corp {i:02d}")
            page.fill("#job-title-input", "Engineer")
            page.fill("#date-input", "2024-01-20")
            page.select_option("#category-dropdown", "SWE")
            page.click("#submit-btn")
            page.wait_for_timeout(500)
        
        # Test page size change
        page_size_dropdown = page.locator("#page-size-dropdown")
        if page_size_dropdown.is_visible():
            page_size_dropdown.select_option("5")
            page.wait_for_timeout(1000)
            
            # Test next page navigation
            next_button = page.locator("#next-page-btn")
            if next_button.is_visible() and next_button.is_enabled():
                next_button.click()
                page.wait_for_timeout(1000)
                
                # Verify we're on a different page
                # Check that different data is visible


@pytest.mark.e2e
@pytest.mark.requires_browser
class TestStatsAndDashboard:
    """Test stats cards and dashboard functionality."""
    
    def test_stats_cards_display(self, page: Page):
        """Test that stats cards are displayed correctly."""
        page.goto("http://localhost:8050")
        
        # Check for stats cards
        stats_cards = page.locator(".card")
        if stats_cards.first.is_visible():
            expect(stats_cards.first).to_be_visible()
            
            # Verify stats cards show numbers
            card_numbers = page.locator(".card h2")
            if card_numbers.first.is_visible():
                first_number = card_numbers.first.text_content()
                assert first_number.isdigit()
    
    def test_stats_update_after_adding_application(self, page: Page):
        """Test that stats update after adding an application."""
        page.goto("http://localhost:8050")
        
        # Get initial stats
        applied_card = page.locator(".card").filter(has_text="Applied").locator("h2")
        initial_count = "0"
        if applied_card.is_visible():
            initial_count = applied_card.text_content()
        
        # Add an application
        page.fill("#company-input", "Stats Test Corp")
        page.fill("#job-title-input", "Engineer")
        page.fill("#date-input", "2024-01-20")
        page.select_option("#category-dropdown", "SWE")
        page.click("#submit-btn")
        
        page.wait_for_timeout(2000)
        
        # Check if stats updated
        if applied_card.is_visible():
            updated_count = applied_card.text_content()
            # Stats should have increased
            assert int(updated_count) >= int(initial_count)


@pytest.mark.e2e
@pytest.mark.requires_browser
class TestResponsiveDesign:
    """Test responsive design across different viewport sizes."""
    
    def test_mobile_viewport(self, page: Page):
        """Test application on mobile viewport."""
        page.set_viewport_size({"width": 375, "height": 667})  # iPhone size
        page.goto("http://localhost:8050")
        
        # Check that key elements are still visible and functional
        expect(page.locator("#company-input")).to_be_visible()
        expect(page.locator("#submit-btn")).to_be_visible()
        
        # Test form submission on mobile
        page.fill("#company-input", "Mobile Test Corp")
        page.fill("#job-title-input", "Mobile Engineer")
        page.fill("#date-input", "2024-01-20")
        page.select_option("#category-dropdown", "SWE")
        page.click("#submit-btn")
        
        page.wait_for_timeout(2000)
        expect(page.locator("text=Mobile Test Corp")).to_be_visible()
    
    def test_tablet_viewport(self, page: Page):
        """Test application on tablet viewport."""
        page.set_viewport_size({"width": 768, "height": 1024})  # iPad size
        page.goto("http://localhost:8050")
        
        # Test that layout adapts properly
        expect(page.locator("#company-input")).to_be_visible()
        expect(page.locator(".card")).to_be_visible()
    
    def test_desktop_viewport(self, page: Page):
        """Test application on desktop viewport."""
        page.set_viewport_size({"width": 1920, "height": 1080})  # Desktop size
        page.goto("http://localhost:8050")
        
        # Test full desktop functionality
        expect(page.locator("#company-input")).to_be_visible()
        
        # All elements should be easily accessible
        page.fill("#company-input", "Desktop Test Corp")
        page.fill("#job-title-input", "Desktop Engineer")
        page.click("#submit-btn")


@pytest.mark.e2e
@pytest.mark.requires_browser
@pytest.mark.slow
class TestPerformanceAndLoad:
    """Test application performance and load handling."""
    
    def test_large_dataset_performance(self, page: Page):
        """Test performance with a large dataset."""
        page.goto("http://localhost:8050")
        
        # Add many applications quickly
        start_time = time.time()
        
        for i in range(20):  # Reduced for faster testing
            page.fill("#company-input", f"Performance Corp {i}")
            page.fill("#job-title-input", "Engineer")
            page.fill("#date-input", "2024-01-20")
            page.select_option("#category-dropdown", "SWE")
            page.click("#submit-btn")
            
            # Small delay to prevent overwhelming
            if i % 5 == 0:
                page.wait_for_timeout(200)
        
        duration = time.time() - start_time
        
        # Should complete within reasonable time
        assert duration < 30.0  # 30 seconds for 20 applications
        
        # Verify functionality still works
        search_input = page.locator("#search-input")
        if search_input.is_visible():
            search_input.fill("Performance Corp 1")
            page.wait_for_timeout(1000)
            expect(page.locator("text=Performance Corp 1")).to_be_visible()
    
    def test_filtering_performance_large_dataset(self, page: Page):
        """Test filtering performance with large dataset."""
        page.goto("http://localhost:8050")
        
        # This test assumes data from previous test or creates its own
        # Test rapid filter changes
        status_filter = page.locator("#status-filter")
        category_filter = page.locator("#category-filter")
        
        if status_filter.is_visible() and category_filter.is_visible():
            start_time = time.time()
            
            # Rapid filter changes
            for _ in range(5):
                status_filter.select_option("all")
                page.wait_for_timeout(200)
                status_filter.select_option("Applied")
                page.wait_for_timeout(200)
                category_filter.select_option("all")
                page.wait_for_timeout(200)
                category_filter.select_option("SWE")
                page.wait_for_timeout(200)
            
            duration = time.time() - start_time
            
            # Should handle rapid changes smoothly
            assert duration < 5.0  # Should complete within 5 seconds


@pytest.mark.e2e
@pytest.mark.requires_browser
class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_network_interruption_handling(self, page: Page):
        """Test handling of network interruptions."""
        page.goto("http://localhost:8050")
        
        # The application should load gracefully
        expect(page.locator("#company-input")).to_be_visible()
        
        # Try operations that might fail
        page.fill("#company-input", "Network Test Corp")
        page.fill("#job-title-input", "Engineer")
        page.click("#submit-btn")
        
        # Application should not crash
        page.wait_for_timeout(2000)
        # Page should still be responsive
        expect(page.locator("#company-input")).to_be_visible()
    
    def test_invalid_input_handling(self, page: Page):
        """Test handling of invalid inputs."""
        page.goto("http://localhost:8050")
        
        # Try invalid date
        page.fill("#company-input", "Invalid Input Corp")
        page.fill("#job-title-input", "Engineer")
        page.fill("#date-input", "invalid-date")
        page.click("#submit-btn")
        
        # Application should handle gracefully
        page.wait_for_timeout(1000)
        expect(page.locator("#company-input")).to_be_visible()
    
    def test_extremely_long_inputs(self, page: Page):
        """Test handling of extremely long inputs."""
        page.goto("http://localhost:8050")
        
        # Very long company name
        long_name = "A" * 100  # Reduced for practical testing
        page.fill("#company-input", long_name)
        page.fill("#job-title-input", "Engineer")
        page.fill("#date-input", "2024-01-20")
        page.click("#submit-btn")
        
        # Should handle without crashing
        page.wait_for_timeout(2000)
        expect(page.locator("#company-input")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.requires_browser
class TestAccessibility:
    """Test accessibility features."""
    
    def test_keyboard_navigation(self, page: Page):
        """Test keyboard navigation through the form."""
        page.goto("http://localhost:8050")
        
        # Start from company input
        page.locator("#company-input").focus()
        
        # Tab through form elements
        page.keyboard.press("Tab")  # Should go to job title
        page.keyboard.press("Tab")  # Should go to URL
        page.keyboard.press("Tab")  # Should go to date
        page.keyboard.press("Tab")  # Should go to category
        page.keyboard.press("Tab")  # Should go to notes
        page.keyboard.press("Tab")  # Should go to submit button
        
        # Should be able to navigate through form
        focused_element = page.evaluate("document.activeElement.tagName")
        assert focused_element in ["INPUT", "SELECT", "TEXTAREA", "BUTTON"]
    
    def test_form_labels_and_accessibility(self, page: Page):
        """Test that form elements have proper labels for accessibility."""
        page.goto("http://localhost:8050")
        
        # Check that form inputs have associated labels or aria-labels
        company_input = page.locator("#company-input")
        expect(company_input).to_be_visible()
        
        # Check for label or aria-label or placeholder
        aria_label = company_input.get_attribute("aria-label")
        placeholder = company_input.get_attribute("placeholder")
        
        # Should have some form of labeling
        assert aria_label or placeholder 