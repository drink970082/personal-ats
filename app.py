import dash
import dash_bootstrap_components as dbc
from components.layout import get_layout
from callbacks import register_callbacks
from database.manager import DatabaseManager
from config.settings import APP_TITLE, APP_HOST, APP_PORT, BOOTSTRAP_THEME
from utils.logger import logger

# Initialize Dash app with Bootstrap stylesheet
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = APP_TITLE

# Initialize database
db = DatabaseManager()
db.init_db()

# Set layout
app.layout = get_layout()

# Register callbacks
register_callbacks(app)

logger.info("system", "app_startup", {
    "app_title": APP_TITLE,
    "host": APP_HOST,
    "port": APP_PORT
})

if __name__ == "__main__":
    logger.info("system", "server_starting")
    app.run(host=APP_HOST, port=APP_PORT, debug=True)
