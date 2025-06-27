"""
Redesigned ATS Dashboard with Clean Pagination
Eliminates the hidden/visible control complexity with a direct approach.
"""

import dash
from dash import html, dcc, Input, Output, State, callback_context, no_update, ALL, clientside_callback
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
    """Create the main application layout."""
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
                            # Filters and Controls Row
                            create_filter_and_controls_row(),
                            
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
        create_status_history_modal()
        
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

def create_filter_and_controls_row():
    """Create the filter controls, page size selector, and pagination info in one row."""
    return dbc.Row([
        # Filters (reduced width to make room for controls)
        dbc.Col([
            dbc.Select(
                id="status-filter",
                options=[{"label": "All Statuses", "value": "all"}] + 
                        [{"label": s, "value": s} for s in STATUSES],
                value="all",
                placeholder="Filter by status...",
                size="sm",
                className="form-select",
            ),
        ], md=3),
        dbc.Col([
            dbc.Select(
                id="category-filter",
                options=[{"label": "All Categories", "value": "all"}] + 
                        [{"label": c, "value": c} for c in CATEGORIES],
                value="all",
                placeholder="Filter by category...",
                size="sm",
                className="form-select",
            ),
        ], md=3),
        dbc.Col([
            dbc.Input(
                id="search-input",
                placeholder="Search companies or job titles...",
                value="",
                debounce=True,
                size="sm",
                className="form-control",
            ),
        ], md=3),
        
        # Page size selector
        dbc.Col([
            html.Div([
                html.Span("Show ", className="small text-secondary me-1", style={"font-size": "12px"}),
                dbc.Select(
                    id="page-size-select",
                    options=[
                        {"label": "10", "value": 10},
                        {"label": "25", "value": 25},
                        {"label": "50", "value": 50},
                    ],
                    value=10,
                    size="sm",
                    className="pagination-select",
                    style={"width": "60px", "display": "inline-block"},
                ),
                html.Span(" entries", className="small text-secondary ms-1", style={"font-size": "12px"}),
            ], className="d-flex align-items-center justify-content-end"),
        ], md=2),
        
        # Pagination info
        dbc.Col([
            html.Div(
                id="pagination-info", 
                className="text-end",
                style={"font-size": "12px", "color": "#6c757d"}
            )
        ], md=1),
    ], align="center", className="mb-3 filter-controls", style={"padding": "1rem 1rem 0.5rem 1rem"})

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

def apply_filters_and_pagination(applications_data, filters, pagination):
    """Central function to apply filters and pagination logic."""
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
    total_items = len(applications_data)
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
    
    return {
        'page_data': page_data,
        'total_items': total_items,
        'filtered_items': filtered_items,
        'current_page': current_page,
        'total_pages': total_pages,
        'page_size': page_size
    }

# Set layout
app.layout = create_app_layout()

# ===== CALLBACK REGISTRATION =====

# 1. DATA MANAGEMENT (Database operations only)
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
    """Handle all database operations."""
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
    
    return data_service.get_applications_table_data()

# 2. STATE MANAGEMENT (Filter and pagination state)
@app.callback(
    [Output('filter-state-store', 'data'),
     Output('pagination-state-store', 'data')],
    [Input('status-filter', 'value'),
     Input('category-filter', 'value'),
     Input('search-input', 'value'),
     Input('page-size-select', 'value')],
    [State('filter-state-store', 'data'),
     State('pagination-state-store', 'data')],
    prevent_initial_call=True
)
def manage_filter_and_pagination_state(status_filter, category_filter, search_input, page_size,
                                     current_filters, current_pagination):
    """Manage filter and pagination state changes."""
    # Initialize defaults
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
    
    # Reset to page 0 when filters change or page size changes
    ctx = callback_context
    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id']
        if 'page-size-select' in trigger_id:
            new_pagination['size'] = int(page_size) if page_size else 10
            new_pagination['page'] = 0
        elif any(filt in trigger_id for filt in ['status-filter', 'category-filter', 'search-input']):
            new_pagination['page'] = 0
    
    return new_filters, new_pagination

# 3. PAGINATION NAVIGATION (Server-side with pattern matching)
@app.callback(
    Output('pagination-state-store', 'data', allow_duplicate=True),
    [Input('prev-page-btn', 'n_clicks'),
     Input('next-page-btn', 'n_clicks'),
     Input({'type': 'page-btn', 'page': ALL}, 'n_clicks')],
    [State('pagination-state-store', 'data'),
     State('applications-data-store', 'data'), 
     State('filter-state-store', 'data')],
    prevent_initial_call=True
)
def handle_pagination_navigation(prev_clicks, next_clicks, page_clicks, 
                               current_pagination, applications_data, filters):
    """Handle pagination navigation with pattern matching."""
    ctx = callback_context
    
    if not ctx.triggered:
        return no_update
    
    # Initialize defaults
    current_pagination = current_pagination or {'page': 0, 'size': 10}
    
    # Apply filters to calculate max pages
    result = apply_filters_and_pagination(applications_data, filters, current_pagination)
    total_pages = result['total_pages']
    
    trigger_id = ctx.triggered[0]['prop_id']
    new_page = current_pagination['page']
    
    if 'prev-page-btn' in trigger_id and prev_clicks:
        new_page = max(0, current_pagination['page'] - 1)
    elif 'next-page-btn' in trigger_id and next_clicks:
        new_page = min(current_pagination['page'] + 1, total_pages - 1)
    elif 'page-btn' in trigger_id and ctx.triggered[0]['value']:
        # Extract page from pattern-matching callback
        import json
        button_info = json.loads(trigger_id.split('.')[0])
        new_page = button_info['page']
        new_page = max(0, min(new_page, total_pages - 1))
    
    return {
        'page': new_page,
        'size': current_pagination['size']
    }

# 4. TABLE RENDERING
@app.callback(
    Output('applications-table-content', 'children'),
    [Input('applications-data-store', 'data'),
     Input('filter-state-store', 'data'),
     Input('pagination-state-store', 'data')],
    prevent_initial_call=False
)
def render_table_content(applications_data, filters, pagination):
    """Render table content using centralized logic."""
    result = apply_filters_and_pagination(applications_data, filters, pagination)
    
    if not result['page_data'] and not applications_data:
        return html.Div([
            html.P("No applications found. Add your first application!", 
                   className="text-center py-4", style={'color': '#c2c7ce'})
        ])
    elif not result['page_data'] and result['filtered_items'] == 0:
        return html.Div([
            html.P("No applications match your filters.", 
                   className="text-center py-4", style={'color': '#c2c7ce'})
        ])
    else:
        from components.table_clean import create_applications_table_clean
        return create_applications_table_clean(result['page_data'])

# 5. PAGINATION INFO
@app.callback(
    Output('pagination-info', 'children'),
    [Input('applications-data-store', 'data'),
     Input('filter-state-store', 'data'),
     Input('pagination-state-store', 'data')],
    prevent_initial_call=False
)
def update_pagination_info(applications_data, filters, pagination):
    """Update pagination information display."""
    result = apply_filters_and_pagination(applications_data, filters, pagination)
    
    if result['filtered_items'] == 0:
        return "No entries"
    
    start_item = result['current_page'] * result['page_size'] + 1
    end_item = min((result['current_page'] + 1) * result['page_size'], result['filtered_items'])
    
    base_text = f"{start_item}-{end_item} of {result['filtered_items']}"
    if result['filtered_items'] != result['total_items']:
        base_text += f" ({result['total_items']} total)"
    
    return base_text

# 6. PAGINATION CONTROLS
@app.callback(
    Output('pagination-controls', 'children'),
    [Input('applications-data-store', 'data'),
     Input('filter-state-store', 'data'),
     Input('pagination-state-store', 'data')],
    prevent_initial_call=False
)
def render_pagination_controls(applications_data, filters, pagination):
    """Render pagination navigation controls."""
    result = apply_filters_and_pagination(applications_data, filters, pagination)
    
    if result['total_pages'] <= 1:
        return html.Div()  # No pagination needed
    
    # Create page buttons
    page_buttons = []
    
    # Previous button
    prev_disabled = result['current_page'] == 0
    page_buttons.append(
        dbc.Button(
            "‹", 
            id="prev-page-btn",
            className=f"pagination-btn {'disabled' if prev_disabled else ''}", 
            disabled=prev_disabled,
            size="sm"
        )
    )
    
    # Page number buttons
    start_page = max(0, result['current_page'] - 2)
    end_page = min(result['total_pages'], start_page + 5)
    
    if end_page - start_page < 5:
        start_page = max(0, end_page - 5)
    
    for page_num in range(start_page, end_page):
        is_current = page_num == result['current_page']
        page_buttons.append(
            dbc.Button(
                str(page_num + 1),
                id={'type': 'page-btn', 'page': page_num},
                className=f"pagination-btn{'-active' if is_current else ''} me-1",
                size="sm"
            )
        )
    
    # Next button
    next_disabled = result['current_page'] >= result['total_pages'] - 1
    page_buttons.append(
        dbc.Button(
            "›", 
            id="next-page-btn",
            className=f"pagination-btn {'disabled' if next_disabled else ''}", 
            disabled=next_disabled,
            size="sm"
        )
    )
    
    return html.Div([
        html.Div(page_buttons, className="d-flex gap-1 justify-content-center"),
         ], className="mt-2", style={"padding": "0rem 1rem 1rem 1rem"})

# 7. FORM HANDLING
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
    
    if ctx.triggered and submit_clicks:
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
        return notification, '', '', '', datetime.now().date().isoformat(), CATEGORIES[0], ''
    
    return no_update, no_update, no_update, no_update, no_update, no_update, no_update

# 8. STATUS UPDATES
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
    
    for trigger in ctx.triggered:
        prop_id = trigger['prop_id']
        
        if 'status-dropdown' in prop_id and trigger['value']:
            try:
                app_id = json.loads(prop_id.split('.')[0])['index']
                new_status = trigger['value']
                result = data_service.update_application_status(app_id, new_status)
                
                if result['success']:
                    return data_service.get_applications_table_data()
                    
            except Exception as e:
                print(f"Error updating status: {str(e)}")
    
    return no_update

# 9. KPI CARDS
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
    """Update KPI cards based on all data."""
    try:
        kpis = data_service.get_kpi_data()
        
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

# 10. ANALYTICS CHARTS
@app.callback(
    Output('analytics-charts', 'children'),
    [Input('applications-data-store', 'data')],
    prevent_initial_call=False
)
def update_analytics_charts(applications_data):
    """Update analytics charts."""
    try:
        sankey_data = data_service.get_sankey_data()
        
        from components.charts import create_charts_section, create_empty_charts
        
        if not applications_data:
            return create_empty_charts()
        
        return create_charts_section(applications_data, sankey_data)
        
    except Exception as e:
        print(f"Error updating analytics charts: {e}")
        from components.charts import create_empty_charts
        return create_empty_charts()

# 11. MODAL HANDLING
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
    """Handle history modal operations."""
    ctx = callback_context
    
    if not ctx.triggered:
        return False, "", "", no_update
    
    trigger = ctx.triggered[0]
    
    # Close modal with auto-save
    if 'close-modal-button' in trigger['prop_id']:
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
    
    # Open modal
    if 'history-button' in trigger['prop_id'] and trigger['value']:
        try:
            app_id = json.loads(trigger['prop_id'].split('.')[0])['index']
            
            history_data = data_service.get_application_history(app_id)
            
            if history_data['success']:
                data_service._current_modal_app_id = app_id
                
                app_data = data_service.get_application_by_id(app_id)
                current_notes = app_data.get('notes', '') if app_data else ''
                
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

if __name__ == '__main__':
    print("Starting Redesigned ATS Dashboard...")
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
    
    print("Server starting at http://127.0.0.1:8053")
    app.run(debug=True, host='127.0.0.1', port=8053) 