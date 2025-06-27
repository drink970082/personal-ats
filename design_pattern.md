# ATS
## core workflow
1. The user is presented with a dashboard showing their applications in a table and various summary charts.
2. They can add a new application via a form.
3. They can edit the status or notes of an application directly within the main table.
4. They can delete applications.
5. They can view a detailed status change history for each application in a pop-up modal, and can also edit or delete these history entries.
6. All actions update the database and dynamically refresh the UI components (table, charts, KPIs) to reflect the new state.

## Database models and schemas
```sql
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
```
* Category should be either one as follow:
    * SWE
    * MLE
    * DS
    * DA
    * Quant Dev
    * Quant Analyst
    * Qunat Trader
    * AI Engineer
    * Others
* status should be either one as follow: 
    * Applied (default options)
    * Online Assessment
    * Interviewing: 1st round
    * Interviewing: 2nd round
    * Interviewing: 3rd round
    * Interviewing: 4th round
    * Interviewing: 5th round
    * Rejected
    * Offer
* No duplicate record (use company_name+job title as primary key)

## Components
* application form: fields for Company, Title, URL, Date, Category, and Notes.
    * Category is a `select`
    * Notes should be `textarea`
    * Date is a `input <type='date'>`
    * All fields except notes should be `required`
* table: main interactive data table that displays the list of all job applications. It dynamically creates dropdowns for status, text areas for notes, and buttons for "Delete" and "History" on each row.
    * When clicking 'History': a `dbc.model` will showup, this contains status history of an application, users can edit or delete the status history, and also modify notes
    * Each row's `status` are modificable. `status` should always reflect the latest status and prevent dublicates
    * Each `status` should have dots on the left with different color to display their status group (like interviewing, online assessment, applied, etc)
* KPI: a numeric statistics, totaling 6 number, considering each application's latest status
    * Applied: total number of applications
    * Active: total number of applications excluding "rejectd"/"offered" status
    * Online Assessment: total number of applications having "Online Assessment" status
    * Interviewing: total number of applications having any "Interviewing" status
    * Rejected: total number of applications having "rejected" status
    * Offered: total number of applications having "Offered status
* Charts: visualizations of applications
    * Sankey chart: use application's status history to draw. When an application has only "Applied" in history, its outflow node is default "No Response"
    * Timeline: a calendar heatmap like Github contribution calendar, showing apply frequency of each day in previous 365 days. it should consider month split (when a week across 2 different months) and year split (when a week across 2 different years)
    * category: a donut chart representing proportions of application category
* notifications: when delete, update, add records, a toast message will show up and notify users
