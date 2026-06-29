#!/usr/bin/env python3
"""Decision Tracking System - Track consensus, execution status, and results"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class DecisionStatus(str, Enum):
    """Decision execution status"""
    PROPOSED = "proposed"
    CONSENSUS = "consensus"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"
    DEFERRED = "deferred"

class ConsensusLevel(str, Enum):
    """Level of consensus among participants"""
    UNANIMOUS = "unanimous"      # All agree
    STRONG = "strong"           # 80%+ agree
    MODERATE = "moderate"       # 60-79% agree
    WEAK = "weak"              # 40-59% agree
    NO_CONSENSUS = "no_consensus"  # <40% agree

@dataclass
class Decision:
    """Individual decision with tracking"""
    id: str
    discussion_id: str
    title: str
    description: str
    proposed_by: str
    proposed_at: str
    status: DecisionStatus
    consensus_level: ConsensusLevel
    votes: Dict[str, str] = None  # participant -> vote (agree/disagree/abstain)
    execution_plan: List[str] = None
    execution_status: Dict[str, Any] = None
    results: Dict[str, Any] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        if self.votes is None:
            self.votes = {}
        if self.execution_plan is None:
            self.execution_plan = []
        if self.execution_status is None:
            self.execution_status = {}
        if self.results is None:
            self.results = {}

@dataclass
class ConsensusAnalysis:
    """Analysis of consensus for a decision"""
    decision_id: str
    total_participants: int
    votes_cast: int
    agree_count: int
    disagree_count: int
    abstain_count: int
    consensus_level: ConsensusLevel
    confidence: float
    analysis_timestamp: str
    key_points: List[str] = None
    
    def __post_init__(self):
        if self.key_points is None:
            self.key_points = []

class DecisionTracker:
    """Track decisions, consensus, and execution across AI discussions"""
    
    def __init__(self, storage_dir: str = "decisions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.decisions_file = self.storage_dir / "decisions.json"
        self.decisions: Dict[str, Decision] = self._load_decisions()
    
    def _load_decisions(self) -> Dict[str, Decision]:
        """Load decisions from storage"""
        if self.decisions_file.exists():
            with open(self.decisions_file) as f:
                data = json.load(f)
                return {k: Decision(**v) for k, v in data.items()}
        return {}
    
    def _save_decisions(self):
        """Save decisions to storage"""
        with open(self.decisions_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.decisions.items()}, f, indent=2)
    
    def create_decision(self, discussion_id: str, title: str, description: str,
                       proposed_by: str, execution_plan: List[str] = None) -> str:
        """Create a new decision for tracking"""
        decision_id = f"dec-{int(time.time())}"
        
        decision = Decision(
            id=decision_id,
            discussion_id=discussion_id,
            title=title,
            description=description,
            proposed_by=proposed_by,
            proposed_at=datetime.now().isoformat(),
            status=DecisionStatus.PROPOSED,
            consensus_level=ConsensusLevel.NO_CONSENSUS,
            execution_plan=execution_plan or []
        )
        
        self.decisions[decision_id] = decision
        self._save_decisions()
        
        return decision_id
    
    def add_vote(self, decision_id: str, participant: str, vote: str, 
                 reasoning: str = None) -> Dict:
        """Add vote for a decision"""
        if decision_id not in self.decisions:
            return {"error": f"Decision {decision_id} not found"}
        
        if vote not in ["agree", "disagree", "abstain"]:
            return {"error": "Vote must be 'agree', 'disagree', or 'abstain'"}
        
        decision = self.decisions[decision_id]
        decision.votes[participant] = vote
        decision.updated_at = datetime.now().isoformat()
        
        # Update consensus analysis
        consensus = self._analyze_consensus(decision_id)
        decision.consensus_level = consensus.consensus_level
        
        # Update status based on consensus
        if consensus.consensus_level in [ConsensusLevel.UNANIMOUS, ConsensusLevel.STRONG]:
            if consensus.agree_count > consensus.disagree_count:
                decision.status = DecisionStatus.CONSENSUS
        
        self._save_decisions()
        
        return {
            "decision_id": decision_id,
            "vote_recorded": vote,
            "consensus_level": consensus.consensus_level,
            "status": decision.status
        }
    
    def _analyze_consensus(self, decision_id: str) -> ConsensusAnalysis:
        """Analyze consensus level for a decision"""
        decision = self.decisions[decision_id]
        
        # Count votes
        agree_count = sum(1 for v in decision.votes.values() if v == "agree")
        disagree_count = sum(1 for v in decision.votes.values() if v == "disagree")
        abstain_count = sum(1 for v in decision.votes.values() if v == "abstain")
        votes_cast = len(decision.votes)
        
        # Calculate consensus level
        if votes_cast == 0:
            consensus_level = ConsensusLevel.NO_CONSENSUS
            confidence = 0.0
        else:
            agree_percentage = agree_count / votes_cast
            
            if agree_percentage == 1.0:
                consensus_level = ConsensusLevel.UNANIMOUS
                confidence = 1.0
            elif agree_percentage >= 0.8:
                consensus_level = ConsensusLevel.STRONG
                confidence = 0.8
            elif agree_percentage >= 0.6:
                consensus_level = ConsensusLevel.MODERATE
                confidence = 0.6
            elif agree_percentage >= 0.4:
                consensus_level = ConsensusLevel.WEAK
                confidence = 0.4
            else:
                consensus_level = ConsensusLevel.NO_CONSENSUS
                confidence = agree_percentage
        
        return ConsensusAnalysis(
            decision_id=decision_id,
            total_participants=votes_cast,  # Could be enhanced with discussion participant count
            votes_cast=votes_cast,
            agree_count=agree_count,
            disagree_count=disagree_count,
            abstain_count=abstain_count,
            consensus_level=consensus_level,
            confidence=confidence,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def update_execution_status(self, decision_id: str, step: str, 
                               status: str, details: Dict = None) -> Dict:
        """Update execution status for a decision step"""
        if decision_id not in self.decisions:
            return {"error": f"Decision {decision_id} not found"}
        
        decision = self.decisions[decision_id]
        
        if step not in decision.execution_plan:
            return {"error": f"Step '{step}' not in execution plan"}
        
        decision.execution_status[step] = {
            "status": status,
            "updated_at": datetime.now().isoformat(),
            "details": details or {}
        }
        
        # Update overall decision status
        completed_steps = sum(1 for s in decision.execution_status.values() 
                            if s.get("status") == "completed")
        total_steps = len(decision.execution_plan)
        
        if completed_steps == 0:
            decision.status = DecisionStatus.APPROVED
        elif completed_steps < total_steps:
            decision.status = DecisionStatus.IN_PROGRESS
        else:
            decision.status = DecisionStatus.COMPLETED
        
        decision.updated_at = datetime.now().isoformat()
        self._save_decisions()
        
        return {
            "decision_id": decision_id,
            "step": step,
            "status": status,
            "progress": f"{completed_steps}/{total_steps}",
            "overall_status": decision.status
        }
    
    def add_results(self, decision_id: str, results: Dict) -> Dict:
        """Add execution results for a decision"""
        if decision_id not in self.decisions:
            return {"error": f"Decision {decision_id} not found"}
        
        decision = self.decisions[decision_id]
        decision.results.update(results)
        decision.updated_at = datetime.now().isoformat()
        
        self._save_decisions()
        
        return {
            "decision_id": decision_id,
            "results_added": True,
            "total_results": len(decision.results)
        }
    
    def get_decision_summary(self, decision_id: str) -> Dict:
        """Get comprehensive decision summary"""
        if decision_id not in self.decisions:
            return {"error": f"Decision {decision_id} not found"}
        
        decision = self.decisions[decision_id]
        consensus = self._analyze_consensus(decision_id)
        
        return {
            "decision": asdict(decision),
            "consensus_analysis": asdict(consensus),
            "execution_progress": self._get_execution_progress(decision_id)
        }
    
    def _get_execution_progress(self, decision_id: str) -> Dict:
        """Get execution progress summary"""
        decision = self.decisions[decision_id]
        
        if not decision.execution_plan:
            return {"total_steps": 0, "completed": 0, "progress_percentage": 0}
        
        completed = sum(1 for step in decision.execution_plan 
                       if decision.execution_status.get(step, {}).get("status") == "completed")
        
        return {
            "total_steps": len(decision.execution_plan),
            "completed": completed,
            "progress_percentage": (completed / len(decision.execution_plan)) * 100,
            "status_by_step": {
                step: decision.execution_status.get(step, {"status": "pending"})
                for step in decision.execution_plan
            }
        }
    
    def get_decisions_for_discussion(self, discussion_id: str) -> List[Dict]:
        """Get all decisions for a discussion"""
        decisions = [
            asdict(decision) for decision in self.decisions.values()
            if decision.discussion_id == discussion_id
        ]
        
        return sorted(decisions, key=lambda x: x['proposed_at'], reverse=True)
    
    def get_pending_decisions(self) -> List[Dict]:
        """Get decisions that need attention"""
        pending = []
        
        for decision in self.decisions.values():
            if decision.status in [DecisionStatus.PROPOSED, DecisionStatus.CONSENSUS, 
                                 DecisionStatus.APPROVED, DecisionStatus.IN_PROGRESS]:
                pending.append({
                    "decision": asdict(decision),
                    "consensus": asdict(self._analyze_consensus(decision.id)),
                    "needs_action": self._get_needed_action(decision)
                })
        
        return sorted(pending, key=lambda x: x['decision']['proposed_at'], reverse=True)
    
    def _get_needed_action(self, decision: Decision) -> str:
        """Determine what action is needed for a decision"""
        if decision.status == DecisionStatus.PROPOSED:
            return "needs_votes"
        elif decision.status == DecisionStatus.CONSENSUS:
            return "needs_approval"
        elif decision.status == DecisionStatus.APPROVED:
            return "needs_execution_start"
        elif decision.status == DecisionStatus.IN_PROGRESS:
            return "needs_execution_update"
        else:
            return "no_action_needed"

def main():
    """CLI interface for decision tracking"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python decision_tracker.py <command> [args...]")
        print("Commands:")
        print("  create <disc_id> <title> <description> [proposed_by]")
        print("  vote <dec_id> <participant> <agree|disagree|abstain>")
        print("  execute <dec_id> <step> <status> [details_json]")
        print("  results <dec_id> <results_json>")
        print("  show <dec_id>")
        print("  list <disc_id>")
        print("  pending")
        return
    
    tracker = DecisionTracker()
    command = sys.argv[1]
    
    if command == "create":
        disc_id = sys.argv[2]
        title = sys.argv[3]
        description = sys.argv[4]
        proposed_by = sys.argv[5] if len(sys.argv) > 5 else "system"
        
        dec_id = tracker.create_decision(disc_id, title, description, proposed_by)
        print(f"Created decision: {dec_id}")
    
    elif command == "vote":
        dec_id = sys.argv[2]
        participant = sys.argv[3]
        vote = sys.argv[4]
        
        result = tracker.add_vote(dec_id, participant, vote)
        print(json.dumps(result, indent=2))
    
    elif command == "show":
        dec_id = sys.argv[2]
        summary = tracker.get_decision_summary(dec_id)
        print(json.dumps(summary, indent=2))
    
    elif command == "list":
        disc_id = sys.argv[2]
        decisions = tracker.get_decisions_for_discussion(disc_id)
        print(json.dumps(decisions, indent=2))
    
    elif command == "pending":
        pending = tracker.get_pending_decisions()
        print(json.dumps(pending, indent=2))

if __name__ == "__main__":
    main()
