#!/usr/bin/env python3
"""Next Steps Updater - Update roadmap with mixed categories insights"""

import json
from pathlib import Path
from datetime import datetime
from mixed_categories_analyzer import MixedCategoriesAnalyzer

class NextStepsUpdater:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.analyzer = MixedCategoriesAnalyzer()
    
    def generate_updated_roadmap(self) -> Dict:
        """Generate updated roadmap based on mixed categories analysis"""
        
        # Run analysis
        analyses = self.analyzer.analyze_all_categories()
        strategy = self.analyzer.generate_optimization_strategy(analyses)
        
        # Create updated roadmap
        roadmap = {
            "timestamp": datetime.now().isoformat(),
            "phase": "mixed_categories_optimization",
            "critical_findings": self._extract_critical_findings(analyses, strategy),
            "immediate_priorities": self._create_immediate_priorities(strategy),
            "split_merge_plan": self._create_split_merge_plan(strategy),
            "search_strategy": self._create_search_strategy(strategy),
            "cleanup_plan": self._create_cleanup_plan(analyses, strategy),
            "implementation_phases": self._create_implementation_phases(strategy)
        }
        
        return roadmap
    
    def _extract_critical_findings(self, analyses: Dict, strategy: Dict) -> List[str]:
        """Extract critical findings from analysis"""
        findings = []
        
        # Major imbalances
        large_categories = [name for name, analysis in analyses.items() if analysis.file_count > 100]
        if large_categories:
            findings.append(f"Major imbalance: {large_categories[0]} has {analyses[large_categories[0]].file_count} files")
        
        # Placeholder proliferation
        placeholders = [name for name, analysis in analyses.items() if analysis.creation_pattern == "placeholder"]
        if len(placeholders) > 5:
            findings.append(f"Placeholder proliferation: {len(placeholders)} placeholder categories need consolidation")
        
        # Mixed type complexity
        complex_mixed = [name for name, analysis in analyses.items() if len(analysis.mixed_types) > 3]
        if complex_mixed:
            findings.append(f"Complex mixing: {len(complex_mixed)} categories have 4+ file types")
        
        return findings
    
    def _create_immediate_priorities(self, strategy: Dict) -> List[Dict]:
        """Create immediate priority actions"""
        priorities = []
        
        # Critical actions first
        for action in strategy["immediate_actions"]:
            priorities.append({
                "action": action,
                "type": "reorganization",
                "urgency": "critical",
                "estimated_time": "2-4 hours"
            })
        
        # High-impact splits
        for split in strategy["split_operations"][:2]:
            priorities.append({
                "action": split,
                "type": "split_operation", 
                "urgency": "high",
                "estimated_time": "1-2 hours"
            })
        
        # Quick merges
        small_merges = [m for m in strategy["merge_operations"] if "only" in m and "1 files" in m]
        for merge in small_merges[:3]:
            priorities.append({
                "action": merge,
                "type": "merge_operation",
                "urgency": "medium",
                "estimated_time": "15-30 minutes"
            })
        
        return priorities
    
    def _create_split_merge_plan(self, strategy: Dict) -> Dict:
        """Create detailed split/merge execution plan"""
        plan = {
            "split_operations": [],
            "merge_operations": [],
            "consolidation_targets": []
        }
        
        # Process splits
        for split_op in strategy["split_operations"]:
            category, operation = split_op.split(": ", 1)
            plan["split_operations"].append({
                "source_category": category,
                "operation": operation,
                "complexity": "high" if "654 files" in operation else "medium",
                "prerequisites": ["backup_category", "analyze_dependencies"]
            })
        
        # Process merges
        for merge_op in strategy["merge_operations"]:
            category, operation = merge_op.split(": ", 1)
            plan["merge_operations"].append({
                "source_category": category,
                "operation": operation,
                "complexity": "low" if "only" in operation else "medium",
                "prerequisites": ["verify_compatibility"]
            })
        
        # Consolidation targets (placeholder categories)
        placeholder_categories = ["git", "db", "config", "web", "data", "system"]
        plan["consolidation_targets"] = [
            {
                "categories": placeholder_categories,
                "target": "utilities",
                "rationale": "Single-file placeholder categories should be consolidated",
                "estimated_reduction": f"{len(placeholder_categories)} → 1 category"
            }
        ]
        
        return plan
    
    def _create_search_strategy(self, strategy: Dict) -> Dict:
        """Create enhanced search strategy"""
        search_strategy = {
            "type_based_search": {
                "implementation": "Add file type filters to search interface",
                "categories": ["discussions", "ai", "workflow"],
                "filters": ["code", "docs", "config", "data"]
            },
            "semantic_grouping": {
                "implementation": "Group semantically similar categories in search results",
                "groups": {
                    "development": ["code", "testing", "refactor"],
                    "documentation": ["docs", "alternatives"],
                    "configuration": ["config", "system"],
                    "ai_tools": ["ai", "discussions"]
                }
            },
            "relevancy_ranking": {
                "implementation": "Rank results by file relevancy score",
                "boost_factors": ["recent_modification", "file_importance", "usage_frequency"]
            },
            "mixed_category_navigation": {
                "implementation": "Add category-specific navigation for mixed content",
                "features": ["type_tabs", "quick_filters", "content_preview"]
            }
        }
        
        return search_strategy
    
    def _create_cleanup_plan(self, analyses: Dict, strategy: Dict) -> Dict:
        """Create cleanup and maintenance plan"""
        cleanup_plan = {
            "outdated_content": [],
            "placeholder_removal": [],
            "relevancy_improvement": [],
            "maintenance_schedule": {}
        }
        
        # Find outdated content
        for name, analysis in analyses.items():
            if analysis.relevancy_score < 0.5:
                cleanup_plan["outdated_content"].append({
                    "category": name,
                    "relevancy": f"{analysis.relevancy_score:.1%}",
                    "action": "Review and archive old files",
                    "priority": analysis.priority
                })
        
        # Placeholder removal plan
        placeholders = [name for name, analysis in analyses.items() 
                       if analysis.creation_pattern == "placeholder" and analysis.file_count <= 1]
        cleanup_plan["placeholder_removal"] = [
            {
                "category": cat,
                "action": "Merge into utilities or remove",
                "impact": "Reduces category count"
            }
            for cat in placeholders
        ]
        
        # Maintenance schedule
        cleanup_plan["maintenance_schedule"] = {
            "weekly": ["Review new file placements", "Update category relevancy scores"],
            "monthly": ["Run mixed categories analysis", "Optimize based on usage patterns"],
            "quarterly": ["Major reorganization review", "Archive outdated content"]
        }
        
        return cleanup_plan
    
    def _create_implementation_phases(self, strategy: Dict) -> List[Dict]:
        """Create phased implementation plan"""
        phases = [
            {
                "phase": 1,
                "name": "Critical Reorganization",
                "duration": "1-2 days",
                "actions": [
                    "Split discussions category (1512 files → manageable chunks)",
                    "Consolidate placeholder categories",
                    "Implement basic search improvements"
                ],
                "success_criteria": ["<500 files per category", "No placeholder categories", "Type-based search working"]
            },
            {
                "phase": 2,
                "name": "Strategic Splits & Merges",
                "duration": "2-3 days", 
                "actions": [
                    "Execute planned split operations",
                    "Merge small categories",
                    "Implement semantic search grouping"
                ],
                "success_criteria": ["Balanced category sizes", "Clear category purposes", "Enhanced search UX"]
            },
            {
                "phase": 3,
                "name": "Optimization & Maintenance",
                "duration": "1 day",
                "actions": [
                    "Clean up outdated content",
                    "Implement relevancy ranking",
                    "Set up maintenance automation"
                ],
                "success_criteria": [">80% relevancy scores", "Automated maintenance", "User satisfaction"]
            }
        ]
        
        return phases
    
    def save_roadmap(self, roadmap: Dict) -> Path:
        """Save updated roadmap to file"""
        output_file = self.base_path / f"mixed_categories_roadmap_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(roadmap, f, indent=2)
        
        return output_file

def main():
    updater = NextStepsUpdater()
    
    print("🔄 Generating updated roadmap with mixed categories insights...")
    roadmap = updater.generate_updated_roadmap()
    
    print("\n🎯 Updated Next Steps")
    print("=" * 20)
    
    print(f"\n🚨 Critical Findings ({len(roadmap['critical_findings'])}):")
    for finding in roadmap['critical_findings']:
        print(f"  • {finding}")
    
    print(f"\n⚡ Immediate Priorities ({len(roadmap['immediate_priorities'])}):")
    for priority in roadmap['immediate_priorities'][:3]:
        urgency_emoji = {"critical": "🔴", "high": "🟡", "medium": "🟠"}[priority['urgency']]
        print(f"  {urgency_emoji} {priority['action']}")
        print(f"    Time: {priority['estimated_time']} | Type: {priority['type']}")
    
    print(f"\n📋 Implementation Phases:")
    for phase in roadmap['implementation_phases']:
        print(f"\n  Phase {phase['phase']}: {phase['name']} ({phase['duration']})")
        for action in phase['actions']:
            print(f"    • {action}")
    
    # Save roadmap
    output_file = updater.save_roadmap(roadmap)
    print(f"\n💾 Detailed roadmap saved to: {output_file}")
    
    print(f"\n🎯 Next Commands:")
    print(f"  python3 mixed_categories_analyzer.py analyze --category discussions")
    print(f"  python3 dashboard.py summary")
    print(f"  python3 roadmap_discussions.py optimize")

if __name__ == "__main__":
    main()
