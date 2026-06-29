#!/usr/bin/env python3
"""
DevFlow Workflow Self-Improvement Automation

Automates proposal lifecycle management, dashboard sync, and workflow health monitoring.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class WorkflowAutomation:
    def __init__(self, workspace_root: str = "/media/sunil-kr/workspace/projects/project"):
        self.root = Path(workspace_root)
        self.docs_dir = self.root / "docs"
        self.improvements_dir = self.docs_dir / "improvements"
        self.dashboard_file = self.docs_dir / "IMPROVEMENTS.md"
        self.history_file = self.docs_dir / "history.json"

    def sync_dashboard(self) -> Dict[str, int]:
        """Sync dashboard with actual proposal files."""
        proposals = self._scan_proposals()
        self._update_dashboard(proposals)
        return {"synced": len(proposals["active"]), "deprecated": len(proposals["deprecated"])}

    def archive_proposal(self, proposal_id: str) -> bool:
        """Archive a completed proposal."""
        proposal_file = self._find_proposal_file(proposal_id)
        if not proposal_file:
            return False
        
        proposal_data = self._parse_proposal(proposal_file)
        if not proposal_data:
            return False

        # Add to history
        self._add_to_history(proposal_data)
        
        # Rename to deprecated
        deprecated_name = proposal_file.stem + ".deprecated.md"
        deprecated_path = proposal_file.parent / deprecated_name
        proposal_file.rename(deprecated_path)
        
        # Update dashboard
        self.sync_dashboard()
        return True

    def health_check(self) -> Dict[str, any]:
        """Check workflow health and identify issues."""
        issues = []
        stats = {}
        
        # Check dashboard consistency
        proposals = self._scan_proposals()
        dashboard_entries = self._parse_dashboard()
        
        # Find mismatches
        active_ids = {p["id"] for p in proposals["active"]}
        dashboard_ids = {entry["id"] for entry in dashboard_entries["active"]}
        
        if active_ids != dashboard_ids:
            issues.append("Dashboard out of sync with proposal files")
        
        # Check for orphaned files
        orphaned = active_ids - dashboard_ids
        if orphaned:
            issues.append(f"Orphaned proposals: {orphaned}")
        
        # Check history consistency
        history = self._load_history()
        deprecated_ids = {p["id"] for p in proposals["deprecated"]}
        history_ids = {entry["id"] for entry in history}
        
        missing_history = deprecated_ids - history_ids
        if missing_history:
            issues.append(f"Deprecated proposals missing from history: {missing_history}")
        
        stats = {
            "active_proposals": len(active_ids),
            "deprecated_proposals": len(deprecated_ids),
            "history_entries": len(history_ids),
            "issues_found": len(issues)
        }
        
        return {"issues": issues, "stats": stats}

    def auto_improve(self) -> Dict[str, any]:
        """Run self-improvement automation."""
        results = {}
        
        # Sync dashboard
        results["sync"] = self.sync_dashboard()
        
        # Health check
        results["health"] = self.health_check()
        
        # Auto-fix common issues
        fixes = []
        if "Dashboard out of sync" in str(results["health"]["issues"]):
            self.sync_dashboard()
            fixes.append("Fixed dashboard sync")
        
        results["fixes"] = fixes
        results["timestamp"] = datetime.now().isoformat()
        
        return results

    def _scan_proposals(self) -> Dict[str, List[Dict]]:
        """Scan improvements directory for proposal files."""
        active = []
        deprecated = []
        
        for file_path in self.improvements_dir.glob("*.md"):
            if file_path.name == "TEMPLATE.md":
                continue
                
            proposal_data = self._parse_proposal(file_path)
            if not proposal_data:
                continue
                
            if file_path.name.endswith(".deprecated.md"):
                deprecated.append(proposal_data)
            else:
                active.append(proposal_data)
        
        return {"active": active, "deprecated": deprecated}

    def _parse_proposal(self, file_path: Path) -> Optional[Dict]:
        """Parse proposal file metadata."""
        try:
            content = file_path.read_text()
            
            # Extract metadata
            id_match = re.search(r"- \*\*ID\*\*: (.+)", content)
            title_match = re.search(r"# Improvement Proposal: (.+)", content)
            category_match = re.search(r"- \*\*Category\*\*: (.+)", content)
            status_match = re.search(r"- \*\*Status\*\*: (.+)", content)
            priority_match = re.search(r"- \*\*Priority\*\*: (.+)", content)
            author_match = re.search(r"- \*\*Author\*\*: (.+)", content)
            
            if not (id_match and title_match):
                return None
                
            return {
                "id": id_match.group(1).strip(),
                "title": title_match.group(1).strip(),
                "category": category_match.group(1).strip() if category_match else "Unknown",
                "status": status_match.group(1).strip() if status_match else "Unknown",
                "priority": priority_match.group(1).strip() if priority_match else "Medium",
                "author": author_match.group(1).strip() if author_match else "Unknown",
                "file_path": file_path
            }
        except Exception:
            return None

    def _update_dashboard(self, proposals: Dict[str, List[Dict]]):
        """Update the dashboard file."""
        lines = [
            "# DevFlow Improvement Proposals",
            "",
            "This document tracks all proposed, ongoing, and completed improvements for the DevFlow workspace.",
            "",
            "| ID | Title | Category | Priority | Status | Link |",
            "|---|---|---|---|---|---|"
        ]
        
        # Add active proposals
        for proposal in sorted(proposals["active"], key=lambda x: x["id"]):
            link = f"[{proposal['file_path'].name}](./improvements/{proposal['file_path'].name})"
            lines.append(f"| {proposal['id']} | {proposal['title']} | {proposal['category']} | {proposal['priority']} | {proposal['status']} | {link} |")
        
        lines.extend([
            "",
            "## Completed Proposals",
            "",
            "See [history.json](./history.json) for archived completed proposals.",
            ""
        ])
        
        # Add deprecated proposals if any
        if proposals["deprecated"]:
            lines.extend([
                "## Deprecated Proposals",
                "",
                "| ID | Title | Status | Link |",
                "|---|---|---|---|"
            ])
            
            for proposal in sorted(proposals["deprecated"], key=lambda x: x["id"]):
                link = f"[{proposal['file_path'].name}](./improvements/{proposal['file_path'].name})"
                lines.append(f"| {proposal['id']} | {proposal['title']} | Deprecated | {link} |")
        
        self.dashboard_file.write_text("\n".join(lines))

    def _parse_dashboard(self) -> Dict[str, List[Dict]]:
        """Parse current dashboard entries."""
        if not self.dashboard_file.exists():
            return {"active": [], "deprecated": []}
        
        content = self.dashboard_file.read_text()
        active = []
        deprecated = []
        
        # Parse active proposals table
        in_active_table = False
        in_deprecated_table = False
        
        for line in content.split("\n"):
            if line.startswith("| ID | Title"):
                in_active_table = True
                continue
            elif line.startswith("## Deprecated Proposals"):
                in_active_table = False
                continue
            elif "| ID | Title | Status |" in line:
                in_deprecated_table = True
                continue
            elif line.startswith("#") and in_deprecated_table:
                in_deprecated_table = False
                
            if in_active_table and line.startswith("|") and not line.startswith("|-"):
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 5:
                    active.append({"id": parts[0], "title": parts[1]})
            elif in_deprecated_table and line.startswith("|") and not line.startswith("|-"):
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 3:
                    deprecated.append({"id": parts[0], "title": parts[1]})
        
        return {"active": active, "deprecated": deprecated}

    def _find_proposal_file(self, proposal_id: str) -> Optional[Path]:
        """Find proposal file by ID."""
        for file_path in self.improvements_dir.glob(f"{proposal_id}-*.md"):
            if not file_path.name.endswith(".deprecated.md"):
                return file_path
        return None

    def _load_history(self) -> List[Dict]:
        """Load history.json."""
        if not self.history_file.exists():
            return []
        try:
            return json.loads(self.history_file.read_text())
        except Exception:
            return []

    def _add_to_history(self, proposal_data: Dict):
        """Add proposal to history.json."""
        history = self._load_history()
        
        entry = {
            "id": proposal_data["id"],
            "title": proposal_data["title"],
            "category": proposal_data["category"],
            "author": proposal_data["author"],
            "reviewers": [],  # Would need to parse from proposal content
            "completion_date": datetime.now().strftime("%Y-%m-%d"),
            "summary": f"Automated archival of {proposal_data['title']}"
        }
        
        history.append(entry)
        self.history_file.write_text(json.dumps(history, indent=2))

def main():
    import sys
    
    automation = WorkflowAutomation()
    
    if len(sys.argv) < 2:
        print("Usage: workflow_automation.py <command>")
        print("Commands: sync, archive <id>, health, auto-improve")
        return
    
    command = sys.argv[1]
    
    if command == "sync":
        result = automation.sync_dashboard()
        print(f"Dashboard synced: {result['synced']} active, {result['deprecated']} deprecated")
    
    elif command == "archive" and len(sys.argv) > 2:
        proposal_id = sys.argv[2]
        if automation.archive_proposal(proposal_id):
            print(f"Proposal {proposal_id} archived successfully")
        else:
            print(f"Failed to archive proposal {proposal_id}")
    
    elif command == "health":
        result = automation.health_check()
        print(f"Health check: {result['stats']['issues_found']} issues found")
        for issue in result["issues"]:
            print(f"  - {issue}")
        print(f"Stats: {result['stats']}")
    
    elif command == "auto-improve":
        result = automation.auto_improve()
        print(f"Auto-improvement completed:")
        print(f"  Synced: {result['sync']}")
        print(f"  Issues: {result['health']['stats']['issues_found']}")
        print(f"  Fixes applied: {len(result['fixes'])}")
        for fix in result["fixes"]:
            print(f"    - {fix}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
