#!/usr/bin/env python3
"""Consolidation manager that executes consolidation opportunities."""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class ConsolidationManager:
    def __init__(self, workspace_root: str = "."):
        self.root = Path(workspace_root).resolve()
        self.report_file = self.root / "data" / "latest_review_report.json"
    
    def load_consolidation_report(self) -> Dict:
        """Load the latest consolidation report."""
        if not self.report_file.exists():
            return {}
        
        with open(self.report_file) as f:
            return json.load(f)
    
    def execute_proposal_batching(self, batch_info: Dict) -> str:
        """Create a batch review session for related proposals."""
        theme = batch_info.get("theme", "general")
        files = batch_info.get("files", [])
        
        # Create batch review document
        batch_doc = f"docs/batch_reviews/batch-{theme}-{datetime.now().strftime('%Y%m%d')}.md"
        batch_path = Path(batch_doc)
        batch_path.parent.mkdir(exist_ok=True)
        
        content = f"""# Batch Review: {theme.title()} Proposals

**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Theme**: {theme.title()}
**Proposals**: {len(files)}

## Proposals in This Batch

"""
        
        for i, filepath in enumerate(files, 1):
            proposal_id = self._extract_proposal_id(filepath)
            content += f"{i}. **{proposal_id}** - [{Path(filepath).name}]({filepath})\n"
        
        content += f"""

## Batch Review Process

1. **Individual Review** (30 min each)
   - Read each proposal thoroughly
   - Note dependencies and conflicts
   - Assess implementation complexity

2. **Cross-Proposal Analysis** (15 min)
   - Identify overlapping requirements
   - Find potential conflicts
   - Spot consolidation opportunities

3. **Prioritization** (10 min)
   - Rank by impact and effort
   - Identify quick wins
   - Plan implementation sequence

4. **Decision & Next Steps** (15 min)
   - Approve/reject/modify proposals
   - Assign implementation owners
   - Set timeline and milestones

## Review Notes

*Add your review notes here...*

## Decisions

*Record final decisions here...*

## Action Items

*List next steps and assignments...*
"""
        
        batch_path.write_text(content)
        return str(batch_path)
    
    def execute_workflow_consolidation(self, workflow_info: Dict) -> str:
        """Consolidate related workflow files."""
        files = workflow_info.get("files", [])
        
        # Create consolidated workflow
        consolidated_path = ".github/workflows/consolidated-ci.yml"
        
        content = f"""# Consolidated CI Workflow
# Generated: {datetime.now().isoformat()}
# Consolidates: {', '.join([Path(f).name for f in files])}

name: Consolidated CI
on: [push, pull_request]

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      packages: ${{{{ steps.changes.outputs.packages }}}}
    steps:
      - uses: actions/checkout@v3
      - name: Detect changes
        id: changes
        run: python3 scripts/detect_changes.py

  test-matrix:
    needs: detect-changes
    runs-on: ubuntu-latest
    strategy:
      matrix:
        package: ${{{{ fromJson(needs.detect-changes.outputs.packages) }}}}
    steps:
      - uses: actions/checkout@v3
      - name: Test package
        run: make test-package PKG=${{{{ matrix.package }}}}

  quality-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run quality checks
        run: |
          make lint
          make security-scan
          make type-check
"""
        
        Path(consolidated_path).write_text(content)
        
        # Create backup of original files
        backup_dir = Path(".github/workflows/backup")
        backup_dir.mkdir(exist_ok=True)
        
        for filepath in files:
            if Path(filepath).exists():
                shutil.copy2(filepath, backup_dir / Path(filepath).name)
        
        return consolidated_path
    
    def execute_script_merging(self, script_info: Dict) -> str:
        """Merge similar scripts into a unified tool."""
        files = script_info.get("files", [])
        
        # Create unified script
        unified_path = "scripts/unified_workflow_tools.py"
        
        content = f'''#!/usr/bin/env python3
"""Unified workflow tools - consolidated from multiple scripts.

Generated: {datetime.now().isoformat()}
Consolidates: {', '.join([Path(f).name for f in files])}
"""

import argparse
import sys
from pathlib import Path


class UnifiedWorkflowTools:
    """Consolidated workflow automation tools."""
    
    def __init__(self):
        self.tools = {{
            'detect-changes': self.detect_changes,
            'analyze-review': self.analyze_review,
            'manage-proposals': self.manage_proposals
        }}
    
    def detect_changes(self, args):
        """Detect package changes (from detect_changes.py)."""
        # Import and execute detect_changes functionality
        from detect_changes import main as detect_main
        return detect_main()
    
    def analyze_review(self, args):
        """Analyze review files (from review_analyzer.py)."""
        from review_analyzer import main as review_main
        return review_main()
    
    def manage_proposals(self, args):
        """Manage proposal lifecycle."""
        print("Proposal management functionality")
        return 0
    
    def run(self, tool_name, args):
        """Run specified tool."""
        if tool_name not in self.tools:
            print(f"Unknown tool: {{tool_name}}")
            print(f"Available tools: {{', '.join(self.tools.keys())}}")
            return 1
        
        return self.tools[tool_name](args)


def main():
    parser = argparse.ArgumentParser(description="Unified workflow tools")
    parser.add_argument("tool", choices=["detect-changes", "analyze-review", "manage-proposals"])
    parser.add_argument("--help-tool", help="Show help for specific tool")
    
    args, remaining = parser.parse_known_args()
    
    tools = UnifiedWorkflowTools()
    return tools.run(args.tool, remaining)


if __name__ == "__main__":
    sys.exit(main())
'''
        
        Path(unified_path).write_text(content)
        return unified_path
    
    def _extract_proposal_id(self, filepath: str) -> str:
        """Extract proposal ID from filepath."""
        filename = Path(filepath).name
        if filename.startswith(('WORKFLOW-', 'FIX-', 'SEC-')):
            return filename.split('-')[0] + '-' + filename.split('-')[1]
        return filename.replace('.md', '')
    
    def execute_consolidations(self) -> Dict[str, List[str]]:
        """Execute all available consolidation opportunities."""
        report = self.load_consolidation_report()
        consolidations = report.get("consolidation_opportunities", {})
        results = {"created": [], "errors": []}
        
        try:
            # Execute proposal batching
            for batch in consolidations.get("proposal_batching", []):
                batch_file = self.execute_proposal_batching(batch)
                results["created"].append(f"Batch review: {batch_file}")
            
            # Execute workflow consolidation
            for workflow in consolidations.get("workflow_consolidation", []):
                workflow_file = self.execute_workflow_consolidation(workflow)
                results["created"].append(f"Consolidated workflow: {workflow_file}")
            
            # Execute script merging
            for script_group in consolidations.get("script_merging", []):
                unified_script = self.execute_script_merging(script_group)
                results["created"].append(f"Unified script: {unified_script}")
            
        except Exception as e:
            results["errors"].append(f"Error during consolidation: {str(e)}")
        
        return results


def main():
    manager = ConsolidationManager()
    results = manager.execute_consolidations()
    
    print("🔄 Consolidation Execution Results")
    
    if results["created"]:
        print(f"\n✅ Created ({len(results['created'])}):")
        for item in results["created"]:
            print(f"  • {item}")
    
    if results["errors"]:
        print(f"\n❌ Errors ({len(results['errors'])}):")
        for error in results["errors"]:
            print(f"  • {error}")
    
    if not results["created"] and not results["errors"]:
        print("\n📝 No consolidation opportunities found in latest report")
        print("Run 'make review-analyze' first to identify opportunities")


if __name__ == "__main__":
    main()
