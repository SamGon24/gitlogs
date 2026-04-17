import tempfile
from pathlib import Path

import pandas as pd
from git import Repo

_SEP = "\x1f"
_LOG_FMT = f"%h{_SEP}%ae{_SEP}%an{_SEP}%aI{_SEP}%s"


def load_commits(source: str, branch: str = "main", max_commits: int = 500) -> pd.DataFrame:
    if source.startswith("http://") or source.startswith("https://"):
        tmp = tempfile.TemporaryDirectory()
        repo = Repo.clone_from(source, tmp.name, depth=max_commits, branch=branch)
    else:
        path = Path(source)
        if not (path / ".git").exists():
            raise ValueError(f"No .git directory found at {source}")
        repo = Repo(source)

    log_output = repo.git.log(
        f"-{max_commits}",
        f"--format={_LOG_FMT}",
        branch,
    )

    if not log_output.strip():
        return pd.DataFrame()

    rows = []
    for line in log_output.splitlines():
        parts = line.split(_SEP, 4)
        if len(parts) == 5:
            rows.append(parts)

    df = pd.DataFrame(rows, columns=["sha", "email", "author", "timestamp", "message"])

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp").reset_index(drop=True)

    df["date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["day_name"] = df["timestamp"].dt.day_name()
    df["week"] = df["timestamp"].dt.isocalendar().week.astype(int)
    df["year"] = df["timestamp"].dt.year
    df["month"] = df["timestamp"].dt.month
    df["gap_hours"] = (
        df["timestamp"].diff().dt.total_seconds().div(3600).round(2)
    )

    return df
