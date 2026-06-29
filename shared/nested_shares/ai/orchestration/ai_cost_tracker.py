#!/usr/bin/env python3
"""AI Cost Tracker - Monitor spending, send alerts, and suggest optimizations"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict

# Import existing systems
try:
    from enhanced_health_monitor import EnhancedHealthMonitor
    from provider_alternatives_manager import ProviderAlternativesManager
    from ai_action_tracker import AIActionTracker
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

@dataclass
class CostAlert:
    """Cost alert notification"""
    alert_id: str
    timestamp: str
    alert_type: str  # warning, critical, budget_exceeded
    threshold: float
    current_amount: float
    period: str  # daily, monthly
    message: str
    suggested_actions: List[str]
    acknowledged: bool = False

@dataclass
class SpendingPeriod:
    """Spending data for a time period"""
    period_id: str
    start_date: str
    end_date: str
    total_cost: float
    request_count: int
    provider_breakdown: Dict[str, float]
    category_breakdown: Dict[str, float]
    avg_cost_per_request: float

@dataclass
class BudgetConfig:
    """Budget configuration"""
    daily_limit: float
    monthly_limit: float
    warning_threshold: float  # 0.8 = 80%
    critical_threshold: float  # 0.95 = 95%
    auto_actions_enabled: bool
    notification_email: Optional[str] = None

class AICostTracker:
    """Comprehensive AI cost tracking and budget management"""
    
    def __init__(self, storage_dir: str = "cost_tracking_data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Storage files
        self.alerts_file = self.storage_dir / "cost_alerts.json"
        self.spending_file = self.storage_dir / "spending_history.json"
        self.budget_file = self.storage_dir / "budget_config.json"
        
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Required dependencies not available")
        
        # Initialize systems
        self.health_monitor = EnhancedHealthMonitor()
        self.alternatives_manager = ProviderAlternativesManager()
        self.action_tracker = AIActionTracker()
        
        # Load data
        self.alerts: List[CostAlert] = self._load_alerts()
        self.spending_history: List[SpendingPeriod] = self._load_spending_history()
        self.budget_config = self._load_budget_config()
        
        # Runtime tracking
        self.current_daily_cost = 0.0
        self.current_monthly_cost = 0.0
        self._update_current_costs()
    
    def _load_alerts(self) -> List[CostAlert]:
        """Load cost alerts from storage"""
        if self.alerts_file.exists():
            with open(self.alerts_file) as f:
                data = json.load(f)
                return [CostAlert(**alert) for alert in data]
        return []
    
    def _save_alerts(self):
        """Save cost alerts to storage"""
        with open(self.alerts_file, 'w') as f:
            json.dump([asdict(alert) for alert in self.alerts], f, indent=2)
    
    def _load_spending_history(self) -> List[SpendingPeriod]:
        """Load spending history from storage"""
        if self.spending_file.exists():
            with open(self.spending_file) as f:
                data = json.load(f)
                return [SpendingPeriod(**period) for period in data]
        return []
    
    def _save_spending_history(self):
        """Save spending history to storage"""
        with open(self.spending_file, 'w') as f:
            json.dump([asdict(period) for period in self.spending_history], f, indent=2)
    
    def _load_budget_config(self) -> BudgetConfig:
        """Load budget configuration"""
        default_config = BudgetConfig(
            daily_limit=5.0,
            monthly_limit=100.0,
            warning_threshold=0.8,
            critical_threshold=0.95,
            auto_actions_enabled=True
        )
        
        if self.budget_file.exists():
            with open(self.budget_file) as f:
                data = json.load(f)
                return BudgetConfig(**data)
        
        return default_config
    
    def _save_budget_config(self):
        """Save budget configuration"""
        with open(self.budget_file, 'w') as f:
            json.dump(asdict(self.budget_config), f, indent=2)
    
    def _update_current_costs(self):
        """Update current daily and monthly costs from health monitor"""
        dashboard = self.health_monitor.generate_dashboard_data()
        self.current_daily_cost = dashboard["system_health"]["total_cost_today"]
        
        # Calculate monthly cost from spending history
        current_month = datetime.now().strftime("%Y-%m")
        monthly_periods = [p for p in self.spending_history if p.period_id.startswith(current_month)]
        self.current_monthly_cost = sum(p.total_cost for p in monthly_periods)
    
    def check_budget_status(self) -> Dict:
        """Check current budget status and generate alerts if needed"""
        self._update_current_costs()
        
        status = {
            "daily": {
                "current": self.current_daily_cost,
                "limit": self.budget_config.daily_limit,
                "percentage": (self.current_daily_cost / self.budget_config.daily_limit * 100) if self.budget_config.daily_limit > 0 else 0,
                "status": "ok"
            },
            "monthly": {
                "current": self.current_monthly_cost,
                "limit": self.budget_config.monthly_limit,
                "percentage": (self.current_monthly_cost / self.budget_config.monthly_limit * 100) if self.budget_config.monthly_limit > 0 else 0,
                "status": "ok"
            },
            "alerts_generated": []
        }
        
        # Check daily budget
        if self.budget_config.daily_limit > 0:
            daily_percentage = status["daily"]["percentage"] / 100
            
            if daily_percentage >= 1.0:
                status["daily"]["status"] = "exceeded"
                alert = self._create_alert("budget_exceeded", self.budget_config.daily_limit, 
                                         self.current_daily_cost, "daily")
                status["alerts_generated"].append(asdict(alert))
            elif daily_percentage >= self.budget_config.critical_threshold:
                status["daily"]["status"] = "critical"
                alert = self._create_alert("critical", self.budget_config.daily_limit, 
                                         self.current_daily_cost, "daily")
                status["alerts_generated"].append(asdict(alert))
            elif daily_percentage >= self.budget_config.warning_threshold:
                status["daily"]["status"] = "warning"
                alert = self._create_alert("warning", self.budget_config.daily_limit, 
                                         self.current_daily_cost, "daily")
                status["alerts_generated"].append(asdict(alert))
        
        # Check monthly budget
        if self.budget_config.monthly_limit > 0:
            monthly_percentage = status["monthly"]["percentage"] / 100
            
            if monthly_percentage >= 1.0:
                status["monthly"]["status"] = "exceeded"
                alert = self._create_alert("budget_exceeded", self.budget_config.monthly_limit, 
                                         self.current_monthly_cost, "monthly")
                status["alerts_generated"].append(asdict(alert))
            elif monthly_percentage >= self.budget_config.critical_threshold:
                status["monthly"]["status"] = "critical"
                alert = self._create_alert("critical", self.budget_config.monthly_limit, 
                                         self.current_monthly_cost, "monthly")
                status["alerts_generated"].append(asdict(alert))
            elif monthly_percentage >= self.budget_config.warning_threshold:
                status["monthly"]["status"] = "warning"
                alert = self._create_alert("warning", self.budget_config.monthly_limit, 
                                         self.current_monthly_cost, "monthly")
                status["alerts_generated"].append(asdict(alert))
        
        return status
    
    def _create_alert(self, alert_type: str, threshold: float, current: float, period: str) -> CostAlert:
        """Create a cost alert"""
        alert_id = f"alert_{int(time.time())}"
        
        messages = {
            "warning": f"{period.title()} spending at {current/threshold*100:.1f}% of budget",
            "critical": f"{period.title()} spending critically high at {current/threshold*100:.1f}% of budget",
            "budget_exceeded": f"{period.title()} budget exceeded: ${current:.2f} > ${threshold:.2f}"
        }
        
        suggested_actions = self._get_cost_reduction_suggestions(alert_type, period)
        
        alert = CostAlert(
            alert_id=alert_id,
            timestamp=datetime.now().isoformat(),
            alert_type=alert_type,
            threshold=threshold,
            current_amount=current,
            period=period,
            message=messages.get(alert_type, f"{period.title()} budget alert"),
            suggested_actions=suggested_actions
        )
        
        # Add to alerts list
        self.alerts.append(alert)
        self._save_alerts()
        
        # Execute auto-actions if enabled
        if self.budget_config.auto_actions_enabled:
            self._execute_auto_actions(alert)
        
        return alert
    
    def _get_cost_reduction_suggestions(self, alert_type: str, period: str) -> List[str]:
        """Get cost reduction suggestions based on alert type"""
        suggestions = []
        
        if alert_type in ["warning", "critical"]:
            suggestions.extend([
                "Switch to cost-optimized provider chain",
                "Use free providers for simple tasks",
                "Reduce batch processing frequency",
                "Review and optimize expensive operations"
            ])
        
        if alert_type == "budget_exceeded":
            suggestions.extend([
                "Immediately switch to free-tier providers only",
                "Pause non-critical AI operations",
                "Review recent high-cost activities",
                "Consider increasing budget limits if justified"
            ])
        
        # Add provider-specific suggestions
        analytics = self.alternatives_manager.get_provider_analytics()
        expensive_providers = [
            p["provider"] for p in analytics["performance_rankings"][-2:]  # Bottom 2 by performance
        ]
        
        if expensive_providers:
            suggestions.append(f"Avoid expensive providers: {', '.join(expensive_providers)}")
        
        return suggestions
    
    def _execute_auto_actions(self, alert: CostAlert):
        """Execute automatic actions based on alert type"""
        if alert.alert_type == "budget_exceeded":
            # Switch to free tier
            self.alternatives_manager.update_budget_tier("free_tier")
            
        elif alert.alert_type == "critical":
            # Switch to development tier (lower cost)
            self.alternatives_manager.update_budget_tier("development")
    
    def get_spending_analysis(self, days: int = 30) -> Dict:
        """Get detailed spending analysis for the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get recent spending periods
        recent_periods = [
            p for p in self.spending_history 
            if datetime.fromisoformat(p.start_date) >= cutoff_date
        ]
        
        if not recent_periods:
            return {"error": "No spending data available for the specified period"}
        
        # Aggregate data
        total_cost = sum(p.total_cost for p in recent_periods)
        total_requests = sum(p.request_count for p in recent_periods)
        
        # Provider breakdown
        provider_costs = defaultdict(float)
        for period in recent_periods:
            for provider, cost in period.provider_breakdown.items():
                provider_costs[provider] += cost
        
        # Category breakdown
        category_costs = defaultdict(float)
        for period in recent_periods:
            for category, cost in period.category_breakdown.items():
                category_costs[category] += cost
        
        # Daily average
        daily_average = total_cost / days if days > 0 else 0
        
        # Cost trends
        daily_costs = []
        for i in range(days):
            day = datetime.now() - timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            day_periods = [p for p in recent_periods if p.period_id.startswith(day_str)]
            day_cost = sum(p.total_cost for p in day_periods)
            daily_costs.append({"date": day_str, "cost": day_cost})
        
        return {
            "period_days": days,
            "total_cost": total_cost,
            "total_requests": total_requests,
            "avg_cost_per_request": total_cost / total_requests if total_requests > 0 else 0,
            "daily_average": daily_average,
            "provider_breakdown": dict(sorted(provider_costs.items(), key=lambda x: x[1], reverse=True)),
            "category_breakdown": dict(sorted(category_costs.items(), key=lambda x: x[1], reverse=True)),
            "daily_trend": daily_costs[-7:],  # Last 7 days
            "cost_efficiency_score": self._calculate_efficiency_score(recent_periods)
        }
    
    def _calculate_efficiency_score(self, periods: List[SpendingPeriod]) -> float:
        """Calculate cost efficiency score (0-100)"""
        if not periods:
            return 0.0
        
        # Base score on cost per request and provider mix
        avg_cost_per_request = sum(p.avg_cost_per_request for p in periods) / len(periods)
        
        # Lower cost per request = higher efficiency
        efficiency = max(0, 100 - (avg_cost_per_request * 100))
        
        return min(100, efficiency)
    
    def get_optimization_recommendations(self) -> Dict:
        """Get comprehensive cost optimization recommendations"""
        analysis = self.get_spending_analysis()
        
        recommendations = {
            "immediate_actions": [],
            "provider_optimizations": [],
            "usage_optimizations": [],
            "budget_adjustments": []
        }
        
        # Immediate actions based on current spending
        if self.current_daily_cost > self.budget_config.daily_limit * 0.8:
            recommendations["immediate_actions"].extend([
                "Switch to cost-optimized provider chain",
                "Review recent expensive operations",
                "Consider pausing non-critical tasks"
            ])
        
        # Provider optimizations
        if "provider_breakdown" in analysis:
            most_expensive = max(analysis["provider_breakdown"].items(), key=lambda x: x[1])
            if most_expensive[1] > analysis["total_cost"] * 0.5:  # >50% of total cost
                recommendations["provider_optimizations"].append(
                    f"Provider '{most_expensive[0]}' accounts for {most_expensive[1]/analysis['total_cost']*100:.1f}% of costs - consider alternatives"
                )
        
        # Usage optimizations
        if "avg_cost_per_request" in analysis and analysis["avg_cost_per_request"] > 1.0:  # $1 per request
            recommendations["usage_optimizations"].extend([
                "High cost per request detected - review task complexity classification",
                "Consider batch processing for similar tasks",
                "Implement caching for repeated operations"
            ])
        
        # Budget adjustments
        if self.current_monthly_cost > self.budget_config.monthly_limit * 0.9:
            recommendations["budget_adjustments"].append(
                "Consider increasing monthly budget limit or implementing stricter controls"
            )
        
        return recommendations
    
    def update_budget_config(self, daily_limit: float = None, monthly_limit: float = None,
                           warning_threshold: float = None, critical_threshold: float = None,
                           auto_actions: bool = None) -> bool:
        """Update budget configuration"""
        if daily_limit is not None:
            self.budget_config.daily_limit = daily_limit
        if monthly_limit is not None:
            self.budget_config.monthly_limit = monthly_limit
        if warning_threshold is not None:
            self.budget_config.warning_threshold = warning_threshold
        if critical_threshold is not None:
            self.budget_config.critical_threshold = critical_threshold
        if auto_actions is not None:
            self.budget_config.auto_actions_enabled = auto_actions
        
        self._save_budget_config()
        return True
    
    def get_active_alerts(self) -> List[CostAlert]:
        """Get unacknowledged alerts from the last 24 hours"""
        cutoff = datetime.now() - timedelta(hours=24)
        
        return [
            alert for alert in self.alerts
            if not alert.acknowledged and datetime.fromisoformat(alert.timestamp) >= cutoff
        ]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge a cost alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                self._save_alerts()
                return True
        return False
    
    def generate_cost_report(self) -> Dict:
        """Generate comprehensive cost report"""
        budget_status = self.check_budget_status()
        spending_analysis = self.get_spending_analysis()
        recommendations = self.get_optimization_recommendations()
        active_alerts = self.get_active_alerts()
        
        return {
            "report_timestamp": datetime.now().isoformat(),
            "budget_status": budget_status,
            "spending_analysis": spending_analysis,
            "optimization_recommendations": recommendations,
            "active_alerts": [asdict(alert) for alert in active_alerts],
            "budget_config": asdict(self.budget_config),
            "summary": {
                "daily_budget_usage": f"{budget_status['daily']['percentage']:.1f}%",
                "monthly_budget_usage": f"{budget_status['monthly']['percentage']:.1f}%",
                "cost_efficiency_score": spending_analysis.get("cost_efficiency_score", 0),
                "alerts_count": len(active_alerts)
            }
        }

def main():
    """CLI interface for AI cost tracker"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ai_cost_tracker.py <command> [args...]")
        print("Commands:")
        print("  status - Check budget status")
        print("  analysis [days] - Get spending analysis")
        print("  recommendations - Get optimization recommendations")
        print("  alerts - Show active alerts")
        print("  report - Generate comprehensive report")
        print("  config <daily> <monthly> - Update budget limits")
        return
    
    if not DEPENDENCIES_AVAILABLE:
        print("Error: Required dependencies not available")
        return
    
    tracker = AICostTracker()
    command = sys.argv[1]
    
    if command == "status":
        status = tracker.check_budget_status()
        print(json.dumps(status, indent=2))
    
    elif command == "analysis":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        analysis = tracker.get_spending_analysis(days)
        print(json.dumps(analysis, indent=2))
    
    elif command == "recommendations":
        recommendations = tracker.get_optimization_recommendations()
        print(json.dumps(recommendations, indent=2))
    
    elif command == "alerts":
        alerts = tracker.get_active_alerts()
        print(json.dumps([asdict(alert) for alert in alerts], indent=2))
    
    elif command == "report":
        report = tracker.generate_cost_report()
        print(json.dumps(report, indent=2))
    
    elif command == "config":
        if len(sys.argv) < 4:
            print("Usage: config <daily_limit> <monthly_limit>")
            return
        
        daily = float(sys.argv[2])
        monthly = float(sys.argv[3])
        success = tracker.update_budget_config(daily_limit=daily, monthly_limit=monthly)
        print(f"Budget config updated: {'success' if success else 'failed'}")

if __name__ == "__main__":
    main()
