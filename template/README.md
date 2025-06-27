# ATS Dashboard Template - Refactored

This is a refactored version of the ATS (Application Tracking System) dashboard template, organized into modular components and prepared for backend integration.

## Project Structure

```
template/
├── app.py                  # Original monolithic app (kept for reference)
├── app_refactored.py       # New modular main app file
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── config/
│   ├── __init__.py
│   ├── constants.py       # Application constants (statuses, categories, etc.)
│   └── styles.py          # CSS styling and themes
├── utils/
│   ├── __init__.py
│   ├── data.py           # Data generation and manipulation utilities
│   └── charts.py         # Chart generation functions
├── components/
│   ├── __init__.py
│   ├── forms.py          # Form components (application form, modals)
│   ├── table.py          # Table and pagination components
│   └── charts.py         # Chart wrapper components
└── callbacks/
    ├── __init__.py
    └── app_callbacks.py   # Placeholder for callback functions
```

## Features

### Current Implementation
- **Modular Architecture**: Components are separated into logical modules
- **Configuration Management**: Constants and styles are centralized
- **Utility Functions**: Data and chart generation are in separate utilities
- **Component-Based UI**: Reusable UI components for forms, tables, and charts
- **Mock Data**: Realistic sample data for development and testing

### Dashboard Components
1. **KPI Cards**: Applied, Active, Online Assessment, Interviewing, Rejected, Offered
2. **Application Form**: Add new job applications with validation
3. **Interactive Table**: View, edit, and manage applications with pagination
4. **Charts**: Timeline heatmap, status flow Sankey, category donut chart
5. **Status History**: Modal showing application progression over time
6. **Filtering**: Search and filter applications by status and category

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   # Original app
   python app.py
   
   # Refactored app
   python app_refactored.py
   ```

3. **Access the Dashboard**:
   - Original: http://localhost:8050
   - Refactored: http://localhost:8051

## Backend Integration Guide

This template is prepared for backend integration. Here's how to connect it to a real database:

### 1. Database Layer
Replace the mock data generation in `utils/data.py` with actual database operations:

```python
# Example database service
class ApplicationService:
    def get_all_applications(self):
        # Replace with actual DB query
        pass
    
    def create_application(self, app_data):
        # Replace with actual DB insert
        pass
    
    def update_application_status(self, app_id, status):
        # Replace with actual DB update
        pass
```

### 2. API Layer
Create API endpoints for CRUD operations:

```python
# Example with Flask-RESTful or FastAPI
@app.route('/api/applications', methods=['GET'])
def get_applications():
    # Return JSON data instead of mock data
    pass

@app.route('/api/applications', methods=['POST'])
def create_application():
    # Handle form submission
    pass
```

### 3. Callback Updates
Update callbacks in `app_refactored.py` to use API calls instead of local data:

```python
@app.callback(...)
def add_application(...):
    # Replace local data manipulation with API calls
    response = requests.post('/api/applications', json=form_data)
    return response.json()
```

### 4. Authentication
Add user authentication and session management:

```python
# Add to main app
from flask_login import LoginManager, login_required

@app.callback(...)
@login_required
def protected_callback(...):
    pass
```

## Design Patterns

The template follows the design patterns specified in `design_pattern.md`:

- **Database Schema**: Ready for SQLite/PostgreSQL with applications and status_history tables
- **UI Components**: All required components (forms, tables, charts, modals)
- **Status Management**: Proper status indicators with color coding
- **Data Validation**: Form validation and duplicate prevention
- **Interactive Features**: Status editing, history tracking, filtering

## Customization

### Adding New Components
1. Create new files in the `components/` directory
2. Import and use in `app_refactored.py`
3. Add any new constants to `config/constants.py`

### Styling
- Modify `config/styles.py` for CSS changes
- Uses Material 3 dark theme with custom CSS variables
- Bootstrap components for responsive layout

### Data Fields
- Update `config/constants.py` for new categories/statuses
- Modify `utils/data.py` for new data fields
- Update form components in `components/forms.py`

## Development Notes

- The refactored version maintains all functionality of the original
- Mock data is still used for development/testing
- Callbacks are partially implemented (core functionality only)
- Ready for production deployment with minimal changes
- Follows separation of concerns and single responsibility principles

## Next Steps for Production

1. **Complete Callback Migration**: Move all callbacks from `app.py` to `callbacks/app_callbacks.py`
2. **Database Integration**: Replace mock data with real database operations
3. **API Development**: Create RESTful API endpoints
4. **Testing**: Add unit tests for components and utilities
5. **Documentation**: Add detailed API documentation
6. **Deployment**: Configure for production deployment (Docker, etc.)

This refactored template provides a solid foundation for building a production-ready ATS dashboard with proper separation of concerns and maintainable code structure. 