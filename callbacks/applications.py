import sqlite3
from datetime import datetime
from dash import Input, Output, State, callback_context, no_update, ALL
from database.manager import DatabaseManager
from utils.constants import DEFAULT_CATEGORY
from utils.logger import log_application_submit, log_application_delete, log_callback_error, log_user_action

db = DatabaseManager()

def register_application_callbacks(app):
    """Register application CRUD callbacks"""
    
    @app.callback(
        Output("update-trigger-store", "data", allow_duplicate=True),
        Output("success-notification", "is_open"),
        Output("success-notification", "children"),
        Output("success-notification", "header"),
        Output("success-notification", "icon"),
        Output("notification-area", "is_open"),
        Output("notification-area", "children"),
        Output("notification-area", "header"),
        Output("notification-area", "icon"),
        Input("submit-btn", "n_clicks"),
        [
            State("company-input", "value"),
            State("title-input", "value"),
            State("url-input", "value"),
            State("date-input", "value"),
            State("category-input", "value"),
            State("notes-input", "value"),
        ],
        prevent_initial_call=True,
    )
    def handle_submit(submit_clicks, company, title, url, date, category, notes):
        try:
            print(f"Submit callback triggered: clicks={submit_clicks}, company={company}, title={title}, date={date}")
            log_user_action("submit_form", {
                "company": company,
                "title": title,
                "has_url": bool(url),
                "category": category
            })
            
            if not submit_clicks or not company or not title or not date:
                print("Missing required fields or no clicks")
                return no_update, False, "", "Success", "success", False, "", "Notification", "info"
            
            # Check for duplicate application
            existing = db.check_duplicate_application(company, title)
            if existing:
                print(f"Duplicate found: {existing}")
                log_application_submit(company, title, existing[0], is_duplicate=True)
                # Return error message for duplicate
                return {
                    "source": "submit", 
                    "error": "duplicate",
                    "message": f"Application already exists for {existing[1]} - {existing[2]} (Status: {existing[4]})",
                    "timestamp": datetime.now().isoformat()
                }, False, "", "Success", "success", True, f"Application already exists for {existing[1]} - {existing[2]} (Status: {existing[4]})", "Warning", "warning"
            
            print("Adding application to database...")
            # No duplicate found, proceed with submission
            app_id = db.add_application(company, title, url, date, "Applied", category, notes)
            # Log initial status
            db.log_status_change(app_id, "Applied")
            
            print(f"Application added successfully with ID: {app_id}")
            log_application_submit(company, title, app_id, is_duplicate=False)
            
            return {
                "source": "submit", 
                "success": True,
                "message": f"Successfully added application for {company} - {title}",
                "timestamp": datetime.now().isoformat()
            }, True, f"Successfully added application for {company} - {title}", "Success", "success", False, "", "Notification", "info"
        except Exception as e:
            log_callback_error("handle_submit", e, {
                "company": company,
                "title": title
            })
            raise

    @app.callback(
        Output("update-trigger-store", "data", allow_duplicate=True),
        Input({"type": "delete-btn", "index": ALL}, "n_clicks"),
        State({"type": "delete-btn", "index": ALL}, "id"),
        prevent_initial_call=True,
    )
    def handle_delete_click(n_clicks, button_ids):
        try:
            ctx = callback_context
            if not ctx.triggered:
                return no_update
            
            # Find which button was clicked
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            trigger_id_dict = eval(trigger_id)
            app_id = trigger_id_dict["index"]
            
            # Check if this button was actually clicked
            for i, button_id in enumerate(button_ids):
                if button_id["index"] == app_id and n_clicks[i]:
                    # Get application details before deletion
                    conn = sqlite3.connect(db.db_path)
                    cursor = conn.cursor()
                    cursor.execute('SELECT company_name, job_title FROM applications WHERE id = ?', (app_id,))
                    app_details = cursor.fetchone()
                    conn.close()
                    
                    db.delete_application(app_id)
                    
                    if app_details:
                        log_application_delete(app_id, app_details[0], app_details[1])
                    
                    return {"source": "delete", "timestamp": datetime.now().isoformat()}
                    break
            
            return no_update
        except Exception as e:
            log_callback_error("handle_delete_click", e)
            raise

    @app.callback(
        [Output("company-input", "value"),
         Output("title-input", "value"),
         Output("url-input", "value"),
         Output("date-input", "value"),
         Output("category-input", "value"),
         Output("notes-input", "value")],
        Input("update-trigger-store", "data"),
        prevent_initial_call=True
    )
    def clear_form_after_submit(trigger_data):
        if trigger_data and trigger_data.get("source") == "submit" and trigger_data.get("success"):
            # Clear form after successful submission
            return "", "", "", datetime.now().date().isoformat(), DEFAULT_CATEGORY, ""
        return no_update, no_update, no_update, no_update, no_update, no_update 