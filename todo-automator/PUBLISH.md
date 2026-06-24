# Publishing Git Todo Monitor to GitHub

This guide walks you through publishing this project to GitHub and setting up all integrations.

## Prerequisites

- GitHub account
- Git installed locally
- GitHub CLI (`gh`) installed (optional but recommended)

## Step 1: Create GitHub Repository

### Option A: Using GitHub CLI (Recommended)

```bash
cd /path/to/git-todo-monitor
gh repo create git-todo-monitor --public --source=. --description="Automated git monitoring with AI-powered todo summaries"
gh repo edit --add-topic python --add-topic automation --add-topic ai --add-topic productivity
```

### Option B: Using GitHub Web Interface

1. Go to https://github.com/new
2. Repository name: `git-todo-monitor`
3. Description: "Automated git monitoring with AI-powered todo summaries"
4. Choose: Public
5. **Don't** initialize with README (we have one)
6. Click "Create repository"

Then push your code:
```bash
cd /path/to/git-todo-monitor
git remote add origin https://github.com/yourusername/git-todo-monitor.git
git branch -M main
git push -u origin main
```

## Step 2: Set Up GitHub Integration (Replit)

If you're using Replit, set up the GitHub integration to enable issues and PR features:

```bash
# The GitHub connector will be proposed during setup
# It will handle authentication automatically
```

Or manually set environment variable:
```bash
export GITHUB_TOKEN=your_github_token_here
```

Add to config.json:
```json
{
  "github_repo": "yourusername/git-todo-monitor",
  "sync_issues": true
}
```

## Step 3: Configure Repository Settings

### Enable GitHub Features

1. Go to repository Settings → Features
2. Enable:
   - [x] Issues
   - [x] Projects (for task management)
   - [x] Discussions (optional)

### Set Up Branch Protection

1. Settings → Branches → Add rule
2. Branch name pattern: `main`
3. Enable:
   - [x] Require pull request reviews before merging
   - [x] Require status checks to pass before merging
   - [x] Require branches to be up to date before merging

### Configure Labels

Create these labels in Issues → Labels:
- `bug` (red) - Something isn't working
- `enhancement` (blue) - New feature or request
- `tech-debt` (yellow) - Code quality improvements
- `documentation` (green) - Documentation updates
- `good first issue` (purple) - Good for newcomers
- `help wanted` (orange) - Extra attention needed

## Step 4: Set Up Secrets

Add these secrets in Settings → Secrets and variables → Actions:

1. `OPENAI_API_KEY` - Your OpenAI API key (for AI summaries)
2. `GITHUB_TOKEN` - Auto-provided by GitHub Actions

## Step 5: Enable GitHub Actions

1. Go to the Actions tab
2. Enable workflows
3. The CI/CD pipelines will run automatically on:
   - Push to main/develop
   - Pull requests
   - New releases (tags)

## Step 6: Create Initial Release

### Using GitHub CLI

```bash
# Tag the current version
git tag -a v1.0.0 -m "Initial release with GitHub integration"
git push origin v1.0.0

# Create release
gh release create v1.0.0 \
  --title "v1.0.0 - Initial Release" \
  --notes "See CHANGELOG.md for details"
```

### Using GitHub Web

1. Go to Releases → Create a new release
2. Tag: `v1.0.0`
3. Title: "v1.0.0 - Initial Release"
4. Description: Copy from CHANGELOG.md
5. Click "Publish release"

## Step 7: Sync TODOs to GitHub Issues

Run the GitHub integration to create issues from TODOs:

```bash
# Export TODOs as GitHub issues
python3 src/github_integration.py

# This creates github_issues.json
# Import using GitHub CLI:
cat github_issues.json | jq -r '.[] | @json' | while read issue; do
  title=$(echo $issue | jq -r '.title')
  body=$(echo $issue | jq -r '.body')
  labels=$(echo $issue | jq -r '.labels | join(",")')
  gh issue create --title "$title" --body "$body" --label "$labels"
done
```

## Step 8: Set Up Project Board

Create a project board for task management:

1. Go to Projects → New project
2. Template: "Board"
3. Name: "Git Todo Monitor Roadmap"
4. Add columns:
   - Backlog
   - Todo
   - In Progress
   - In Review
   - Done

Link issues to the project board as they're created.

## Step 9: Configure Integration Features

### Auto-sync TODOs to Issues

Add to config.json:
```json
{
  "github_repo": "yourusername/git-todo-monitor",
  "sync_issues": true,
  "auto_create_issues": true,
  "issue_labels": ["todo", "automated"]
}
```

### Enable PR Analysis

The monitor can analyze pull requests automatically. Configure in config.json:
```json
{
  "analyze_prs": true,
  "pr_check_patterns": ["TODO", "FIXME", "HACK"]
}
```

## Step 10: Community Setup

### Add Community Files

We've already created:
- [x] LICENSE (MIT)
- [x] CONTRIBUTING.md
- [x] CODE_OF_CONDUCT.md (recommended - add if needed)
- [x] Issue templates
- [x] PR template

### Add Topics/Tags

```bash
gh repo edit --add-topic python
gh repo edit --add-topic automation
gh repo edit --add-topic git
gh repo edit --add-topic ai
gh repo edit --add-topic productivity
gh repo edit --add-topic ubuntu
gh repo edit --add-topic desktop-notifications
```

### Enable GitHub Pages (Optional)

For documentation hosting:
1. Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main`, folder: `/docs`

## Step 11: Promote Your Project

### Add Badges to README

```markdown
![GitHub release](https://img.shields.io/github/v/release/yourusername/git-todo-monitor)
![GitHub](https://img.shields.io/github/license/yourusername/git-todo-monitor)
![GitHub issues](https://img.shields.io/github/issues/yourusername/git-todo-monitor)
![GitHub stars](https://img.shields.io/github/stars/yourusername/git-todo-monitor)
![CI](https://github.com/yourusername/git-todo-monitor/workflows/CI/badge.svg)
```

### Share on Social Media

- Twitter/X with hashtags: #Python #Automation #Productivity
- Dev.to article explaining the project
- Hacker News (Show HN)
- Reddit: r/Python, r/programming, r/productivity

### List on Directories

- [Awesome Python](https://github.com/vinta/awesome-python)
- [Awesome Ubuntu](https://github.com/bpearson/Awesome-Ubuntu-Linux)
- [Python Weekly](https://www.pythonweekly.com/)

## Maintenance

### Regular Tasks

1. **Weekly**: Review and respond to issues
2. **Monthly**: Update dependencies, check security alerts
3. **Quarterly**: Major feature releases
4. **As needed**: Bug fixes, documentation updates

### Versioning Strategy

Follow Semantic Versioning (SemVer):
- **Major** (v2.0.0): Breaking changes
- **Minor** (v1.1.0): New features, backward compatible
- **Patch** (v1.0.1): Bug fixes

## Testing the Integration

Run comprehensive tests before going live:

```bash
# Test CLI
./test_cli.sh

# Test monitor
python3 src/test_monitor.py

# Test GitHub integration
python3 src/github_integration.py

# Test task manager
python3 src/task_manager.py

# Test roadmap planner
python3 src/roadmap_planner.py
```

## Troubleshooting

### GitHub Actions Failing

- Check secrets are properly set
- Verify Python version compatibility
- Review workflow logs for specific errors

### Issue Sync Not Working

- Verify GITHUB_TOKEN is set
- Check repository permissions
- Ensure github_repo in config is correct

### PR Analysis Not Running

- Verify webhook is configured
- Check GitHub Actions permissions
- Review workflow triggers

## Success Checklist

- [ ] Repository created and code pushed
- [ ] GitHub integration configured
- [ ] Actions/CI workflows passing
- [ ] Initial release published
- [ ] Issues synced from TODOs
- [ ] Project board created
- [ ] Community files added
- [ ] README badges added
- [ ] Topics/tags configured
- [ ] Shared on social media

Congratulations! Your project is now live on GitHub! 🎉
