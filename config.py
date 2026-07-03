from pathlib import Path
import json


def load_settings():
    config_file = Path(
        "config/settings.json"
    )

    if not config_file.exists():
        raise FileNotFoundError(
            f"Settings file not found: "
            f"{config_file}"
        )

    with open(
        config_file,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)