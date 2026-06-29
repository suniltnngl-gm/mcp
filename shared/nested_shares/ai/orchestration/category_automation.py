#!/usr/bin/env python3
"""Category Split/Merge Automation - Automated optimization based on thresholds and patterns"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

class CategoryAutomation:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares")
        
        # Thresholds for automation
        self.thresholds = {
            'split_threshold': 100,      # Split if > 100 files
            'merge_threshold': 5,        # Merge if < 5 files
            'diversity_threshold': 4,    # Split if > 4 file types
            'subcategory_threshold': 20, # Create subcategory if > 20 files of same type
        }
        
        self.file_types = {
            'python': ['.py'],
            'shell': ['.sh'],
            'javascript': ['.js', '.ts'],
            'config': ['.json', '.yaml', '.yml', '.toml', '.ini'],
            'docs': ['.md', '.txt', '.rst'],
            'data': ['.csv', '.jsonl', '.xml']
        }
        
        self.automation_log = []
    
    def _get_file_type(self, file_path: Path) -> str:
        """Determine file type from extension"""
        suffix = file_path.suffix.lower()
        for type_name, extensions in self.file_types.items():
            if suffix in extensions:
                return type_name
        return 'other'
    
    def _analyze_category(self, cat_path: Path) -> Dict:
        """Analyze a single category"""
        files = [f for f in cat_path.rglob("*") if f.is_file()]
        file_types = defaultdict(int)
        
        for file_path in files:
            file_type = self._get_file_type(file_path)
            file_types[file_type] += 1
        
        return {
            'file_count': len(files),
            'file_types': dict(file_types),
            'subcategories': [d.name for d in cat_path.iterdir() if d.is_dir()]
        }
    
    def analyze_automation_opportunities(self) -> Dict:
        """Analyze categories for automated split/merge opportunities"""
        opportunities = {
            'auto_splits': [],
            'auto_merges': [],
            'subcategory_creation': [],
            'recommendations': []
        }
        
        # Analyze each category
        for cat_dir in self.workspace_path.iterdir():
            if not cat_dir.is_dir() or cat_dir.name.startswith('.'):
                continue
            
            cat_info = self._analyze_category(cat_dir)
            cat_name = cat_dir.name
            file_count = cat_info['file_count']
            file_types = len(cat_info['file_types'])
            
            # Check for auto-split opportunities
            if file_count > self.thresholds['split_threshold']:
                split_strategy = self._determine_split_strategy(cat_name, cat_info)
                opportunities['auto_splits'].append({
                    'category': cat_name,
                    'files': file_count,
                    'strategy': split_strategy,
                    'priority': 'high' if file_count > 200 else 'medium'
                })
            
            # Check for auto-merge opportunities
            elif file_count < self.thresholds['merge_threshold'] and file_count > 0:
                merge_target = self._find_merge_target(cat_name, cat_info)
                opportunities['auto_merges'].append({
                    'category': cat_name,
                    'files': file_count,
                    'target': merge_target,
                    'priority': 'low'
                })
            
            # Check for subcategory creation
            if file_types > self.thresholds['diversity_threshold']:
                subcats = self._suggest_subcategories(cat_name, cat_info)
                if subcats:
                    opportunities['subcategory_creation'].append({
                        'category': cat_name,
                        'subcategories': subcats,
                        'priority': 'medium'
                    })
        
        # Generate recommendations
        opportunities['recommendations'] = self._generate_recommendations(opportunities)
        
        return opportunities
    
    def _determine_split_strategy(self, category: str, cat_info: Dict) -> Dict:
        """Determine best split strategy for a category"""
        file_types = cat_info['file_types']
        
        # Type-based split if diverse file types
        if len(file_types) >= 3:
            return {
                'type': 'by_file_type',
                'splits': [f"{category}-{ftype}" for ftype in file_types.keys() if file_types[ftype] > 10]
            }
        
        # Size-based split if homogeneous
        return {
            'type': 'by_size',
            'splits': [f"{category}-part1", f"{category}-part2"]
        }
    
    def _find_merge_target(self, category: str, cat_info: Dict) -> str:
        """Find best merge target for small category"""
        # Simple heuristic: merge into category with similar file types
        dominant_type = max(cat_info['file_types'].items(), key=lambda x: x[1])[0]
        
        if dominant_type == 'python':
            return 'core'
        elif dominant_type == 'shell':
            return 'workflow'
        elif dominant_type in ['config', 'data']:
            return 'utilities'
        else:
            return 'utilities'
    
    def _suggest_subcategories(self, category: str, cat_info: Dict) -> List[str]:
        """Suggest subcategory structure for diverse categories"""
        subcats = []
        
        for file_type, count in cat_info['file_types'].items():
            if count > self.thresholds['subcategory_threshold']:
                subcats.append(f"{file_type}-files")
        
        return subcats
    
    def _generate_recommendations(self, opportunities: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recs = []
        
        if opportunities['auto_splits']:
            high_priority = [s for s in opportunities['auto_splits'] if s['priority'] == 'high']
            if high_priority:
                recs.append(f"URGENT: Split {len(high_priority)} oversized categories immediately")
        
        if len(opportunities['auto_merges']) > 3:
            recs.append(f"Consider merging {len(opportunities['auto_merges'])} small categories")
        
        if opportunities['subcategory_creation']:
            recs.append("Create subcategories for better organization")
        
        return recs
    
    def execute_automation(self, dry_run: bool = True) -> Dict:
        """Execute automated optimizations"""
        results = {
            'executed': [],
            'skipped': [],
            'errors': []
        }
        
        opportunities = self.analyze_automation_opportunities()
        
        # Execute high-priority splits first
        for split_op in opportunities['auto_splits']:
            if split_op['priority'] == 'high':
                try:
                    if not dry_run:
                        self._execute_split(split_op)
                    results['executed'].append(f"Split {split_op['category']}")
                    self.automation_log.append({
                        'action': 'split',
                        'category': split_op['category'],
                        'strategy': split_op['strategy']
                    })
                except Exception as e:
                    results['errors'].append(f"Split {split_op['category']}: {str(e)}")
        
        # Execute merges for small categories
        for merge_op in opportunities['auto_merges']:
            try:
                if not dry_run:
                    self._execute_merge(merge_op)
                results['executed'].append(f"Merge {merge_op['category']} → {merge_op['target']}")
                self.automation_log.append({
                    'action': 'merge',
                    'source': merge_op['category'],
                    'target': merge_op['target']
                })
            except Exception as e:
                results['errors'].append(f"Merge {merge_op['category']}: {str(e)}")
        
        return results
    
    def _execute_split(self, split_op: Dict):
        """Execute category split operation"""
        category = split_op['category']
        strategy = split_op['strategy']
        
        if strategy['type'] == 'by_file_type':
            # Use existing splitter for type-based splits
            self.splitter.split_by_file_type(category)
        else:
            # Simple size-based split
            self.splitter.split_by_size(category, 2)
    
    def _execute_merge(self, merge_op: Dict):
        """Execute category merge operation"""
        source = merge_op['category']
        target = merge_op['target']
        
        # Use existing merger
        source_path = self.workspace_path / source
        target_path = self.workspace_path / target
        
        if source_path.exists() and target_path.exists():
            # Move files to target as subcategory
            target_subcat = target_path / source
            target_subcat.mkdir(exist_ok=True)
            
            for item in source_path.iterdir():
                item.rename(target_subcat / item.name)
            
            source_path.rmdir()
    
    def get_automation_schedule(self) -> Dict:
        """Generate automation schedule based on patterns"""
        opportunities = self.analyze_automation_opportunities()
        
        schedule = {
            'immediate': [],
            'weekly': [],
            'monthly': []
        }
        
        # Immediate: High-priority splits
        for split_op in opportunities['auto_splits']:
            if split_op['priority'] == 'high':
                schedule['immediate'].append({
                    'action': f"Split {split_op['category']}",
                    'reason': f"{split_op['files']} files exceed threshold"
                })
        
        # Weekly: Medium-priority optimizations
        for split_op in opportunities['auto_splits']:
            if split_op['priority'] == 'medium':
                schedule['weekly'].append({
                    'action': f"Consider splitting {split_op['category']}",
                    'reason': f"{split_op['files']} files approaching threshold"
                })
        
        # Monthly: Low-priority merges
        for merge_op in opportunities['auto_merges']:
            schedule['monthly'].append({
                'action': f"Merge {merge_op['category']} → {merge_op['target']}",
                'reason': f"Only {merge_op['files']} files"
            })
        
        return schedule
    
    def save_automation_config(self, config_path: str = None):
        """Save automation configuration and thresholds"""
        if not config_path:
            config_path = self.workspace_path / "automation_config.json"
        
        config = {
            'thresholds': self.thresholds,
            'automation_log': self.automation_log,
            'last_analysis': self.analyze_automation_opportunities()
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

def main():
    import sys
    
    automation = CategoryAutomation()
    
    if len(sys.argv) < 2:
        print("Usage: python3 category_automation.py <command>")
        print("Commands:")
        print("  analyze     - Analyze automation opportunities")
        print("  schedule    - Show automation schedule")
        print("  execute     - Execute automation (dry-run)")
        print("  run         - Execute automation (real)")
        print("  config      - Save automation config")
        return
    
    command = sys.argv[1]
    
    if command == 'analyze':
        opportunities = automation.analyze_automation_opportunities()
        
        print("🤖 Category Automation Analysis")
        print("=" * 35)
        
        if opportunities['auto_splits']:
            print(f"\n📈 Auto-Split Opportunities ({len(opportunities['auto_splits'])}):")
            for split in opportunities['auto_splits']:
                print(f"  • {split['category']}: {split['files']} files ({split['priority']} priority)")
                print(f"    └─ Strategy: {split['strategy']['type']}")
        
        if opportunities['auto_merges']:
            print(f"\n📉 Auto-Merge Opportunities ({len(opportunities['auto_merges'])}):")
            for merge in opportunities['auto_merges']:
                print(f"  • {merge['category']}: {merge['files']} files → {merge['target']}")
        
        if opportunities['subcategory_creation']:
            print(f"\n📂 Subcategory Suggestions ({len(opportunities['subcategory_creation'])}):")
            for subcat in opportunities['subcategory_creation']:
                print(f"  • {subcat['category']}: {', '.join(subcat['subcategories'])}")
        
        if opportunities['recommendations']:
            print("\n💡 Recommendations:")
            for rec in opportunities['recommendations']:
                print(f"  • {rec}")
    
    elif command == 'schedule':
        schedule = automation.get_automation_schedule()
        
        print("📅 Automation Schedule")
        print("=" * 25)
        
        if schedule['immediate']:
            print("\n🚨 Immediate Actions:")
            for action in schedule['immediate']:
                print(f"  • {action['action']}")
                print(f"    └─ {action['reason']}")
        
        if schedule['weekly']:
            print("\n📊 Weekly Review:")
            for action in schedule['weekly']:
                print(f"  • {action['action']}")
                print(f"    └─ {action['reason']}")
        
        if schedule['monthly']:
            print("\n🔄 Monthly Cleanup:")
            for action in schedule['monthly']:
                print(f"  • {action['action']}")
                print(f"    └─ {action['reason']}")
    
    elif command in ['execute', 'run']:
        dry_run = command == 'execute'
        results = automation.execute_automation(dry_run=dry_run)
        
        mode = "DRY RUN" if dry_run else "EXECUTION"
        print(f"🤖 Automation {mode}")
        print("=" * 25)
        
        if results['executed']:
            print(f"\n✅ Actions {'Planned' if dry_run else 'Executed'} ({len(results['executed'])}):")
            for action in results['executed']:
                print(f"  • {action}")
        
        if results['errors']:
            print(f"\n❌ Errors ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"  • {error}")
        
        if not results['executed'] and not results['errors']:
            print("\n✨ No automation actions needed")
    
    elif command == 'config':
        automation.save_automation_config()
        print("✅ Automation config saved")

if __name__ == "__main__":
    main()
