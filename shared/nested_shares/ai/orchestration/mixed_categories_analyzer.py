#!/usr/bin/env python3
"""Mixed Categories Analyzer - Advanced categorization and optimization strategies"""

import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class CategoryAnalysis:
    name: str
    file_count: int
    mixed_types: List[str]
    relevancy_score: float
    creation_pattern: str  # creational, placeholder, legacy, active
    split_candidates: List[str]
    merge_candidates: List[str]
    priority: str  # critical, high, medium, low

class MixedCategoriesAnalyzer:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares")
        self.file_patterns = {
            'code': ['.py', '.js', '.sh', '.ts', '.go', '.rs'],
            'docs': ['.md', '.txt', '.rst', '.adoc'],
            'config': ['.json', '.yaml', '.yml', '.toml', '.ini', '.conf'],
            'data': ['.csv', '.xml', '.sql', '.db'],
            'templates': ['.template', '.example', '.sample'],
            'tests': ['test_', '_test.', 'spec_', '.test.'],
            'backup': ['.bak', '.backup', '.old', '.orig'],
            'temp': ['.tmp', '.temp', '.cache']
        }
    
    def analyze_all_categories(self) -> Dict[str, CategoryAnalysis]:
        """Analyze all categories for mixed content and optimization opportunities"""
        analyses = {}
        
        for category_dir in self.workspace_path.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith('.'):
                analysis = self._analyze_category(category_dir)
                analyses[category_dir.name] = analysis
        
        return analyses
    
    def _analyze_category(self, category_path: Path) -> CategoryAnalysis:
        """Deep analysis of single category"""
        files = list(category_path.rglob("*"))
        files = [f for f in files if f.is_file() and not f.name.startswith('.')]
        
        # Analyze file type distribution
        type_distribution = self._get_type_distribution(files)
        mixed_types = [t for t, count in type_distribution.items() if count > 0]
        
        # Calculate relevancy score
        relevancy_score = self._calculate_relevancy(files)
        
        # Determine creation pattern
        creation_pattern = self._determine_creation_pattern(files, category_path)
        
        # Find split/merge opportunities
        split_candidates = self._find_split_opportunities(files, type_distribution)
        merge_candidates = self._find_merge_opportunities(category_path.name, type_distribution)
        
        # Calculate priority
        priority = self._calculate_priority(len(files), len(mixed_types), relevancy_score, creation_pattern)
        
        return CategoryAnalysis(
            name=category_path.name,
            file_count=len(files),
            mixed_types=mixed_types,
            relevancy_score=relevancy_score,
            creation_pattern=creation_pattern,
            split_candidates=split_candidates,
            merge_candidates=merge_candidates,
            priority=priority
        )
    
    def _get_type_distribution(self, files: List[Path]) -> Dict[str, int]:
        """Analyze distribution of file types"""
        distribution = defaultdict(int)
        
        for file_path in files:
            file_type = self._classify_file(file_path)
            distribution[file_type] += 1
        
        return dict(distribution)
    
    def _classify_file(self, file_path: Path) -> str:
        """Classify file into type category"""
        name = file_path.name.lower()
        suffix = file_path.suffix.lower()
        
        # Check patterns in order of specificity
        for pattern_type, patterns in self.file_patterns.items():
            for pattern in patterns:
                if pattern.startswith('.') and suffix == pattern:
                    return pattern_type
                elif not pattern.startswith('.') and pattern in name:
                    return pattern_type
        
        # Special cases
        if 'readme' in name or 'license' in name:
            return 'docs'
        elif 'dockerfile' in name or 'makefile' in name:
            return 'config'
        elif name.endswith('rc') or name.startswith('.'):
            return 'config'
        
        return 'misc'
    
    def _calculate_relevancy(self, files: List[Path]) -> float:
        """Calculate relevancy score based on file age and usage patterns"""
        if not files:
            return 0.0
        
        now = datetime.now()
        scores = []
        
        for file_path in files:
            try:
                # Get file modification time
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                age_days = (now - mtime).days
                
                # Score based on recency (0-1 scale)
                if age_days <= 7:
                    age_score = 1.0
                elif age_days <= 30:
                    age_score = 0.8
                elif age_days <= 90:
                    age_score = 0.6
                elif age_days <= 365:
                    age_score = 0.4
                else:
                    age_score = 0.2
                
                # Boost score for important files
                name = file_path.name.lower()
                if any(keyword in name for keyword in ['main', 'index', 'core', 'primary']):
                    age_score *= 1.2
                elif any(keyword in name for keyword in ['test', 'example', 'sample']):
                    age_score *= 0.8
                elif any(keyword in name for keyword in ['old', 'backup', 'deprecated']):
                    age_score *= 0.3
                
                scores.append(min(1.0, age_score))
                
            except (OSError, ValueError):
                scores.append(0.5)  # Default for inaccessible files
        
        return sum(scores) / len(scores)
    
    def _determine_creation_pattern(self, files: List[Path], category_path: Path) -> str:
        """Determine if category is creational, placeholder, legacy, or active"""
        if len(files) == 0:
            return "placeholder"
        
        # Check for placeholder indicators
        placeholder_indicators = ['todo', 'placeholder', 'empty', 'template']
        if any(indicator in category_path.name.lower() for indicator in placeholder_indicators):
            return "placeholder"
        
        # Check file names for patterns
        file_names = [f.name.lower() for f in files]
        
        # Creational pattern - lots of templates, examples, generators
        creational_count = sum(1 for name in file_names 
                             if any(word in name for word in ['template', 'generator', 'creator', 'builder', 'factory']))
        
        # Legacy pattern - old files, deprecated, backup
        legacy_count = sum(1 for name in file_names 
                          if any(word in name for word in ['old', 'legacy', 'deprecated', 'backup', 'archive']))
        
        total_files = len(files)
        
        if creational_count / total_files > 0.3:
            return "creational"
        elif legacy_count / total_files > 0.4:
            return "legacy"
        elif total_files < 3:
            return "placeholder"
        else:
            return "active"
    
    def _find_split_opportunities(self, files: List[Path], type_distribution: Dict[str, int]) -> List[str]:
        """Find opportunities to split mixed categories"""
        opportunities = []
        total_files = len(files)
        
        if total_files < 10:
            return opportunities
        
        # Check for dominant secondary types
        sorted_types = sorted(type_distribution.items(), key=lambda x: x[1], reverse=True)
        
        for file_type, count in sorted_types[1:]:  # Skip the dominant type
            percentage = count / total_files
            
            if percentage > 0.25 and count > 5:  # Significant minority
                opportunities.append(f"Split {file_type} files ({count} files, {percentage:.1%}) into separate category")
        
        # Check for functional groupings
        if type_distribution.get('tests', 0) > 3:
            opportunities.append("Move test files to dedicated testing category")
        
        if type_distribution.get('config', 0) > 5:
            opportunities.append("Extract configuration files to config category")
        
        return opportunities
    
    def _find_merge_opportunities(self, category_name: str, type_distribution: Dict[str, int]) -> List[str]:
        """Find opportunities to merge with other categories"""
        opportunities = []
        total_files = sum(type_distribution.values())
        
        # Small categories are merge candidates
        if total_files < 5:
            dominant_type = max(type_distribution.items(), key=lambda x: x[1])[0] if type_distribution else 'misc'
            opportunities.append(f"Merge into {dominant_type} category (only {total_files} files)")
        
        # Single-type categories might belong elsewhere
        if len(type_distribution) == 1:
            file_type = list(type_distribution.keys())[0]
            if file_type != 'misc':
                opportunities.append(f"Consider merging into existing {file_type} category")
        
        # Check for semantic similarity
        similar_categories = self._find_semantically_similar_categories(category_name)
        for similar in similar_categories:
            opportunities.append(f"Consider merging with {similar} (semantic similarity)")
        
        return opportunities
    
    def _find_semantically_similar_categories(self, category_name: str) -> List[str]:
        """Find categories with similar semantic meaning"""
        # Simple semantic groupings
        semantic_groups = {
            'ai': ['artificial-intelligence', 'machine-learning', 'ml', 'neural', 'model'],
            'web': ['http', 'api', 'rest', 'server', 'client', 'frontend', 'backend'],
            'data': ['database', 'db', 'storage', 'persistence', 'cache'],
            'test': ['testing', 'spec', 'validation', 'qa', 'quality'],
            'config': ['configuration', 'settings', 'env', 'environment'],
            'docs': ['documentation', 'readme', 'guide', 'manual', 'help'],
            'tools': ['utilities', 'utils', 'helpers', 'scripts'],
            'core': ['base', 'foundation', 'common', 'shared', 'lib']
        }
        
        similar = []
        name_lower = category_name.lower()
        
        for group_key, synonyms in semantic_groups.items():
            if name_lower == group_key or name_lower in synonyms:
                # Find other categories in workspace that match this group
                for other_dir in self.workspace_path.iterdir():
                    if other_dir.is_dir() and other_dir.name != category_name:
                        other_name = other_dir.name.lower()
                        if other_name == group_key or other_name in synonyms:
                            similar.append(other_dir.name)
        
        return similar
    
    def _calculate_priority(self, file_count: int, mixed_types: int, relevancy: float, pattern: str) -> str:
        """Calculate optimization priority"""
        score = 0
        
        # File count factor
        if file_count > 100:
            score += 3
        elif file_count > 50:
            score += 2
        elif file_count > 10:
            score += 1
        
        # Mixed types factor
        if mixed_types > 4:
            score += 3
        elif mixed_types > 2:
            score += 2
        elif mixed_types > 1:
            score += 1
        
        # Relevancy factor (inverted - low relevancy = high priority for cleanup)
        if relevancy < 0.3:
            score += 3
        elif relevancy < 0.6:
            score += 2
        elif relevancy < 0.8:
            score += 1
        
        # Pattern factor
        pattern_scores = {
            'placeholder': 3,
            'legacy': 2,
            'creational': 1,
            'active': 0
        }
        score += pattern_scores.get(pattern, 1)
        
        # Convert to priority level
        if score >= 8:
            return "critical"
        elif score >= 5:
            return "high"
        elif score >= 3:
            return "medium"
        else:
            return "low"
    
    def generate_optimization_strategy(self, analyses: Dict[str, CategoryAnalysis]) -> Dict:
        """Generate comprehensive optimization strategy"""
        strategy = {
            "immediate_actions": [],
            "split_operations": [],
            "merge_operations": [],
            "cleanup_targets": [],
            "search_improvements": [],
            "priority_matrix": {"critical": [], "high": [], "medium": [], "low": []}
        }
        
        for name, analysis in analyses.items():
            # Add to priority matrix
            strategy["priority_matrix"][analysis.priority].append(name)
            
            # Immediate actions for critical/high priority
            if analysis.priority in ["critical", "high"]:
                if analysis.creation_pattern == "placeholder":
                    strategy["immediate_actions"].append(f"Remove or populate placeholder category: {name}")
                elif analysis.creation_pattern == "legacy":
                    strategy["cleanup_targets"].append(f"Archive legacy files in {name}")
                elif len(analysis.mixed_types) > 3:
                    strategy["immediate_actions"].append(f"Reorganize mixed category: {name}")
            
            # Split operations
            if analysis.split_candidates:
                strategy["split_operations"].extend([
                    f"{name}: {candidate}" for candidate in analysis.split_candidates
                ])
            
            # Merge operations
            if analysis.merge_candidates:
                strategy["merge_operations"].extend([
                    f"{name}: {candidate}" for candidate in analysis.merge_candidates
                ])
            
            # Search improvements
            if len(analysis.mixed_types) > 2:
                strategy["search_improvements"].append(
                    f"Add type-specific search for {name} ({', '.join(analysis.mixed_types)})"
                )
        
        return strategy

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Mixed categories analyzer")
    parser.add_argument("command", choices=["analyze", "strategy", "priority", "search"])
    parser.add_argument("--category", help="Analyze specific category")
    
    args = parser.parse_args()
    analyzer = MixedCategoriesAnalyzer()
    
    if args.command == "analyze":
        if args.category:
            # Analyze single category
            category_path = analyzer.workspace_path / args.category
            if category_path.exists():
                analysis = analyzer._analyze_category(category_path)
                print(f"📊 Analysis: {analysis.name}")
                print(f"Files: {analysis.file_count}")
                print(f"Mixed Types: {', '.join(analysis.mixed_types)}")
                print(f"Relevancy: {analysis.relevancy_score:.1%}")
                print(f"Pattern: {analysis.creation_pattern}")
                print(f"Priority: {analysis.priority}")
            else:
                print(f"❌ Category not found: {args.category}")
        else:
            # Analyze all categories
            analyses = analyzer.analyze_all_categories()
            
            print("📊 Mixed Categories Analysis")
            print("=" * 30)
            
            for name, analysis in sorted(analyses.items(), key=lambda x: x[1].file_count, reverse=True):
                priority_emoji = {"critical": "🔴", "high": "🟡", "medium": "🟠", "low": "🟢"}[analysis.priority]
                print(f"\n{name} {priority_emoji}")
                print(f"  Files: {analysis.file_count} | Types: {len(analysis.mixed_types)} | Relevancy: {analysis.relevancy_score:.1%}")
                print(f"  Pattern: {analysis.creation_pattern} | Mixed: {', '.join(analysis.mixed_types[:3])}")
    
    elif args.command == "strategy":
        analyses = analyzer.analyze_all_categories()
        strategy = analyzer.generate_optimization_strategy(analyses)
        
        print("🎯 Optimization Strategy")
        print("=" * 25)
        
        if strategy["immediate_actions"]:
            print(f"\n🚨 Immediate Actions ({len(strategy['immediate_actions'])}):")
            for action in strategy["immediate_actions"][:5]:
                print(f"  • {action}")
        
        if strategy["split_operations"]:
            print(f"\n✂️  Split Operations ({len(strategy['split_operations'])}):")
            for op in strategy["split_operations"][:3]:
                print(f"  • {op}")
        
        if strategy["merge_operations"]:
            print(f"\n🔗 Merge Operations ({len(strategy['merge_operations'])}):")
            for op in strategy["merge_operations"][:3]:
                print(f"  • {op}")
        
        if strategy["cleanup_targets"]:
            print(f"\n🧹 Cleanup Targets ({len(strategy['cleanup_targets'])}):")
            for target in strategy["cleanup_targets"]:
                print(f"  • {target}")
    
    elif args.command == "priority":
        analyses = analyzer.analyze_all_categories()
        strategy = analyzer.generate_optimization_strategy(analyses)
        
        print("📋 Priority Matrix")
        print("=" * 16)
        
        for priority in ["critical", "high", "medium", "low"]:
            categories = strategy["priority_matrix"][priority]
            if categories:
                emoji = {"critical": "🔴", "high": "🟡", "medium": "🟠", "low": "🟢"}[priority]
                print(f"\n{emoji} {priority.upper()} ({len(categories)}):")
                for cat in categories:
                    analysis = analyses[cat]
                    print(f"  • {cat}: {analysis.file_count} files, {analysis.creation_pattern}")
    
    elif args.command == "search":
        analyses = analyzer.analyze_all_categories()
        strategy = analyzer.generate_optimization_strategy(analyses)
        
        print("🔍 Search Strategy Improvements")
        print("=" * 30)
        
        for improvement in strategy["search_improvements"]:
            print(f"  • {improvement}")
        
        # Additional search recommendations
        print(f"\n💡 Recommended Search Enhancements:")
        print(f"  • Add file type filters for mixed categories")
        print(f"  • Implement semantic search across similar categories")
        print(f"  • Create category-specific search shortcuts")
        print(f"  • Add relevancy-based result ranking")

if __name__ == "__main__":
    main()
