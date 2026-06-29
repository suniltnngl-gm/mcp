#!/usr/bin/env python3

import json
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskStatus(Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    BLOCKED = "blocked"

class TaskManager:
    def __init__(self, tasks_file="tasks.json"):
        self.tasks_file = tasks_file
        self.tasks = self.load_tasks()
    
    def load_tasks(self) -> List[Dict]:
        try:
            with open(self.tasks_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_tasks(self):
        with open(self.tasks_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def create_task(self, title: str, description: str = "", priority: str = "medium", 
                   tags: List[str] = None, assignee: str = None) -> Dict:
        task = {
            "id": len(self.tasks) + 1,
            "title": title,
            "description": description,
            "priority": priority,
            "status": TaskStatus.TODO.value,
            "tags": tags or [],
            "assignee": assignee,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed_at": None
        }
        self.tasks.append(task)
        self.save_tasks()
        return task
    
    def update_task_status(self, task_id: int, status: str) -> Optional[Dict]:
        for task in self.tasks:
            if task["id"] == task_id:
                task["status"] = status
                task["updated_at"] = datetime.now().isoformat()
                if status == TaskStatus.DONE.value:
                    task["completed_at"] = datetime.now().isoformat()
                self.save_tasks()
                return task
        return None
    
    def get_tasks_by_status(self, status: str) -> List[Dict]:
        return [t for t in self.tasks if t["status"] == status]
    
    def get_tasks_by_priority(self, priority: str) -> List[Dict]:
        return [t for t in self.tasks if t["priority"] == priority]
    
    def get_high_priority_tasks(self) -> List[Dict]:
        return [t for t in self.tasks if t["priority"] in ["high", "critical"] 
                and t["status"] != TaskStatus.DONE.value]
    
    def generate_task_summary(self) -> Dict:
        summary = {
            "total_tasks": len(self.tasks),
            "by_status": {},
            "by_priority": {},
            "high_priority_open": len(self.get_high_priority_tasks())
        }
        
        for status in TaskStatus:
            count = len(self.get_tasks_by_status(status.value))
            if count > 0:
                summary["by_status"][status.value] = count
        
        for priority in TaskPriority:
            count = len(self.get_tasks_by_priority(priority.value))
            if count > 0:
                summary["by_priority"][priority.value] = count
        
        return summary
    
    def export_to_markdown(self, output_file: str = "TASKS.md"):
        content = "# Project Tasks\n\n"
        content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        summary = self.generate_task_summary()
        content += "## Summary\n\n"
        content += f"- **Total Tasks:** {summary['total_tasks']}\n"
        content += f"- **High Priority Open:** {summary['high_priority_open']}\n\n"
        
        for status in TaskStatus:
            status_tasks = self.get_tasks_by_status(status.value)
            if status_tasks:
                content += f"## {status.value.replace('_', ' ').title()}\n\n"
                for task in status_tasks:
                    priority_emoji = {
                        "critical": "🔥",
                        "high": "⚠️",
                        "medium": "📌",
                        "low": "💡"
                    }.get(task["priority"], "📋")
                    
                    content += f"### {priority_emoji} {task['title']}\n\n"
                    if task["description"]:
                        content += f"{task['description']}\n\n"
                    content += f"- **Priority:** {task['priority']}\n"
                    content += f"- **ID:** #{task['id']}\n"
                    if task["assignee"]:
                        content += f"- **Assignee:** @{task['assignee']}\n"
                    if task["tags"]:
                        content += f"- **Tags:** {', '.join(task['tags'])}\n"
                    content += f"- **Created:** {task['created_at'][:10]}\n"
                    content += "\n---\n\n"
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        print(f"✓ Exported tasks to {output_file}")
        return content

if __name__ == "__main__":
    tm = TaskManager()
    
    if not tm.tasks:
        print("Creating example tasks...")
        tm.create_task(
            "Add GitHub Issues Integration",
            "Sync TODOs to GitHub issues automatically",
            priority="high",
            tags=["feature", "github"]
        )
        tm.create_task(
            "Implement PR Review Bot",
            "Analyze PRs for code quality",
            priority="medium",
            tags=["feature", "github", "automation"]
        )
        tm.create_task(
            "Write comprehensive tests",
            "Add unit and integration tests",
            priority="high",
            tags=["testing", "quality"]
        )
    
    print("\n" + "=" * 60)
    print("Task Summary:")
    print("=" * 60)
    summary = tm.generate_task_summary()
    print(json.dumps(summary, indent=2))
    print("\n" + "=" * 60)
    
    tm.export_to_markdown()
