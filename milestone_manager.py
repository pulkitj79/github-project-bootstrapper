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