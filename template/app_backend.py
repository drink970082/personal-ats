"""
ATS Dashboard Application with Backend Integration
Modular structure with database backend for job application tracking.
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# Import configuration and styling
from config.constants import CATEGORIES, STATUSES, CATEGORY_COLORS

# Import components
from components.forms import create_application_form, create_status_history_modal, create_stats_card
from components.table import create_applications_table, create_filter_search_row, create_pagination_controls
from components.charts import create_charts_section

# Import backend services
from backend.data_service import DataService
from callbacks.app_callbacks import register_callbacks

# Initialize Dash app
app = dash.Dash(__name__, 
               external_stylesheets=[dbc.themes.BOOTSTRAP],
               suppress_callback_exceptions=True)

# CSS will be auto-loaded from assets/ folder

def create_app_layout():
    """Create the main application layout - EXACTLY matching original app.py."""
    return dbc.Container(
        [
            # Header
            html.Div(
                [
                    html.H1("Modern ATS Dashboard", className="mb-1 md-typescale-display-small"),
                    html.P(
                        "A Demo of Interactive Application Tracking System",
                        className="text-secondary md-typescale-body-large",
                    ),
                ],
                className="my-4 text-center fade-in",
            ),
            
            # Notification container
            html.Div(id='notification-container'),
            
            # Main Content
            dbc.Row(
                [
                    # Left Column: Stats & Form
                    dbc.Col(
                        [
                            # KPI Stats
                            dbc.Row(
                                [
                                    dbc.Col(html.Div(id="kpi-card-applied"), md=4),
                                    dbc.Col(html.Div(id="kpi-card-active"), md=4),
                                    dbc.Col(html.Div(id="kpi-card-assessment"), md=4),
                                ],
                                className="g-2 mb-2",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(html.Div(id="kpi-card-interviewing"), md=4),
                                    dbc.Col(html.Div(id="kpi-card-rejected"), md=4),
                                    dbc.Col(html.Div(id="kpi-card-offer"), md=4),
                                ],
                                className="g-2 mb-3",
                            ),
                            # Application Form
                            create_application_form(),
                        ],
                        md=3,
                    ),
                    # Right Column: Tabs for Table & Charts
                    dbc.Col(
                        html.Div(
                            dbc.Tabs(
                                [
                                    # Applications Tab
                                    dbc.Tab(
                                        [
                                            # Combined filters, table, and pagination in one container
                                            html.Div([
                                                # Filter row
                                                dbc.Row(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                dbc.Select(
                                                                    id="status-filter",
                                                                    options=[{"label": "All Statuses", "value": "all"}]
                                                                    + [{"label": s, "value": s} for s in STATUSES],
                                                                    value="all",
                                                                    placeholder="Filter by status...",
                                                                ),
                                                            ],
                                                            md=4,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Select(
                                                                    id="category-filter",
                                                                    options=[{"label": "All Categories", "value": "all"}]
                                                                    + [{"label": c, "value": c} for c in CATEGORIES],
                                                                    value="all",
                                                                    placeholder="Filter by category...",
                                                                ),
                                                            ],
                                                            md=4,
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Input(
                                                                    id="search-input",
                                                                    placeholder="Search companies or job titles...",
                                                                    value="",
                                                                ),
                                                            ],
                                                            md=4,
                                                        ),
                                                    ],
                                                    style={"padding": "1rem 1rem"},
                                                ),
                                                
                                                                                # Applications table content (will include pagination)
                                html.Div(id='applications-table'),
                                
                                # Hidden pagination controls that are always present for callbacks
                                html.Div([
                                    dbc.Button("‹", id="prev-page-button", style={'display': 'none'}),
                                    dbc.Button("›", id="next-page-button", style={'display': 'none'}),
                                    dbc.Button("1", id={"type": "page-button", "index": 0}, style={'display': 'none'}),
                                    dbc.Select(id="page-size-select", options=[{"label": "10", "value": 10}], value=10, style={'display': 'none'})
                                ], style={'display': 'none'})
                                                
                                            ], className="card-component"),
                                        ],
                                        label="Applications",
                                    ),
                                    # Analytics Tab
                                    dbc.Tab(
                                        [
                                            html.Div(id='analytics-charts')
                                        ],
                                        label="Analytics",
                                    ),
                                ]
                            ),
                            className="card-component fade-in p-0",
                        ),
                        md=9,
                    ),
                ],
                className="g-3",
            ),
            
            # History Modal
            create_status_history_modal()
            
        ],
        fluid=True,
        className="fade-in",
    )


# Set app layout
app.layout = create_app_layout()

# Register callbacks with backend integration
data_service = register_callbacks(app)

if __name__ == '__main__':
    print("🚀 Starting ATS Dashboard with Backend...")
    print("📊 Database initialized successfully")
    
    # Optional: Seed database with mock data if empty
    try:
        existing_apps = data_service.get_applications_table_data()
        if not existing_apps:
            print("📝 Database is empty, seeding with mock data...")
            from utils.data import seed_database_with_mock_data
            seed_database_with_mock_data(data_service, 25)
        else:
            print(f"📊 Found {len(existing_apps)} existing applications in database")
    except Exception as e:
        print(f"⚠️ Warning: Could not check/seed database: {e}")
    
    print("🌐 Server starting at http://127.0.0.1:8051")
    app.run(debug=True, host='127.0.0.1', port=8051) 