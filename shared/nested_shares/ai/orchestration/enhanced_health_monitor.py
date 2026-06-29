#!/usr/bin/env python3
"""Enhanced Provider Health Monitor - Real-time costs, response times, and recommendations"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

# Import existing systems
try:
    from smart_ai_router import SmartAIRouter
    from ai_action_tracker import AIActionTracker
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

@dataclass
class ProviderMetrics:
    """Real-time metrics for a provider"""
    provider: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_cost: float = 0.0
    avg_response_time: float = 0.0
    last_request_time: Optional[str] = None
    success_rate: float = 100.0
    cost_per_request: float = 0.0
    requests_per_hour: float = 0.0
    error_types: Dict[str, int] = None
    
    def __post_init__(self):
        if self.error_types is None:
            self.error_types = {}

@dataclass
class ProviderHealth:
    """Health status for a provider"""
    provider: str
    status: str  # healthy, degraded, unhealthy, offline
    last_check: str
    response_time_ms: float
    availability_score: float  # 0-100
    cost_efficiency: float  # 0-100 (lower cost = higher efficiency)
    recommendation: str
    alerts: List[str] = None
    
    def __post_init__(self):
        if self.alerts is None:
            self.alerts = []

@dataclass
class SystemHealth:
    """Overall system health summary"""
    timestamp: str
    overall_status: str  # healthy, degraded, critical
    total_providers: int
    healthy_providers: int
    total_cost_today: float
    avg_response_time: float
    system_efficiency: float
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []

class EnhancedHealthMonitor:
    """Enhanced health monitoring with real-time metrics and recommendations"""
    
    def __init__(self, storage_dir: str = "health_data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Required dependencies not available")
        
        self.ai_router = SmartAIRouter()
        self.action_tracker = AIActionTracker()
        
        # Metrics storage
        self.provider_metrics: Dict[str, ProviderMetrics] = {}
        self.health_history: deque = deque(maxlen=1000)  # Last 1000 health checks
        self.response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Load existing data
        self._load_metrics()
    
    def _load_metrics(self):
        """Load existing metrics from storage"""
        metrics_file = self.storage_dir / "provider_metrics.json"
        if metrics_file.exists():
            with open(metrics_file) as f:
                data = json.load(f)
                self.provider_metrics = {
                    k: ProviderMetrics(**v) for k, v in data.items()
                }
    
    def _save_metrics(self):
        """Save metrics to storage"""
        metrics_file = self.storage_dir / "provider_metrics.json"
        with open(metrics_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.provider_metrics.items()}, f, indent=2)
    
    def update_metrics_from_actions(self):
        """Update metrics from AI action tracker"""
        # Read recent actions from tracker
        actions_file = Path(self.action_tracker.history_file)
        if not actions_file.exists():
            return
        
        # Process recent actions (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        with open(actions_file) as f:
            for line in f:
                try:
                    action = json.loads(line.strip())
                    action_time = datetime.fromisoformat(action.get('timestamp', ''))
                    
                    if action_time < cutoff_time:
                        continue
                    
                    provider = action.get('provider', 'unknown')
                    success = action.get('success', False)
                    cost = action.get('cost', 0.0)
                    latency = action.get('latency', 0.0)
                    
                    # Update or create metrics
                    if provider not in self.provider_metrics:
                        self.provider_metrics[provider] = ProviderMetrics(provider=provider)
                    
                    metrics = self.provider_metrics[provider]
                    metrics.total_requests += 1
                    metrics.total_cost += cost
                    metrics.last_request_time = action.get('timestamp')
                    
                    if success:
                        metrics.successful_requests += 1
                    else:
                        metrics.failed_requests += 1
                        error_type = action.get('error', 'unknown_error')
                        metrics.error_types[error_type] = metrics.error_types.get(error_type, 0) + 1
                    
                    # Update response times
                    self.response_times[provider].append(latency * 1000)  # Convert to ms
                    
                    # Calculate derived metrics
                    metrics.success_rate = (metrics.successful_requests / metrics.total_requests) * 100
                    metrics.cost_per_request = metrics.total_cost / metrics.total_requests if metrics.total_requests > 0 else 0
                    metrics.avg_response_time = sum(self.response_times[provider]) / len(self.response_times[provider]) if self.response_times[provider] else 0
                    
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
        
        self._save_metrics()
    
    def check_provider_health(self, provider: str) -> ProviderHealth:
        """Check health status for a specific provider"""
        if provider not in self.provider_metrics:
            return ProviderHealth(
                provider=provider,
                status="offline",
                last_check=datetime.now().isoformat(),
                response_time_ms=0,
                availability_score=0,
                cost_efficiency=0,
                recommendation="No recent activity detected"
            )
        
        metrics = self.provider_metrics[provider]
        alerts = []
        
        # Determine status based on metrics
        status = "healthy"
        if metrics.success_rate < 50:
            status = "unhealthy"
            alerts.append(f"Low success rate: {metrics.success_rate:.1f}%")
        elif metrics.success_rate < 80:
            status = "degraded"
            alerts.append(f"Reduced success rate: {metrics.success_rate:.1f}%")
        
        if metrics.avg_response_time > 10000:  # 10 seconds
            status = "unhealthy" if status != "unhealthy" else status
            alerts.append(f"High response time: {metrics.avg_response_time:.0f}ms")
        elif metrics.avg_response_time > 5000:  # 5 seconds
            status = "degraded" if status == "healthy" else status
            alerts.append(f"Slow response time: {metrics.avg_response_time:.0f}ms")
        
        # Calculate scores
        availability_score = min(100, metrics.success_rate)
        
        # Cost efficiency (lower cost = higher efficiency)
        max_cost_per_request = 1.0  # $1 per request as baseline
        cost_efficiency = max(0, 100 - (metrics.cost_per_request / max_cost_per_request * 100))
        
        # Generate recommendation
        recommendation = self._generate_recommendation(provider, metrics, status)
        
        return ProviderHealth(
            provider=provider,
            status=status,
            last_check=datetime.now().isoformat(),
            response_time_ms=metrics.avg_response_time,
            availability_score=availability_score,
            cost_efficiency=cost_efficiency,
            recommendation=recommendation,
            alerts=alerts
        )
    
    def _generate_recommendation(self, provider: str, metrics: ProviderMetrics, status: str) -> str:
        """Generate recommendation for provider usage"""
        if status == "unhealthy":
            return f"Avoid using {provider}. Consider switching to alternative providers."
        elif status == "degraded":
            return f"Use {provider} with caution. Monitor closely or consider alternatives."
        elif metrics.cost_per_request > 0.1:  # $0.10 per request
            return f"{provider} is expensive. Consider using for complex tasks only."
        elif metrics.avg_response_time < 1000 and metrics.success_rate > 95:
            return f"{provider} is performing excellently. Recommended for frequent use."
        else:
            return f"{provider} is performing well. Safe to use for regular tasks."
    
    def get_system_health(self) -> SystemHealth:
        """Get overall system health summary"""
        self.update_metrics_from_actions()
        
        provider_healths = []
        total_cost_today = 0
        response_times = []
        
        for provider in self.provider_metrics:
            health = self.check_provider_health(provider)
            provider_healths.append(health)
            
            metrics = self.provider_metrics[provider]
            # Calculate today's cost (simplified - using all cost for now)
            total_cost_today += metrics.total_cost
            
            if metrics.avg_response_time > 0:
                response_times.append(metrics.avg_response_time)
        
        # Calculate system metrics
        total_providers = len(provider_healths)
        healthy_providers = sum(1 for h in provider_healths if h.status == "healthy")
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Determine overall status
        if healthy_providers == 0:
            overall_status = "critical"
        elif healthy_providers / total_providers < 0.5:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        # Calculate system efficiency (combination of cost and performance)
        avg_cost_efficiency = sum(h.cost_efficiency for h in provider_healths) / len(provider_healths) if provider_healths else 0
        avg_availability = sum(h.availability_score for h in provider_healths) / len(provider_healths) if provider_healths else 0
        system_efficiency = (avg_cost_efficiency + avg_availability) / 2
        
        # Generate system recommendations
        recommendations = self._generate_system_recommendations(provider_healths, total_cost_today)
        
        return SystemHealth(
            timestamp=datetime.now().isoformat(),
            overall_status=overall_status,
            total_providers=total_providers,
            healthy_providers=healthy_providers,
            total_cost_today=total_cost_today,
            avg_response_time=avg_response_time,
            system_efficiency=system_efficiency,
            recommendations=recommendations
        )
    
    def _generate_system_recommendations(self, provider_healths: List[ProviderHealth], 
                                       total_cost: float) -> List[str]:
        """Generate system-wide recommendations"""
        recommendations = []
        
        # Cost recommendations
        if total_cost > 10.0:  # $10 daily threshold
            recommendations.append("Daily cost is high. Consider using cheaper providers for simple tasks.")
        
        # Performance recommendations
        unhealthy_providers = [h for h in provider_healths if h.status == "unhealthy"]
        if unhealthy_providers:
            recommendations.append(f"Avoid these unhealthy providers: {', '.join(h.provider for h in unhealthy_providers)}")
        
        # Efficiency recommendations
        best_providers = sorted(provider_healths, 
                              key=lambda h: (h.availability_score + h.cost_efficiency) / 2, 
                              reverse=True)[:3]
        if best_providers:
            recommendations.append(f"Best performing providers: {', '.join(h.provider for h in best_providers)}")
        
        return recommendations
    
    def get_provider_recommendations(self) -> Dict[str, str]:
        """Get switching recommendations for each provider"""
        recommendations = {}
        
        for provider in self.provider_metrics:
            health = self.check_provider_health(provider)
            
            if health.status == "unhealthy":
                # Find best alternative
                alternatives = self._find_alternatives(provider)
                recommendations[provider] = f"Switch to: {alternatives[0] if alternatives else 'any healthy provider'}"
            elif health.cost_efficiency < 30:  # Low cost efficiency
                cheaper_alternatives = self._find_cheaper_alternatives(provider)
                if cheaper_alternatives:
                    recommendations[provider] = f"Consider cheaper option: {cheaper_alternatives[0]}"
        
        return recommendations
    
    def _find_alternatives(self, provider: str) -> List[str]:
        """Find healthy alternatives to a provider"""
        alternatives = []
        
        for alt_provider in self.provider_metrics:
            if alt_provider != provider:
                health = self.check_provider_health(alt_provider)
                if health.status == "healthy":
                    alternatives.append(alt_provider)
        
        # Sort by performance score
        alternatives.sort(key=lambda p: self.check_provider_health(p).availability_score, reverse=True)
        return alternatives
    
    def _find_cheaper_alternatives(self, provider: str) -> List[str]:
        """Find cheaper alternatives to a provider"""
        current_metrics = self.provider_metrics.get(provider)
        if not current_metrics:
            return []
        
        cheaper = []
        for alt_provider, alt_metrics in self.provider_metrics.items():
            if (alt_provider != provider and 
                alt_metrics.cost_per_request < current_metrics.cost_per_request and
                alt_metrics.success_rate > 80):
                cheaper.append(alt_provider)
        
        # Sort by cost efficiency
        cheaper.sort(key=lambda p: self.provider_metrics[p].cost_per_request)
        return cheaper
    
    def generate_dashboard_data(self) -> Dict:
        """Generate comprehensive dashboard data"""
        system_health = self.get_system_health()
        provider_healths = []
        
        for provider in self.provider_metrics:
            health = self.check_provider_health(provider)
            metrics = self.provider_metrics[provider]
            
            provider_data = {
                "health": asdict(health),
                "metrics": asdict(metrics),
                "recent_response_times": list(self.response_times.get(provider, []))[-10:]  # Last 10
            }
            provider_healths.append(provider_data)
        
        return {
            "system_health": asdict(system_health),
            "providers": provider_healths,
            "recommendations": self.get_provider_recommendations(),
            "generated_at": datetime.now().isoformat()
        }

def main():
    """CLI interface for health monitoring"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_health_monitor.py <command>")
        print("Commands:")
        print("  dashboard - Show complete dashboard")
        print("  system - Show system health")
        print("  provider <name> - Show specific provider health")
        print("  recommendations - Show switching recommendations")
        print("  update - Update metrics from action tracker")
        return
    
    if not DEPENDENCIES_AVAILABLE:
        print("Error: Required dependencies not available")
        return
    
    monitor = EnhancedHealthMonitor()
    command = sys.argv[1]
    
    if command == "dashboard":
        dashboard = monitor.generate_dashboard_data()
        print(json.dumps(dashboard, indent=2))
    
    elif command == "system":
        system_health = monitor.get_system_health()
        print(json.dumps(asdict(system_health), indent=2))
    
    elif command == "provider":
        if len(sys.argv) < 3:
            print("Usage: provider <name>")
            return
        provider_name = sys.argv[2]
        health = monitor.check_provider_health(provider_name)
        print(json.dumps(asdict(health), indent=2))
    
    elif command == "recommendations":
        recommendations = monitor.get_provider_recommendations()
        print(json.dumps(recommendations, indent=2))
    
    elif command == "update":
        monitor.update_metrics_from_actions()
        print("Metrics updated from action tracker")

if __name__ == "__main__":
    main()
