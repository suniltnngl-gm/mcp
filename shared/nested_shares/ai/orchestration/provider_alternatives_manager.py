#!/usr/bin/env python3
"""Provider Alternatives Manager - Automatic switching and fallback chains"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict

# Import existing systems
try:
    from smart_ai_router import SmartAIRouter
    from enhanced_health_monitor import EnhancedHealthMonitor
    from ai_action_tracker import AIActionTracker
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

@dataclass
class SwitchingEvent:
    """Record of provider switching event"""
    timestamp: str
    trigger: str
    from_provider: str
    to_provider: str
    reason: str
    cost_impact: float
    success: bool

@dataclass
class ProviderStatus:
    """Current status of a provider"""
    provider: str
    available: bool
    health_score: float
    current_cost_tier: str
    last_used: Optional[str]
    failure_count: int
    rate_limited_until: Optional[str]
    performance_score: float

class ProviderAlternativesManager:
    """Manage provider alternatives with automatic switching"""
    
    def __init__(self, config_file: str = "provider_alternatives.json"):
        self.config_file = Path(config_file)
        self.switching_log_file = Path("provider_switching_log.jsonl")
        
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Required dependencies not available")
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize systems
        self.ai_router = SmartAIRouter()
        self.health_monitor = EnhancedHealthMonitor()
        self.action_tracker = AIActionTracker()
        
        # Runtime state
        self.provider_status: Dict[str, ProviderStatus] = {}
        self.switching_events: List[SwitchingEvent] = []
        self.current_budget_tier = "development"
        
        # Initialize provider status
        self._initialize_provider_status()
    
    def _load_config(self) -> Dict:
        """Load provider alternatives configuration"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        
        with open(self.config_file) as f:
            return json.load(f)
    
    def _initialize_provider_status(self):
        """Initialize provider status from health monitor"""
        dashboard = self.health_monitor.generate_dashboard_data()
        
        for provider_data in dashboard["providers"]:
            provider_name = provider_data["health"]["provider"]
            health = provider_data["health"]
            
            self.provider_status[provider_name] = ProviderStatus(
                provider=provider_name,
                available=health["status"] in ["healthy", "degraded"],
                health_score=health["availability_score"],
                current_cost_tier=self._get_provider_cost_tier(provider_name),
                last_used=None,
                failure_count=0,
                rate_limited_until=None,
                performance_score=(health["availability_score"] + health["cost_efficiency"]) / 2
            )
    
    def _get_provider_cost_tier(self, provider: str) -> str:
        """Get cost tier for a provider"""
        for tier, config in self.config["cost_tiers"].items():
            if provider in config["providers"]:
                return tier
        return "unknown"
    
    def select_optimal_provider(self, task_complexity: str, task_category: str = None,
                              max_cost: float = None, preferred_chain: str = None) -> Tuple[str, str, Dict]:
        """Select optimal provider with fallback logic"""
        
        # Determine routing strategy
        routing_config = self.config["task_routing"].get(task_complexity, 
                                                        self.config["task_routing"]["moderate"])
        
        # Use provided chain or default from routing
        chain_name = preferred_chain or routing_config["preferred_chain"]
        fallback_chain = self.config["fallback_chains"][chain_name]
        
        # Check budget constraints
        dashboard = self.health_monitor.generate_dashboard_data()
        daily_cost = dashboard["system_health"]["total_cost_today"]
        budget_limit = self.config["budget_controls"]["daily_limits"][self.current_budget_tier]
        
        # Apply switching rules
        active_rules = self._check_switching_rules(daily_cost, budget_limit)
        
        # Try providers in fallback chain order
        for chain_entry in fallback_chain["chain"]:
            provider = chain_entry["provider"]
            conditions = chain_entry["conditions"]
            
            # Check if provider is available and meets conditions
            if self._is_provider_suitable(provider, conditions, routing_config, active_rules):
                # Estimate cost for this provider
                estimated_cost = self.ai_router.estimate_cost(provider, 1000, 1000)  # Rough estimate
                
                # Check cost constraints
                max_allowed_cost = max_cost or routing_config.get("max_cost", float('inf'))
                if estimated_cost <= max_allowed_cost:
                    
                    # Record selection
                    selection_info = {
                        "chain_used": chain_name,
                        "position_in_chain": fallback_chain["chain"].index(chain_entry),
                        "conditions_met": conditions,
                        "active_rules": active_rules,
                        "estimated_cost": estimated_cost,
                        "budget_remaining": budget_limit - daily_cost if budget_limit > 0 else float('inf')
                    }
                    
                    return provider, f"selected_from_{chain_name}_chain", selection_info
        
        # If no provider in chain is suitable, emergency fallback
        emergency_provider = self._get_emergency_fallback()
        return emergency_provider, "emergency_fallback", {"reason": "no_suitable_provider_in_chain"}
    
    def _check_switching_rules(self, daily_cost: float, budget_limit: float) -> List[str]:
        """Check which switching rules are currently active"""
        active_rules = []
        
        # Budget rules
        if budget_limit > 0 and daily_cost > budget_limit:
            active_rules.append("budget_exceeded")
        elif budget_limit > 0 and daily_cost > budget_limit * 0.8:
            active_rules.append("budget_warning")
        
        # Provider health rules
        for provider, status in self.provider_status.items():
            if not status.available:
                active_rules.append(f"provider_unhealthy_{provider}")
            
            if status.rate_limited_until:
                rate_limit_time = datetime.fromisoformat(status.rate_limited_until)
                if datetime.now() < rate_limit_time:
                    active_rules.append(f"rate_limited_{provider}")
        
        return active_rules
    
    def _is_provider_suitable(self, provider: str, conditions: List[str], 
                            routing_config: Dict, active_rules: List[str]) -> bool:
        """Check if provider is suitable given current conditions"""
        
        # Check basic availability
        if provider not in self.provider_status:
            return False
        
        status = self.provider_status[provider]
        if not status.available:
            return False
        
        # Check rate limiting
        if status.rate_limited_until:
            rate_limit_time = datetime.fromisoformat(status.rate_limited_until)
            if datetime.now() < rate_limit_time:
                return False
        
        # Check budget rules
        if "budget_exceeded" in active_rules:
            provider_tier = self._get_provider_cost_tier(provider)
            if provider_tier not in ["free"]:
                return False
        
        # Check condition-specific rules
        if "always_try_first" in conditions:
            return True
        
        if "if_free_fails" in conditions:
            # Only suitable if free tier has failed
            free_providers = self.config["cost_tiers"]["free"]["providers"]
            free_failed = any(not self.provider_status.get(p, ProviderStatus("", False, 0, "", None, 0, None, 0)).available 
                            for p in free_providers)
            return free_failed
        
        # Check quality requirements
        quality_threshold = routing_config.get("quality_threshold", 0)
        provider_profile = self.config["provider_profiles"].get(provider, {})
        provider_quality = provider_profile.get("quality", 0)
        
        return provider_quality >= quality_threshold
    
    def _get_emergency_fallback(self) -> str:
        """Get emergency fallback provider"""
        # Try free providers first
        for provider in self.config["cost_tiers"]["free"]["providers"]:
            if provider in self.provider_status and self.provider_status[provider].available:
                return provider
        
        # Try any available provider
        for provider, status in self.provider_status.items():
            if status.available:
                return provider
        
        # Last resort - return first provider in config
        return list(self.config["provider_profiles"].keys())[0]
    
    def record_provider_result(self, provider: str, success: bool, cost: float, 
                             latency: float, error: str = None):
        """Record result of provider usage for adaptive switching"""
        
        if provider not in self.provider_status:
            return
        
        status = self.provider_status[provider]
        status.last_used = datetime.now().isoformat()
        
        if success:
            status.failure_count = max(0, status.failure_count - 1)  # Reduce failure count on success
            # Update performance score
            speed_score = max(0, 10 - (latency / 1000))  # 10 points minus seconds
            status.performance_score = (status.performance_score * 0.9) + (speed_score * 0.1)
        else:
            status.failure_count += 1
            
            # Check if provider should be marked as unhealthy
            if status.failure_count >= 3:
                status.available = False
                self._log_switching_event("provider_failures", provider, "none", 
                                        f"Marked unhealthy after {status.failure_count} failures")
            
            # Handle rate limiting
            if error and "rate limit" in error.lower():
                # Set rate limit for 1 hour
                status.rate_limited_until = (datetime.now() + timedelta(hours=1)).isoformat()
                self._log_switching_event("rate_limited", provider, "none", 
                                        "Rate limited for 1 hour")
    
    def _log_switching_event(self, trigger: str, from_provider: str, to_provider: str, 
                           reason: str, cost_impact: float = 0.0, success: bool = True):
        """Log a provider switching event"""
        
        event = SwitchingEvent(
            timestamp=datetime.now().isoformat(),
            trigger=trigger,
            from_provider=from_provider,
            to_provider=to_provider,
            reason=reason,
            cost_impact=cost_impact,
            success=success
        )
        
        self.switching_events.append(event)
        
        # Also log to file
        with open(self.switching_log_file, 'a') as f:
            f.write(json.dumps(asdict(event)) + '\n')
    
    def get_switching_recommendations(self) -> Dict:
        """Get current switching recommendations"""
        recommendations = {
            "immediate_actions": [],
            "cost_optimizations": [],
            "reliability_improvements": [],
            "performance_optimizations": []
        }
        
        # Check current system state
        dashboard = self.health_monitor.generate_dashboard_data()
        system_health = dashboard["system_health"]
        
        # Cost recommendations
        if system_health["total_cost_today"] > self.config["budget_controls"]["daily_limits"][self.current_budget_tier] * 0.8:
            recommendations["immediate_actions"].append({
                "action": "switch_to_cost_optimized_chain",
                "reason": "Approaching daily budget limit",
                "impact": "Reduce costs by 60-80%"
            })
        
        # Performance recommendations
        if system_health["avg_response_time"] > 5000:  # 5 seconds
            recommendations["performance_optimizations"].append({
                "action": "prioritize_faster_providers",
                "reason": "High average response time",
                "impact": "Improve response time by 40-60%"
            })
        
        # Reliability recommendations
        unhealthy_providers = [p for p, s in self.provider_status.items() if not s.available]
        if unhealthy_providers:
            recommendations["reliability_improvements"].append({
                "action": "avoid_unhealthy_providers",
                "providers": unhealthy_providers,
                "reason": "Multiple provider failures detected",
                "impact": "Improve success rate"
            })
        
        return recommendations
    
    def update_budget_tier(self, new_tier: str) -> bool:
        """Update current budget tier"""
        if new_tier not in self.config["budget_controls"]["daily_limits"]:
            return False
        
        old_tier = self.current_budget_tier
        self.current_budget_tier = new_tier
        
        self._log_switching_event("budget_tier_change", old_tier, new_tier, 
                                f"Budget tier updated to {new_tier}")
        
        return True
    
    def get_provider_analytics(self) -> Dict:
        """Get analytics on provider usage and performance"""
        analytics = {
            "provider_status": {p: asdict(s) for p, s in self.provider_status.items()},
            "switching_events_count": len(self.switching_events),
            "recent_switches": [asdict(e) for e in self.switching_events[-10:]],
            "cost_tier_distribution": {},
            "performance_rankings": [],
            "reliability_scores": {}
        }
        
        # Cost tier distribution
        for tier in self.config["cost_tiers"]:
            analytics["cost_tier_distribution"][tier] = len([
                p for p in self.provider_status 
                if self._get_provider_cost_tier(p) == tier and self.provider_status[p].available
            ])
        
        # Performance rankings
        performance_sorted = sorted(
            self.provider_status.items(),
            key=lambda x: x[1].performance_score,
            reverse=True
        )
        analytics["performance_rankings"] = [
            {"provider": p, "score": s.performance_score} 
            for p, s in performance_sorted if s.available
        ]
        
        # Reliability scores
        for provider, status in self.provider_status.items():
            reliability = max(0, 100 - (status.failure_count * 10))
            analytics["reliability_scores"][provider] = reliability
        
        return analytics

def main():
    """CLI interface for provider alternatives manager"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python provider_alternatives_manager.py <command> [args...]")
        print("Commands:")
        print("  select <complexity> [category] - Select optimal provider")
        print("  status - Show provider status")
        print("  recommendations - Get switching recommendations")
        print("  analytics - Show provider analytics")
        print("  set-budget <tier> - Set budget tier")
        return
    
    if not DEPENDENCIES_AVAILABLE:
        print("Error: Required dependencies not available")
        return
    
    manager = ProviderAlternativesManager()
    command = sys.argv[1]
    
    if command == "select":
        if len(sys.argv) < 3:
            print("Usage: select <complexity> [category]")
            return
        
        complexity = sys.argv[2]
        category = sys.argv[3] if len(sys.argv) > 3 else None
        
        provider, reason, info = manager.select_optimal_provider(complexity, category)
        result = {
            "selected_provider": provider,
            "selection_reason": reason,
            "selection_info": info
        }
        print(json.dumps(result, indent=2))
    
    elif command == "status":
        status = {p: asdict(s) for p, s in manager.provider_status.items()}
        print(json.dumps(status, indent=2))
    
    elif command == "recommendations":
        recommendations = manager.get_switching_recommendations()
        print(json.dumps(recommendations, indent=2))
    
    elif command == "analytics":
        analytics = manager.get_provider_analytics()
        print(json.dumps(analytics, indent=2))
    
    elif command == "set-budget":
        if len(sys.argv) < 3:
            print("Usage: set-budget <tier>")
            return
        
        tier = sys.argv[2]
        success = manager.update_budget_tier(tier)
        print(f"Budget tier update: {'success' if success else 'failed'}")

if __name__ == "__main__":
    main()
