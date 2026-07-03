import argparse
import sys

from config import load_settings
from parser import parse_markdown

from github_client import (
    connect_to_github,
    get_github_token
)

from issue_manager import (
    create_issues,
    sync_issues
)


def dry_run(issues):
    print("\nDRY RUN")
    print("-" * 60)

    for issue in issues:
        milestone = (
            issue.get("milestone")
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
        description="GitHub Project Bootstrapper"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true"
    )

    parser.add_argument(
        "--sync",
        action="store_true"
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
            f"Found {len(issues)} issue(s)"
        )

        if args.dry_run:
            dry_run(issues)
            return

        github_client, repo = (
            connect_to_github(
                settings["repo_name"]
            )
        )

        token = (
            get_github_token()
        )

        project_name = (
            settings.get(
                "project_name"
            )
        )

        print(
            f"Connected to: "
            f"{repo.full_name}"
        )

        if args.sync:

            print(
                "\nSynchronizing issues...\n"
            )

            sync_issues(
                repo,
                issues,
                token,
                project_name
            )

        else:

            print(
                "\nCreating issues...\n"
            )

            create_issues(
                repo,
                issues,
                token,
                project_name
            )

    except Exception as ex:

        print("\nFAILED")
        print("-" * 40)
        print(str(ex))

        sys.exit(1)


if __name__ == "__main__":
    main()