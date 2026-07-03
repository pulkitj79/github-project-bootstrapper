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


def create_project(
    token,
    project_name
):
    owner_id = get_viewer_id(
        token
    )

    mutation = """
    mutation(
      $ownerId: ID!,
      $title: String!
    ) {
      createProjectV2(
        input: {
          ownerId: $ownerId,
          title: $title
        }
      ) {
        projectV2 {
          id
        }
      }
    }
    """

    data = graphql_request(
        token,
        mutation,
        {
            "ownerId": owner_id,
            "title": project_name
        }
    )

    return (
        data
        ["createProjectV2"]
        ["projectV2"]
        ["id"]
    )


def ensure_project_exists(
    token,
    project_name
):
    project_id = find_project(
        token,
        project_name
    )

    if project_id:
        return project_id

    print(
        f"Creating project: "
        f"{project_name}"
    )

    return create_project(
        token,
        project_name
    )


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
    project_id = (
        ensure_project_exists(
            token,
            project_name
        )
    )

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