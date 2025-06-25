import dash_bootstrap_components as dbc
from dash import dcc, html

def get_charts_container():
    """Charts container with all visualization components"""
    return [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Status Flow"),
                                dbc.CardBody([dcc.Graph(id="status-chart")]),
                            ]
                        )
                    ],
                    md=12,
                    className="mb-4",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Category Distribution"),
                                dbc.CardBody([dcc.Graph(id="category-chart")]),
                            ]
                        )
                    ],
                    md=12,
                    className="mb-4",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Application Heatmap (Last 365 Days)"),
                                dbc.CardBody([dcc.Graph(id="timeline-chart")]),
                            ]
                        )
                    ],
                    md=12,
                    className="mb-4",
                ),
            ]
        ),
    ] 