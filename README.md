# Personal Application Tracking System (ATS)

A single-page web application built with Dash for tracking job applications with analytics and visualizations.

## Project Structure

```
ats/
├── app.py              # Main application entry point
├── database.py         # Database operations and SQLite management
├── components.py       # UI components and layout functions
├── callbacks.py        # Dash callbacks and event handlers
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Features

- **New Application Entry**: Add applications with company, title, URL, date, status, category, and notes
- **Summary KPIs**: Real-time counts for each application status
- **Interactive Table**: Sort, filter, search, and edit applications inline
- **Analytics**: Status distribution, category distribution, and timeline charts
- **SQLite Database**: Local data storage with automatic schema creation

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open browser to `http://localhost:8050`

## Architecture

- **Frontend**: Dash components and layout
- **Backend**: SQLite database with pandas for data manipulation
- **Separation**: Clean separation between UI components, database operations, and callback logic

## Database Schema

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
    last_updated TEXT
);
```

## Usage

1. **Add Application**: Fill out the form at the top and click "Submit Application"
2. **View Summary**: See counts for each status in the KPI section
3. **Filter & Search**: Use the filters above the table to narrow results
4. **Edit**: Click on Status or Notes cells to edit inline
5. **Delete**: Click "Delete" in the Actions column
6. **Analytics**: View charts showing distribution and trends

## Status Options
- Applied
- Online Assessment  
- Interviewing
- Rejected
- Offer

## Categories
- SWE/SDE
- MLE
- Quant Analyst
- Quant Dev
- DS
- DA
- Others 