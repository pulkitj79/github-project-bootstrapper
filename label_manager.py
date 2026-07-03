LABEL_COLORS = {
    "Epic: Scanning": "1D76DB",
    "Epic: Reporting": "0E8A16",
    "Epic: Classification": "5319E7",
    "General": "D4C5F9",
    "P1": "B60205",
    "P2": "FBCA04",
    "P3": "0E8A16"
}


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