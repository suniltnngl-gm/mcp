#!/usr/bin/env python3
"""Smart AI Router - Cost-optimized provider selection with automatic fallback"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

@dataclass
class ProviderCost:
    """Cost structure for AI providers"""
    name: str
    cost_per_1k_input: float
    cost_per_1k_output: float
    rate_limit: int  # requests per minute
    context_window: int
    quality_tier: str  # 'basic', 'standard', 'premium'

@dataclass
class UsageStats:
    """Track provider usage statistics"""
    provider: str
    requests: int = 0
    tokens_input: int = 0
    tokens_output: int = 0
    total_cost: float = 0.0
    failures: int = 0
    avg_latency: float = 0.0
    last_used: Optional[str] = None

class SmartAIRouter:
    """Intelligent AI provider router with cost optimization"""
    
    PROVIDERS = {
        'openrouter-free': ProviderCost('openrouter-free', 0.0, 0.0, 20, 8000, 'basic'),
        'gemini-flash': ProviderCost('gemini-flash', 0.075, 0.30, 60, 32000, 'standard'),
        'gpt-3.5': ProviderCost('gpt-3.5', 0.50, 1.50, 60, 16000, 'standard'),
        'claude-haiku': ProviderCost('claude-haiku', 0.25, 1.25, 50, 200000, 'standard'),
        'gpt-4': ProviderCost('gpt-4', 30.0, 60.0, 10, 128000, 'premium'),
        'claude-sonnet': ProviderCost('claude-sonnet', 3.0, 15.0, 40, 200000, 'premium'),
    }
    
    TASK_COMPLEXITY = {
        'simple': ['basic', 'standard'],  # Use cheap providers
        'moderate': ['standard', 'premium'],  # Prefer standard
        'complex': ['premium'],  # Only premium
    }
    
    def __init__(self, stats_file: str = 'ai_usage_stats.json', budget_daily: float = 1.0):
        self.stats_file = Path(stats_file)
        self.budget_daily = budget_daily
        self.stats: Dict[str, UsageStats] = self._load_stats()
        self.session_start = datetime.now()
    
    def _load_stats(self) -> Dict[str, UsageStats]:
        """Load usage statistics"""
        if self.stats_file.exists():
            with open(self.stats_file) as f:
                data = json.load(f)
                return {k: UsageStats(**v) for k, v in data.items()}
        return {name: UsageStats(provider=name) for name in self.PROVIDERS}
    
    def _save_stats(self):
        """Save usage statistics"""
        with open(self.stats_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.stats.items()}, f, indent=2)
    
    def estimate_cost(self, provider: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a request"""
        p = self.PROVIDERS[provider]
        return (input_tokens / 1000 * p.cost_per_1k_input + 
                output_tokens / 1000 * p.cost_per_1k_output)
    
    def get_daily_cost(self) -> float:
        """Get total cost for today"""
        today = datetime.now().date().isoformat()
        return sum(s.total_cost for s in self.stats.values() 
                  if s.last_used and s.last_used.startswith(today))
    
    def select_provider(self, task_complexity: str = 'simple', 
                       estimated_tokens: int = 1000,
                       required_context: int = 8000) -> Tuple[str, str]:
        """
        Select optimal provider based on task complexity and cost
        
        Returns: (provider_name, reason)
        """
        # Check budget
        daily_cost = self.get_daily_cost()
        if daily_cost >= self.budget_daily:
            return 'openrouter-free', 'budget_exceeded'
        
        # Filter by complexity tier
        allowed_tiers = self.TASK_COMPLEXITY.get(task_complexity, ['standard'])
        candidates = [
            (name, cost) for name, cost in self.PROVIDERS.items()
            if cost.quality_tier in allowed_tiers and cost.context_window >= required_context
        ]
        
        if not candidates:
            return 'gpt-3.5', 'fallback_default'
        
        # Sort by cost (cheapest first)
        candidates.sort(key=lambda x: x[1].cost_per_1k_input)
        
        # Check provider health (avoid if high failure rate)
        for name, cost in candidates:
            stats = self.stats[name]
            failure_rate = stats.failures / max(stats.requests, 1)
            if failure_rate < 0.3:  # Less than 30% failure rate
                return name, 'cost_optimized'
        
        # All have high failure rates, use most reliable
        best = min(self.stats.items(), key=lambda x: x[1].failures)
        return best[0], 'reliability_fallback'
    
    def get_fallback_chain(self, primary: str) -> List[str]:
        """Get fallback providers if primary fails"""
        primary_tier = self.PROVIDERS[primary].quality_tier
        
        # Same tier first, then lower tiers
        same_tier = [n for n, p in self.PROVIDERS.items() 
                    if p.quality_tier == primary_tier and n != primary]
        lower_tiers = [n for n, p in self.PROVIDERS.items() 
                      if p.quality_tier != primary_tier]
        
        return same_tier + lower_tiers
    
    def record_usage(self, provider: str, input_tokens: int, output_tokens: int, 
                    latency: float, success: bool = True):
        """Record provider usage"""
        stats = self.stats[provider]
        stats.requests += 1
        stats.tokens_input += input_tokens
        stats.tokens_output += output_tokens
        stats.total_cost += self.estimate_cost(provider, input_tokens, output_tokens)
        stats.last_used = datetime.now().isoformat()
        
        if not success:
            stats.failures += 1
        
        # Update average latency
        if stats.avg_latency == 0:
            stats.avg_latency = latency
        else:
            stats.avg_latency = (stats.avg_latency * (stats.requests - 1) + latency) / stats.requests
        
        self._save_stats()
    
    def get_recommendations(self) -> List[str]:
        """Get cost optimization recommendations"""
        recommendations = []
        daily_cost = self.get_daily_cost()
        
        if daily_cost > self.budget_daily * 0.8:
            recommendations.append(f"⚠️  Daily cost ${daily_cost:.2f} approaching budget ${self.budget_daily:.2f}")
            recommendations.append("💡 Consider using 'simple' complexity for basic tasks")
        
        # Find expensive providers being overused
        for name, stats in self.stats.items():
            if stats.requests > 0:
                provider = self.PROVIDERS[name]
                if provider.quality_tier == 'premium' and stats.requests > 10:
                    recommendations.append(f"💡 {name} used {stats.requests}x - consider cheaper alternatives")
        
        # Find providers with high failure rates
        for name, stats in self.stats.items():
            if stats.requests > 5:
                failure_rate = stats.failures / stats.requests
                if failure_rate > 0.2:
                    recommendations.append(f"⚠️  {name} has {failure_rate*100:.1f}% failure rate")
        
        return recommendations
    
    def print_stats(self):
        """Print usage statistics"""
        print("\n=== AI Provider Usage Statistics ===\n")
        print(f"Daily Budget: ${self.budget_daily:.2f}")
        print(f"Today's Cost: ${self.get_daily_cost():.2f}\n")
        
        for name, stats in sorted(self.stats.items(), key=lambda x: x[1].total_cost, reverse=True):
            if stats.requests > 0:
                provider = self.PROVIDERS[name]
                failure_rate = stats.failures / stats.requests * 100
                print(f"{name} ({provider.quality_tier}):")
                print(f"  Requests: {stats.requests} | Failures: {stats.failures} ({failure_rate:.1f}%)")
                print(f"  Tokens: {stats.tokens_input:,} in / {stats.tokens_output:,} out")
                print(f"  Cost: ${stats.total_cost:.4f} | Latency: {stats.avg_latency:.2f}s")
                print()
        
        recommendations = self.get_recommendations()
        if recommendations:
            print("=== Recommendations ===\n")
            for rec in recommendations:
                print(rec)

def main():
    """CLI interface"""
    import sys
    
    router = SmartAIRouter()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  smart_ai_router.py select <simple|moderate|complex> [tokens] [context]")
        print("  smart_ai_router.py stats")
        print("  smart_ai_router.py recommend")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'select':
        complexity = sys.argv[2] if len(sys.argv) > 2 else 'simple'
        tokens = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
        context = int(sys.argv[4]) if len(sys.argv) > 4 else 8000
        
        provider, reason = router.select_provider(complexity, tokens, context)
        print(f"Selected: {provider} (reason: {reason})")
        print(f"Fallback chain: {' → '.join(router.get_fallback_chain(provider))}")
    
    elif cmd == 'stats':
        router.print_stats()
    
    elif cmd == 'recommend':
        for rec in router.get_recommendations():
            print(rec)

if __name__ == '__main__':
    main()
