import sqlite3
import pandas as pd
from datetime import datetime
from config.settings import DATABASE_PATH
from database.models import APPLICATIONS_TABLE_SCHEMA, STATUS_HISTORY_TABLE_SCHEMA
from utils.logger import logger, log_database_error

class DatabaseManager:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(APPLICATIONS_TABLE_SCHEMA)
        cursor.execute(STATUS_HISTORY_TABLE_SCHEMA)
        conn.commit()
        conn.close()
    
    def get_applications(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM applications ORDER BY id DESC", conn)
        conn.close()
        return df
    
    def add_application(self, company, title, url, date_applied, status, category, notes):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO applications (company_name, job_title, application_url, date_applied, status, category, notes, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (company, title, url, date_applied, status, category, notes, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            app_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info("database", "add_application", {
                "app_id": app_id,
                "company": company,
                "title": title,
                "status": status
            })
            return app_id
        except Exception as e:
            log_database_error("add_application", e, {
                "company": company,
                "title": title
            })
            raise
    
    def update_application(self, id, field, value):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f'UPDATE applications SET {field} = ?, last_updated = ? WHERE id = ?', 
                           (value, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id))
            conn.commit()
            conn.close()
            
            logger.info("database", "update_application", {
                "app_id": id,
                "field": field,
                "value": value
            })
        except Exception as e:
            log_database_error("update_application", e, {
                "app_id": id,
                "field": field,
                "value": value
            })
            raise
    
    def delete_application(self, id):
        try:
            # Get application details before deletion for logging
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT company_name, job_title FROM applications WHERE id = ?', (id,))
            app_details = cursor.fetchone()
            
            cursor.execute('DELETE FROM applications WHERE id = ?', (id,))
            conn.commit()
            conn.close()
            
            if app_details:
                logger.info("database", "delete_application", {
                    "app_id": id,
                    "company": app_details[0],
                    "title": app_details[1]
                })
        except Exception as e:
            log_database_error("delete_application", e, {"app_id": id})
            raise
    
    def get_status_counts(self):
        df = self.get_applications()
        return {status: len(df[df['status'] == status]) for status in ['Applied', 'Online Assessment', 'Interviewing', 'Rejected', 'No Response', 'Offer']}
    
    def get_category_counts(self):
        df = self.get_applications()
        return df['category'].value_counts().to_dict()
    
    def get_timeline_data(self):
        df = self.get_applications()
        if df.empty:
            return []
        df['date_applied'] = pd.to_datetime(df['date_applied'])
        timeline_data = df.groupby(df['date_applied'].dt.to_period('W')).size().reset_index()
        timeline_data.columns = ['week', 'count']
        timeline_data['week'] = timeline_data['week'].astype(str)
        return timeline_data.to_dict('records')

    def log_status_change(self, application_id, status, timestamp=None):
        try:
            if timestamp is None:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO status_history (application_id, status, timestamp)
                VALUES (?, ?, ?)
            ''', (application_id, status, timestamp))
            conn.commit()
            conn.close()
            
            logger.info("database", "log_status_change", {
                "app_id": application_id,
                "status": status,
                "timestamp": timestamp
            })
        except Exception as e:
            log_database_error("log_status_change", e, {
                "app_id": application_id,
                "status": status
            })
            raise

    def get_status_history(self, application_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, status, timestamp FROM status_history WHERE application_id = ? ORDER BY timestamp ASC
        ''', (application_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def delete_status_history(self, history_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM status_history WHERE id = ?', (history_id,))
        conn.commit()
        conn.close()

    def check_duplicate_application(self, company, title):
        """Check if an application already exists for the same company and job title"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, company_name, job_title, date_applied, status 
            FROM applications 
            WHERE LOWER(company_name) = LOWER(?) AND LOWER(job_title) = LOWER(?)
        ''', (company, title))
        existing = cursor.fetchone()
        conn.close()
        return existing

    def auto_update_no_response(self):
        """Update status to 'No Response' for applications older than 30 days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE applications 
                SET status = 'No Response', last_updated = ?
                WHERE status = 'Applied' 
                AND date_applied < date('now', '-30 days')
            ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
            updated_count = cursor.rowcount
            
            # Get the IDs of updated applications
            updated_apps = []
            if updated_count > 0:
                cursor.execute('''
                    SELECT id FROM applications 
                    WHERE status = 'No Response' 
                    AND last_updated = ?
                ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
                updated_apps = [row[0] for row in cursor.fetchall()]
            
            conn.commit()
            conn.close()
            
            # Log status changes for updated applications using separate connection
            for app_id in updated_apps:
                self.log_status_change(app_id, "No Response")
            
            logger.info("database", "auto_update_no_response", {
                "updated_count": updated_count,
                "updated_apps": updated_apps
            })
            
            return updated_count
        except Exception as e:
            log_database_error("auto_update_no_response", e)
            raise 