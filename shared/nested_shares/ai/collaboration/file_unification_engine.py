#!/usr/bin/env python3
"""File Unification Engine for roadmap/todo/progress consolidation"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass

@dataclass
class FileContent:
    path: str
    type: str  # 'roadmap', 'todo', 'progress'
    content: str
    metadata: Dict

class FileUnificationEngine:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.ignore_patterns = {'.venv', 'node_modules', '__pycache__', '.git'}
        
    def scan_files(self) -> List[FileContent]:
        """Scan workspace for roadmap/todo/progress files"""
        files = []
        patterns = {
            'roadmap': r'.*roadmap.*\.(md|json|txt)$',
            'todo': r'.*todo.*\.(md|json|txt)$', 
            'progress': r'.*progress.*\.(md|json|txt)$'
        }
        
        for file_path in self.workspace_path.rglob('*'):
            if any(ignore in str(file_path) for ignore in self.ignore_patterns):
                continue
                
            if file_path.is_file():
                for file_type, pattern in patterns.items():
                    if re.match(pattern, file_path.name, re.IGNORECASE):
                        try:
                            content = file_path.read_text(encoding='utf-8')
                            files.append(FileContent(
                                path=str(file_path),
                                type=file_type,
                                content=content,
                                metadata={'size': len(content), 'modified': file_path.stat().st_mtime}
                            ))
                        except:
                            pass
        return files
    
    def analyze_content(self, files: List[FileContent]) -> Dict:
        """Analyze content for consolidation opportunities"""
        analysis = {
            'duplicates': [],
            'overlaps': [],
            'consolidation_plan': {}
        }
        
        # Group by type
        by_type = {}
        for file in files:
            if file.type not in by_type:
                by_type[file.type] = []
            by_type[file.type].append(file)
        
        # Find duplicates and overlaps
        for file_type, type_files in by_type.items():
            for i, file1 in enumerate(type_files):
                for file2 in type_files[i+1:]:
                    similarity = self._calculate_similarity(file1.content, file2.content)
                    if similarity > 0.8:
                        analysis['duplicates'].append({
                            'files': [file1.path, file2.path],
                            'similarity': similarity
                        })
                    elif similarity > 0.3:
                        analysis['overlaps'].append({
                            'files': [file1.path, file2.path],
                            'similarity': similarity
                        })
        
        return analysis
    
    def _calculate_similarity(self, content1: str, content2: str) -> float:
        """Simple similarity calculation"""
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        return intersection / union if union > 0 else 0.0

if __name__ == "__main__":
    engine = FileUnificationEngine("/media/sunil-kr/workspace/user-projects")
    files = engine.scan_files()
    analysis = engine.analyze_content(files)
    print(f"Found {len(files)} files")
    print(f"Duplicates: {len(analysis['duplicates'])}")
    print(f"Overlaps: {len(analysis['overlaps'])}")
