# Callbacks package
from callbacks.applications import register_application_callbacks
from callbacks.status import register_status_callbacks
from callbacks.table import register_table_callbacks
from callbacks.history import register_history_callbacks
from callbacks.charts import register_charts_callbacks

def register_callbacks(app):
    """Register all application callbacks"""
    register_application_callbacks(app)
    register_status_callbacks(app)
    register_table_callbacks(app)
    register_history_callbacks(app)
    register_charts_callbacks(app) 