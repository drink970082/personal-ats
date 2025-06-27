"""Chart components for the dashboard."""

import dash_bootstrap_components as dbc
from dash import dcc, html
from utils.charts import create_timeline_heatmap, create_category_donut, create_sankey_chart, create_status_distribution


def create_charts_section(applications_data, status_history_data):
    """Create the charts section with three-row layout for better chart proportions."""
    return html.Div([
        # Row 1: Sankey Chart (Full Width)
        dbc.Row([
            dbc.Col([
                html.H5("Application Status Flow", className="mb-3", style={'color': '#e2e2e6', 'font-family': 'Roboto'}),
                dcc.Graph(
                    figure=create_sankey_chart(applications_data, status_history_data),
                    config={'displayModeBar': False},
                    style={'height': '400px'}
                )
            ], md=12)
        ], className="mb-4"),
        
        # Row 2: Timeline Heatmap (Full Width)
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    figure=create_timeline_heatmap(applications_data),
                    config={'displayModeBar': False}
                )
            ], md=12)
        ], className="mb-4"),
        
        # Row 3: Category Donut + Status Distribution (Side by Side)
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    figure=create_category_donut(applications_data),
                    config={'displayModeBar': False},
                    style={'height': '400px'}
                )
            ], md=6),
            dbc.Col([
                dcc.Graph(
                    figure=create_status_distribution(applications_data),
                    config={'displayModeBar': False},
                    style={'height': '400px'}
                )
            ], md=6)
        ], className="mb-3")
    ])


def create_empty_charts():
    """Create empty charts when no data is available."""
    return html.Div([
        html.P(
            "Charts will appear here once you add some applications.",
            className="text-center py-5",
            style={'color': '#c2c7ce'}
        )
    ]) 