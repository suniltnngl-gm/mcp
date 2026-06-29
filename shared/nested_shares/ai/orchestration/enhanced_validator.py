#!/usr/bin/env python3
"""Enhanced Validator - Deep analysis with quick improvement suggestions"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from collections import Counter, defaultdict
from system_validator import SystemValidator

class EnhancedValidator(SystemValidator):
    def __init__(self):
        super().__init__()
        self.improvement_suggestions = []
    
    def analyze_search_performance(self) -> Dict:
        """Deep analysis of search system performance and accuracy"""
        results = {
            'search_accuracy': 0.0,
            'index_completeness': 0.0,
            'response_time': 0.0,
            'suggestions': []
        }
        
        # Test search accuracy with known queries
        test_queries = [
            ('python automation', ['automation', 'python']),
            ('category split', ['category', 'split']),
            ('monitoring health', ['monitor', 'health']),
            ('semantic search', ['semantic', 'search'])
        ]
        
        accurate_results = 0
        total_time = 0
        
        for query, expected_terms in test_queries:
            start_time = time.time()
            search_results = self.semantic_search.semantic_search(query, max_results=10)
            query_time = time.time() - start_time
            total_time += query_time
            
            # Check if results contain expected terms
            found_terms = 0
            for result in search_results[:5]:  # Top 5 results
                result_text = (result.file_path + ' ' + result.snippet).lower()
                for term in expected_terms:
                    if term in result_text:
                        found_terms += 1
                        break
            
            if found_terms >= len(expected_terms) * 0.6:  # 60% accuracy threshold
                accurate_results += 1
        
        results['search_accuracy'] = accurate_results / len(test_queries)
        results['response_time'] = total_time / len(test_queries)
        
        # Check index completeness
        menu = self.type_search.generate_navigation_menu()
        total_workspace_files = sum(len(list(cat_dir.rglob("*"))) 
                                  for cat_dir in self.workspace_path.iterdir() 
                                  if cat_dir.is_dir() and not cat_dir.name.startswith('.'))
        
        results['index_completeness'] = menu['quick_stats']['total_files'] / max(total_workspace_files, 1)
        
        # Generate suggestions
        if results['search_accuracy'] < 0.8:
            results['suggestions'].append("Improve keyword extraction algorithm")
        if results['response_time'] > 1.0:
            results['suggestions'].append("Add search result caching")
        if results['index_completeness'] < 0.9:
            results['suggestions'].append("Expand file type indexing")
        
        return results
    
    def analyze_monitoring_efficiency(self) -> Dict:
        """Analyze monitoring system efficiency and alert quality"""
        results = {
            'alert_accuracy': 0.0,
            'monitoring_coverage': 0.0,
            'response_efficiency': 0.0,
            'suggestions': []
        }
        
        # Take health snapshot and analyze alerts
        snapshot = self.monitor.take_health_snapshot()
        alerts = snapshot['alerts_generated']
        
        # Analyze alert quality
        critical_alerts = [a for a in alerts if a['level'] == 'critical']
        actionable_alerts = [a for a in alerts if a.get('action_required', False)]
        
        if alerts:
            results['alert_accuracy'] = len(actionable_alerts) / len(alerts)
        
        # Check monitoring coverage
        categories_with_alerts = set(a['category'] for a in alerts)
        total_categories = len(snapshot['categories'])
        results['monitoring_coverage'] = len(categories_with_alerts) / max(total_categories, 1)
        
        # Check response efficiency (time to generate insights)
        start_time = time.time()
        opportunities = self.monitor.get_optimization_opportunities()
        response_time = time.time() - start_time
        results['response_efficiency'] = 1.0 / max(response_time, 0.1)  # Inverse of time
        
        # Generate suggestions
        if results['alert_accuracy'] < 0.7:
            results['suggestions'].append("Refine alert thresholds to reduce noise")
        if len(critical_alerts) > 3:
            results['suggestions'].append("Implement automated critical alert resolution")
        if response_time > 2.0:
            results['suggestions'].append("Optimize monitoring data processing")
        
        return results
    
    def analyze_automation_intelligence(self) -> Dict:
        """Analyze automation system intelligence and decision quality"""
        results = {
            'decision_accuracy': 0.0,
            'automation_coverage': 0.0,
            'prediction_quality': 0.0,
            'suggestions': []
        }
        
        # Analyze automation opportunities
        opportunities = self.automation.analyze_automation_opportunities()
        schedule = self.automation.get_automation_schedule()
        
        # Check decision accuracy (do suggestions make sense?)
        total_suggestions = (len(opportunities['auto_splits']) + 
                           len(opportunities['auto_merges']) + 
                           len(opportunities['subcategory_creation']))
        
        # Validate split suggestions
        valid_splits = 0
        for split in opportunities['auto_splits']:
            if split['files'] > 100:  # Valid threshold
                valid_splits += 1
        
        # Validate merge suggestions  
        valid_merges = 0
        for merge in opportunities['auto_merges']:
            if merge['files'] < 10:  # Valid threshold
                valid_merges += 1
        
        valid_suggestions = valid_splits + valid_merges
        if total_suggestions > 0:
            results['decision_accuracy'] = valid_suggestions / total_suggestions
        
        # Check automation coverage
        total_actions = (len(schedule['immediate']) + 
                        len(schedule['weekly']) + 
                        len(schedule['monthly']))
        results['automation_coverage'] = min(total_actions / 5, 1.0)  # Normalize to 5 max actions
        
        # Prediction quality (based on thresholds)
        high_priority_splits = [s for s in opportunities['auto_splits'] if s['priority'] == 'high']
        results['prediction_quality'] = len(high_priority_splits) / max(len(opportunities['auto_splits']), 1)
        
        # Generate suggestions
        if results['decision_accuracy'] < 0.8:
            results['suggestions'].append("Improve threshold calibration")
        if total_actions == 0:
            results['suggestions'].append("Enable proactive automation suggestions")
        if len(high_priority_splits) > 2:
            results['suggestions'].append("Implement immediate auto-execution for critical cases")
        
        return results
    
    def find_quick_optimization_wins(self) -> List[Dict]:
        """Identify quick wins for system optimization"""
        quick_wins = []
        
        # Analyze current state
        snapshot = self.monitor.take_health_snapshot()
        opportunities = self.automation.analyze_automation_opportunities()
        
        # Quick win 1: Cache search results
        quick_wins.append({
            'type': 'performance',
            'title': 'Add Search Result Caching',
            'impact': 'high',
            'effort': 'low',
            'description': 'Cache semantic search results for 5 minutes to improve response time',
            'implementation': 'Add LRU cache to semantic_search.py'
        })
        
        # Quick win 2: Batch alert processing
        if len(snapshot['alerts_generated']) > 10:
            quick_wins.append({
                'type': 'monitoring',
                'title': 'Batch Alert Processing',
                'impact': 'medium',
                'effort': 'low',
                'description': 'Group similar alerts to reduce noise',
                'implementation': 'Add alert grouping in continuous_monitor.py'
            })
        
        # Quick win 3: Auto-execute safe operations
        safe_merges = [m for m in opportunities['auto_merges'] if m['files'] < 3]
        if safe_merges:
            quick_wins.append({
                'type': 'automation',
                'title': 'Auto-Execute Safe Merges',
                'impact': 'medium',
                'effort': 'low',
                'description': f'Automatically merge {len(safe_merges)} tiny categories',
                'implementation': 'Add auto-execution for categories with <3 files'
            })
        
        # Quick win 4: Keyboard shortcuts for common operations
        quick_wins.append({
            'type': 'usability',
            'title': 'Add Quick Command Aliases',
            'impact': 'medium',
            'effort': 'low',
            'description': 'Create short aliases for common operations',
            'implementation': 'Add alias script: s=search, m=monitor, a=automate'
        })
        
        # Quick win 5: Progress indicators
        quick_wins.append({
            'type': 'feedback',
            'title': 'Add Progress Indicators',
            'impact': 'low',
            'effort': 'low',
            'description': 'Show progress bars for long operations',
            'implementation': 'Add tqdm progress bars to indexing operations'
        })
        
        return quick_wins
    
    def generate_system_health_score(self) -> Dict:
        """Generate comprehensive system health score"""
        # Run all analyses
        search_analysis = self.analyze_search_performance()
        monitoring_analysis = self.analyze_monitoring_efficiency()
        automation_analysis = self.analyze_automation_intelligence()
        
        # Calculate weighted scores
        search_score = (search_analysis['search_accuracy'] * 0.4 + 
                       search_analysis['index_completeness'] * 0.3 + 
                       (1.0 / max(search_analysis['response_time'], 0.1)) * 0.3)
        
        monitoring_score = (monitoring_analysis['alert_accuracy'] * 0.4 + 
                          monitoring_analysis['monitoring_coverage'] * 0.3 + 
                          min(monitoring_analysis['response_efficiency'] / 10, 1.0) * 0.3)
        
        automation_score = (automation_analysis['decision_accuracy'] * 0.5 + 
                          automation_analysis['automation_coverage'] * 0.3 + 
                          automation_analysis['prediction_quality'] * 0.2)
        
        # Overall health score
        overall_score = (search_score * 0.35 + monitoring_score * 0.35 + automation_score * 0.30)
        
        # Determine health grade
        if overall_score >= 0.9:
            grade = 'A+'
        elif overall_score >= 0.8:
            grade = 'A'
        elif overall_score >= 0.7:
            grade = 'B'
        elif overall_score >= 0.6:
            grade = 'C'
        else:
            grade = 'D'
        
        return {
            'overall_score': overall_score,
            'grade': grade,
            'component_scores': {
                'search': search_score,
                'monitoring': monitoring_score,
                'automation': automation_score
            },
            'detailed_analysis': {
                'search': search_analysis,
                'monitoring': monitoring_analysis,
                'automation': automation_analysis
            },
            'quick_wins': self.find_quick_optimization_wins()
        }
    
    def implement_quick_win(self, win_type: str) -> Dict:
        """Implement a specific quick win"""
        results = {'success': False, 'message': ''}
        
        if win_type == 'cache':
            # Add simple caching to search
            cache_code = '''
# Add to semantic_search.py
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_search(self, query: str, max_results: int = 20):
    return self.semantic_search(query, max_results)
'''
            results = {'success': True, 'message': 'Search caching code generated', 'code': cache_code}
        
        elif win_type == 'aliases':
            # Create quick command aliases
            alias_script = '''#!/bin/bash
# Quick command aliases
alias s="python3 semantic_search.py search"
alias m="python3 continuous_monitor.py snapshot"
alias a="python3 category_automation.py analyze"
alias v="python3 system_validator.py quick"
'''
            alias_path = self.workspace_path / "quick_commands.sh"
            with open(alias_path, 'w') as f:
                f.write(alias_script)
            results = {'success': True, 'message': f'Quick aliases created at {alias_path}'}
        
        elif win_type == 'auto_merge':
            # Execute safe merges automatically
            opportunities = self.automation.analyze_automation_opportunities()
            safe_merges = [m for m in opportunities['auto_merges'] if m['files'] < 3]
            
            if safe_merges:
                # Would execute merges here in real implementation
                results = {'success': True, 'message': f'Would auto-merge {len(safe_merges)} tiny categories'}
            else:
                results = {'success': False, 'message': 'No safe merges available'}
        
        return results

def main():
    import sys
    
    validator = EnhancedValidator()
    
    if len(sys.argv) < 2:
        print("Usage: python3 enhanced_validator.py <command>")
        print("Commands:")
        print("  health      - Generate system health score")
        print("  search      - Analyze search performance")
        print("  monitor     - Analyze monitoring efficiency")
        print("  automate    - Analyze automation intelligence")
        print("  quickwins   - Show quick optimization wins")
        print("  implement <type> - Implement quick win (cache/aliases/auto_merge)")
        return
    
    command = sys.argv[1]
    
    if command == 'health':
        health = validator.generate_system_health_score()
        
        print("🏥 System Health Report")
        print("=" * 25)
        print(f"Overall Score: {health['overall_score']:.2f} ({health['grade']})")
        
        print(f"\n📊 Component Scores:")
        for component, score in health['component_scores'].items():
            print(f"  • {component.title()}: {score:.2f}")
        
        print(f"\n🚀 Quick Wins Available: {len(health['quick_wins'])}")
        for i, win in enumerate(health['quick_wins'][:3], 1):
            print(f"  {i}. {win['title']} ({win['impact']} impact, {win['effort']} effort)")
    
    elif command == 'search':
        analysis = validator.analyze_search_performance()
        
        print("🔍 Search Performance Analysis")
        print("=" * 30)
        print(f"Accuracy: {analysis['search_accuracy']:.1%}")
        print(f"Index Completeness: {analysis['index_completeness']:.1%}")
        print(f"Response Time: {analysis['response_time']:.3f}s")
        
        if analysis['suggestions']:
            print(f"\n💡 Suggestions:")
            for suggestion in analysis['suggestions']:
                print(f"  • {suggestion}")
    
    elif command == 'monitor':
        analysis = validator.analyze_monitoring_efficiency()
        
        print("📊 Monitoring Efficiency Analysis")
        print("=" * 35)
        print(f"Alert Accuracy: {analysis['alert_accuracy']:.1%}")
        print(f"Coverage: {analysis['monitoring_coverage']:.1%}")
        print(f"Response Efficiency: {analysis['response_efficiency']:.2f}")
        
        if analysis['suggestions']:
            print(f"\n💡 Suggestions:")
            for suggestion in analysis['suggestions']:
                print(f"  • {suggestion}")
    
    elif command == 'automate':
        analysis = validator.analyze_automation_intelligence()
        
        print("🤖 Automation Intelligence Analysis")
        print("=" * 38)
        print(f"Decision Accuracy: {analysis['decision_accuracy']:.1%}")
        print(f"Coverage: {analysis['automation_coverage']:.1%}")
        print(f"Prediction Quality: {analysis['prediction_quality']:.1%}")
        
        if analysis['suggestions']:
            print(f"\n💡 Suggestions:")
            for suggestion in analysis['suggestions']:
                print(f"  • {suggestion}")
    
    elif command == 'quickwins':
        wins = validator.find_quick_optimization_wins()
        
        print("🚀 Quick Optimization Wins")
        print("=" * 28)
        
        for i, win in enumerate(wins, 1):
            print(f"\n{i}. {win['title']}")
            print(f"   Type: {win['type']}")
            print(f"   Impact: {win['impact']} | Effort: {win['effort']}")
            print(f"   Description: {win['description']}")
            print(f"   Implementation: {win['implementation']}")
    
    elif command == 'implement' and len(sys.argv) >= 3:
        win_type = sys.argv[2]
        result = validator.implement_quick_win(win_type)
        
        if result['success']:
            print(f"✅ {result['message']}")
            if 'code' in result:
                print(f"\nCode to add:\n{result['code']}")
        else:
            print(f"❌ {result['message']}")

if __name__ == "__main__":
    main()
