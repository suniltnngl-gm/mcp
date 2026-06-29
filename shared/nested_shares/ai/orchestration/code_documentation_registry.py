#!/usr/bin/env python3
"""
Code Documentation Registry - Enhanced context resolution and intelligent code analysis

This registry provides comprehensive documentation, context resolution, and intelligent
code analysis for the workspace optimization system. It serves as both a documentation
hub and a context enhancement tool for better AI understanding.
"""

from shared_tools.utils.config_utils import get_workspace_path
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

@dataclass
class CodeContext:
    """Enhanced code context with intelligent analysis"""
    file_path: str
    purpose: str                    # What this code does
    key_functions: List[str]        # Main functions/methods
    dependencies: List[str]         # Import dependencies
    context_tags: List[str]         # Semantic tags for context
    complexity_score: float         # Code complexity (0-1)
    documentation_quality: float    # Doc quality score (0-1)
    integration_points: List[str]   # How it connects to other components
    usage_examples: List[str]       # Example usage patterns
    limitations: List[str]          # Known limitations or constraints
    improvement_suggestions: List[str]  # Potential improvements

class CodeDocumentationRegistry:
    """
    Intelligent code documentation and context resolution system
    
    This class provides:
    1. Automated code analysis and documentation extraction
    2. Context resolution for better AI understanding
    3. Integration mapping between components
    4. Limitation identification and improvement suggestions
    5. Usage pattern analysis and examples
    """
    
    def __init__(self):
        self.workspace_path = get_workspace_path() / "shared-tools" / "nested-shares"
        self.registry_file = self.workspace_path / "code_registry.json"
        self.documentation = {}
        self.context_map = {}
        
        # Load existing registry
        self._load_registry()
    
    def analyze_code_file(self, file_path: Path) -> CodeContext:
        """
        Intelligent code analysis with context extraction
        
        Analyzes Python files to extract:
        - Purpose and functionality
        - Key functions and methods
        - Dependencies and imports
        - Context tags for semantic understanding
        - Complexity and documentation quality
        - Integration points with other components
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Parse AST for structural analysis
            tree = ast.parse(content)
            
            # Extract components
            purpose = self._extract_purpose(content)
            key_functions = self._extract_functions(tree)
            dependencies = self._extract_dependencies(tree)
            context_tags = self._generate_context_tags(file_path, content)
            complexity_score = self._calculate_complexity(tree, content)
            doc_quality = self._assess_documentation_quality(content)
            integration_points = self._identify_integration_points(content)
            usage_examples = self._extract_usage_examples(content)
            limitations = self._identify_limitations(content)
            improvements = self._suggest_improvements(content, complexity_score, doc_quality)
            
            return CodeContext(
                file_path=str(file_path.relative_to(self.workspace_path)),
                purpose=purpose,
                key_functions=key_functions,
                dependencies=dependencies,
                context_tags=context_tags,
                complexity_score=complexity_score,
                documentation_quality=doc_quality,
                integration_points=integration_points,
                usage_examples=usage_examples,
                limitations=limitations,
                improvement_suggestions=improvements
            )
            
        except Exception as e:
            # Return minimal context for problematic files
            return CodeContext(
                file_path=str(file_path.relative_to(self.workspace_path)),
                purpose=f"Analysis failed: {str(e)}",
                key_functions=[],
                dependencies=[],
                context_tags=['analysis-error'],
                complexity_score=0.0,
                documentation_quality=0.0,
                integration_points=[],
                usage_examples=[],
                limitations=[f"Analysis error: {str(e)}"],
                improvement_suggestions=["Fix syntax errors", "Add proper encoding"]
            )
    
    def _extract_purpose(self, content: str) -> str:
        """Extract the main purpose from docstrings and comments"""
        # Look for module docstring
        docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        if docstring_match:
            docstring = docstring_match.group(1).strip()
            # Get first meaningful line
            lines = [line.strip() for line in docstring.split('\n') if line.strip()]
            if lines:
                return lines[0][:200]  # First 200 chars
        
        # Look for class docstring
        class_doc_match = re.search(r'class.*?:\s*"""(.*?)"""', content, re.DOTALL)
        if class_doc_match:
            return class_doc_match.group(1).strip().split('\n')[0][:200]
        
        # Look for descriptive comments
        comment_match = re.search(r'#\s*(.+)', content)
        if comment_match:
            return comment_match.group(1).strip()[:200]
        
        return "Purpose not clearly documented"
    
    def _extract_functions(self, tree: ast.AST) -> List[str]:
        """Extract key functions and methods"""
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private methods unless they're important
                if not node.name.startswith('_') or node.name in ['__init__', '__main__']:
                    functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                functions.append(f"class:{node.name}")
        
        return functions[:10]  # Top 10 most important
    
    def _extract_dependencies(self, tree: ast.AST) -> List[str]:
        """Extract import dependencies"""
        dependencies = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.append(node.module)
        
        return list(set(dependencies))  # Remove duplicates
    
    def _generate_context_tags(self, file_path: Path, content: str) -> List[str]:
        """Generate semantic context tags for better AI understanding"""
        tags = []
        
        # File name based tags
        filename = file_path.name.lower()
        if 'search' in filename:
            tags.extend(['search', 'query', 'indexing'])
        if 'monitor' in filename:
            tags.extend(['monitoring', 'health', 'alerts'])
        if 'automat' in filename:
            tags.extend(['automation', 'scheduling', 'execution'])
        if 'optim' in filename:
            tags.extend(['optimization', 'performance', 'improvement'])
        if 'valid' in filename:
            tags.extend(['validation', 'testing', 'verification'])
        
        # Content based tags
        content_lower = content.lower()
        
        # AI/ML related
        if any(word in content_lower for word in ['semantic', 'similarity', 'embedding']):
            tags.extend(['ai', 'machine-learning', 'nlp'])
        
        # Data processing
        if any(word in content_lower for word in ['json', 'csv', 'parse', 'process']):
            tags.extend(['data-processing', 'serialization'])
        
        # System operations
        if any(word in content_lower for word in ['file', 'directory', 'path']):
            tags.extend(['filesystem', 'io-operations'])
        
        # Performance
        if any(word in content_lower for word in ['cache', 'optimize', 'performance']):
            tags.extend(['performance', 'caching', 'optimization'])
        
        # Integration
        if any(word in content_lower for word in ['api', 'interface', 'integration']):
            tags.extend(['integration', 'api', 'interface'])
        
        return list(set(tags))  # Remove duplicates
    
    def _calculate_complexity(self, tree: ast.AST, content: str) -> float:
        """Calculate code complexity score (0-1, higher = more complex)"""
        complexity_factors = 0
        total_nodes = 0
        
        for node in ast.walk(tree):
            total_nodes += 1
            
            # Control flow complexity
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                complexity_factors += 1
            
            # Nested structures
            if isinstance(node, ast.FunctionDef):
                # Count nested functions
                for child in ast.walk(node):
                    if isinstance(child, ast.FunctionDef) and child != node:
                        complexity_factors += 0.5
        
        # Line count factor
        line_count = len(content.split('\n'))
        line_factor = min(line_count / 500, 1.0)  # Normalize to 500 lines
        
        # Calculate final score
        if total_nodes == 0:
            return 0.0
        
        complexity_ratio = complexity_factors / total_nodes
        final_score = (complexity_ratio * 0.7) + (line_factor * 0.3)
        
        return min(final_score, 1.0)
    
    def _assess_documentation_quality(self, content: str) -> float:
        """Assess documentation quality (0-1, higher = better documented)"""
        score = 0.0
        
        # Module docstring
        if '"""' in content and content.count('"""') >= 2:
            score += 0.3
        
        # Function docstrings
        docstring_count = content.count('def ') 
        if docstring_count > 0:
            # Estimate docstring coverage
            function_docs = len(re.findall(r'def\s+\w+.*?:\s*"""', content, re.DOTALL))
            doc_coverage = function_docs / docstring_count
            score += doc_coverage * 0.4
        
        # Comments
        comment_lines = len([line for line in content.split('\n') if line.strip().startswith('#')])
        total_lines = len(content.split('\n'))
        if total_lines > 0:
            comment_ratio = comment_lines / total_lines
            score += min(comment_ratio * 2, 0.3)  # Cap at 0.3
        
        return min(score, 1.0)
    
    def _identify_integration_points(self, content: str) -> List[str]:
        """Identify how this code integrates with other components"""
        integration_points = []
        
        # Look for class instantiations of other components
        class_patterns = [
            r'(\w+Search)\(',
            r'(\w+Monitor)\(',
            r'(\w+Automation)\(',
            r'(\w+Validator)\(',
            r'(\w+Optimizer)\('
        ]
        
        for pattern in class_patterns:
            matches = re.findall(pattern, content)
            integration_points.extend(matches)
        
        # Look for file operations that suggest integration
        if 'json.load' in content or 'json.dump' in content:
            integration_points.append('json-data-exchange')
        
        if 'Path(' in content or 'pathlib' in content:
            integration_points.append('filesystem-integration')
        
        if 'subprocess' in content or 'os.system' in content:
            integration_points.append('system-command-integration')
        
        return list(set(integration_points))
    
    def _extract_usage_examples(self, content: str) -> List[str]:
        """Extract usage examples from code"""
        examples = []
        
        # Look for main function examples
        main_match = re.search(r'if __name__ == "__main__":(.*?)(?=\n\S|\Z)', content, re.DOTALL)
        if main_match:
            main_content = main_match.group(1)
            # Extract command line usage
            usage_lines = [line.strip() for line in main_content.split('\n') 
                          if 'print(' in line and ('Usage:' in line or 'Commands:' in line)]
            examples.extend(usage_lines[:3])
        
        # Look for docstring examples
        docstring_examples = re.findall(r'Examples?:\s*(.*?)(?="""|\n\s*\n)', content, re.DOTALL | re.IGNORECASE)
        for example in docstring_examples:
            clean_example = example.strip().replace('\n', ' ')[:100]
            if clean_example:
                examples.append(clean_example)
        
        return examples[:5]  # Top 5 examples
    
    def _identify_limitations(self, content: str) -> List[str]:
        """Identify potential limitations or constraints"""
        limitations = []
        
        # Look for TODO comments
        todos = re.findall(r'#\s*TODO:?\s*(.+)', content, re.IGNORECASE)
        limitations.extend([f"TODO: {todo.strip()}" for todo in todos[:3]])
        
        # Look for FIXME comments
        fixmes = re.findall(r'#\s*FIXME:?\s*(.+)', content, re.IGNORECASE)
        limitations.extend([f"FIXME: {fixme.strip()}" for fixme in fixmes[:3]])
        
        # Look for exception handling that suggests limitations
        if 'except Exception' in content:
            limitations.append("Broad exception handling may mask specific errors")
        
        # Look for hardcoded values
        if re.search(r'=\s*\d+\s*#.*threshold', content, re.IGNORECASE):
            limitations.append("Contains hardcoded thresholds that may need adjustment")
        
        # Look for performance concerns
        if 'time.sleep' in content:
            limitations.append("Uses blocking sleep operations")
        
        return limitations[:5]  # Top 5 limitations
    
    def _suggest_improvements(self, content: str, complexity: float, doc_quality: float) -> List[str]:
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        
        # Documentation improvements
        if doc_quality < 0.5:
            suggestions.append("Add comprehensive docstrings and comments")
        
        # Complexity improvements
        if complexity > 0.7:
            suggestions.append("Consider breaking down complex functions into smaller components")
        
        # Error handling improvements
        if 'except Exception' in content and 'logging' not in content:
            suggestions.append("Add proper logging for better error tracking")
        
        # Performance improvements
        if 'for ' in content and 'append(' in content:
            suggestions.append("Consider using list comprehensions for better performance")
        
        # Type hints
        if 'def ' in content and '-> ' not in content:
            suggestions.append("Add type hints for better code clarity")
        
        # Configuration
        if re.search(r'=\s*\d+', content) and 'config' not in content.lower():
            suggestions.append("Move hardcoded values to configuration")
        
        return suggestions[:5]  # Top 5 suggestions
    
    def scan_workspace(self) -> Dict[str, CodeContext]:
        """Scan entire workspace and build comprehensive registry"""
        print("🔍 Scanning workspace for code documentation...")
        
        registry = {}
        
        # Scan Python files in orchestration directory
        orchestration_path = self.workspace_path / "ai" / "orchestration"
        if orchestration_path.exists():
            for py_file in orchestration_path.glob("*.py"):
                print(f"  📄 Analyzing {py_file.name}...")
                context = self.analyze_code_file(py_file)
                registry[context.file_path] = context
        
        # Update internal registry
        self.documentation = registry
        
        # Save to file
        self._save_registry()
        
        return registry
    
    def get_context_for_file(self, file_path: str) -> Optional[CodeContext]:
        """Get enhanced context for a specific file"""
        return self.documentation.get(file_path)
    
    def get_integration_map(self) -> Dict[str, List[str]]:
        """Generate integration map showing component relationships"""
        integration_map = {}
        
        for file_path, context in self.documentation.items():
            if context.integration_points:
                integration_map[file_path] = context.integration_points
        
        return integration_map
    
    def get_improvement_priorities(self) -> List[Tuple[str, float, List[str]]]:
        """Get prioritized list of files needing improvement"""
        priorities = []
        
        for file_path, context in self.documentation.items():
            # Calculate priority score (higher = needs more improvement)
            priority_score = 0.0
            
            # High complexity penalty
            priority_score += context.complexity_score * 0.4
            
            # Low documentation penalty
            priority_score += (1.0 - context.documentation_quality) * 0.3
            
            # Limitations penalty
            priority_score += len(context.limitations) * 0.1
            
            # Improvement suggestions penalty
            priority_score += len(context.improvement_suggestions) * 0.05
            
            if priority_score > 0.3:  # Only include files that need improvement
                priorities.append((file_path, priority_score, context.improvement_suggestions))
        
        # Sort by priority score (highest first)
        priorities.sort(key=lambda x: x[1], reverse=True)
        
        return priorities
    
    def generate_context_summary(self) -> str:
        """Generate comprehensive context summary for AI understanding"""
        if not self.documentation:
            return "No documentation available. Run scan_workspace() first."
        
        summary = []
        summary.append("🧠 WORKSPACE CONTEXT SUMMARY")
        summary.append("=" * 35)
        summary.append("")
        
        # Overall statistics
        total_files = len(self.documentation)
        avg_complexity = sum(ctx.complexity_score for ctx in self.documentation.values()) / total_files
        avg_doc_quality = sum(ctx.documentation_quality for ctx in self.documentation.values()) / total_files
        
        summary.append(f"📊 Overview: {total_files} files analyzed")
        summary.append(f"🔧 Avg Complexity: {avg_complexity:.2f}/1.0")
        summary.append(f"📚 Avg Documentation: {avg_doc_quality:.2f}/1.0")
        summary.append("")
        
        # Component purposes
        summary.append("🎯 Component Purposes:")
        for file_path, context in self.documentation.items():
            filename = Path(file_path).name
            summary.append(f"  • {filename}: {context.purpose[:80]}...")
        summary.append("")
        
        # Integration map
        integration_map = self.get_integration_map()
        if integration_map:
            summary.append("🔗 Integration Points:")
            for file_path, integrations in integration_map.items():
                filename = Path(file_path).name
                summary.append(f"  • {filename}: {', '.join(integrations[:3])}")
            summary.append("")
        
        # Improvement priorities
        priorities = self.get_improvement_priorities()
        if priorities:
            summary.append("🎯 Improvement Priorities:")
            for file_path, score, suggestions in priorities[:5]:
                filename = Path(file_path).name
                summary.append(f"  • {filename} ({score:.2f}): {suggestions[0] if suggestions else 'General improvements'}")
        
        return '\n'.join(summary)
    
    def _load_registry(self):
        """Load existing registry from file"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    # Convert dict back to CodeContext objects
                    self.documentation = {
                        path: CodeContext(**context_data) 
                        for path, context_data in data.items()
                    }
            except Exception as e:
                print(f"Warning: Could not load registry: {e}")
                self.documentation = {}
        else:
            self.documentation = {}
    
    def _save_registry(self):
        """Save registry to file"""
        try:
            # Convert CodeContext objects to dicts for JSON serialization
            data = {
                path: asdict(context) 
                for path, context in self.documentation.items()
            }
            
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not save registry: {e}")

def main():
    """Main function with comprehensive usage examples"""
    import sys
    
    registry = CodeDocumentationRegistry()
    
    if len(sys.argv) < 2:
        print("Usage: python3 code_documentation_registry.py <command>")
        print("Commands:")
        print("  scan        - Scan workspace and build registry")
        print("  summary     - Show context summary")
        print("  priorities  - Show improvement priorities")
        print("  integration - Show integration map")
        print("  file <path> - Show context for specific file")
        return
    
    command = sys.argv[1]
    
    if command == 'scan':
        registry.scan_workspace()
        print(f"✅ Scanned {len(registry.documentation)} files")
        
    elif command == 'summary':
        summary = registry.generate_context_summary()
        print(summary)
        
    elif command == 'priorities':
        priorities = registry.get_improvement_priorities()
        
        print("🎯 Improvement Priorities")
        print("=" * 25)
        
        for file_path, score, suggestions in priorities[:10]:
            filename = Path(file_path).name
            print(f"\n📄 {filename} (Priority: {score:.2f})")
            for suggestion in suggestions[:3]:
                print(f"  • {suggestion}")
                
    elif command == 'integration':
        integration_map = registry.get_integration_map()
        
        print("🔗 Integration Map")
        print("=" * 18)
        
        for file_path, integrations in integration_map.items():
            filename = Path(file_path).name
            print(f"📄 {filename}:")
            for integration in integrations:
                print(f"  → {integration}")
            print()
            
    elif command == 'file' and len(sys.argv) >= 3:
        file_path = sys.argv[2]
        context = registry.get_context_for_file(file_path)
        
        if context:
            print(f"📄 Context for {Path(file_path).name}")
            print("=" * 30)
            print(f"Purpose: {context.purpose}")
            print(f"Complexity: {context.complexity_score:.2f}/1.0")
            print(f"Documentation: {context.documentation_quality:.2f}/1.0")
            print(f"Key Functions: {', '.join(context.key_functions[:5])}")
            print(f"Context Tags: {', '.join(context.context_tags)}")
            
            if context.limitations:
                print(f"\nLimitations:")
                for limitation in context.limitations:
                    print(f"  • {limitation}")
                    
            if context.improvement_suggestions:
                print(f"\nSuggestions:")
                for suggestion in context.improvement_suggestions:
                    print(f"  • {suggestion}")
        else:
            print(f"❌ No context found for {file_path}")

if __name__ == "__main__":
    main()
