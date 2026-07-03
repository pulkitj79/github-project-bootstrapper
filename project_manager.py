import requests


GITHUB_GRAPHQL_URL = (
    "https://api.github.com/graphql"
)


def graphql_request(
    token,
    query,
    variables=None
):
    response = requests.post(
        GITHUB_GRAPHQL_URL,
        json={
            "query": query,
            "variables": variables or {}
        },
        headers={
            "Authorization":
            f"Bearer {token}"
        }
    )

    response.raise_for_status()

    payload = response.json()

    if "errors" in payload:
        raise RuntimeError(
            payload["errors"]
        )

    return payload["data"]


def get_viewer_id(
    token
):
    query = """
    query {
      viewer {
        id
      }
    }
    """

    data = graphql_request(
        token,
        query
    )

    return data[
        "viewer"
    ][
        "id"
    ]


def find_project(
    token,
    project_name
):
    query = """
    query($ownerId: ID!) {
      node(id: $ownerId) {
        ... on User {
          projectsV2(first: 100) {
            nodes {
              id
              title
            }
          }
        }
      }
    }
    """

    owner_id = get_viewer_id(
        token
    )

    data = graphql_request(
        token,
        query,
        {
            "ownerId": owner_id
        }
    )

    projects = (
        data["node"]
        ["projectsV2"]
        ["nodes"]
    )

    for project in projects:

        if (
            project["title"]
            .lower()
            ==
            project_name.lower()
        ):
            return project["id"]

    return None


def issue_already_in_project(
    token,
    project_id,
    issue_node_id
):
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          items(first: 100) {
            nodes {
              content {
                ... on Issue {
                  id
                }
              }
            }
          }
        }
      }
    }
    """

    data = graphql_request(
        token,
        query,
        {
            "projectId": project_id
        }
    )

    items = (
        data["node"]
        ["items"]
        ["nodes"]
    )

    for item in items:

        content = (
            item.get(
                "content"
            )
        )

        if not content:
            continue

        if (
            content["id"]
            ==
            issue_node_id
        ):
            return True

    return False


def add_issue_to_project(
    token,
    project_id,
    issue_node_id
):
    mutation = """
    mutation(
      $projectId: ID!,
      $contentId: ID!
    ) {
      addProjectV2ItemById(
        input: {
          projectId: $projectId,
          contentId: $contentId
        }
      ) {
        item {
          id
        }
      }
    }
    """

    graphql_request(
        token,
        mutation,
        {
            "projectId": project_id,
            "contentId": issue_node_id
        }
    )


def ensure_issue_in_project(
    token,
    github_issue,
    project_name
):
    try:

        project_id = (
            find_project(
                token,
                project_name
            )
        )

        if not project_id:

            print(
                f"WARNING : "
                f"Project '{project_name}' "
                f"not found. "
                f"Skipping project sync."
            )

            return

        issue_node_id = (
            github_issue.node_id
        )

        if issue_already_in_project(
            token,
            project_id,
            issue_node_id
        ):
            return

        print(
            f"Adding issue "
            f"#{github_issue.number} "
            f"to project"
        )

        add_issue_to_project(
            token,
            project_id,
            issue_node_id
        )

    except Exception as ex:

        print(
            f"WARNING : "
            f"Project sync failed: "
            f"{ex}"
        )

        print(
            "Continuing issue sync..."
        )