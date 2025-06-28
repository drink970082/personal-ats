"""Clean table components with simple, static pagination controls."""

import dash_bootstrap_components as dbc
from dash import html
from config.constants import STATUSES
from utils.data import get_status_color_class


def create_applications_table_clean(page_data):
    """Create a clean table with just the data, no pagination logic."""
    if not page_data:
        return html.Div([
            html.P("No applications match your filters.", 
                   className="text-center py-4", style={'color': '#c2c7ce'})
        ])
    
    # Create table rows
    table_rows = []
    for app in page_data:
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
        
        # Notes cell
        notes_cell = html.Div(
            app['notes'][:50] + '...' if len(app['notes']) > 50 else app['notes'],
            style={'color': '#c2c7ce', 'font-size': '13px'},
            title=app['notes']
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
            html.Td(app.get('category', 'Others'), style={'font-size': '13px', 'min-width': '100px'}),
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
            html.Th("CATEGORY", style={'font-size': '12px', 'font-weight': '600', 'color': '#c2c7ce'}),
            html.Th("STATUS", style={'font-size': '12px', 'font-weight': '600', 'color': '#c2c7ce'}),
            html.Th("NOTES", style={'font-size': '12px', 'font-weight': '600', 'color': '#c2c7ce'}),
            html.Th("ACTIONS", style={'font-size': '12px', 'font-weight': '600', 'color': '#c2c7ce'})
        ])
    ])
    
    return html.Div([
        html.Table([
            header,
            html.Tbody(table_rows)
        ], className="table table-hover")
    ], className="table-responsive")


def create_pagination_controls_clean(current_page, total_pages, page_size, total_items, filtered_items):
    """Create clean pagination controls with static IDs."""
    # Calculate display range
    start_item = current_page * page_size + 1 if filtered_items > 0 else 0
    end_item = min((current_page + 1) * page_size, filtered_items)
    
    # Create page buttons (show up to 5 pages around current)
    page_buttons = []
    
    if total_pages > 1:
        # Previous button
        prev_disabled = current_page == 0
        page_buttons.append(
            dbc.Button(
                "‹", 
                id="visible-prev-page-button", 
                className=f"pagination-btn {'disabled' if prev_disabled else ''}", 
                disabled=prev_disabled,
                size="sm"
            )
        )
        
        # Page number buttons
        start_page = max(0, current_page - 2)
        end_page = min(total_pages, start_page + 5)
        
        # Adjust start if we're near the end
        if end_page - start_page < 5:
            start_page = max(0, end_page - 5)
        
        for page_num in range(start_page, end_page):
            is_current = page_num == current_page
            page_buttons.append(
                dbc.Button(
                    str(page_num + 1),
                    id={"type": "visible-page-button", "index": page_num},
                    className=f"pagination-btn{'-active' if is_current else ''} me-1",
                    size="sm"
                )
            )
        
        # Next button
        next_disabled = current_page >= total_pages - 1
        page_buttons.append(
            dbc.Button(
                "›", 
                id="visible-next-page-button", 
                className=f"pagination-btn {'disabled' if next_disabled else ''}", 
                disabled=next_disabled,
                size="sm"
            )
        )
    
    return dbc.Row([
        dbc.Col([
            html.Div([
                html.Span("Show ", className="small text-secondary me-1"),
                dbc.Select(
                    id="visible-page-size-select",
                    options=[
                        {"label": "10", "value": 10},
                        {"label": "25", "value": 25},
                        {"label": "50", "value": 50},
                    ],
                    value=page_size,
                    style={"width": "70px", "display": "inline-block"},
                    className="pagination-select",
                ),
                html.Span(" entries", className="small text-secondary ms-1"),
            ], className="d-flex align-items-center"),
        ], width="auto"),
        dbc.Col([
            f"Showing {start_item}-{end_item} of {filtered_items}" + 
            (f" (filtered from {total_items})" if filtered_items != total_items else "") if filtered_items > 0 else "No entries to show", 
        ], className="small text-secondary d-flex align-items-center"),
        dbc.Col([
            html.Div(page_buttons, className="d-flex gap-1") if total_pages > 1 else html.Div(),
        ], width="auto", className="ms-auto"),
    ], align="center", className="mt-2", style={"padding": "0rem 1rem 1rem 1rem"})


def create_status_history_table_clean(history_data, app_id):
    """Create a clean status history table."""
    if not history_data:
        return html.P("No status history available.", className="text-muted")
    
    # Filter history for this application and sort by timestamp
    app_history = [h for h in history_data if h['application_id'] == app_id]
    app_history.sort(key=lambda x: x['timestamp'], reverse=True)
    
    table_rows = []
    for entry in app_history:
        # Use formatted timestamp if available, otherwise fallback to basic format
        display_time = entry.get('timestamp_formatted', entry['timestamp'])
        if not display_time or display_time == entry['timestamp']:
            # Fallback formatting if timestamp_formatted is not available
            timestamp = entry['timestamp']
            if len(timestamp) > 10:  # Has time component
                display_time = timestamp.split(' ')[0]
            else:
                display_time = timestamp
        
        row = html.Tr([
            html.Td(entry['status'], style={'font-weight': '500'}),
            html.Td(display_time, style={'font-size': '13px'}),
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