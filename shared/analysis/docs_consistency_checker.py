#!/usr/bin/env python3
"""Documentation Consistency Checker - Ensure no duplication, maintain consistency"""
import re
from pathlib import Path


class DocsConsistencyChecker:
    def __init__(self):
        self.root = Path(".")
        self.docs = {
            "README.md": "",
            "docs/USER_GUIDE.md": "",
            "docs/API_REFERENCE.md": "",
        }

    def load_docs(self):
        """Load all documentation content"""
        for doc_path in self.docs.keys():
            file_path = self.root / doc_path
            if file_path.exists():
                with open(file_path) as f:
                    self.docs[doc_path] = f.read()

    def find_duplications(self):
        """Find duplicate content across documents"""
        duplicates = []

        # Check for duplicate commands/examples
        command_pattern = r"`python3 cli [^`]+`"

        all_commands = {}
        for doc_name, content in self.docs.items():
            commands = re.findall(command_pattern, content)
            for cmd in commands:
                if cmd not in all_commands:
                    all_commands[cmd] = []
                all_commands[cmd].append(doc_name)

        # Find duplicates
        for cmd, locations in all_commands.items():
            if len(locations) > 1:
                duplicates.append({"command": cmd, "locations": locations})

        return duplicates

    def ensure_consistency(self):
        """Ensure consistent information across docs"""

        # Standard command format
        commands = {
            "git_staged": "python3 cli git staged",
            "git_push": "python3 cli git pre-push",
            "logs_system": "python3 cli logs system",
            "logs_custom": "python3 cli logs <file>",
            "prevent_check": "python3 cli prevent check <purpose>",
        }

        # Update README.md - minimal quick start
        readme_content = f"""# Dev Refactor Tools

## Quick Start
```bash
{commands["git_staged"]}     # Git intelligence
{commands["logs_system"]}    # Log analysis
{commands["prevent_check"]} # Duplication prevention
```

## Structure
- `core/` - Essential intelligence tools (3 files)
- `config/` - Configuration and knowledge base
- `docs/` - Documentation (USER_GUIDE.md, API_REFERENCE.md)
- `tools/` - Development integration

## Features
- Git intelligence with learning
- AI-powered log analysis
- Code duplication prevention
- Self-improving knowledge base

See `docs/USER_GUIDE.md` for complete usage guide.
"""

        # Update USER_GUIDE.md - complete reference
        guide_content = f"""# User Guide

## All Commands

### Git Intelligence
- `{commands["git_staged"]}` - Validate staged changes
- `{commands["git_push"]}` - Pre-push validation with tests

### Log Analysis
- `{commands["logs_system"]}` - Analyze system logs with AI
- `{commands["logs_custom"]}` - Analyze custom log file

### Duplication Prevention
- `{commands["prevent_check"]}` - Check for duplicate functions
- `python3 cli prevent register <file> <function> <purpose>` - Register new function

## Configuration
- Edit `config/knowledge_base/` files to customize behavior
- Modify `config/duplication-rules` for prevention rules
- Update `tools/vscode/` for development environment

## Development Setup
1. Use VSCode with settings in `tools/vscode/`
2. Git hooks automatically installed for intelligence
3. Knowledge base learns from your patterns
"""

        # Update API_REFERENCE.md - technical details only
        api_content = """# API Reference

## Core Modules

### core/git_intelligence.py
- `analyze_staged_changes()` - Validate staged files, return issues
- `learn_from_commit()` - Learn patterns from commit history
- `get_git_patterns()` - Retrieve learned git patterns

### core/log_analyzer.py
- `analyze_logs(file_path)` - Analyze log file, return structured results
- `chunk_logs(text, size=1500)` - Split logs into manageable chunks
- `analyze_with_llm(chunks)` - AI analysis of log chunks

### core/duplication_prevention.py
- `check_before_create(purpose)` - Check for existing similar functions
- `register_function(file, name, purpose)` - Register new function
- `detect_duplicate_logic()` - Scan codebase for duplicates

## Configuration Files
- `config/knowledge_base/real_time_metrics.json` - Learning metrics
- `config/knowledge_base/function_registry.json` - Function registry
- `config/duplication-rules` - Prevention rules
"""

        # Write consistent docs
        with open(self.root / "README.md", "w") as f:
            f.write(readme_content)

        with open(self.root / "docs" / "USER_GUIDE.md", "w") as f:
            f.write(guide_content)

        with open(self.root / "docs" / "API_REFERENCE.md", "w") as f:
            f.write(api_content)

        return commands

    def run_consistency_check(self):
        """Execute consistency check and fixes"""
        print("📋 Checking documentation consistency...")

        # Load current docs
        self.load_docs()

        # Find duplications
        duplicates = self.find_duplications()
        print(f"🔍 Found {len(duplicates)} potential duplications")

        # Ensure consistency
        commands = self.ensure_consistency()
        print("✅ Updated all docs with consistent information")

        print("📚 Documentation hierarchy:")
        print("  README.md - Quick start (3 commands)")
        print("  USER_GUIDE.md - Complete reference (6 commands)")
        print("  API_REFERENCE.md - Technical details (9 functions)")

        return {
            "duplicates_found": len(duplicates),
            "commands_standardized": len(commands),
            "docs_updated": 3,
        }


if __name__ == "__main__":
    checker = DocsConsistencyChecker()
    checker.run_consistency_check()
