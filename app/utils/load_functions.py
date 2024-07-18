from pathlib import Path

import joblib


def load_resources(resources_type, file_type):
    model_path = Path("app/resources") / f"{resources_type}.{file_type}"

    if file_type == "joblib":
        with open(model_path, "rb") as file:
            resources = joblib.load(file)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    return resources
