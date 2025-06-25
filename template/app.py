import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import calendar

# --- Constants ---
COMPANIES = ["Google", "Microsoft", "Apple", "Amazon", "Meta", "Netflix", "Stripe", "Figma", "OpenAI"]
JOB_TITLES = ["Software Engineer", "ML Engineer", "Data Scientist", "Product Manager", "UX Designer"]
CATEGORIES = ["SWE/SDE", "MLE", "Data Science", "Product", "Design"]
STATUS_FLOW = ["Applied", "Assessment", "Interviewing", "Offer"]
CATEGORY_COLORS = ["#a8c7fa", "#74d2e7", "#f76f8e", "#54c184", "#f29e4c"]

# --- App Initialization ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# --- Data Generation ---
def generate_dummy_data():
    """Generate dummy application and history data for the dashboard."""
    apps_data = []
    history_data = []
    
    for i in range(100):
        company = random.choice(COMPANIES)
        title = random.choice(JOB_TITLES)
        category = random.choice(CATEGORIES)
        app_date = datetime.now() - timedelta(days=random.randint(0, 365))
        
        # Determine the application's progression through status flow
        final_stage_index = random.randint(0, len(STATUS_FLOW))
        current_status = ""
        
        # Create status history
        for j in range(final_stage_index):
            status = STATUS_FLOW[j]
            history_data.append({"app_id": i, "status": status})
            current_status = status
            if random.random() < 0.3:  # 30% chance to drop off early
                break
        
        # Determine final status based on progression
        if current_status == "Offer" and random.random() < 0.3:
            current_status = "Declined"
            history_data.append({"app_id": i, "status": "Declined"})
        elif current_status == "Applied" and (datetime.now() - app_date).days > 30:
            current_status = "No Response"
        elif current_status in ["Assessment", "Interviewing"] and random.random() < 0.4:
            current_status = "Rejected"
            history_data.append({"app_id": i, "status": "Rejected"})
        elif final_stage_index == 0:
            current_status = "Applied"
            history_data.append({"app_id": i, "status": "Applied"})

        apps_data.append({
            "id": i,
            "company": company,
            "title": title,
            "category": category,
            "status": current_status,
            "date_applied": app_date.strftime("%Y-%m-%d"),
            "url": f"https://careers.google.com/jobs/results/",
            "notes": "Lorem ipsum dolor sit amet." if random.random() > 0.5 else "",
        })
        
    df_apps = pd.DataFrame(apps_data)
    df_history = pd.DataFrame(history_data)
    
    # Calculate status transitions for Sankey diagram
    df_history["next_status"] = df_history.groupby("app_id")["status"].shift(-1)
    sankey_data = df_history.dropna().groupby(["status", "next_status"]).size().reset_index(name="value")
    
    return df_apps, sankey_data

# --- Data Initialization ---
df, sankey_data = generate_dummy_data()
all_statuses = list(pd.unique(df["status"]))

# --- KPI Calculations ---
def calculate_kpis(dataframe):
    """Calculate key performance indicators from the applications data."""
    return {
        "total": len(dataframe),
        "assessment": len(dataframe[dataframe["status"] == "Assessment"]),
        "interviewing": len(dataframe[dataframe["status"] == "Interviewing"]),
        "offer": len(dataframe[dataframe["status"] == "Offer"]),
        "rejected": len(dataframe[dataframe["status"] == "Rejected"]),
        "no_response": len(dataframe[dataframe["status"] == "No Response"]),
    }

kpis = calculate_kpis(df)

# --- Styling ---
CUSTOM_CSS = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>ATS Dashboard</title>
        {%favicon%}
        {%css%}
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
        <style>
            /* --- Material 3 Dark Theme Color Palette --- */
            :root {
                --md-sys-color-primary-rgb: 168, 199, 250;
                --md-sys-color-primary: #a8c7fa;
                --md-sys-color-on-primary: #0d3058;
                --md-sys-color-surface-container: #212429;
                --md-sys-color-surface-container-high: #2c2f33;
                --md-sys-color-surface-container-highest: #373a3e;
                --md-sys-color-surface: #131416;
                --md-sys-color-on-surface: #e2e2e6;
                --md-sys-color-on-surface-variant: #c2c7ce;
                --md-sys-color-outline: #8c9199;
                --md-sys-color-outline-variant: #42474e;
                --md-sys-color-error: #f2b8b5;
            }
            
            /* --- Base Styles --- */
            body {
                background-color: var(--md-sys-color-surface) !important;
                color: var(--md-sys-color-on-surface) !important;
                font-family: 'Roboto', sans-serif;
                font-size: 14px;
            }
            h1, h2, h3, h4, h5, h6, .h1, .h2, .h3, .h4, .h5, .h6 {
                color: var(--md-sys-color-on-surface) !important;
            }
            .fade-in { 
                animation: fadeIn 0.4s ease-in-out; 
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(8px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            /* --- Component Containers --- */
            .card-component {
                background-color: var(--md-sys-color-surface-container);
                border: 1px solid var(--md-sys-color-outline-variant);
                border-radius: 12px;
                padding: 1.25rem;
            }

            /* --- Form Controls --- */
            .form-control, .form-select, .Select-control {
                background-color: var(--md-sys-color-surface-container-highest) !important;
                border: 1px solid var(--md-sys-color-outline-variant) !important;
                border-radius: 4px !important;
                color: var(--md-sys-color-on-surface) !important;
                padding: 0.5rem 0.75rem !important;
                transition: all 0.2s ease-in-out !important;
                height: 38px !important;
                min-height: 38px !important;
            }
            .form-control:focus, .form-select:focus, .Select-control:focus-within {
                box-shadow: 0 0 0 1px var(--md-sys-color-primary) !important;
                border-color: var(--md-sys-color-primary) !important;
                background-color: var(--md-sys-color-surface-container-highest) !important;
            }
            .form-control::placeholder { 
                color: var(--md-sys-color-on-surface-variant) !important; 
                opacity: 1; 
            }
            .Select-input input { color: var(--md-sys-color-on-surface) !important; }
            .Select-value-label, .Select-placeholder { 
                color: var(--md-sys-color-on-surface-variant) !important; 
            }
            .Select-menu-outer {
                background-color: var(--md-sys-color-surface-container-highest) !important;
                border: 1px solid var(--md-sys-color-outline-variant) !important;
                border-radius: 4px !important;
            }
            .Select-option {
                background-color: var(--md-sys-color-surface-container-highest);
                color: var(--md-sys-color-on-surface);
            }
            .Select-option.is-focused {
                background-color: var(--md-sys-color-primary) !important;
                color: var(--md-sys-color-on-primary) !important;
            }

            /* --- Button Styles --- */
            .btn-primary {
                background-color: var(--md-sys-color-primary) !important;
                color: var(--md-sys-color-on-primary) !important;
                border: none !important;
                border-radius: 20px !important;
                font-weight: 500;
                padding: 0.5rem 1.25rem;
            }
            .btn-m3-outline {
                background-color: transparent !important;
                border: 1px solid var(--md-sys-color-outline) !important;
                color: var(--md-sys-color-primary) !important;
                border-radius: 20px !important;
                font-weight: 500;
                padding: 0.4rem 1rem;
                font-size: 13px;
                line-height: 1.5;
                transition: background-color 0.2s ease;
            }
            .btn-m3-outline:hover {
                background-color: rgba(var(--md-sys-color-primary-rgb), 0.08) !important;
            }
            .btn-m3-text-danger {
                background-color: transparent !important;
                border: 1px solid var(--md-sys-color-error) !important;
                color: var(--md-sys-color-error) !important;
                border-radius: 20px !important;
                font-weight: 500;
                padding: 0.4rem 1rem;
                font-size: 13px;
                line-height: 1.5;
                transition: background-color 0.2s ease;
            }
            .btn-m3-text-danger:hover {
                background-color: rgba(242, 184, 181, 0.08) !important;
            }

            /* --- Stats Cards --- */
            .stats-card {
                background-color: var(--md-sys-color-surface-container-high);
                border: 1px solid var(--md-sys-color-outline-variant);
                border-radius: 12px;
                padding: 1rem;
                text-align: center;
                display: flex;
                flex-direction: column;
                justify-content: center;
                min-height: 110px;
            }
            .stat-number { 
                font-size: 1.75rem; 
                font-weight: 500; 
                color: var(--md-sys-color-primary); 
            }
            .stat-label { 
                font-size: 0.75rem; 
                color: var(--md-sys-color-on-surface-variant); 
                text-transform: uppercase; 
                letter-spacing: 0.8px; 
                line-height: 1.4; 
                margin: 0 auto; 
            }
            
            /* --- Table Styles --- */
            .table {
                --bs-table-bg: var(--md-sys-color-surface-container);
                --bs-table-color: var(--md-sys-color-on-surface);
                --bs-table-border-color: var(--md-sys-color-outline-variant);
                --bs-table-hover-bg: var(--md-sys-color-surface-container-high);
                --bs-table-hover-color: var(--md-sys-color-on-surface);
                --bs-table-striped-bg: var(--md-sys-color-surface-container);
                --bs-table-striped-color: var(--md-sys-color-on-surface);
                vertical-align: middle;
            }
            .table > :not(caption) > * > * { padding: 0.75rem 0.75rem; }
            .status-cell { display: flex; align-items: center; gap: 8px; }
            .status-indicator { 
                width: 8px; 
                height: 8px; 
                border-radius: 50%; 
                flex-shrink: 0; 
            }
            .status-indicator.status-applied { background-color: #5d8eff; }
            .status-indicator.status-assessment { background-color: #f29e4c; }
            .status-indicator.status-interviewing { background-color: #f76f8e; }
            .status-indicator.status-offer { background-color: #54c184; }
            .status-indicator.status-rejected { background-color: #909da2; }
            .status-indicator.status-no-response { background-color: #c2c7ce; }

            /* --- Tab Styles --- */
            .nav-tabs { border-bottom: 1px solid var(--md-sys-color-outline-variant) !important; }
            .nav-tabs .nav-link { 
                background: transparent; 
                border: none; 
                color: var(--md-sys-color-on-surface-variant); 
                transition: all 0.2s ease;
            }
            .nav-tabs .nav-link.active {
                color: var(--md-sys-color-primary) !important;
                background-color: rgba(var(--md-sys-color-primary-rgb), 0.04) !important;
                border-bottom: 2px solid var(--md-sys-color-primary) !important;
                border-radius: 4px 4px 0 0 !important;
            }
            
            /* --- Filter/Search Row --- */
            .filter-search-row {
                padding: 0 1rem;
                margin: 1rem 0;
            }
            
            /* --- Table Spacing --- */
            .table-responsive {
                margin-bottom: 0rem !important;
            }
            
            /* --- Pagination Styles --- */
            .pagination-select {
                height: 24px !important;
                min-height: 24px !important;
                font-size: 0.875rem !important;
                padding: 0 0.5rem !important;
            }
            .pagination-btn {
                background-color: transparent !important;
                border: 1px solid var(--md-sys-color-outline-variant) !important;
                color: var(--md-sys-color-on-surface-variant) !important;
                border-radius: 6px !important;
                font-weight: 400 !important;
                padding: 0.25rem 0.5rem !important;
                font-size: 0.875rem !important;
                min-width: 32px !important;
            }
            .pagination-btn:hover {
                background-color: var(--md-sys-color-surface-container-high) !important;
                border-color: var(--md-sys-color-outline) !important;
            }
            .pagination-btn-active {
                background-color: var(--md-sys-color-surface-container-highest) !important;
                border: 1px solid var(--md-sys-color-primary) !important;
                color: var(--md-sys-color-primary) !important;
                border-radius: 6px !important;
                font-weight: 500 !important;
            }
            
            /* --- Notes Textarea --- */
            .notes-textarea {
                min-height: 80px !important;
                resize: vertical !important;
            }
        </style>
    </head>
    <body> {%app_entry%} <footer> {%config%} {%scripts%} {%renderer%} </footer> </body>
</html>
"""

app.index_string = CUSTOM_CSS

# --- Chart Creation Functions ---
def create_styled_chart(figure):
    """Apply Material 3 dark theme styling to Plotly figures."""
    figure.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#c2c7ce",
        margin=dict(t=40, b=20, l=20, r=20),
        showlegend=False,
        title_font_color="#e2e2e6",
    )
    if "xaxis" in figure.layout:
        figure.update_xaxes(gridcolor="#42474e")
    if "yaxis" in figure.layout:
        figure.update_yaxes(gridcolor="#42474e")
    return dcc.Graph(figure=figure, config={"displayModeBar": False})

def create_sankey_chart(sankey_data):
    """Create a Sankey diagram showing application status flow."""
    all_nodes = list(pd.unique(sankey_data[["status", "next_status"]].values.ravel("K")))
    node_map = {node: i for i, node in enumerate(all_nodes)}
    
    fig = go.Figure(
        go.Sankey(
            arrangement="snap",
            node=dict(
                pad=15, 
                thickness=20, 
                line=dict(color="black", width=0.5), 
                label=all_nodes, 
                color="#a8c7fa"
            ),
            link=dict(
                source=sankey_data["status"].map(node_map),
                target=sankey_data["next_status"].map(node_map),
                value=sankey_data["value"],
                color="rgba(168, 199, 250, 0.6)",
            ),
        )
    )
    fig.update_layout(title_text="Application Status Flow", font_size=10)
    return fig

def create_timeline_heatmap(dataframe):
    """Create a timeline heatmap showing application activity."""
    df_copy = dataframe.copy()
    df_copy["date_applied"] = pd.to_datetime(df_copy["date_applied"])
    activity = df_copy["date_applied"].dt.date.value_counts().sort_index()
    all_days = pd.date_range(start=activity.index.min(), end=activity.index.max(), freq="D")
    activity = activity.reindex(all_days, fill_value=0)
    
    fig = go.Figure(
        go.Heatmap(
            z=activity.values,
            x=activity.index,
            colorscale=[[0, "#2c2f33"], [1, "#a8c7fa"]],
            showscale=False,
        )
    )
    fig.update_layout(title_text="Application Timeline")
    return fig

def create_category_pie_chart(dataframe):
    """Create a pie chart showing category distribution."""
    fig = px.pie(
        dataframe, 
        names="category", 
        title="Category Distribution", 
        hole=0.6,
        color_discrete_sequence=CATEGORY_COLORS
    )
    fig.update_traces(marker=dict(line=dict(color="var(--md-sys-color-surface-container)", width=2)))
    fig.update_layout(legend=dict(font_color="var(--md-sys-color-on-surface)"))
    return fig

# --- Initialize Charts ---
sankey_fig = create_sankey_chart(sankey_data)
heatmap_fig = create_timeline_heatmap(df)
category_fig = create_category_pie_chart(df)

# --- Component Creation Functions ---
def create_stats_card(number, label):
    """Create a KPI statistics card."""
    label_content = []
    if " " in label:
        parts = label.split(" ", 1)
        label_content = [parts[0], html.Br(), parts[1]]
    else:
        label_content = [label, html.Br(), html.Span("\u00a0", style={"opacity": 0})]

    return html.Div(
        [
            html.P(number, className="stat-number mb-1"), 
            html.P(label_content, className="stat-label mb-0")
        ],
        className="stats-card",
    )

def create_application_table(dataframe, statuses):
    """Create the main applications table."""
    return dbc.Table(
        [
            html.Thead(
                html.Tr([
                    html.Th("Company"),
                    html.Th("Title"),
                    html.Th("Date Applied"),
                    html.Th("Status"),
                    html.Th("Actions", style={"textAlign": "right"}),
                ])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(row["company"]),
                    html.Td(row["title"]),
                    html.Td(row["date_applied"]),
                    html.Td(
                        html.Div([
                            html.Span(
                                className=f"status-indicator status-{row['status'].lower().replace(' ', '-')}"
                            ),
                            dbc.Select(
                                options=[{"label": s, "value": s} for s in statuses],
                                value=row["status"],
                                size="sm",
                            ),
                        ], className="status-cell")
                    ),
                    html.Td([
                        dbc.Button("History", className="btn-m3-outline me-1"),
                        dbc.Button("Delete", className="btn-m3-text-danger"),
                    ], style={"textAlign": "right"}),
                ]) for _, row in dataframe.iterrows()
            ])
        ],
        striped=True,
        hover=True,
        responsive=True,
    )

def create_filter_search_row(statuses, categories):
    """Create the filter and search controls."""
    return html.Div([
        dbc.Row([
            dbc.Col(
                dbc.Select(
                    options=[{"label": "All Statuses", "value": "all"}] + [{"label": s, "value": s} for s in statuses],
                    value="all",
                    placeholder="Filter by status...",
                ),
                md=4,
            ),
            dbc.Col(
                dbc.Select(
                    options=[{"label": "All Categories", "value": "all"}] + [{"label": c, "value": c} for c in categories],
                    value="all",
                    placeholder="Filter by category...",
                ),
                md=4,
            ),
            dbc.Col(
                dbc.Input(placeholder="Search...", debounce=True), 
                md=4
            ),
        ])
    ], className="filter-search-row")

def create_pagination_controls():
    """Create pagination controls with page numbers and entries selector."""
    return dbc.Row([
        dbc.Col(
            html.Div([
                html.Span("Show ", className="small text-secondary me-1"),
                dbc.Select(
                    options=[
                        {"label": "10", "value": 10},
                        {"label": "25", "value": 25},
                        {"label": "50", "value": 50},
                    ],
                    value=10,
                    style={"width": "60px", "display": "inline-block"},
                    className="pagination-select",
                ),
                html.Span(" entries", className="small text-secondary ms-1"),
            ], className="d-flex align-items-center"),
            width="auto",
        ),
        dbc.Col("Showing 1-10 of 100", className="small text-secondary"),
        dbc.Col(
            html.Div([
                dbc.Button("‹", className="pagination-btn me-1"),
                dbc.Button("1", className="pagination-btn-active me-1"),
                dbc.Button("2", className="pagination-btn me-1"),
                dbc.Button("3", className="pagination-btn me-1"),
                dbc.Button("4", className="pagination-btn me-1"),
                dbc.Button("5", className="pagination-btn me-1"),
                dbc.Button("›", className="pagination-btn"),
            ], className="d-flex"),
            width="auto",
            className="ms-auto",
        ),
    ], align="center", className="mt-2", style={"padding": "0rem 1rem 1rem 1rem"})

def create_application_form(categories):
    """Create the application submission form."""
    return html.Div([
        html.H2("Add Application", className="h5 mb-3"),
        dbc.Input(placeholder="Company Name", className="mb-2"),
        dbc.Input(placeholder="Job Title", className="mb-2"),
        dbc.Input(placeholder="Application URL", type="url", className="mb-2"),
        dbc.Select(
            options=[{"label": c, "value": c} for c in categories],
            value=categories[0],
            placeholder="Category",
            className="mb-2",
        ),
        dbc.Textarea(placeholder="Notes...", className="mb-2 notes-textarea"),
        dbc.Input(type="date", value=datetime.now().date().isoformat(), className="mb-2"),
        dbc.Button("Submit", color="primary", className="w-100 mt-2"),
    ], className="card-component fade-in")

# --- Main Layout ---
def create_layout():
    """Create the main application layout."""
    return dbc.Container([
        # Header
        html.Div([
            html.H1("ATS Dashboard", className="h3 mb-1", style={"fontWeight": "400"}),
            html.P(
                "Application Tracking System",
                className="mb-0",
                style={"color": "var(--md-sys-color-on-surface-variant)"},
            ),
        ], className="my-4 fade-in"),

        # Main Content
        dbc.Row([
            # Left Column: Stats & Form
            dbc.Col([
                # KPI Stats
                dbc.Row([
                    dbc.Col(create_stats_card(kpis["total"], "Applied"), md=4),
                    dbc.Col(create_stats_card(kpis["assessment"], "Assessment"), md=4),
                    dbc.Col(create_stats_card(kpis["interviewing"], "Interviewing"), md=4),
                ], className="g-2 mb-2"),
                dbc.Row([
                    dbc.Col(create_stats_card(kpis["offer"], "Offer"), md=4),
                    dbc.Col(create_stats_card(kpis["rejected"], "Rejected"), md=4),
                    dbc.Col(create_stats_card(kpis["no_response"], "No Response"), md=4),
                ], className="g-2 mb-3"),
                
                # Application Form
                create_application_form(df["category"].unique()),
            ], md=3),

            # Right Column: Tabs for Table & Charts
            dbc.Col(
                html.Div(
                    dbc.Tabs([
                        # Applications Tab
                        dbc.Tab([
                            create_filter_search_row(all_statuses, df["category"].unique()),
                            html.Div(create_application_table(df, all_statuses), className="table-responsive"),
                            create_pagination_controls(),
                        ], label="Applications"),
                        
                        # Analytics Tab
                        dbc.Tab([
                            dbc.Row([
                                dbc.Col(create_styled_chart(sankey_fig), md=12),
                                dbc.Col(create_styled_chart(heatmap_fig), md=8),
                                dbc.Col(create_styled_chart(category_fig), md=4),
                            ], className="g-3 mt-1")
                        ], label="Analytics"),
                    ]),
                    className="card-component fade-in p-0",
                ),
                md=9,
            ),
        ], className="g-3"),
    ], fluid=True, className="p-3")

# --- Set Layout ---
app.layout = create_layout()

# --- Run App ---
if __name__ == "__main__":
    app.run(debug=True, port=8052)
