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
    "P1": "B60205",
    "P2": "FBCA04",
    "P3": "0E8A16"
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
    current_milestone = None

    lines = markdown_path.read_text(
        encoding="utf-8"
    ).splitlines()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.startswith("# Milestone:"):
            current_milestone = (
                line.replace(
                    "# Milestone:",
                    ""
                ).strip()
            )
            continue

        if line.startswith("## "):
            current_section = (
                line[3:].strip()
            )
            continue

        if re.match(r"^- ", line):
            item = line[2:].strip()

            priority_match = re.match(
                r"\[(P[123])\]\s+(.*)",
                item,
                re.IGNORECASE
            )

            if priority_match:
                priority = (
                    priority_match.group(1)
                    .upper()
                )

                title = (
                    priority_match.group(2)
                    .strip()
                )

            else:
                priority = "P3"
                title = item

            issues.append(
                {
                    "title": title,
                    "section": current_section,
                    "priority": priority,
                    "milestone": current_milestone
                }
            )

    return issues


def build_issue_body(issue):
    body = (
        f"Category: {issue['section']}\n"
        f"Priority: {issue['priority']}\n"
    )

    if issue.get("milestone"):
        body += (
            f"Milestone: "
            f"{issue['milestone']}\n"
        )

    body += (
        "\nGenerated automatically "
        "from project-plan.md"
    )

    return body


def ensure_label_exists(
    repo,
    label_name
):
    existing_labels = {
        label.name.lower(): label
        for label in repo.get_labels()
    }

    if (
        label_name.lower()
        in existing_labels
    ):
        return existing_labels[
            label_name.lower()
        ]

    color = LABEL_COLORS.get(
        label_name,
        "0366D6"
    )

    print(
        f"Creating label: "
        f"{label_name}"
    )

    return repo.create_label(
        name=label_name,
        color=color
    )


def ensure_milestone_exists(
    repo,
    milestone_name
):
    if not milestone_name:
        return None

    for milestone in repo.get_milestones(
        state="all"
    ):
        if (
            milestone.title.lower()
            ==
            milestone_name.lower()
        ):
            return milestone

    print(
        f"Creating milestone: "
        f"{milestone_name}"
    )

    return repo.create_milestone(
        title=milestone_name
    )


def get_existing_issue_titles(
    repo
):
    return {
        issue.title
        for issue in repo.get_issues(
            state="all"
        )
    }


def find_issue_by_title(
    repo,
    title
):
    for issue in repo.get_issues(
        state="all"
    ):
        if issue.title == title:
            return issue

    return None


def create_single_issue(
    repo,
    issue
):
    section_label = (
        ensure_label_exists(
            repo,
            issue["section"]
        )
    )

    priority_label = (
        ensure_label_exists(
            repo,
            issue["priority"]
        )
    )

    milestone = (
        ensure_milestone_exists(
            repo,
            issue.get(
                "milestone"
            )
        )
    )

    repo.create_issue(
        title=issue["title"],
        body=build_issue_body(
            issue
        ),
        labels=[
            section_label,
            priority_label
        ],
        milestone=milestone
    )


def compare_issue(
    github_issue,
    issue_definition
):
    expected_body = (
        build_issue_body(
            issue_definition
        )
    )

    current_labels = {
        label.name
        for label
        in github_issue.labels
    }

    expected_labels = {
        issue_definition["section"],
        issue_definition["priority"]
    }

    current_milestone = (
        github_issue.milestone.title
        if github_issue.milestone
        else None
    )

    expected_milestone = (
        issue_definition.get(
            "milestone"
        )
    )

    body_changed = (
        (github_issue.body or "")
        != expected_body
    )

    labels_changed = (
        current_labels
        != expected_labels
    )

    milestone_changed = (
        current_milestone
        != expected_milestone
    )

    return (
        body_changed
        or labels_changed
        or milestone_changed
    )


def sync_issue(
    repo,
    github_issue,
    issue_definition
):
    section_label = (
        ensure_label_exists(
            repo,
            issue_definition["section"]
        )
    )

    priority_label = (
        ensure_label_exists(
            repo,
            issue_definition["priority"]
        )
    )

    milestone = (
        ensure_milestone_exists(
            repo,
            issue_definition.get(
                "milestone"
            )
        )
    )

    github_issue.edit(
        body=build_issue_body(
            issue_definition
        ),
        labels=[
            section_label.name,
            priority_label.name
        ],
        milestone=milestone
    )


def create_issues(
    repo,
    issues
):
    existing_titles = (
        get_existing_issue_titles(
            repo
        )
    )

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

        try:
            create_single_issue(
                repo,
                issue
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
    print(
        f"Created : {created}"
    )
    print(
        f"Skipped : {skipped}"
    )


def sync_issues(
    repo,
    issues
):
    created = 0
    updated = 0
    skipped = 0

    for issue_definition in issues:
        title = (
            issue_definition["title"]
        )

        try:
            github_issue = (
                find_issue_by_title(
                    repo,
                    title
                )
            )

            if github_issue is None:
                create_single_issue(
                    repo,
                    issue_definition
                )

                print(
                    f"CREATED : {title}"
                )

                created += 1
                continue

            if compare_issue(
                github_issue,
                issue_definition
            ):
                sync_issue(
                    repo,
                    github_issue,
                    issue_definition
                )

                print(
                    f"UPDATED : {title}"
                )

                updated += 1

            else:
                print(
                    f"SKIP    : {title}"
                )

                skipped += 1

        except GithubException as ex:
            print(
                f"ERROR   : {title}"
            )

            print(ex.data)

    print("\nSummary")
    print("-" * 40)
    print(
        f"Created : {created}"
    )
    print(
        f"Updated : {updated}"
    )
    print(
        f"Skipped : {skipped}"
    )


def dry_run(
    issues
):
    print("\nDRY RUN")
    print("-" * 60)

    for issue in issues:
        milestone = (
            issue.get(
                "milestone"
            )
            or "None"
        )

        print(
            f"[{issue['priority']}] "
            f"[{issue['section']}] "
            f"[{milestone}] "
            f"{issue['title']}"
        )

    print("-" * 60)
    print(
        f"Total Issues: "
        f"{len(issues)}"
    )


def main():
    parser = argparse.ArgumentParser(
        description=
        "GitHub Project Bootstrapper"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Preview issues "
            "without creating them"
        )
    )

    parser.add_argument(
        "--sync",
        action="store_true",
        help=(
            "Synchronize "
            "existing issues"
        )
    )

    args = parser.parse_args()

    try:
        print(
            "Loading configuration..."
        )

        settings = load_settings()

        issues = parse_markdown(
            "PROJECT-PLAN.md"
        )

        print(
            f"Found "
            f"{len(issues)} "
            f"issue(s)"
        )

        if args.dry_run:
            dry_run(issues)
            return

        token = (
            get_github_token()
        )

        print(
            "Connecting to GitHub..."
        )

        auth = Auth.Token(
            token
        )

        github_client = Github(
            auth=auth
        )

        repo = (
            github_client.get_repo(
                settings["repo_name"]
            )
        )

        print(
            f"Connected to: "
            f"{repo.full_name}"
        )

        if args.sync:
            print(
                "\nSynchronizing "
                "issues...\n"
            )

            sync_issues(
                repo,
                issues
            )

        else:
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