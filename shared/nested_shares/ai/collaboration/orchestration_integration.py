#!/usr/bin/env python3
"""Integration with existing AI orchestration systems"""

import sys
from pathlib import Path

# Import existing orchestration
sys.path.insert(0, str(Path(__file__).parent.parent / "orchestration"))
from integrated_ai_discussion import IntegratedAIDiscussion
from decision_tracker import DecisionTracker
from roadmap_engine import RoadmapEngine

# Import collaboration tools
from gemini_kiro_bridge import GeminiKiroBridge
from gemini_context_rules import GeminiContextEngine

class CollaborationOrchestrator:
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.bridge = GeminiKiroBridge()
        self.context_engine = GeminiContextEngine(workspace_path)
        
        # Existing systems
        self.ai_discussion = IntegratedAIDiscussion()
        self.decision_tracker = DecisionTracker()
        self.roadmap_engine = RoadmapEngine()
    
    def start_collaboration(self, task_type: str, context: dict) -> str:
        """Start collaborative session with full integration"""
        # Create session
        session_id = self.bridge.create_session(task_type, context)
        
        # Set up Gemini context
        gemini_context = self.context_engine.create_context(task_type)
        
        # Integrate with existing systems
        # Create a discussion with relevant AI participants from IntegratedAIDiscussion's list
        self.ai_discussion.create_discussion(f"Collaborative {task_type} for session {session_id}", ["architect-ai", "security-ai"], context={"gemini_context": gemini_context, "task_context": context})
        # Decisions will be tracked via create_decision later
        
        return session_id
    
    def coordinate_review(self, files: list) -> dict:
        """Coordinate multi-AI file review"""
        session_id = self.start_collaboration("review", {"files": files})
        
        # Use existing review infrastructure
        results = {
            "session_id": session_id,
            "gemini_context": self.context_engine.get_all_ignore_patterns(),
            "integration_points": [
                "integrated_ai_discussion",
                "decision_tracker", 
                "roadmap_engine"
            ]
        }
        return results

if __name__ == "__main__":
    orchestrator = CollaborationOrchestrator("/media/sunil-kr/workspace/user-projects")
    session = orchestrator.coordinate_review(["roadmap_data.json", "progress_tracker.py"])
    print(f"Started collaborative review: {session['session_id']}")
