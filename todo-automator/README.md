# Git Todo Monitor - Automated Code Analysis & Todo Tracking

A local automation system that monitors your git repository, analyzes code changes, extracts todos, and sends AI-generated summaries as Ubuntu desktop notifications. Choose between hourly scheduling or commit-triggered monitoring.

## Features

### Core Monitoring
- ⚡ **Flexible Triggering**: Run hourly via cron OR automatically on every git commit
- 🚀 **Bash Entry Point**: Simple `./monitor` command for easy execution
- 📊 **Git Analysis**: Tracks commits, file changes, and diffs from configurable time windows
- 📝 **Todo Extraction**: Scans code files for TODO, FIXME, HACK, XXX, and NOTE comments
- 🤖 **AI Summarization**: Uses OpenAI to generate concise, actionable summaries
- 🔔 **Desktop Notifications**: Sends summaries directly to Ubuntu desktop notifications
- 📋 **Logging**: Maintains a log file of all summaries for historical reference
- 🎯 **Performance Optimized**: Configurable file scan limits for large repositories

### GitHub Integration (v2.0+)
- 🐙 **GitHub Issues Export**: Export TODOs as GitHub issues in JSON format
- 📋 **Task Management**: Priority-based task tracking with status workflows
- 🗺️ **Roadmap Planning**: Milestone tracking with progress visualization and Gantt chart export
- 🔄 **PR Analysis**: Analyze and review pull requests (planned feature)

### Package Installation
- 📦 **Pip Installation**: Install via pip for system-wide access
- 🛠️ **CLI Tool**: Access via `git-todo-monitor` command after installation

## Prerequisites

- Ubuntu LTS (or any Linux with notify-send)
- Python 3.11+
- Git repository
- OpenAI API key
- `jq` (optional, for automatic config updates during commit hook installation)

## Installation

### Option A: Pip Installation (Recommended)

1. **Install system dependencies**:
```bash
sudo apt-get update
sudo apt-get install libnotify-bin python3-pip
```

2. **Install the package**:
```bash
pip install git-todo-monitor
```

3. **Set up your OpenAI API key**:
```bash
echo "OPENAI_API_KEY=your-api-key-here" > ~/.env
```

4. **Configure repository settings**:
Create `config.json` in your project directory (see Configuration section below)

### Option B: Manual Installation

1. **Install system dependencies** (if not already installed):
```bash
sudo apt-get update
sudo apt-get install libnotify-bin python3-pip jq  # jq is optional but recommended
```

2. **Clone or download this project**

3. **Install Python dependencies**:
```bash
pip install gitpython openai python-dotenv
```

## Configuration

1. **Set up your OpenAI API key**:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

2. **Configure repository settings** (optional):
Edit `config.json` to customize:
```json
{
  "repo_path": "/path/to/your/git/repository",
  "time_window_hours": 1,
  "log_file": "todo_monitor.log",
  "notification_timeout": 10000,
  "max_files_to_scan": 500
}
```

Configuration options:
- `repo_path`: Path to your git repository (default: current directory)
- `time_window_hours`: How many hours back to check for commits (default: 1)
- `log_file`: Where to save summary logs (default: "todo_monitor.log")
- `notification_timeout`: Desktop notification display time in milliseconds (default: 10000)
- `max_files_to_scan`: Maximum number of files to scan for TODOs, prevents slowdowns on large repos (default: 500)

## Usage

### Quick Start - Run Once
```bash
./monitor              # Run with full output
./monitor --quiet      # Run silently (notifications only)
```

### Automation Options

#### Option A: Hourly Cron Job (Automatic Setup)
Run the setup script for hourly monitoring:
```bash
./setup_cron.sh
```

This will:
- Configure your repository path
- Set up your OpenAI API key
- Install the hourly cron job
- Run a test notification

#### Option B: Git Commit Hook (Trigger on Every Commit)
Install post-commit hook for automatic monitoring:
```bash
./install_commit_hook.sh
```

This will:
- Install a git post-commit hook
- Monitor runs automatically after each commit
- Works silently in the background

#### Option C: Manual Cron Setup
Add to your crontab manually:
```bash
crontab -e
```

Add this line (adjust paths):
```
0 * * * * cd /path/to/git-todo-monitor && ./monitor --quiet >> cron.log 2>&1
```

### Command Line Options

```bash
# If installed via pip:
git-todo-monitor --help
git-todo-monitor --quiet                    # Suppress console output
git-todo-monitor --config custom.json       # Use custom config
git-todo-monitor --export-issues            # Export TODOs as GitHub issues JSON
git-todo-monitor --run-tasks                # Run task manager
git-todo-monitor --run-roadmap              # Run roadmap planner

# If running from source:
python3 src/git_todo_monitor.py --help
./monitor --quiet                           # Bash wrapper
```

### GitHub Integration Commands

**Export TODOs as GitHub Issues** (no OpenAI API key required):
```bash
git-todo-monitor --export-issues
# Outputs: github_issues.json
```

**Run Task Manager**:
```bash
git-todo-monitor --run-tasks
# Outputs: TASKS.md with priority-based task tracking
```

**Generate Roadmap Plan**:
```bash
git-todo-monitor --run-roadmap
# Outputs: ROADMAP_PLAN.md and gantt_data.json
```

## How It Works

1. **Git Analysis**: The script analyzes commits from the last hour using GitPython
2. **Todo Extraction**: Scans Python, JavaScript, Markdown, Shell, TypeScript, and JSON files for todo comments
3. **AI Summarization**: Sends the changes and todos to OpenAI for intelligent summarization
4. **Desktop Notification**: Displays the summary using Ubuntu's notify-send
5. **Logging**: Appends the summary to a log file with timestamp

## File Structure

```
.
├── src/
│   ├── git_todo_monitor.py      # Main automation script
│   ├── github_integration.py    # GitHub issues export
│   ├── task_manager.py          # Task management system
│   ├── roadmap_planner.py       # Roadmap planning tool
│   └── test_monitor.py          # Setup validation script
├── .github/
│   ├── workflows/
│   │   ├── ci.yml               # CI/CD testing workflow
│   │   └── release.yml          # Automated releases
│   ├── ISSUE_TEMPLATE/          # GitHub issue templates
│   └── PULL_REQUEST_TEMPLATE.md # PR template
├── monitor                      # Bash entry point for easy execution
├── setup_cron.sh                # Automated cron setup script
├── install_commit_hook.sh       # Git commit hook installer
├── setup.py                     # Package installation config
├── config.json                  # Configuration file
├── .env                         # OpenAI API key (create from .env.example)
├── .env.example                 # Template for environment variables
├── README.md                    # This file
├── CONTRIBUTING.md              # Contribution guidelines
├── LICENSE                      # MIT License
├── PUBLISH.md                   # GitHub publishing guide
├── CHANGELOG.md                 # Version history and changes
├── ROADMAP.md                   # Future features and roadmap
├── todo_monitor.log             # Summary log (created automatically)
└── cron.log                     # Cron execution log (created automatically)
```

## Logs

- **todo_monitor.log**: Contains all AI-generated summaries with timestamps
- **cron.log**: Contains cron execution output and errors

## Customization

### Change Check Frequency
Edit the cron schedule (default is hourly at :00):
- Every 2 hours: `0 */2 * * *`
- Every 30 minutes: `*/30 * * * *`
- Daily at 9 AM: `0 9 * * *`

### Modify Todo Patterns
Edit `git_todo_monitor.py` and update the `todo_patterns` list:
```python
todo_patterns = ["TODO", "FIXME", "HACK", "XXX", "NOTE", "BUG"]
```

### Adjust AI Model
Change the OpenAI model in `git_todo_monitor.py`:
```python
model="gpt-4o-mini"  # or "gpt-4", "gpt-3.5-turbo", etc.
```

## Troubleshooting

### No notifications appearing
- Ensure `libnotify-bin` is installed: `sudo apt-get install libnotify-bin`
- Test notify-send: `notify-send "Test" "This is a test"`
- Check if you're logged into a graphical session

### Cron job not running
- Verify cron is installed: `sudo systemctl status cron`
- Check crontab: `crontab -l`
- Review cron.log for errors

### OpenAI API errors
- Verify your API key in `.env`
- Check your OpenAI account has available credits
- Review error messages in cron.log

### Git repository not found
- Ensure the `repo_path` in config.json points to a valid git repository
- Check that the repository has at least one commit

## Uninstallation

### Remove Cron Job
```bash
crontab -e
# Delete the line containing git-todo-monitor
```

### Remove Commit Hook
```bash
rm /path/to/your/repo/.git/hooks/post-commit
```

## What's New in v2.0.0

- 🐙 **GitHub Integration**: Export TODOs as GitHub issues in JSON format
- 📋 **Task Management**: Priority-based task tracking with status workflows  
- 🗺️ **Roadmap Planning**: Milestone tracking with Gantt chart export
- 📦 **Pip Installation**: Install via pip for system-wide access
- 🛠️ **CLI Enhancement**: New commands for tasks, roadmap, and issue export
- 📚 **Publishing Ready**: Complete GitHub repository setup with CI/CD workflows
- 📖 **Documentation**: CONTRIBUTING.md, LICENSE, GitHub templates, and publishing guide

See [CHANGELOG.md](CHANGELOG.md) for full version history.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code of conduct
- Development setup
- Coding standards
- Pull request process
- Issue reporting guidelines

## Next Steps & Roadmap

Want to see what's coming next? Check out our [ROADMAP.md](ROADMAP.md) for:
- Multi-repository support
- Email/Slack/Discord notifications
- Web dashboard for history
- Custom todo patterns
- And much more!

Contributions welcome! See planned features in the roadmap.

## License

MIT License - Feel free to modify and distribute
