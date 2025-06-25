import dash_bootstrap_components as dbc
from dash import dcc, html
from datetime import datetime
from utils.constants import CATEGORY_OPTIONS, DEFAULT_CATEGORY


def get_application_form():
    """Application input form component"""
    return dbc.Card(
        [
            dbc.CardHeader(html.H4("New Application Entry")),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Company Name"),
                                    dbc.Input(
                                        id="company-input",
                                        placeholder="Enter company name",
                                        type="text",
                                        required=True,
                                    ),
                                ],
                                md=6,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Job Title"),
                                    dbc.Input(
                                        id="title-input", placeholder="Enter job title", type="text", required=True
                                    ),
                                ],
                                md=6,
                            ),
                        ],
                        style={"margin-bottom": "10px"},
                        className="mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Application URL"),
                                    dbc.Input(
                                        id="url-input", placeholder="https://...", type="url", required=True
                                    ),
                                ],
                                md=12,
                            ),
                        ],
                        className="mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Date Applied"),
                                    dbc.Input(
                                        id="date-input",
                                        type="date",
                                        value=datetime.now().date().isoformat(),
                                        required=True,
                                    ),
                                ],
                                md=6,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Category"),
                                    dcc.Dropdown(
                                        id="category-input",
                                        options=CATEGORY_OPTIONS,
                                        value=DEFAULT_CATEGORY,
                                        clearable=False,
                                    ),
                                ],
                                md=6,
                            ),
                        ],
                        className="mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Notes"),
                                    dbc.Textarea(id="notes-input", placeholder="Add notes..."),
                                ],
                                md=12,
                            ),
                        ],
                        className="mb-3",
                    ),
                    dbc.Button("Submit Application", id="submit-btn", color="primary", className="w-100"),
                ]
            ),
        ],
        className="mb-4",
    )
