import requests


def get_user_repos(username: str, token: str = None) -> list[str]:
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    clone_urls = []
    page = 1

    while True:
        response = requests.get(
            f"https://api.github.com/users/{username}/repos",
            headers=headers,
            params={"per_page": 100, "page": page, "sort": "pushed", "type": "owner"},
        )
        response.raise_for_status()
        repos = response.json()

        if not repos:
            break

        clone_urls.extend(repo["clone_url"] for repo in repos if not repo["fork"])
        page += 1

    return clone_urls
