## Contributing to Git Todo Monitor

First off, thank you for considering contributing to Git Todo Monitor! It's people like you that make this tool better for everyone.

### Code of Conduct

This project and everyone participating in it is governed by our commitment to creating a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

### How Can I Contribute?

#### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples** to demonstrate the steps
* **Describe the behavior you observed** and what you expected to see
* **Include screenshots** if applicable
* **Include your environment details** (OS, Python version, etc.)

**Bug Report Template:**
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. See error

**Expected behavior**
What you expected to happen.

**Environment:**
 - OS: [e.g. Ubuntu 22.04]
 - Python Version: [e.g. 3.11]
 - Git Todo Monitor Version: [e.g. 1.0.0]

**Additional context**
Any other context about the problem.
```

#### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a detailed description** of the suggested enhancement
* **Provide specific examples** of how the enhancement would be used
* **Explain why this enhancement would be useful** to most users

#### Pull Requests

* Fill in the required template
* Follow the Python style guidelines (PEP 8)
* Include appropriate test cases
* Update documentation as needed
* End all files with a newline

### Development Setup

1. **Fork and clone the repository**
```bash
git clone https://github.com/yourusername/git-todo-monitor.git
cd git-todo-monitor
```

2. **Install dependencies**
```bash
pip install gitpython openai python-dotenv
```

3. **Create a branch for your changes**
```bash
git checkout -b feature/your-feature-name
```

4. **Make your changes and test**
```bash
./test_cli.sh
python3 src/test_monitor.py
```

5. **Commit your changes**
```bash
git add .
git commit -m "Add: Brief description of your changes"
```

6. **Push to your fork**
```bash
git push origin feature/your-feature-name
```

7. **Open a Pull Request**

### Commit Message Guidelines

We follow a simple commit message convention:

* **Add:** New feature or functionality
* **Fix:** Bug fix
* **Update:** Changes to existing features
* **Docs:** Documentation changes
* **Test:** Adding or updating tests
* **Refactor:** Code refactoring without feature changes
* **Chore:** Maintenance tasks, dependency updates

Examples:
```
Add: GitHub issue sync functionality
Fix: Memory leak in todo extraction
Update: Improve AI summarization prompts
Docs: Add installation guide for macOS
```

### Style Guidelines

#### Python Style Guide

* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
* Use 4 spaces for indentation (no tabs)
* Maximum line length: 100 characters
* Use meaningful variable and function names
* Add docstrings to all functions and classes
* Add type hints where appropriate

Example:
```python
def extract_todos_from_files(self, file_patterns: List[str]) -> List[Dict]:
    """
    Extract TODO comments from specified file patterns.
    
    Args:
        file_patterns: List of glob patterns to scan
        
    Returns:
        List of dictionaries containing todo information
    """
    # Implementation here
    pass
```

#### Bash Script Style

* Use `#!/bin/bash` shebang
* Quote all variables: `"${VARIABLE}"`
* Use meaningful variable names in CAPS
* Add comments for complex logic
* Check for errors and provide helpful messages

### Testing

* Add tests for new features
* Ensure all existing tests pass
* Test on multiple Python versions if possible (3.9, 3.10, 3.11)
* Test on both Ubuntu and macOS if possible

### Documentation

* Update README.md if adding features
* Update CHANGELOG.md with your changes
* Add inline comments for complex code
* Update docstrings as needed

### Project Structure

```
git-todo-monitor/
├── src/                    # Source code
│   ├── git_todo_monitor.py # Main monitor
│   ├── github_integration.py
│   ├── task_manager.py
│   └── roadmap_planner.py
├── .github/               # GitHub specific files
│   ├── workflows/         # CI/CD workflows
│   └── ISSUE_TEMPLATE/    # Issue templates
├── docs/                  # Documentation
├── monitor                # Bash entry point
├── setup_cron.sh         # Cron setup script
├── install_commit_hook.sh # Git hook installer
└── README.md             # Main documentation
```

### Getting Help

* Check the [README.md](README.md) for documentation
* Look through existing [issues](https://github.com/yourusername/git-todo-monitor/issues)
* Ask questions by opening a new issue with the "question" label

### Recognition

Contributors will be:
* Listed in the project README
* Mentioned in release notes
* Forever appreciated! 🙏

Thank you for contributing! 🎉
