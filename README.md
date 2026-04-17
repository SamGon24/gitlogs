# gitlogs

Analyze any git repository's commit history and surface behavioral patterns, productivity insights, and AI-powered summaries.

## Features

- **Commit heatmap** — 7×24 grid showing when you code most
- **Hourly & daily breakdowns** — bar charts with peak periods highlighted
- **Weekly trend** — line chart with 4-week rolling average
- **Streak calendar** — consecutive coding day streaks
- **Top contributors** — ranked by commit count
- **AI Insights** — Claude-powered summary of your coding behavior and patterns
- **Author filter** — drill down into any contributor's activity
- **CSV export** — download the raw commit data

## Supported Sources

- Public GitHub, GitLab, or Bitbucket repos (via `.git` URL)
- Local repositories on your machine

## Running Locally

**1. Clone the repo**
```bash
git clone https://github.com/SamGon24/gitlogs.git
cd gitlogs
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your Anthropic API key**

Create `.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

Get a key at [console.anthropic.com](https://console.anthropic.com).

**4. Run**
```bash
streamlit run app.py
```

## Deploying to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. Set the main file to `app.py`
4. In **Settings → Secrets**, add:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```
5. Deploy

## Stack

- [Streamlit](https://streamlit.io) — UI
- [GitPython](https://gitpython.readthedocs.io) — repo ingestion
- [pandas](https://pandas.pydata.org) — data transforms
- [Plotly](https://plotly.com/python) — charts
- [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) — AI insights
