import sqlite3
from datetime import datetime
from dash import Input, Output, State, callback_context, no_update, ALL
from database.manager import DatabaseManager

db = DatabaseManager()

def register_status_callbacks(app):
    """Register status and notes update callbacks"""
    
    @app.callback(
        Output("update-trigger-store", "data", allow_duplicate=True),
        Input({"type": "status-dropdown", "index": ALL}, "value"),
        State({"type": "status-dropdown", "index": ALL}, "id"),
        prevent_initial_call=True,
    )
    def handle_status_change(status_values, dropdown_ids):
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        
        # Find which dropdown was changed
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_id_dict = eval(trigger_id)
        app_id = trigger_id_dict["index"]
        
        # Get the new status value
        for i, dropdown_id in enumerate(dropdown_ids):
            if dropdown_id["index"] == app_id:
                new_status = status_values[i]
                if new_status and new_status.strip():
                    # Check if status actually changed
                    conn = sqlite3.connect(db.db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT status FROM applications WHERE id = ?", (app_id,))
                    current_status = cursor.fetchone()
                    conn.close()
                    
                    if current_status and current_status[0] != new_status:
                        db.update_application(app_id, "status", new_status)
                        db.log_status_change(app_id, new_status)
                        return {"source": "status-change", "timestamp": datetime.now().isoformat()}
                    else:
                        return no_update
                break
        
        return no_update

    @app.callback(
        Output("update-trigger-store", "data", allow_duplicate=True),
        Input({"type": "notes-textarea", "index": ALL}, "value"),
        State({"type": "notes-textarea", "index": ALL}, "id"),
        prevent_initial_call=True,
    )
    def handle_notes_change(notes_values, textarea_ids):
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        
        # Find which textarea was changed
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        trigger_id_dict = eval(trigger_id)
        app_id = trigger_id_dict["index"]
        
        # Get the new notes value
        for i, textarea_id in enumerate(textarea_ids):
            if textarea_id["index"] == app_id:
                new_notes = notes_values[i] if notes_values[i] else ""
                db.update_application(app_id, "notes", new_notes)
                return {"source": "notes-change", "timestamp": datetime.now().isoformat()}
                break
        
        return no_update 