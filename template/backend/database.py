"""Database module for ATS application."""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
import pandas as pd


class DatabaseManager:
    """Manages SQLite database operations for the ATS application."""
    
    def __init__(self, db_path: str = "ats.db"):
        """Initialize database manager with connection."""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn
    
    def init_database(self) -> None:
        """Initialize database tables."""
        with self.get_connection() as conn:
            # Applications table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS applications (
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
                )
            ''')
            
            # Status history table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS status_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(application_id) REFERENCES applications(id)
                )
            ''')
            
            conn.commit()
    
    def add_application(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new application with automatic status history."""
        try:
            with self.get_connection() as conn:
                # Check for duplicates
                existing = conn.execute(
                    "SELECT id FROM applications WHERE company_name = ? AND job_title = ?",
                    (data['company_name'], data['job_title'])
                ).fetchone()
                
                if existing:
                    return {"success": False, "error": "Application already exists"}
                
                # Insert application
                cursor = conn.execute('''
                    INSERT INTO applications 
                    (company_name, job_title, application_url, date_applied, category, status, notes, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['company_name'],
                    data['job_title'],
                    data.get('application_url', ''),
                    data['date_applied'],
                    data.get('category', 'Others'),
                    data.get('status', 'Applied'),
                    data.get('notes', ''),
                    datetime.now().isoformat()
                ))
                
                app_id = cursor.lastrowid
                
                # Add initial status history
                conn.execute('''
                    INSERT INTO status_history (application_id, status, timestamp)
                    VALUES (?, ?, ?)
                ''', (app_id, data.get('status', 'Applied'), datetime.now().isoformat()))
                
                conn.commit()
                return {"success": True, "id": app_id}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_applications(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get applications with optional filtering."""
        query = "SELECT * FROM applications WHERE 1=1"
        params = []
        
        if filters:
            if filters.get('status'):
                query += " AND status = ?"
                params.append(filters['status'])
            if filters.get('category'):
                query += " AND category = ?"
                params.append(filters['category'])
            if filters.get('search'):
                query += " AND (company_name LIKE ? OR job_title LIKE ?)"
                search_term = f"%{filters['search']}%"
                params.extend([search_term, search_term])
        
        query += " ORDER BY date_applied DESC"
        
        with self.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
    
    def update_application(self, app_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update application and add status history if status changed."""
        try:
            with self.get_connection() as conn:
                # Get current application
                current = conn.execute(
                    "SELECT * FROM applications WHERE id = ?", (app_id,)
                ).fetchone()
                
                if not current:
                    return {"success": False, "error": "Application not found"}
                
                # Update application
                conn.execute('''
                    UPDATE applications 
                    SET company_name = ?, job_title = ?, application_url = ?, 
                        date_applied = ?, category = ?, status = ?, notes = ?, last_updated = ?
                    WHERE id = ?
                ''', (
                    data.get('company_name', current['company_name']),
                    data.get('job_title', current['job_title']),
                    data.get('application_url', current['application_url']),
                    data.get('date_applied', current['date_applied']),
                    data.get('category', current['category']),
                    data.get('status', current['status']),
                    data.get('notes', current['notes']),
                    datetime.now().isoformat(),
                    app_id
                ))
                
                # Add status history if status changed
                if data.get('status') and data['status'] != current['status']:
                    conn.execute('''
                        INSERT INTO status_history (application_id, status, timestamp)
                        VALUES (?, ?, ?)
                    ''', (app_id, data['status'], datetime.now().isoformat()))
                
                conn.commit()
                return {"success": True}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_application(self, app_id: int) -> Dict[str, Any]:
        """Delete application and its status history."""
        try:
            with self.get_connection() as conn:
                # Delete status history first (foreign key constraint)
                conn.execute("DELETE FROM status_history WHERE application_id = ?", (app_id,))
                
                # Delete application
                cursor = conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
                
                if cursor.rowcount == 0:
                    return {"success": False, "error": "Application not found"}
                
                conn.commit()
                return {"success": True}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_status_history(self, app_id: int) -> List[Dict[str, Any]]:
        """Get status history for an application."""
        with self.get_connection() as conn:
            rows = conn.execute('''
                SELECT * FROM status_history 
                WHERE application_id = ? 
                ORDER BY timestamp DESC
            ''', (app_id,)).fetchall()
            return [dict(row) for row in rows]
    
    def get_all_status_history(self) -> List[Dict[str, Any]]:
        """Get all status history for all applications (for Sankey chart)."""
        with self.get_connection() as conn:
            rows = conn.execute('''
                SELECT * FROM status_history 
                ORDER BY application_id, timestamp
            ''').fetchall()
            return [dict(row) for row in rows]
    
    def update_status_history(self, history_id: int, status: str) -> Dict[str, Any]:
        """Update a status history entry."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "UPDATE status_history SET status = ? WHERE id = ?",
                    (status, history_id)
                )
                
                if cursor.rowcount == 0:
                    return {"success": False, "error": "History entry not found"}
                
                conn.commit()
                return {"success": True}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_status_history(self, history_id: int) -> Dict[str, Any]:
        """Delete a status history entry and auto-delete application if no status remains."""
        try:
            with self.get_connection() as conn:
                # Get the application_id before deleting
                history_entry = conn.execute(
                    "SELECT application_id FROM status_history WHERE id = ?", 
                    (history_id,)
                ).fetchone()
                
                if not history_entry:
                    return {"success": False, "error": "History entry not found"}
                
                app_id = history_entry['application_id']
                
                # Delete the status history entry
                cursor = conn.execute("DELETE FROM status_history WHERE id = ?", (history_id,))
                
                if cursor.rowcount == 0:
                    return {"success": False, "error": "History entry not found"}
                
                # Check if this application has any remaining status history
                remaining_history = conn.execute(
                    "SELECT COUNT(*) as count FROM status_history WHERE application_id = ?",
                    (app_id,)
                ).fetchone()
                
                if remaining_history['count'] == 0:
                    # No status history remains, delete the application
                    conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
                    conn.commit()
                    return {
                        "success": True, 
                        "message": "Status deleted. Application auto-deleted since no status history remains.",
                        "application_deleted": True
                    }
                else:
                    # Update application status to most recent status in history
                    latest_status = conn.execute('''
                        SELECT status FROM status_history 
                        WHERE application_id = ? 
                        ORDER BY timestamp DESC 
                        LIMIT 1
                    ''', (app_id,)).fetchone()
                    
                    if latest_status:
                        conn.execute(
                            "UPDATE applications SET status = ?, last_updated = ? WHERE id = ?",
                            (latest_status['status'], datetime.now().isoformat(), app_id)
                        )
                
                conn.commit()
                return {"success": True, "message": "Status history entry deleted successfully"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_kpi_data(self) -> Dict[str, int]:
        """Calculate KPI statistics."""
        with self.get_connection() as conn:
            # Get all applications
            apps = conn.execute("SELECT status FROM applications").fetchall()
            
            if not apps:
                return {
                    "applied": 0,
                    "active": 0,
                    "online_assessment": 0,
                    "interviewing": 0,
                    "rejected": 0,
                    "offered": 0
                }
            
            statuses = [app['status'] for app in apps]
            
            return {
                "applied": len(statuses),
                "active": len([s for s in statuses if s not in ['Rejected', 'Offer']]),
                "online_assessment": len([s for s in statuses if s == 'Online Assessment']),
                "interviewing": len([s for s in statuses if 'Interviewing' in s]),
                "rejected": len([s for s in statuses if s == 'Rejected']),
                "offered": len([s for s in statuses if s == 'Offer'])
            }
    
    def get_chart_data(self) -> Dict[str, Any]:
        """Get data for charts (timeline, category, status flow)."""
        with self.get_connection() as conn:
            # Applications data
            apps = conn.execute("SELECT * FROM applications").fetchall()
            applications_data = [dict(app) for app in apps]
            
            # Status history data
            history = conn.execute("SELECT * FROM status_history").fetchall()
            status_history_data = [dict(h) for h in history]
            
            return {
                "applications": applications_data,
                "status_history": status_history_data
            } 