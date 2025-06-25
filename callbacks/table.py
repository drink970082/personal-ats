from dash import Input, Output, State, callback_context, no_update

def register_table_callbacks(app):
    """Register table pagination and filtering callbacks"""
    
    @app.callback(
        Output("pagination-store", "data"),
        [
            Input("page-size-dropdown", "value"),
            Input("prev-page-btn", "n_clicks"),
            Input("next-page-btn", "n_clicks"),
        ],
        State("pagination-store", "data"),
        prevent_initial_call=True,
    )
    def update_pagination(page_size, prev_clicks, next_clicks, current_data):
        if not current_data:
            current_data = {"current_page": 0, "page_size": 10}
        
        current_page = current_data.get("current_page", 0)
        current_page_size = current_data.get("page_size", 10)
        
        ctx = callback_context
        if ctx.triggered:
            trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
            
            if trigger_id == "page-size-dropdown" and page_size:
                return {"current_page": 0, "page_size": page_size}
            elif trigger_id == "prev-page-btn" and prev_clicks:
                return {"current_page": max(0, current_page - 1), "page_size": current_page_size}
            elif trigger_id == "next-page-btn" and next_clicks:
                return {"current_page": current_page + 1, "page_size": current_page_size}
        
        return current_data 