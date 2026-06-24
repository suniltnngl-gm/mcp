#!/usr/bin/env python3

import os
import subprocess
import json
from typing import List, Dict, Optional
from datetime import datetime
import re

class GitHubIntegration:
    def __init__(self, config_path="config.json"):
        self.config = self.load_config(config_path)
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_repo = self.config.get("github_repo", "")

    def load_config(self, config_path):
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}

    def _gh(self, *args: str) -> subprocess.CompletedProcess:
        """Run a gh CLI command and return the result."""
        cmd = ["gh", *args]
        env = os.environ.copy()
        if self.github_token:
            env["GH_TOKEN"] = self.github_token
        if self.github_repo:
            env["GH_REPO"] = self.github_repo
        return subprocess.run(cmd, capture_output=True, text=True, env=env)

    def parse_todo_to_issue(self, todo: Dict) -> Dict:
        content = todo['content']
        file_path = todo['file']
        line_num = todo['line']

        priority = "low"
        if "FIXME" in content or "BUG" in content:
            priority = "high"
        elif "HACK" in content:
            priority = "medium"

        labels = []
        if "TODO" in content:
            labels.append("enhancement")
        if "FIXME" in content or "BUG" in content:
            labels.append("bug")
        if "HACK" in content:
            labels.append("tech-debt")

        issue_title = content.replace("TODO:", "").replace("FIXME:", "").replace("HACK:", "")
        issue_title = issue_title.replace("XXX:", "").replace("NOTE:", "").strip()

        if len(issue_title) > 80:
            issue_title = issue_title[:77] + "..."

        issue_body = f"""**Source:** `{file_path}:{line_num}`

```
{content}
```

**Priority:** {priority}

---
*Auto-generated from code comment*
"""

        return {
            "title": issue_title,
            "body": issue_body,
            "labels": labels,
            "priority": priority,
            "source_file": file_path,
            "source_line": line_num
        }

    def create_issue_from_todo(self, todo: Dict) -> Optional[Dict]:
        if not self.github_repo:
            print("GitHub repo not configured. Set github_repo in config.json")
            return None

        issue_data = self.parse_todo_to_issue(todo)
        labels_arg = ",".join(issue_data["labels"])
        title = issue_data["title"]
        body = issue_data["body"]

        result = self._gh(
            "issue", "create",
            "--repo", self.github_repo,
            "--title", title,
            "--body", body,
            "--label", labels_arg,
        )

        if result.returncode == 0:
            url = result.stdout.strip()
            issue_data["url"] = url
            print(f"  ✓ Created issue: {url}")
        else:
            print(f"  ✗ Failed to create issue '{title}': {result.stderr.strip()}")
            issue_data["error"] = result.stderr.strip()

        return issue_data

    def sync_todos_to_issues(self, todos: List[Dict]) -> List[Dict]:
        issues = []
        for todo in todos:
            issue = self.create_issue_from_todo(todo)
            if issue:
                issues.append(issue)
        return issues

    def analyze_pr_diff(self, pr_number: int) -> Dict:
        if not self.github_repo:
            print("GitHub repo not configured")
            return {}

        result = self._gh("pr", "view", str(pr_number), "--json", "title,body,files,additions,deletions")
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {
            "pr_number": pr_number,
            "analysis": "PR analysis requires gh CLI and valid repo",
            "suggestions": []
        }

    def export_issues_json(self, todos: List[Dict], output_file: str = "github_issues.json"):
        issues = []
        for todo in todos:
            issue_data = self.parse_todo_to_issue(todo)
            issues.append({
                "title": issue_data["title"],
                "body": issue_data["body"],
                "labels": issue_data["labels"]
            })

        with open(output_file, 'w') as f:
            json.dump(issues, f, indent=2)

        print(f"✓ Exported {len(issues)} issues to {output_file}")
        if self.github_repo and self._gh("--version").returncode == 0:
            print(f"  Run: ./monitor --sync-issues to create them on GitHub")

        return issues

if __name__ == "__main__":
    gh = GitHubIntegration()

    example_todos = [
        {"file": "app.py", "line": 42, "content": "TODO: Add input validation"},
        {"file": "utils.py", "line": 15, "content": "FIXME: Memory leak in cache"},
        {"file": "api.py", "line": 88, "content": "HACK: Temporary workaround for auth"}
    ]

    print("GitHub Issue Generation Example:")
    print("=" * 60)
    gh.export_issues_json(example_todos)
