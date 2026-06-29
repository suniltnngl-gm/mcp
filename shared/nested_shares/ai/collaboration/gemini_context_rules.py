#!/usr/bin/env python3
"""Gemini Context and Rules Engine with Enhanced Ignore Logic"""

import json
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass, asdict

@dataclass
class GeminiIgnoreRules:
    """Enhanced ignore patterns for Gemini AI collaboration"""
    
    # Base patterns from Kiro workspace
    base_ignore: List[str] = None
    
    # Gemini-specific patterns
    gemini_ignore: List[str] = None
    
    # Collaboration-specific patterns  
    collab_ignore: List[str] = None
    
    def __post_init__(self):
        if self.base_ignore is None:
            self.base_ignore = [
                'node_modules/', '.venv/', 'venv/', '__pycache__/',
                '*.pyc', '*.pyo', '*.egg-info/', 'dist/', 'build/',
                '.cache/', '.pytest_cache/', '.mypy_cache/', '.ruff_cache/',
                '*.log', '*.tmp', '.DS_Store', '.vscode/', '.idea/',
                '.git/objects/', '.git/refs/', '.git/logs/',
                '*.so', '*.dylib', '*.dll', '*.exe', '*.zip', '*.tar.gz'
            ]
        
        if self.gemini_ignore is None:
            self.gemini_ignore = [
                # Gemini-specific temporary files
                '.gemini_cache/', '.gemini_temp/',
                '*.gemini_backup', '.gemini_session/',
                # Large model files
                '*.bin', '*.safetensors', '*.gguf',
                # Gemini collaboration artifacts
                '.collab_temp/', 'gemini_working_*'
            ]
        
        if self.collab_ignore is None:
            self.collab_ignore = [
                # Collaboration session artifacts
                'collaboration_sessions.json.bak',
                'shared_context.json.tmp',
                '.review_cache/', '.unification_temp/',
                # Multi-AI coordination files
                '.ai_handoff/', '.consensus_temp/'
            ]

class GeminiContextEngine:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.rules = GeminiIgnoreRules()
        self.context_file = Path(__file__).parent / "gemini_context.json"
        
    def get_all_ignore_patterns(self) -> List[str]:
        """Get combined ignore patterns for Gemini operations"""
        return (self.rules.base_ignore + 
                self.rules.gemini_ignore + 
                self.rules.collab_ignore)
    
    def should_ignore(self, file_path: str) -> bool:
        """Check if file should be ignored based on all rules"""
        path_str = str(file_path).lower()
        
        for pattern in self.get_all_ignore_patterns():
            if pattern.endswith('/'):
                # Directory pattern
                if f"/{pattern[:-1]}/" in path_str or path_str.endswith(f"/{pattern[:-1]}"):
                    return True
            elif pattern.startswith('*.'):
                # Extension pattern
                if path_str.endswith(pattern[1:]):
                    return True
            else:
                # Exact match or substring
                if pattern in path_str:
                    return True
        
        # Archive is reference only - ignore for active operations
        if '/archive/' in path_str:
            return True
            
        return False
    
    def create_context(self, task_type: str) -> Dict:
        """Create Gemini context for specific task type"""
        context = {
            'workspace_path': str(self.workspace_path),
            'task_type': task_type,
            'ignore_patterns': self.get_all_ignore_patterns(),
            'focus_areas': self._get_focus_areas(task_type),
            'collaboration_rules': self._get_collaboration_rules(),
            'file_priorities': self._get_file_priorities()
        }
        
        # Save context
        self.context_file.write_text(json.dumps(context, indent=2))
        return context
    
    def _get_focus_areas(self, task_type: str) -> List[str]:
        """Get focus areas based on task type"""
        focus_map = {
            'review': ['current/', 'shared-tools/nested-shares/'],
            'unification': ['shared-tools/nested-shares/ai/orchestration/'],
            'analysis': ['current/', 'shared-tools/'],
            'consolidation': ['shared-tools/nested-shares/ai/']
        }
        return focus_map.get(task_type, ['current/', 'shared-tools/'])
    
    def _get_collaboration_rules(self) -> Dict:
        """Get collaboration-specific rules"""
        return {
            'handoff_protocol': 'session_based',
            'context_sharing': 'json_files',
            'decision_tracking': 'integrated_ai_discussion',
            'conflict_resolution': 'consensus_analyzer',
            'progress_sync': 'roadmap_engine'
        }
    
    def _get_file_priorities(self) -> Dict:
        """Get file priority levels for processing"""
        return {
            'high': ['.py', '.sh', '.md', '.json'],
            'medium': ['.js', '.ts', '.yml', '.yaml'],
            'low': ['.txt', '.log', '.tmp'],
            'ignore': ['*.pyc', '*.so', '*.zip']
        }

if __name__ == "__main__":
    engine = GeminiContextEngine("/media/sunil-kr/workspace/user-projects")
    context = engine.create_context("file_unification")
    print(f"Created Gemini context with {len(context['ignore_patterns'])} ignore patterns")
    print(f"Focus areas: {context['focus_areas']}")
