#!/usr/bin/env python3
"""System Validator - End-to-end testing of complete optimization system"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

# Import all system components
from category_automation import CategoryAutomation
from continuous_monitor import ContinuousMonitor
from semantic_search import SemanticSearch
from self_improvement import SelfImprovementSystem
from type_based_search import TypeBasedSearch

@dataclass
class TestResult:
    component: str
    test_name: str
    status: str  # pass, fail, warning
    execution_time: float
    details: str
    metrics: Dict = None

class SystemValidator:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares")
        self.test_results = []
        
        # Initialize all components
        self.automation = CategoryAutomation()
        self.monitor = ContinuousMonitor()
        self.semantic_search = SemanticSearch()
        self.self_improvement = SelfImprovementSystem()
        self.type_search = TypeBasedSearch()
    
    def run_component_test(self, component_name: str, test_func, test_name: str) -> TestResult:
        """Run individual component test"""
        start_time = time.time()
        
        try:
            result = test_func()
            execution_time = time.time() - start_time
            
            if result.get('success', True):
                status = 'pass'
                details = result.get('message', 'Test passed')
            else:
                status = 'fail'
                details = result.get('error', 'Test failed')
            
            return TestResult(
                component=component_name,
                test_name=test_name,
                status=status,
                execution_time=execution_time,
                details=details,
                metrics=result.get('metrics', {})
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                component=component_name,
                test_name=test_name,
                status='fail',
                execution_time=execution_time,
                details=f"Exception: {str(e)}"
            )
    
    def test_category_automation(self) -> Dict:
        """Test category automation system"""
        try:
            # Test analysis
            opportunities = self.automation.analyze_automation_opportunities()
            
            # Test scheduling
            schedule = self.automation.get_automation_schedule()
            
            # Test dry run execution
            results = self.automation.execute_automation(dry_run=True)
            
            return {
                'success': True,
                'message': f"Automation working: {len(opportunities['auto_splits'])} splits, {len(opportunities['auto_merges'])} merges identified",
                'metrics': {
                    'split_opportunities': len(opportunities['auto_splits']),
                    'merge_opportunities': len(opportunities['auto_merges']),
                    'scheduled_actions': len(schedule['immediate']) + len(schedule['weekly']) + len(schedule['monthly'])
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_continuous_monitoring(self) -> Dict:
        """Test continuous monitoring system"""
        try:
            # Test health snapshot
            snapshot = self.monitor.take_health_snapshot()
            
            # Test alerts
            alerts = self.monitor.get_active_alerts(24)
            
            # Test trends
            trends = self.monitor.get_health_trends()
            
            # Test optimization opportunities
            opportunities = self.monitor.get_optimization_opportunities()
            
            return {
                'success': True,
                'message': f"Monitoring working: {len(snapshot['categories'])} categories monitored, {len(alerts)} active alerts",
                'metrics': {
                    'categories_monitored': len(snapshot['categories']),
                    'active_alerts': len(alerts),
                    'overall_health': snapshot['overall_health'],
                    'total_files': snapshot['total_files']
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_semantic_search(self) -> Dict:
        """Test semantic search system"""
        try:
            # Test search functionality
            search_results = self.semantic_search.semantic_search("python automation", max_results=5)
            
            # Test semantic groups
            groups = self.semantic_search.get_semantic_groups()
            
            # Test cross-category analysis
            analysis = self.semantic_search.cross_category_analysis()
            
            # Test category suggestions
            suggestions = self.semantic_search.get_category_suggestions("automation tools")
            
            return {
                'success': True,
                'message': f"Semantic search working: {len(search_results)} results, {len(groups)} semantic groups",
                'metrics': {
                    'search_results': len(search_results),
                    'semantic_groups': len(groups),
                    'similar_categories': len(analysis.get('similar_categories', [])),
                    'category_suggestions': len(suggestions)
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_type_based_search(self) -> Dict:
        """Test type-based search system"""
        try:
            # Test file type search
            python_files = self.type_search.search_by_type('python')
            
            # Test category search
            ai_category = self.type_search.search_by_category('ai')
            
            # Test mixed content preview
            preview = self.type_search.mixed_content_preview('discussions')
            
            # Test navigation menu
            menu = self.type_search.generate_navigation_menu()
            
            return {
                'success': True,
                'message': f"Type search working: {len(python_files['matches'])} Python files, {menu['quick_stats']['total_files']} total files indexed",
                'metrics': {
                    'python_files': len(python_files['matches']),
                    'total_indexed': menu['quick_stats']['total_files'],
                    'categories': menu['quick_stats']['total_categories'],
                    'file_types': menu['quick_stats']['total_file_types']
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_self_improvement(self) -> Dict:
        """Test self-improvement system"""
        try:
            # Test workspace assessment
            state = self.self_improvement.assess_workspace_state()
            
            # Test improvement plan generation
            plan = self.self_improvement.generate_improvement_plan()
            
            # Test evolution status
            status = self.self_improvement.get_evolution_status()
            
            # Test improvement cycle (dry run)
            cycle_results = self.self_improvement.run_improvement_cycle(dry_run=True)
            
            return {
                'success': True,
                'message': f"Self-improvement working: {len(plan)} actions planned, phase: {status['current_phase']}",
                'metrics': {
                    'improvement_actions': len(plan),
                    'current_phase': status['current_phase'],
                    'phase_progress': status['phase_progress'],
                    'workspace_health': state['overall_health']
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_system_integration(self) -> Dict:
        """Test integration between all systems"""
        try:
            # Test data flow between components
            
            # 1. Monitor generates health data
            health_snapshot = self.monitor.take_health_snapshot()
            
            # 2. Automation uses health data for opportunities
            auto_opportunities = self.automation.analyze_automation_opportunities()
            
            # 3. Self-improvement uses both for planning
            improvement_plan = self.self_improvement.generate_improvement_plan()
            
            # 4. Semantic search provides additional insights
            semantic_analysis = self.semantic_search.cross_category_analysis()
            
            # Verify data consistency
            health_categories = set(health_snapshot['categories'].keys())
            auto_categories = set()
            for split in auto_opportunities['auto_splits']:
                auto_categories.add(split['category'])
            for merge in auto_opportunities['auto_merges']:
                auto_categories.add(merge['category'])
            
            # Check if categories are consistent
            category_consistency = auto_categories.issubset(health_categories)
            
            return {
                'success': category_consistency,
                'message': f"Integration working: {len(health_categories)} categories consistent across systems",
                'metrics': {
                    'health_categories': len(health_categories),
                    'auto_categories': len(auto_categories),
                    'improvement_actions': len(improvement_plan),
                    'semantic_groups': len(semantic_analysis.get('similar_categories', [])),
                    'data_consistency': category_consistency
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def test_performance_benchmarks(self) -> Dict:
        """Test system performance benchmarks"""
        try:
            benchmarks = {}
            
            # Benchmark search performance
            start_time = time.time()
            search_results = self.semantic_search.semantic_search("python automation")
            benchmarks['semantic_search_time'] = time.time() - start_time
            
            # Benchmark type search performance
            start_time = time.time()
            type_results = self.type_search.search_by_type('python')
            benchmarks['type_search_time'] = time.time() - start_time
            
            # Benchmark monitoring performance
            start_time = time.time()
            health_snapshot = self.monitor.take_health_snapshot()
            benchmarks['monitoring_time'] = time.time() - start_time
            
            # Benchmark automation analysis
            start_time = time.time()
            auto_analysis = self.automation.analyze_automation_opportunities()
            benchmarks['automation_analysis_time'] = time.time() - start_time
            
            # Check performance thresholds
            performance_ok = all([
                benchmarks['semantic_search_time'] < 5.0,  # 5 seconds max
                benchmarks['type_search_time'] < 2.0,      # 2 seconds max
                benchmarks['monitoring_time'] < 3.0,       # 3 seconds max
                benchmarks['automation_analysis_time'] < 2.0  # 2 seconds max
            ])
            
            return {
                'success': performance_ok,
                'message': f"Performance {'acceptable' if performance_ok else 'issues detected'}",
                'metrics': benchmarks
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run_full_validation(self) -> Dict:
        """Run complete system validation"""
        print("🧪 Starting Full System Validation")
        print("=" * 40)
        
        # Define all tests
        tests = [
            ('Category Automation', self.test_category_automation, 'automation_functionality'),
            ('Continuous Monitoring', self.test_continuous_monitoring, 'monitoring_functionality'),
            ('Semantic Search', self.test_semantic_search, 'semantic_search_functionality'),
            ('Type-Based Search', self.test_type_based_search, 'type_search_functionality'),
            ('Self-Improvement', self.test_self_improvement, 'self_improvement_functionality'),
            ('System Integration', self.test_system_integration, 'integration_test'),
            ('Performance Benchmarks', self.test_performance_benchmarks, 'performance_test')
        ]
        
        # Run all tests
        for component, test_func, test_name in tests:
            print(f"\n🔍 Testing {component}...")
            result = self.run_component_test(component, test_func, test_name)
            self.test_results.append(result)
            
            # Print immediate result
            status_emoji = {'pass': '✅', 'fail': '❌', 'warning': '⚠️'}
            emoji = status_emoji.get(result.status, '❓')
            print(f"   {emoji} {result.test_name}: {result.details} ({result.execution_time:.2f}s)")
        
        # Generate summary
        summary = self._generate_test_summary()
        
        # Save results
        self._save_test_results()
        
        return summary
    
    def _generate_test_summary(self) -> Dict:
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == 'pass'])
        failed_tests = len([r for r in self.test_results if r.status == 'fail'])
        warning_tests = len([r for r in self.test_results if r.status == 'warning'])
        
        total_time = sum(r.execution_time for r in self.test_results)
        
        return {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'warnings': warning_tests,
            'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'total_execution_time': total_time,
            'overall_status': 'pass' if failed_tests == 0 else 'fail',
            'timestamp': datetime.now().isoformat()
        }
    
    def _save_test_results(self):
        """Save test results to file"""
        results_file = self.workspace_path / "validation_results.json"
        
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': self._generate_test_summary(),
            'detailed_results': [asdict(r) for r in self.test_results]
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)

def main():
    import sys
    
    validator = SystemValidator()
    
    if len(sys.argv) < 2:
        print("Usage: python3 system_validator.py <command>")
        print("Commands:")
        print("  validate    - Run full system validation")
        print("  quick       - Run quick validation (core tests only)")
        print("  performance - Run performance benchmarks only")
        return
    
    command = sys.argv[1]
    
    if command == 'validate':
        summary = validator.run_full_validation()
        
        print(f"\n📊 Validation Summary")
        print("=" * 25)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Warnings: {summary['warnings']} ⚠️")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Total Time: {summary['total_execution_time']:.2f}s")
        print(f"Overall Status: {summary['overall_status'].upper()}")
        
        if summary['failed'] > 0:
            print(f"\n❌ Failed Tests:")
            for result in validator.test_results:
                if result.status == 'fail':
                    print(f"  • {result.component}: {result.details}")
    
    elif command == 'quick':
        # Run core tests only
        core_tests = [
            ('Monitoring', validator.test_continuous_monitoring, 'quick_monitoring'),
            ('Search', validator.test_type_based_search, 'quick_search'),
            ('Integration', validator.test_system_integration, 'quick_integration')
        ]
        
        print("🚀 Quick Validation")
        print("=" * 20)
        
        for component, test_func, test_name in core_tests:
            result = validator.run_component_test(component, test_func, test_name)
            status_emoji = {'pass': '✅', 'fail': '❌', 'warning': '⚠️'}
            emoji = status_emoji.get(result.status, '❓')
            print(f"{emoji} {component}: {result.details} ({result.execution_time:.2f}s)")
    
    elif command == 'performance':
        print("⚡ Performance Benchmarks")
        print("=" * 25)
        
        result = validator.run_component_test('Performance', validator.test_performance_benchmarks, 'performance_test')
        
        if result.metrics:
            for metric, value in result.metrics.items():
                print(f"  • {metric}: {value:.3f}s")
        
        status_emoji = {'pass': '✅', 'fail': '❌'}
        emoji = status_emoji.get(result.status, '❓')
        print(f"\n{emoji} Performance: {result.details}")

if __name__ == "__main__":
    main()
