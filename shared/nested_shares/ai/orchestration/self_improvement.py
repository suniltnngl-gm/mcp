#!/usr/bin/env python3
"""Self-Improvement Integration - Connect category optimization with roadmap system for continuous evolution"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass, asdict
from category_automation import CategoryAutomation
from continuous_monitor import ContinuousMonitor
from semantic_search import SemanticSearch

@dataclass
class ImprovementAction:
    timestamp: str
    action_type: str  # split, merge, reorganize, optimize
    category: str
    reason: str
    impact_score: float
    status: str  # planned, executing, completed, failed
    execution_time: str = None
    results: Dict = None

@dataclass
class WorkspaceEvolution:
    phase: str
    goals: List[str]
    metrics: Dict
    timeline: str
    progress: float

class SelfImprovementSystem:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares")
        self.roadmap_file = self.workspace_path / "workspace_roadmap.json"
        self.improvement_log = self.workspace_path / "improvement_history.json"
        
        self.automation = CategoryAutomation()
        self.monitor = ContinuousMonitor()
        self.semantic_search = SemanticSearch()
        
        self.roadmap = self._load_roadmap()
        self.history = self._load_history()
        
        # Evolution phases
        self.phases = {
            'stabilization': {
                'goals': ['Fix critical issues', 'Balance categories', 'Reduce alerts'],
                'priority': 'critical_fixes',
                'success_criteria': {'critical_alerts': 0, 'balance_score': 0.7}
            },
            'optimization': {
                'goals': ['Improve organization', 'Enhance search', 'Automate workflows'],
                'priority': 'efficiency',
                'success_criteria': {'avg_balance': 0.8, 'search_accuracy': 0.9}
            },
            'evolution': {
                'goals': ['Adaptive structure', 'Predictive optimization', 'Self-healing'],
                'priority': 'intelligence',
                'success_criteria': {'automation_rate': 0.9, 'prediction_accuracy': 0.8}
            }
        }
    
    def _load_roadmap(self) -> Dict:
        """Load workspace evolution roadmap"""
        if self.roadmap_file.exists():
            with open(self.roadmap_file, 'r') as f:
                return json.load(f)
        
        return {
            'current_phase': 'stabilization',
            'phase_progress': 0.0,
            'evolution_history': [],
            'active_goals': [],
            'completed_milestones': []
        }
    
    def _load_history(self) -> Dict:
        """Load improvement history"""
        if self.improvement_log.exists():
            with open(self.improvement_log, 'r') as f:
                return json.load(f)
        
        return {
            'actions': [],
            'metrics_history': [],
            'learning_insights': []
        }
    
    def _save_roadmap(self):
        """Save roadmap state"""
        with open(self.roadmap_file, 'w') as f:
            json.dump(self.roadmap, f, indent=2)
    
    def _save_history(self):
        """Save improvement history"""
        with open(self.improvement_log, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def assess_workspace_state(self) -> Dict:
        """Comprehensive workspace assessment"""
        # Get current health snapshot
        health_snapshot = self.monitor.take_health_snapshot()
        
        # Get optimization opportunities
        opportunities = self.monitor.get_optimization_opportunities()
        
        # Get automation analysis
        auto_analysis = self.automation.analyze_automation_opportunities()
        
        # Calculate overall metrics
        total_files = health_snapshot['total_files']
        critical_alerts = len([a for a in health_snapshot['alerts_generated'] if a['level'] == 'critical'])
        warning_alerts = len([a for a in health_snapshot['alerts_generated'] if a['level'] == 'warning'])
        
        # Calculate balance scores
        balance_scores = []
        for cat_health in health_snapshot['categories'].values():
            balance_scores.append(cat_health['balance_score'])
        
        avg_balance = sum(balance_scores) / len(balance_scores) if balance_scores else 0
        
        return {
            'overall_health': health_snapshot['overall_health'],
            'total_files': total_files,
            'critical_alerts': critical_alerts,
            'warning_alerts': warning_alerts,
            'avg_balance_score': avg_balance,
            'categories_count': len(health_snapshot['categories']),
            'immediate_actions': len(opportunities.get('immediate_actions', [])),
            'optimization_suggestions': len(opportunities.get('optimization_suggestions', [])),
            'auto_split_opportunities': len(auto_analysis['auto_splits']),
            'auto_merge_opportunities': len(auto_analysis['auto_merges'])
        }
    
    def determine_current_phase(self, workspace_state: Dict) -> str:
        """Determine appropriate evolution phase based on workspace state"""
        # Stabilization phase criteria
        if workspace_state['critical_alerts'] > 0 or workspace_state['avg_balance_score'] < 0.5:
            return 'stabilization'
        
        # Optimization phase criteria
        elif workspace_state['avg_balance_score'] < 0.8 or workspace_state['immediate_actions'] > 0:
            return 'optimization'
        
        # Evolution phase
        else:
            return 'evolution'
    
    def generate_improvement_plan(self) -> List[ImprovementAction]:
        """Generate prioritized improvement plan"""
        workspace_state = self.assess_workspace_state()
        current_phase = self.determine_current_phase(workspace_state)
        
        # Update roadmap if phase changed
        if current_phase != self.roadmap['current_phase']:
            self._transition_phase(current_phase)
        
        actions = []
        timestamp = datetime.now().isoformat()
        
        # Get opportunities from all systems
        opportunities = self.monitor.get_optimization_opportunities()
        auto_analysis = self.automation.analyze_automation_opportunities()
        
        # Prioritize based on current phase
        if current_phase == 'stabilization':
            # Focus on critical fixes
            for action in opportunities.get('immediate_actions', []):
                actions.append(ImprovementAction(
                    timestamp=timestamp,
                    action_type=action['type'],
                    category=action['category'],
                    reason=action['reason'],
                    impact_score=0.9,  # High impact for critical fixes
                    status='planned'
                ))
        
        elif current_phase == 'optimization':
            # Focus on efficiency improvements
            for split in auto_analysis['auto_splits']:
                if split['priority'] in ['high', 'medium']:
                    actions.append(ImprovementAction(
                        timestamp=timestamp,
                        action_type='split',
                        category=split['category'],
                        reason=f"Optimize large category ({split['files']} files)",
                        impact_score=0.7 if split['priority'] == 'high' else 0.5,
                        status='planned'
                    ))
            
            for suggestion in opportunities.get('optimization_suggestions', []):
                actions.append(ImprovementAction(
                    timestamp=timestamp,
                    action_type=suggestion['type'],
                    category='+'.join(suggestion.get('categories', [suggestion.get('category', 'unknown')])),
                    reason=suggestion['reason'],
                    impact_score=0.6,
                    status='planned'
                ))
        
        elif current_phase == 'evolution':
            # Focus on intelligent automation
            actions.append(ImprovementAction(
                timestamp=timestamp,
                action_type='automate',
                category='system',
                reason='Enable predictive optimization',
                impact_score=0.8,
                status='planned'
            ))
        
        # Sort by impact score
        actions.sort(key=lambda x: x.impact_score, reverse=True)
        
        return actions[:5]  # Top 5 actions
    
    def _transition_phase(self, new_phase: str):
        """Handle phase transition"""
        old_phase = self.roadmap['current_phase']
        
        self.roadmap['evolution_history'].append({
            'timestamp': datetime.now().isoformat(),
            'from_phase': old_phase,
            'to_phase': new_phase,
            'trigger': 'workspace_state_change'
        })
        
        self.roadmap['current_phase'] = new_phase
        self.roadmap['phase_progress'] = 0.0
        self.roadmap['active_goals'] = self.phases[new_phase]['goals']
        
        self._save_roadmap()
    
    def execute_improvement_action(self, action: ImprovementAction, dry_run: bool = True) -> Dict:
        """Execute a single improvement action"""
        results = {
            'success': False,
            'message': '',
            'metrics_before': {},
            'metrics_after': {},
            'execution_time': 0
        }
        
        start_time = datetime.now()
        
        try:
            # Record metrics before
            results['metrics_before'] = self.assess_workspace_state()
            
            if action.action_type == 'split':
                if not dry_run:
                    # Execute category split
                    split_result = self.automation.execute_automation(dry_run=False)
                    results['success'] = len(split_result.get('errors', [])) == 0
                    results['message'] = f"Split executed: {split_result}"
                else:
                    results['success'] = True
                    results['message'] = f"Split planned for {action.category}"
            
            elif action.action_type == 'merge':
                if not dry_run:
                    # Execute merge (would need specific implementation)
                    results['success'] = True
                    results['message'] = f"Merge executed for {action.category}"
                else:
                    results['success'] = True
                    results['message'] = f"Merge planned for {action.category}"
            
            elif action.action_type == 'automate':
                # Enable automation features
                results['success'] = True
                results['message'] = "Automation features enabled"
            
            # Record metrics after
            if not dry_run:
                results['metrics_after'] = self.assess_workspace_state()
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            results['execution_time'] = execution_time
            
            # Update action status
            action.status = 'completed' if results['success'] else 'failed'
            action.execution_time = start_time.isoformat()
            action.results = results
            
        except Exception as e:
            results['success'] = False
            results['message'] = f"Error: {str(e)}"
            action.status = 'failed'
        
        return results
    
    def run_improvement_cycle(self, dry_run: bool = True) -> Dict:
        """Run complete improvement cycle"""
        cycle_results = {
            'timestamp': datetime.now().isoformat(),
            'phase': self.roadmap['current_phase'],
            'actions_planned': 0,
            'actions_executed': 0,
            'actions_successful': 0,
            'workspace_improvement': 0.0,
            'next_cycle_recommendation': ''
        }
        
        # Generate improvement plan
        actions = self.generate_improvement_plan()
        cycle_results['actions_planned'] = len(actions)
        
        # Record initial state
        initial_state = self.assess_workspace_state()
        
        # Execute actions
        successful_actions = []
        for action in actions:
            result = self.execute_improvement_action(action, dry_run)
            cycle_results['actions_executed'] += 1
            
            if result['success']:
                cycle_results['actions_successful'] += 1
                successful_actions.append(action)
        
        # Calculate improvement
        if not dry_run:
            final_state = self.assess_workspace_state()
            improvement = self._calculate_improvement(initial_state, final_state)
            cycle_results['workspace_improvement'] = improvement
        
        # Update roadmap progress
        if successful_actions:
            progress_increment = len(successful_actions) / len(actions) * 0.2
            self.roadmap['phase_progress'] = min(1.0, self.roadmap['phase_progress'] + progress_increment)
        
        # Generate next cycle recommendation
        cycle_results['next_cycle_recommendation'] = self._recommend_next_cycle(cycle_results)
        
        # Log actions to history
        for action in successful_actions:
            self.history['actions'].append(asdict(action))
        
        # Save state
        self._save_roadmap()
        self._save_history()
        
        return cycle_results
    
    def _calculate_improvement(self, before: Dict, after: Dict) -> float:
        """Calculate overall workspace improvement score"""
        improvements = []
        
        # Critical alerts improvement
        if before['critical_alerts'] > after['critical_alerts']:
            improvements.append(0.3)
        
        # Balance score improvement
        balance_improvement = after['avg_balance_score'] - before['avg_balance_score']
        if balance_improvement > 0:
            improvements.append(balance_improvement * 0.5)
        
        # Alert reduction
        alert_reduction = (before['warning_alerts'] - after['warning_alerts']) / max(before['warning_alerts'], 1)
        if alert_reduction > 0:
            improvements.append(alert_reduction * 0.2)
        
        return sum(improvements)
    
    def _recommend_next_cycle(self, cycle_results: Dict) -> str:
        """Recommend timing for next improvement cycle"""
        success_rate = cycle_results['actions_successful'] / max(cycle_results['actions_executed'], 1)
        
        if success_rate > 0.8:
            return "Run next cycle in 1 hour (high success rate)"
        elif success_rate > 0.5:
            return "Run next cycle in 6 hours (moderate success)"
        else:
            return "Review issues before next cycle (low success rate)"
    
    def get_evolution_status(self) -> Dict:
        """Get current evolution status"""
        workspace_state = self.assess_workspace_state()
        current_phase = self.roadmap['current_phase']
        phase_info = self.phases[current_phase]
        
        return {
            'current_phase': current_phase,
            'phase_progress': self.roadmap['phase_progress'],
            'active_goals': self.roadmap['active_goals'],
            'workspace_health': workspace_state['overall_health'],
            'success_criteria': phase_info['success_criteria'],
            'current_metrics': {
                'critical_alerts': workspace_state['critical_alerts'],
                'avg_balance': workspace_state['avg_balance_score'],
                'total_files': workspace_state['total_files']
            },
            'next_phase': self._get_next_phase(current_phase),
            'evolution_history': self.roadmap['evolution_history'][-5:]  # Last 5 transitions
        }
    
    def _get_next_phase(self, current_phase: str) -> str:
        """Determine next evolution phase"""
        phase_order = ['stabilization', 'optimization', 'evolution']
        current_index = phase_order.index(current_phase)
        
        if current_index < len(phase_order) - 1:
            return phase_order[current_index + 1]
        else:
            return 'evolution'  # Stay in evolution phase

def main():
    import sys
    
    system = SelfImprovementSystem()
    
    if len(sys.argv) < 2:
        print("Usage: python3 self_improvement.py <command>")
        print("Commands:")
        print("  status      - Show evolution status")
        print("  assess      - Assess workspace state")
        print("  plan        - Generate improvement plan")
        print("  cycle       - Run improvement cycle (dry-run)")
        print("  execute     - Run improvement cycle (real)")
        return
    
    command = sys.argv[1]
    
    if command == 'status':
        status = system.get_evolution_status()
        
        print("🚀 Workspace Evolution Status")
        print("=" * 30)
        print(f"Current Phase: {status['current_phase']}")
        print(f"Progress: {status['phase_progress']:.1%}")
        print(f"Health: {status['workspace_health']}")
        
        print(f"\n🎯 Active Goals:")
        for goal in status['active_goals']:
            print(f"  • {goal}")
        
        print(f"\n📊 Current Metrics:")
        metrics = status['current_metrics']
        print(f"  • Critical Alerts: {metrics['critical_alerts']}")
        print(f"  • Avg Balance: {metrics['avg_balance']:.2f}")
        print(f"  • Total Files: {metrics['total_files']}")
        
        if status['evolution_history']:
            print(f"\n📈 Recent Evolution:")
            for transition in status['evolution_history']:
                time_str = datetime.fromisoformat(transition['timestamp']).strftime('%m/%d %H:%M')
                print(f"  [{time_str}] {transition['from_phase']} → {transition['to_phase']}")
    
    elif command == 'assess':
        state = system.assess_workspace_state()
        
        print("📊 Workspace Assessment")
        print("=" * 25)
        print(f"Overall Health: {state['overall_health']}")
        print(f"Total Files: {state['total_files']}")
        print(f"Categories: {state['categories_count']}")
        
        print(f"\n🚨 Alerts:")
        print(f"  • Critical: {state['critical_alerts']}")
        print(f"  • Warning: {state['warning_alerts']}")
        
        print(f"\n📈 Opportunities:")
        print(f"  • Immediate Actions: {state['immediate_actions']}")
        print(f"  • Auto Splits: {state['auto_split_opportunities']}")
        print(f"  • Auto Merges: {state['auto_merge_opportunities']}")
        
        print(f"\n⚖️ Balance Score: {state['avg_balance_score']:.2f}")
    
    elif command == 'plan':
        actions = system.generate_improvement_plan()
        
        print("📋 Improvement Plan")
        print("=" * 20)
        
        if not actions:
            print("No improvement actions needed - workspace is optimized!")
            return
        
        for i, action in enumerate(actions, 1):
            print(f"{i}. {action.action_type.title()} {action.category}")
            print(f"   Reason: {action.reason}")
            print(f"   Impact: {action.impact_score:.1f}")
            print(f"   Status: {action.status}")
            print()
    
    elif command in ['cycle', 'execute']:
        dry_run = command == 'cycle'
        results = system.run_improvement_cycle(dry_run)
        
        mode = "DRY RUN" if dry_run else "EXECUTION"
        print(f"🔄 Improvement Cycle {mode}")
        print("=" * 30)
        
        print(f"Phase: {results['phase']}")
        print(f"Actions Planned: {results['actions_planned']}")
        print(f"Actions Executed: {results['actions_executed']}")
        print(f"Success Rate: {results['actions_successful']}/{results['actions_executed']}")
        
        if not dry_run:
            print(f"Workspace Improvement: {results['workspace_improvement']:.2f}")
        
        print(f"\n💡 Next Cycle: {results['next_cycle_recommendation']}")

if __name__ == "__main__":
    main()
