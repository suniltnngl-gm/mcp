#!/usr/bin/env python3
"""Integrated AI Discussion System - Real AI responses with cost optimization and decision tracking"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Import existing systems
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "python-code" / "orchestration"))

try:
    from smart_ai_router import SmartAIRouter
    from session_tracker import SessionTracker
    from ai_action_tracker import AIActionTracker
    from decision_tracker import DecisionTracker
    from consensus_analyzer import ConsensusAnalyzer
    from enhanced_health_monitor import EnhancedHealthMonitor
    from ai_task_classifier import AITaskClassifier
    from enhanced_ai_registry import EnhancedAIRegistry
    from provider_alternatives_manager import ProviderAlternativesManager
    from ai_cost_tracker import AICostTracker
    from real_ai_client import real_ai_client
    from logging_config import orchestration_logger
    TRACKING_ENABLED = True
except ImportError:
    TRACKING_ENABLED = False

@dataclass
class AIParticipant:
    """AI participant with provider and role"""
    name: str
    role: str
    expertise: List[str]
    provider: str
    personality: str
    complexity_level: str = 'simple'

@dataclass
class Message:
    id: str
    participant: str
    timestamp: str
    content: str
    provider_used: Optional[str] = None
    cost: Optional[float] = None
    references: List[str] = None
    
    def __post_init__(self):
        if self.references is None:
            self.references = []

@dataclass
class Discussion:
    id: str
    topic: str
    created: str
    status: str
    participants: List[str]
    context: Dict
    messages: List[Message]
    decisions: List[str] = None
    total_cost: float = 0.0
    
    def __post_init__(self):
        if self.decisions is None:
            self.decisions = []

class IntegratedAIDiscussion:
    """AI Discussion System with real AI responses, cost optimization, and decision tracking"""
    
    AI_PARTICIPANTS = {
        "architect-ai": AIParticipant(
            name="architect-ai",
            role="Software Architect", 
            expertise=["system design", "scalability", "patterns"],
            provider="auto",
            personality="analytical, thorough",
            complexity_level="complex"
        ),
        "cost-optimizer-ai": AIParticipant(
            name="cost-optimizer-ai",
            role="Cost Analyst",
            expertise=["cloud costs", "optimization", "budget analysis"],
            provider="auto", 
            personality="pragmatic, budget-conscious",
            complexity_level="moderate"
        ),
        "devops-ai": AIParticipant(
            name="devops-ai",
            role="DevOps Engineer",
            expertise=["deployment", "monitoring", "automation"],
            provider="auto",
            personality="practical, operations-focused", 
            complexity_level="moderate"
        ),
        "security-ai": AIParticipant(
            name="security-ai",
            role="Security Analyst",
            expertise=["security", "compliance", "risk assessment"],
            provider="auto",
            personality="cautious, thorough",
            complexity_level="complex"
        )
    }
    
    def __init__(self, storage_dir: str = "threads", enable_tracking: bool = True):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Initialize AI router for cost optimization
        self.ai_router = SmartAIRouter()
        
        # Initialize decision tracking
        self.decision_tracker = DecisionTracker()
        
        # Initialize consensus analyzer
        if TRACKING_ENABLED:
            self.consensus_analyzer = ConsensusAnalyzer()
            self.health_monitor = EnhancedHealthMonitor()
            self.task_classifier = AITaskClassifier()
            self.ai_registry = EnhancedAIRegistry()
            self.alternatives_manager = ProviderAlternativesManager()
            self.cost_tracker = AICostTracker()
        
        # Initialize tracking
        self.tracking_enabled = enable_tracking and TRACKING_ENABLED
        if self.tracking_enabled:
            base_dir = Path(__file__).parent
            self.session_tracker = SessionTracker(str(base_dir / "session_history.jsonl"))
            self.action_tracker = AIActionTracker(str(base_dir / "ai_action_history.jsonl"))
    
    def create_discussion(self, topic: str, participants: List[str], 
                         context: Dict = None) -> str:
        """Create new discussion with AI participants"""
        discussion_id = f"disc-{int(time.time())}"
        
        if self.tracking_enabled:
            self.session_tracker.start_session(f"AI Discussion: {topic}")
        
        discussion = Discussion(
            id=discussion_id,
            topic=topic,
            created=datetime.now().isoformat(),
            status="active",
            participants=participants,
            context=context or {},
            messages=[]
        )
        
        self._save_discussion(discussion)
        
        if self.tracking_enabled:
            self.session_tracker.add_action(
                purpose="Create AI discussion",
                action=f"integrated_discussion.create({topic})",
                result=f"Created {discussion_id} with AI participants: {', '.join(participants)}"
            )
        
        return discussion_id
    
    def add_ai_response(self, discussion_id: str, participant: str, 
                       prompt_context: str = None) -> Dict:
        """Generate and add AI response to discussion"""
        if participant not in self.AI_PARTICIPANTS:
            return {"error": f"Unknown AI participant: {participant}"}
        
        discussion = self._load_discussion(discussion_id)
        ai_participant = self.AI_PARTICIPANTS[participant]
        
        # Build context from discussion history
        context = self._build_ai_context(discussion, ai_participant, prompt_context)
        
        # Use alternatives manager for optimal provider selection
        if hasattr(self, 'alternatives_manager'):
            # Classify task first
            classification = self.task_classifier.classify_task(
                context, f"{discussion_id}-{participant}-{len(discussion.messages)}"
            )
            
            # Use alternatives manager for provider selection
            provider, reason, selection_info = self.alternatives_manager.select_optimal_provider(
                classification.complexity, classification.category
            )
        elif hasattr(self, 'task_classifier'):
            # Fallback to task classifier
            classification = self.task_classifier.classify_task(
                context, f"{discussion_id}-{participant}-{len(discussion.messages)}"
            )
            provider = classification.recommended_provider
            reason = f"classified_as_{classification.complexity}_{classification.category}"
            selection_info = {}
        else:
            # Original fallback
            provider, reason = self.ai_router.select_provider(
                task_complexity=ai_participant.complexity_level,
                estimated_tokens=len(context) + 500
            )
            selection_info = {}
        
        start_time = time.time()
        
        # Generate AI response (mock for now - integrate with actual providers)
        response_content = self._generate_ai_response(context, ai_participant, provider)
        
        # Estimate cost
        estimated_cost = self.ai_router.estimate_cost(provider, len(context), len(response_content))
        
        # Create message
        message = Message(
            id=f"msg-{len(discussion.messages)+1:03d}",
            participant=participant,
            timestamp=datetime.now().isoformat(),
            content=response_content,
            provider_used=provider,
            cost=estimated_cost
        )
        
        discussion.messages.append(message)
        discussion.total_cost += estimated_cost
        self._save_discussion(discussion)
        
        # Track AI action
        if self.tracking_enabled:
            latency = time.time() - start_time
            self.action_tracker.log_action(
                action_type="ai_discussion",
                provider=provider,
                model=provider,
                input_tokens=len(context),
                output_tokens=len(response_content),
                cost=estimated_cost,
                latency=latency,
                success=True,
                context={
                    "discussion_id": discussion_id,
                    "participant": participant,
                    "role": ai_participant.role,
                    "selection_reason": reason
                },
                result=f"Generated response for {participant}"
            )
        
        result = {
            "message_id": message.id,
            "provider": provider,
            "cost": estimated_cost,
            "selection_reason": reason,
            "content": response_content
        }
        
        # Add classification info if available
        if hasattr(self, 'task_classifier') and 'classification' in locals():
            result["classification"] = {
                "complexity": classification.complexity,
                "category": classification.category,
                "confidence": classification.confidence
            }
        
        return result
    
    def _build_ai_context(self, discussion: Discussion, ai_participant: AIParticipant, 
                         additional_context: str = None) -> str:
        """Build context prompt for AI participant"""
        context_parts = [
            f"You are {ai_participant.name}, a {ai_participant.role}.",
            f"Your expertise: {', '.join(ai_participant.expertise)}",
            f"Your personality: {ai_participant.personality}",
            f"",
            f"Discussion Topic: {discussion.topic}",
        ]
        
        if discussion.context:
            context_parts.append(f"Context: {json.dumps(discussion.context, indent=2)}")
        
        if additional_context:
            context_parts.append(f"Additional Context: {additional_context}")
        
        # Add recent messages
        if discussion.messages:
            context_parts.append("\nRecent Discussion:")
            for msg in discussion.messages[-5:]:  # Last 5 messages
                context_parts.append(f"{msg.participant}: {msg.content}")
        
        context_parts.extend([
            "",
            f"As {ai_participant.name}, provide your perspective on this discussion.",
            "Be concise but insightful. Focus on your area of expertise.",
            "If making recommendations, be specific and actionable."
        ])
        
        return "\n".join(context_parts)
    
    def _generate_ai_response(self, context: str, ai_participant: AIParticipant, 
                            provider: str) -> str:
        """Generate AI response using real AI client or fallback to mock"""
        
        if hasattr(self, 'real_ai_client') and real_ai_client:
            try:
                # Use real AI client
                response = real_ai_client.generate_response(
                    prompt=context,
                    provider=provider,
                    max_tokens=1000
                )
                
                # Log real AI usage
                if self.tracking_enabled:
                    orchestration_logger.info("Real AI response generated",
                                            provider=provider,
                                            model=response.model,
                                            tokens=response.tokens_used,
                                            cost=response.cost,
                                            cached=response.cached)
                
                return response.content
                
            except Exception as e:
                if self.tracking_enabled:
                    orchestration_logger.error("Real AI failed, using fallback",
                                             provider=provider, error=str(e))
        
        # Fallback to mock responses (existing logic)
        role_responses = {
            "Software Architect": f"From an architectural perspective on '{context[:50]}...': I recommend considering scalability patterns and system boundaries. The current approach should be evaluated for long-term maintainability.",
            
            "Cost Analyst": f"Cost analysis for '{context[:50]}...': This approach has budget implications. I suggest evaluating cheaper alternatives and monitoring resource usage closely.",
            
            "DevOps Engineer": f"DevOps perspective on '{context[:50]}...': Implementation should consider deployment complexity, monitoring requirements, and operational overhead.",
            
            "Security Analyst": f"Security assessment of '{context[:50]}...': Need to evaluate potential vulnerabilities, access controls, and compliance requirements."
        }
        
        base_response = role_responses.get(ai_participant.role, f"Analysis from {ai_participant.name}: {context[:100]}...")
        
        return f"{base_response} [Generated via {provider}]"
    
    def run_collaborative_session(self, discussion_id: str, rounds: int = 3) -> Dict:
        """Run multi-round AI collaboration"""
        discussion = self._load_discussion(discussion_id)
        results = {"rounds": [], "total_cost": 0.0}
        
        if self.tracking_enabled:
            self.session_tracker.add_thinking(f"Starting {rounds}-round collaboration with {len(discussion.participants)} AI participants")
        
        for round_num in range(rounds):
            round_results = []
            
            for participant in discussion.participants:
                if participant in self.AI_PARTICIPANTS:
                    result = self.add_ai_response(discussion_id, participant)
                    round_results.append(result)
                    results["total_cost"] += result.get("cost", 0)
            
            results["rounds"].append({
                "round": round_num + 1,
                "responses": round_results
            })
            
            # Reload discussion for next round
            discussion = self._load_discussion(discussion_id)
        
        if self.tracking_enabled:
            self.session_tracker.complete_session(f"Completed {rounds} rounds, total cost: ${results['total_cost']:.4f}")
        
        return results
    
    def create_decision(self, discussion_id: str, title: str, description: str,
                       proposed_by: str = "system", execution_plan: List[str] = None) -> str:
        """Create a decision for the discussion"""
        decision_id = self.decision_tracker.create_decision(
            discussion_id, title, description, proposed_by, execution_plan
        )
        
        if self.tracking_enabled:
            self.session_tracker.add_action(
                purpose="Create decision",
                action=f"create_decision({title})",
                result=f"Created decision {decision_id}"
            )
        
        return decision_id
    
    def add_ai_vote(self, decision_id: str, participant: str, 
                   context: str = None) -> Dict:
        """Generate AI vote for a decision"""
        if participant not in self.AI_PARTICIPANTS:
            return {"error": f"Unknown AI participant: {participant}"}
        
        ai_participant = self.AI_PARTICIPANTS[participant]
        
        # Get decision details
        decision_summary = self.decision_tracker.get_decision_summary(decision_id)
        if "error" in decision_summary:
            return decision_summary
        
        # Build voting context
        voting_context = self._build_voting_context(decision_summary, ai_participant, context)
        
        # Select provider for voting (simple task)
        provider, reason = self.ai_router.select_provider(
            task_complexity="simple",
            estimated_tokens=len(voting_context) + 100
        )
        
        # Generate AI vote (mock implementation)
        vote_decision = self._generate_ai_vote(voting_context, ai_participant, provider)
        
        # Record the vote
        result = self.decision_tracker.add_vote(decision_id, participant, vote_decision["vote"])
        result.update({
            "reasoning": vote_decision["reasoning"],
            "provider": provider,
            "selection_reason": reason
        })
        
        if self.tracking_enabled:
            self.action_tracker.log_action(
                action_type="ai_vote",
                provider=provider,
                model=provider,
                input_tokens=len(voting_context),
                output_tokens=len(vote_decision["reasoning"]),
                cost=self.ai_router.estimate_cost(provider, len(voting_context), 100),
                latency=0.5,  # Mock latency
                success=True,
                context={
                    "decision_id": decision_id,
                    "participant": participant,
                    "vote": vote_decision["vote"]
                },
                result=f"Vote: {vote_decision['vote']}"
            )
        
        return result
    
    def _build_voting_context(self, decision_summary: Dict, ai_participant: AIParticipant,
                            additional_context: str = None) -> str:
        """Build context for AI voting"""
        decision = decision_summary["decision"]
        
        context_parts = [
            f"You are {ai_participant.name}, a {ai_participant.role}.",
            f"Your expertise: {', '.join(ai_participant.expertise)}",
            f"Your personality: {ai_participant.personality}",
            "",
            f"Decision to vote on:",
            f"Title: {decision['title']}",
            f"Description: {decision['description']}",
            f"Proposed by: {decision['proposed_by']}",
        ]
        
        if decision.get("execution_plan"):
            context_parts.append(f"Execution plan: {', '.join(decision['execution_plan'])}")
        
        if additional_context:
            context_parts.append(f"Additional context: {additional_context}")
        
        context_parts.extend([
            "",
            "Based on your expertise and role, vote on this decision:",
            "- 'agree' if you support the decision",
            "- 'disagree' if you oppose the decision", 
            "- 'abstain' if you're neutral or need more information",
            "",
            "Provide your vote and brief reasoning."
        ])
        
        return "\n".join(context_parts)
    
    def _generate_ai_vote(self, context: str, ai_participant: AIParticipant, 
                         provider: str) -> Dict:
        """Generate AI vote decision (mock implementation)"""
        # Mock voting logic based on role
        role_voting_patterns = {
            "Software Architect": {"vote": "agree", "reasoning": "From an architectural perspective, this decision aligns with scalability and maintainability principles."},
            "Cost Analyst": {"vote": "disagree", "reasoning": "This decision may have significant cost implications that need further analysis."},
            "DevOps Engineer": {"vote": "agree", "reasoning": "This decision supports operational efficiency and deployment simplicity."},
            "Security Analyst": {"vote": "abstain", "reasoning": "Need more information about security implications before making a decision."}
        }
        
        default_vote = role_voting_patterns.get(ai_participant.role, {
            "vote": "abstain", 
            "reasoning": "Need more context to make an informed decision."
        })
        
        return {
            "vote": default_vote["vote"],
            "reasoning": f"{default_vote['reasoning']} [Generated via {provider}]"
        }
    
    def analyze_consensus(self, discussion_id: str) -> Dict:
        """Analyze consensus in the discussion using AI"""
        if not hasattr(self, 'consensus_analyzer'):
            return {"error": "Consensus analyzer not available"}
        
        discussion = self._load_discussion(discussion_id)
        messages = [asdict(msg) for msg in discussion.messages]
        
        if self.tracking_enabled:
            self.session_tracker.add_thinking(f"Analyzing consensus for discussion with {len(messages)} messages")
        
        analysis = self.consensus_analyzer.analyze_discussion_consensus(discussion_id, messages)
        
        if self.tracking_enabled:
            self.session_tracker.add_action(
                purpose="Analyze consensus",
                action=f"consensus_analyzer.analyze({discussion_id})",
                result=f"Consensus: {analysis.overall_consensus}, Confidence: {analysis.confidence_score:.2f}"
            )
        
        return asdict(analysis)
    
    def get_next_steps(self, discussion_id: str) -> Dict:
        """Get AI-suggested next steps for the discussion"""
        if not hasattr(self, 'consensus_analyzer'):
            return {"error": "Consensus analyzer not available"}
        
        discussion = self._load_discussion(discussion_id)
        messages = [asdict(msg) for msg in discussion.messages]
        
        suggestions = self.consensus_analyzer.suggest_next_steps(discussion_id, messages)
        
        if self.tracking_enabled:
            self.session_tracker.add_action(
                purpose="Get next steps",
                action=f"consensus_analyzer.suggest_next_steps({discussion_id})",
                result=f"Generated {len(suggestions.get('recommendations', {}))} recommendation categories"
            )
        
        return suggestions
    
    def auto_propose_decisions(self, discussion_id: str) -> List[str]:
        """Automatically propose decisions based on consensus analysis"""
        if not hasattr(self, 'consensus_analyzer'):
            return []
        
        discussion = self._load_discussion(discussion_id)
        messages = [asdict(msg) for msg in discussion.messages]
        
        proposed_decisions = self.consensus_analyzer.auto_propose_decisions(discussion_id, messages)
        
        if self.tracking_enabled:
            self.session_tracker.add_action(
                purpose="Auto-propose decisions",
                action=f"consensus_analyzer.auto_propose_decisions({discussion_id})",
                result=f"Proposed {len(proposed_decisions)} decisions"
            )
        
        return proposed_decisions
    
    def get_system_health(self) -> Dict:
        """Get comprehensive system health dashboard"""
        if not hasattr(self, 'health_monitor'):
            return {"error": "Health monitor not available"}
        
        dashboard = self.health_monitor.generate_dashboard_data()
        
        if self.tracking_enabled:
            self.session_tracker.add_action(
                purpose="Get system health",
                action="health_monitor.generate_dashboard_data()",
                result=f"System status: {dashboard['system_health']['overall_status']}"
            )
        
        return dashboard
    
    def get_provider_recommendations(self) -> Dict:
        """Get provider switching recommendations"""
        if not hasattr(self, 'health_monitor'):
            return {"error": "Health monitor not available"}
        
        recommendations = self.health_monitor.get_provider_recommendations()
        
        return {
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
    
    def classify_task(self, task_text: str, task_id: str = None) -> Dict:
        """Classify a task and get provider recommendations"""
        if not hasattr(self, 'task_classifier'):
            return {"error": "Task classifier not available"}
        
        classification = self.task_classifier.classify_task(task_text, task_id)
        
        if self.tracking_enabled:
            self.session_tracker.add_action(
                purpose="Classify task",
                action=f"task_classifier.classify({task_text[:50]}...)",
                result=f"Complexity: {classification.complexity}, Provider: {classification.recommended_provider}"
            )
        
        return asdict(classification)
    
    def get_classification_stats(self) -> Dict:
        """Get task classification statistics"""
        if not hasattr(self, 'task_classifier'):
            return {"error": "Task classifier not available"}
        
        return self.task_classifier.get_classification_stats()
    
    def analyze_codebase(self, directory_path: str) -> Dict:
        """Analyze codebase with AI registry"""
        if not hasattr(self, 'ai_registry'):
            return {"error": "AI registry not available"}
        
        directory = Path(directory_path)
        if not directory.exists():
            return {"error": f"Directory not found: {directory_path}"}
        
        # Collect files
        file_paths = []
        for ext in self.ai_registry.config["file_extensions"]:
            file_paths.extend(directory.rglob(f"*{ext}"))
        
        # Create and process batch job
        job_id = self.ai_registry.create_batch_job(file_paths, f"codebase_{int(time.time())}")
        
        if self.tracking_enabled:
            self.session_tracker.add_thinking(f"Starting codebase analysis with {len(file_paths)} files")
        
        result = self.ai_registry.process_batch_job(job_id)
        
        if self.tracking_enabled:
            self.session_tracker.add_action(
                purpose="Analyze codebase",
                action=f"ai_registry.analyze_codebase({directory_path})",
                result=f"Processed {result.get('processed', 0)} files, cost: ${result.get('total_cost', 0):.2f}"
            )
        
        return result
    
    def get_registry_summary(self) -> Dict:
        """Get AI registry analysis summary"""
        if not hasattr(self, 'ai_registry'):
            return {"error": "AI registry not available"}
        
        return self.ai_registry.get_analysis_summary()
    
    def get_provider_alternatives(self, task_complexity: str = "moderate") -> Dict:
        """Get provider alternatives and recommendations"""
        if not hasattr(self, 'alternatives_manager'):
            return {"error": "Provider alternatives manager not available"}
        
        provider, reason, info = self.alternatives_manager.select_optimal_provider(task_complexity)
        recommendations = self.alternatives_manager.get_switching_recommendations()
        analytics = self.alternatives_manager.get_provider_analytics()
        
        return {
            "optimal_selection": {
                "provider": provider,
                "reason": reason,
                "selection_info": info
            },
            "switching_recommendations": recommendations,
            "provider_analytics": analytics,
            "current_budget_tier": self.alternatives_manager.current_budget_tier
        }
    
    def get_cost_status(self) -> Dict:
        """Get current cost and budget status"""
        if not hasattr(self, 'cost_tracker'):
            return {"error": "Cost tracker not available"}
        
        return self.cost_tracker.check_budget_status()
    
    def get_cost_report(self) -> Dict:
        """Get comprehensive cost report"""
        if not hasattr(self, 'cost_tracker'):
            return {"error": "Cost tracker not available"}
        
        return self.cost_tracker.generate_cost_report()
    
    def update_budget_limits(self, daily_limit: float, monthly_limit: float) -> Dict:
        """Update budget limits"""
        if not hasattr(self, 'cost_tracker'):
            return {"error": "Cost tracker not available"}
        
        success = self.cost_tracker.update_budget_config(
            daily_limit=daily_limit, 
            monthly_limit=monthly_limit
        )
        
        if self.tracking_enabled:
            self.session_tracker.add_action(
                purpose="Update budget limits",
                action=f"cost_tracker.update_budget_config({daily_limit}, {monthly_limit})",
                result=f"Budget limits updated: daily=${daily_limit}, monthly=${monthly_limit}"
            )
        
        return {
            "success": success,
            "daily_limit": daily_limit,
            "monthly_limit": monthly_limit
        }
    
    def get_cost_optimization_suggestions(self) -> Dict:
        """Get cost optimization suggestions"""
        if not hasattr(self, 'cost_tracker'):
            return {"error": "Cost tracker not available"}
        
        return self.cost_tracker.get_optimization_recommendations()
        """Update budget tier for cost management"""
        if not hasattr(self, 'alternatives_manager'):
            return {"error": "Provider alternatives manager not available"}
        
        success = self.alternatives_manager.update_budget_tier(new_tier)
        
        if self.tracking_enabled:
            self.session_tracker.add_action(
                purpose="Update budget tier",
                action=f"alternatives_manager.update_budget_tier({new_tier})",
                result=f"Budget tier update: {'success' if success else 'failed'}"
            )
        
        return {
            "success": success,
            "new_tier": new_tier if success else self.alternatives_manager.current_budget_tier,
            "daily_limit": self.alternatives_manager.config["budget_controls"]["daily_limits"].get(new_tier, 0)
        }
        """Setup automated codebase analysis"""
        if not hasattr(self, 'ai_registry'):
            return {"error": "AI registry not available"}
        
        cron_info = self.ai_registry.setup_cron_automation()
        
        return {
            "cron_setup": cron_info,
            "config": self.ai_registry.config,
            "automation_enabled": True,
            "next_run": "Based on cron schedule"
        }
        """Optimize provider selection for all messages in a discussion"""
        if not hasattr(self, 'task_classifier'):
            return {"error": "Task classifier not available"}
        
        discussion = self._load_discussion(discussion_id)
        optimizations = []
        total_current_cost = 0
        total_optimized_cost = 0
        
        for message in discussion.messages:
            if message.participant in self.AI_PARTICIPANTS:
                # Classify the message content
                classification = self.task_classifier.classify_task(
                    message.content, f"{discussion_id}-{message.id}"
                )
                
                current_cost = message.cost or 0
                optimized_cost = classification.estimated_cost
                
                total_current_cost += current_cost
                total_optimized_cost += optimized_cost
                
                optimizations.append({
                    "message_id": message.id,
                    "participant": message.participant,
                    "current_provider": message.provider_used,
                    "recommended_provider": classification.recommended_provider,
                    "current_cost": current_cost,
                    "optimized_cost": optimized_cost,
                    "savings": current_cost - optimized_cost,
                    "complexity": classification.complexity,
                    "category": classification.category
                })
        
        savings_percentage = 0
        if total_current_cost > 0:
            savings_percentage = ((total_current_cost - total_optimized_cost) / total_current_cost) * 100
        
        return {
            "discussion_id": discussion_id,
            "total_messages_analyzed": len(optimizations),
            "current_total_cost": total_current_cost,
            "optimized_total_cost": total_optimized_cost,
            "potential_savings": total_current_cost - total_optimized_cost,
            "savings_percentage": savings_percentage,
            "optimizations": optimizations,
            "analysis_timestamp": datetime.now().isoformat()
        }
        """Optimize provider selection based on health metrics"""
        if not hasattr(self, 'health_monitor'):
            return {"error": "Health monitor not available"}
        
        # Get current system health
        dashboard = self.health_monitor.generate_dashboard_data()
        
        # Find best providers for different complexity levels
        providers = dashboard["providers"]
        
        # Sort by combined score (availability + cost efficiency)
        def provider_score(p):
            health = p["health"]
            return (health["availability_score"] + health["cost_efficiency"]) / 2
        
        sorted_providers = sorted(providers, key=provider_score, reverse=True)
        
        optimization_plan = {
            "discussion_id": discussion_id,
            "current_system_status": dashboard["system_health"]["overall_status"],
            "recommended_providers": {
                "simple_tasks": [],
                "moderate_tasks": [],
                "complex_tasks": []
            },
            "cost_savings_potential": 0.0,
            "performance_impact": "minimal"
        }
        
        # Categorize providers by suitability
        for provider_data in sorted_providers:
            provider_name = provider_data["health"]["provider"]
            health = provider_data["health"]
            metrics = provider_data["metrics"]
            
            if health["status"] == "healthy":
                if metrics["cost_per_request"] < 0.01:  # Very cheap
                    optimization_plan["recommended_providers"]["simple_tasks"].append(provider_name)
                elif metrics["cost_per_request"] < 1.0:  # Moderate cost
                    optimization_plan["recommended_providers"]["moderate_tasks"].append(provider_name)
                else:  # Expensive but high quality
                    optimization_plan["recommended_providers"]["complex_tasks"].append(provider_name)
        
        # Calculate potential savings
        current_avg_cost = sum(p["metrics"]["cost_per_request"] for p in providers) / len(providers)
        cheapest_healthy = min((p["metrics"]["cost_per_request"] for p in providers 
                               if p["health"]["status"] == "healthy"), default=0)
        
        if current_avg_cost > 0:
            optimization_plan["cost_savings_potential"] = ((current_avg_cost - cheapest_healthy) / current_avg_cost) * 100
        
        return optimization_plan
        """Get consensus trends over the discussion timeline"""
        if not hasattr(self, 'consensus_analyzer'):
            return {"error": "Consensus analyzer not available"}
        
        discussion = self._load_discussion(discussion_id)
        messages = [asdict(msg) for msg in discussion.messages]
        
        trends = self.consensus_analyzer.get_consensus_trends(discussion_id, messages)
        
        return trends
        """Get discussion summary including decisions"""
        summary = self.get_discussion_summary(discussion_id)
        decisions = self.decision_tracker.get_decisions_for_discussion(discussion_id)
        
        summary["decisions"] = decisions
        summary["decision_count"] = len(decisions)
        
        return summary
        """Get discussion summary with cost analysis"""
        discussion = self._load_discussion(discussion_id)
        
        ai_messages = [m for m in discussion.messages if m.participant in self.AI_PARTICIPANTS]
        
        return {
            "id": discussion.id,
            "topic": discussion.topic,
            "status": discussion.status,
            "participants": discussion.participants,
            "message_count": len(discussion.messages),
            "ai_message_count": len(ai_messages),
            "total_cost": discussion.total_cost,
            "created": discussion.created,
            "last_activity": discussion.messages[-1].timestamp if discussion.messages else discussion.created
        }
    
    def _load_discussion(self, discussion_id: str) -> Discussion:
        """Load discussion from storage"""
        file_path = self.storage_dir / f"{discussion_id}.json"
        with open(file_path) as f:
            data = json.load(f)
            data['messages'] = [Message(**msg) for msg in data['messages']]
            return Discussion(**data)
    
    def _save_discussion(self, discussion: Discussion):
        """Save discussion to storage"""
        file_path = self.storage_dir / f"{discussion.id}.json"
        with open(file_path, 'w') as f:
            json.dump(asdict(discussion), f, indent=2)

def main():
    """CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python integrated_ai_discussion.py <command> [args...]")
        print("Commands:")
        print("  create <topic> <participants>  - Create discussion")
        print("  respond <disc_id> <participant> - Add AI response")
        print("  collaborate <disc_id> [rounds] - Run collaboration")
        print("  show <disc_id> - Show discussion")
        print("  decide <disc_id> <title> <description> - Create decision")
        print("  vote <dec_id> <participant> - Add AI vote")
        print("  decisions <disc_id> - Show decisions for discussion")
        print("  analyze <disc_id> - Analyze consensus")
        print("  next-steps <disc_id> - Get suggested next steps")
        print("  auto-decide <disc_id> - Auto-propose decisions")
        print("  trends <disc_id> - Show consensus trends")
        print("  health - Show system health dashboard")
        print("  optimize <disc_id> - Get provider optimization plan")
        print("  classify <task_text> - Classify task complexity")
        print("  stats - Show classification statistics")
        print("  analyze-code <directory> - Analyze codebase with AI")
        print("  registry-summary - Show AI registry summary")
        print("  setup-automation - Setup automated analysis")
        print("  alternatives [complexity] - Show provider alternatives")
        print("  set-budget <tier> - Set budget tier (free_tier/development/production/enterprise)")
        print("  cost-status - Show cost and budget status")
        print("  cost-report - Generate comprehensive cost report")
        print("  set-limits <daily> <monthly> - Set budget limits")
        print("  cost-optimize - Get cost optimization suggestions")
        return
    
    manager = IntegratedAIDiscussion()
    command = sys.argv[1]
    
    if command == "create":
        topic = sys.argv[2]
        participants = sys.argv[3].split(',') if len(sys.argv) > 3 else ["architect-ai", "cost-optimizer-ai"]
        disc_id = manager.create_discussion(topic, participants)
        print(f"Created discussion: {disc_id}")
    
    elif command == "respond":
        disc_id = sys.argv[2]
        participant = sys.argv[3]
        result = manager.add_ai_response(disc_id, participant)
        print(f"Response added: {json.dumps(result, indent=2)}")
    
    elif command == "collaborate":
        disc_id = sys.argv[2]
        rounds = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        results = manager.run_collaborative_session(disc_id, rounds)
        print(f"Collaboration complete: {json.dumps(results, indent=2)}")
    
    elif command == "show":
        disc_id = sys.argv[2]
        summary = manager.get_discussion_with_decisions(disc_id)
        print(f"Discussion summary: {json.dumps(summary, indent=2)}")
    
    elif command == "decide":
        disc_id = sys.argv[2]
        title = sys.argv[3]
        description = sys.argv[4]
        dec_id = manager.create_decision(disc_id, title, description)
        print(f"Created decision: {dec_id}")
    
    elif command == "vote":
        dec_id = sys.argv[2]
        participant = sys.argv[3]
        result = manager.add_ai_vote(dec_id, participant)
        print(f"Vote recorded: {json.dumps(result, indent=2)}")
    
    elif command == "decisions":
        disc_id = sys.argv[2]
        decisions = manager.decision_tracker.get_decisions_for_discussion(disc_id)
        print(f"Decisions: {json.dumps(decisions, indent=2)}")
    
    elif command == "analyze":
        disc_id = sys.argv[2]
        analysis = manager.analyze_consensus(disc_id)
        print(f"Consensus analysis: {json.dumps(analysis, indent=2)}")
    
    elif command == "next-steps":
        disc_id = sys.argv[2]
        steps = manager.get_next_steps(disc_id)
        print(f"Next steps: {json.dumps(steps, indent=2)}")
    
    elif command == "auto-decide":
        disc_id = sys.argv[2]
        decisions = manager.auto_propose_decisions(disc_id)
        print(f"Auto-proposed decisions: {decisions}")
    
    elif command == "trends":
        disc_id = sys.argv[2]
        trends = manager.get_consensus_trends(disc_id)
        print(f"Consensus trends: {json.dumps(trends, indent=2)}")
    
    elif command == "health":
        health = manager.get_system_health()
        print(f"System health: {json.dumps(health, indent=2)}")
    
    elif command == "optimize":
        disc_id = sys.argv[2]
        optimization = manager.optimize_discussion_providers(disc_id)
        print(f"Optimization analysis: {json.dumps(optimization, indent=2)}")
    
    elif command == "classify":
        if len(sys.argv) < 3:
            print("Usage: classify <task_text>")
            return
        task_text = sys.argv[2]
        classification = manager.classify_task(task_text)
        print(f"Task classification: {json.dumps(classification, indent=2)}")
    
    elif command == "stats":
        stats = manager.get_classification_stats()
        print(f"Classification stats: {json.dumps(stats, indent=2)}")
    
    elif command == "analyze-code":
        if len(sys.argv) < 3:
            print("Usage: analyze-code <directory>")
            return
        directory = sys.argv[2]
        result = manager.analyze_codebase(directory)
        print(f"Codebase analysis: {json.dumps(result, indent=2)}")
    
    elif command == "registry-summary":
        summary = manager.get_registry_summary()
        print(f"Registry summary: {json.dumps(summary, indent=2)}")
    
    elif command == "setup-automation":
        setup = manager.setup_automated_analysis()
        print(f"Automation setup: {json.dumps(setup, indent=2)}")
    
    elif command == "alternatives":
        complexity = sys.argv[2] if len(sys.argv) > 2 else "moderate"
        alternatives = manager.get_provider_alternatives(complexity)
        print(f"Provider alternatives: {json.dumps(alternatives, indent=2)}")
    
    elif command == "set-budget":
        if len(sys.argv) < 3:
            print("Usage: set-budget <tier>")
            print("Available tiers: free_tier, development, production, enterprise")
            return
        tier = sys.argv[2]
        result = manager.update_budget_tier(tier)
        print(f"Budget tier update: {json.dumps(result, indent=2)}")
    
    elif command == "cost-status":
        status = manager.get_cost_status()
        print(f"Cost status: {json.dumps(status, indent=2)}")
    
    elif command == "cost-report":
        report = manager.get_cost_report()
        print(f"Cost report: {json.dumps(report, indent=2)}")
    
    elif command == "set-limits":
        if len(sys.argv) < 4:
            print("Usage: set-limits <daily_limit> <monthly_limit>")
            return
        daily = float(sys.argv[2])
        monthly = float(sys.argv[3])
        result = manager.update_budget_limits(daily, monthly)
        print(f"Budget limits update: {json.dumps(result, indent=2)}")
    
    elif command == "cost-optimize":
        suggestions = manager.get_cost_optimization_suggestions()
        print(f"Cost optimization: {json.dumps(suggestions, indent=2)}")

if __name__ == "__main__":
    main()
