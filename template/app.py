import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import calendar
import numpy as np

# --- Constants ---
COMPANIES = ["Google", "Microsoft", "Apple", "Amazon", "Meta", "Netflix", "Stripe", "Figma", "OpenAI"]
JOB_TITLES = [
    "Software Engineer",
    "ML Engineer",
    "Data Scientist",
    "Product Manager",
    "UX Designer",
    "Quantitative Developer",
    "AI Engineer",
]
CATEGORIES = ["SWE", "MLE", "DS", "DA", "Quant Dev", "Quant Analyst", "Quant Trader", "AI Engineer", "Others"]
STATUSES = [
    "Applied",
    "Online Assessment",
    "Interviewing: 1st round",
    "Interviewing: 2nd round",
    "Interviewing: 3rd round",
    "Interviewing: 4th round",
    "Interviewing: 5th round",
    "Rejected",
    "Offer",
]
CATEGORY_COLORS = [
    "#a8c7fa",
    "#74d2e7",
    "#f76f8e",
    "#54c184",
    "#f29e4c",
    "#f5d384",
    "#b49ed1",
    "#83d9b3",
    "#d3d3d3",
]

# --- App Initialization ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


# --- Data Generation ---
def generate_dummy_data():
    """Generate dummy application and history data for the dashboard."""
    apps_data = []
    history_data = []
    all_interview_rounds = [s for s in STATUSES if s.startswith("Interviewing")]

    for i in range(100):
        company = random.choice(COMPANIES)
        title = random.choice(JOB_TITLES)
        category = random.choice(CATEGORIES)
        app_date = datetime.now() - timedelta(days=random.randint(0, 365))

        # Determine the application's progression through status flow
        current_status = "Applied"
        history_data.append({"app_id": i, "status": "Applied", "timestamp": app_date})

        # Chance to go to Assessment
        if random.random() > 0.3:
            current_status = "Online Assessment"
            history_data.append(
                {
                    "app_id": i,
                    "status": current_status,
                    "timestamp": app_date + timedelta(days=random.randint(1, 10)),
                }
            )

            # Chance to go to interviews
            if random.random() > 0.4:
                num_interviews = random.randint(1, len(all_interview_rounds))
                last_date = app_date + timedelta(days=random.randint(1, 10))
                for j in range(num_interviews):
                    current_status = all_interview_rounds[j]
                    last_date = last_date + timedelta(days=random.randint(7, 21))
                    history_data.append({"app_id": i, "status": current_status, "timestamp": last_date})
                    if random.random() < 0.3:  # Chance to get rejected after an interview
                        current_status = "Rejected"
                        history_data.append(
                            {
                                "app_id": i,
                                "status": "Rejected",
                                "timestamp": last_date + timedelta(days=random.randint(1, 5)),
                            }
                        )
                break

                # If not rejected, chance for an offer
                if current_status != "Rejected" and random.random() > 0.5:
                    current_status = "Offer"
                    history_data.append(
                        {
                            "app_id": i,
                            "status": "Offer",
                            "timestamp": last_date + timedelta(days=random.randint(1, 5)),
                        }
                    )

        # Chance of being rejected at any point before an offer
        if current_status not in ["Offer", "Rejected"] and random.random() < 0.2:
            current_status = "Rejected"
            history_data.append(
                {"app_id": i, "status": "Rejected", "timestamp": app_date + timedelta(days=random.randint(1, 30))}
            )

        apps_data.append(
            {
                "id": i,
                "company": company,
                "title": title,
                "category": category,
                "status": current_status,
                "date_applied": app_date.strftime("%Y-%m-%d"),
                "url": f"https://careers.google.com/jobs/results/",
                "notes": "Lorem ipsum dolor sit amet." if random.random() > 0.5 else "",
            }
        )

    df_apps = pd.DataFrame(apps_data)
    df_history = pd.DataFrame(history_data)

    # Calculate status transitions for Sankey diagram
    df_history["next_status"] = df_history.groupby("app_id")["status"].shift(-1)
    sankey_data = (
        df_history.dropna(subset=["next_status"])
        .groupby(["status", "next_status"])
        .size()
        .reset_index(name="value")
    )

    # Add "No Response" for apps stuck in "Applied" for Sankey
    app_status_counts = df_history.groupby("app_id")["status"].count()
    applied_only_apps = app_status_counts[app_status_counts == 1].index
    applied_only_apps = df_history[
        df_history["app_id"].isin(applied_only_apps) & (df_history["status"] == "Applied")
    ]["app_id"].unique()

    if len(applied_only_apps) > 0:
        no_response_rows = [{"status": "Applied", "next_status": "No Response", "value": 1}]
        sankey_data = (
            pd.concat([sankey_data, pd.DataFrame(no_response_rows * len(applied_only_apps))])
            .groupby(["status", "next_status"], as_index=False)
            .sum()
        )

    return df_apps, sankey_data


# --- Data Initialization ---
df, sankey_data = generate_dummy_data()
all_statuses = STATUSES


# --- KPI Calculations ---
def calculate_kpis(dataframe):
    """Calculate key performance indicators from the applications data."""
    return {
        "applied": len(dataframe),
        "active": len(dataframe[~dataframe["status"].isin(["Rejected", "Offer"])]),
        "assessment": len(dataframe[dataframe["status"] == "Online Assessment"]),
        "interviewing": len(dataframe[dataframe["status"].str.startswith("Interviewing")]),
        "rejected": len(dataframe[dataframe["status"] == "Rejected"]),
        "offer": len(dataframe[dataframe["status"] == "Offer"]),
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
        <script type="importmap">
        {
          "imports": {
            "@material/web/": "https://esm.run/@material/web/"
          }
        }
        </script>
        <script type="module">
          import '@material/web/all.js';
          import {styles as typescaleStyles} from '@material/web/typography/md-typescale-styles.js';

          document.adoptedStyleSheets.push(typescaleStyles.styleSheet);
        </script>
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
            .status-indicator.status-online-assessment { background-color: #f29e4c; }
            .status-indicator.status-interviewing { background-color: #f76f8e; }
            .status-indicator.status-offer { background-color: #54c184; }
            .status-indicator.status-rejected { background-color: #909da2; }

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
            
            /* --- In-Table Controls --- */
            .table-dropdown {
                font-size: 14px !important;
                height: 34px !important;
                width: 85% !important;
                min-height: 34px !important;
                padding-top: 0.35rem !important;
                padding-bottom: 0.35rem !important;
            }
            /* --- Form Textarea --- */
            .form-notes-textarea {
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
        figure.update_xaxes(gridcolor="#42474e", zeroline=False, showline=False)
    if "yaxis" in figure.layout:
        figure.update_yaxes(gridcolor="#42474e", zeroline=False, showline=False)
    return dcc.Graph(figure=figure, config={"displayModeBar": False})


def create_sankey_chart(sankey_data):
    """Create a Sankey diagram showing application status flow."""
    all_nodes = list(pd.unique(sankey_data[["status", "next_status"]].values.ravel("K")))
    if "No Response" not in all_nodes:
        all_nodes.append("No Response")
    node_map = {node: i for i, node in enumerate(all_nodes)}

    fig = go.Figure(
        go.Sankey(
            arrangement="snap",
            node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=all_nodes, color="#a8c7fa"),
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


def create_calendar_heatmap(dataframe):
    """Create a GitHub-style calendar heatmap of application activity."""
    df = dataframe.copy()
    df["date"] = pd.to_datetime(df["date_applied"]).dt.normalize()

    # Define the 1-year window for the heatmap
    end_date = pd.Timestamp.now().normalize()
    start_date = end_date - timedelta(days=365)
    
    # Create a complete dataframe for the 365-day period
    all_days = pd.DataFrame({'date': pd.date_range(start=start_date, end=end_date, freq='D')})

    # Prepare activity data
    activity = (
        df[df["date"].between(start_date, end_date)]
        .groupby("date")
        .size()
        .reset_index(name="count")
    )

    # Combine activity with the full date range to get a complete grid
    data = pd.merge(all_days, activity, on='date', how='left').fillna(0)
    
    # --- Final, Corrected Week and Month Splitting Logic ---
    data['weekday'] = data['date'].dt.weekday
    # Use ISO calendar week which correctly handles year boundaries
    data['week_of_year'] = data['date'].dt.isocalendar().week
    
    # Create a continuous week index that handles the year-end transition
    if data['week_of_year'].max() >= 52 and data['week_of_year'].min() == 1:
        first_week = data.iloc[0]['week_of_year']
        if first_week > 10:  # Starting mid-year
            data['continuous_week'] = np.where(data['week_of_year'] < first_week,
                                               data['week_of_year'] + 52,
                                               data['week_of_year'])
        else:
            data['continuous_week'] = data['week_of_year']
    else:
        data['continuous_week'] = data['week_of_year']
        
    data['week_index'] = data['continuous_week'] - data['continuous_week'].min()
    
    # Pivot the data to create the heatmap grid
    heatmap_data = data.pivot_table(index='weekday', columns='week_index', values='count')
    heatmap_data = heatmap_data.reindex(range(7), fill_value=0) # Ensure 7 days are always present

    # Create the hover text for each cell
    data['text'] = data.apply(
        lambda row: f"Date: {row['date'].strftime('%Y-%m-%d')}<br>Applications: {int(row['count'])}", 
        axis=1
    )
    hover_text_data = data.pivot_table(index='weekday', columns='week_index', values='text', aggfunc='first')
    hover_text_data = hover_text_data.reindex(range(7), fill_value='')

    # Position month labels correctly at the start of each month
    data['month_abbr'] = data['date'].dt.strftime('%b')
    month_starts = data.drop_duplicates(subset='month_abbr', keep='first').set_index('month_abbr')['week_index']
    month_names = month_starts.index

    # Create the final heatmap figure
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        hoverongaps=False,
        text=hover_text_data.values,
        hoverinfo="text",
        colorscale='Blues',
        showscale=False
    ))
    
    fig.update_layout(
        title="Application Heatmap (Last 365 Days)",
        yaxis=dict(autorange="reversed"),
        xaxis=dict(
            tickmode='array',
            tickvals=month_starts.values,
            ticktext=month_names,
            showgrid=True,
            gridcolor='rgba(0,0,0,0.2)' # Add subtle grid lines for month separation
        )
    )
    return fig


def create_category_pie_chart(dataframe):
    """Create a pie chart showing category distribution."""
    fig = px.pie(
        dataframe,
        names="category",
        title="Category Distribution",
        hole=0.6,
        color_discrete_sequence=CATEGORY_COLORS,
    )
    fig.update_traces(marker=dict(line=dict(color="var(--md-sys-color-surface-container)", width=2)))
    fig.update_layout(legend=dict(font_color="var(--md-sys-color-on-surface)"))
    return fig


# --- Initialize Charts ---
sankey_fig = create_sankey_chart(sankey_data)
heatmap_fig = create_calendar_heatmap(df)
category_fig = create_category_pie_chart(df)


# --- Component Creation Functions ---
def create_stats_card(number, label):
    """Create a KPI statistics card."""
    label_content = []
    if " " in label:
        parts = label.split(" ", 1)
        label_content = [parts[0], html.Br(), parts[1]]
    else:
        label_content = [label, html.Br(), html.Span(" ", style={"opacity": 0})]

    return html.Div(
        [html.P(number, className="stat-number mb-1"), html.P(label_content, className="stat-label mb-0")],
        className="stats-card",
    )


def create_application_table(dataframe, statuses):
    """Generate the application table component."""
    return dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("TIME", className="md-typescale-title-small"),
                        html.Th("COMPANY", className="md-typescale-title-small"),
                        html.Th("TITLE", className="md-typescale-title-small"),
                        html.Th("STATUS", className="md-typescale-title-small"),
                        html.Th("NOTES", className="md-typescale-title-small"),
                        html.Th("ACTIONS", className="md-typescale-title-small text-end"),
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(row["date_applied"]),
                            html.Td(row["company"]),
                            html.Td(row["title"]),
                            html.Td(
                                html.Div(
                                    [
                                        html.Div(
                                            className=f"status-indicator status-{row['status'].lower().replace(' ', '-').split(':')[0]}"
                                        ),
                                        dbc.Select(
                                        options=[{"label": s, "value": s} for s in statuses],
                                        value=row["status"],
                                        style={"width": "150px"},
                                        className="table-dropdown",
                                    ),
                                    ],
                                    className="status-cell",
                                )
                            ),
                            html.Td(row["notes"]),
                            html.Td(
                                [
                                    dbc.Button("History", className="btn-m3-outline me-1"),
                                    dbc.Button("Delete", className="btn-m3-text-danger"),
                                ],
                                style={"textAlign": "right"},
                            ),
                        ]
                    )
                    for _, row in dataframe.iterrows()
                ]
            ),
        ],
        striped=True,
        hover=True,
        responsive=True,
    )


def create_filter_search_row(statuses, categories):
    """Create the row with filters and search."""
    return html.Div(
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Select(
                            id="status-filter",
                            options=[{"label": "All Statuses", "value": "all"}]
                            + [{"label": s, "value": s} for s in statuses],
                            value="all",
                            placeholder="Filter by status...",
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dbc.Select(
                            id="category-filter",
                            options=[{"label": "All Categories", "value": "all"}]
                            + [{"label": c, "value": c} for c in categories],
                            value="all",
                            placeholder="Filter by category...",
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dbc.Input(
                            id="search-input",
                            placeholder="Search...",
                            debounce=True,
                        ),
                    ],
                    md=4,
                ),
            ],
            style={"padding": "1rem 1rem"},
        )
    )


def create_pagination_controls():
    """Create pagination controls with page numbers and entries selector."""
    return dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
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
                    ],
                    className="d-flex align-items-center",
                ),
                width="auto",
            ),
            dbc.Col("Showing 1-10 of 100", className="small text-secondary"),
            dbc.Col(
                html.Div(
                    [
                        dbc.Button("‹", className="pagination-btn me-1"),
                        dbc.Button("1", className="pagination-btn-active me-1"),
                        dbc.Button("2", className="pagination-btn me-1"),
                        dbc.Button("3", className="pagination-btn me-1"),
                        dbc.Button("4", className="pagination-btn me-1"),
                        dbc.Button("5", className="pagination-btn me-1"),
                        dbc.Button("›", className="pagination-btn"),
                    ],
                    className="d-flex",
                ),
                width="auto",
                className="ms-auto",
            ),
        ],
        align="center",
        className="mt-2",
        style={"padding": "0rem 1rem 1rem 1rem"},
    )


def create_application_form(categories):
    """Create the form for adding a new application."""
    return html.Div(
        [
            html.H5("Add New Application", className="md-typescale-title-large mb-3"),
            dbc.Input(
                id="company-input",
                placeholder="Company Name",
                className="mb-2",
                required=True,
            ),
            dbc.Input(
                id="title-input",
                placeholder="Job Title",
                className="mb-2",
                required=True,
            ),
            dbc.Input(
                id="url-input",
                placeholder="Application URL",
                type="url",
                className="mb-2",
                required=True,
            ),
            dbc.Select(
                id="category-input",
                options=[{"label": c, "value": c} for c in categories],
                value=categories[0],
                placeholder="Category",
                className="mb-2",
                required=True,
            ),
            dbc.Textarea(
                id="notes-input",
                placeholder="Notes...",
                className="mb-2 form-notes-textarea",
            ),
            dbc.Input(
                id="date-input",
                type="date",
                value=datetime.now().date().isoformat(),
                className="mb-2",
                required=True,
            ),
            dbc.Button("Submit", color="primary", className="w-100 mt-2"),
        ],
        className="card-component fade-in",
    )


# --- Main Layout ---
def create_layout():
    """Create the main application layout."""
    return dbc.Container(
        [
            # Header
            html.Div(
                [
                    html.H1("Modern ATS Dashboard", className="mb-1 md-typescale-display-small"),
                    html.P(
                        "A Demo of Interactive Application Tracking System",
                        className="text-secondary md-typescale-body-large",
                    ),
                ],
                className="my-4 text-center fade-in",
            ),
            # Main Content
            dbc.Row(
                [
                    # Left Column: Stats & Form
                    dbc.Col(
                        [
                            # KPI Stats
                            dbc.Row(
                                [
                                    dbc.Col(create_stats_card(kpis["applied"], "Applied"), md=4),
                                    dbc.Col(create_stats_card(kpis["active"], "Active"), md=4),
                                    dbc.Col(create_stats_card(kpis["assessment"], "Online Assessment"), md=4),
                                ],
                                className="g-2 mb-2",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(create_stats_card(kpis["interviewing"], "Interviewing"), md=4),
                                    dbc.Col(create_stats_card(kpis["rejected"], "Rejected"), md=4),
                                    dbc.Col(create_stats_card(kpis["offer"], "Offer"), md=4),
                                ],
                                className="g-2 mb-3",
                            ),
                            # Application Form
                            create_application_form(CATEGORIES),
                        ],
                        md=3,
                    ),
                    # Right Column: Tabs for Table & Charts
                    dbc.Col(
                        html.Div(
                            dbc.Tabs(
                                [
                                    # Applications Tab
                                    dbc.Tab(
                                        [
                                            create_filter_search_row(all_statuses, CATEGORIES),
                                            html.Div(
                                                create_application_table(df, all_statuses),
                                                className="table-responsive",
                                            ),
                                            create_pagination_controls(),
                                        ],
                                        label="Applications",
                                    ),
                                    # Analytics Tab
                                    dbc.Tab(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(create_styled_chart(sankey_fig), md=12),
                                                    dbc.Col(create_styled_chart(heatmap_fig), md=8),
                                                    dbc.Col(create_styled_chart(category_fig), md=4),
                                                ],
                                                className="g-3 mt-1",
                                            )
                                        ],
                                        label="Analytics",
                                    ),
                                ]
                            ),
                            className="card-component fade-in p-0",
                        ),
                        md=9,
                    ),
                ],
                className="g-3",
            ),
        ],
        fluid=True,
        className="fade-in",
    )


# --- Set Layout ---
app.layout = create_layout()

# --- Callbacks ---
# (Callbacks for interactivity will be defined here)
# For example: updating table based on filters, handling pagination, form submission, etc.


# --- Run App ---
if __name__ == "__main__":
    app.run(debug=True)
