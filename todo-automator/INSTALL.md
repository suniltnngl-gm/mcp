# Quick Start Installation Guide

## Step 1: Install System Dependencies (Ubuntu)

```bash
sudo apt-get update
sudo apt-get install libnotify-bin python3-pip git
```

## Step 2: Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Create a new API key
4. Copy the key (you'll need it in Step 4)

## Step 3: Install Python Dependencies

```bash
pip install gitpython openai python-dotenv
```

Or if using this project directly:
```bash
cd /path/to/git-todo-monitor
pip install -r requirements.txt  # if available, or use the command above
```

## Step 4: Configure the Monitor

### Automated Setup (Recommended)
```bash
./setup_cron.sh
```

The script will ask you for:
- Git repository path (default: current directory)
- Time window for checking changes (default: 1 hour)
- Your OpenAI API key

### Manual Setup
1. Create `.env` file:
```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

2. Edit `config.json` (optional):
```json
{
  "repo_path": "/path/to/your/repo",
  "time_window_hours": 1,
  "log_file": "todo_monitor.log",
  "notification_timeout": 10000,
  "max_files_to_scan": 500
}
```

## Step 5: Test the Setup

```bash
python3 test_monitor.py
```

This will verify:
- ✓ Python dependencies are installed
- ✓ Git repository is accessible
- ✓ OpenAI API key is configured
- ✓ Desktop notifications work

## Step 6: Run Manually (Optional)

Test the monitor once:
```bash
python3 git_todo_monitor.py
```

## Step 7: Enable Hourly Automation

### Using Cron (automated by setup_cron.sh)
The setup script automatically adds a cron job. Verify it:
```bash
crontab -l
```

### Manual Cron Setup
```bash
crontab -e
```

Add this line (adjust paths):
```
0 * * * * cd /path/to/git-todo-monitor && /usr/bin/python3 git_todo_monitor.py >> cron.log 2>&1
```

## Troubleshooting

### No notification appears
```bash
notify-send "Test" "Testing notifications"
```
If this doesn't work, check:
- You're in a graphical session
- libnotify-bin is installed

### OpenAI API errors
- Verify your API key in `.env`
- Check you have credits: https://platform.openai.com/usage

### Git repository not found
- Ensure `repo_path` in config.json points to a valid git repo
- Run `git status` in that directory to verify

## Viewing Logs

- **Summaries**: `tail -f todo_monitor.log`
- **Cron output**: `tail -f cron.log`

## Next Steps

Once everything is working:
1. The monitor will run every hour automatically
2. Check logs to see what it's tracking
3. Adjust configuration as needed
4. Enjoy automated todo summaries!
