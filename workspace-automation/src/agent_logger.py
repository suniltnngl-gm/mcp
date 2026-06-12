import datetime
import os
import json
from typing import Any, Dict, Optional


class AgentLogger:
    def __init__(self, log_file_path: str = "AGENT_LOG.md"):
        self.log_file_path = log_file_path
        self._ensure_log_file_exists()

    def _ensure_log_file_exists(self):
        """Ensures the log file and its directory exist."""
        log_dir = os.path.dirname(self.log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        if not os.path.exists(self.log_file_path):
            with open(self.log_file_path, "w") as f:
                f.write("# Agent Operation Log\n\n")
                f.write(
                    "This document tracks significant actions and decisions made by the AI agent.\n"
                )
                f.write(
                    "Each entry includes details on *Why*, *What*, *How*, and *When* the action was performed.\n\n"
                )

    def log_action(
        self,
        why: str,
        what: str,
        how: str,
        result: str,
        task_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """
        Logs a significant action performed by the agent.

        Args:
            why (str): The reason or motivation behind the action.
            what (str): A description of the action performed.
            how (str): The method or tool used to perform the action (e.g., tool call, specific command).
            result (str): The outcome or direct result of the action.
            task_id (str, optional): The ID of the PLAN.md task this action relates to.
            context (Dict[str, Any], optional): Additional contextual information in a dictionary.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"## Action Log Entry - {timestamp}\n"

        if task_id:
            log_entry += f"**Task ID:** {task_id}\n"
        log_entry += f"**Why:** {why}\n"
        log_entry += f"**What:** {what}\n"
        log_entry += f"**How:** {how}\n"
        log_entry += f"**Result:**\n```\n{result}\n```\n"
        if context:
            log_entry += "**Context:**\n```json\n"
            log_entry += json.dumps(context, indent=2)
            log_entry += "\n```\n"
        log_entry += "---\n\n"

        with open(self.log_file_path, "a") as f:
            f.write(log_entry)

        print(f"Logged action to {self.log_file_path}")


# Example Usage (for demonstration, agent will call this directly)
if __name__ == "__main__":
    logger = AgentLogger("AGENT_LOG.md")
    logger.log_action(
        why="To test the logging mechanism.",
        what="Created a test log entry.",
        how="Called AgentLogger.log_action function.",
        result="Log entry successfully written to AGENT_LOG.md.",
        task_id="TEST-001",
        context={"test_param": "value", "another_detail": 123},
    )
