#!/usr/bin/env python3

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class RoadmapPlanner:
    def __init__(self, roadmap_file="roadmap_plan.json"):
        self.roadmap_file = roadmap_file
        self.milestones = self.load_roadmap()
    
    def load_roadmap(self) -> List[Dict]:
        try:
            with open(self.roadmap_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_roadmap(self):
        with open(self.roadmap_file, 'w') as f:
            json.dump(self.milestones, f, indent=2)
    
    def create_milestone(self, title: str, description: str, target_date: str, 
                        features: List[str] = None, version: str = None) -> Dict:
        milestone = {
            "id": len(self.milestones) + 1,
            "title": title,
            "description": description,
            "version": version or f"v{len(self.milestones) + 1}.0.0",
            "target_date": target_date,
            "status": "planned",
            "features": features or [],
            "progress": 0,
            "created_at": datetime.now().isoformat()
        }
        self.milestones.append(milestone)
        self.save_roadmap()
        return milestone
    
    def update_milestone_progress(self, milestone_id: int, progress: int):
        for milestone in self.milestones:
            if milestone["id"] == milestone_id:
                milestone["progress"] = min(100, max(0, progress))
                if progress >= 100:
                    milestone["status"] = "completed"
                elif progress > 0:
                    milestone["status"] = "in_progress"
                self.save_roadmap()
                return milestone
        return None
    
    def get_active_milestones(self) -> List[Dict]:
        return [m for m in self.milestones if m["status"] != "completed"]
    
    def get_upcoming_milestones(self, days: int = 30) -> List[Dict]:
        cutoff = (datetime.now() + timedelta(days=days)).isoformat()
        return [m for m in self.milestones 
                if m["target_date"] <= cutoff and m["status"] != "completed"]
    
    def export_to_markdown(self, output_file: str = "ROADMAP_PLAN.md") -> str:
        content = "# Development Roadmap\n\n"
        content += f"Last Updated: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        content += "## Overview\n\n"
        active = len(self.get_active_milestones())
        completed = len([m for m in self.milestones if m["status"] == "completed"])
        content += f"- **Active Milestones:** {active}\n"
        content += f"- **Completed Milestones:** {completed}\n"
        content += f"- **Total Milestones:** {len(self.milestones)}\n\n"
        
        content += "---\n\n"
        
        for milestone in sorted(self.milestones, key=lambda x: x["target_date"]):
            status_emoji = {
                "planned": "📋",
                "in_progress": "🚧",
                "completed": "✅"
            }.get(milestone["status"], "📌")
            
            content += f"## {status_emoji} {milestone['version']} - {milestone['title']}\n\n"
            content += f"**Target Date:** {milestone['target_date']}\n\n"
            content += f"**Status:** {milestone['status'].replace('_', ' ').title()}\n\n"
            content += f"**Progress:** {milestone['progress']}%\n\n"
            
            if milestone["progress"] > 0:
                progress_bar = "█" * (milestone["progress"] // 10) + "░" * (10 - milestone["progress"] // 10)
                content += f"`{progress_bar}` {milestone['progress']}%\n\n"
            
            content += f"{milestone['description']}\n\n"
            
            if milestone["features"]:
                content += "### Features\n\n"
                for feature in milestone["features"]:
                    content += f"- {feature}\n"
                content += "\n"
            
            content += "---\n\n"
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        print(f"✓ Exported roadmap to {output_file}")
        return content
    
    def generate_gantt_data(self) -> Dict:
        """Generate data for Gantt chart visualization"""
        gantt = {
            "milestones": [],
            "timeline": {
                "start": None,
                "end": None
            }
        }
        
        dates = []
        for milestone in self.milestones:
            gantt["milestones"].append({
                "name": milestone["title"],
                "version": milestone["version"],
                "start": milestone["created_at"][:10],
                "end": milestone["target_date"],
                "progress": milestone["progress"],
                "status": milestone["status"]
            })
            dates.append(milestone["target_date"])
        
        if dates:
            gantt["timeline"]["start"] = min(dates)
            gantt["timeline"]["end"] = max(dates)
        
        return gantt

if __name__ == "__main__":
    planner = RoadmapPlanner()
    
    if not planner.milestones:
        print("Creating example roadmap...")
        planner.create_milestone(
            "GitHub Integration",
            "Add full GitHub integration with issues and PR analysis",
            (datetime.now() + timedelta(days=30)).isoformat()[:10],
            features=[
                "Sync TODOs to GitHub Issues",
                "PR Review Automation",
                "Commit Analysis"
            ],
            version="v2.0.0"
        )
        planner.create_milestone(
            "Multi-Repository Support",
            "Monitor multiple repositories simultaneously",
            (datetime.now() + timedelta(days=60)).isoformat()[:10],
            features=[
                "Multi-repo configuration",
                "Aggregated summaries",
                "Repository comparison"
            ],
            version="v2.1.0"
        )
        planner.create_milestone(
            "Web Dashboard",
            "Interactive web dashboard for viewing history and analytics",
            (datetime.now() + timedelta(days=90)).isoformat()[:10],
            features=[
                "Todo analytics and trends",
                "Interactive charts",
                "Export capabilities"
            ],
            version="v3.0.0"
        )
    
    print("\n" + "=" * 60)
    print("Roadmap Summary:")
    print("=" * 60)
    active = planner.get_active_milestones()
    print(f"Active Milestones: {len(active)}")
    for m in active:
        print(f"  - {m['version']} {m['title']} ({m['target_date']})")
    print("\n" + "=" * 60)
    
    planner.export_to_markdown()
    
    gantt_data = planner.generate_gantt_data()
    with open("gantt_data.json", 'w') as f:
        json.dump(gantt_data, f, indent=2)
    print("✓ Exported Gantt chart data to gantt_data.json")
