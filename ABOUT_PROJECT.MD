GITHUB PROJECT BOOTSTRAPPER CONTEXT
Objective

Build a Python utility that converts a Markdown project plan into a fully structured GitHub project.

Target outcomes:

Personal productivity tool
GitHub portfolio project
Upwork automation showcase
Reusable open-source utility

Repository:

github-project-bootstrapper

Local:

C:\Workspace\GitRepos\GitHubProjectBootstrapper
Project Vision

The Markdown file becomes the single source of truth.

Instead of manually creating:

Issues
Labels
Milestones
Project Boards
Dependencies
Priorities

the tool automatically creates and synchronizes them in GitHub.

Current Architecture
GitHubProjectBootstrapper
│
├── bootstrap_github.py
├── PROJECT-PLAN.md
├── README.md
│
├── config
│   └── settings.json
│
└── logs
Authentication

Uses GitHub Personal Access Token.

Current implementation:

token = os.getenv("GITHUB_TOKEN")
auth = Auth.Token(token)
github_client = Github(auth=auth)

Token is stored in:

Environment Variable

Never inside:

settings.json
Current Features
Markdown Parsing

Reads:

# Epic: Scanning

- Folder Inventory
- Duplicate Detection
- Empty Folder Detection

Produces:

[
    {
        "title": "Folder Inventory",
        "epic": "Scanning"
    }
]
Issue Creation

Automatically creates GitHub Issues.

Example:

- Duplicate Detection

becomes:

GitHub Issue

with proper labels and descriptions.

Label Management

Creates labels automatically if missing.

Example:

Scanning
Reporting
Classification

Labels are created once and reused.

Duplicate Prevention

Before creating an issue:

find_issue_by_title()

Checks if issue already exists.

If found:

SKIP

instead of creating duplicates.

Dry Run Mode

Command:

python bootstrap_github.py --dry-run

Output:

Would Create:
    Folder Inventory

Would Skip:
    Duplicate Detection

No GitHub changes are made.

Current PROJECT-PLAN Structure
# Epic: Scanning

- Folder Inventory
- Duplicate Detection
- Empty Folder Detection

# Epic: Reporting

- Excel Export
- HTML Export

# Epic: Classification

- File Type Rules
- Folder Suggestions
Current Status

Implemented:

Markdown Parsing
GitHub Authentication
Issue Creation
Label Creation
Duplicate Detection
Dry Run

Stable and working.

Priority Support (Designed)

Planned enhancement:

Markdown:

- [P1] Duplicate Detection
- [P2] Empty Folder Detection
- [P3] Folder Suggestions

Parsed result:

{
    "title": "Duplicate Detection",
    "priority": "P1"
}

Auto labels:

P1
P2
P3

Default:

P3

if omitted.

Next Major Feature
v1.4 Synchronization Mode

Current behavior:

Issue Exists
→ Skip

Desired behavior:

Issue Exists
→ Compare
→ Update

Command:

python bootstrap_github.py --sync
Example

Markdown changed from:

[P2] Duplicate Detection

to:

[P1] Duplicate Detection

Sync updates:

Priority Label
Issue Body
Metadata

inside GitHub automatically.

Planned Synchronization Functions
find_issue_by_title()

compare_issue()

sync_issue()

sync_issues()
Future Roadmap
v1.5 Milestones

Markdown:

## Milestone: MVP

Creates:

GitHub Milestone

and assigns issues.

v1.6 Dependencies

Markdown:

depends-on: Folder Inventory

Creates relationship metadata.

Example:

Duplicate Detection
depends on
Folder Inventory
v1.7 GitHub Project Boards

Automatically creates:

Backlog
Ready
In Progress
Testing
Done

and populates issues.

v1.8 Issue Templates

Support:

description:
acceptance-criteria:
estimate:
owner:

Example:

- Duplicate Detection

Description:
Detect files with identical hashes.

Acceptance Criteria:
- SHA256 hashing
- Duplicate grouping
- Excel report
Long-Term Vision

A complete GitHub Project-as-Code system.

Input:

PROJECT-PLAN.md

Output:

Repository Labels
Issues
Milestones
Dependencies
Project Board
Priorities

all automatically synchronized.

Current Development Priority

Next feature:

v1.4 Synchronization Mode

Specifically:

--sync

that updates existing GitHub issues instead of skipping them.

This provides the highest value because it transforms the Markdown document into the authoritative project definition.

Development Preferences

Important:

Whenever generating code:

Provide complete module files.
Do not provide partial snippets.
If uncertain about current file contents, ask for latest versions first.
Strategic Positioning
File Guardian

Primary project.

Purpose:

Portfolio
Upwork
Potential Product

Current focus:

80%
GitHub Project Bootstrapper

Secondary project.

Purpose:

Developer Automation
GitHub Showcase
Reusable Utility

Current focus:

20%

Development should resume only after major File Guardian milestones are completed, unless a specific need arises for GitHub automation features.