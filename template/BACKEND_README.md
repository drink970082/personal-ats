# ATS Backend Implementation

A modular backend implementation for the ATS (Application Tracking System) dashboard with SQLite database integration.

## Architecture Overview

The backend follows a layered architecture pattern:

```
Frontend (Dash Components)
    ↓
Callbacks Layer (app_callbacks.py)
    ↓
Service Layer (data_service.py)
    ↓
Database Layer (database.py)
    ↓
SQLite Database
```

## Directory Structure

```
backend/
├── __init__.py              # Package initialization
├── database.py              # Core database operations
├── data_service.py          # Business logic and data transformation
└── db_manager.py            # Database management utilities

callbacks/
└── app_callbacks.py         # Dash callback handlers

utils/
├── data.py                  # Data utilities and mock data generation
└── charts.py                # Chart generation functions
```

## Core Components

### 1. Database Layer (`database.py`)

The `DatabaseManager` class handles all direct database operations:

- **Schema Management**: Creates and maintains SQLite tables
- **CRUD Operations**: Create, Read, Update, Delete for applications and status history
- **Data Integrity**: Enforces foreign key constraints and duplicate prevention
- **Connection Management**: Handles SQLite connections with proper cleanup

Key methods:
- `add_application()` - Insert new application with status history
- `get_applications()` - Retrieve applications with optional filtering
- `update_application()` - Update application and track status changes
- `delete_application()` - Remove application and associated history
- `get_status_history()` - Retrieve complete status history for an application

### 2. Service Layer (`data_service.py`)

The `DataService` class provides business logic and data transformation:

- **Input Validation**: Validates form data against business rules
- **Data Formatting**: Prepares data for frontend consumption
- **Chart Data Preparation**: Transforms database data for visualizations
- **KPI Calculations**: Computes dashboard metrics
- **Search and Filtering**: Handles application search and status/category filtering

Key methods:
- `add_application()` - Validate and add new applications
- `get_applications_table_data()` - Format data for table display
- `get_chart_data()` - Prepare data for all chart types
- `get_kpi_data()` - Calculate dashboard KPIs
- `search_applications()` - Search by company/title

### 3. Callback Layer (`app_callbacks.py`)

The `AppCallbacks` class manages Dash callback functions:

- **Form Callbacks**: Handle form submissions and validation
- **Table Callbacks**: Manage table updates, pagination, and inline editing
- **Chart Callbacks**: Update visualizations when data changes
- **Modal Callbacks**: Handle history modal interactions
- **KPI Callbacks**: Update dashboard metrics

### 4. Database Management (`db_manager.py`)

Administrative utilities for database operations:

- **Backup/Restore**: Create and restore database backups
- **Data Seeding**: Populate database with mock data for testing
- **Statistics**: Generate database usage statistics
- **Export**: Export data to CSV format
- **Clear**: Clear all data with safety confirmations

## Database Schema

### Applications Table
```sql
CREATE TABLE applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    job_title TEXT NOT NULL,
    application_url TEXT,
    date_applied TEXT NOT NULL,
    category TEXT,
    status TEXT NOT NULL,
    notes TEXT,
    last_updated TEXT,
    UNIQUE(company_name, job_title)
);
```

### Status History Table
```sql
CREATE TABLE status_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY(application_id) REFERENCES applications(id)
);
```

## Business Rules

### Categories
- SWE, MLE, DS, DA, Quant Dev, Quant Analyst, Quant Trader, AI Engineer, Others

### Statuses
- Applied (default)
- Online Assessment
- Interviewing: 1st-5th round
- Rejected
- Offer

### Validation Rules
- Company name and job title are required
- No duplicate applications (same company + job title)
- Status changes are automatically tracked in history
- All status changes include timestamps

## API Overview

### Data Service Methods

#### Application Management
```python
# Add new application
result = data_service.add_application({
    'company_name': 'Google',
    'job_title': 'Software Engineer',
    'date_applied': '2024-01-15',
    'category': 'SWE',
    'notes': 'Applied through referral'
})

# Update application status
result = data_service.update_application_status(app_id, 'Interviewing: 1st round')

# Get applications with filtering
apps = data_service.get_applications_table_data(filters={'status': 'Applied'})
```

#### Chart Data
```python
# Get all chart data
chart_data = data_service.get_chart_data()
# Returns: {
#   'applications': [...],
#   'status_history': [...],
#   'timeline_data': [...],
#   'category_data': [...],
#   'sankey_data': {...},
#   'status_distribution': [...]
# }
```

#### KPI Data
```python
# Get dashboard KPIs
kpis = data_service.get_kpi_data()
# Returns: {
#   'applied': 50,
#   'active': 35,
#   'online_assessment': 8,
#   'interviewing': 12,
#   'rejected': 10,
#   'offered': 5
# }
```

## Database Management CLI

The backend includes a command-line interface for database management:

```bash
# Create database backup
python -m backend.db_manager backup

# Seed database with mock data
python -m backend.db_manager seed --num-apps 50

# View database statistics
python -m backend.db_manager stats

# Clear all data (with confirmation)
python -m backend.db_manager clear --confirm

# Export data to CSV
python -m backend.db_manager export

# Restore from backup
python -m backend.db_manager restore --backup-path backups/ats_backup_20240115.db
```

## Integration with Frontend

### Starting the Application
```python
# app_backend.py
from backend.data_service import DataService
from callbacks.app_callbacks import register_callbacks

# Initialize data service and register callbacks
data_service = register_callbacks(app)

# Optional auto-seeding for empty databases
if not data_service.get_applications_table_data():
    seed_database_with_mock_data(data_service, 25)
```

### Callback Integration
The callback system automatically:
- Refreshes charts when data changes
- Updates KPIs after form submissions
- Handles real-time table updates
- Manages modal interactions
- Provides user notifications

## Error Handling

The backend implements comprehensive error handling:

- **Database Errors**: Connection issues, constraint violations
- **Validation Errors**: Invalid form data, missing required fields
- **Business Logic Errors**: Duplicate applications, invalid status transitions
- **User Feedback**: Toast notifications for all operations

## Testing and Development

### Mock Data Generation
```python
from utils.data import seed_database_with_mock_data

# Generate realistic test data
seed_database_with_mock_data(data_service, num_applications=50)
```

### Database Statistics
```python
from backend.db_manager import DatabaseManager

db_manager = DatabaseManager()
stats = db_manager.get_database_stats()
print(f"Total applications: {stats['total_applications']}")
```

## Security Considerations

- **SQL Injection Prevention**: All queries use parameterized statements
- **Input Validation**: Comprehensive validation on all user inputs
- **Data Integrity**: Foreign key constraints and unique constraints
- **Backup Strategy**: Automatic backups before destructive operations

## Performance Optimization

- **Connection Pooling**: Efficient SQLite connection management
- **Query Optimization**: Indexed queries for filtering and search
- **Data Pagination**: Table pagination reduces memory usage
- **Lazy Loading**: Chart data prepared only when needed

## Future Enhancements

Potential backend improvements:
- PostgreSQL/MySQL support for production
- User authentication and authorization
- API rate limiting and caching
- Background job processing
- Data analytics and reporting
- Email notifications for status changes
- Integration with external job boards

## Dependencies

Core backend dependencies:
- `sqlite3` - Database operations
- `pandas` - Data manipulation
- `datetime` - Date/time handling
- `typing` - Type hints for better code quality

The backend is designed to be database-agnostic and can be easily extended to support other database systems in the future. 