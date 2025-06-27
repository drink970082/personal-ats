"""Chart generation utilities."""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from config.constants import CATEGORIES, CATEGORY_COLORS


def create_timeline_heatmap(applications_data):
    """Create a clean calendar heatmap with proper month boundaries."""
    if not applications_data:
        fig = go.Figure()
        fig.update_layout(
            title="Application Timeline - No Data",
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e2e6'
        )
        return fig
    
    try:
        import calendar
        import numpy as np
        
        # Convert to DataFrame and get date range
        df = pd.DataFrame(applications_data)
        df['date_applied'] = pd.to_datetime(df['date_applied'])
        
        start_date = df['date_applied'].min()
        end_date = df['date_applied'].max()
        
        # Ensure at least 365 days
        if (end_date - start_date).days < 365:
            end_date = start_date + timedelta(days=365)
        
        # Count applications by date
        counts_by_date = df.groupby('date_applied').size().to_dict()
        
        # Generate all dates in range
        current_date = start_date
        all_months = []
        
        while current_date <= end_date:
            month_start = current_date.replace(day=1)
            next_month = (month_start + timedelta(days=32)).replace(day=1)
            month_end = next_month - timedelta(days=1)
            
            if month_end > end_date:
                month_end = end_date
                
            all_months.append((month_start, month_end))
            current_date = next_month
        
        # Build heatmap data month by month
        z_columns = []
        hover_columns = []
        x_labels = []
        x_positions = []
        
        col_idx = 0
        
        for month_start, month_end in all_months:
            # Get first Sunday of month view (may be from previous month)
            first_day_weekday = month_start.weekday()  # 0=Monday, 6=Sunday
            days_back = (first_day_weekday + 1) % 7  # Convert to Sunday=0 base
            week_start = month_start - timedelta(days=days_back)
            
            # Generate weeks for this month
            current_week_start = week_start
            month_label_added = False
            
            while current_week_start <= month_end:
                week_end = current_week_start + timedelta(days=6)
                
                # Create week column (7 rows: Sun=0 to Sat=6)
                week_values = np.full(7, np.nan)
                week_hover = [""] * 7
                
                # Check if this week has any days from current month
                has_month_days = False
                for day_offset in range(7):
                    check_date = current_week_start + timedelta(days=day_offset)
                    if month_start <= check_date <= month_end:
                        has_month_days = True
                        break
                
                if has_month_days:
                    # Add month label for first week of month
                    if not month_label_added:
                        month_name = calendar.month_abbr[month_start.month]
                        if month_start.year != (month_start - timedelta(days=365)).year:
                            month_name = f"{month_name} {month_start.year}"
                        x_labels.append(month_name)
                        x_positions.append(col_idx)
                        month_label_added = True
                    
                    # Fill week data
                    for day_offset in range(7):
                        current_day = current_week_start + timedelta(days=day_offset)
                        
                        # Only show days from current month
                        if month_start <= current_day <= month_end:
                            count = counts_by_date.get(pd.Timestamp(current_day), 0)
                            # Flip the day_offset to match flipped y-axis (Sat=0, Fri=1, ..., Sun=6)
                            flipped_day_idx = 6 - day_offset
                            week_values[flipped_day_idx] = count
                            week_hover[flipped_day_idx] = f"Date: {current_day.strftime('%Y-%m-%d')}<br>Applications: {int(count)}"
                    
                    z_columns.append(week_values.reshape(-1, 1))
                    hover_columns.append(np.array(week_hover).reshape(-1, 1))
                    col_idx += 1
                
                current_week_start += timedelta(days=7)
            
            # Add gap between months (except for last month)
            if month_end < end_date:
                z_columns.append(np.full((7, 1), np.nan))
                hover_columns.append(np.full((7, 1), ""))
                col_idx += 1
        
        # Combine all columns
        if z_columns:
            final_z = np.hstack(z_columns)
            final_hover = np.hstack(hover_columns)
        else:
            final_z = np.array([[0]])
            final_hover = np.array([["No data"]])
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=final_z,
            y=["Sat", "Fri", "Thu", "Wed", "Tue", "Mon", "Sun"],  # Flipped: Sat at top, Sun at bottom
            customdata=final_hover,
            hovertemplate="%{customdata}<extra></extra>",
            colorscale=[
                [0, "#2c2f33"],
                [0.01, "#3d5a80"],
                [0.3, "#5d8eff"],
                [0.6, "#7da3ff"],
                [1.0, "#a8c7fa"]
            ],
            showscale=True,
            colorbar=dict(
                thickness=12,
                len=0.6,
                x=1.01,
                y=0.5,
                bgcolor='rgba(0,0,0,0)',
                bordercolor='rgba(0,0,0,0)',
                borderwidth=0,
                tickfont=dict(size=9, color='#c2c7ce', family='Roboto'),
                tickmode='linear',
                tick0=0,
                dtick=1
            ),
            xgap=2,
            ygap=2
        ))
        
        # Clean layout with no borders
        fig.update_layout(
            title=dict(
                text="Application Timeline",
                font=dict(size=14, color='#e2e2e6', family='Roboto'),
                x=0.02,
                y=0.95
            ),
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=100, r=50, t=50, b=20),
            xaxis=dict(
                tickmode='array',
                tickvals=x_positions,
                ticktext=x_labels,
                side='top',
                showgrid=False,
                showline=False,
                zeroline=False,
                linewidth=0,
                mirror=False,
                ticks='',
                tickfont=dict(size=11, color='#c2c7ce', family='Roboto'),
                fixedrange=True
            ),
            yaxis=dict(
                showgrid=False,
                showline=False,
                zeroline=False,
                linewidth=0,
                mirror=False,
                ticks='',
                tickfont=dict(size=11, color='#c2c7ce', family='Roboto'),
                fixedrange=True,
                constrain='domain',
                scaleanchor="x",
                scaleratio=1
            ),
            font=dict(color='#e2e2e6', family='Roboto'),
            dragmode=False,
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error: {str(e)}",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
            font=dict(color='#f2b8b5')
        )
        fig.update_layout(
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig


def create_category_donut(applications_data):
    """Create a minimal donut chart for application categories."""
    if not applications_data:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="Categories",
            height=380,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e2e6'
        )
        return fig
    
    # Count applications by category
    df = pd.DataFrame(applications_data)
    category_counts = df['category'].value_counts()
    
    # Create subtle monochrome color palette with minimal contrast differences
    monochrome_colors = [
        '#8b9dc3',  # Light blue-gray
        '#7b8fb5',  # Medium blue-gray  
        '#6b81a7',  # Darker blue-gray
        '#5b7399',  # Deep blue-gray
        '#4b658b',  # Dark blue-gray
        '#3b577d',  # Very dark blue-gray
        '#6366f1',  # Single subtle accent (indigo)
        '#5856eb',  # Darker indigo
        '#4f46e5'   # Darkest indigo
    ]
    
    colors = monochrome_colors[:len(category_counts)]
    
    fig = go.Figure(data=[go.Pie(
        labels=category_counts.index,
        values=category_counts.values,
        hole=0.65,
        marker=dict(
            colors=colors,
            line=dict(color='#1f2937', width=1)
        ),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=11, color='#d1d5db', family='Roboto'),
        hovertemplate='<b>%{label}</b><br>%{value} applications<extra></extra>',
        showlegend=False,
        pull=[0.01] * len(category_counts)  # Subtle separation
    )])
    
    fig.update_layout(
        title=dict(
            text="Categories",
            font=dict(size=14, color='#f9fafb', family='Roboto'),
            x=0.5,
            y=0.95
        ),
        height=380,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=50, b=40),
        showlegend=False,
        font=dict(color='#d1d5db', family='Roboto')
    )
    
    return fig


def create_status_distribution(applications_data):
    """Create a horizontal bar chart showing status distribution."""
    if not applications_data:
        # Return empty figure if no data
        fig = go.Figure()
        fig.update_layout(
            title="Status Distribution",
            height=380,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e2e6'
        )
        return fig
    
    # Count applications by status
    df = pd.DataFrame(applications_data)
    status_counts = df['status'].value_counts()
    
    # Define status colors (matching your existing status indicators)
    status_colors = {
        'Applied': '#5d8eff',
        'Online Assessment': '#f29e4c', 
        'Interviewing: 1st round': '#f76f8e',
        'Interviewing: 2nd round': '#f76f8e',
        'Interviewing: 3rd round': '#f76f8e',
        'Interviewing: 4th round': '#f76f8e', 
        'Interviewing: 5th round': '#f76f8e',
        'Rejected': '#909da2',
        'Offer': '#54c184'
    }
    
    colors = [status_colors.get(status, '#6b7280') for status in status_counts.index]
    
    fig = go.Figure(data=[go.Bar(
        y=status_counts.index,
        x=status_counts.values,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='#1f2937', width=1)
        ),
        text=status_counts.values,
        textposition='inside',
        textfont=dict(size=11, color='white', family='Roboto'),
        hovertemplate='<b>%{y}</b><br>%{x} applications<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text="Status Distribution",
            font=dict(size=14, color='#f9fafb', family='Roboto'),
            x=0.5,
            y=0.95
        ),
        height=380,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=40, t=50, b=40),
        xaxis=dict(
            showgrid=True,
            gridcolor='#374151',
            gridwidth=1,
            tickfont=dict(size=10, color='#c2c7ce', family='Roboto'),
            title=dict(text="Number of Applications", font=dict(size=11, color='#c2c7ce', family='Roboto'))
        ),
        yaxis=dict(
            showgrid=False,
            tickfont=dict(size=10, color='#c2c7ce', family='Roboto'),
            categoryorder='total ascending'
        ),
        showlegend=False,
        font=dict(color='#d1d5db', family='Roboto')
    )
    
    return fig


def create_sankey_chart(sankey_data):
    """Create a Sankey diagram showing status flow using pre-computed transitions - EXACTLY matching original app.py."""
    if not sankey_data:
        fig = go.Figure()
        fig.update_layout(
            title="Application Status Flow - No Data",
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e2e6'
        )
        return fig
    
    import pandas as pd
    
    # Convert to DataFrame
    df_sankey = pd.DataFrame(sankey_data)
    
    if df_sankey.empty:
        fig = go.Figure()
        fig.update_layout(
            title="Application Status Flow - No Transitions",
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e2e6'
        )
        return fig
    
    # Use original Sankey logic exactly
    all_nodes = list(pd.unique(df_sankey[["status", "next_status"]].values.ravel("K")))
    if "No Response" not in all_nodes:
        all_nodes.append("No Response")
    node_map = {node: i for i, node in enumerate(all_nodes)}

    fig = go.Figure(
        go.Sankey(
            arrangement="snap",
            node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=all_nodes, color="#a8c7fa"),
            link=dict(
                source=df_sankey["status"].map(node_map),
                target=df_sankey["next_status"].map(node_map),
                value=df_sankey["value"],
                color="rgba(168, 199, 250, 0.6)",
            ),
        )
    )
    fig.update_layout(
        title_text="Application Status Flow", 
        font_size=10,
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='#e2e2e6'
    )
    return fig 