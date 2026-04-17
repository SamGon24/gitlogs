import pandas as pd


def analyze(df: pd.DataFrame, author_filter: str = "All") -> dict:
    """
    Analyze commit DataFrame and return insights dict.
    
    Args:
        df: DataFrame from load_commits with columns: sha, email, author, timestamp, message, etc.
        author_filter: Email to filter by, or "All" for no filter.
    
    Returns:
        dict with keys: df, stats, heatmap, hourly, daily, weekly, streaks, authors, messages
    """
    if df.empty:
        return {
            "df": df,
            "stats": {},
            "heatmap": pd.DataFrame(),
            "hourly": pd.Series(),
            "daily": pd.Series(),
            "weekly": pd.Series(),
            "streaks": {},
            "authors": pd.Series(),
            "messages": [],
        }
    
    # Filter by author
    if author_filter != "All":
        filtered_df = df[df["email"] == author_filter].reset_index(drop=True)
    else:
        filtered_df = df.copy()
    
    if filtered_df.empty:
        return {
            "df": filtered_df,
            "stats": {},
            "heatmap": pd.DataFrame(),
            "hourly": pd.Series(),
            "daily": pd.Series(),
            "weekly": pd.Series(),
            "streaks": {},
            "authors": pd.Series(),
            "messages": [],
        }
    
    # Extract messages
    messages = filtered_df["message"].tolist()
    
    # Hourly, daily, weekly counts
    hourly = filtered_df["hour"].value_counts().sort_index()
    daily = filtered_df["day_name"].value_counts().reindex(
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    )
    weekly = filtered_df.groupby(["year", "week"]).size()
    
    # Heatmap: 7×24 pivot (day_name × hour), Monday-first
    heatmap_pivot = filtered_df.groupby(["day_name", "hour"]).size().unstack(fill_value=0)
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    heatmap_pivot = heatmap_pivot.reindex(
        [d for d in day_order if d in heatmap_pivot.index]
    )
    
    # Streaks: consecutive days with commits
    unique_dates = pd.to_datetime(filtered_df["date"]).unique()
    unique_dates = pd.Series(unique_dates).sort_values().reset_index(drop=True)
    
    streaks_info = _calculate_streaks(unique_dates)
    
    # Stats
    busiest_hour = hourly.idxmax() if not hourly.empty else None
    busiest_day = daily.idxmax() if not daily.empty else None
    gap_hours = filtered_df["gap_hours"].dropna()
    longest_gap = gap_hours.max() if not gap_hours.empty else None
    
    first_commit = filtered_df["timestamp"].min()
    last_commit = filtered_df["timestamp"].max()
    date_range_days = (last_commit - first_commit).days
    
    stats = {
        "total_commits": len(filtered_df),
        "avg_per_week": len(filtered_df) / max(1, (date_range_days / 7)),
        "busiest_hour": int(busiest_hour) if busiest_hour is not None else None,
        "busiest_day": busiest_day,
        "longest_streak": streaks_info["longest"],
        "current_streak": streaks_info["current"],
        "longest_gap": round(longest_gap, 2) if longest_gap is not None else None,
        "unique_authors": filtered_df["email"].nunique(),
        "first_commit": first_commit.isoformat(),
        "last_commit": last_commit.isoformat(),
        "date_range_days": date_range_days,
    }
    
    # Authors: counts per email, sorted descending
    authors = filtered_df["email"].value_counts()
    
    return {
        "df": filtered_df,
        "stats": stats,
        "heatmap": heatmap_pivot,
        "hourly": hourly,
        "daily": daily,
        "weekly": weekly,
        "streaks": streaks_info,
        "authors": authors,
        "messages": messages,
    }


def _calculate_streaks(unique_dates: pd.Series) -> dict:
    """
    Calculate longest and current consecutive-day streaks.
    
    Args:
        unique_dates: Series of unique dates (sorted) when commits occurred.
    
    Returns:
        dict with keys: longest, current, streak_calendar
    """
    if len(unique_dates) == 0:
        return {"longest": 0, "current": 0, "streak_calendar": pd.Series()}
    
    # Convert to datetime if not already
    if unique_dates.dtype != "datetime64[ns]":
        unique_dates = pd.to_datetime(unique_dates)
    
    # Calculate day differences
    diffs = unique_dates.diff().dt.days
    
    # Find streaks: where diff == 1 (consecutive days)
    streaks_list = []
    current_streak = 1
    
    for i in range(1, len(diffs)):
        if diffs.iloc[i] == 1:
            current_streak += 1
        else:
            if current_streak > 0:
                streaks_list.append(current_streak)
            current_streak = 1
    
    streaks_list.append(current_streak)
    
    longest = max(streaks_list) if streaks_list else 1
    
    # Current streak: from last date backward
    current = 1
    for i in range(len(diffs) - 1, 0, -1):
        if diffs.iloc[i] == 1:
            current += 1
        else:
            break
    
    # Streak calendar: date → commit count
    streak_calendar = pd.Series(
        [1] * len(unique_dates),
        index=unique_dates,
        name="commit_count"
    )
    
    return {
        "longest": longest,
        "current": current,
        "streak_calendar": streak_calendar,
    }


def get_author_list(df: pd.DataFrame) -> list:
    """
    Get list of all unique authors sorted by commit count, with "All" first.
    
    Args:
        df: DataFrame from load_commits.
    
    Returns:
        ["All", email1, email2, ...] sorted by commit count descending.
    """
    if df.empty:
        return ["All"]
    
    author_counts = df["email"].value_counts()
    return ["All"] + author_counts.index.tolist()
