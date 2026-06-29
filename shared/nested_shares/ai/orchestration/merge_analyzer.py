#!/usr/bin/env python3
"""Merge Analyzer - Analyze codebases for merge/split operations"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

@dataclass
class CodeElement:
    name: str
    type: str  # class, function, import, variable
    line_start: int
    line_end: int
    dependencies: List[str]
    complexity: int

@dataclass
class MergeAnalysis:
    file1_elements: List[CodeElement]
    file2_elements: List[CodeElement]
    conflicts: List[str]
    shared_dependencies: List[str]
    merge_strategy: str
    integration_points: List[str]

class MergeAnalyzer:
    def __init__(self):
        self.ast_parser = ast
    
    def analyze_file(self, file_path: Path) -> List[CodeElement]:
        """Extract code elements from Python file"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        elements = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                elements.append(CodeElement(
                    name=node.name,
                    type="class",
                    line_start=node.lineno,
                    line_end=getattr(node, 'end_lineno', node.lineno),
                    dependencies=self._extract_dependencies(node),
                    complexity=len(node.body)
                ))
            elif isinstance(node, ast.FunctionDef):
                elements.append(CodeElement(
                    name=node.name,
                    type="function", 
                    line_start=node.lineno,
                    line_end=getattr(node, 'end_lineno', node.lineno),
                    dependencies=self._extract_dependencies(node),
                    complexity=len(node.body)
                ))
        
        return elements
    
    def _extract_dependencies(self, node) -> List[str]:
        """Extract dependencies from AST node"""
        deps = []
        for child in ast.walk(node):
            if isinstance(child, ast.Name):
                deps.append(child.id)
        return list(set(deps))
    
    def analyze_merge(self, file1: Path, file2: Path) -> MergeAnalysis:
        """Analyze two files for merge compatibility"""
        elements1 = self.analyze_file(file1)
        elements2 = self.analyze_file(file2)
        
        # Find conflicts (same names)
        names1 = {e.name for e in elements1}
        names2 = {e.name for e in elements2}
        conflicts = list(names1.intersection(names2))
        
        # Find shared dependencies
        deps1 = set()
        deps2 = set()
        for e in elements1:
            deps1.update(e.dependencies)
        for e in elements2:
            deps2.update(e.dependencies)
        shared_deps = list(deps1.intersection(deps2))
        
        # Determine merge strategy
        strategy = self._determine_strategy(elements1, elements2, conflicts)
        
        # Find integration points
        integration_points = self._find_integration_points(elements1, elements2)
        
        return MergeAnalysis(
            file1_elements=elements1,
            file2_elements=elements2,
            conflicts=conflicts,
            shared_dependencies=shared_deps,
            merge_strategy=strategy,
            integration_points=integration_points
        )
    
    def _determine_strategy(self, e1: List[CodeElement], e2: List[CodeElement], conflicts: List[str]) -> str:
        """Determine best merge strategy"""
        if len(conflicts) == 0:
            return "simple_merge"
        elif len(conflicts) < 3:
            return "selective_merge"
        else:
            return "integration_wrapper"
    
    def _find_integration_points(self, e1: List[CodeElement], e2: List[CodeElement]) -> List[str]:
        """Find natural integration points between codebases"""
        points = []
        
        # Look for manager/orchestrator patterns
        for elem in e1:
            if "manager" in elem.name.lower():
                points.append(f"Integrate {elem.name} with orchestration")
        
        for elem in e2:
            if "orchestrat" in elem.name.lower():
                points.append(f"Use {elem.name} for AI coordination")
        
        return points

def main():
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python merge_analyzer.py <file1> <file2>")
        sys.exit(1)
    
    analyzer = MergeAnalyzer()
    file1 = Path(sys.argv[1])
    file2 = Path(sys.argv[2])
    
    if not file1.exists() or not file2.exists():
        print("Error: Files not found")
        sys.exit(1)
    
    analysis = analyzer.analyze_merge(file1, file2)
    
    print(f"\n🔍 Merge Analysis: {file1.name} + {file2.name}")
    print("=" * 50)
    
    print(f"\n📊 File 1 Elements: {len(analysis.file1_elements)}")
    for elem in analysis.file1_elements[:5]:  # Show first 5
        print(f"  {elem.type}: {elem.name} (lines {elem.line_start}-{elem.line_end})")
    
    print(f"\n📊 File 2 Elements: {len(analysis.file2_elements)}")
    for elem in analysis.file2_elements[:5]:  # Show first 5
        print(f"  {elem.type}: {elem.name} (lines {elem.line_start}-{elem.line_end})")
    
    print(f"\n⚠️  Conflicts: {len(analysis.conflicts)}")
    for conflict in analysis.conflicts:
        print(f"  - {conflict}")
    
    print(f"\n🔗 Shared Dependencies: {len(analysis.shared_dependencies)}")
    for dep in analysis.shared_dependencies[:10]:  # Show first 10
        print(f"  - {dep}")
    
    print(f"\n🎯 Strategy: {analysis.merge_strategy}")
    print(f"\n🔧 Integration Points:")
    for point in analysis.integration_points:
        print(f"  - {point}")

if __name__ == "__main__":
    main()
