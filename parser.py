from pathlib import Path
import re


def parse_markdown(
    markdown_file
):
    markdown_path = Path(
        markdown_file
    )

    if not markdown_path.exists():
        raise FileNotFoundError(
            f"Markdown file not found: "
            f"{markdown_file}"
        )

    issues = []

    current_section = "General"
    current_milestone = None

    lines = (
        markdown_path
        .read_text(
            encoding="utf-8"
        )
        .splitlines()
    )

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.startswith(
            "# Milestone:"
        ):
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

        if re.match(
            r"^- ",
            line
        ):
            item = line[2:].strip()

            priority_match = re.match(
                r"\[(P[123])\]\s+(.*)",
                item,
                re.IGNORECASE
            )

            if priority_match:
                priority = (
                    priority_match
                    .group(1)
                    .upper()
                )

                title = (
                    priority_match
                    .group(2)
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


def build_issue_body(
    issue
):
    body = (
        f"Category: "
        f"{issue['section']}\n"
        f"Priority: "
        f"{issue['priority']}\n"
    )

    if issue.get(
        "milestone"
    ):
        body += (
            f"Milestone: "
            f"{issue['milestone']}\n"
        )

    body += (
        "\nGenerated "
        "automatically from "
        "project-plan.md"
    )

    return body