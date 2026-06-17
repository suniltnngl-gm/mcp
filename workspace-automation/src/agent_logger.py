#!/usr/bin/env python3
"""Agent Logger — structured action logging for AGENT_LOG.md."""

import datetime
import os
import sys
import json
from typing import Any, Dict, Optional


class AgentLogger:
    FORMAT = """### {title}
- **Date**: {date}
- **Project**: {project}
- **Phase/Task**: {task}
- **Integration**: {integration}
- **Why**: {why}
- **What**: {what}
- **How**: {how}
- **Files**: {files}
- **Outcome**: {outcome}
- **Next**: {next}
"""

    def __init__(self, log_file_path: str = "AGENT_LOG.md"):
        self.log_file_path = log_file_path
        self._ensure_log_file_exists()

    def _ensure_log_file_exists(self):
        log_dir = os.path.dirname(self.log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        if not os.path.exists(self.log_file_path):
            header = "# Agent Log\n\nRecords all significant actions taken by the agent.\n\n"
            header += "See `ERROR_REGISTRY.md` for error-specific entries.\n\n---\n\n"
            header += "## Log Format\n\n"
            header += "Each entry follows this structure:\n\n```\n"
            header += self.FORMAT.strip()
            header += "\n```\n\n---\n\n## 2026\n"
            with open(self.log_file_path, "w") as f:
                f.write(header)

    def log_action(
        self,
        title: str = "",
        project: str = "",
        task: str = "",
        integration: str = "",
        why: str = "",
        what: str = "",
        how: str = "",
        files: str = "",
        outcome: str = "",
        next_action: str = "",
    ):
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        entry = self.FORMAT.format(
            title=title or "Untitled",
            date=date,
            project=project,
            task=task,
            integration=integration,
            why=why,
            what=what,
            how=how,
            files=files,
            outcome=outcome,
            next=next_action,
        )
        entry += "\n"
        with open(self.log_file_path, "a") as f:
            f.write(entry)
        print(f"Logged: {title}")


def cli():
    import argparse
    parser = argparse.ArgumentParser(description="Log an agent action to AGENT_LOG.md")
    parser.add_argument("--title", required=True)
    parser.add_argument("--project", default="")
    parser.add_argument("--task", default="")
    parser.add_argument("--integration", default="")
    parser.add_argument("--why", default="")
    parser.add_argument("--what", default="")
    parser.add_argument("--how", default="")
    parser.add_argument("--files", default="")
    parser.add_argument("--outcome", default="pending")
    parser.add_argument("--next", default="")
    parser.add_argument("--log-file", default="AGENT_LOG.md")
    args = parser.parse_args()

    logger = AgentLogger(args.log_file)
    logger.log_action(
        title=args.title,
        project=args.project,
        task=args.task,
        integration=args.integration,
        why=args.why,
        what=args.what,
        how=args.how,
        files=args.files,
        outcome=args.outcome,
        next_action=args.next,
    )


if __name__ == "__main__":
    cli()
