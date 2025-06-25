import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import calendar

# --- App Initialization ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# --- Advanced Dummy Data for All Charts ---
def generate_dummy_data():
    companies = ['Google', 'Microsoft', 'Apple', 'Amazon', 'Meta', 'Netflix', 'Stripe']
    titles = ['Software Engineer', 'ML Engineer', 'Data Scientist']
    categories = ['SWE/SDE', 'MLE', 'Data Science', 'Other']
    status_flow = ['Applied', 'Assessment', 'Interviewing', 'Offer']
    
    apps_data = []
    history_data = []
    
    for i in range(100):
        company = random.choice(companies)
        title = random.choice(titles)
        category = random.choice(categories)
        app_date = datetime.now() - timedelta(days=random.randint(0, 365))
        
        # Determine the application's path
        final_stage_index = random.randint(0, len(status_flow))
        is_rejected = random.random() < 0.25 and final_stage_index > 0
        
        current_status = ""
        # Create history
        for j in range(final_stage_index):
            status = status_flow[j]
            history_data.append({'app_id': i, 'status': status})
            current_status = status
            if random.random() < 0.3: # Chance to drop off early
                break
        
        if is_rejected:
            current_status = 'Rejected'
            history_data.append({'app_id': i, 'status': 'Rejected'})
        elif final_stage_index == 0:
            current_status = 'Applied'
            history_data.append({'app_id': i, 'status': 'Applied'})

        apps_data.append({
            'id': i, 'company': company, 'title': title, 'category': category,
            'status': current_status, 'date_applied': app_date.strftime('%Y-%m-%d')
        })
        
    df_apps = pd.DataFrame(apps_data)
    df_history = pd.DataFrame(history_data)
    
    # Calculate transitions for Sankey
    df_history['next_status'] = df_history.groupby('app_id')['status'].shift(-1)
    sankey_data = df_history.dropna().groupby(['status', 'next_status']).size().reset_index(name='value')
    
    return df_apps, sankey_data

df, sankey_data = generate_dummy_data()

# --- Custom CSS for True VS Code Theme ---
# (Styling remains the same as the previous correct version)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>ATS Dashboard</title>
        {%favicon%}
        {%css%}
        <style>
            :root {
                --bg-primary: #1e1e1e; --bg-secondary: #252526; --bg-tertiary: #2d2d30;
                --border-color: #3c3c3c; --text-primary: #cccccc; --text-secondary: #969696;
                --accent-blue: #007acc;
            }
            body {
                background-color: var(--bg-primary) !important; color: var(--text-primary) !important;
                font-family: Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
                font-size: 14px;
            }
            .fade-in { animation: fadeIn 0.4s ease-in-out; }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(8px); }
                to { opacity: 1; transform: translateY(0); }
            }
            /* --- Custom Form Placeholder Color --- */
            .form-control::placeholder { color: var(--text-secondary) !important; opacity: 0.7; }
            .form-control:-ms-input-placeholder { color: var(--text-secondary) !important; }
            .form-control::-ms-input-placeholder { color: var(--text-secondary) !important; }

            .stats-card {
                background-color: var(--bg-secondary); border: 1px solid var(--border-color);
                border-radius: 4px; padding: 1rem; transition: background-color 0.2s ease;
            }
            .stats-card:hover { background-color: var(--bg-tertiary); }
            .stat-number { font-size: 1.75rem; font-weight: 600; color: var(--accent-blue); }
            .stat-label { font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.8px; }
            .card-component { background-color: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: 4px; padding: 1.25rem; }
            .form-control, .form-select, .btn {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }
            .form-control, .form-select {
                background-color: var(--bg-tertiary) !important; border: 1px solid var(--border-color) !important;
                color: var(--text-primary) !important; font-size: 14px;
            }
            .form-control:focus, .form-select:focus { box-shadow: 0 0 0 2px var(--accent-blue) !important; border-color: var(--accent-blue) !important; }
            .btn-primary { background-color: var(--accent-blue) !important; border-color: var(--accent-blue) !important; font-size: 14px; transition: background-color 0.2s ease; }
            .btn-primary:hover { background-color: #005a9e !important; }

            /* --- Themed Table Styles --- */
            .table {
                --bs-table-bg: var(--bg-secondary);
                --bs-table-color: var(--text-primary);
                --bs-table-border-color: var(--border-color);
                --bs-table-hover-bg: var(--bg-tertiary);
                --bs-table-striped-bg: var(--bg-tertiary); /* Correctly theme striped rows */
                --bs-table-striped-color: var(--text-primary);
                vertical-align: middle;
            }
            .table > :not(caption) > * > * { padding: 0.6rem 0.6rem; }
            .status-badge { display: inline-block; padding: 0.3em 0.7em; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase; color: white; }
            .status-applied { background-color: #3b82f6; } .status-assessment { background-color: #f97316; }
            .status-interviewing { background-color: #8b5cf6; } .status-offer { background-color: #22c55e; }
            .status-rejected { background-color: #64748b; }
            .nav-tabs { border-bottom: 1px solid var(--border-color) !important; }
            .nav-tabs .nav-link { background-color: transparent; border-color: transparent; color: var(--text-secondary); font-size: 14px; padding: 0.5rem 1rem; }
            .nav-tabs .nav-link.active { background-color: var(--bg-secondary); color: var(--text-primary); border-color: var(--border-color) !important; border-bottom-color: var(--bg-secondary) !important; }
            .nav-tabs .nav-link:hover { color: var(--text-primary); border-color: transparent; }
            .tab-content { background-color: var(--bg-secondary); padding-top: 1.25rem; }
        </style>
    </head>
    <body> {%app_entry%} <footer> {%config%} {%scripts%} {%renderer%} </footer> </body>
</html>
'''

# --- Charting Functions & Figures ---
def create_styled_chart(figure):
    """Applies common VS Code theme styling to a Plotly figure."""
    figure.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font_color='var(--text-secondary)', margin=dict(t=40, b=20, l=20, r=20),
        showlegend=False
    )
    if 'xaxis' in figure.layout:
        figure.update_xaxes(gridcolor='var(--border-color)')
    if 'yaxis' in figure.layout:
        figure.update_yaxes(gridcolor='var(--border-color)')
    return dcc.Graph(figure=figure)

# 1. Sankey Chart
all_nodes = list(pd.unique(sankey_data[['status', 'next_status']].values.ravel('K')))
node_map = {node: i for i, node in enumerate(all_nodes)}
sankey_fig = go.Figure(go.Sankey(
    arrangement="snap",
    node=dict(
        pad=15, thickness=20, line=dict(color="black", width=0.5),
        label=all_nodes, color="var(--accent-blue)"
    ),
    link=dict(
        source=sankey_data['status'].map(node_map),
        target=sankey_data['next_status'].map(node_map),
        value=sankey_data['value']
    )
))
sankey_fig.update_layout(title_text="Application Status Flow", font_size=10)

# 2. Timeline Heatmap
df['date_applied'] = pd.to_datetime(df['date_applied'])
activity = df['date_applied'].dt.date.value_counts().sort_index()
all_days = pd.date_range(start=activity.index.min(), end=activity.index.max(), freq='D')
activity = activity.reindex(all_days, fill_value=0)
heatmap_fig = go.Figure(go.Heatmap(
    z=activity.values, x=activity.index,
    colorscale=[[0, 'var(--bg-tertiary)'], [1, 'var(--accent-blue)']],
    showscale=False
))
heatmap_fig.update_layout(title_text="Application Timeline")

# 3. Category Distribution Chart
category_fig = px.pie(
    df, names='category', title='Category Distribution', hole=0.6,
    color_discrete_sequence=px.colors.qualitative.Pastel
)

# --- Reusable Components & Table ---
def create_stats_card(number, label):
    return html.Div([
        html.P(number, className='stat-number mb-1'),
        html.P(label, className='stat-label mb-0')
    ], className='stats-card')

def create_status_badge(status):
    return html.Span(status, className=f"status-badge status-{status.lower()}")

table = dbc.Table([
    html.Thead(html.Tr([html.Th("Company"), html.Th("Title"), html.Th("Date Applied"), html.Th("Status")])),
    html.Tbody([
        html.Tr([
            html.Td(row['company']), html.Td(row['title']),
            html.Td(row['date_applied']), html.Td(create_status_badge(row['status']))
        ]) for _, row in df.iterrows()
    ])
], striped=True, hover=True, responsive=True)

# --- App Layout with All Components ---
app.layout = dbc.Container([
    # Header
    html.Div([
        html.H1("ATS Dashboard", className="h3 mb-1", style={'fontWeight': '600'}),
        html.P("A minimal, compact, and modern application tracking interface.", className="mb-0", style={'color': 'var(--text-secondary)'}),
    ], className='my-4 fade-in'),

    # Main Content
    dbc.Row([
        # Left Column: Stats & Form
        dbc.Col([
            dbc.Row([
                dbc.Col(create_stats_card(len(df), "Total"), md=6, className="mb-3"),
                dbc.Col(create_stats_card(len(df[df['status'] != 'Rejected']), "Active"), md=6, className="mb-3"),
                dbc.Col(create_stats_card(len(df[df['status'] == 'Interviewing']), "Interviews"), md=6, className="mb-3"),
                dbc.Col(create_stats_card(len(df[df['status'] == 'Offer']), "Offers"), md=6, className="mb-3"),
            ]),
            html.Div([
                html.H2("Add Application", className='h5 mb-3'),
                dbc.Input(placeholder="Company Name", className="mb-2"),
                dbc.Input(placeholder="Job Title", className="mb-2"),
                dbc.Select(options=[{'label': s, 'value': s} for s in df['status'].unique()], value="Applied"),
                dbc.Button("Submit", color="primary", className="w-100 mt-3")
            ], className='card-component fade-in')
        ], md=3),

        # Right Column: Tabs for Table & Charts
        dbc.Col(
            html.Div(dbc.Tabs([
                dbc.Tab(table, label="Applications"),
                dbc.Tab([
                    dbc.Row([
                        dbc.Col(create_styled_chart(sankey_fig), md=12),
                        dbc.Col(create_styled_chart(heatmap_fig), md=8),
                        dbc.Col(create_styled_chart(category_fig), md=4),
                    ], className="g-3 mt-1")
                ], label="Analytics"),
            ]), className='card-component fade-in p-0'),
            md=9
        ),
    ], className='g-3'),
], fluid=True, className='p-3')

if __name__ == '__main__':
    app.run_server(debug=True, port=8052)
