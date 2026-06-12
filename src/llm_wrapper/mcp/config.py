import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ValidationError


class LocalServerConfig(BaseModel):
    """Configuration for a local MCP server."""

    command: List[str] = Field(
        ..., description="The command and arguments to start the local server."
    )
    args: Optional[List[str]] = Field(
        None, description="Additional arguments to pass to the server command."
    )
    env: Optional[Dict[str, str]] = Field(
        None, description="Environment variables for the server process."
    )
    client_config: Optional[Dict[str, Any]] = Field(
        None, description="Client-specific configuration for this server."
    )


class RemoteServerConfig(BaseModel):
    """Configuration for a remote MCP server."""

    url: str = Field(..., description="The URL of the remote MCP server.")
    api_key: Optional[str] = Field(
        None, description="API key for authenticating with the remote server."
    )
    client_config: Optional[Dict[str, Any]] = Field(
        None, description="Client-specific configuration for this server."
    )


class ServerDefinition(BaseModel):
    """Defines a single MCP server, either local or remote."""

    type: str = Field(
        ...,
        pattern="^(local|remote)$",
        description="The type of the server (e.g., 'local', 'remote').",
    )
    config: Any = Field(
        ..., description="The specific configuration for the server type."
    )

    def model_post_init(self, __context: Any) -> None:
        if self.type == "local":
            self.config = LocalServerConfig(**self.config)
        elif self.type == "remote":
            self.config = RemoteServerConfig(**self.config)
        else:
            raise ValueError(f"Unknown server type: {self.type}")


class McpConfig(BaseModel):
    """Overall Model Context Protocol (MCP) configuration."""

    mcpServers: Dict[str, ServerDefinition] = Field(
        ..., description="A dictionary of named MCP server definitions."
    )
    default_server: Optional[str] = Field(
        None, description="The name of the default server to use."
    )


def find_mcp_json_path(search_paths: Optional[List[Path]] = None) -> Optional[Path]:
    """
    Searches for 'mcp.json' in a list of predefined paths.
    """
    if search_paths is None:
        # Default search paths
        search_paths = [
            Path("mcp.json"),  # Current working directory
            Path.home() / ".config" / "mcp.json",  # User config directory
            Path.home()
            / ".aws"
            / "amazonq"
            / "mcp.json",  # Specific AWS Q location mentioned in GEMINI.md
        ]

    for path in search_paths:
        if path.is_file():
            return path
    return None


def load_mcp_config(mcp_json_path: Optional[Path] = None) -> Optional[McpConfig]:
    """
    Loads and validates the MCP configuration from 'mcp.json'.

    Args:
        mcp_json_path: Optional path to the mcp.json file. If not provided,
                       it searches in common locations.

    Returns:
        An McpConfig object if successful, None otherwise.
    """
    if mcp_json_path is None:
        mcp_json_path = find_mcp_json_path()

    if not mcp_json_path:
        print("Error: mcp.json not found in common locations.")
        return None

    try:
        with open(mcp_json_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        return McpConfig(**config_data)
    except FileNotFoundError:
        print(f"Error: mcp.json not found at {mcp_json_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {mcp_json_path}: {e}")
        return None
    except ValidationError as e:
        print(f"Error: Configuration validation failed for {mcp_json_path}: {e}")
        return None
    except Exception as e:
        print(
            f"An unexpected error occurred while loading config from {mcp_json_path}: {e}"
        )
        return None


if __name__ == "__main__":
    # Example usage for testing
    print("Attempting to load MCP configuration...")
    # Create a dummy mcp.json for testing if it doesn't exist
    dummy_config_path = Path("mcp.json")
    if not dummy_config_path.is_file():
        print(f"Creating a dummy {dummy_config_path} for testing.")
        dummy_content = {
            "mcpServers": {
                "local_dev_server": {
                    "type": "local",
                    "config": {
                        "command": ["python", "my_mcp_server.py"],
                        "args": ["--debug"],
                        "env": {"PYTHONUNBUFFERED": "1"},
                        "client_config": {"timeout": 60},
                    },
                },
                "remote_prod_server": {
                    "type": "remote",
                    "config": {
                        "url": "https://api.example.com/mcp",
                        "api_key": "YOUR_REMOTE_API_KEY",
                    },
                },
            },
            "default_server": "local_dev_server",
        }
        with open(dummy_config_path, "w", encoding="utf-8") as f:
            json.dump(dummy_content, f, indent=2)

    config = load_mcp_config()
    if config:
        print("\nSuccessfully loaded MCP Configuration:")
        print(f"Default Server: {config.default_server}")
        for server_name, server_def in config.mcpServers.items():
            print(f"  Server: {server_name} (Type: {server_def.type})")
            if isinstance(server_def.config, LocalServerConfig):
                print(f"    Command: {server_def.config.command}")
                print(f"    Args: {server_def.config.args}")
            elif isinstance(server_def.config, RemoteServerConfig):
                print(f"    URL: {server_def.config.url}")
                print(f"    API Key (present): {bool(server_def.config.api_key)}")
    else:
        print("\nFailed to load MCP Configuration.")

    # Clean up dummy config
    if (
        dummy_config_path.is_file()
        and input("Delete dummy mcp.json? (y/N): ").lower() == "y"
    ):
        dummy_config_path.unlink()
        print(f"Deleted {dummy_config_path}.")


def create_dummy_mcp_config(path: Path, dummy_server_script_path: Path):
    """Creates a dummy mcp.json for testing purposes."""
    if not path.is_file():
        print(f"Creating a dummy {path} for testing.")
        dummy_content = {
            "mcpServers": {
                "local_dev_server": {
                    "type": "local",
                    "config": {
                        "command": ["python", str(dummy_server_script_path)],
                        "args": ["--debug"],
                        "env": {"PYTHONUNBUFFERED": "1"},
                        "client_config": {"timeout": 60},
                    },
                },
                "remote_prod_server": {
                    "type": "remote",
                    "config": {
                        "url": "http://localhost:8081",
                        "api_key": "YOUR_REMOTE_API_KEY",
                    },
                },
                "doc_manager": {
                    "type": "local",
                    "config": {
                        "command": [
                            "python",
                            "-m",
                            "src.llm_wrapper.mcp.doc_manager_server",
                        ],
                        "args": [],
                        "env": {
                            "DB_PATH": "./data/docs.db"  # Specify DB path for the server
                        },
                        "client_config": {},
                    },
                },
                "game_rules_manager": {
                    "type": "local",
                    "config": {
                        "command": [
                            "python",
                            "-m",
                            "src.llm_wrapper.mcp.game_rules_server",
                        ],
                        "args": [],
                        "env": {
                            "DB_PATH": "./data/game_rules.db"  # Specify DB path for the server
                        },
                        "client_config": {},
                    },
                },
                "system_utility": {  # Add SystemUtilityServer
                    "type": "local",
                    "config": {
                        "command": [
                            "python",
                            "-m",
                            "src.llm_wrapper.mcp.system_utility_server",
                        ],
                        "args": [],
                        "env": {
                            "SANDBOX_ROOT": "./llm_sandbox"  # Specify sandbox root for the server
                        },
                        "client_config": {},
                    },
                },
            },
            "default_server": "local_dev_server",
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dummy_content, f, indent=2)
        print("Dummy mcp.json created.")


def cleanup_dummy_mcp_config(path: Path):
    """Cleans up the dummy mcp.json file."""
    if path.is_file():
        path.unlink()
        print(f"Deleted dummy mcp.json: {path}.")
