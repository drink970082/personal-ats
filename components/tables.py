import dash_bootstrap_components as dbc
from dash import dcc, html
from utils.constants import PAGE_SIZE_OPTIONS, DEFAULT_PAGE_SIZE

def get_applications_table_container():
    """Applications table container with filters and pagination"""
    return dbc.Card(
        [
            dbc.CardHeader(html.H5("Applications")),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Filter by Status:"),
                                    dcc.Dropdown(id="status-filter", multi=True, style={"height": "38px"}),
                                ],
                                md=4,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Filter by Category:"),
                                    dcc.Dropdown(
                                        id="category-filter", multi=True, style={"height": "38px"}
                                    ),
                                ],
                                md=4,
                            ),
                            dbc.Col(
                                [
                                    dbc.Label("Search:"),
                                    dbc.Input(
                                        id="search-input",
                                        type="text",
                                        placeholder="Search...",
                                        debounce=True,
                                        style={"height": "38px"},
                                    ),
                                ],
                                md=4,
                            ),
                        ]
                    ),
                    html.Div(id="applications-table-container"),
                ]
            ),
            dbc.CardFooter(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Label("Rows per page:"),
                                    dcc.Dropdown(
                                        id="page-size-dropdown",
                                        options=PAGE_SIZE_OPTIONS,
                                        value=DEFAULT_PAGE_SIZE,
                                        clearable=False,
                                        style={"width": "80px"},
                                    ),
                                ],
                                md=3,
                            ),
                            dbc.Col([html.Div(id="pagination-info", className="text-center")], md=6),
                            dbc.Col(
                                [
                                    dbc.ButtonGroup(
                                        [
                                            dbc.Button(
                                                "Previous",
                                                id="prev-page-btn",
                                                color="secondary",
                                                size="sm",
                                            ),
                                            dbc.Button(
                                                "Next", id="next-page-btn", color="secondary", size="sm"
                                            ),
                                        ]
                                    )
                                ],
                                md=3,
                                className="text-end",
                            ),
                        ]
                    )
                ]
            ),
        ],
        className="mb-4",
    ) 