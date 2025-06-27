"""Table component for displaying applications."""

import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from config.constants import STATUSES
from utils.data import get_status_color_class


def create_applications_table(applications_data, page_size=10, page_current=0):
    """Create the main applications table with interactive controls."""
    if not applications_data:
        return html.Div([
            html.P("No applications found. Add your first application using the form above!", 
                   className="text-center py-4", style={'color': '#c2c7ce'})
        ], className="card-component")
    
    # Sort by date applied (most recent first)
    sorted_data = sorted(applications_data, key=lambda x: x['date_applied'], reverse=True)
    
    # Pagination
    start_idx = page_current * page_size
    end_idx = start_idx + page_size
    page_data = sorted_data[start_idx:end_idx]
    
    # Create table rows
    table_rows = []
    for i, app in enumerate(page_data):
        # Status indicator
        status_class = get_status_color_class(app['status'])
        status_cell = html.Div([
            html.Div(className=f"status-indicator {status_class}"),
            dbc.Select(
                id={"type": "status-dropdown", "index": app['id']},
                options=[{"label": status, "value": status} for status in STATUSES],
                value=app['status'],
                className="table-dropdown flex-grow-1",
                style={'min-width': '160px'}
            )
        ], className="status-cell")
        
        # Notes cell with plain text (not editable in table)
        notes_cell = html.Div(
            app['notes'][:50] + '...' if len(app['notes']) > 50 else app['notes'],
            style={'color': '#c2c7ce', 'font-size': '13px'},
            title=app['notes']  # Show full text on hover
        )
        
        # Action buttons
        actions_cell = html.Div([
            dbc.Button(
                "History",
                id={"type": "history-button", "index": app['id']},
                size="sm",
                className="btn-m3-outline me-2",
                style={'font-size': '11px', 'padding': '0.25rem 0.75rem'}
            ),
            dbc.Button(
                "Delete",
                id={"type": "delete-button", "index": app['id']},
                size="sm",
                className="btn-m3-text-danger",
                style={'font-size': '11px', 'padding': '0.25rem 0.75rem'}
            )
        ], className="d-flex gap-1")
        
        row = html.Tr([
            html.Td(app['date_applied'], style={'font-size': '13px', 'min-width': '100px'}),
            html.Td(app['company_name'], style={'font-weight': '500', 'font-size': '14px'}),
            html.Td(app['job_title'], style={'font-size': '13px'}),
            html.Td(status_cell, style={'min-width': '180px'}),
            html.Td(notes_cell, style={'max-width': '200px'}),
            html.Td(actions_cell, style={'min-width': '140px'})
        ])
        table_rows.append(row)
    
    # Table header
    header = html.Thead([
        html.Tr([
            html.Th("TIME", style={'font-size': '12px', 'font-weight': '600', 'color': '#c2c7ce'}),
            html.Th("COMPANY", style={'font-size': '12px', 'font-weight': '600', 'color': '#c2c7ce'}),
            html.Th("TITLE", style={'font-size': '12px', 'font-weight': '600', 'color': '#c2c7ce'}),
            html.Th("STATUS", style={'font-size': '12px', 'font-weight': '600', 'color': '#c2c7ce'}),
            html.Th("NOTES", style={'font-size': '12px', 'font-weight': '600', 'color': '#c2c7ce'}),
            html.Th("ACTIONS", style={'font-size': '12px', 'font-weight': '600', 'color': '#c2c7ce'})
        ])
    ])
    
    # Create pagination controls
    total_pages = (len(sorted_data) + page_size - 1) // page_size
    pagination = create_pagination_controls(page_current, total_pages, page_size, len(sorted_data))
    
    return html.Div([
        # Filter/Search row
        create_table_filters(),
        
        # Table
        html.Div([
            html.Table([
                header,
                html.Tbody(table_rows)
            ], className="table table-hover")
        ], className="table-responsive"),
        
        # Pagination
        pagination
    ], className="card-component")


def create_table_filters():
    """Create filter and search controls for the table."""
    return dbc.Row([
        dbc.Col([
            dbc.InputGroup([
                dbc.Input(
                    id="search-input",
                    placeholder="Search companies, titles, or notes...",
                    type="text",
                    style={'font-size': '14px'}
                ),
                dbc.Button(
                    "Clear",
                    id="clear-search-button",
                    outline=True,
                    color="secondary",
                    style={'font-size': '13px'}
                )
            ], size="sm")
        ], md=6),
        dbc.Col([
            dbc.Select(
                id="status-filter",
                options=[
                    {"label": "All Statuses", "value": "all"}
                ] + [{"label": status, "value": status} for status in STATUSES],
                value="all",
                style={'font-size': '14px'}
            )
        ], md=3),
        dbc.Col([
            dbc.Select(
                id="category-filter",
                options=[
                    {"label": "All Categories", "value": "all"},
                    {"label": "SWE", "value": "SWE"},
                    {"label": "MLE", "value": "MLE"},
                    {"label": "DS", "value": "DS"},
                    {"label": "DA", "value": "DA"},
                    {"label": "Quant Dev", "value": "Quant Dev"},
                    {"label": "Quant Analyst", "value": "Quant Analyst"},
                    {"label": "Quant Trader", "value": "Quant Trader"},
                    {"label": "AI Engineer", "value": "AI Engineer"},
                    {"label": "Others", "value": "Others"}
                ],
                value="all",
                style={'font-size': '14px'}
            )
        ], md=3)
    ], className="filter-search-row align-items-end")


def create_pagination_controls(current_page, total_pages, page_size, total_items):
    """Create pagination controls for the table."""
    if total_pages <= 1:
        return html.Div()
    
    # Page size selector
    page_size_options = [
        {"label": "10", "value": 10},
        {"label": "25", "value": 25},
        {"label": "50", "value": 50},
        {"label": "100", "value": 100}
    ]
    
    # Page buttons
    page_buttons = []
    
    # Previous button
    page_buttons.append(
        dbc.Button(
            "‹",
            id="prev-page-button",
            className="pagination-btn me-1",
            disabled=current_page == 0,
            style={'min-width': '32px'}
        )
    )
    
    # Page number buttons (show max 5 pages around current)
    start_page = max(0, current_page - 2)
    end_page = min(total_pages, start_page + 5)
    start_page = max(0, end_page - 5)
    
    for page in range(start_page, end_page):
        is_current = page == current_page
        page_buttons.append(
            dbc.Button(
                str(page + 1),
                id={"type": "page-button", "index": page},
                className="pagination-btn-active me-1" if is_current else "pagination-btn me-1",
                style={'min-width': '32px'}
            )
        )
    
    # Next button
    page_buttons.append(
        dbc.Button(
            "›",
            id="next-page-button",
            className="pagination-btn",
            disabled=current_page >= total_pages - 1,
            style={'min-width': '32px'}
        )
    )
    
    # Info text
    start_item = current_page * page_size + 1
    end_item = min((current_page + 1) * page_size, total_items)
    info_text = f"Showing {start_item}-{end_item} of {total_items} applications"
    
    return dbc.Row([
        dbc.Col([
            html.Div([
                html.Span("Items per page: ", style={'font-size': '0.875rem', 'color': '#c2c7ce'}),
                dbc.Select(
                    id="page-size-select",
                    options=page_size_options,
                    value=page_size,
                    className="pagination-select d-inline-block",
                    style={'width': '70px', 'display': 'inline-block'}
                )
            ], className="d-flex align-items-center")
        ], md=4),
        dbc.Col([
            html.Div(page_buttons, className="d-flex justify-content-center")
        ], md=4),
        dbc.Col([
            html.Div(
                info_text,
                className="text-end",
                style={'font-size': '0.875rem', 'color': '#c2c7ce'}
            )
        ], md=4)
    ], className="mt-3 pt-3", style={'border-top': '1px solid var(--md-sys-color-outline-variant)'})


def create_status_history_table(history_data, app_id):
    """Create a table showing status history for a specific application."""
    if not history_data:
        return html.P("No status history available.", className="text-muted")
    
    # Filter history for this application and sort by timestamp
    app_history = [h for h in history_data if h['application_id'] == app_id]
    app_history.sort(key=lambda x: x['timestamp'], reverse=True)
    
    table_rows = []
    for i, entry in enumerate(app_history):
        # Format timestamp
        timestamp = entry['timestamp']
        if len(timestamp) > 10:  # Has time component
            date_part = timestamp.split(' ')[0]
        else:
            date_part = timestamp
        
        row = html.Tr([
            html.Td(entry['status'], style={'font-weight': '500'}),
            html.Td(date_part),
            html.Td([
                dbc.Button(
                    "Delete",
                    id={"type": "delete-history", "index": entry['id']},
                    size="sm",
                    className="btn-m3-text-danger",
                    style={'font-size': '11px', 'padding': '0.2rem 0.6rem'}
                )
            ])
        ])
        table_rows.append(row)
    
    return html.Table([
        html.Thead([
            html.Tr([
                html.Th("Status"),
                html.Th("Date"),
                html.Th("Actions")
            ])
        ]),
        html.Tbody(table_rows)
    ], className="table table-sm") 