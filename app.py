import streamlit as st

from git_loader import load_commits
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
        options=["GitHub URL", "Local Path"],
        index=0,
    )
    
    if source_type == "GitHub URL":
        source = st.text_input(
            "GitHub URL",
            placeholder="https://github.com/user/repo",
            value="",
        )
    else:
        source = st.text_input(
            "Local Path",
            placeholder="/path/to/repo",
            value="",
        )
    
    # Branch and max commits
    branch = st.text_input("Branch", value="main", placeholder="main")
    max_commits = st.slider("Max Commits", min_value=10, max_value=1000, value=500)
    
    # Analyze button
    analyze_button = st.button("🔍 Analyze", use_container_width=True, type="primary")
    
    if analyze_button:
        if not source:
            st.error("Please enter a repository source.")
        else:
            with st.spinner("Loading commits..."):
                try:
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
