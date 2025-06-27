"""Form components for the application."""

import dash_bootstrap_components as dbc
from dash import dcc, html
from config.constants import CATEGORIES, STATUSES
from datetime import datetime


def create_application_form():
    """Create the application form component - matches original simple design."""
    return html.Div([
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
            options=[{"label": cat, "value": cat} for cat in CATEGORIES],
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
    ], className="card-component fade-in")


def create_status_history_modal():
    """Create the status history modal component."""
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
                style={'resize': 'vertical'},
                className="mb-3"
            ),
            dbc.Button(
                "Update Notes",
                id="update-notes-button",
                color="primary",
                className="btn-primary me-2"
            )
        ]),
        dbc.ModalFooter([
            dbc.Button(
                "Close",
                id="close-modal-button",
                className="btn-m3-outline"
            )
        ])
    ], id="status-history-modal", size="lg")


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


def create_kpi_cards(kpis):
    """Create KPI cards component."""
    kpi_items = [
        ("Applied", kpis.get('Applied', 0), "Total applications submitted"),
        ("Active", kpis.get('Active', 0), "Applications in progress"),
        ("Online Assessment", kpis.get('Online Assessment', 0), "Pending assessments"),
        ("Interviewing", kpis.get('Interviewing', 0), "In interview process"),
        ("Rejected", kpis.get('Rejected', 0), "Applications rejected"),
        ("Offered", kpis.get('Offered', 0), "Offers received")
    ]
    
    cards = []
    for label, value, description in kpi_items:
        card = dbc.Col([
            html.Div([
                html.Div(str(value), className="stat-number"),
                html.Div(label, className="stat-label")
            ], className="stats-card")
        ], md=2, sm=6, className="mb-3")
        cards.append(card)
    
    return dbc.Row(cards, className="mb-4")


def create_single_kpi_card(label, value):
    """Create a single KPI card for use in grid layouts."""
    return html.Div([
        html.Div(str(value), className="stat-number"),
        html.Div(label, className="stat-label")
    ], className="stats-card")