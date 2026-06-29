#!/usr/bin/env python3
"""Smart AI Action History Tracker"""

import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict

@dataclass
class AIAction:
    id: str
    timestamp: str
    action_type: str  # 'query', 'discussion', 'decision', 'code_gen', 'review'
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    latency: float
    success: bool
    context: Dict
    result: Optional[str] = None
    error: Optional[str] = None

class AIActionTracker:
    """Track all AI actions with cost, performance, and outcomes"""
    
    def __init__(self, history_file: str = "ai_action_history.jsonl"):
        self.history_file = Path(history_file)
        self.session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    def log_action(self, action_type: str, provider: str, model: str,
                   input_tokens: int, output_tokens: int, cost: float,
                   latency: float, success: bool, context: Dict,
                   result: str = None, error: str = None) -> str:
        """Log an AI action"""
        action_id = f"{self.session_id}-{datetime.now().strftime('%H%M%S%f')}"
        
        action = AIAction(
            id=action_id,
            timestamp=datetime.now().isoformat(),
            action_type=action_type,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            latency=latency,
            success=success,
            context=context,
            result=result,
            error=error
        )
        
        # Append to JSONL file
        with open(self.history_file, 'a') as f:
            f.write(json.dumps(asdict(action)) + '\n')
        
        return action_id
    
    def get_actions(self, limit: int = 100, action_type: str = None,
                   provider: str = None, success: bool = None) -> List[AIAction]:
        """Get filtered action history"""
        if not self.history_file.exists():
            return []
        
        actions = []
        with open(self.history_file) as f:
            for line in f:
                action_dict = json.loads(line)
                action = AIAction(**action_dict)
                
                # Apply filters
                if action_type and action.action_type != action_type:
                    continue
                if provider and action.provider != provider:
                    continue
                if success is not None and action.success != success:
                    continue
                
                actions.append(action)
        
        return actions[-limit:]
    
    def get_stats(self, period: str = 'today') -> Dict:
        """Get statistics for period (today, week, month, all)"""
        actions = self.get_actions(limit=10000)
        
        if period == 'today':
            today = datetime.now().date().isoformat()
            actions = [a for a in actions if a.timestamp.startswith(today)]
        elif period == 'week':
            # Last 7 days
            from datetime import timedelta
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            actions = [a for a in actions if a.timestamp >= week_ago]
        
        if not actions:
            return {'total_actions': 0}
        
        total_cost = sum(a.cost for a in actions)
        total_tokens = sum(a.input_tokens + a.output_tokens for a in actions)
        avg_latency = sum(a.latency for a in actions) / len(actions)
        success_rate = sum(1 for a in actions if a.success) / len(actions)
        
        by_type = {}
        by_provider = {}
        
        for action in actions:
            by_type[action.action_type] = by_type.get(action.action_type, 0) + 1
            by_provider[action.provider] = by_provider.get(action.provider, 0) + 1
        
        return {
            'total_actions': len(actions),
            'total_cost': round(total_cost, 4),
            'total_tokens': total_tokens,
            'avg_latency': round(avg_latency, 2),
            'success_rate': round(success_rate * 100, 1),
            'by_type': by_type,
            'by_provider': by_provider,
            'period': period
        }
    
    def get_timeline(self, hours: int = 24) -> List[Dict]:
        """Get hourly timeline of actions"""
        from datetime import timedelta
        from collections import defaultdict
        
        actions = self.get_actions(limit=10000)
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        actions = [a for a in actions if a.timestamp >= cutoff]
        
        hourly = defaultdict(lambda: {'count': 0, 'cost': 0, 'tokens': 0})
        
        for action in actions:
            hour = action.timestamp[:13]  # YYYY-MM-DDTHH
            hourly[hour]['count'] += 1
            hourly[hour]['cost'] += action.cost
            hourly[hour]['tokens'] += action.input_tokens + action.output_tokens
        
        return [{'hour': h, **data} for h, data in sorted(hourly.items())]
    
    def find_expensive_actions(self, limit: int = 10) -> List[AIAction]:
        """Find most expensive actions"""
        actions = self.get_actions(limit=10000)
        return sorted(actions, key=lambda a: a.cost, reverse=True)[:limit]
    
    def find_slow_actions(self, limit: int = 10) -> List[AIAction]:
        """Find slowest actions"""
        actions = self.get_actions(limit=10000)
        return sorted(actions, key=lambda a: a.latency, reverse=True)[:limit]
    
    def find_failures(self, limit: int = 20) -> List[AIAction]:
        """Find recent failures"""
        return self.get_actions(limit=limit, success=False)
    
    def export_report(self, output_file: str = "ai_action_report.json"):
        """Export comprehensive report"""
        report = {
            'generated': datetime.now().isoformat(),
            'stats_today': self.get_stats('today'),
            'stats_week': self.get_stats('week'),
            'stats_all': self.get_stats('all'),
            'timeline_24h': self.get_timeline(24),
            'expensive_actions': [asdict(a) for a in self.find_expensive_actions(5)],
            'slow_actions': [asdict(a) for a in self.find_slow_actions(5)],
            'recent_failures': [asdict(a) for a in self.find_failures(10)]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return output_file

def main():
    """CLI interface"""
    import sys
    
    tracker = AIActionTracker()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  ai_action_tracker.py stats [today|week|month|all]")
        print("  ai_action_tracker.py timeline [hours]")
        print("  ai_action_tracker.py expensive [limit]")
        print("  ai_action_tracker.py slow [limit]")
        print("  ai_action_tracker.py failures [limit]")
        print("  ai_action_tracker.py report [output_file]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'stats':
        period = sys.argv[2] if len(sys.argv) > 2 else 'today'
        stats = tracker.get_stats(period)
        print(f"\n=== AI Action Stats ({period}) ===\n")
        print(f"Total actions: {stats['total_actions']}")
        print(f"Total cost: ${stats['total_cost']}")
        print(f"Total tokens: {stats['total_tokens']:,}")
        print(f"Avg latency: {stats['avg_latency']}s")
        print(f"Success rate: {stats['success_rate']}%")
        print(f"\nBy type: {stats.get('by_type', {})}")
        print(f"By provider: {stats.get('by_provider', {})}")
    
    elif cmd == 'timeline':
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        timeline = tracker.get_timeline(hours)
        print(f"\n=== Timeline (last {hours}h) ===\n")
        for entry in timeline:
            print(f"{entry['hour']}: {entry['count']} actions, ${entry['cost']:.4f}, {entry['tokens']} tokens")
    
    elif cmd == 'expensive':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        actions = tracker.find_expensive_actions(limit)
        print(f"\n=== Most Expensive Actions ===\n")
        for action in actions:
            print(f"${action.cost:.4f} - {action.action_type} via {action.provider} ({action.timestamp})")
    
    elif cmd == 'slow':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        actions = tracker.find_slow_actions(limit)
        print(f"\n=== Slowest Actions ===\n")
        for action in actions:
            print(f"{action.latency:.2f}s - {action.action_type} via {action.provider} ({action.timestamp})")
    
    elif cmd == 'failures':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        actions = tracker.find_failures(limit)
        print(f"\n=== Recent Failures ===\n")
        for action in actions:
            print(f"{action.timestamp} - {action.action_type} via {action.provider}")
            print(f"  Error: {action.error}\n")
    
    elif cmd == 'report':
        output = sys.argv[2] if len(sys.argv) > 2 else "ai_action_report.json"
        report_file = tracker.export_report(output)
        print(f"Report exported to: {report_file}")

if __name__ == '__main__':
    main()
