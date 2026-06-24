# Changelog

All notable changes to the Git Todo Monitor project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-12

### Added
- Initial release of Git Todo Monitor
- Hourly git repository monitoring via cron scheduling
- Git commit analysis with time-window filtering
- Todo extraction from code files (TODO, FIXME, HACK, XXX, NOTE patterns)
- AI-powered summarization using OpenAI GPT-4o-mini
- Ubuntu desktop notifications via notify-send
- Configurable settings through `config.json`
- Secure API key management via `.env` file
- Automated setup script (`setup_cron.sh`)
- Test validation script (`test_monitor.py`)
- Bash entry point (`monitor`) for easier execution
- Git post-commit hook support for commit-triggered monitoring
- Performance optimization with configurable file scan limits
- Comprehensive documentation (README.md, INSTALL.md)
- Error handling and graceful degradation
- Logging system for historical summary tracking

### Security
- API keys stored in `.env` file, excluded from version control
- Early validation of credentials with clear error messages
- Secure credential handling via python-dotenv

### Configuration Options
- `repo_path`: Git repository path
- `time_window_hours`: Commit history window (default: 1 hour)
- `log_file`: Summary log location
- `notification_timeout`: Desktop notification duration (milliseconds)
- `max_files_to_scan`: File scan limit for performance (default: 500)

## [Unreleased]

### Planned Features
- Support for multiple git repositories
- Email notification option
- Slack/Discord webhook integration
- Customizable todo patterns
- Priority ranking for todos
- Summary verbosity levels
- Web dashboard for viewing history
- GitHub/GitLab API integration for remote repositories
