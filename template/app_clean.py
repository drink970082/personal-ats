"""
Clean ATS Dashboard with dcc.Store Architecture
Modern, maintainable implementation following Dash best practices.
"""

import dash
from dash import html, dcc, Input, Output, State, callback_context, no_update, ALL
import dash_bootstrap_components as dbc
from datetime import datetime
import json

# Import backend services
from backend.data_service import DataService
from config.constants import CATEGORIES, STATUSES

# Initialize Dash app
app = dash.Dash(__name__, 
               external_stylesheets=[dbc.themes.BOOTSTRAP],
               suppress_callback_exceptions=True)

# Initialize data service
data_service = DataService()

def create_app_layout():
    """Create the main application layout with data stores."""
    return dbc.Container([
        # Data Stores - Single source of truth
        dcc.Store(id='applications-data-store', data=[]),
        dcc.Store(id='filter-state-store', data={'status': 'all', 'category': 'all', 'search': ''}),
        dcc.Store(id='pagination-state-store', data={'page': 0, 'size': 10}),
        
        # Header
        html.Div([
            html.H1("Modern ATS Dashboard", className="mb-1 md-typescale-display-small"),
            html.P("A Demo of Interactive Application Tracking System", 
                   className="text-secondary md-typescale-body-large"),
        ], className="my-4 text-center fade-in"),
        
        # Notification container
        html.Div(id='notification-container'),
        
        # Main Content
        dbc.Row([
            # Left Column: Stats & Form
            dbc.Col([
                # KPI Stats (2x3 grid)
                dbc.Row([
                    dbc.Col(html.Div(id="kpi-card-applied"), md=4),
                    dbc.Col(html.Div(id="kpi-card-active"), md=4),
                    dbc.Col(html.Div(id="kpi-card-assessment"), md=4),
                ], className="g-2 mb-2"),
                dbc.Row([
                    dbc.Col(html.Div(id="kpi-card-interviewing"), md=4),
                    dbc.Col(html.Div(id="kpi-card-rejected"), md=4),
                    dbc.Col(html.Div(id="kpi-card-offer"), md=4),
                ], className="g-2 mb-3"),
                
                # Application Form
                create_application_form(),
            ], md=3),
            
            # Right Column: Tabs
            dbc.Col([
                dbc.Tabs([
                    # Applications Tab
                    dbc.Tab([
                        html.Div([
                            # Filters
                            create_filter_row(),
                            # Table
                            html.Div(id='applications-table-content'),
                            # Pagination Controls
                            html.Div(id='pagination-controls')
                        ], className="card-component")
                    ], label="Applications"),
                    
                    # Analytics Tab
                    dbc.Tab([
                        html.Div(id='analytics-charts')
                    ], label="Analytics"),
                ], className="card-component fade-in p-0")
            ], md=9),
        ], className="g-3"),
        
        # History Modal
        create_status_history_modal(),
        
        # Hidden pagination controls for callback consistency  
        html.Div([
            dbc.Button("", id="prev-page-button", style={"display": "none"}),
            dbc.Button("", id="next-page-button", style={"display": "none"}),
            dbc.Select(
                id="page-size-select",
                options=[{"label": "10", "value": 10}],
                value=10,
                style={"display": "none"}
            ),
            # Add hidden page buttons for max expected pages
            *[dbc.Button("", id={"type": "page-button", "index": i}, style={"display": "none"}) 
              for i in range(10)]  # Support up to 10 pages initially
        ], style={"display": "none"})
        
    ], fluid=True, className="fade-in")

def create_application_form():
    """Create the application form component."""
    return html.Div([
        html.H5("Add New Application", className="md-typescale-title-large mb-3"),
        dbc.Input(id="company-input", placeholder="Company Name", className="mb-2", required=True),
        dbc.Input(id="title-input", placeholder="Job Title", className="mb-2", required=True),
        dbc.Input(id="url-input", placeholder="Application URL", type="url", className="mb-2"),
        dbc.Select(
            id="category-input",
            options=[{"label": c, "value": c} for c in CATEGORIES],
            value=CATEGORIES[0],
            placeholder="Category",
            className="mb-2",
            required=True,
        ),
        dbc.Textarea(id="notes-input", placeholder="Notes...", className="mb-2 form-notes-textarea"),
        dbc.Input(
            id="date-input",
            type="date",
            value=datetime.now().date().isoformat(),
            className="mb-2",
            required=True,
        ),
        dbc.Button("Submit", id="submit-button", color="primary", className="w-100 mt-2"),
    ], className="card-component fade-in")

def create_filter_row():
    """Create the filter controls."""
    return dbc.Row([
        dbc.Col([
            dbc.Select(
                id="status-filter",
                options=[{"label": "All Statuses", "value": "all"}] + 
                        [{"label": s, "value": s} for s in STATUSES],
                value="all",
                placeholder="Filter by status...",
            ),
        ], md=4),
        dbc.Col([
            dbc.Select(
                id="category-filter",
                options=[{"label": "All Categories", "value": "all"}] + 
                        [{"label": c, "value": c} for c in CATEGORIES],
                value="all",
                placeholder="Filter by category...",
            ),
        ], md=4),
        dbc.Col([
            dbc.Input(
                id="search-input",
                placeholder="Search companies or job titles...",
                value="",
                debounce=True,
            ),
        ], md=4),
    ], style={"padding": "1rem 1rem"})

def create_status_history_modal():
    """Create the status history modal."""
    return dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Status History", id="modal-title")),
        dbc.ModalBody([
            html.Div(id="status-history-content"),
            html.Hr(),
            html.H6("Edit Application Notes:"),
            dbc.Textarea(
                id="modal-notes-input",
                placeholder="Enter notes...",
                rows=3,
                className="mb-3 form-notes-textarea"
            )
        ]),
        dbc.ModalFooter([
            dbc.Button("Close & Save", id="close-modal-button", className="btn-m3-outline")
        ])
    ], id="status-history-modal", size="lg")

def create_stats_card(number, label):
    """Create a KPI statistics card."""
    label_content = []
    if " " in label:
        parts = label.split(" ", 1)
        label_content = [parts[0], html.Br(), parts[1]]
    else:
        label_content = [label, html.Br(), html.Span(" ", style={"opacity": 0})]

    return html.Div([
        html.P(number, className="stat-number mb-1"), 
        html.P(label_content, className="stat-label mb-0")
    ], className="stats-card")

# Set layout
app.layout = create_app_layout()

# ===== CALLBACK REGISTRATION =====

# 1. DATA MANAGEMENT CALLBACKS (Database operations)
@app.callback(
    Output('applications-data-store', 'data'),
    [Input('submit-button', 'n_clicks'),
     Input({'type': 'delete-button', 'index': ALL}, 'n_clicks'),
     Input({'type': 'delete-history', 'index': ALL}, 'n_clicks')],
    [State('company-input', 'value'),
     State('title-input', 'value'),
     State('url-input', 'value'),
     State('date-input', 'value'),
     State('category-input', 'value'),
     State('notes-input', 'value')],
    prevent_initial_call=False
)
def manage_applications_data(submit_clicks, delete_clicks, delete_history_clicks,
                           company, title, url, date, category, notes):
    """Manage applications data - only callback that touches the database."""
    ctx = callback_context
    
    # Handle form submission
    if ctx.triggered and 'submit-button' in ctx.triggered[0]['prop_id'] and submit_clicks:
        if company and title and date:
            form_data = {
                'company_name': company,
                'job_title': title,
                'application_url': url or '',
                'date_applied': date,
                'category': category or 'Others',
                'notes': notes or ''
            }
            result = data_service.add_application(form_data)
    
    # Handle deletions
    elif ctx.triggered:
        for trigger in ctx.triggered:
            prop_id = trigger['prop_id']
            
            if 'delete-button' in prop_id and trigger['value']:
                app_id = json.loads(prop_id.split('.')[0])['index']
                data_service.db.delete_application(app_id)
            
            elif 'delete-history' in prop_id and trigger['value']:
                history_id = json.loads(prop_id.split('.')[0])['index']
                data_service.delete_status_history(history_id)
    
    # Always return fresh data from database
    return data_service.get_applications_table_data()

@app.callback(
    [Output('filter-state-store', 'data'),
     Output('pagination-state-store', 'data')],
    [Input('status-filter', 'value'),
     Input('category-filter', 'value'),
     Input('search-input', 'value'),
     Input('prev-page-button', 'n_clicks'),
     Input('next-page-button', 'n_clicks'),
     Input({'type': 'page-button', 'index': ALL}, 'n_clicks'),
     Input('page-size-select', 'value')],
    [State('filter-state-store', 'data'),
     State('pagination-state-store', 'data'),
     State('applications-data-store', 'data')],
    prevent_initial_call=True
)
def manage_ui_state(status_filter, category_filter, search_input,
                   prev_click, next_click, page_clicks, page_size,
                   current_filters, current_pagination, applications_data):
    """Manage filter and pagination state."""
    ctx = callback_context
    
    if not ctx.triggered:
        return no_update, no_update
    
    trigger_id = ctx.triggered[0]['prop_id']
    
    # Initialize with current values if None
    current_filters = current_filters or {'status': 'all', 'category': 'all', 'search': ''}
    current_pagination = current_pagination or {'page': 0, 'size': 10}
    
    # Update filters
    new_filters = {
        'status': status_filter or 'all',
        'category': category_filter or 'all', 
        'search': search_input or ''
    }
    
    # Update pagination
    new_pagination = current_pagination.copy()
    
    # Reset pagination when filters change
    if any(filt in trigger_id for filt in ['status-filter', 'category-filter', 'search-input']):
        new_pagination['page'] = 0
    
    # Handle pagination changes
    elif 'prev-page-button' in trigger_id and prev_click:
        new_pagination['page'] = max(0, current_pagination['page'] - 1)
    elif 'next-page-button' in trigger_id and next_click:
        # Calculate filtered data to determine max pages
        filtered_data = applications_data or []
        if new_filters['status'] != 'all':
            filtered_data = [app for app in filtered_data if app['status'] == new_filters['status']]
        if new_filters['category'] != 'all':
            filtered_data = [app for app in filtered_data if app.get('category', 'Others') == new_filters['category']]
        if new_filters['search']:
            search_term = new_filters['search'].lower().strip()
            filtered_data = [app for app in filtered_data if 
                            search_term in app['company_name'].lower() or 
                            search_term in app['job_title'].lower()]
        
        total_pages = max(1, (len(filtered_data) + current_pagination['size'] - 1) // current_pagination['size'])
        new_pagination['page'] = min(current_pagination['page'] + 1, total_pages - 1)
    elif 'page-button' in trigger_id and any(page_clicks):
        page_info = json.loads(trigger_id.split('.')[0])
        new_pagination['page'] = page_info['index']
    elif 'page-size-select' in trigger_id and page_size:
        new_pagination['size'] = int(page_size)
        new_pagination['page'] = 0
    
    return new_filters, new_pagination

# 2. UI RENDERING CALLBACKS (Pure data transformation)
# 2. TABLE RENDERING CALLBACKS (Pure data transformation)
@app.callback(
    Output('applications-table-content', 'children'),
    [Input('applications-data-store', 'data'),
     Input('filter-state-store', 'data'),
     Input('pagination-state-store', 'data')],
    prevent_initial_call=False
)
def render_applications_table_content(applications_data, filters, pagination):
    """Render the applications table content only."""
    # Initialize defaults
    filters = filters or {'status': 'all', 'category': 'all', 'search': ''}
    pagination = pagination or {'page': 0, 'size': 10}
    applications_data = applications_data or []
    
    # Apply filters
    filtered_data = applications_data
    if filters['status'] != 'all':
        filtered_data = [app for app in filtered_data if app['status'] == filters['status']]
    if filters['category'] != 'all':
        filtered_data = [app for app in filtered_data if app.get('category', 'Others') == filters['category']]
    if filters['search']:
        search_term = filters['search'].lower().strip()
        filtered_data = [app for app in filtered_data if 
                        search_term in app['company_name'].lower() or 
                        search_term in app['job_title'].lower()]
    
    # Calculate pagination
    filtered_items = len(filtered_data)
    page_size = pagination['size']
    current_page = pagination['page']
    total_pages = max(1, (filtered_items + page_size - 1) // page_size) if filtered_items > 0 else 1
    current_page = min(current_page, total_pages - 1)
    current_page = max(0, current_page)
    
    # Paginate data
    start_idx = current_page * page_size
    end_idx = start_idx + page_size
    page_data = sorted(filtered_data, key=lambda x: x['date_applied'], reverse=True)[start_idx:end_idx]
    
    # Create table
    from components.table_clean import create_applications_table_clean
    
    if not page_data and not applications_data:
        return html.Div([
            html.P("No applications found. Add your first application!", 
                   className="text-center py-4", style={'color': '#c2c7ce'})
        ])
    elif not page_data and filtered_items == 0:
        return html.Div([
            html.P("No applications match your filters.", 
                   className="text-center py-4", style={'color': '#c2c7ce'})
        ])
    else:
        return create_applications_table_clean(page_data)

@app.callback(
    Output('pagination-controls', 'children'),
    [Input('applications-data-store', 'data'),
     Input('filter-state-store', 'data'),
     Input('pagination-state-store', 'data')],
    prevent_initial_call=False
)
def render_pagination_controls(applications_data, filters, pagination):
    """Render pagination controls separately."""
    # Initialize defaults
    filters = filters or {'status': 'all', 'category': 'all', 'search': ''}
    pagination = pagination or {'page': 0, 'size': 10}
    applications_data = applications_data or []
    
    # Apply filters to calculate counts
    filtered_data = applications_data
    if filters['status'] != 'all':
        filtered_data = [app for app in filtered_data if app['status'] == filters['status']]
    if filters['category'] != 'all':
        filtered_data = [app for app in filtered_data if app.get('category', 'Others') == filters['category']]
    if filters['search']:
        search_term = filters['search'].lower().strip()
        filtered_data = [app for app in filtered_data if 
                        search_term in app['company_name'].lower() or 
                        search_term in app['job_title'].lower()]
    
    # Calculate pagination
    total_items = len(applications_data)
    filtered_items = len(filtered_data)
    page_size = pagination['size']
    current_page = pagination['page']
    total_pages = max(1, (filtered_items + page_size - 1) // page_size) if filtered_items > 0 else 1
    current_page = min(current_page, total_pages - 1)
    current_page = max(0, current_page)
    
    # Create visible pagination controls
    from components.table_clean import create_pagination_controls_clean
    return create_pagination_controls_clean(current_page, total_pages, page_size, total_items, filtered_items)

# 3. FORM HANDLING CALLBACKS
@app.callback(
    [Output('notification-container', 'children'),
     Output('company-input', 'value'),
     Output('title-input', 'value'),
     Output('url-input', 'value'),
     Output('date-input', 'value'),
     Output('category-input', 'value'),
     Output('notes-input', 'value')],
    [Input('applications-data-store', 'data')],
    [State('submit-button', 'n_clicks')],
    prevent_initial_call=True
)
def handle_form_feedback(applications_data, submit_clicks):
    """Handle form feedback and clearing after successful submission."""
    ctx = callback_context
    
    # Check if this was triggered by a successful form submission
    if ctx.triggered and submit_clicks:
        # Create success notification
        notification = dbc.Toast(
            "Application added successfully!",
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
        
        # Clear form fields
        return notification, '', '', '', datetime.now().date().isoformat(), CATEGORIES[0], ''
    
    return no_update, no_update, no_update, no_update, no_update, no_update, no_update

# 4. STATUS UPDATE CALLBACK
@app.callback(
    Output('applications-data-store', 'data', allow_duplicate=True),
    [Input({'type': 'status-dropdown', 'index': ALL}, 'value')],
    [State('applications-data-store', 'data')],
    prevent_initial_call=True
)
def handle_status_updates(status_values, current_data):
    """Handle inline status updates."""
    ctx = callback_context
    
    if not ctx.triggered:
        return no_update
    
    # Handle status updates
    for trigger in ctx.triggered:
        prop_id = trigger['prop_id']
        
        if 'status-dropdown' in prop_id and trigger['value']:
            try:
                app_id = json.loads(prop_id.split('.')[0])['index']
                new_status = trigger['value']
                result = data_service.update_application_status(app_id, new_status)
                
                if result['success']:
                    # Return fresh data
                    return data_service.get_applications_table_data()
                    
            except Exception as e:
                print(f"Error updating status: {str(e)}")
    
    return no_update

# 5. KPI CALLBACKS
@app.callback(
    [Output('kpi-card-applied', 'children'),
     Output('kpi-card-active', 'children'),
     Output('kpi-card-assessment', 'children'),
     Output('kpi-card-interviewing', 'children'),
     Output('kpi-card-rejected', 'children'),
     Output('kpi-card-offer', 'children')],
    [Input('applications-data-store', 'data')],
    prevent_initial_call=False
)
def update_kpi_cards(applications_data):
    """Update KPI cards based on all data (unfiltered)."""
    try:
        # Calculate KPIs
        kpis = data_service.get_kpi_data()
        
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
        empty_card = create_stats_card(0, "Error")
        return empty_card, empty_card, empty_card, empty_card, empty_card, empty_card

# 6. ANALYTICS CHARTS CALLBACK
@app.callback(
    Output('analytics-charts', 'children'),
    [Input('applications-data-store', 'data')],
    prevent_initial_call=False
)
def update_analytics_charts(applications_data):
    """Update analytics charts based on all data (unfiltered)."""
    try:
        # Get Sankey data using all data
        sankey_data = data_service.get_sankey_data()
        
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

# 7. MODAL CALLBACKS
@app.callback(
    [Output('status-history-modal', 'is_open'),
     Output('status-history-content', 'children'),
     Output('modal-notes-input', 'value'),
     Output('notification-container', 'children', allow_duplicate=True)],
    [Input({'type': 'history-button', 'index': ALL}, 'n_clicks'),
     Input('close-modal-button', 'n_clicks')],
    [State('status-history-modal', 'is_open'),
     State('modal-notes-input', 'value')],
    prevent_initial_call=True
)
def handle_history_modal(history_clicks, close_click, is_open, current_notes):
    """Handle history modal open/close with auto-save."""
    ctx = callback_context
    
    if not ctx.triggered:
        return False, "", "", no_update
    
    trigger = ctx.triggered[0]
    
    # Close modal with auto-save
    if 'close-modal-button' in trigger['prop_id']:
        # Auto-save notes before closing
        app_id = getattr(data_service, '_current_modal_app_id', None)
        if app_id and current_notes is not None:
            try:
                result = data_service.update_application_notes(app_id, current_notes or '')
                if result['success']:
                    notification = dbc.Toast(
                        "Notes saved successfully",
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
                    return False, "", "", notification
            except Exception as e:
                notification = dbc.Toast(
                    f"Error saving notes: {str(e)}",
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
                return False, "", "", notification
        
        return False, "", "", no_update
    
    # Open modal with history data
    if 'history-button' in trigger['prop_id'] and trigger['value']:
        try:
            # Extract app_id from prop_id
            app_id = json.loads(trigger['prop_id'].split('.')[0])['index']
            
            # Get application history
            history_data = data_service.get_application_history(app_id)
            
            if history_data['success']:
                # Store app_id for later use in update callback
                data_service._current_modal_app_id = app_id
                
                # Get application details for notes
                app_data = data_service.get_application_by_id(app_id)
                current_notes = app_data.get('notes', '') if app_data else ''
                
                # Create modal content
                from components.table_clean import create_status_history_table_clean
                modal_content = create_status_history_table_clean(
                    history_data['history'], 
                    app_id
                )
                return True, modal_content, current_notes, no_update
            else:
                return False, "", "", no_update
        except:
            return False, "", "", no_update
    
        return is_open, no_update, no_update, no_update

# 8. PAGINATION SYNC CALLBACKS
@app.callback(
    Output('prev-page-button', 'n_clicks'),
    [Input('visible-prev-page-button', 'n_clicks')],
    prevent_initial_call=True
)
def sync_prev_button(visible_clicks):
    """Sync visible prev button with hidden callback button."""
    return visible_clicks

@app.callback(
    Output('next-page-button', 'n_clicks'),
    [Input('visible-next-page-button', 'n_clicks')],
    prevent_initial_call=True
)
def sync_next_button(visible_clicks):
    """Sync visible next button with hidden callback button."""
    return visible_clicks

@app.callback(
    Output('page-size-select', 'value'),
    [Input('visible-page-size-select', 'value')],
    prevent_initial_call=True
)
def sync_page_size(visible_value):
    """Sync visible page size with hidden callback select."""
    return visible_value

if __name__ == '__main__':
    print("Starting Clean ATS Dashboard...")
    print("Database initialized successfully")
    
    # Seed database if empty
    try:
        existing_apps = data_service.get_applications_table_data()
        if not existing_apps:
            print("Database is empty, seeding with mock data...")
            from utils.data import seed_database_with_mock_data
            seed_database_with_mock_data(data_service, 25)
        else:
            print(f"Found {len(existing_apps)} existing applications in database")
    except Exception as e:
        print(f"Warning: Could not check/seed database: {e}")
    
    print("Server starting at http://127.0.0.1:8052")
    app.run(debug=True, host='127.0.0.1', port=8052) 