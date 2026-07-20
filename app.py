import streamlit as st

from git_loader import load_commits, load_user_commits
from analyzer import analyze, get_author_list

# Initialize Streamlit page config
st.set_page_config(
    page_title="gitlogs",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 gitlogs")
st.markdown("*Analyze your git commit history and uncover behavioral patterns.*")

# Initialize session state
if "raw_df" not in st.session_state:
    st.session_state.raw_df = None
if "results" not in st.session_state:
    st.session_state.results = None
if "ai_summary" not in st.session_state:
    st.session_state.ai_summary = None

# ============================================================================
# SIDEBAR: Configuration
# ============================================================================

with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Repo source
    source_type = st.radio(
        "Repository Source",
        options=["GitHub URL", "Local Path", "GitHub User"],
        index=0,
    )

    if source_type == "GitHub URL":
        source = st.text_input("GitHub URL", placeholder="https://github.com/user/repo", value="")
        branch = st.text_input("Branch", value="main", placeholder="main")
        max_commits = st.slider("Max Commits", min_value=10, max_value=1000, value=500)
        gh_token = None
        max_repos = None

    elif source_type == "Local Path":
        source = st.text_input("Local Path", placeholder="/path/to/repo", value="")
        branch = st.text_input("Branch", value="main", placeholder="main")
        max_commits = st.slider("Max Commits", min_value=10, max_value=1000, value=500)
        gh_token = None
        max_repos = None

    else:
        source = st.text_input("GitHub Username", placeholder="SamGon24", value="")
        gh_token = st.text_input("GitHub Token (optional)", type="password", value="")
        max_repos = st.slider("Max Repos", min_value=1, max_value=20, value=5)
        max_commits = st.slider("Max Commits per Repo", min_value=10, max_value=500, value=200)
        branch = "main"

    # Analyze button
    analyze_button = st.button("🔍 Analyze", use_container_width=True, type="primary")

    if analyze_button:
        if not source:
            st.error("Please enter a repository source.")
        else:
            with st.spinner("Loading commits..."):
                try:
                    if source_type == "GitHub User":
                        st.session_state.raw_df = load_user_commits(
                            source,
                            token=gh_token or None,
                            branch=branch,
                            max_repos=max_repos,
                            max_commits_per_repo=max_commits,
                        )
                    else:
                        st.session_state.raw_df = load_commits(source, branch, max_commits)

                    if st.session_state.raw_df.empty:
                        st.error("No commits found.")
                    else:
                        st.success(f"Loaded {len(st.session_state.raw_df)} commits!")
                except Exception as e:
                    st.error(f"Error loading repo: {e}")
    
    # Author filter (only show if data is loaded)
    if st.session_state.raw_df is not None and not st.session_state.raw_df.empty:
        st.divider()
        authors = get_author_list(st.session_state.raw_df)
        selected_author = st.selectbox("Filter by Author", authors, index=0)
        
        # Re-analyze if author changes
        if selected_author:
            st.session_state.results = analyze(st.session_state.raw_df, selected_author)

# ============================================================================
# MAIN: Initial message
# ============================================================================

if st.session_state.raw_df is None or st.session_state.raw_df.empty:
    st.info("👈 Enter a repository source in the sidebar and click **Analyze** to get started.")
    st.stop()

if st.session_state.results is None and st.session_state.raw_df is not None:
    st.session_state.results = analyze(st.session_state.raw_df, "All")

import charts

results = st.session_state.results
stats = results["stats"]

# ============================================================================
# STAT CARDS
# ============================================================================

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Commits", stats["total_commits"])
c2.metric("Avg / Week", f"{stats['avg_per_week']:.1f}")
c3.metric("Busiest Hour", f"{stats['busiest_hour']}:00" if stats["busiest_hour"] is not None else "—")
c4.metric("Busiest Day", stats["busiest_day"] or "—")
c5.metric("Longest Streak", f"{stats['longest_streak']}d")
c6.metric("Current Streak", f"{stats['current_streak']}d")

st.divider()

# ============================================================================
# HEATMAP
# ============================================================================

st.plotly_chart(charts.heatmap(results["heatmap"]), use_container_width=True)

# ============================================================================
# HOUR BAR + DAY BAR
# ============================================================================

col_h, col_d = st.columns(2)
with col_h:
    st.plotly_chart(charts.hourly_bar(results["hourly"]), use_container_width=True)
with col_d:
    st.plotly_chart(charts.daily_bar(results["daily"]), use_container_width=True)

# ============================================================================
# WEEKLY TREND
# ============================================================================

st.plotly_chart(charts.weekly_trend(results["weekly"]), use_container_width=True)

# ============================================================================
# STREAK CALENDAR + AUTHOR BARS
# ============================================================================

col_s, col_a = st.columns(2)
with col_s:
    st.plotly_chart(
        charts.streak_calendar(results["streaks"]["streak_calendar"]),
        use_container_width=True,
    )
with col_a:
    st.plotly_chart(charts.author_bars(results["authors"]), use_container_width=True)

st.divider()

# ============================================================================
# AI INSIGHTS
# ============================================================================

st.subheader("🤖 AI Insights")

if st.button("Generate AI Summary", type="primary"):
    import anthropic

    sample_messages = results["messages"][:50]
    prompt = f"""Analyze this git commit history and surface behavioral patterns.

Stats:
{stats}

Sample commit messages ({len(sample_messages)} of {stats['total_commits']}):
{chr(10).join(f'- {m}' for m in sample_messages)}

Provide a concise markdown summary covering:
1. Work patterns (peak hours, days, consistency)
2. Commit behavior (frequency, streaks, gaps)
3. Notable observations from the commit messages
4. One actionable suggestion to improve habits
"""
    with st.spinner("Generating insights..."):
        try:
            client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            st.session_state.ai_summary = response.content[0].text
        except Exception as e:
            st.error(f"Error generating summary: {e}")

if st.session_state.ai_summary:
    st.markdown(st.session_state.ai_summary)

st.divider()

# ============================================================================
# RAW DATA
# ============================================================================

with st.expander("Raw Commit Data"):
    st.dataframe(results["df"], use_container_width=True)
    csv = results["df"].to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="gitlogs_commits.csv",
        mime="text/csv",
    )
