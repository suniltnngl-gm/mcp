#!/usr/bin/env python3

import os
import sys
from pathlib import Path

print("=" * 60)
print("Git Todo Monitor - Test Script")
print("=" * 60)

print("\n1. Checking Python dependencies...")
try:
    import git
    import ollama
    from dotenv import load_dotenv
    print("   ✓ All dependencies installed")
except ImportError as e:
    print(f"   ✗ Missing dependency: {e}")
    sys.exit(1)

print("\n2. Checking configuration file...")
config_file = Path("config.json")
if config_file.exists():
    print(f"   ✓ Config file found: {config_file}")
    import json
    with open(config_file) as f:
        config = json.load(f)
        print(f"   - Repository path: {config.get('repo_path')}")
        print(f"   - Time window: {config.get('time_window_hours')} hour(s)")
else:
    print("   ✗ Config file not found")

print("\n3. Checking git repository...")
try:
    from git import Repo
    repo = Repo(config.get('repo_path', '.'))
    print(f"   ✓ Git repository found")
    print(f"   - Branch: {repo.active_branch}")
    print(f"   - Commits: {len(list(repo.iter_commits(max_count=10)))}")
except Exception as e:
    print(f"   ✗ Git error: {e}")

print("\n4. Checking environment variables...")
load_dotenv()
if os.getenv("OLLAMA_API_KEY"):
    key = os.getenv("OLLAMA_API_KEY")
    print(f"   ✓ OLLAMA_API_KEY found (ends with ...{key[-4:]})")
else:
    print("   ✗ OLLAMA_API_KEY not found in .env file")
    print("   → Create .env file with: OLLAMA_API_KEY=your_key_here")

print("\n5. Checking notify-send (Ubuntu notifications)...")
import subprocess
try:
    result = subprocess.run(['which', 'notify-send'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✓ notify-send found: {result.stdout.strip()}")
        print("   Testing notification...")
        subprocess.run([
            'notify-send',
            'Git Todo Monitor Test',
            'If you see this, notifications are working!',
            '-i', 'dialog-information',
            '-t', '5000'
        ])
    else:
        print("   ✗ notify-send not found")
        print("   → Install with: sudo apt-get install libnotify-bin")
except Exception as e:
    print(f"   ⚠ Error testing notify-send: {e}")

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
print("\nTo run the monitor manually:")
print("  python3 git_todo_monitor.py")
print("\nTo set up hourly automation:")
print("  ./setup_cron.sh")
print()
