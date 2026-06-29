import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_INFO_FILE = os.path.join(PROJECT_ROOT, 'config', 'environment_info.json')

def read_env_info():
    """Reads the environment information from the JSON file."""
    if not os.path.exists(ENV_INFO_FILE):
        return {}
    with open(ENV_INFO_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def write_env_info(data):
    """Writes the environment information to the JSON file."""
    os.makedirs(os.path.dirname(ENV_INFO_FILE), exist_ok=True)
    with open(ENV_INFO_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def update_env_info(key, value):
    """Updates a specific key-value pair in the environment information."""
    data = read_env_info()
    data[key] = value
    write_env_info(data)

if __name__ == "__main__":
    # Example usage:
    # python scripts/environment_manager.py update git_branch master
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "update":
        update_env_info(sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 2 and sys.argv[1] == "read":
        print(json.dumps(read_env_info(), indent=2))
    else:
        print("Usage: python scripts/environment_manager.py update <key> <value>")
        print("       python scripts/environment_manager.py read")
