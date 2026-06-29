#!/usr/bin/env python3
"""AI-Powered Consensus Analyzer - Detect agreement levels and suggest next steps"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Import existing systems
try:
    from smart_ai_router import SmartAIRouter
    from decision_tracker import DecisionTracker, Decision, ConsensusLevel
    from ai_action_tracker import AIActionTracker
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

@dataclass
class ConsensusInsight:
    """AI-generated insight about consensus"""
    insight_type: str  # 'agreement', 'disagreement', 'concern', 'suggestion'
    content: str
    confidence: float
    participants_mentioned: List[str] = None
    
    def __post_init__(self):
        if self.participants_mentioned is None:
            self.participants_mentioned = []

@dataclass
class ConsensusAnalysis:
    """Comprehensive AI analysis of discussion consensus"""
    discussion_id: str
    analysis_timestamp: str
    overall_consensus: ConsensusLevel
    confidence_score: float
    key_agreements: List[str]
    key_disagreements: List[str]
    concerns_raised: List[str]
    insights: List[ConsensusInsight]
    suggested_actions: List[str]
    potential_decisions: List[Dict[str, str]]
    provider_used: str
    analysis_cost: float

class ConsensusAnalyzer:
    """AI-powered consensus analysis for discussions"""
    
    def __init__(self):
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Required dependencies not available")
        
        self.ai_router = SmartAIRouter()
        self.decision_tracker = DecisionTracker()
        self.action_tracker = AIActionTracker()
        self.analysis_cache = {}
    
    def analyze_discussion_consensus(self, discussion_id: str, 
                                   messages: List[Dict], 
                                   force_refresh: bool = False) -> ConsensusAnalysis:
        """Analyze consensus in a discussion using AI"""
        
        # Check cache first
        cache_key = f"{discussion_id}_{len(messages)}"
        if not force_refresh and cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]
        
        # Build analysis context
        context = self._build_analysis_context(discussion_id, messages)
        
        # Select AI provider for analysis
        provider, reason = self.ai_router.select_provider(
            task_complexity="complex",  # Consensus analysis is complex
            estimated_tokens=len(context) + 1000
        )
        
        start_time = time.time()
        
        # Generate AI analysis
        analysis_result = self._generate_consensus_analysis(context, provider)
        
        # Calculate cost
        analysis_cost = self.ai_router.estimate_cost(
            provider, len(context), len(str(analysis_result))
        )
        
        # Create structured analysis
        consensus_analysis = ConsensusAnalysis(
            discussion_id=discussion_id,
            analysis_timestamp=datetime.now().isoformat(),
            overall_consensus=analysis_result["overall_consensus"],
            confidence_score=analysis_result["confidence_score"],
            key_agreements=analysis_result["key_agreements"],
            key_disagreements=analysis_result["key_disagreements"],
            concerns_raised=analysis_result["concerns_raised"],
            insights=[ConsensusInsight(**insight) for insight in analysis_result["insights"]],
            suggested_actions=analysis_result["suggested_actions"],
            potential_decisions=analysis_result["potential_decisions"],
            provider_used=provider,
            analysis_cost=analysis_cost
        )
        
        # Track the analysis
        self.action_tracker.log_action(
            action_type="consensus_analysis",
            provider=provider,
            model=provider,
            input_tokens=len(context),
            output_tokens=len(str(analysis_result)),
            cost=analysis_cost,
            latency=time.time() - start_time,
            success=True,
            context={
                "discussion_id": discussion_id,
                "message_count": len(messages),
                "consensus_level": analysis_result["overall_consensus"]
            },
            result=f"Consensus: {analysis_result['overall_consensus']}"
        )
        
        # Cache the result
        self.analysis_cache[cache_key] = consensus_analysis
        
        return consensus_analysis
    
    def _build_analysis_context(self, discussion_id: str, messages: List[Dict]) -> str:
        """Build context for AI consensus analysis"""
        context_parts = [
            "CONSENSUS ANALYSIS TASK",
            "=" * 50,
            "",
            f"Discussion ID: {discussion_id}",
            f"Total Messages: {len(messages)}",
            "",
            "INSTRUCTIONS:",
            "Analyze the following discussion for consensus patterns.",
            "Identify areas of agreement, disagreement, and concerns.",
            "Suggest actionable next steps and potential decisions.",
            "",
            "DISCUSSION MESSAGES:",
            "-" * 30
        ]
        
        # Add messages with participant roles
        for i, msg in enumerate(messages[-20:], 1):  # Last 20 messages
            participant = msg.get("participant", "unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")
            
            context_parts.append(f"{i}. [{participant}] ({timestamp[:19]})")
            context_parts.append(f"   {content}")
            context_parts.append("")
        
        context_parts.extend([
            "",
            "ANALYSIS REQUIREMENTS:",
            "1. Overall consensus level (unanimous/strong/moderate/weak/no_consensus)",
            "2. Confidence score (0.0-1.0)",
            "3. Key agreements (list of points where participants agree)",
            "4. Key disagreements (list of contentious points)",
            "5. Concerns raised (list of issues or risks mentioned)",
            "6. Insights (specific observations about participant positions)",
            "7. Suggested actions (concrete next steps)",
            "8. Potential decisions (decisions that could be proposed)",
            "",
            "Respond in JSON format with these exact keys."
        ])
        
        return "\n".join(context_parts)
    
    def _generate_consensus_analysis(self, context: str, provider: str) -> Dict:
        """Generate AI consensus analysis (mock implementation)"""
        # This would integrate with actual AI providers
        # For now, return structured mock analysis
        
        mock_analysis = {
            "overall_consensus": "moderate",
            "confidence_score": 0.75,
            "key_agreements": [
                "Need for improved system architecture",
                "Importance of cost optimization",
                "Value of operational efficiency"
            ],
            "key_disagreements": [
                "Microservices vs monolith approach",
                "Timeline for implementation",
                "Resource allocation priorities"
            ],
            "concerns_raised": [
                "Potential cost overruns",
                "Complexity of migration",
                "Team readiness for change"
            ],
            "insights": [
                {
                    "insight_type": "agreement",
                    "content": "All participants agree on the need for architectural improvements",
                    "confidence": 0.9,
                    "participants_mentioned": ["architect-ai", "cost-optimizer-ai", "devops-ai"]
                },
                {
                    "insight_type": "disagreement", 
                    "content": "Cost-optimizer-ai consistently raises budget concerns",
                    "confidence": 0.8,
                    "participants_mentioned": ["cost-optimizer-ai"]
                },
                {
                    "insight_type": "suggestion",
                    "content": "DevOps perspective focuses on operational simplicity",
                    "confidence": 0.7,
                    "participants_mentioned": ["devops-ai"]
                }
            ],
            "suggested_actions": [
                "Conduct detailed cost-benefit analysis",
                "Create proof-of-concept implementation",
                "Define clear migration timeline",
                "Establish success metrics"
            ],
            "potential_decisions": [
                {
                    "title": "Approve architectural assessment",
                    "description": "Conduct 2-week assessment of current architecture"
                },
                {
                    "title": "Allocate budget for POC",
                    "description": "Approve $10k budget for proof-of-concept development"
                }
            ]
        }
        
        # Add provider info to mock response
        mock_analysis["_generated_by"] = provider
        
        return mock_analysis
    
    def suggest_next_steps(self, discussion_id: str, messages: List[Dict]) -> Dict:
        """Suggest specific next steps based on consensus analysis"""
        analysis = self.analyze_discussion_consensus(discussion_id, messages)
        
        # Generate prioritized recommendations
        recommendations = {
            "immediate_actions": [],
            "short_term_goals": [],
            "decisions_to_propose": [],
            "consensus_building": []
        }
        
        # Categorize suggestions based on consensus level
        if analysis.overall_consensus in [ConsensusLevel.UNANIMOUS, ConsensusLevel.STRONG]:
            recommendations["immediate_actions"] = analysis.suggested_actions[:2]
            recommendations["decisions_to_propose"] = analysis.potential_decisions
        elif analysis.overall_consensus == ConsensusLevel.MODERATE:
            recommendations["consensus_building"] = [
                "Address key disagreements through focused discussion",
                "Gather additional data on contentious points"
            ]
            recommendations["short_term_goals"] = analysis.suggested_actions[:3]
        else:
            recommendations["consensus_building"] = [
                "Identify common ground among participants",
                "Clarify individual positions and concerns",
                "Consider breaking down complex issues"
            ]
        
        return {
            "discussion_id": discussion_id,
            "consensus_level": analysis.overall_consensus,
            "confidence": analysis.confidence_score,
            "recommendations": recommendations,
            "analysis_timestamp": analysis.analysis_timestamp
        }
    
    def auto_propose_decisions(self, discussion_id: str, messages: List[Dict],
                              min_consensus: ConsensusLevel = ConsensusLevel.MODERATE) -> List[str]:
        """Automatically propose decisions based on consensus analysis"""
        analysis = self.analyze_discussion_consensus(discussion_id, messages)
        
        proposed_decisions = []
        
        # Only propose decisions if consensus meets minimum threshold
        consensus_hierarchy = {
            ConsensusLevel.UNANIMOUS: 5,
            ConsensusLevel.STRONG: 4,
            ConsensusLevel.MODERATE: 3,
            ConsensusLevel.WEAK: 2,
            ConsensusLevel.NO_CONSENSUS: 1
        }
        
        if consensus_hierarchy.get(analysis.overall_consensus, 0) >= consensus_hierarchy.get(min_consensus, 0):
            for potential_decision in analysis.potential_decisions:
                decision_id = self.decision_tracker.create_decision(
                    discussion_id=discussion_id,
                    title=potential_decision["title"],
                    description=potential_decision["description"],
                    proposed_by="consensus_analyzer"
                )
                proposed_decisions.append(decision_id)
        
        return proposed_decisions
    
    def get_consensus_trends(self, discussion_id: str, messages: List[Dict]) -> Dict:
        """Analyze consensus trends over time"""
        if len(messages) < 6:  # Need minimum messages for trend analysis
            return {"error": "Insufficient messages for trend analysis"}
        
        # Analyze consensus at different points
        checkpoints = [
            len(messages) // 4,      # 25%
            len(messages) // 2,      # 50%
            3 * len(messages) // 4,  # 75%
            len(messages)            # 100%
        ]
        
        trend_data = []
        
        for checkpoint in checkpoints:
            if checkpoint > 0:
                subset_messages = messages[:checkpoint]
                analysis = self.analyze_discussion_consensus(
                    f"{discussion_id}_trend_{checkpoint}", 
                    subset_messages,
                    force_refresh=True
                )
                
                trend_data.append({
                    "message_count": checkpoint,
                    "consensus_level": analysis.overall_consensus,
                    "confidence": analysis.confidence_score,
                    "timestamp": analysis.analysis_timestamp
                })
        
        return {
            "discussion_id": discussion_id,
            "trend_analysis": trend_data,
            "consensus_direction": self._determine_consensus_direction(trend_data)
        }
    
    def _determine_consensus_direction(self, trend_data: List[Dict]) -> str:
        """Determine if consensus is improving, declining, or stable"""
        if len(trend_data) < 2:
            return "insufficient_data"
        
        # Map consensus levels to numeric values
        consensus_values = {
            "unanimous": 5,
            "strong": 4,
            "moderate": 3,
            "weak": 2,
            "no_consensus": 1
        }
        
        values = [consensus_values.get(point["consensus_level"], 1) for point in trend_data]
        
        # Simple trend analysis
        if values[-1] > values[0]:
            return "improving"
        elif values[-1] < values[0]:
            return "declining"
        else:
            return "stable"

def main():
    """CLI interface for consensus analysis"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python consensus_analyzer.py <command> [args...]")
        print("Commands:")
        print("  analyze <discussion_id> <messages_json_file>")
        print("  suggest <discussion_id> <messages_json_file>")
        print("  trends <discussion_id> <messages_json_file>")
        print("  auto-decide <discussion_id> <messages_json_file>")
        return
    
    if not DEPENDENCIES_AVAILABLE:
        print("Error: Required dependencies not available")
        return
    
    analyzer = ConsensusAnalyzer()
    command = sys.argv[1]
    
    if command == "analyze":
        discussion_id = sys.argv[2]
        messages_file = sys.argv[3]
        
        with open(messages_file) as f:
            messages = json.load(f)
        
        analysis = analyzer.analyze_discussion_consensus(discussion_id, messages)
        print(json.dumps(asdict(analysis), indent=2))
    
    elif command == "suggest":
        discussion_id = sys.argv[2]
        messages_file = sys.argv[3]
        
        with open(messages_file) as f:
            messages = json.load(f)
        
        suggestions = analyzer.suggest_next_steps(discussion_id, messages)
        print(json.dumps(suggestions, indent=2))

if __name__ == "__main__":
    main()
