import sqlite3
from datetime import datetime
from dash import Input, Output, State, callback_context, no_update, ALL, html, dcc
import dash_bootstrap_components as dbc
from database.manager import DatabaseManager
from utils.constants import STATUS_OPTIONS

db = DatabaseManager()


def register_history_callbacks(app):
    """Register status history callbacks"""

    @app.callback(
        Output("update-trigger-store", "data", allow_duplicate=True),
        Input({"type": "history-btn", "index": ALL}, "n_clicks"),
        State({"type": "history-btn", "index": ALL}, "id"),
        prevent_initial_call=True,
    )
    def handle_history_button_click(history_clicks, button_ids):
        ctx = callback_context
        if not ctx.triggered:
            return no_update

        # Find which button was clicked
        for i, button_id in enumerate(button_ids):
            if history_clicks[i] and history_clicks[i] > 0:
                app_id = button_id["index"]
                return {"source": "history-click", "app_id": app_id, "timestamp": datetime.now().isoformat()}

        return no_update

    @app.callback(
        [
            Output("status-history-modal", "is_open"),
            Output("history-modal-content", "children"),
            Output("modal-app-store", "data"),
        ],
        [
            Input("update-trigger-store", "data"),
        ],
        State("status-history-modal", "is_open"),
        State("modal-app-store", "data"),
        prevent_initial_call=True,
    )
    def handle_history_modal(trigger_data, modal_is_open, current_app_id):
        ctx = callback_context
        if not ctx.triggered:
            return False, [], None

        # Only one trigger: update-trigger-store
        source = trigger_data.get("source") if trigger_data else None

        if source == "history-click":
            app_id = trigger_data.get("app_id")
            if not modal_is_open:
                modal_content = _create_modal_content(app_id)
                return True, modal_content, app_id
        elif source in ["history-edit", "history-delete"] and modal_is_open and current_app_id:
            modal_content = _create_modal_content(current_app_id)
            return True, modal_content, current_app_id
        elif source == "close":
            return False, [], None

        return no_update, no_update, no_update

    def _create_modal_content(app_id):
        # Get application details
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT company_name, job_title FROM applications WHERE id = ?", (app_id,))
        app_result = cursor.fetchone()

        if app_result:
            company_name, job_title = app_result

            # Get status history
            cursor.execute(
                "SELECT id, status, timestamp FROM status_history WHERE application_id = ? ORDER BY id DESC",
                (app_id,),
            )
            history_data = cursor.fetchall()
            conn.close()

            # Create history table
            history_rows = []
            for hist_id, status, timestamp in history_data:
                # Status dropdown for editing
                status_options = [{"label": s, "value": s} for s in STATUS_OPTIONS]

                status_dropdown = dcc.Dropdown(
                    id={"type": "history-status-dropdown", "index": hist_id},
                    options=status_options,
                    value=status,
                    clearable=False,
                    style={"width": "150px", "height": "35px", "fontSize": "12px"},
                )

                # Delete button for history entry
                delete_btn = dbc.Button(
                    "Delete",
                    id={"type": "history-delete-btn", "index": hist_id},
                    color="danger",
                    size="sm",
                    style={"fontSize": "10px"},
                )

                history_rows.append(
                    html.Tr(
                        [
                            html.Td(timestamp),
                            html.Td(status_dropdown),
                            html.Td(delete_btn),
                        ]
                    )
                )

            history_table = dbc.Table(
                [
                    html.Thead(
                        [
                            html.Tr(
                                [
                                    html.Th("Timestamp"),
                                    html.Th("Status"),
                                    html.Th("Actions"),
                                ]
                            )
                        ]
                    ),
                    html.Tbody(history_rows),
                ],
                bordered=True,
                hover=True,
                responsive=True,
                striped=True,
            )

            modal_content = [
                html.H5(f"Status History for {company_name} - {job_title}"),
                html.Hr(),
                history_table if history_rows else html.P("No status history found.", className="text-muted"),
                html.Br(),
            ]

            return modal_content

        conn.close()
        return html.P("No application found.", className="text-muted")

    @app.callback(
        Output("update-trigger-store", "data", allow_duplicate=True),
        Input({"type": "history-status-dropdown", "index": ALL}, "value"),
        State({"type": "history-status-dropdown", "index": ALL}, "id"),
        prevent_initial_call=True,
    )
    def handle_history_status_change(status_values, dropdown_ids):
        ctx = callback_context
        if not ctx.triggered:
            return no_update

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_id_dict = eval(trigger_id)
        hist_id = trigger_id_dict["index"]

        # Get the new status value
        for i, dropdown_id in enumerate(dropdown_ids):
            if dropdown_id["index"] == hist_id:
                new_status = status_values[i]
                if new_status and new_status.strip():
                    # Check if status actually changed
                    conn = sqlite3.connect(db.db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT status FROM status_history WHERE id = ?", (hist_id,))
                    current_status = cursor.fetchone()

                    if current_status and current_status[0] != new_status:
                        # Update the status history entry
                        cursor.execute("UPDATE status_history SET status = ? WHERE id = ?", (new_status, hist_id))
                        conn.commit()
                        conn.close()
                        return {"source": "history-edit", "timestamp": datetime.now().isoformat()}
                    else:
                        conn.close()
                break

        return no_update

    @app.callback(
        Output("update-trigger-store", "data", allow_duplicate=True),
        Input({"type": "history-delete-btn", "index": ALL}, "n_clicks"),
        State({"type": "history-delete-btn", "index": ALL}, "id"),
        prevent_initial_call=True,
    )
    def handle_history_delete(n_clicks, button_ids):
        ctx = callback_context
        if not ctx.triggered:
            return no_update

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_id_dict = eval(trigger_id)
        hist_id = trigger_id_dict["index"]

        # Check if this button was actually clicked
        for i, button_id in enumerate(button_ids):
            if button_id["index"] == hist_id and n_clicks[i]:
                # Get the application ID and check if this is the latest entry
                conn = sqlite3.connect(db.db_path)
                cursor = conn.cursor()
                
                # Get the application ID for this history entry
                cursor.execute("SELECT application_id FROM status_history WHERE id = ?", (hist_id,))
                app_result = cursor.fetchone()
                
                if app_result:
                    app_id = app_result[0]
                    
                    # Check if this is the latest history entry (highest ID)
                    cursor.execute("""
                        SELECT id FROM status_history 
                        WHERE application_id = ? 
                        ORDER BY id DESC 
                        LIMIT 1
                    """, (app_id,))
                    latest_hist = cursor.fetchone()
                    
                    # Delete the history entry
                    db.delete_status_history(hist_id)
                    
                    # If this was the latest entry, update the application status to the new latest
                    if latest_hist and latest_hist[0] == hist_id:
                        # Get the new latest status
                        cursor.execute("""
                            SELECT status FROM status_history 
                            WHERE application_id = ? 
                            ORDER BY id DESC 
                            LIMIT 1
                        """, (app_id,))
                        new_latest = cursor.fetchone()
                        
                        if new_latest:
                            # Update application status to the new latest
                            db.update_application(app_id, "status", new_latest[0])
                        else:
                            # No history left, set to "Applied" as default
                            db.update_application(app_id, "status", "Applied")
                
                conn.close()
                return {"source": "history-delete", "timestamp": datetime.now().isoformat()}
                break

        return no_update
