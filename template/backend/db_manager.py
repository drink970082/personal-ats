"""Database management utilities for ATS application."""

import os
import sqlite3
import shutil
from datetime import datetime
from typing import Optional

from .database import DatabaseManager as DB
from .data_service import DataService
from utils.data import seed_database_with_mock_data


class DatabaseManager:
    """Database management utilities."""
    
    def __init__(self, db_path: str = "ats.db"):
        """Initialize database manager."""
        self.db_path = db_path
        self.backup_dir = "backups"
    
    def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Create a backup of the database."""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database file {self.db_path} not found")
        
        # Create backup directory if it doesn't exist
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Generate backup filename
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"ats_backup_{timestamp}.db"
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        # Copy database file
        shutil.copy2(self.db_path, backup_path)
        
        print(f"✅ Database backup created: {backup_path}")
        return backup_path
    
    def restore_backup(self, backup_path: str) -> None:
        """Restore database from backup."""
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file {backup_path} not found")
        
        # Create backup of current database before restore
        if os.path.exists(self.db_path):
            self.create_backup("pre_restore_backup.db")
        
        # Restore from backup
        shutil.copy2(backup_path, self.db_path)
        
        print(f"✅ Database restored from: {backup_path}")
    
    def clear_database(self, confirm: bool = False) -> None:
        """Clear all data from the database."""
        if not confirm:
            print("⚠️ This will delete ALL data. Use confirm=True to proceed.")
            return
        
        # Create backup before clearing
        self.create_backup("pre_clear_backup.db")
        
        # Clear tables
        db = DB(self.db_path)
        with db.get_connection() as conn:
            conn.execute("DELETE FROM status_history")
            conn.execute("DELETE FROM applications")
            conn.commit()
        
        print("✅ Database cleared successfully")
    
    def seed_database(self, num_applications: int = 25) -> None:
        """Seed database with mock data."""
        data_service = DataService(self.db_path)
        return seed_database_with_mock_data(data_service, num_applications)
    
    def get_database_stats(self) -> dict:
        """Get database statistics."""
        db = DB(self.db_path)
        
        with db.get_connection() as conn:
            app_count = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
            history_count = conn.execute("SELECT COUNT(*) FROM status_history").fetchone()[0]
            
            # Get status distribution
            status_dist = conn.execute("""
                SELECT status, COUNT(*) as count 
                FROM applications 
                GROUP BY status 
                ORDER BY count DESC
            """).fetchall()
            
            # Get category distribution
            category_dist = conn.execute("""
                SELECT category, COUNT(*) as count 
                FROM applications 
                GROUP BY category 
                ORDER BY count DESC
            """).fetchall()
        
        return {
            "total_applications": app_count,
            "total_history_entries": history_count,
            "status_distribution": dict(status_dist),
            "category_distribution": dict(category_dist),
            "database_size": os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        }
    
    def export_to_csv(self, output_dir: str = "exports") -> dict:
        """Export database tables to CSV files."""
        os.makedirs(output_dir, exist_ok=True)
        
        data_service = DataService(self.db_path)
        
        # Export applications
        applications = data_service.get_applications_table_data()
        apps_file = os.path.join(output_dir, f"applications_{datetime.now().strftime('%Y%m%d')}.csv")
        
        if applications:
            import pandas as pd
            df_apps = pd.DataFrame(applications)
            df_apps.to_csv(apps_file, index=False)
        
        # Export status history
        chart_data = data_service.get_chart_data()
        history_file = os.path.join(output_dir, f"status_history_{datetime.now().strftime('%Y%m%d')}.csv")
        
        if chart_data['status_history']:
            df_history = pd.DataFrame(chart_data['status_history'])
            df_history.to_csv(history_file, index=False)
        
        return {
            "applications_file": apps_file if applications else None,
            "history_file": history_file if chart_data['status_history'] else None
        }


def main():
    """Command-line interface for database management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ATS Database Management")
    parser.add_argument('command', choices=[
        'backup', 'restore', 'clear', 'seed', 'stats', 'export'
    ], help='Command to execute')
    
    parser.add_argument('--db-path', default='ats.db', help='Database file path')
    parser.add_argument('--backup-path', help='Backup file path (for restore)')
    parser.add_argument('--num-apps', type=int, default=25, help='Number of applications to seed')
    parser.add_argument('--confirm', action='store_true', help='Confirm destructive operations')
    
    args = parser.parse_args()
    
    db_manager = DatabaseManager(args.db_path)
    
    try:
        if args.command == 'backup':
            db_manager.create_backup()
        
        elif args.command == 'restore':
            if not args.backup_path:
                print("❌ --backup-path required for restore command")
                return
            db_manager.restore_backup(args.backup_path)
        
        elif args.command == 'clear':
            db_manager.clear_database(args.confirm)
        
        elif args.command == 'seed':
            db_manager.seed_database(args.num_apps)
        
        elif args.command == 'stats':
            stats = db_manager.get_database_stats()
            print(f"📊 Database Statistics:")
            print(f"   Applications: {stats['total_applications']}")
            print(f"   History Entries: {stats['total_history_entries']}")
            print(f"   Database Size: {stats['database_size']} bytes")
            print(f"   Status Distribution: {stats['status_distribution']}")
            print(f"   Category Distribution: {stats['category_distribution']}")
        
        elif args.command == 'export':
            files = db_manager.export_to_csv()
            print(f"📁 Exported data to:")
            if files['applications_file']:
                print(f"   Applications: {files['applications_file']}")
            if files['history_file']:
                print(f"   History: {files['history_file']}")
    
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    main() 