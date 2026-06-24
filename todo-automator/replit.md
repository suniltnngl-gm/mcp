# Git Todo Monitor - Automated Hourly Summaries with GitHub Integration

## Overview

Git Todo Monitor is a local automation system that continuously monitors a git repository, analyzing code changes and extracting developer todos. The system runs hourly checks to track commits, scan for TODO/FIXME comments, generates AI-powered summaries using OpenAI, and delivers insights through Ubuntu desktop notifications. Version 2.0 adds comprehensive GitHub integration features including issue export, task management, and roadmap planning.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Application Structure

**Main Monitor Component** (`src/git_todo_monitor.py`)
- Centralized GitTodoMonitor class that orchestrates all functionality
- Loads configuration from JSON file and environment variables
- Integrates git analysis, todo extraction, AI summarization, and notification delivery
- Uses datetime-based time windows to track recent changes (default: 1 hour)
- Enhanced CLI with multiple operation modes: monitoring, issue export, task management, roadmap planning
- Main entry point function for pip console script installation

**Configuration Management**
- JSON-based configuration (`config.json`) for repository settings
- Environment variables for sensitive data (OpenAI API key via `.env` file)
- Configurable parameters: repo path, time window, log file location, notification timeout, and file scan limits
- Design rationale: Separates sensitive credentials from application settings while maintaining flexibility

**Git Analysis Pattern**
- Uses GitPython library for repository interaction
- Tracks commits within configurable time windows using datetime filtering
- Collects commit metadata: messages, changed files, and diffs
- Returns structured data (commits, files_changed set, commit_messages list)
- Chosen approach: Time-based filtering allows hourly monitoring without complex state management

**Todo Extraction System**
- Scans code files for comment patterns: TODO, FIXME, HACK, XXX, NOTE
- File scanning with configurable limits (max_files_to_scan) to prevent performance issues
- Pattern matching approach ensures compatibility across multiple programming languages
- Alternative considered: AST-based parsing (rejected due to language-specific complexity)
- Standalone extraction mode for GitHub export (works without OpenAI API key)

**AI Integration Layer**
- OpenAI API client for natural language summary generation
- Processes git changes and todos into actionable insights
- API key validation at initialization prevents runtime failures
- Design choice: Fail-fast approach for missing credentials improves user experience
- Optional for certain features (issue export works without AI)

**Notification Delivery**
- Ubuntu desktop notifications via `notify-send` command
- Subprocess-based approach for system integration
- Configurable timeout for notification display duration
- Logging mechanism maintains historical record in log files

### GitHub Integration Features (v2.0+)

**GitHub Issue Export** (`src/github_integration.py`)
- Exports TODO/FIXME comments as GitHub-ready issue JSON
- Includes file path, line number, and full context
- Priority assignment based on comment type (FIXME = high priority)
- No OpenAI API key required for this feature
- Generates github_issues.json for bulk import
- Design choice: JSON format enables automation via GitHub CLI

**Task Management System** (`src/task_manager.py`)
- Priority-based task tracking (low, medium, high, critical)
- Status workflow: todo → in_progress → done → blocked
- Automatic task generation from repository TODOs
- Export to TASKS.md with summary statistics
- Design rationale: Provides project-level task visibility without external services

**Roadmap Planning Tool** (`src/roadmap_planner.py`)
- Milestone-based planning with dates and progress tracking
- Feature tracking across milestones
- Export to ROADMAP_PLAN.md for documentation
- Gantt chart data export (gantt_data.json) for visualization tools
- Design choice: Local-first approach with optional external visualization

### Error Handling Philosophy

- Early validation of critical dependencies (API keys, git repository)
- Graceful degradation when no recent changes exist
- Clear error messages guide users toward resolution
- Test script (`src/test_monitor.py`) validates setup before execution
- Feature-specific error handling (some features work without OpenAI)

### Monitoring Strategy

**Hourly Execution Model**
- Designed for cron or systemd timer integration
- Stateless operation: each run is independent
- Time-window approach eliminates need for persistent state tracking
- Pros: Simple, reliable, easy to debug
- Cons: Requires external scheduler, may miss sub-hour changes

**Git Commit Hook Alternative**
- Post-commit hook triggers monitoring after each commit
- Installed via `install_commit_hook.sh` script
- Runs silently in background
- Pros: Immediate feedback, no scheduling needed
- Cons: Runs on every commit (may be excessive for frequent commits)

### Package Distribution

**Pip Installation Structure**
- setup.py configured with py_modules for individual module installation
- Console script entry point: git-todo-monitor → git_todo_monitor:main()
- Package sources from src/ directory via package_dir={'': 'src'}
- Includes helper scripts: monitor, setup_cron.sh, install_commit_hook.sh
- Design choice: py_modules approach for non-package module structure
- Enables system-wide CLI access after pip install

**CLI Architecture**
- Main entry point with argparse for option parsing
- Subcommands via flags: --export-issues, --run-tasks, --run-roadmap
- Quiet mode for background execution
- Custom config file support
- Design rationale: Single binary with multiple operation modes

### Project Organization

**Source Code Structure** (`src/` directory)
- Modular architecture with specialized components
- Clear separation of concerns (git ops, GitHub features, task/roadmap tools)
- Independent feature modules can run standalone
- Importable from installed package location

**GitHub Publishing Preparation**
- MIT License for open source distribution
- CONTRIBUTING.md with contribution guidelines
- Issue and PR templates for community engagement
- CI/CD workflows (GitHub Actions) for testing and releases
- PUBLISH.md guide for repository publishing steps

## External Dependencies

### Third-Party Libraries

**GitPython** - Git repository interaction
- Purpose: Read commits, diffs, and file changes programmatically
- Usage: Repository analysis and change tracking

**OpenAI Python Client** - AI-powered summarization
- Purpose: Generate natural language summaries of code changes and todos
- Requires: API key authentication via environment variable
- Usage: Text generation from structured git and todo data
- Optional: Some features (issue export) work without it

**python-dotenv** - Environment variable management
- Purpose: Load API keys and sensitive configuration from `.env` files
- Usage: Secure credential handling outside version control

### System Dependencies

**notify-send** (libnotify-bin package)
- Purpose: Display desktop notifications on Ubuntu/Linux
- Integration: Called via subprocess for system-level notifications

**Git** - Version control system
- Purpose: Underlying git operations accessed through GitPython
- Requirement: Must be installed and repository must be initialized

**jq** (optional)
- Purpose: JSON processing for commit hook configuration updates
- Usage: Automatic config.json updates during hook installation

### Configuration Files

**config.json** - Application settings
- Repository path configuration
- Time window for change detection
- Logging and notification parameters
- File scanning limits

**.env** - Sensitive credentials
- OpenAI API key storage
- Excluded from version control for security

**setup.py** - Package installation configuration
- Metadata for pip distribution
- Module list and entry points
- Dependencies and requirements

### External Services

**OpenAI API** - Language model service
- Service: GPT model access for text summarization
- Authentication: API key-based
- Network dependency: Requires internet connectivity for API calls
- Optional for certain features

**GitHub** - Repository hosting and issue tracking
- Integration via JSON export for issue creation
- CI/CD via GitHub Actions workflows
- Optional: Local tool works without GitHub account

## Command Line Interface

### Core Monitoring
- `git-todo-monitor` - Run git analysis and send notification
- `git-todo-monitor --quiet` - Run silently (notifications only)
- `git-todo-monitor --config custom.json` - Use custom configuration

### GitHub Features
- `git-todo-monitor --export-issues` - Export TODOs as GitHub issues JSON
- `git-todo-monitor --run-tasks` - Generate task management report
- `git-todo-monitor --run-roadmap` - Create roadmap plan with Gantt data

### Legacy Entry Points
- `./monitor` - Bash wrapper for backward compatibility
- `python3 src/git_todo_monitor.py` - Direct script execution
- Scripts: `setup_cron.sh`, `install_commit_hook.sh` for automation setup

## Version History

### v2.0.0 (Current)
- GitHub integration: issue export, task management, roadmap planning
- Pip package installation with console script
- Reorganized source to src/ directory
- Enhanced CLI with multiple operation modes
- Publishing preparation: LICENSE, CONTRIBUTING.md, GitHub templates, CI/CD
- Improved documentation and contribution guidelines

### v1.0.0
- Bash entry point (`./monitor`)
- Git commit hook support
- Command line arguments (--quiet, --config)
- Enhanced documentation (CHANGELOG, ROADMAP, INSTALL)

### Initial Release
- Core git monitoring and todo extraction
- OpenAI summarization
- Ubuntu desktop notifications
- Hourly cron scheduling
