#!/usr/bin/env python3
"""Automated Duplicate Code Snippet Detection - Lean improvement workflow for small duplicates (<1KB)"""

from shared_tools.utils.config_utils import get_workspace_path
import json
import hashlib
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from lean_systematic_improvements import LeanSystematicImprovements

class AutomatedDuplicateDetection:
    def __init__(self):
        self.lean_improvements = LeanSystematicImprovements()
        self.workspace_path = get_workspace_path()
        self.file_registry_path = self.workspace_path / "workspace-automation" / "file_registry.json"
        self.results_path = self.workspace_path / ".versions" / "duplicate_detection_results.json"
        
    def load_file_registry(self) -> dict:
        """Load file registry for target identification"""
        if self.file_registry_path.exists():
            try:
                with open(self.file_registry_path) as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def extract_code_snippets(self, file_path: str, max_size: int = 1024) -> list:
        """Extract code snippets under max_size bytes"""
        
        try:
            content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
            
            # Skip if file is too large
            if len(content) > 50000:  # Skip files > 50KB
                return []
            
            snippets = []
            
            # Extract function definitions
            function_patterns = [
                r'def\s+\w+\([^)]*\):[^}]+?(?=\n\s*def|\n\s*class|\Z)',  # Python functions
                r'function\s+\w+\([^)]*\)\s*{[^}]+}',  # JS functions
                r'[a-zA-Z_]\w*\s*\([^)]*\)\s*{[^}]+}',  # C-style functions
            ]
            
            for pattern in function_patterns:
                matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
                for match in matches:
                    snippet = match.group().strip()
                    if 50 < len(snippet) <= max_size:  # Between 50 bytes and 1KB
                        snippets.append({
                            'content': snippet,
                            'start_pos': match.start(),
                            'end_pos': match.end(),
                            'type': 'function',
                            'hash': hashlib.md5(snippet.encode()).hexdigest()
                        })
            
            # Extract class definitions (small ones)
            class_patterns = [
                r'class\s+\w+[^{]*{[^}]+}',  # Simple classes
                r'class\s+\w+.*?:\s*\n(?:\s{4}.*\n)*',  # Python classes (indented)
            ]
            
            for pattern in class_patterns:
                matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
                for match in matches:
                    snippet = match.group().strip()
                    if 50 < len(snippet) <= max_size:
                        snippets.append({
                            'content': snippet,
                            'start_pos': match.start(),
                            'end_pos': match.end(),
                            'type': 'class',
                            'hash': hashlib.md5(snippet.encode()).hexdigest()
                        })
            
            return snippets
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return []
    
    def find_duplicate_snippets(self, target_files: list) -> dict:
        """Find duplicate code snippets across target files"""
        
        print(f"🔍 ANALYZING {len(target_files)} files for duplicate snippets...")
        
        snippet_map = defaultdict(list)  # hash -> list of (file, snippet_info)
        file_snippets = {}  # file -> snippets
        
        # Extract snippets from all files
        for file_path in target_files:
            snippets = self.extract_code_snippets(file_path)
            if snippets:
                file_snippets[file_path] = snippets
                
                for snippet in snippets:
                    snippet_map[snippet['hash']].append({
                        'file': file_path,
                        'snippet': snippet
                    })
        
        # Find duplicates (hash appears in multiple files)
        duplicates = {}
        for snippet_hash, occurrences in snippet_map.items():
            if len(occurrences) >= 2:  # Duplicate found
                duplicates[snippet_hash] = {
                    'occurrences': occurrences,
                    'count': len(occurrences),
                    'size': len(occurrences[0]['snippet']['content']),
                    'type': occurrences[0]['snippet']['type'],
                    'content_preview': occurrences[0]['snippet']['content'][:100] + "..."
                }
        
        print(f"   📊 Found {len(duplicates)} duplicate snippets")
        print(f"   📁 Processed {len(file_snippets)} files with code")
        
        return {
            'duplicates': duplicates,
            'file_snippets': file_snippets,
            'analysis_timestamp': datetime.now().isoformat(),
            'total_files_analyzed': len(target_files),
            'files_with_code': len(file_snippets)
        }
    
    def prioritize_duplicates(self, duplicates: dict) -> list:
        """Prioritize duplicates for improvement"""
        
        priority_list = []
        
        for snippet_hash, duplicate_info in duplicates.items():
            # Calculate priority score
            count = duplicate_info['count']
            size = duplicate_info['size']
            
            # Priority factors:
            # - More occurrences = higher priority
            # - Larger size = higher priority  
            # - Functions > classes (easier to refactor)
            type_weight = 1.2 if duplicate_info['type'] == 'function' else 1.0
            
            priority_score = (count * 2) + (size / 100) * type_weight
            
            priority_list.append({
                'hash': snippet_hash,
                'priority_score': priority_score,
                'count': count,
                'size': size,
                'type': duplicate_info['type'],
                'files': [occ['file'] for occ in duplicate_info['occurrences']],
                'content_preview': duplicate_info['content_preview']
            })
        
        # Sort by priority score (highest first)
        priority_list.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return priority_list
    
    def create_improvement_tags(self, priority_list: list) -> dict:
        """Create improvement tags for duplicate snippets"""
        
        tags = {
            'high_priority': [],    # Score > 10
            'medium_priority': [],  # Score 5-10
            'low_priority': [],     # Score < 5
            'refactor_candidates': [],  # Functions with 3+ duplicates
            'merge_candidates': []      # Small snippets with 2 duplicates
        }
        
        for item in priority_list:
            score = item['priority_score']
            count = item['count']
            size = item['size']
            
            # Priority tagging
            if score > 10:
                tags['high_priority'].append(item)
            elif score >= 5:
                tags['medium_priority'].append(item)
            else:
                tags['low_priority'].append(item)
            
            # Improvement strategy tagging
            if count >= 3 and item['type'] == 'function':
                tags['refactor_candidates'].append(item)
            elif count == 2 and size < 300:
                tags['merge_candidates'].append(item)
        
        return tags
    
    def run_automated_detection(self) -> dict:
        """Run complete automated duplicate detection workflow"""
        
        print("🚀 AUTOMATED DUPLICATE DETECTION WORKFLOW")
        print("Target: Small code snippets (<1KB) for merging/refactoring\n")
        
        # 1. Load file registry to identify targets
        file_registry = self.load_file_registry()
        
        # Filter for code files
        target_files = []
        for file_path, file_info in file_registry.items():
            if file_info.get('name', '').endswith(('.py', '.js', '.sh', '.cpp', '.java')):
                # Handle relative paths from registry
                if file_path.startswith('workspace-automation/'):
                    # Remove duplicate workspace-automation prefix
                    clean_path = file_path.replace('workspace-automation/workspace-automation/', 'workspace-automation/')
                    full_path = self.workspace_path / clean_path
                else:
                    full_path = self.workspace_path / file_path
                    
                if full_path.exists():
                    target_files.append(str(full_path))
        
        print(f"📋 Target files from registry: {len(target_files)}")
        
        # 2. Find duplicate snippets
        analysis_results = self.find_duplicate_snippets(target_files)
        
        # 3. Prioritize duplicates
        priority_list = self.prioritize_duplicates(analysis_results['duplicates'])
        
        # 4. Create improvement tags
        improvement_tags = self.create_improvement_tags(priority_list)
        
        # 5. Compile final results
        workflow_results = {
            'workflow_type': 'automated_duplicate_detection',
            'analysis_results': analysis_results,
            'priority_list': priority_list[:20],  # Top 20
            'improvement_tags': improvement_tags,
            'summary': {
                'total_duplicates': len(analysis_results['duplicates']),
                'high_priority': len(improvement_tags['high_priority']),
                'refactor_candidates': len(improvement_tags['refactor_candidates']),
                'merge_candidates': len(improvement_tags['merge_candidates']),
                'files_analyzed': analysis_results['total_files_analyzed']
            },
            'next_actions': [
                "Review high_priority duplicates for immediate action",
                "Plan refactoring for refactor_candidates", 
                "Consider merging merge_candidates",
                "Use lean_improvement_workflow() for selected duplicates"
            ]
        }
        
        # 6. Save results
        self.results_path.write_text(json.dumps(workflow_results, indent=2))
        
        # 7. Display summary
        print(f"\n📊 DETECTION RESULTS:")
        print(f"   Total duplicates found: {workflow_results['summary']['total_duplicates']}")
        print(f"   High priority: {workflow_results['summary']['high_priority']}")
        print(f"   Refactor candidates: {workflow_results['summary']['refactor_candidates']}")
        print(f"   Merge candidates: {workflow_results['summary']['merge_candidates']}")
        
        print(f"\n🎯 TOP 5 DUPLICATES:")
        for i, item in enumerate(priority_list[:5], 1):
            print(f"   {i}. {item['type']} ({item['count']} files, {item['size']} bytes, score: {item['priority_score']:.1f})")
            print(f"      Files: {', '.join([Path(f).name for f in item['files']])}")
        
        print(f"\n💾 Results saved: {self.results_path}")
        
        return workflow_results

def main():
    """Run automated duplicate detection workflow"""
    
    detector = AutomatedDuplicateDetection()
    results = detector.run_automated_detection()
    
    print(f"\n✅ AUTOMATED DUPLICATE DETECTION COMPLETE")
    print(f"🎯 Ready for lean improvement workflows on identified duplicates!")

if __name__ == "__main__":
    main()
