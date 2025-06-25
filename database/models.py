# Database models and schemas

APPLICATIONS_TABLE_SCHEMA = '''
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT NOT NULL,
        job_title TEXT NOT NULL,
        application_url TEXT,
        date_applied TEXT NOT NULL,
        category TEXT,
        status TEXT NOT NULL,
        notes TEXT,
        last_updated TEXT
    )
'''

STATUS_HISTORY_TABLE_SCHEMA = '''
    CREATE TABLE IF NOT EXISTS status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY(application_id) REFERENCES applications(id)
    )
''' 