#!/usr/bin/env python3

import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import json
from git import Repo
from ollama import Client as OllamaClient
from dotenv import load_dotenv

load_dotenv()

class GitTodoMonitor:
    def __init__(self, config_path="config.json"):
        self.config = self.load_config(config_path)
        self.repo_path = self.config.get("repo_path", os.getcwd())
        self.time_window = self.config.get("time_window_hours", 1)
        self.ollama_model = self.config.get("ollama_model", "gpt-oss:20b-cloud")
        
        api_key = os.getenv("OLLAMA_API_KEY")
        if not api_key:
            print("ERROR: OLLAMA_API_KEY not found in environment.")
            print("Please create a .env file with your Ollama Cloud API key.")
            print("See .env.example for reference.")
            sys.exit(1)
        
        self.ollama = OllamaClient(
            host="https://ollama.com",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        
    def load_config(self, config_path):
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def get_recent_changes(self):
        try:
            repo = Repo(self.repo_path)
            since_time = datetime.now() - timedelta(hours=self.time_window)
            since_str = since_time.strftime("%Y-%m-%d %H:%M:%S")
            
            commits = list(repo.iter_commits(all=True, since=since_str))
            
            if not commits:
                return None
            
            changes_summary = {
                "commits": [],
                "files_changed": set(),
                "commit_messages": [],
                "diffs": []
            }
            
            for commit in commits:
                changes_summary["commits"].append({
                    "hash": commit.hexsha[:8],
                    "author": str(commit.author),
                    "date": commit.committed_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                    "message": commit.message.strip()
                })
                changes_summary["commit_messages"].append(commit.message.strip())
                
                if commit.parents:
                    diff = commit.parents[0].diff(commit, create_patch=True)
                    for diff_item in diff:
                        changes_summary["files_changed"].add(diff_item.b_path or diff_item.a_path)
                        if diff_item.diff:
                            changes_summary["diffs"].append({
                                "file": diff_item.b_path or diff_item.a_path,
                                "diff": diff_item.diff.decode('utf-8', errors='ignore')[:500]
                            })
            
            changes_summary["files_changed"] = list(changes_summary["files_changed"])
            return changes_summary
            
        except Exception as e:
            print(f"Error accessing git repository: {e}")
            return None
    
    def extract_todos_from_files(self):
        todos = []
        todo_patterns = ["TODO", "FIXME", "HACK", "XXX", "NOTE"]
        max_files = self.config.get("max_files_to_scan", 500)
        files_scanned = 0
        
        try:
            repo = Repo(self.repo_path)
            
            for item in repo.tree().traverse():
                if files_scanned >= max_files:
                    print(f"Reached max file scan limit ({max_files}), stopping todo extraction.")
                    break
                    
                if item.type == 'blob':
                    file_path = item.path
                    
                    if any(file_path.endswith(ext) for ext in ['.py', '.js', '.md', '.sh', '.ts', '.json']):
                        files_scanned += 1
                        try:
                            content = item.data_stream.read().decode('utf-8', errors='ignore')
                            lines = content.split('\n')
                            
                            for i, line in enumerate(lines, 1):
                                for pattern in todo_patterns:
                                    if pattern in line:
                                        todos.append({
                                            "file": file_path,
                                            "line": i,
                                            "content": line.strip()
                                        })
                        except:
                            pass
            
            return todos
        except Exception as e:
            print(f"Error extracting todos: {e}")
            return []
    
    def generate_ai_summary(self, changes, todos):
        if not changes and not todos:
            return "No recent changes or todos found."
        
        prompt = f"""Analyze the following git activity and todos, then create a concise summary for a desktop notification (max 200 words).

Recent Git Changes (last {self.time_window} hour(s)):
"""
        
        if changes:
            prompt += f"\nCommits: {len(changes['commits'])}\n"
            prompt += f"Files changed: {', '.join(changes['files_changed'][:10])}\n"
            prompt += f"\nCommit messages:\n"
            for msg in changes['commit_messages'][:5]:
                prompt += f"- {msg}\n"
        else:
            prompt += "\nNo commits in the last hour.\n"
        
        if todos:
            prompt += f"\n\nActive TODOs found ({len(todos)} total):\n"
            for todo in todos[:10]:
                prompt += f"- {todo['file']}:{todo['line']} - {todo['content'][:80]}\n"
        
        prompt += """\n\nProvide a brief summary focusing on:
1. What work was done (if any commits)
2. Priority todos that need attention
3. Any patterns or themes in the changes

Keep it actionable and concise for a desktop notification."""
        
        try:
            response = self.ollama.chat(
                model=self.ollama_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes code changes and todos concisely."},
                    {"role": "user", "content": prompt}
                ],
                options={"num_predict": 300, "temperature": 0.7},
            )
            
            return response.message.content.strip()
        except Exception as e:
            return f"Error generating AI summary: {e}"
    
    def send_desktop_notification(self, summary):
        title = f"Git Todo Summary - {datetime.now().strftime('%H:%M')}"
        timeout = str(self.config.get("notification_timeout", 10000))
        
        try:
            subprocess.run([
                'notify-send',
                title,
                summary,
                '-i', 'dialog-information',
                '-t', timeout
            ], check=True)
            print(f"Notification sent: {title}")
        except FileNotFoundError:
            print("notify-send not found. Install libnotify-bin: sudo apt-get install libnotify-bin")
        except Exception as e:
            print(f"Error sending notification: {e}")
    
    def run(self, quiet=False):
        if not quiet:
            print(f"Checking repository: {self.repo_path}")
        
        changes = self.get_recent_changes()
        todos = self.extract_todos_from_files()
        
        summary = self.generate_ai_summary(changes, todos)
        
        if not quiet:
            print("\n" + "="*60)
            print("SUMMARY:")
            print("="*60)
            print(summary)
            print("="*60 + "\n")
        
        self.send_desktop_notification(summary)
        
        log_file = self.config.get("log_file", "todo_monitor.log")
        with open(log_file, 'a') as f:
            f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
            f.write(summary + "\n")
            f.write("-" * 60 + "\n")

def main():
    """Main entry point for the git-todo-monitor CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Git Todo Monitor - Analyze git changes and extract todos")
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress console output')
    parser.add_argument('--config', '-c', default='config.json', help='Path to config file')
    parser.add_argument('--export-issues', action='store_true', help='Export TODOs as GitHub issues JSON')
    parser.add_argument('--sync-issues', action='store_true', help='Create GitHub issues from TODOs via gh CLI')
    parser.add_argument('--run-tasks', action='store_true', help='Run task manager')
    parser.add_argument('--run-roadmap', action='store_true', help='Run roadmap planner')
    args = parser.parse_args()
    
    if args.export_issues:
        sys.path.insert(0, os.path.dirname(__file__))
        from github_integration import GitHubIntegration
        config = {}
        if os.path.exists(args.config):
            with open(args.config, 'r') as f:
                config = json.load(f)
        repo_path = config.get("repo_path", os.getcwd())
        
        from git import Repo
        repo = Repo(repo_path)
        todos = []
        todo_patterns = ["TODO", "FIXME", "HACK", "XXX", "NOTE"]
        for item in repo.tree().traverse():
            if hasattr(item, 'type') and item.type == 'blob':
                file_path = str(item.path)
                if any(file_path.endswith(ext) for ext in ['.py', '.js', '.md', '.sh', '.ts', '.json']):
                    try:
                        content = item.data_stream.read().decode('utf-8', errors='ignore')
                        for i, line in enumerate(content.split('\n'), 1):
                            for pattern in todo_patterns:
                                if pattern in line:
                                    todos.append({"file": file_path, "line": i, "content": line.strip()})
                    except:
                        pass
        gh = GitHubIntegration(config_path=args.config)
        gh.export_issues_json(todos)
    elif args.sync_issues:
        sys.path.insert(0, os.path.dirname(__file__))
        from github_integration import GitHubIntegration
        config = {}
        if os.path.exists(args.config):
            with open(args.config, 'r') as f:
                config = json.load(f)
        repo_path = config.get("repo_path", os.getcwd())
        from git import Repo
        repo = Repo(repo_path)
        todos = []
        todo_patterns = ["TODO", "FIXME", "HACK", "XXX", "NOTE"]
        for item in repo.tree().traverse():
            if hasattr(item, 'type') and item.type == 'blob':
                file_path = str(item.path)
                if any(file_path.endswith(ext) for ext in ['.py', '.js', '.md', '.sh', '.ts', '.json']):
                    try:
                        content = item.data_stream.read().decode('utf-8', errors='ignore')
                        for i, line in enumerate(content.split('\n'), 1):
                            for pattern in todo_patterns:
                                if pattern in line:
                                    todos.append({"file": file_path, "line": i, "content": line.strip()})
                    except:
                        pass
        gh = GitHubIntegration(config_path=args.config)
        gh.sync_todos_to_issues(todos)
    elif args.run_tasks:
        sys.path.insert(0, os.path.dirname(__file__))
        from task_manager import TaskManager
        tm = TaskManager()
        tm.export_to_markdown()
        print("Task management summary exported")
    elif args.run_roadmap:
        sys.path.insert(0, os.path.dirname(__file__))
        from roadmap_planner import RoadmapPlanner
        planner = RoadmapPlanner()
        planner.export_to_markdown()
        print("Roadmap exported")
    else:
        monitor = GitTodoMonitor(config_path=args.config)
        monitor.run(quiet=args.quiet)

if __name__ == "__main__":
    main()
