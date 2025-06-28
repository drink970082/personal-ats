# ATS Dashboard Test Suite

A comprehensive testing framework for the ATS (Applicant Tracking System) Dashboard using modern testing tools and best practices.

## 🏗️ Test Architecture

The test suite is organized into focused, maintainable modules:

```
tests/
├── unit/                    # Unit tests for core functionality
│   ├── test_filtering_pagination.py  # Filtering and pagination logic
│   └── test_stats_cards.py          # Statistics calculation and cards
├── integration/             # Integration tests between components
│   └── test_component_integration.py # Cross-component testing
├── database/                # Database layer tests
│   └── test_data_service.py         # In-memory SQLite testing
├── callbacks/               # Dash callback tests
│   └── test_dash_callbacks.py       # Callback context mocking
├── e2e/                     # End-to-end tests
│   └── test_playwright_e2e.py       # Playwright browser automation
└── conftest.py              # Shared fixtures and configuration
```

## 🧪 Testing Technologies

- **pytest**: Core testing framework with advanced fixtures
- **Playwright**: Modern E2E browser automation (replacing Selenium)
- **In-memory SQLite**: Fast, isolated database testing
- **Dash Testing**: Official callback context mocking
- **Coverage.py**: Code coverage analysis
- **pytest-xdist**: Parallel test execution

## 🚀 Quick Start

### Install Dependencies

```bash
# Install test dependencies
python run_organized_tests.py --install-deps

# Or manually
pip install -r requirements-test.txt
playwright install chromium
```

### Run All Tests

```bash
# Simple run
pytest

# Using the test runner
python run_organized_tests.py
```

## 📋 Test Categories

### Unit Tests (`pytest -m unit`)

Fast, isolated tests for core business logic:

- **Filtering Logic**: Status, category, and search filtering
- **Pagination Logic**: Page navigation, bounds checking, size changes
- **Stats Calculation**: Application statistics and KPI generation
- **Edge Cases**: Empty data, malformed inputs, boundary conditions

```bash
# Run only unit tests
python run_organized_tests.py --type unit
```

### Integration Tests (`pytest -m integration`)

Test interactions between system components:

- **Data Service Integration**: Database operations with application logic
- **Filter-Pagination Integration**: Combined filtering and pagination
- **Stats Integration**: Real-time statistics with data changes
- **Error Handling**: Cross-component error propagation

```bash
# Run integration tests
python run_organized_tests.py --type integration
```

### Database Tests (`pytest -m database`)

In-memory SQLite testing for data persistence:

- **CRUD Operations**: Create, read, update, delete applications
- **Status History**: Automatic status change tracking
- **Data Validation**: SQL injection protection, unicode handling
- **Performance**: Bulk operations, large dataset handling
- **Concurrency**: Thread-safe database operations

```bash
# Run database tests
python run_organized_tests.py --type database
```

### Callback Tests (`pytest -m callbacks`)

Dash callback testing with proper context mocking:

- **Form Callbacks**: Application form submission and validation
- **Filter Callbacks**: Dynamic filtering and search functionality
- **Status Update Callbacks**: Application status changes with context
- **Stats Callbacks**: Real-time statistics updates
- **Error Handling**: Graceful callback error recovery

```bash
# Run callback tests
python run_organized_tests.py --type callbacks
```

### End-to-End Tests (`pytest -m e2e`)

Full browser automation with Playwright:

- **Application Management**: Complete CRUD workflows
- **User Interface**: Form interactions, table operations
- **Filtering & Pagination**: Real user filtering scenarios
- **Responsive Design**: Mobile, tablet, desktop viewports
- **Performance**: Large dataset handling, rapid interactions
- **Accessibility**: Keyboard navigation, screen reader compatibility

```bash
# Run E2E tests
python run_organized_tests.py --type e2e
```

## ⚡ Running Specific Test Types

### Fast Tests (Skip E2E and Slow)
```bash
python run_organized_tests.py --type fast
```

### Slow/Performance Tests
```bash
python run_organized_tests.py --type slow
```

### Parallel Execution
```bash
python run_organized_tests.py --parallel
```

### With Coverage Report
```bash
python run_organized_tests.py --coverage
```

### Comprehensive Report
```bash
python run_organized_tests.py --report
```

## 🔧 Test Configuration

### pytest.ini
```ini
[tool:pytest]
testpaths = tests
markers =
    unit: Unit tests for core functionality
    integration: Integration tests between components
    e2e: End-to-end tests with browser automation
    database: Database layer tests
    callbacks: Dash callback tests
    slow: Tests that take longer to run
    requires_browser: Tests that require a browser
```

### Fixtures Overview

Key shared fixtures in `conftest.py`:

- `in_memory_db`: SQLite in-memory database for testing
- `data_service`: DataService with mocked database connection
- `sample_application_data`: Single application test data
- `multiple_application_data`: Multiple applications for complex testing
- `populated_data_service`: Pre-populated database for integration tests

## 📊 Key Features

### In-Memory Database Testing
- **Fast**: No file I/O, tests run in microseconds
- **Isolated**: Each test gets a fresh database
- **Realistic**: Uses actual SQLite, not mocks
- **Concurrent**: Thread-safe test execution

### Playwright E2E Testing
- **Modern**: Latest browser automation technology
- **Reliable**: Auto-waiting, stable element selection
- **Fast**: Parallel browser contexts
- **Cross-Platform**: Chromium, Firefox, WebKit support

### Dash Callback Testing
- **Official**: Uses Dash's recommended testing approach
- **Context Aware**: Proper callback context mocking
- **Realistic**: Tests actual callback functions
- **Error Handling**: Validates error scenarios

## 🎯 Test Markers

Use pytest markers to run specific test subsets:

```bash
# Run only fast tests
pytest -m "not slow and not e2e"

# Run database and integration tests
pytest -m "database or integration"

# Run everything except E2E
pytest -m "not e2e"

# Run only browser-requiring tests
pytest -m requires_browser
```

## 📈 Coverage and Reporting

### Generate Coverage Report
```bash
pytest --cov=. --cov-report=html --cov-report=term
```

### View HTML Coverage Report
```bash
open htmlcov/index.html
```

### Generate Comprehensive Test Report
```bash
pytest --html=test_report.html --self-contained-html
```

## 🐛 Debugging Tests

### Verbose Output
```bash
pytest -v
```

### Show Local Variables on Failure
```bash
pytest -l
```

### Stop on First Failure
```bash
pytest -x
```

### Run Specific Test
```bash
pytest tests/unit/test_filtering_pagination.py::TestFilteringLogic::test_status_filter_applied
```

### Debug with Print Statements
```bash
pytest -s  # Don't capture stdout
```

## 🔍 Test Data Management

### Sample Data Fixtures
The test suite includes realistic sample data:

- **Multiple Categories**: SWE, DS, MLE, Quant roles
- **Various Statuses**: Applied through Offer/Rejected
- **Realistic Companies**: Tech, Data, ML, Finance companies
- **Edge Cases**: Unicode, special characters, long strings

### Dynamic Test Data
Tests generate data dynamically for:

- Performance testing (100+ applications)
- Pagination testing (specific page boundaries)
- Filtering testing (known filter results)
- Concurrent testing (thread-safe operations)

## 🚀 Performance Optimization

### Parallel Test Execution
```bash
pip install pytest-xdist
pytest -n auto  # Use all CPU cores
```

### Fast Test Selection
```bash
# Skip slow tests during development
pytest -m "not slow"
```

### In-Memory Database Benefits
- 10-100x faster than file-based testing
- No test cleanup required
- Perfect test isolation
- Concurrent test execution

## 🔒 Security Testing

The test suite includes security validations:

- **SQL Injection Protection**: Malicious input handling
- **Input Sanitization**: XSS prevention testing
- **Data Validation**: Type and range checking
- **Unicode Handling**: International character support

## 📝 Adding New Tests

### Unit Test Template
```python
@pytest.mark.unit
class TestNewFeature:
    def test_basic_functionality(self, app_module):
        # Test basic functionality
        result = app_module.new_function()
        assert result is not None
    
    def test_edge_cases(self, app_module):
        # Test edge cases
        result = app_module.new_function(edge_case_input)
        assert result == expected_output
```

### Integration Test Template
```python
@pytest.mark.integration
class TestNewIntegration:
    def test_component_interaction(self, data_service, app_module):
        # Test interaction between components
        data_service.add_application(test_data)
        result = app_module.process_data()
        assert result['success'] is True
```

### E2E Test Template
```python
@pytest.mark.e2e
@pytest.mark.requires_browser
class TestNewE2EFeature:
    def test_user_workflow(self, page: Page):
        page.goto("http://localhost:8050")
        # Test user interactions
        page.click("#new-feature-button")
        expect(page.locator("#result")).to_be_visible()
```

## 🏆 Best Practices

1. **Test Isolation**: Each test should be independent
2. **Descriptive Names**: Test names should explain what they test
3. **Single Responsibility**: One assertion per test when possible
4. **Realistic Data**: Use realistic test data
5. **Performance Aware**: Mark slow tests appropriately
6. **Error Scenarios**: Test both success and failure cases
7. **Documentation**: Comment complex test logic

## 🚨 Continuous Integration

For CI/CD pipelines:

```bash
# Install dependencies
python run_organized_tests.py --install-deps

# Run fast tests first
python run_organized_tests.py --type fast

# Run full suite with coverage
python run_organized_tests.py --report

# Upload coverage to CI
pytest --cov=. --cov-report=xml
```

## 💡 Tips and Tricks

### Speed Up E2E Tests
- Use `page.wait_for_timeout()` sparingly
- Prefer `expect().to_be_visible()` over manual waits
- Run E2E tests in parallel contexts
- Use headless mode in CI

### Debug Database Tests
- Print SQL queries for complex operations
- Use temporary files for debugging persistent state
- Check foreign key constraints
- Validate data types and constraints

### Optimize Callback Tests
- Mock external dependencies
- Use proper context setup
- Test both success and error paths
- Validate return value structures

## 📞 Support

For questions about the test suite:

1. Check existing test examples
2. Review pytest documentation
3. Consult Playwright guides for E2E issues
4. Check Dash testing documentation for callback issues

The test suite is designed to be comprehensive, maintainable, and fast. Happy testing! 🎉 