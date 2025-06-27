"""Main application file for the ATS Dashboard Template.

This is a refactored version that uses modular components and is ready for backend integration.
"""

import dash
from dash import dcc, html, Input, Output, State, callback, ALL, MATCH
import dash_bootstrap_components as dbc
from datetime import datetime
import pandas as pd

# Import our modular components
from config.constants import STATUSES, CATEGORIES
from config.styles import CUSTOM_CSS
from utils.data import generate_mock_data, generate_status_history, calculate_kpis, get_status_color_class
from utils.charts import create_timeline_heatmap, create_category_donut, create_sankey_chart
from components.forms import create_application_form, create_status_history_modal, create_kpi_cards, create_single_kpi_card
from components.table import create_applications_table, create_status_history_table
from components.charts import create_charts_section, create_empty_charts

# Initialize the Dash app
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)

# Set the custom HTML template
app.index_string = CUSTOM_CSS

# Global data stores (In production, these would be replaced with database calls)
applications_data = generate_mock_data(30)
status_history_data = generate_status_history(applications_data)

def create_layout():
    """Create the main layout of the application."""
    kpis = calculate_kpis(applications_data)
    
    return dbc.Container([
        # Header
        html.Div([
            html.H1("Modern ATS Dashboard", className="mb-1 text-center mt-4"),
            html.P("A Demo of Interactive Application Tracking System", 
                   className="text-center mb-4", style={'color': '#c2c7ce'})
        ], className="my-4 text-center fade-in"),
        
        # Main Content - Two Column Layout
        dbc.Row([
            # Left Column: Stats & Form
            dbc.Col([
                # KPI Stats - Two rows of 3 cards each
                dbc.Row([
                    dbc.Col(create_single_kpi_card("Applied", kpis.get('Applied', 0)), md=4),
                    dbc.Col(create_single_kpi_card("Active", kpis.get('Active', 0)), md=4),
                    dbc.Col(create_single_kpi_card("Online Assessment", kpis.get('Online Assessment', 0)), md=4),
                ], className="g-2 mb-2"),
                dbc.Row([
                    dbc.Col(create_single_kpi_card("Interviewing", kpis.get('Interviewing', 0)), md=4),
                    dbc.Col(create_single_kpi_card("Rejected", kpis.get('Rejected', 0)), md=4),
                    dbc.Col(create_single_kpi_card("Offered", kpis.get('Offered', 0)), md=4),
                ], className="g-2 mb-3"),
                
                # Application Form
                create_application_form(),
            ], md=3),
            
            # Right Column: Tabbed interface for Table & Charts
            dbc.Col([
                html.Div([
                    dbc.Tabs([
                        # Applications Tab
                        dbc.Tab([
                            html.Div(id="table-container"),
                        ], label="Applications"),
                        
                        # Analytics Tab
                        dbc.Tab([
                            create_charts_section(applications_data, status_history_data) if applications_data else create_empty_charts(),
                        ], label="Analytics"),
                    ])
                ], className="card-component fade-in p-0")
            ], md=9),
        ], className="g-3"),
        
        # Status History Modal
        create_status_history_modal(),
        
        # Toast notifications container
        html.Div(id="toast-container"),
        
        # Hidden divs for storing data and state
        dcc.Store(id='applications-store', data=applications_data),
        dcc.Store(id='status-history-store', data=status_history_data),
        dcc.Store(id='table-page-store', data={'current_page': 0, 'page_size': 10}),
        dcc.Store(id='modal-app-id-store', data=None),
        dcc.Store(id='search-filter-store', data={'search': '', 'status': 'all', 'category': 'all'}),
        
    ], fluid=True, className="fade-in")

# Set the layout
app.layout = create_layout

# ================================
# CALLBACK FUNCTIONS
# ================================
# Note: In a production refactor, these would be moved to separate callback modules

@app.callback(
    Output('table-container', 'children'),
    [Input('applications-store', 'data'),
     Input('table-page-store', 'data'),
     Input('search-filter-store', 'data')]
)
def update_table(apps_data, page_data, filter_data):
    """Update the applications table based on data and filters."""
    if not apps_data:
        return html.Div([
            html.P("No applications found. Add your first application using the form above!", 
                   className="text-center py-4", style={'color': '#c2c7ce'})
        ], className="card-component")
    
    # Apply filters
    filtered_data = apps_data.copy()
    
    # Search filter
    if filter_data.get('search'):
        search_term = filter_data['search'].lower()
        filtered_data = [
            app for app in filtered_data
            if (search_term in app['company_name'].lower() or 
                search_term in app['job_title'].lower() or 
                search_term in app.get('notes', '').lower())
        ]
    
    # Status filter
    if filter_data.get('status', 'all') != 'all':
        filtered_data = [app for app in filtered_data if app['status'] == filter_data['status']]
    
    # Category filter
    if filter_data.get('category', 'all') != 'all':
        filtered_data = [app for app in filtered_data if app['category'] == filter_data['category']]
    
    return create_applications_table(
        filtered_data, 
        page_size=page_data.get('page_size', 10),
        page_current=page_data.get('current_page', 0)
    )

@app.callback(
    [Output('applications-store', 'data'),
     Output('status-history-store', 'data'),
     Output('toast-container', 'children'),
     Output('company-input', 'value'),
     Output('title-input', 'value'),
     Output('url-input', 'value'),
     Output('date-input', 'value'),
     Output('category-input', 'value'),
     Output('notes-input', 'value')],
    [Input('submit-button', 'n_clicks')],
    [State('company-input', 'value'),
     State('title-input', 'value'),
     State('url-input', 'value'),
     State('date-input', 'value'),
     State('category-input', 'value'),
     State('notes-input', 'value'),
     State('applications-store', 'data'),
     State('status-history-store', 'data')]
)
def add_application(n_clicks, company, title, url, date, category, notes, apps_data, history_data):
    """Add a new application."""
    if not n_clicks:
        return apps_data, history_data, None, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    if not company or not title or not date:
        toast = dbc.Toast(
            "Please fill in all required fields (Company, Title, Date)",
            id="error-toast",
            header="Error",
            is_open=True,
            dismissable=True,
            duration=3000,
            icon="danger",
            style={"position": "fixed", "top": 20, "right": 20, "z-index": 9999}
        )
        return apps_data, history_data, toast, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Check for duplicates
    for app in apps_data:
        if app['company_name'].lower() == company.lower() and app['job_title'].lower() == title.lower():
            toast = dbc.Toast(
                "Application with this company and title already exists",
                id="duplicate-toast",
                header="Duplicate Entry",
                is_open=True,
                dismissable=True,
                duration=3000,
                icon="warning",
                style={"position": "fixed", "top": 20, "right": 20, "z-index": 9999}
            )
            return apps_data, history_data, toast, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Create new application
    new_id = max([app['id'] for app in apps_data], default=0) + 1
    new_app = {
        'id': new_id,
        'company_name': company,
        'job_title': title,
        'application_url': url or '',
        'date_applied': date,
        'category': category,
        'status': 'Applied',
        'notes': notes or '',
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Add status history entry
    new_history_id = max([h['id'] for h in history_data], default=0) + 1
    new_history = {
        'id': new_history_id,
        'application_id': new_id,
        'status': 'Applied',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    updated_apps = apps_data + [new_app]
    updated_history = history_data + [new_history]
    
    toast = dbc.Toast(
        f"Application to {company} added successfully!",
        id="success-toast",
        header="Success",
        is_open=True,
        dismissable=True,
        duration=3000,
        icon="success",
        style={"position": "fixed", "top": 20, "right": 20, "z-index": 9999}
    )
    
    # Clear form
    return updated_apps, updated_history, toast, '', '', '', datetime.now().strftime('%Y-%m-%d'), CATEGORIES[0], ''

# Additional callbacks would go here...
# For brevity, I'm including just the essential ones
# In a full refactor, all callbacks would be organized into separate modules

if __name__ == '__main__':
    app.run(debug=True, port=8051) 