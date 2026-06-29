#!/usr/bin/env python3
"""Merge Discussion Facilitator - AI-powered merge planning discussions"""

import sys
from pathlib import Path
from datetime import datetime

# Add discussions path
sys.path.insert(0, str(Path(__file__).parent.parent / "discussions"))
from discussion_manager import DiscussionManager
from merge_analyzer import MergeAnalyzer

class MergeDiscussionFacilitator:
    def __init__(self):
        self.discussion_manager = DiscussionManager()
        self.merge_analyzer = MergeAnalyzer()
    
    def create_merge_discussion(self, file1: Path, file2: Path, target_name: str) -> str:
        """Create AI discussion for merge planning"""
        
        # Analyze merge complexity
        analysis = self.merge_analyzer.analyze_merge(file1, file2)
        
        # Create discussion topic
        topic = f"Merge Planning: {file1.name} + {file2.name} → {target_name}"
        
        # Select AI participants based on complexity
        if analysis.merge_strategy == "simple_merge":
            participants = ["architect-ai", "code-reviewer-ai"]
        elif analysis.merge_strategy == "selective_merge":
            participants = ["architect-ai", "code-reviewer-ai", "integration-ai"]
        else:
            participants = ["architect-ai", "code-reviewer-ai", "integration-ai", "refactor-ai"]
        
        # Create discussion with context
        context = {
            "merge_type": "code_integration",
            "source_files": [str(file1), str(file2)],
            "target_file": target_name,
            "analysis": {
                "strategy": analysis.merge_strategy,
                "conflicts": analysis.conflicts,
                "integration_points": analysis.integration_points,
                "shared_deps": analysis.shared_dependencies[:10]  # Limit for readability
            }
        }
        
        disc_id = self.discussion_manager.create_discussion(topic, participants, context)
        
        # Add initial analysis message
        analysis_msg = self._format_analysis_message(analysis, file1, file2, target_name)
        self.discussion_manager.add_message(disc_id, "merge-analyzer", analysis_msg)
        
        return disc_id
    
    def _format_analysis_message(self, analysis, file1: Path, file2: Path, target: str) -> str:
        """Format merge analysis as discussion message"""
        msg = f"""🔍 **Merge Analysis Complete**

**Files**: {file1.name} + {file2.name} → {target}
**Strategy**: {analysis.merge_strategy}

**Conflicts Found**: {len(analysis.conflicts)}
{chr(10).join(f"- {c}" for c in analysis.conflicts[:5])}

**Integration Points**:
{chr(10).join(f"- {p}" for p in analysis.integration_points)}

**Shared Dependencies**: {len(analysis.shared_dependencies)}
{chr(10).join(f"- {d}" for d in analysis.shared_dependencies[:8])}

**Recommendations**:
1. Review conflict resolution strategy
2. Plan integration sequence
3. Identify testing requirements
4. Consider backward compatibility

Please provide your analysis and merge plan."""
        
        return msg
    
    def add_merge_decision(self, disc_id: str, decision: str):
        """Add merge decision to discussion"""
        self.discussion_manager.add_decision(disc_id, decision)
    
    def get_merge_plan(self, disc_id: str) -> dict:
        """Extract merge plan from discussion"""
        discussion = self.discussion_manager.get_discussion(disc_id)
        
        plan = {
            "discussion_id": disc_id,
            "topic": discussion.topic,
            "strategy": discussion.context.get("analysis", {}).get("strategy"),
            "decisions": discussion.decisions,
            "messages": len(discussion.messages),
            "status": discussion.status,
            "participants": discussion.participants
        }
        
        return plan

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Facilitate merge discussions")
    parser.add_argument("command", choices=["create", "plan", "status"])
    parser.add_argument("--file1", help="First file to merge")
    parser.add_argument("--file2", help="Second file to merge") 
    parser.add_argument("--target", help="Target merged file name")
    parser.add_argument("--disc-id", help="Discussion ID")
    
    args = parser.parse_args()
    
    facilitator = MergeDiscussionFacilitator()
    
    if args.command == "create":
        if not all([args.file1, args.file2, args.target]):
            print("Error: --file1, --file2, and --target required for create")
            sys.exit(1)
        
        file1 = Path(args.file1)
        file2 = Path(args.file2)
        
        if not file1.exists() or not file2.exists():
            print("Error: Source files not found")
            sys.exit(1)
        
        disc_id = facilitator.create_merge_discussion(file1, file2, args.target)
        print(f"✅ Created merge discussion: {disc_id}")
        print(f"View with: python discussion_manager.py show {disc_id}")
    
    elif args.command == "plan":
        if not args.disc_id:
            print("Error: --disc-id required for plan")
            sys.exit(1)
        
        plan = facilitator.get_merge_plan(args.disc_id)
        print(f"\n📋 Merge Plan for {plan['topic']}")
        print(f"Strategy: {plan['strategy']}")
        print(f"Messages: {plan['messages']}")
        print(f"Status: {plan['status']}")
        print(f"Participants: {', '.join(plan['participants'])}")
        
        if plan['decisions']:
            print(f"\n✅ Decisions:")
            for i, decision in enumerate(plan['decisions'], 1):
                print(f"{i}. {decision}")
    
    elif args.command == "status":
        # Show all merge discussions
        dm = DiscussionManager()
        discussions = dm.list_discussions()
        
        merge_discussions = [d for d in discussions if "Merge Planning" in d.get('topic', '')]
        
        if not merge_discussions:
            print("No merge discussions found")
            return
        
        print(f"\n📋 Active Merge Discussions ({len(merge_discussions)})")
        print("-" * 50)
        
        for disc in merge_discussions:
            print(f"ID: {disc['id']}")
            print(f"Topic: {disc['topic']}")
            print(f"Status: {disc['status']}")
            print(f"Messages: {disc['message_count']}")
            print()

if __name__ == "__main__":
    main()
