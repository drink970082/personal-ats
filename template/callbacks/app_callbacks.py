"""Main application callbacks connecting backend to frontend."""

import json
from typing import Dict, Any, List, Tuple
import dash
from dash import Input, Output, State, callback_context, no_update, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import datetime

from backend.data_service import DataService
from utils.charts import create_sankey_chart, create_timeline_heatmap, create_category_donut, create_status_distribution
from utils.data import calculate_kpis
# from components.forms import create_history_modal_content  # Function doesn't exist


class AppCallbacks:
    """Handles all application callbacks."""
    
    def __init__(self, app, data_service: DataService):
        """Initialize callbacks with app and data service."""
        self.app = app
        self.data_service = data_service
        self.register_callbacks()
    
    def register_callbacks(self):
        """Register all callback functions."""
        self.register_form_callbacks()
        self.register_table_callbacks()
        self.register_chart_callbacks()
        self.register_kpi_callbacks()
        self.register_modal_callbacks()
        self.register_filter_callbacks()
        self.register_pagination_callbacks()
    
    def register_form_callbacks(self):
        """Register form-related callbacks."""
        
        @self.app.callback(
            [Output('notification-container', 'children'),
             Output('company-input', 'value'),
             Output('title-input', 'value'),
             Output('url-input', 'value'),
             Output('date-input', 'value'),
             Output('category-input', 'value'),
             Output('notes-input', 'value'),
             Output('applications-table', 'children', allow_duplicate=True)],
            [Input('submit-button', 'n_clicks')],
            [State('company-input', 'value'),
             State('title-input', 'value'),
             State('url-input', 'value'),
             State('date-input', 'value'),
             State('category-input', 'value'),
             State('notes-input', 'value')],
            prevent_initial_call=True
        )
        def handle_form_submission(n_clicks, company, title, url, date, category, notes):
            """Handle new application form submission with table refresh."""
            if not n_clicks:
                return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
            
            # Validate required fields
            if not company or not title or not date:
                notification = dbc.Toast(
                    "Please fill in all required fields",
                    header="Error",
                    icon="danger",
                    duration=4000,
                    is_open=True,
                    style={
                        'position': 'fixed',
                        'bottom': '20px',
                        'right': '20px',
                        'z-index': '9999',
                        'background-color': 'rgba(220, 53, 69, 0.95)',
                        'border': '1px solid rgba(220, 53, 69, 0.2)',
                        'color': 'white',
                        'backdrop-filter': 'blur(8px)'
                    }
                )
                return notification, no_update, no_update, no_update, no_update, no_update, no_update, no_update
            
            # Prepare form data
            form_data = {
                'company_name': company,
                'job_title': title,
                'application_url': url or '',
                'date_applied': date,
                'category': category or 'Others',
                'notes': notes or ''
            }
            
            # Add application
            result = self.data_service.add_application(form_data)
            
            if result['success']:
                notification = dbc.Toast(
                    result.get('message', 'Application added successfully!'),
                    header="Success",
                    icon="success",
                    duration=3000,
                    is_open=True,
                    style={
                        'position': 'fixed',
                        'bottom': '20px',
                        'right': '20px',
                        'z-index': '9999',
                        'background-color': 'rgba(25, 135, 84, 0.95)',
                        'border': '1px solid rgba(25, 135, 84, 0.2)',
                        'color': 'white',
                        'backdrop-filter': 'blur(8px)'
                    }
                )
                
                # Get updated table content
                from components.table import create_applications_table
                all_applications = self.data_service.get_applications_table_data()
                
                # Use current pagination state if available
                page_size = int(getattr(self, '_page_size', 10))
                current_page = int(getattr(self, '_current_page', 0))
                
                updated_table = create_applications_table(
                    all_applications, 
                    page_size=page_size,
                    page_current=current_page,
                    filters=None
                )
                
                # Clear form and return updated table
                return notification, '', '', '', datetime.now().date().isoformat(), 'Others', '', updated_table
            else:
                notification = dbc.Toast(
                    result.get('error', 'Failed to add application'),
                    header="Error",
                    icon="danger",
                    duration=4000,
                    is_open=True,
                    style={
                        'position': 'fixed',
                        'bottom': '20px',
                        'right': '20px',
                        'z-index': '9999',
                        'background-color': 'rgba(220, 53, 69, 0.95)',
                        'border': '1px solid rgba(220, 53, 69, 0.2)',
                        'color': 'white',
                        'backdrop-filter': 'blur(8px)'
                    }
                )
                return notification, no_update, no_update, no_update, no_update, no_update, no_update, no_update
    
    def register_table_callbacks(self):
        """Register table-related callbacks."""
        @self.app.callback(
            Output('applications-table', 'children'),
            [Input('submit-button', 'n_clicks'),  # Form submission
             Input({'type': 'status-dropdown', 'index': dash.dependencies.ALL}, 'value'),
             Input({'type': 'delete-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
             Input('status-filter', 'value'),
             Input('category-filter', 'value'),
             Input('search-input', 'value'),
             Input('prev-page-button', 'n_clicks'),
             Input('next-page-button', 'n_clicks'),
             Input({'type': 'page-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
             Input('page-size-select', 'value')],
            prevent_initial_call=False
        )
        def update_applications_table(form_submit, status_values, delete_clicks, 
                                    status_filter, category_filter, search_input,
                                    prev_click, next_click, page_clicks, page_size_value):
            """Handle table updates: data changes, filtering, and pagination."""
            ctx = callback_context
            
            # Initialize pagination state
            if not hasattr(self, '_current_page'):
                self._current_page = 0
            if not hasattr(self, '_page_size'):
                self._page_size = 10
            
            # Ensure page_size is always an integer
            self._page_size = int(self._page_size) if self._page_size else 10
            self._current_page = int(self._current_page) if self._current_page else 0
            
            # Handle page size changes
            if page_size_value and int(page_size_value) != self._page_size:
                self._page_size = int(page_size_value)
                self._current_page = 0  # Reset to first page
            
            # Handle pagination clicks
            if ctx.triggered:
                trigger_id = ctx.triggered[0]['prop_id']
                
                # Handle page navigation
                if 'prev-page-button' in trigger_id and prev_click:
                    self._current_page = max(0, self._current_page - 1)
                elif 'next-page-button' in trigger_id and next_click:
                    # We'll validate max page later after getting data
                    self._current_page += 1
                elif 'page-button' in trigger_id and any(page_clicks):
                    # Find which page button was clicked
                    for i, clicks in enumerate(page_clicks):
                        if clicks:
                            try:
                                page_info = json.loads(trigger_id.split('.')[0])
                                self._current_page = page_info['index']
                                break
                            except:
                                pass
                
                # Handle filter changes - reset to page 0
                elif any(filt in trigger_id for filt in ['status-filter', 'category-filter', 'search-input']):
                    self._current_page = 0
            
            # Handle status updates and deletions first
            if ctx.triggered:
                for trigger in ctx.triggered:
                    prop_id = trigger['prop_id']
                    
                    # Handle status updates
                    if 'status-dropdown' in prop_id and trigger['value']:
                        try:
                            app_id = json.loads(prop_id.split('.')[0])['index']
                            new_status = trigger['value']
                            result = self.data_service.update_application_status(app_id, new_status)
                            
                            if not result['success']:
                                print(f"Status update failed: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            print(f"Error updating status: {str(e)}")
                    
                    # Handle deletions
                    elif 'delete-button' in prop_id and trigger['value']:
                        try:
                            app_id = json.loads(prop_id.split('.')[0])['index']
                            result = self.data_service.db.delete_application(app_id)
                            
                            if not result['success']:
                                print(f"Delete failed: {result.get('error', 'Unknown error')}")
                        except Exception as e:
                            print(f"Error deleting application: {str(e)}")
            
            # Build filters dictionary
            filters = {}
            if status_filter and status_filter != 'all':
                filters['status'] = status_filter
            if category_filter and category_filter != 'all':
                filters['category'] = category_filter
            if search_input:
                filters['search'] = search_input
            
            # Get all applications data
            all_applications = self.data_service.get_applications_table_data()
            
            # Apply filters to calculate filtered count for pagination validation
            filtered_data = all_applications
            if filters:
                if filters.get('status'):
                    filtered_data = [app for app in filtered_data if app['status'] == filters['status']]
                if filters.get('category'):
                    filtered_data = [app for app in filtered_data if app.get('category', 'Others') == filters['category']]
                if filters.get('search'):
                    search_term = filters['search'].lower().strip()
                    filtered_data = [app for app in filtered_data if 
                                   search_term in app['company_name'].lower() or 
                                   search_term in app['job_title'].lower()]
            
            # Validate current page against filtered data
            total_pages = max(1, (len(filtered_data) + self._page_size - 1) // self._page_size) if filtered_data else 1
            self._current_page = min(self._current_page, total_pages - 1)
            self._current_page = max(0, self._current_page)
            
            # Create table with proper pagination
            from components.table import create_applications_table
            table_content = create_applications_table(
                all_applications, 
                page_size=self._page_size,
                page_current=self._current_page,
                filters=filters
            )
            
            return table_content
    
    def register_chart_callbacks(self):
        """Register chart-related callbacks."""
        @self.app.callback(
            Output('analytics-charts', 'children'),
            [Input('applications-table', 'children'),
             Input('submit-button', 'n_clicks')]
        )
        def update_analytics_charts(table_children, submit_clicks):
            """Update all analytics charts when data changes (NOT when filters change)."""
            try:
                # Get ALL applications data (unfiltered for charts)
                applications_data = self.data_service.get_applications_table_data()
                
                # Get Sankey data using all data
                sankey_data = self.data_service.get_sankey_data()
                
                # Import charts section
                from components.charts import create_charts_section, create_empty_charts
                
                if not applications_data:
                    return create_empty_charts()
                
                # Create charts using ALL data (not filtered)
                return create_charts_section(applications_data, sankey_data)
                
            except Exception as e:
                print(f"Error updating analytics charts: {e}")
                from components.charts import create_empty_charts
                return create_empty_charts()
    
    def register_kpi_callbacks(self):
        """Register KPI card update callbacks."""
        @self.app.callback(
            [Output('kpi-card-applied', 'children'),
             Output('kpi-card-active', 'children'),
             Output('kpi-card-assessment', 'children'),
             Output('kpi-card-interviewing', 'children'),
             Output('kpi-card-rejected', 'children'),
             Output('kpi-card-offer', 'children')],
            [Input('applications-table', 'children'),
             Input('submit-button', 'n_clicks')]
        )
        def update_kpi_cards(table_children, submit_clicks):
            """Update all KPI cards when data changes (NOT when filters change)."""
            try:
                from components.forms import create_stats_card
                
                # Get KPI data from ALL applications (unfiltered)
                kpis = self.data_service.get_kpi_data()
                
                # Create KPI cards
                applied_card = create_stats_card(kpis.get('applied', 0), "Applied")
                active_card = create_stats_card(kpis.get('active', 0), "Active")
                assessment_card = create_stats_card(kpis.get('online_assessment', 0), "Online Assessment")
                interviewing_card = create_stats_card(kpis.get('interviewing', 0), "Interviewing")
                rejected_card = create_stats_card(kpis.get('rejected', 0), "Rejected")
                offer_card = create_stats_card(kpis.get('offered', 0), "Offer")
                
                return applied_card, active_card, assessment_card, interviewing_card, rejected_card, offer_card
                
            except Exception as e:
                print(f"Error updating KPI cards: {e}")
                from components.forms import create_stats_card
                empty_card = create_stats_card(0, "Error")
                return empty_card, empty_card, empty_card, empty_card, empty_card, empty_card
    
    def register_modal_callbacks(self):
        """Register modal-related callbacks."""
        @self.app.callback(
            [Output('status-history-modal', 'is_open'),
             Output('status-history-content', 'children'),
             Output('modal-notes-input', 'value'),
             Output('notification-container', 'children', allow_duplicate=True),
             Output('applications-table', 'children', allow_duplicate=True)],
            [Input({'type': 'history-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
             Input('close-modal-button', 'n_clicks')],
             [State('status-history-modal', 'is_open'),
              State('modal-notes-input', 'value')],
             prevent_initial_call=True
        )
        def handle_history_modal(history_clicks, close_click, is_open, current_notes):
            """Handle history modal open/close with auto-save on close."""
            ctx = callback_context
            
            if not ctx.triggered:
                return False, "", "", no_update, no_update
            
            trigger = ctx.triggered[0]
            
            # Close modal with auto-save
            if 'close-modal-button' in trigger['prop_id']:
                # Auto-save notes before closing
                app_id = getattr(self.data_service, '_current_modal_app_id', None)
                if app_id and current_notes is not None:
                    try:
                        result = self.data_service.update_application_notes(app_id, current_notes or '')
                        if result['success']:
                            notification = self.create_toast_notification(
                                "Notes saved successfully", 
                                "success"
                            )
                            
                            # Refresh table to show updated notes
                            all_applications = self.data_service.get_applications_table_data()
                            from components.table import create_applications_table
                            page_size = int(getattr(self, '_page_size', 10))
                            current_page = int(getattr(self, '_current_page', 0))
                            updated_table = create_applications_table(
                                all_applications, 
                                page_size=page_size,
                                page_current=current_page,
                                filters=None
                            )
                            
                            return False, "", "", notification, updated_table
                        else:
                            notification = self.create_toast_notification(
                                f"Failed to save notes: {result.get('error', 'Unknown error')}", 
                                "error"
                            )
                            return False, "", "", notification, no_update
                    except Exception as e:
                        notification = self.create_toast_notification(
                            f"Error saving notes: {str(e)}", 
                            "error"
                        )
                        return False, "", "", notification, no_update
                
                return False, "", "", no_update, no_update
            
            # Open modal with history data
            if 'history-button' in trigger['prop_id'] and trigger['value']:
                try:
                    # Extract app_id from prop_id
                    app_id = json.loads(trigger['prop_id'].split('.')[0])['index']
                    
                    # Get application history
                    history_data = self.data_service.get_application_history(app_id)
                    
                    if history_data['success']:
                        # Store app_id for later use in update callback
                        self.data_service._current_modal_app_id = app_id
                        
                        # Get application details for notes
                        app_data = self.data_service.get_application_by_id(app_id)
                        current_notes = app_data.get('notes', '') if app_data else ''
                        
                        # Create simple modal content since create_history_modal_content doesn't exist
                        from components.table import create_status_history_table
                        modal_content = create_status_history_table(
                            history_data['history'], 
                            app_id
                        )
                        return True, modal_content, current_notes, no_update, no_update
                    else:
                        return False, "", "", no_update, no_update
                except:
                    return False, "", "", no_update, no_update
            
            return is_open, no_update, no_update, no_update, no_update
        
        @self.app.callback(
            [Output('notification-container', 'children', allow_duplicate=True),
             Output('applications-table', 'children', allow_duplicate=True),
             Output('status-history-content', 'children', allow_duplicate=True),
             Output('status-history-modal', 'is_open', allow_duplicate=True)],
            [Input({'type': 'delete-history', 'index': dash.dependencies.ALL}, 'n_clicks')],
            prevent_initial_call=True
        )
        def handle_delete_history(delete_clicks):
            """Handle deletion of status history entries with immediate modal refresh."""
            ctx = callback_context
            
            if not ctx.triggered or not any(delete_clicks):
                return no_update, no_update, no_update, no_update
            
            trigger = ctx.triggered[0]
            
            if 'delete-history' in trigger['prop_id'] and trigger['value']:
                try:
                    # Extract history_id from prop_id
                    history_id = json.loads(trigger['prop_id'].split('.')[0])['index']
                    
                    # Get the app_id before deletion for modal refresh
                    app_id = getattr(self.data_service, '_current_modal_app_id', None)
                    
                    # Delete the history entry
                    result = self.data_service.delete_status_history(history_id)
                    
                    if result['success']:
                        # Create success notification
                        notification = self.create_toast_notification(
                            "Status history deleted successfully", 
                            "success"
                        )
                        
                        # Refresh table
                        applications_data = self.data_service.get_applications_table_data()
                        from components.table import create_applications_table
                        
                        # Use current pagination state if available
                        page_size = int(getattr(self, '_page_size', 10))
                        current_page = int(getattr(self, '_current_page', 0))
                        
                        table_content = create_applications_table(
                            applications_data, 
                            page_size=page_size,
                            page_current=current_page
                        )
                        
                        # Refresh modal content if app still exists
                        if app_id:
                            try:
                                updated_history = self.data_service.get_application_history(app_id)
                                if updated_history['success']:
                                    from components.table import create_status_history_table
                                    updated_modal_content = create_status_history_table(
                                        updated_history['history'], 
                                        app_id
                                    )
                                    return notification, table_content, updated_modal_content, no_update
                                else:
                                    # Application was deleted, auto-close modal
                                    return notification, table_content, html.P("Application deleted.", className="text-muted"), False
                            except:
                                # Application was deleted, auto-close modal
                                return notification, table_content, html.P("Application deleted.", className="text-muted"), False
                        
                        return notification, table_content, no_update, no_update
                    else:
                        # Create error notification
                        notification = self.create_toast_notification(
                            f"Failed to delete history: {result.get('error', 'Unknown error')}", 
                            "error"
                        )
                        return notification, no_update, no_update, no_update
                        
                except Exception as e:
                    print(f"Error deleting history: {str(e)}")
                    print(f"Debug info - app_id: {app_id}, history_id: {history_id}")
                    notification = self.create_toast_notification(
                        f"Error deleting history: {str(e)}", 
                        "error"
                    )
                    return notification, no_update, no_update, no_update
            
            return no_update, no_update, no_update, no_update
        


    def register_filter_callbacks(self):
        """Register filter-related callbacks."""
        # All filtering logic is now handled in the main table callback above
        pass

    def register_pagination_callbacks(self):
        """Register pagination-related callbacks."""
        # Pagination will be handled through a separate mechanism
        # Since the pagination components are dynamically created, we'll use
        # a different approach that doesn't reference them in the callback registration
        pass
    
    def create_toast_notification(self, message: str, notification_type: str = "success"):
        """Create a toast notification component."""
        import dash_bootstrap_components as dbc
        
        if notification_type == "success":
            return dbc.Toast(
                message,
                header="Success",
                icon="success",
                duration=3000,
                is_open=True,
                style={
                    'position': 'fixed',
                    'bottom': '20px',
                    'right': '20px',
                    'z-index': '9999',
                    'background-color': 'rgba(25, 135, 84, 0.95)',
                    'border': '1px solid rgba(25, 135, 84, 0.2)',
                    'color': 'white',
                    'backdrop-filter': 'blur(8px)'
                }
            )
        else:  # error
            return dbc.Toast(
                message,
                header="Error",
                icon="danger",
                duration=4000,
                is_open=True,
                style={
                    'position': 'fixed',
                    'bottom': '20px',
                    'right': '20px',
                    'z-index': '9999',
                    'background-color': 'rgba(220, 53, 69, 0.95)',
                    'border': '1px solid rgba(220, 53, 69, 0.2)',
                    'color': 'white',
                    'backdrop-filter': 'blur(8px)'
                }
            )


def register_callbacks(app):
    """Main function to register all callbacks with the app."""
    # Initialize data service
    data_service = DataService()
    
    # Initialize and register callbacks
    callbacks = AppCallbacks(app, data_service)
    
    return data_service  # Return for potential use in main app 