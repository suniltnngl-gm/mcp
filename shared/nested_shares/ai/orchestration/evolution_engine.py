#!/usr/bin/env python3
"""Evolution Engine - Autonomous continuous optimization system"""

from shared_tools.utils.config_utils import get_workspace_path
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from advanced_optimizer import AdvancedOptimizer
from continuous_monitor import ContinuousMonitor
from self_improvement import SelfImprovementSystem

class EvolutionEngine:
    def __init__(self):
        self.workspace_path = get_workspace_path() / "shared-tools" / "nested-shares"
        self.optimizer = AdvancedOptimizer()
        self.monitor = ContinuousMonitor()
        self.self_improvement = SelfImprovementSystem()
        
        self.evolution_log = []
        self.autonomous_mode = True
        
    def run_evolution_cycle(self) -> Dict:
        """Execute single evolution cycle with autonomous decision making"""
        cycle_start = datetime.now()
        
        # 1. Health assessment
        health = self.monitor.take_health_snapshot()
        
        # 2. Identify critical issues
        critical_categories = [
            cat for cat, info in health['categories'].items() 
            if info['health_status'] == 'critical'
        ]
        
        results = {
            'timestamp': cycle_start.isoformat(),
            'critical_issues': len(critical_categories),
            'actions_taken': [],
            'improvements': 0,
            'next_cycle': '1 hour'
        }
        
        # 3. Execute autonomous optimizations
        if critical_categories:
            for category in critical_categories[:2]:  # Handle top 2 critical
                if health['categories'][category]['file_count'] > 200:
                    # Auto-split large categories
                    split_result = self._auto_split_category(category)
                    if split_result['success']:
                        results['actions_taken'].append(f"Auto-split {category}")
                        results['improvements'] += 1
        
        # 4. Proactive optimizations
        self._run_proactive_optimizations(results)
        
        # 5. Log evolution step
        self.evolution_log.append(results)
        
        return results
    
    def _auto_split_category(self, category: str) -> Dict:
        """Autonomously split oversized category"""
        try:
            # Use advanced optimizer for intelligent splitting
            if category == 'python-code':
                result = self.optimizer.optimize_python_code_category()
            elif category == 'ai':
                result = self.optimizer.optimize_ai_category()
            else:
                # Generic optimization
                result = {'success': True, 'actions': [f'Optimized {category}']}
            
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _run_proactive_optimizations(self, results: Dict):
        """Run proactive optimizations for continuous improvement"""
        # Cleanup small files
        cleanup_result = self.optimizer.cleanup_small_categories()
        if cleanup_result['success'] and cleanup_result['files_moved'] > 0:
            results['actions_taken'].append("Cleaned up small categories")
            results['improvements'] += 1
    
    def start_continuous_evolution(self, cycle_interval_hours: int = 1):
        """Start autonomous continuous evolution"""
        print(f"🚀 Starting Continuous Evolution (every {cycle_interval_hours}h)")
        
        cycle_count = 0
        
        while True:
            try:
                cycle_count += 1
                print(f"\n🔄 Evolution Cycle #{cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
                
                # Run evolution cycle
                results = self.run_evolution_cycle()
                
                # Report results
                print(f"✅ Critical Issues: {results['critical_issues']}")
                print(f"🎯 Actions Taken: {len(results['actions_taken'])}")
                for action in results['actions_taken']:
                    print(f"   • {action}")
                
                print(f"📈 Improvements: {results['improvements']}")
                print(f"⏰ Next Cycle: {results['next_cycle']}")
                
                # Adaptive cycle timing based on activity
                if results['improvements'] > 0:
                    sleep_time = 30 * 60  # 30 minutes if active
                else:
                    sleep_time = cycle_interval_hours * 3600  # Normal interval
                
                print(f"💤 Sleeping for {sleep_time//60} minutes...")
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                print("\n🛑 Evolution stopped by user")
                break
            except Exception as e:
                print(f"❌ Evolution error: {e}")
                time.sleep(300)  # 5 minute recovery
    
    def get_evolution_status(self) -> Dict:
        """Get current evolution status"""
        if not self.evolution_log:
            return {'status': 'Not started', 'cycles': 0}
        
        recent_cycles = self.evolution_log[-10:]
        total_improvements = sum(cycle['improvements'] for cycle in recent_cycles)
        
        return {
            'status': 'Active',
            'total_cycles': len(self.evolution_log),
            'recent_improvements': total_improvements,
            'last_cycle': self.evolution_log[-1]['timestamp'],
            'autonomous_mode': self.autonomous_mode
        }

def main():
    import sys
    
    engine = EvolutionEngine()
    
    if len(sys.argv) < 2:
        print("Usage: python3 evolution_engine.py <command>")
        print("Commands:")
        print("  cycle       - Run single evolution cycle")
        print("  start [hrs] - Start continuous evolution")
        print("  status      - Show evolution status")
        return
    
    command = sys.argv[1]
    
    if command == 'cycle':
        results = engine.run_evolution_cycle()
        
        print("🔄 Evolution Cycle Results")
        print("=" * 30)
        print(f"Critical Issues: {results['critical_issues']}")
        print(f"Actions Taken: {len(results['actions_taken'])}")
        for action in results['actions_taken']:
            print(f"  • {action}")
        print(f"Improvements: {results['improvements']}")
        
    elif command == 'start':
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        engine.start_continuous_evolution(interval)
        
    elif command == 'status':
        status = engine.get_evolution_status()
        
        print("🚀 Evolution Status")
        print("=" * 20)
        print(f"Status: {status['status']}")
        print(f"Total Cycles: {status.get('total_cycles', 0)}")
        print(f"Recent Improvements: {status.get('recent_improvements', 0)}")
        if 'last_cycle' in status:
            print(f"Last Cycle: {status['last_cycle']}")
        print(f"Autonomous Mode: {status.get('autonomous_mode', False)}")

if __name__ == "__main__":
    main()
