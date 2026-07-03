import os

from github import Github, Auth


def get_github_token():
    token = os.getenv(
        "GITHUB_TOKEN"
    )

    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN environment "
            "variable not found."
        )

    return token


def connect_to_github(
    repo_name
):
    print(
        "Connecting to GitHub..."
    )

    auth = Auth.Token(
        get_github_token()
    )

    github_client = Github(
        auth=auth
    )

    repo = (
        github_client.get_repo(
            repo_name
        )
    )

    return (
        github_client,
        repo
    )