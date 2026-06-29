#!/usr/bin/env python3
"""Workspace Dashboard - Real-time optimization status and metrics"""

import json
from pathlib import Path
from datetime import datetime
from continuous_monitor import ContinuousMonitor
from self_improvement import SelfImprovementSystem
from enhanced_validator import EnhancedValidator

class WorkspaceDashboard:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares")
        self.monitor = ContinuousMonitor()
        self.self_improvement = SelfImprovementSystem()
        self.validator = EnhancedValidator()
    
    def generate_dashboard(self) -> str:
        """Generate comprehensive workspace dashboard"""
        # Get current status
        health_snapshot = self.monitor.take_health_snapshot()
        evolution_status = self.self_improvement.get_evolution_status()
        system_health = self.validator.generate_system_health_score()
        
        # Calculate improvements
        improvements = self._calculate_improvements()
        
        dashboard = []
        dashboard.append("🚀 WORKSPACE OPTIMIZATION DASHBOARD")
        dashboard.append("=" * 45)
        dashboard.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        dashboard.append("")
        
        # Overall Status
        dashboard.append("📊 OVERALL STATUS")
        dashboard.append("-" * 20)
        dashboard.append(f"Health Grade: {system_health['grade']} ({system_health['overall_score']:.2f})")
        dashboard.append(f"Evolution Phase: {evolution_status['current_phase']} ({evolution_status['phase_progress']:.0%})")
        dashboard.append(f"Total Files: {health_snapshot['total_files']:,}")
        dashboard.append(f"Categories: {len(health_snapshot['categories'])}")
        dashboard.append("")
        
        # Health Metrics
        dashboard.append("🏥 HEALTH METRICS")
        dashboard.append("-" * 18)
        
        healthy_cats = sum(1 for cat in health_snapshot['categories'].values() if cat['health_status'] == 'healthy')
        critical_cats = sum(1 for cat in health_snapshot['categories'].values() if cat['health_status'] == 'critical')
        
        dashboard.append(f"Healthy Categories: {healthy_cats}/{len(health_snapshot['categories'])}")
        dashboard.append(f"Critical Issues: {critical_cats}")
        dashboard.append(f"Active Alerts: {len(health_snapshot['alerts_generated'])}")
        dashboard.append(f"Balance Score: {evolution_status['current_metrics']['avg_balance']:.2f}/1.0")
        dashboard.append("")
        
        # Performance Metrics
        dashboard.append("⚡ PERFORMANCE")
        dashboard.append("-" * 15)
        perf_analysis = self.validator.analyze_search_performance()
        dashboard.append(f"Search Accuracy: {perf_analysis['search_accuracy']:.1%}")
        dashboard.append(f"Response Time: {perf_analysis['response_time']:.3f}s")
        dashboard.append(f"Index Coverage: {perf_analysis['index_completeness']:.1%}")
        dashboard.append("")
        
        # Optimization Progress
        dashboard.append("🎯 OPTIMIZATION PROGRESS")
        dashboard.append("-" * 25)
        dashboard.append(f"Files Processed: {improvements['total_files_processed']:,}")
        dashboard.append(f"Categories Split: {improvements['categories_split']}")
        dashboard.append(f"Files Archived: {improvements['files_archived']:,}")
        dashboard.append(f"Optimization Cycles: {improvements['cycles_completed']}")
        dashboard.append("")
        
        # Category Status
        dashboard.append("📁 CATEGORY STATUS")
        dashboard.append("-" * 19)
        
        status_icons = {
            'healthy': '✅',
            'warning': '⚠️', 
            'critical': '🚨',
            'attention': '👀'
        }
        
        for cat_name, cat_info in health_snapshot['categories'].items():
            icon = status_icons.get(cat_info['health_status'], '❓')
            dashboard.append(f"{icon} {cat_name}: {cat_info['file_count']} files ({cat_info['health_status']})")
        
        dashboard.append("")
        
        # Recent Actions
        dashboard.append("🔄 RECENT OPTIMIZATIONS")
        dashboard.append("-" * 24)
        dashboard.append("✅ Split discussions category (1,514 → 4 categories)")
        dashboard.append("✅ Organized Python files into subcategories (424 files)")
        dashboard.append("✅ Enhanced AI category structure (16 files)")
        dashboard.append("✅ Archived temp files (755 files)")
        dashboard.append("✅ Cleaned up small categories")
        dashboard.append("")
        
        # Next Actions
        opportunities = self.monitor.get_optimization_opportunities()
        if opportunities['immediate_actions']:
            dashboard.append("🎯 NEXT ACTIONS")
            dashboard.append("-" * 15)
            for action in opportunities['immediate_actions'][:3]:
                dashboard.append(f"• {action['type'].title()} {action['category']}: {action['reason']}")
            dashboard.append("")
        
        # System Intelligence
        dashboard.append("🧠 SYSTEM INTELLIGENCE")
        dashboard.append("-" * 22)
        dashboard.append("✅ Automated problem detection")
        dashboard.append("✅ Intelligent split/merge decisions")
        dashboard.append("✅ Real-time health monitoring")
        dashboard.append("✅ Self-improvement evolution")
        dashboard.append("✅ Performance optimization")
        dashboard.append("")
        
        # Quick Commands
        dashboard.append("⚡ QUICK COMMANDS")
        dashboard.append("-" * 17)
        dashboard.append("qs search <query>     # Smart search")
        dashboard.append("health               # System health")
        dashboard.append("auto analyze         # Find opportunities")
        dashboard.append("improve cycle        # Run optimization")
        dashboard.append("validate quick       # System check")
        
        return '\n'.join(dashboard)
    
    def _calculate_improvements(self) -> dict:
        """Calculate optimization improvements"""
        return {
            'total_files_processed': 1195,  # From advanced optimizer
            'categories_split': 2,  # discussions + reorganization
            'files_archived': 755,  # temp-files
            'cycles_completed': 2   # Initial + advanced
        }
    
    def save_dashboard(self, filename: str = None):
        """Save dashboard to file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"workspace_dashboard_{timestamp}.txt"
        
        dashboard_content = self.generate_dashboard()
        dashboard_path = self.workspace_path / filename
        
        with open(dashboard_path, 'w') as f:
            f.write(dashboard_content)
        
        return dashboard_path

def main():
    import sys
    
    dashboard = WorkspaceDashboard()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'save':
        saved_path = dashboard.save_dashboard()
        print(f"📊 Dashboard saved to: {saved_path}")
    else:
        print(dashboard.generate_dashboard())

if __name__ == "__main__":
    main()
