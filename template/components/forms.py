"""Form components for the application."""

import dash_bootstrap_components as dbc
from dash import dcc, html
from config.constants import CATEGORIES, STATUSES
from datetime import datetime


def create_application_form():
    """Create the application form component - EXACTLY matching original app.py."""
    return html.Div(
        [
            html.H5("Add New Application", className="md-typescale-title-large mb-3"),
            dbc.Input(
                id="company-input",
                placeholder="Company Name",
                className="mb-2",
                required=True,
            ),
            dbc.Input(
                id="title-input",
                placeholder="Job Title",
                className="mb-2",
                required=True,
            ),
            dbc.Input(
                id="url-input",
                placeholder="Application URL",
                type="url",
                className="mb-2",
                required=True,
            ),
            dbc.Select(
                id="category-input",
                options=[{"label": c, "value": c} for c in CATEGORIES],
                value=CATEGORIES[0],
                placeholder="Category",
                className="mb-2",
                required=True,
            ),
            dbc.Textarea(
                id="notes-input",
                placeholder="Notes...",
                className="mb-2 form-notes-textarea",
            ),
            dbc.Input(
                id="date-input",
                type="date",
                value=datetime.now().date().isoformat(),
                className="mb-2",
                required=True,
            ),
            dbc.Button("Submit", id="submit-button", color="primary", className="w-100 mt-2"),
        ],
        className="card-component fade-in",
    )


def create_status_history_modal():
    """Create the status history modal component with proper Material 3 styling."""
    return dbc.Modal([
        dbc.ModalHeader(
            dbc.ModalTitle("Status History", id="modal-title"),
            style={
                'background-color': 'var(--md-sys-color-surface-container)',
                'border-bottom': '1px solid var(--md-sys-color-outline-variant)',
                'color': 'var(--md-sys-color-on-surface)'
            }
        ),
        dbc.ModalBody([
            html.Div(id="status-history-content"),
            html.Hr(style={'border-color': 'var(--md-sys-color-outline-variant)'}),
            html.H6("Edit Application Notes:", style={'color': 'var(--md-sys-color-on-surface)'}),
            dbc.Textarea(
                id="modal-notes-input",
                placeholder="Enter notes...",
                rows=3,
                style={
                    'resize': 'vertical',
                    'background-color': 'var(--md-sys-color-surface-container-highest)',
                    'border': '1px solid var(--md-sys-color-outline-variant)',
                    'color': 'var(--md-sys-color-on-surface)',
                    'min-height': '80px',
                    'max-height': '200px'
                },
                className="mb-3 form-notes-textarea"
            )
        ], style={
            'background-color': 'var(--md-sys-color-surface-container)',
            'color': 'var(--md-sys-color-on-surface)'
        }),
        dbc.ModalFooter([
            dbc.Button(
                "Close & Save",
                id="close-modal-button",
                className="btn-m3-outline"
            )
        ], style={
            'background-color': 'var(--md-sys-color-surface-container)',
            'border-top': '1px solid var(--md-sys-color-outline-variant)'
        })
    ], 
    id="status-history-modal", 
    size="lg",
    style={
        'background-color': 'var(--md-sys-color-surface-container)'
    })


def create_add_status_form():
    """Create form for adding new status to history."""
    return html.Div([
        html.H6("Add Status Change:", className="mt-3"),
        dbc.Row([
            dbc.Col([
                dbc.Select(
                    id="new-status-select",
                    options=[{"label": status, "value": status} for status in STATUSES],
                    placeholder="Select new status...",
                    className="mb-2"
                )
            ], md=8),
            dbc.Col([
                dbc.Button(
                    "Add Status",
                    id="add-status-button",
                    color="primary",
                    className="btn-primary",
                    size="sm"
                )
            ], md=4)
        ])
    ], id="add-status-form", style={'display': 'none'})


def create_stats_card(number, label):
    """Create a KPI statistics card matching original design."""
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


def create_kpi_cards(kpis):
    """Create KPI cards component with 2 rows × 3 columns layout, matching original design."""
    kpi_items = [
        ("Applied", kpis.get('applied', 0), "Total applications submitted"),
        ("Active", kpis.get('active', 0), "Applications in progress"),
        ("Online Assessment", kpis.get('online_assessment', 0), "Pending assessments"),
        ("Interviewing", kpis.get('interviewing', 0), "In interview process"),
        ("Rejected", kpis.get('rejected', 0), "Applications rejected"),
        ("Offered", kpis.get('offered', 0), "Offers received")
    ]
    
    # Create first row (first 3 cards)
    first_row = dbc.Row([
        dbc.Col(create_stats_card(kpi_items[i][1], kpi_items[i][0]), md=4, className="mb-2") 
        for i in range(3)
    ], className="g-2")
    
    # Create second row (last 3 cards)
    second_row = dbc.Row([
        dbc.Col(create_stats_card(kpi_items[i][1], kpi_items[i][0]), md=4, className="mb-2") 
        for i in range(3, 6)
    ], className="g-2")
    
    return html.Div([first_row, second_row], className="mb-3")


def create_single_kpi_card(label, value):
    """Create a single KPI card for use in grid layouts."""
    return html.Div([
        html.Div(str(value), className="stat-number"),
        html.Div(label, className="stat-label")
    ], className="stats-card")