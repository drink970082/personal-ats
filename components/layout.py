import dash_bootstrap_components as dbc
from dash import dcc, html
from components.forms import get_application_form
from components.tables import get_applications_table_container
from components.modals import get_status_history_modal
from components.charts import get_charts_container

def get_layout():
    """Main application layout"""
    # Notification area for alerts
    notification_area = dbc.Toast(
        id="notification-area",
        header="Notification",
        is_open=False,
        duration=4000,
        dismissable=True,
        style={
            "position": "fixed",
            "bottom": "20px",
            "right": "20px",
            "zIndex": 9999,
            "minWidth": "300px"
        }
    )
    
    # Success notification
    success_notification = dbc.Toast(
        id="success-notification",
        header="Success",
        is_open=False,
        duration=4000,
        dismissable=True,
        icon="success",
        style={
            "position": "fixed",
            "bottom": "20px",
            "right": "20px",
            "zIndex": 9999,
            "minWidth": "300px"
        }
    )

    return dbc.Container(
        [
            html.H1("Personal Application Tracking System", className="text-center my-4"),
            
            # Notification area for errors/success messages
            notification_area,
            
            # Success notification
            success_notification,
            
            # Application Input Form
            get_application_form(),
            
            # KPIs
            dbc.Row(id="kpi-container", className="mb-4 justify-content-center"),
            
            # Applications Table
            get_applications_table_container(),
            
            # Status History Modal
            get_status_history_modal(),
            
            # Charts
            *get_charts_container(),
            
            # Stores
            dcc.Store(id="update-trigger-store"),
            dcc.Store(id="pagination-store", data={"current_page": 0, "page_size": 10}),
            dcc.Store(id="modal-app-store", data=None),
        ],
        fluid=True,
    ) 