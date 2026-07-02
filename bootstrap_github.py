from pathlib import Path
import json
import os
import re
import sys
import argparse

from github import Github, Auth
from github.GithubException import GithubException


LABEL_COLORS = {
    "Epic: Scanning": "1D76DB",
    "Epic: Reporting": "0E8A16",
    "Epic: Classification": "5319E7",
    "General": "D4C5F9",

    "P1": "B60205",      # Red
    "P2": "FBCA04",      # Yellow
    "P3": "0E8A16"       # Green
}


def get_github_token():

    token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN environment variable not found."
        )

    return token


def load_settings():

    config_file = Path("config/settings.json")

    if not config_file.exists():
        raise FileNotFoundError(
            f"Settings file not found: {config_file}"
        )

    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_markdown(markdown_file):

    markdown_path = Path(markdown_file)

    if not markdown_path.exists():
        raise FileNotFoundError(
            f"Markdown file not found: {markdown_file}"
        )

    issues = []

    current_section = "General"

    lines = markdown_path.read_text(
        encoding="utf-8"
    ).splitlines()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if line.startswith("## "):

            current_section = line[3:].strip()

        elif re.match(r"^- ", line):

            item = line[2:].strip()

            priority_match = re.match(
                r"\[(P[123])\]\s+(.*)",
                item,
                re.IGNORECASE
            )

            if priority_match:

                priority = priority_match.group(1).upper()
                title = priority_match.group(2).strip()

            else:

                priority = "P3"
                title = item

            issues.append(
                {
                    "title": title,
                    "section": current_section,
                    "priority": priority
                }
            )

    return issues


def ensure_label_exists(repo, label_name):

    existing_labels = {
        label.name.lower(): label
        for label in repo.get_labels()
    }

    if label_name.lower() in existing_labels:

        return existing_labels[
            label_name.lower()
        ]

    color = LABEL_COLORS.get(
        label_name,
        "0366D6"
    )

    print(
        f"Creating label: {label_name}"
    )

    return repo.create_label(
        name=label_name,
        color=color
    )


def get_existing_issue_titles(repo):

    return {
        issue.title
        for issue in repo.get_issues(
            state="all"
        )
    }


def create_issues(repo, issues):

    existing_titles = get_existing_issue_titles(repo)

    created = 0
    skipped = 0

    for issue in issues:

        title = issue["title"]

        if title in existing_titles:

            print(
                f"SKIP    : {title}"
            )

            skipped += 1
            continue

        section_label = ensure_label_exists(
            repo,
            issue["section"]
        )

        priority_label = ensure_label_exists(
            repo,
            issue["priority"]
        )

        body = (
            f"Category: {issue['section']}\n"
            f"Priority: {issue['priority']}\n\n"
            f"Generated automatically from project-plan.md"
        )

        try:

            repo.create_issue(
                title=title,
                body=body,
                labels=[
                    section_label,
                    priority_label
                ]
            )

            print(
                f"CREATED : "
                f"[{issue['priority']}] "
                f"{title}"
            )

            created += 1

        except GithubException as ex:

            print(
                f"ERROR   : {title}"
            )

            print(ex.data)

    print("\nSummary")
    print("-" * 40)
    print(f"Created : {created}")
    print(f"Skipped : {skipped}")


def dry_run(issues):

    print("\nDRY RUN")
    print("-" * 60)

    for issue in issues:

        print(
            f"[{issue['priority']}] "
            f"[{issue['section']}] "
            f"{issue['title']}"
        )

    print("-" * 60)

    print(
        f"Total Issues: {len(issues)}"
    )


def main():

    parser = argparse.ArgumentParser(
        description="GitHub Project Bootstrapper"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview issues without creating them"
    )

    args = parser.parse_args()

    try:

        print(
            "Loading configuration..."
        )

        settings = load_settings()

        issues = parse_markdown(
            "project-plan.md"
        )

        print(
            f"Found {len(issues)} issue(s)"
        )

        if args.dry_run:

            dry_run(issues)
            return

        token = get_github_token()

        print(
            "Connecting to GitHub..."
        )

        auth = Auth.Token(token)

        github_client = Github(
            auth=auth
        )

        repo = github_client.get_repo(
            settings["repo_name"]
        )

        print(
            f"Connected to: {repo.full_name}"
        )

        print(
            "\nCreating issues...\n"
        )

        create_issues(
            repo,
            issues
        )

    except Exception as ex:

        print("\nFAILED")
        print("-" * 40)
        print(str(ex))

        sys.exit(1)


if __name__ == "__main__":
    main()