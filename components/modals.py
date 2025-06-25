import dash_bootstrap_components as dbc
from dash import html


def get_status_history_modal():
    """Status history modal component"""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Status History"), id="close-history-modal"),
            dbc.ModalBody([html.Div(id="history-modal-content")]),
        ],
        id="status-history-modal",
        is_open=False,
        size="lg",
    )
