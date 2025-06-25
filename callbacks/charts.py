import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import calendar
import numpy as np
from collections import Counter
from dash import Input, Output, State, callback_context, no_update, html, dcc, ALL
import dash_bootstrap_components as dbc
from database.manager import DatabaseManager
from utils.constants import STATUS_OPTIONS, CHART_COLORS
from utils.logger import log_auto_update, log_callback_error

db = DatabaseManager()

def register_charts_callbacks(app):
    """Register dashboard update and chart callbacks"""
    
    @app.callback(
        [
            Output("applications-table-container", "children"),
            Output("kpi-container", "children"),
            Output("status-chart", "figure"),
            Output("category-chart", "figure"),
            Output("timeline-chart", "figure"),
            Output("status-filter", "options"),
            Output("category-filter", "options"),
            Output("pagination-info", "children"),
        ],
        [
            Input("update-trigger-store", "data"),
            Input("status-filter", "value"),
            Input("category-filter", "value"),
            Input("search-input", "value"),
            Input("pagination-store", "data"),
            Input("page-size-dropdown", "value"),
            Input("prev-page-btn", "n_clicks"),
            Input("next-page-btn", "n_clicks"),
        ],
    )
    def update_dashboard(update_trigger, status_filter, category_filter, search_value, pagination_data, page_size, prev_clicks, next_clicks):
        try:
            # Auto-update applications to "No Response" after 30 days
            updated_count = db.auto_update_no_response()
            log_auto_update(updated_count)
            
            # Handle notifications - removed from here since it's handled in applications callback
            
            # Get pagination state
            current_page = pagination_data.get("current_page", 0) if pagination_data else 0
            current_page_size = pagination_data.get("page_size", 10) if pagination_data else 10
            
            # Handle pagination button clicks
            ctx = callback_context
            if ctx.triggered:
                trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
                if trigger_id == "prev-page-btn" and prev_clicks:
                    current_page = max(0, current_page - 1)
                elif trigger_id == "next-page-btn" and next_clicks:
                    current_page += 1
                elif trigger_id == "page-size-dropdown" and page_size:
                    current_page_size = page_size
                    current_page = 0  # Reset to first page when changing page size
            
            df = db.get_applications()
            kpi_data = df.copy()

            filtered_df = df.copy()
            if status_filter:
                filtered_df = filtered_df[filtered_df["status"].isin(status_filter)]
            if category_filter and "category" in filtered_df.columns:
                filtered_df = filtered_df[filtered_df["category"].isin(category_filter)]
            if search_value:
                mask = filtered_df["company_name"].str.contains(search_value, case=False, na=False) | filtered_df[
                    "job_title"
                ].str.contains(search_value, case=False, na=False)
                filtered_df = filtered_df[mask]

            # Apply pagination
            total_rows = len(filtered_df)
            total_pages = (total_rows + current_page_size - 1) // current_page_size
            start_idx = current_page * current_page_size
            end_idx = min(start_idx + current_page_size, total_rows)
            
            # Ensure current_page is valid
            if current_page >= total_pages and total_pages > 0:
                current_page = total_pages - 1
                start_idx = current_page * current_page_size
                end_idx = min(start_idx + current_page_size, total_rows)
            
            paginated_df = filtered_df.iloc[start_idx:end_idx]

            # Create Bootstrap table
            table_rows = []
            for _, row in paginated_df.iterrows():
                # Status dropdown options
                status_options = [
                    {"label": status, "value": status} for status in STATUS_OPTIONS
                ]
                
                # URL link
                url_link = html.A("View", href=row['application_url'], target="_blank") if pd.notna(row["application_url"]) and row["application_url"] else ""
                
                # Status dropdown
                status_dropdown = dcc.Dropdown(
                    id={"type": "status-dropdown", "index": row["id"]},
                    options=status_options,
                    value=row["status"],
                    clearable=False,
                    style={"width": "150px", "height": "35px", "fontSize": "12px"}
                )
                
                # Notes textarea
                notes_textarea = dbc.Textarea(
                    id={"type": "notes-textarea", "index": row["id"]},
                    value=row["notes"] if pd.notna(row["notes"]) else "",
                    style={"width": "200px", "height": "60px", "fontSize": "12px"},
                    placeholder="Add notes..."
                )
                
                # Delete button
                delete_button = dbc.Button(
                    "Delete",
                    id={"type": "delete-btn", "index": row["id"]},
                    color="danger",
                    size="sm",
                    style={"fontSize": "10px"}
                )
                
                # History button
                history_button = dbc.Button(
                    "History",
                    id={"type": "history-btn", "index": row["id"]},
                    color="info",
                    size="sm",
                    style={"fontSize": "10px", "marginLeft": "5px"},
                    n_clicks=0  # Initialize n_clicks
                )
                
                table_rows.append(
                    html.Tr([
                        html.Td(row["date_applied"]),
                        html.Td(row["company_name"]),
                        html.Td(row["job_title"]),
                        html.Td(url_link),
                        html.Td(status_dropdown),
                        html.Td(row["category"]),
                        html.Td(notes_textarea),
                        html.Td([delete_button, history_button]),
                    ])
                )

            table = dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Date Applied"),
                        html.Th("Company"),
                        html.Th("Job Title"),
                        html.Th("URL"),
                        html.Th("Status"),
                        html.Th("Category"),
                        html.Th("Notes"),
                        html.Th("Actions"),
                    ])
                ]),
                html.Tbody(table_rows)
            ], bordered=True, hover=True, responsive=True, striped=True)

            # Pagination info
            if total_rows > 0:
                pagination_info = f"Showing {start_idx + 1}-{end_idx} of {total_rows} applications (Page {current_page + 1} of {total_pages})"
            else:
                pagination_info = "No applications found"

            kpis = dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.H4(str(count), style={"color": "#007bff", "margin": 0}),
                                html.P(s, style={"margin": 0, "fontSize": "12px"}),
                            ],
                            style={
                                "textAlign": "center",
                                "padding": "10px",
                                "border": "1px solid #ddd",
                                "borderRadius": "5px",
                                "background": "#f8f9fa",
                                "minWidth": "120px",
                            },
                        ),
                        className="d-flex flex-column align-items-center h-100",
                        width="auto",
                    )
                    for s, count in zip(
                        [
                            "Applied",
                            "Online Assessment",
                            "Interviewing",
                            "Offer",
                            "Declined",
                            "Rejected",
                            "No Response",
                        ],
                        [
                            len(kpi_data),
                            len(kpi_data[kpi_data["status"] == "Online Assessment"]),
                            len(
                                kpi_data[
                                    kpi_data["status"].isin(
                                        ["1st round", "2nd round", "3rd round", "4th round", "5th round", "6th round"]
                                    )
                                ]
                            ),
                            len(kpi_data[kpi_data["status"] == "Offer"]),
                            len(kpi_data[kpi_data["status"] == "Declined"]),
                            len(kpi_data[kpi_data["status"] == "Rejected"]),
                            len(kpi_data[kpi_data["status"] == "No Response"]),
                        ],
                    )
                ],
                className="g-2 w-100 justify-content-center",
                justify="center",
            )

            # Sankey Diagram for status transitions
            sankey_nodes = STATUS_OPTIONS + ["No Response"]  # Add No Response back for the chart
            node_colors = [
                "#2ca02c",  # Applied
                "#ff7f0e",  # Online Assessment
                "#98df8a",  # 1st round
                "#7f7f7f",  # 2nd round
                "#c49c94",  # 3rd round
                "#bcbd22",  # 4th round
                "#8c564b",  # 5th round
                "#17becf",  # 6th round
                "#9467bd",  # Offer
                "#e377c2",  # Declined
                "#f7b6d2",  # Rejected
                "#1f77b4",  # No Response
            ]
            node_map = {node: i for i, node in enumerate(sankey_nodes)}
            
            # Build transitions (from -> to) using status_history
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM applications")
            app_ids = [row[0] for row in cursor.fetchall()]
            transitions = []
            
            # Track applications that only have "Applied" status
            applied_only_apps = []
            
            for app_id in app_ids:
                cursor.execute(
                    "SELECT status FROM status_history WHERE application_id = ? ORDER BY timestamp ASC", (app_id,)
                )
                status_seq = [row[0] for row in cursor.fetchall()]
                
                if len(status_seq) == 1 and status_seq[0] == "Applied":
                    # Application only has "Applied" status - will auto-link to "No Response"
                    applied_only_apps.append(app_id)
                elif len(status_seq) >= 2:
                    # Application has transitions - add them to the flow
                    for prev, curr in zip(status_seq[:-1], status_seq[1:]):
                        if prev in node_map and curr in node_map:
                            transitions.append((prev, curr))
            
            conn.close()

            # Add auto-transitions from "Applied" to "No Response" for applications with no changes
            if applied_only_apps:
                transitions.extend([("Applied", "No Response")] * len(applied_only_apps))

            transition_counts = Counter(transitions)
            # Build DataFrame for Sankey links
            df_links = pd.DataFrame(
                [{"Source": s, "Target": t, "Value": v} for (s, t), v in transition_counts.items()]
            )
            if df_links.empty:
                # If no transitions, show all status nodes with current status highlighted
                # Get current status distribution
                status_counts = kpi_data["status"].value_counts()
                
                # Create nodes for all possible statuses
                node_colors = [
                    "#2ca02c",  # Applied
                    "#ff7f0e",  # Online Assessment
                    "#98df8a",  # 1st round
                    "#7f7f7f",  # 2nd round
                    "#c49c94",  # 3rd round
                    "#bcbd22",  # 4th round
                    "#8c564b",  # 5th round
                    "#17becf",  # 6th round
                    "#9467bd",  # Offer
                    "#e377c2",  # Declined
                    "#f7b6d2",  # Rejected
                    "#1f77b4",  # No Response
                ]
                
                # Explicit node positions (x/y) for clean layout
                node_x = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 1.0, 1.0, 1.0, 1.0]
                node_y = [
                    0.5,  # Applied
                    0.4,  # Online Assessment
                    0.3,  # 1st round
                    0.2,  # 2nd round
                    0.1,  # 3rd round
                    0.0,  # 4th round
                    0.6,  # 5th round
                    0.7,  # 6th round
                    0.1,  # Offer (top)
                    0.3,  # Declined
                    0.5,  # Rejected
                    0.9,  # No Response (bottom)
                ]
                
                # Highlight current status nodes with larger thickness
                node_thickness = []
                for status in sankey_nodes:
                    if status in status_counts.index:
                        node_thickness.append(30)  # Thicker for nodes with applications
                    else:
                        node_thickness.append(10)  # Thinner for empty nodes
                
                status_fig = go.Figure(
                    data=[
                        go.Sankey(
                            arrangement="snap",
                            node=dict(
                                pad=15,
                                thickness=node_thickness,
                                line=dict(color="black", width=0.5),
                                label=sankey_nodes,
                                color=node_colors,
                                x=node_x,
                                y=node_y,
                            ),
                            link=dict(
                                source=[],  # No links
                                target=[],
                                value=[],
                                color=[],
                            ),
                        )
                    ]
                )
                status_fig.update_layout(
                    title="Application Status Flow (No transitions yet)",
                    font_size=10,
                    height=800,
                    plot_bgcolor="rgba(0,0,0,0)",
                )
            else:
                source_indices = df_links["Source"].map(node_map)
                target_indices = df_links["Target"].map(node_map)
                values = df_links["Value"]
                # Explicit node positions (x/y) for clean layout
                node_x = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 1.0, 1.0, 1.0, 1.0]
                node_y = [
                    0.5,  # Applied
                    0.4,  # Online Assessment
                    0.3,  # 1st round
                    0.2,  # 2nd round
                    0.1,  # 3rd round
                    0.0,  # 4th round
                    0.6,  # 5th round
                    0.7,  # 6th round
                    0.1,  # Offer (top)
                    0.3,  # Declined
                    0.5,  # Rejected
                    0.9,  # No Response (bottom)
                ]
                status_fig = go.Figure(
                    data=[
                        go.Sankey(
                            arrangement="snap",
                            node=dict(
                                pad=15,
                                thickness=20,
                                line=dict(color="black", width=0.5),
                                label=sankey_nodes,
                                color=node_colors,
                                x=node_x,
                                y=node_y,
                            ),
                            link=dict(
                                source=source_indices,
                                target=target_indices,
                                value=values,
                                color=["rgba(0,0,0,0.2)"] * len(values),
                            ),
                        )
                    ]
                )
                status_fig.update_layout(
                    font_size=10,
                    height=800,
                    plot_bgcolor="rgba(0,0,0,0)",
                )

            # Category Distribution Chart
            if not kpi_data.empty and "category" in kpi_data.columns:
                category_counts = kpi_data["category"].value_counts()
                category_fig = px.pie(
                    values=category_counts.values,
                    names=category_counts.index,
                    color_discrete_sequence=px.colors.qualitative.Set3,
                )
                category_fig.update_layout(
                    height=400,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                )
            else:
                category_fig = go.Figure()
                category_fig.add_annotation(
                    text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
                )
                category_fig.update_layout(height=400)

            # Timeline Heatmap
            timeline_fig = go.Figure()
            if not kpi_data.empty:
                try:
                    # 1. Prepare data
                    kpi_data["date_applied"] = pd.to_datetime(kpi_data["date_applied"])
                    start_date = kpi_data["date_applied"].min()
                    end_date = kpi_data["date_applied"].max()

                    # Ensure we have at least 30 days of data
                    if (end_date - start_date).days < 30:
                        end_date = start_date + timedelta(days=365)

                    # Count applications by date
                    counts_by_date = kpi_data.groupby("date_applied").size().reset_index(name="count")
                    counts_by_date.rename(columns={"date_applied": "date"}, inplace=True)
                    counts_by_date["date"] = pd.to_datetime(counts_by_date["date"])

                    # 2. Create full date range grid
                    grid_start_date = start_date - timedelta(days=(start_date.weekday() + 1) % 7)
                    all_dates_grid = pd.DataFrame(
                        {"date": pd.date_range(start=grid_start_date, end=end_date, freq="D")}
                    )

                    # 3. Merge application counts with the grid
                    heatmap_data = pd.merge(all_dates_grid, counts_by_date, on="date", how="left").fillna(0)
                    heatmap_data["weekday"] = (heatmap_data["date"].dt.weekday + 1) % 7  # Sun=0, Mon=1, ..., Sat=6
                    heatmap_data["week_num"] = (heatmap_data["date"] - pd.to_datetime(grid_start_date)).dt.days // 7

                    # 4. Create the base matrices
                    heatmap_matrix = heatmap_data.pivot_table(index="weekday", columns="week_num", values="count")
                    custom_data_matrix = heatmap_data.pivot_table(
                        index="weekday", columns="week_num", values="date", aggfunc=lambda x: x.iloc[0]
                    )

                    # Flip the matrices to match the y-axis labels (Sat at top, Sun at bottom)
                    heatmap_matrix = heatmap_matrix.iloc[::-1]
                    custom_data_matrix = custom_data_matrix.iloc[::-1]

                    # 5. Create calendar-based month separation
                    z_with_gaps = []
                    custom_data_with_gaps = []
                    x_labels = []
                    x_tickvals = []  # Use this for precise label positioning

                    # Create a mapping for month numbers to full names
                    month_names = {i: calendar.month_name[i] for i in range(1, 13)}

                    current_year_month = None

                    for week_idx in range(custom_data_matrix.shape[1]):
                        week_dates = custom_data_matrix.iloc[:, week_idx].dropna()

                        if week_dates.empty:
                            continue

                        # Determine the primary month for the week (the month with more days)
                        week_month = week_dates.dt.month.mode()[0]
                        week_year = week_dates.dt.year.mode()[0]
                        year_month = (week_year, week_month)

                        # Add a gap if we are entering a new month
                        if current_year_month is not None and year_month != current_year_month:
                            # Add two blank columns for extra spacing
                            z_with_gaps.append(np.full((7, 1), np.nan))
                            custom_data_with_gaps.append(np.full((7, 1), None))

                        # Add month label if it's new
                        if current_year_month is None or year_month != current_year_month:
                            month_str = month_names[week_dates.iloc[0].month]
                            label_pos = len(z_with_gaps) + 0.5
                            x_labels.append(month_str)
                            x_tickvals.append(label_pos)

                        current_year_month = year_month

                        # Create the column for this week
                        week_data_col = np.full((7, 1), np.nan)
                        hover_text_col = [""] * 7

                        for date_val in week_dates:
                            # weekday: Sun=0, Mon=1...Sat=6
                            day_idx = (date_val.weekday() + 1) % 7

                            # Find matching count
                            count_series = heatmap_data[heatmap_data["date"] == date_val]["count"]
                            count_val = count_series.iloc[0] if not count_series.empty else 0

                            # Only show data for the current month
                            if date_val.month == week_month:
                                # Flip index for visual representation (Sat top, Sun bottom)
                                visual_day_idx = 6 - day_idx
                                week_data_col[visual_day_idx, 0] = count_val
                                if pd.notna(count_val) and count_val > 0:
                                    hover_text_col[visual_day_idx] = (
                                        f"Date: {date_val.strftime('%Y-%m-%d')}<br>Applications: {int(count_val)}"
                                    )
                                else:
                                    hover_text_col[visual_day_idx] = (
                                        f"Date: {date_val.strftime('%Y-%m-%d')}<br>Applications: 0"
                                    )

                        z_with_gaps.append(week_data_col)
                        custom_data_with_gaps.append(np.array(hover_text_col).reshape(7, 1))

                    final_z = np.hstack(z_with_gaps) if z_with_gaps else np.array([[]])
                    final_custom_data = np.hstack(custom_data_with_gaps) if custom_data_with_gaps else np.array([[]])

                    timeline_fig.add_trace(
                        go.Heatmap(
                            z=final_z,
                            y=["Sat", "Fri", "Thu", "Wed", "Tue", "Mon", "Sun"],
                            customdata=final_custom_data,
                            hovertemplate="%{customdata}<extra></extra>",
                            colorscale=[[0, "#ebedf0"], [0.01, "#c6e48b"], [0.5, "#7bc96f"], [1, "#239a3b"]],
                            showscale=False,
                            xgap=3,
                            ygap=3,
                        )
                    )
                    timeline_fig.update_layout(
                        xaxis=dict(
                            tickmode="array",
                            tickvals=x_tickvals,
                            ticktext=x_labels,
                        ),
                        height=300,
                        yaxis_constrain="domain",
                        plot_bgcolor="rgba(0,0,0,0)",
                        xaxis_showgrid=False,
                        yaxis_showgrid=False,
                    )

                except Exception as e:
                    import traceback

                    print(f"Error generating heatmap: {e}")
                    print(traceback.format_exc())
                    timeline_fig.add_annotation(
                        text="Error generating heatmap", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
                    )
            else:
                timeline_fig.add_annotation(
                    text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False
                )
                timeline_fig.update_layout(height=400)

            status_options = [{"label": s, "value": s} for s in kpi_data["status"].unique()]
            category_options = [{"label": c, "value": c} for c in kpi_data["category"].unique() if pd.notna(c)]

            return table, kpis, status_fig, category_fig, timeline_fig, status_options, category_options, pagination_info 
        except Exception as e:
            log_callback_error("update_dashboard", e)
            # Return empty/default values on error
            empty_table = dbc.Table([], bordered=True, hover=True, responsive=True, striped=True)
            empty_kpis = dbc.Row([])
            empty_fig = go.Figure()
            empty_fig.add_annotation(text="Error loading data", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
            empty_fig.update_layout(height=400)
            
            return empty_table, empty_kpis, empty_fig, empty_fig, empty_fig, [], [], "Error loading data" 