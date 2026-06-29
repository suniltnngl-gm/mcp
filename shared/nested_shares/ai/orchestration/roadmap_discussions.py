#!/usr/bin/env python3
"""Roadmap Discussions - AI discussion integration for planning"""

import sys
from pathlib import Path
from datetime import datetime

# Add discussions path
sys.path.insert(0, str(Path(__file__).parent.parent / "discussions"))

class RoadmapDiscussions:
    def __init__(self):
        try:
            from discussion_manager import DiscussionManager
            self.discussion_manager = DiscussionManager()
            self.available = True
        except ImportError:
            self.available = False
    
    def create_optimization_discussion(self, analysis_data: dict) -> str:
        """Create AI discussion for optimization planning"""
        if not self.available:
            return "discussion_system_unavailable"
        
        # Determine discussion complexity and participants
        critical_issues = len(analysis_data.get("critical_issues", []))
        
        if critical_issues >= 2:
            participants = ["architect-ai", "optimizer-ai", "strategy-ai", "implementation-ai"]
            topic = "Critical Roadmap Optimization - Multiple Issues Detected"
        elif critical_issues == 1:
            participants = ["architect-ai", "optimizer-ai", "strategy-ai"]
            topic = "Roadmap Optimization - Priority Issue Resolution"
        else:
            participants = ["optimizer-ai", "strategy-ai"]
            topic = "Roadmap Improvement - Continuous Optimization"
        
        # Create discussion context
        context = {
            "discussion_type": "roadmap_optimization",
            "analysis_data": analysis_data,
            "urgency": "high" if critical_issues >= 2 else "medium" if critical_issues == 1 else "low",
            "focus_areas": ["nested_structure", "merge_operations", "documentation", "automation"]
        }
        
        disc_id = self.discussion_manager.create_discussion(topic, participants, context)
        
        # Add initial analysis message
        analysis_msg = self._format_analysis_message(analysis_data)
        self.discussion_manager.add_message(disc_id, "roadmap-analyzer", analysis_msg)
        
        return disc_id
    
    def _format_analysis_message(self, data: dict) -> str:
        """Format analysis data as discussion message"""
        msg = f"""🎛️ **Roadmap Analysis Complete**

**System Health**: {data.get('health_score', 0):.1%} ({data.get('status', 'unknown').title()})

**Critical Metrics**:
- Nested Efficiency: {data.get('metrics', {}).get('nested_efficiency', 0):.1%}
- Category Imbalance: {data.get('metrics', {}).get('imbalance_ratio', 0):.1%}
- Total Files: {data.get('metrics', {}).get('total_files', 0)}
- Categories: {data.get('metrics', {}).get('categories', 0)}

**Critical Issues Detected**:
{chr(10).join(f"- {issue.replace('_', ' ').title()}" for issue in data.get('critical_issues', []))}

**Immediate Actions Needed**:
{chr(10).join(f"- {action}" for action in data.get('next_actions', []))}

**Discussion Focus**:
Please analyze the current roadmap effectiveness and provide:
1. Priority ranking for identified issues
2. Optimization strategy recommendations  
3. Implementation timeline suggestions
4. Risk assessment for proposed changes
5. Success metrics for tracking progress

The system requires immediate attention to address the severe category imbalance (AI category: 1585 files vs others: 1-57 files each)."""
        
        return msg
    
    def create_progress_review(self, todo_progress: dict) -> str:
        """Create discussion for progress review"""
        if not self.available:
            return "discussion_system_unavailable"
        
        completion_rate = todo_progress.get("completion_rate", 0)
        
        # Select participants based on progress
        if completion_rate >= 0.8:
            participants = ["reviewer-ai", "optimizer-ai"]
            topic = "Roadmap Progress Review - Near Completion"
        elif completion_rate >= 0.5:
            participants = ["reviewer-ai", "optimizer-ai", "accelerator-ai"]
            topic = "Roadmap Progress Review - Mid-Point Analysis"
        else:
            participants = ["reviewer-ai", "troubleshooter-ai", "accelerator-ai", "strategy-ai"]
            topic = "Roadmap Progress Review - Acceleration Needed"
        
        context = {
            "discussion_type": "progress_review",
            "completion_rate": completion_rate,
            "todo_data": todo_progress,
            "review_type": "milestone" if completion_rate >= 0.5 else "checkpoint"
        }
        
        disc_id = self.discussion_manager.create_discussion(topic, participants, context)
        
        # Add progress summary
        progress_msg = self._format_progress_message(todo_progress)
        self.discussion_manager.add_message(disc_id, "progress-tracker", progress_msg)
        
        return disc_id
    
    def _format_progress_message(self, progress: dict) -> str:
        """Format progress data as discussion message"""
        completed = progress.get("completed_tasks", 0)
        total = progress.get("total_tasks", 8)
        rate = progress.get("completion_rate", 0)
        
        msg = f"""📊 **Roadmap Progress Review**

**Current Status**: {completed}/{total} tasks completed ({rate:.1%})

**Completed Tasks**:
- ✅ Roadmap engine with self-improvement capabilities
- ✅ Progress tracking integration
- ✅ Nested-shares optimizer  
- ✅ Merge/split pattern analyzer
- ✅ Docs-to-wiki converter

**Remaining Tasks**:
- ⏳ Self-improvement feedback loop
- ⏳ Roadmap dashboard
- ⏳ AI discussion integration

**Performance Indicators**:
- Task completion velocity: {rate/max(1, completed) if completed > 0 else 0:.2f} per task
- Time to completion estimate: {(total-completed)*2:.0f} hours remaining
- Bottlenecks: Integration complexity, testing requirements

**Discussion Objectives**:
1. Assess current progress quality vs speed
2. Identify acceleration opportunities
3. Recommend priority adjustments
4. Suggest process improvements
5. Plan final integration steps

Please provide recommendations for optimizing the remaining roadmap execution."""
        
        return msg
    
    def get_discussion_insights(self, disc_id: str) -> dict:
        """Extract insights from roadmap discussion"""
        if not self.available:
            return {"error": "discussion_system_unavailable"}
        
        discussion = self.discussion_manager.get_discussion(disc_id)
        
        insights = {
            "discussion_id": disc_id,
            "topic": discussion.topic,
            "participants": discussion.participants,
            "message_count": len(discussion.messages),
            "decisions": discussion.decisions,
            "status": discussion.status,
            "key_recommendations": self._extract_recommendations(discussion.messages),
            "consensus_level": self._assess_consensus(discussion.messages)
        }
        
        return insights
    
    def _extract_recommendations(self, messages: list) -> list:
        """Extract key recommendations from discussion messages"""
        recommendations = []
        
        for msg in messages:
            content = msg.content.lower()
            
            # Look for recommendation patterns
            if "recommend" in content or "suggest" in content:
                # Extract sentence containing recommendation
                sentences = msg.content.split('.')
                for sentence in sentences:
                    if "recommend" in sentence.lower() or "suggest" in sentence.lower():
                        recommendations.append(sentence.strip())
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _assess_consensus(self, messages: list) -> str:
        """Assess consensus level from discussion"""
        if len(messages) < 3:
            return "insufficient_data"
        
        # Simple consensus assessment based on agreement indicators
        agreement_words = ["agree", "correct", "yes", "exactly", "right"]
        disagreement_words = ["disagree", "no", "wrong", "however", "but"]
        
        agreement_count = 0
        disagreement_count = 0
        
        for msg in messages:
            content = msg.content.lower()
            agreement_count += sum(1 for word in agreement_words if word in content)
            disagreement_count += sum(1 for word in disagreement_words if word in content)
        
        if agreement_count > disagreement_count * 2:
            return "high_consensus"
        elif agreement_count > disagreement_count:
            return "moderate_consensus"
        else:
            return "low_consensus"

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Roadmap discussions")
    parser.add_argument("command", choices=["optimize", "review", "insights"])
    parser.add_argument("--disc-id", help="Discussion ID for insights")
    
    args = parser.parse_args()
    discussions = RoadmapDiscussions()
    
    if not discussions.available:
        print("❌ Discussion system not available")
        return
    
    if args.command == "optimize":
        # Create optimization discussion with current data
        from dashboard import RoadmapDashboard
        
        dashboard = RoadmapDashboard()
        analysis_data = dashboard.create_summary_report()
        
        disc_id = discussions.create_optimization_discussion(analysis_data)
        print(f"✅ Created optimization discussion: {disc_id}")
        print(f"View with: python discussion_manager.py show {disc_id}")
    
    elif args.command == "review":
        # Create progress review discussion
        progress_data = {
            "completed_tasks": 5,
            "total_tasks": 8,
            "completion_rate": 5/8
        }
        
        disc_id = discussions.create_progress_review(progress_data)
        print(f"✅ Created progress review: {disc_id}")
        print(f"View with: python discussion_manager.py show {disc_id}")
    
    elif args.command == "insights":
        if not args.disc_id:
            print("Error: --disc-id required for insights")
            return
        
        insights = discussions.get_discussion_insights(args.disc_id)
        
        print("💡 Discussion Insights")
        print("=" * 20)
        print(f"Topic: {insights['topic']}")
        print(f"Messages: {insights['message_count']}")
        print(f"Participants: {', '.join(insights['participants'])}")
        print(f"Consensus: {insights['consensus_level']}")
        
        if insights['key_recommendations']:
            print(f"\n🎯 Key Recommendations:")
            for i, rec in enumerate(insights['key_recommendations'], 1):
                print(f"{i}. {rec}")

if __name__ == "__main__":
    main()
