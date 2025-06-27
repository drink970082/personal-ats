"""Data service layer for ATS application."""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from .database import DatabaseManager


class DataService:
    """Service layer for data operations and business logic."""
    
    def __init__(self, db_path: str = "ats.db"):
        """Initialize data service with database manager."""
        self.db = DatabaseManager(db_path)
    
    def add_application(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add new application with enhanced validation."""
        # Validate required fields
        required_fields = ['company_name', 'job_title', 'date_applied']
        for field in required_fields:
            if not form_data.get(field) or str(form_data.get(field)).strip() == '':
                field_names = {
                    'company_name': 'Company Name',
                    'job_title': 'Job Title', 
                    'date_applied': 'Date Applied'
                }
                return {"success": False, "error": f"{field_names[field]} is required"}
        
        # Validate category
        valid_categories = [
            'SWE', 'MLE', 'DS', 'DA', 'Quant Dev', 
            'Quant Analyst', 'Quant Trader', 'AI Engineer', 'Others'
        ]
        if form_data.get('category') and form_data['category'] not in valid_categories:
            return {"success": False, "error": f"Invalid category. Must be one of: {', '.join(valid_categories)}"}
        
        # Validate status
        valid_statuses = [
            'Applied', 'Online Assessment', 'Interviewing: 1st round',
            'Interviewing: 2nd round', 'Interviewing: 3rd round',
            'Interviewing: 4th round', 'Interviewing: 5th round',
            'Rejected', 'Offer'
        ]
        if form_data.get('status') and form_data['status'] not in valid_statuses:
            return {"success": False, "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}
        
        # Validate date format
        try:
            if form_data.get('date_applied'):
                datetime.fromisoformat(form_data['date_applied'])
        except:
            return {"success": False, "error": "Invalid date format. Please use YYYY-MM-DD format"}
        
        # Set defaults
        form_data.setdefault('status', 'Applied')
        form_data.setdefault('category', 'Others')
        form_data.setdefault('notes', '')
        
        # Attempt to add application (this will check for duplicates in database layer)
        result = self.db.add_application(form_data)
        
        if result['success']:
            return {"success": True, "message": f"Application for {form_data['company_name']} - {form_data['job_title']} added successfully"}
        else:
            # Enhanced duplicate error message
            if "already exists" in result.get('error', ''):
                return {"success": False, "error": f"Application for {form_data['company_name']} - {form_data['job_title']} already exists"}
            return result
    
    def get_applications_table_data(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get applications data formatted for the table component."""
        applications = self.db.get_applications(filters)
        
        # Add additional formatting for table display
        for app in applications:
            # Format date for display
            if app['date_applied']:
                try:
                    date_obj = datetime.fromisoformat(app['date_applied'])
                    app['date_applied_formatted'] = date_obj.strftime('%Y-%m-%d')
                except:
                    app['date_applied_formatted'] = app['date_applied']
            
            # Add status category for color coding
            app['status_category'] = self._get_status_category(app['status'])
            
            # Truncate long notes for table display
            if app['notes'] and len(app['notes']) > 100:
                app['notes_preview'] = app['notes'][:100] + "..."
            else:
                app['notes_preview'] = app['notes'] or ""
        
        return applications
    
    def update_application_status(self, app_id: int, new_status: str) -> Dict[str, Any]:
        """Update application status with validation and duplicate prevention."""
        valid_statuses = [
            'Applied', 'Online Assessment', 'Interviewing: 1st round',
            'Interviewing: 2nd round', 'Interviewing: 3rd round',
            'Interviewing: 4th round', 'Interviewing: 5th round',
            'Rejected', 'Offer'
        ]
        
        if new_status not in valid_statuses:
            return {"success": False, "error": "Invalid status"}
        
        # Get current application to check for duplicate status
        try:
            applications = self.db.get_applications()
            current_app = next((app for app in applications if app['id'] == app_id), None)
            
            if not current_app:
                return {"success": False, "error": "Application not found"}
            
            # Check if status is the same as current status
            if current_app['status'] == new_status:
                return {"success": False, "error": f"Application is already in '{new_status}' status"}
            
            # Update status in database
            result = self.db.update_application(app_id, {"status": new_status})
            
            if result['success']:
                return {"success": True, "message": f"Status updated to '{new_status}'"}
            else:
                return result
                
        except Exception as e:
            return {"success": False, "error": f"Failed to update status: {str(e)}"}
    
    def update_application_notes(self, app_id: int, notes: str) -> Dict[str, Any]:
        """Update application notes."""
        return self.db.update_application(app_id, {"notes": notes})
    
    def get_kpi_data(self) -> Dict[str, int]:
        """Get KPI data for dashboard cards."""
        return self.db.get_kpi_data()
    
    def get_chart_data(self) -> Dict[str, Any]:
        """Get comprehensive chart data for all visualizations."""
        raw_data = self.db.get_chart_data()
        
        return {
            "applications": raw_data["applications"],
            "status_history": raw_data["status_history"],
            "timeline_data": self._prepare_timeline_data(raw_data["applications"]),
            "category_data": self._prepare_category_data(raw_data["applications"]),
            "sankey_data": self._prepare_sankey_data(raw_data["applications"], raw_data["status_history"]),
            "status_distribution": self._prepare_status_distribution(raw_data["applications"])
        }
    
    def get_application_history(self, app_id: int) -> Dict[str, Any]:
        """Get application details with full status history."""
        # Get application details
        applications = self.db.get_applications()
        application = next((app for app in applications if app['id'] == app_id), None)
        
        if not application:
            return {"success": False, "error": "Application not found"}
        
        # Get status history
        history = self.db.get_status_history(app_id)
        
        # Format history for display
        for entry in history:
            try:
                timestamp = datetime.fromisoformat(entry['timestamp'])
                # Create a more human-readable format
                entry['timestamp_formatted'] = timestamp.strftime('%b %d, %Y at %I:%M %p')
            except:
                entry['timestamp_formatted'] = entry['timestamp']
            
            entry['status_category'] = self._get_status_category(entry['status'])
        
        return {
            "success": True,
            "application": application,
            "history": history
        }
    
    def _get_status_category(self, status: str) -> str:
        """Get status category for color coding."""
        if status == 'Applied':
            return 'applied'
        elif status == 'Online Assessment':
            return 'assessment'
        elif 'Interviewing' in status:
            return 'interviewing'
        elif status == 'Rejected':
            return 'rejected'
        elif status == 'Offer':
            return 'offer'
        else:
            return 'other'
    
    def _prepare_timeline_data(self, applications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare data for timeline heatmap chart."""
        timeline_data = []
        
        for app in applications:
            try:
                date_obj = datetime.fromisoformat(app['date_applied'])
                timeline_data.append({
                    'date': date_obj.strftime('%Y-%m-%d'),
                    'count': 1,
                    'applications': [app['company_name']]
                })
            except:
                continue
        
        # Aggregate by date
        date_counts = {}
        for entry in timeline_data:
            date = entry['date']
            if date in date_counts:
                date_counts[date]['count'] += entry['count']
                date_counts[date]['applications'].extend(entry['applications'])
            else:
                date_counts[date] = entry
        
        return list(date_counts.values())
    
    def _prepare_category_data(self, applications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare data for category donut chart."""
        category_counts = {}
        
        for app in applications:
            category = app.get('category', 'Others')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return [
            {"category": category, "count": count}
            for category, count in category_counts.items()
        ]
    
    def _prepare_status_distribution(self, applications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare data for status distribution chart."""
        status_counts = {}
        
        for app in applications:
            status = app.get('status', 'Applied')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return [
            {"status": status, "count": count}
            for status, count in status_counts.items()
        ]
    
    def _prepare_sankey_data(self, applications: List[Dict[str, Any]], status_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare data for Sankey diagram in the format expected by the original chart function."""
        import pandas as pd
        
        # Create DataFrame from status history
        if not status_history:
            return []
        
        df_history = pd.DataFrame(status_history)
        
        # Create next_status column for transitions
        df_history['next_status'] = df_history.groupby('application_id')['status'].shift(-1)
        
        # Count transitions between statuses
        transitions = (
            df_history.dropna(subset=['next_status'])
            .groupby(['status', 'next_status'])
            .size()
            .reset_index(name='value')
        )
        
        # Add "No Response" for applications that only have "Applied" status
        app_status_counts = df_history.groupby('application_id')['status'].count()
        applied_only_apps = app_status_counts[app_status_counts == 1].index
        
        if len(applied_only_apps) > 0:
            applied_only_history = df_history[
                df_history['application_id'].isin(applied_only_apps) & 
                (df_history['status'] == 'Applied')
            ]
            
            if len(applied_only_history) > 0:
                no_response_data = pd.DataFrame([{
                    'status': 'Applied',
                    'next_status': 'No Response', 
                    'value': len(applied_only_history)
                }])
                
                transitions = pd.concat([transitions, no_response_data], ignore_index=True)
                transitions = transitions.groupby(['status', 'next_status'], as_index=False).sum()
        
        return transitions.to_dict('records')
    
    def search_applications(self, search_term: str) -> List[Dict[str, Any]]:
        """Search applications by company name or job title."""
        filters = {"search": search_term}
        return self.get_applications_table_data(filters)
    
    def get_applications_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get applications filtered by status."""
        filters = {"status": status}
        return self.get_applications_table_data(filters)
    
    def get_applications_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get applications filtered by category."""
        filters = {"category": category}
        return self.get_applications_table_data(filters)
    
    def get_sankey_data(self):
        """Get Sankey chart data - EXACTLY matching original app.py logic."""
        try:
            # Get all status history
            history_data = self.db.get_all_status_history()
            
            if not history_data:
                return []
            
            import pandas as pd
            
            # Create DataFrame exactly like original
            # history_data is already a list of dictionaries, so we can use it directly
            df_history = pd.DataFrame([
                {
                    'app_id': record['application_id'],  # use key instead of index
                    'status': record['status'],  # use key instead of index
                    'timestamp': record['timestamp']  # use key instead of index
                }
                for record in history_data
            ])
            
            # Sort by application and timestamp to ensure correct order
            df_history = df_history.sort_values(['app_id', 'timestamp'])
            
            # Calculate status transitions for Sankey diagram (EXACT ORIGINAL LOGIC)
            df_history["next_status"] = df_history.groupby("app_id")["status"].shift(-1)
            sankey_data = (
                df_history.dropna(subset=["next_status"])
                .groupby(["status", "next_status"])
                .size()
                .reset_index(name="value")
            )

            # Add "No Response" for apps stuck in "Applied" for Sankey (EXACT ORIGINAL LOGIC)
            app_status_counts = df_history.groupby("app_id")["status"].count()
            applied_only_apps = app_status_counts[app_status_counts == 1].index
            applied_only_apps = df_history[
                df_history["app_id"].isin(applied_only_apps) & (df_history["status"] == "Applied")
            ]["app_id"].unique()

            if len(applied_only_apps) > 0:
                no_response_rows = [{"status": "Applied", "next_status": "No Response", "value": 1}]
                sankey_data = (
                    pd.concat([sankey_data, pd.DataFrame(no_response_rows * len(applied_only_apps))])
                    .groupby(["status", "next_status"], as_index=False)
                    .sum()
                )
            
            # Convert to list of dictionaries
            return sankey_data.to_dict('records')
            
        except Exception as e:
            print(f"Error in get_sankey_data: {e}")
            return []
    
    def get_application_by_id(self, app_id: int) -> Optional[Dict[str, Any]]:
        """Get a single application by ID."""
        applications = self.db.get_applications()
        return next((app for app in applications if app['id'] == app_id), None)
    
    def delete_status_history(self, history_id: int) -> Dict[str, Any]:
        """Delete a status history entry."""
        try:
            # Get the history entry to check if it exists
            history_data = self.db.get_all_status_history()
            history_entry = next((h for h in history_data if h['id'] == history_id), None)
            
            if not history_entry:
                return {"success": False, "error": "History entry not found"}
            
            app_id = history_entry['application_id']
            
            # Delete the history entry
            result = self.db.delete_status_history(history_id)
            
            if result['success']:
                # Check if application still has history entries
                remaining_history = self.db.get_status_history(app_id)
                
                if not remaining_history:
                    # If no history remains, delete the application
                    self.db.delete_application(app_id)
                    print(f"Application {app_id} auto-deleted due to no remaining history")
                else:
                    # Update application status to the latest in history
                    latest_status = max(remaining_history, key=lambda x: x['timestamp'])['status']
                    self.db.update_application(app_id, {'status': latest_status})
                    print(f"Application {app_id} status updated to latest: {latest_status}")
                
                return {"success": True}
            else:
                return result
                
        except Exception as e:
            print(f"Error deleting status history: {str(e)}")
            return {"success": False, "error": str(e)} 