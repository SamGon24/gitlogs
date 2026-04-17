import pandas as pd
import plotly.graph_objects as go

# Color palette
COLOR_PURPLE = "#7F77DD"
COLOR_TEAL = "#1D9E75"
COLOR_AMBER = "#EF9F27"


def heatmap(pivot: pd.DataFrame) -> go.Figure:
    """
    Create 7×24 heatmap (day × hour) of commit distribution.
    
    Args:
        pivot: DataFrame with day_name as index, hour as columns, values as commit counts.
    
    Returns:
        Plotly Figure with purple colorscale.
    """
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale="Purples",
            colorbar=dict(title="Commits"),
        )
    )
    
    fig.update_layout(
        title="Commit Heatmap (Day × Hour)",
        xaxis_title="Hour of Day",
        yaxis_title="Day of Week",
        template="plotly",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
    )
    
    return fig


def hourly_bar(hourly: pd.Series) -> go.Figure:
    """
    Create bar chart of commits per hour with peak highlighted.
    
    Args:
        hourly: Series with hour as index, commit count as value.
    
    Returns:
        Plotly Figure with peak hour in amber.
    """
    colors = [COLOR_AMBER if x == hourly.max() else COLOR_PURPLE for x in hourly.values]
    
    fig = go.Figure(
        data=go.Bar(
            x=hourly.index,
            y=hourly.values,
            marker=dict(color=colors),
            text=hourly.values,
            textposition="outside",
        )
    )
    
    fig.update_layout(
        title="Commits by Hour",
        xaxis_title="Hour of Day",
        yaxis_title="Commits",
        template="plotly",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
        showlegend=False,
    )
    
    return fig


def daily_bar(daily: pd.Series) -> go.Figure:
    """
    Create bar chart of commits per day with peak highlighted.
    
    Args:
        daily: Series with day_name as index, commit count as value.
    
    Returns:
        Plotly Figure with peak day in amber.
    """
    colors = [COLOR_AMBER if x == daily.max() else COLOR_PURPLE for x in daily.values]
    
    fig = go.Figure(
        data=go.Bar(
            x=daily.index,
            y=daily.values,
            marker=dict(color=colors),
            text=daily.values,
            textposition="outside",
        )
    )
    
    fig.update_layout(
        title="Commits by Day",
        xaxis_title="Day of Week",
        yaxis_title="Commits",
        template="plotly",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
        showlegend=False,
    )
    
    return fig


def weekly_trend(weekly: pd.Series) -> go.Figure:
    """
    Create line chart of weekly commit trend with 4-week rolling average.
    
    Args:
        weekly: Series with (year, week) MultiIndex, commit count as value.
    
    Returns:
        Plotly Figure with trend line and rolling average overlay.
    """
    # Convert MultiIndex to labels for x-axis
    labels = [f"{idx[0]}-W{idx[1]}" for idx in weekly.index]
    
    # Calculate 4-week rolling average
    rolling_avg = weekly.rolling(window=4, center=True).mean()
    
    fig = go.Figure()
    
    # Weekly line
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=weekly.values,
            mode="lines+markers",
            name="Weekly Commits",
            line=dict(color=COLOR_PURPLE, width=2),
            marker=dict(size=6),
        )
    )
    
    # Rolling average overlay
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=rolling_avg.values,
            mode="lines",
            name="4-Week Average",
            line=dict(color=COLOR_TEAL, width=3, dash="dash"),
        )
    )
    
    fig.update_layout(
        title="Weekly Commit Trend",
        xaxis_title="Week",
        yaxis_title="Commits",
        template="plotly",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
        hovermode="x unified",
    )
    
    return fig


def streak_calendar(date_counts: pd.Series) -> go.Figure:
    """
    Create scatter plot of commits per day (streak calendar).
    
    Args:
        date_counts: Series with dates as index, commit count as value.
    
    Returns:
        Plotly Figure with dots colored/sized by commit count.
    """
    if date_counts.empty:
        fig = go.Figure()
        fig.update_layout(title="Streak Calendar (No data)")
        return fig
    
    # Extract dates and counts
    dates = date_counts.index
    counts = date_counts.values
    
    # Normalize sizes for scatter
    size_min, size_max = 5, 20
    sizes = size_min + (counts - counts.min()) / max(1, counts.max() - counts.min()) * (size_max - size_min)
    
    fig = go.Figure(
        data=go.Scatter(
            x=dates,
            y=[1] * len(dates),  # All on same y level
            mode="markers",
            marker=dict(
                size=sizes,
                color=counts,
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(title="Commits"),
            ),
            text=[f"Date: {d.date()}<br>Commits: {c}" for d, c in zip(dates, counts)],
            hovertemplate="%{text}<extra></extra>",
        )
    )
    
    fig.update_layout(
        title="Streak Calendar",
        xaxis_title="Date",
        yaxis_title="",
        template="plotly",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=300,
        yaxis=dict(visible=False),
        showlegend=False,
    )
    
    return fig


def author_bars(authors: pd.Series) -> go.Figure:
    """
    Create horizontal bar chart of top authors by commit count.
    
    Args:
        authors: Series with email as index, commit count as value.
    
    Returns:
        Plotly Figure with top N contributors.
    """
    # Take top 10 authors
    top_authors = authors.head(10)
    
    fig = go.Figure(
        data=go.Bar(
            y=top_authors.index,
            x=top_authors.values,
            orientation="h",
            marker=dict(color=COLOR_TEAL),
            text=top_authors.values,
            textposition="outside",
        )
    )
    
    fig.update_layout(
        title="Top Contributors",
        xaxis_title="Commits",
        yaxis_title="Author",
        template="plotly",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
        showlegend=False,
    )
    
    return fig
