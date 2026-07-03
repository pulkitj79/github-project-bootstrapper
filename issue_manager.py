from github.GithubException import (
    GithubException
)

from parser import (
    build_issue_body
)

from label_manager import (
    ensure_label_exists
)

from milestone_manager import (
    ensure_milestone_exists
)

from project_manager import (
    ensure_issue_in_project
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

    created_issue = (
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
    )

    return created_issue


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

    return (
        (github_issue.body or "")
        != expected_body
        or current_labels
        != expected_labels
        or current_milestone
        != expected_milestone
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

    return github_issue


def create_issues(
    repo,
    issues,
    token,
    project_name
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

            github_issue = (
                create_single_issue(
                    repo,
                    issue
                )
            )

            if project_name:

                ensure_issue_in_project(
                    token,
                    github_issue,
                    project_name
                )

            print(
                f"CREATED : "
                f"[{issue['priority']}] "
                f"{title} "
                f"(#{github_issue.number})"
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
    issues,
    token,
    project_name
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

                created_issue = (
                    create_single_issue(
                        repo,
                        issue_definition
                    )
                )

                if project_name:

                    ensure_issue_in_project(
                        token,
                        created_issue,
                        project_name
                    )

                print(
                    f"CREATED : "
                    f"{title} "
                    f"(#{created_issue.number})"
                )

                created += 1
                continue

            if compare_issue(
                github_issue,
                issue_definition
            ):

                github_issue = (
                    sync_issue(
                        repo,
                        github_issue,
                        issue_definition
                    )
                )

                if project_name:

                    ensure_issue_in_project(
                        token,
                        github_issue,
                        project_name
                    )

                print(
                    f"UPDATED : "
                    f"{title}"
                )

                updated += 1

            else:

                if project_name:

                    ensure_issue_in_project(
                        token,
                        github_issue,
                        project_name
                    )

                print(
                    f"SKIP    : "
                    f"{title}"
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