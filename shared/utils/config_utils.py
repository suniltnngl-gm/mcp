import json
from pathlib import Path

def get_workspace_path() -> Path:
    """
    Reads the workspace path from the config file.
    """
    # This is not ideal, but it's better than having the path hardcoded everywhere.
    # A better solution would be to find the project root dynamically.
    config_path = Path("/media/sunil-kr/workspace/user-projects/workspace-automation/config/workspace_config.json")
    with open(config_path, "r") as f:
        config = json.load(f)
    return Path(config["workspace_path"])
