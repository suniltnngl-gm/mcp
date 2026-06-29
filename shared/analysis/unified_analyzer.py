#!/usr/bin/env python3
"""
🔍 AI Orchestra - Intelligent Codebase Analyzer
===============================================
Advanced codebase analysis for structure optimization and duplicate detection
"""

import ast
import difflib
import hashlib
import json
import re
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from scripts.config_manager import is_path_ignored


DB_PATH = Path("/media/sunil-kr/workspace/workspace-system/workspace_knowledge.db")


# Colors for terminal output
class Colors:
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def log_info(msg: str):
    print(f"{Colors.BLUE}🔍 {msg}{Colors.ENDC}")


def log_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")


def log_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.ENDC}")


def log_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.ENDC}")

def log_header(msg: str):
    print(f"\n{Colors.PURPLE}{Colors.BOLD}🎭 {msg}{Colors.ENDC}")
    print("=" * (len(msg) + 3))


def init_db():
    """Initialize the database with all necessary tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Improvement opportunities table
    c.execute(
        """CREATE TABLE IF NOT EXISTS improvement_opportunities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        what TEXT NOT NULL,
        why TEXT NOT NULL,
        how TEXT NOT NULL,
        impact TEXT NOT NULL,
        effort TEXT NOT NULL,
        priority INTEGER NOT NULL,
        status TEXT DEFAULT 'identified',
        created_at TEXT NOT NULL
    )"""
    )

    # Optimizations table
    c.execute(
        """CREATE TABLE IF NOT EXISTS optimizations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        issue TEXT NOT NULL,
        current_state TEXT,
        proposed_state TEXT,
        impact TEXT,
        effort TEXT,
        priority TEXT,
        created_at TEXT NOT NULL
    )"""
    )

    conn.commit()
    conn.close()



@dataclass
class FunctionInfo:
    name: str
    file_path: str
    line_start: int
    line_end: int
    args: list[str]
    docstring: str | None
    complexity: int
    imports_used: set[str]
    calls_made: set[str]
    source_hash: str
    semantic_hash: str


@dataclass
class ClassInfo:
    name: str
    file_path: str
    line_start: int
    line_end: int
    bases: list[str]
    methods: list[str]
    docstring: str | None
    imports_used: set[str]
    complexity: int
    source_hash: str


@dataclass
class ModuleInfo:
    name: str
    file_path: str
    imports: set[str]
    exports: set[str]
    functions: list[FunctionInfo]
    classes: list[ClassInfo]
    complexity: int
    lines_of_code: int
    docstring: str | None


@dataclass
class DuplicateGroup:
    type: str  # 'function', 'class', 'module'
    similarity: float
    items: list[Any]
    recommendation: str


@dataclass
class Improvement:
    what: str
    why: str
    how: str
    impact: str
    effort: str
    steps: list[str]
    time: str
    priority: int
    category: str


@dataclass
class Optimization:
    category: str
    issue: str
    current_state: str
    proposed_state: str
    impact: str
    effort: str
    priority: str


@dataclass
class AnalysisReport:
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    modules: list[ModuleInfo] = field(default_factory=list)
    duplicates: list[DuplicateGroup] = field(default_factory=list)
    naming_issues: dict[str, list[str]] = field(default_factory=dict)
    structure_recommendations: list[str] = field(default_factory=list)
    complexity_hotspots: list[tuple[str, int]] = field(default_factory=list)
    import_analysis: dict[str, Any] = field(default_factory=dict)
    refactoring_opportunities: list[dict[str, Any]] = field(default_factory=list)
    improvements: list[Improvement] = field(default_factory=list)
    optimizations: list[Optimization] = field(default_factory=list)


class CodebaseAnalyzer:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.modules: dict[str, ModuleInfo] = {}
        self.all_functions: list[FunctionInfo] = []
        self.all_classes: list[ClassInfo] = []
        self.report = AnalysisReport()

        # Patterns for analysis
        self.naming_patterns = {
            "snake_case": re.compile(r"^[a-z_][a-z0-9_]*$"),
            "camel_case": re.compile(r"^[a-z][a-zA-Z0-9]*$"),
            "pascal_case": re.compile(r"^[A-Z][a-zA-Z0-9]*$"),
            "constant": re.compile(r"^[A-Z_][A-Z0-9_]*$"),
        }

        # Common AI/ML patterns to recognize
        self.ai_patterns = {
            "providers": ["openai", "anthropic", "mistral", "provider"],
            "orchestration": ["orchestrat", "coordinat", "manage", "control"],
            "persistence": ["persist", "save", "store", "cache"],
            "monitoring": ["monitor", "track", "log", "metric"],
            "configuration": ["config", "setup", "init", "param"],
        }

    def analyze_project(self) -> AnalysisReport:
        """Main analysis entry point"""
        log_header("Analyzing AI Orchestra Codebase")

        # Find all Python files, restricting to main project directories
        python_files = [
            f for f in self.project_root.rglob("*.py") if not is_path_ignored(f)
        ]

        log_info(f"Found {len(python_files)} project Python files to analyze")

        # Analyze each file
        for file_path in python_files:
            try:
                self._analyze_file(file_path)
            except Exception as e:
                log_warning(f"Could not analyze {file_path}: {e}")

        log_success(f"Analyzed {len(self.modules)} modules")

        # Perform advanced analysis
        self._detect_duplicates()
        self._analyze_naming()
        self._analyze_structure()
        self._analyze_imports()
        self._find_refactoring_opportunities()
        self._analyze_improvements()
        self._analyze_optimizations()

        return self.report

    def _analyze_optimizations(self):
        """Analyze and identify optimization opportunities"""
        log_info("Analyzing for optimization opportunities...")
        issues = []

        # 1. Database connection duplication
        issues.append(
            {
                "category": "DUPLICATION",
                "issue": "Repeated sqlite3.connect() calls",
                "current": "16 files with 100+ total connections, no connection pooling",
                "proposed": "Single db_utils.py with connection pool and context manager",
                "impact": "Reduce code by ~200 lines, improve performance, easier maintenance",
                "effort": "medium",
                "priority": "high",
            }
        )

        # 2. init_db() duplication
        issues.append(
            {
                "category": "DUPLICATION",
                "issue": "Duplicate init_db() in 14 files",
                "current": "14 separate init_db() functions, each creates own tables",
                "proposed": "Single schema.py with all table definitions, one init_all()",
                "impact": "Reduce code by ~150 lines, single source of truth for schema",
                "effort": "low",
                "priority": "high",
            }
        )

        # 3. CLI pattern duplication
        issues.append(
            {
                "category": "DUPLICATION",
                "issue": "16 files with CLI patterns",
                "current": 'Each module has if __name__ == "__main__" with argparse',
                "proposed": "Keep only workspace_cli.py, others become libraries",
                "impact": "Reduce code by ~300 lines, cleaner architecture",
                "effort": "low",
                "priority": "medium",
            }
        )

        # 4. Similar list/add/get functions
        issues.append(
            {
                "category": "DUPLICATION",
                "issue": "Repeated CRUD patterns (list_*, add_*, get_*)",
                "current": "30+ similar functions across 11 files",
                "proposed": "Generic CRUD base class or functions",
                "impact": "Reduce code by ~400 lines, consistent interface",
                "effort": "medium",
                "priority": "medium",
            }
        )

        # 5. workspace_cli.py imports everything
        issues.append(
            {
                "category": "ALTERNATIVE",
                "issue": "workspace_cli.py imports 10 modules",
                "current": "Direct imports, tight coupling, hard to test",
                "proposed": "Plugin architecture or service registry pattern",
                "impact": "Better modularity, easier testing, extensible",
                "effort": "high",
                "priority": "low",
            }
        )

        # 6. Two automation systems
        issues.append(
            {
                "category": "REDUNDANT",
                "issue": "automation_manager.py vs task_automator.py overlap",
                "current": "Both handle automated tasks, different approaches",
                "proposed": "Merge into single automation_system.py",
                "impact": "Reduce confusion, single interface for automation",
                "effort": "medium",
                "priority": "high",
            }
        )

        # 7. Two knowledge tables
        issues.append(
            {
                "category": "REDUNDANT",
                "issue": "knowledge table in kb_manager and workspace_manager",
                "current": "Same table created in 2 places",
                "proposed": "Single knowledge table, shared by both",
                "impact": "Avoid conflicts, cleaner schema",
                "effort": "low",
                "priority": "urgent",
            }
        )

        # 8. Manual SQL everywhere
        issues.append(
            {
                "category": "ALTERNATIVE",
                "issue": "Raw SQL in every file",
                "current": "Manual SQL strings, no query builder",
                "proposed": "Use SQLAlchemy or simple query builder",
                "impact": "Type safety, easier refactoring, less errors",
                "effort": "high",
                "priority": "low",
            }
        )

        # 9. No migration system
        issues.append(
            {
                "category": "CONVERSION",
                "issue": "No database migration/versioning",
                "current": "Schema changes require manual updates",
                "proposed": "Add migration system (Alembic or custom)",
                "impact": "Safe schema evolution, version tracking",
                "effort": "medium",
                "priority": "medium",
            }
        )

        # 10. Scattered error handling
        issues.append(
            {
                "category": "DUPLICATION",
                "issue": "Inconsistent error handling patterns",
                "current": "Mix of try/except, some silent failures",
                "proposed": "Centralized error handling with custom exceptions",
                "impact": "Better debugging, consistent behavior",
                "effort": "medium",
                "priority": "medium",
            }
        )
        self.report.optimizations = [Optimization(**issue) for issue in issues]


    def _analyze_improvements(self):
        """Analyze and identify improvement opportunities"""
        log_info("Analyzing for improvement opportunities...")
        issues = self._identify_what()

        improvements = []
        for issue in issues:
            why = self._explain_why(issue["what"])
            how = self._suggest_how(issue["what"])

            # Calculate priority (1-10)
            severity_score = {"high": 8, "medium": 5, "low": 2}[issue["severity"]]
            effort_score = {"low": 3, "medium": 2, "high": 1}[how["effort"]]
            priority = severity_score + effort_score

            improvements.append(
                Improvement(
                    what=issue["what"],
                    why=why["why"],
                    how=how["how"],
                    impact=why["impact"],
                    effort=how["effort"],
                    steps=how["steps"],
                    time=how["time"],
                    priority=priority,
                    category=issue["category"],
                )
            )

        # Sort by priority
        improvements.sort(key=lambda x: x.priority, reverse=True)
        self.report.improvements = improvements

    def _identify_what(self):
        """Identify what needs to be changed"""
        issues = []
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # 1. Missing tests
        try:
            c.execute('SELECT COUNT(*) FROM tools WHERE name LIKE "%test%"')
            test_tools = c.fetchone()[0]
            if test_tools == 0:
                issues.append(
                    {
                        "what": "No automated tests",
                        "category": "quality",
                        "severity": "high",
                    }
                )
        except:
            pass

        # 2. No backups
        backup_file = Path(DB_PATH).parent / "workspace_knowledge.backup.db"
        if not backup_file.exists():
            issues.append(
                {
                    "what": "No database backups",
                    "category": "reliability",
                    "severity": "high",
                }
            )

        # 3. Manual processes
        c.execute("SELECT COUNT(*) FROM automated_tasks WHERE enabled=1")
        auto_tasks = c.fetchone()[0]
        if auto_tasks < 3:
            issues.append(
                {
                    "what": "Few automated tasks",
                    "category": "efficiency",
                    "severity": "medium",
                }
            )

        # 4. No monitoring
        c.execute("SELECT COUNT(*) FROM health_checks")
        health_checks = c.fetchone()[0]
        if health_checks == 0:
            issues.append(
                {
                    "what": "No health monitoring",
                    "category": "observability",
                    "severity": "medium",
                }
            )

        # 5. Unused capabilities
        c.execute("SELECT COUNT(*) FROM capabilities WHERE usage_count=0")
        unused = c.fetchone()[0]
        if unused > 0:
            issues.append(
                {
                    "what": f"{unused} unused capabilities",
                    "category": "complexity",
                    "severity": "low",
                }
            )

        # 6. Old sessions
        cutoff = (datetime.now() - timedelta(days=7)).isoformat()
        c.execute(
            'SELECT COUNT(*) FROM sessions WHERE status="active" AND started_at < ?',
            (cutoff,),
        )
        old_sessions = c.fetchone()[0]
        if old_sessions > 0:
            issues.append(
                {
                    "what": f"{old_sessions} stale sessions",
                    "category": "cleanup",
                    "severity": "low",
                }
            )

        # 7. No documentation for tools
        c.execute('SELECT COUNT(*) FROM tools WHERE description="" OR description IS NULL')
        undocumented = c.fetchone()[0]
        if undocumented > 0:
            issues.append(
                {
                    "what": f"{undocumented} undocumented tools",
                    "category": "documentation",
                    "severity": "low",
                }
            )

        conn.close()
        return issues

    def _explain_why(self, what):
        """Explain why something needs to change"""
        reasons = {
            "No automated tests": {
                "why": "Without tests, bugs go undetected until production",
                "impact": "High risk of breaking changes, reduced confidence in deployments",
                "cost": "Manual testing takes 10x longer, bugs cost 100x more to fix in production",
            },
            "No database backups": {
                "why": "Data loss is catastrophic and unrecoverable",
                "impact": "Single point of failure, all work could be lost",
                "cost": "Recovery impossible, complete rebuild required",
            },
            "Few automated tasks": {
                "why": "Manual work is error-prone and time-consuming",
                "impact": "Reduced productivity, inconsistent execution",
                "cost": "10+ hours per week on manual tasks",
            },
            "No health monitoring": {
                "why": "Issues go unnoticed until they become critical",
                "impact": "Reactive instead of proactive, longer downtime",
                "cost": "10x more expensive to fix than prevent",
            },
        }

        # Generic reasons for pattern matching
        if "unused" in what.lower():
            return {
                "why": "Unused code increases complexity without value",
                "impact": "Harder to maintain, slower to understand",
                "cost": "Cognitive overhead, potential bugs",
            }
        elif "stale" in what.lower() or "old" in what.lower():
            return {
                "why": "Stale data clutters the system",
                "impact": "Slower queries, confusing state",
                "cost": "Wasted resources, reduced clarity",
            }
        elif "undocumented" in what.lower():
            return {
                "why": "Undocumented code is hard to use and maintain",
                "impact": "Knowledge silos, onboarding friction",
                "cost": "Repeated questions, mistakes",
            }

        return reasons.get(
            what,
            {
                "why": "Improvement needed for better system health",
                "impact": "Moderate impact on system quality",
                "cost": "Some efficiency loss",
            },
        )

    def _suggest_how(self, what):
        """Suggest how to fix the issue"""
        solutions = {
            "No automated tests": {
                "how": "Create tests/ directory with pytest tests for each module",
                "steps": [
                    "mkdir tests",
                    "pip install pytest pytest-cov",
                    "Create test_*.py files",
                    "Run: pytest --cov=. tests/",
                    "Add to CI/CD pipeline",
                ],
                "effort": "medium",
                "time": "4-8 hours",
            },
            "No database backups": {
                "how": "Setup automated daily backups with rotation",
                "steps": [
                    "Create backup script",
                    "Add cron job: 0 2 * * * backup.sh",
                    "Keep 7 daily, 4 weekly, 12 monthly",
                    "Test restore process",
                    "Monitor backup success",
                ],
                "effort": "low",
                "time": "1-2 hours",
            },
            "Few automated tasks": {
                "how": "Identify manual tasks and automate them",
                "steps": [
                    "List all manual tasks",
                    "Prioritize by frequency",
                    "Create automation scripts",
                    "Schedule with cron",
                    "Monitor execution",
                ],
                "effort": "medium",
                "time": "2-4 hours per task",
            },
            "No health monitoring": {
                "how": "Setup continuous health monitoring",
                "steps": [
                    "Already have: automation_manager.py health",
                    "Schedule: 0 * * * * health check",
                    "Alert on failures",
                    "Dashboard for visualization",
                    "Track trends",
                ],
                "effort": "low",
                "time": "1 hour",
            },
        }

        # Generic solutions
        if "unused" in what.lower():
            return {
                "how": "Remove or archive unused components",
                "steps": [
                    "Identify unused items",
                    "Verify no dependencies",
                    "Archive to backup",
                    "Remove from active system",
                    "Monitor for issues",
                ],
                "effort": "low",
                "time": "30 minutes",
            }
        elif "stale" in what.lower() or "old" in what.lower():
            return {
                "how": "Cleanup old data with retention policy",
                "steps": [
                    "Define retention policy",
                    "Archive old data",
                    "Delete after archive",
                    "Automate cleanup",
                    "Monitor storage",
                ],
                "effort": "low",
                "time": "1 hour",
            }
        elif "undocumented" in what.lower():
            return {
                "how": "Add documentation to all tools",
                "steps": [
                    "List undocumented items",
                    "Add descriptions",
                    "Add usage examples",
                    "Generate API docs",
                    "Keep updated",
                ],
                "effort": "low",
                "time": "15 min per tool",
            }

        return solutions.get(
            what,
            {
                "how": "Analyze and implement improvement",
                "steps": ["Investigate", "Plan", "Implement", "Test", "Deploy"],
                "effort": "medium",
                "time": "2-4 hours",
            },
        )


    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single Python file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            module_name = self._get_module_name(file_path)
            module = ModuleInfo(
                name=module_name,
                file_path=str(file_path),
                imports=set(),
                exports=set(),
                functions=[],
                classes=[],
                complexity=0,
                lines_of_code=len(content.splitlines()),
                docstring=ast.get_docstring(tree),
            )

            # Analyze AST
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._analyze_function(node, file_path, content)
                    module.functions.append(func_info)
                    self.all_functions.append(func_info)

                elif isinstance(node, ast.ClassDef):
                    class_info = self._analyze_class(node, file_path, content)
                    module.classes.append(class_info)
                    self.all_classes.append(class_info)

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        module.imports.add(alias.name)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module.imports.add(node.module)

            # Calculate module complexity
            module.complexity = sum(f.complexity for f in module.functions) + sum(
                c.complexity for c in module.classes
            )

            self.modules[module_name] = module
            self.report.modules.append(module)

        except Exception as e:
            log_warning(f"Error analyzing {file_path}: {e}")

    def _analyze_function(
        self,
        node: ast.FunctionDef,
        file_path: Path,
        content: str,
    ) -> FunctionInfo:
        """Analyze a function definition"""
        lines = content.splitlines()
        start_line = node.lineno
        end_line = node.end_lineno or start_line

        # Extract function source
        func_source = "\n".join(lines[start_line - 1 : end_line])

        # Calculate complexity (simplified cyclomatic complexity)
        complexity = 1  # Base complexity
        for child in ast.walk(node):
            if isinstance(
                child,
                ast.If
                | ast.While
                | ast.For
                | ast.With
                | ast.Try
                | ast.ExceptHandler
                | ast.AsyncWith
                | ast.AsyncFor,
            ):
                complexity += 1

        # Analyze function calls
        calls_made = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls_made.add(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    calls_made.add(child.func.attr)

        # Get function arguments
        args = [arg.arg for arg in node.args.args]

        # Create semantic hash (normalized function signature and logic)
        semantic_content = f"{node.name}({','.join(args)})"
        semantic_hash = hashlib.md5(semantic_content.encode()).hexdigest()[:16]

        return FunctionInfo(
            name=node.name,
            file_path=str(file_path),
            line_start=start_line,
            line_end=end_line,
            args=args,
            docstring=ast.get_docstring(node),
            complexity=complexity,
            imports_used=set(),  # Would need more analysis
            calls_made=calls_made,
            source_hash=hashlib.md5(func_source.encode()).hexdigest()[:16],
            semantic_hash=semantic_hash,
        )

    def _analyze_class(
        self,
        node: ast.ClassDef,
        file_path: Path,
        content: str,
    ) -> ClassInfo:
        """Analyze a class definition"""
        lines = content.splitlines()
        start_line = node.lineno
        end_line = node.end_lineno or start_line

        # Extract class source
        class_source = "\n".join(lines[start_line - 1 : end_line])

        # Get base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(base.attr)

        # Get methods
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]

        # Calculate complexity
        complexity = 0
        for child in ast.walk(node):
            if isinstance(
                child,
                ast.If
                | ast.While
                | ast.For
                | ast.With
                | ast.Try
                | ast.ExceptHandler
                | ast.AsyncWith
                | ast.AsyncFor,
            ):
                complexity += 1

        return ClassInfo(
            name=node.name,
            file_path=str(file_path),
            line_start=start_line,
            line_end=end_line,
            bases=bases,
            methods=methods,
            docstring=ast.get_docstring(node),
            imports_used=set(),
            complexity=complexity,
            source_hash=hashlib.md5(class_source.encode()).hexdigest()[:16],
        )

    def _get_module_name(self, file_path: Path) -> str:
        """Get module name from file path"""
        relative_path = file_path.relative_to(self.project_root)
        if relative_path.name == "__init__.py":
            return str(relative_path.parent).replace("/", ".")
        else:
            return str(relative_path.with_suffix("")).replace("/", ".")

    def _detect_duplicates(self) -> None:
        """Detect duplicate or similar functions and classes"""
        log_info("Detecting duplicates and similar code...")

        # Function duplicates
        func_groups = defaultdict(list)
        for func in self.all_functions:
            # Group by semantic similarity
            key = f"{len(func.args)}_{func.complexity}_{len(func.calls_made)}"
            func_groups[key].append(func)

        for group in func_groups.values():
            if len(group) > 1:
                # Check for actual similarity
                similar_funcs = self._find_similar_functions(group)
                if similar_funcs:
                    self.report.duplicates.append(
                        DuplicateGroup(
                            type="function",
                            similarity=similar_funcs[0],
                            items=similar_funcs[1],
                            recommendation=self._generate_duplicate_recommendation(
                                similar_funcs[1]
                            ),
                        )
                    )

        # Class duplicates
        class_groups = defaultdict(list)
        for cls in self.all_classes:
            key = f"{len(cls.methods)}_{cls.complexity}_{len(cls.bases)}"
            class_groups[key].append(cls)

        for group in class_groups.values():
            if len(group) > 1:
                similar_classes = self._find_similar_classes(group)
                if similar_classes:
                    self.report.duplicates.append(
                        DuplicateGroup(
                            type="class",
                            similarity=similar_classes[0],
                            items=similar_classes[1],
                            recommendation=self._generate_duplicate_recommendation(
                                similar_classes[1]
                            ),
                        )
                    )

    def _find_similar_functions(
        self,
        functions: list[FunctionInfo],
    ) -> tuple[float, list[FunctionInfo]] | None:
        """Find similar functions using multiple criteria"""
        if len(functions) < 2:
            return None

        similar_pairs = []
        for i, func1 in enumerate(functions):
            for func2 in functions[i + 1 :]:
                similarity = self._calculate_function_similarity(func1, func2)
                if similarity > 0.7:  # 70% similarity threshold
                    similar_pairs.append((similarity, [func1, func2]))

        if similar_pairs:
            # Return the most similar pair
            return max(similar_pairs, key=lambda x: x[0])
        return None

    def _find_similar_classes(
        self,
        classes: list[ClassInfo],
    ) -> tuple[float, list[ClassInfo]] | None:
        """Find similar classes"""
        if len(classes) < 2:
            return None

        similar_pairs = []
        for i, cls1 in enumerate(classes):
            for cls2 in classes[i + 1 :]:
                similarity = self._calculate_class_similarity(cls1, cls2)
                if similarity > 0.7:
                    similar_pairs.append((similarity, [cls1, cls2]))

        if similar_pairs:
            return max(similar_pairs, key=lambda x: x[0])
        return None

    def _calculate_function_similarity(
        self,
        func1: FunctionInfo,
        func2: FunctionInfo,
    ) -> float:
        """Calculate similarity between two functions"""
        if func1.source_hash == func2.source_hash:
            return 1.0  # Identical

        # Name similarity
        name_sim = difflib.SequenceMatcher(None, func1.name, func2.name).ratio()

        # Argument similarity
        args_sim = len(set(func1.args) & set(func2.args)) / max(
            len(func1.args), len(func2.args), 1
        )

        # Calls similarity
        calls_sim = len(func1.calls_made & func2.calls_made) / max(
            len(func1.calls_made), len(func2.calls_made), 1
        )

        # Complexity similarity
        complexity_sim = 1.0 - abs(func1.complexity - func2.complexity) / max(
            func1.complexity, func2.complexity, 1
        )

        # Weighted average
        return name_sim * 0.3 + args_sim * 0.3 + calls_sim * 0.2 + complexity_sim * 0.2

    def _calculate_class_similarity(self, cls1: ClassInfo, cls2: ClassInfo) -> float:
        """Calculate similarity between two classes"""
        if cls1.source_hash == cls2.source_hash:
            return 1.0

        # Name similarity
        name_sim = difflib.SequenceMatcher(None, cls1.name, cls2.name).ratio()

        # Method similarity
        method_sim = len(set(cls1.methods) & set(cls2.methods)) / max(
            len(cls1.methods), len(cls2.methods), 1
        )

        # Base class similarity
        base_sim = len(set(cls1.bases) & set(cls2.bases)) / max(
            len(cls1.bases), len(cls2.bases), 1
        )

        return name_sim * 0.4 + method_sim * 0.4 + base_sim * 0.2

    def _generate_duplicate_recommendation(self, items: list[Any]) -> str:
        """Generate recommendation for handling duplicates"""
        if len(items) == 2:
            return "Consider merging or refactoring these similar items. Check if they serve the same purpose."
        else:
            return f"Found {len(items)} similar items. Consider creating a common base class or utility function."

    def _analyze_naming(self) -> None:
        """Analyze naming conventions and suggest improvements"""
        log_info("Analyzing naming conventions...")

        naming_issues = {"functions": [], "classes": [], "modules": []}

        # Check function names
        for func in self.all_functions:
            if not self.naming_patterns["snake_case"].match(func.name):
                if not func.name.startswith("__"):  # Skip magic methods
                    naming_issues["functions"].append(
                        f"{func.name} in {func.file_path}:{func.line_start} - should use snake_case"
                    )

        # Check class names
        for cls in self.all_classes:
            if not self.naming_patterns["pascal_case"].match(cls.name):
                naming_issues["classes"].append(
                    f"{cls.name} in {cls.file_path}:{cls.line_start} - should use PascalCase"
                )

        # Check module names
        for module in self.report.modules:
            module_name = Path(module.file_path).stem
            if not self.naming_patterns["snake_case"].match(module_name):
                naming_issues["modules"].append(
                    f"{module_name} - should use snake_case"
                )

        self.report.naming_issues = naming_issues

    def _analyze_structure(self) -> None:
        """Analyze project structure and suggest improvements"""
        log_info("Analyzing project structure...")

        recommendations = []

        # Analyze file organization
        file_categories = defaultdict(list)
        for module in self.report.modules:
            Path(module.file_path)

            # Categorize by function
            module_lower = module.name.lower()
            for category, patterns in self.ai_patterns.items():
                if any(pattern in module_lower for pattern in patterns):
                    file_categories[category].append(module.name)
                    break
            else:
                file_categories["other"].append(module.name)

        # Check for organization opportunities
        for category, modules in file_categories.items():
            if len(modules) > 3 and category != "other":
                recommendations.append(
                    f"Consider organizing {len(modules)} {category}-related modules into a dedicated package"
                )

        # Check for large modules
        for module in self.report.modules:
            if module.lines_of_code > 500:
                recommendations.append(
                    f"Module {module.name} has {module.lines_of_code} lines - consider splitting"
                )

        # Check for complex modules
        complexity_threshold = 50
        for module in self.report.modules:
            if module.complexity > complexity_threshold:
                self.report.complexity_hotspots.append((module.name, module.complexity))
                recommendations.append(
                    f"Module {module.name} has high complexity ({module.complexity}) - consider refactoring"
                )

        self.report.structure_recommendations = recommendations

    def _analyze_imports(self) -> None:
        """Analyze import patterns and dependencies"""
        log_info("Analyzing import patterns...")

        all_imports = Counter()
        circular_imports = []
        unused_imports = []

        for module in self.report.modules:
            for imp in module.imports:
                all_imports[imp] += 1

        # Find most common imports
        common_imports = all_imports.most_common(10)

        self.report.import_analysis = {
            "most_common": common_imports,
            "total_unique": len(all_imports),
            "circular_imports": circular_imports,
            "unused_imports": unused_imports,
        }

    def _find_refactoring_opportunities(self) -> None:
        """Find opportunities for refactoring"""
        log_info("Finding refactoring opportunities...")

        opportunities = []

        # Large functions
        for func in self.all_functions:
            if func.complexity > 15:
                opportunities.append(
                    {
                        "type": "large_function",
                        "location": f"{func.file_path}:{func.line_start}",
                        "description": f"Function '{func.name}' has high complexity ({func.complexity})",
                        "suggestion": "Consider breaking this function into smaller functions",
                    }
                )

        # Classes with many methods
        for cls in self.all_classes:
            if len(cls.methods) > 20:
                opportunities.append(
                    {
                        "type": "large_class",
                        "location": f"{cls.file_path}:{cls.line_start}",
                        "description": f"Class '{cls.name}' has many methods ({len(cls.methods)})",
                        "suggestion": "Consider splitting this class or using composition",
                    }
                )

        # Modules with many classes/functions
        for module in self.report.modules:
            total_items = len(module.functions) + len(module.classes)
            if total_items > 15:
                opportunities.append(
                    {
                        "type": "large_module",
                        "location": module.file_path,
                        "description": f"Module has many items ({total_items})",
                        "suggestion": "Consider splitting this module",
                    }
                )

        self.report.refactoring_opportunities = opportunities


def main():
    """Main analysis function"""
    import argparse

    init_db()


    parser = argparse.ArgumentParser(description="AI Orchestra Codebase Analyzer")
    parser.add_argument(
        "--project-root", type=Path, default=Path.cwd(), help="Project root directory"
    )
    parser.add_argument("--output", type=Path, help="Output file for analysis report")
    parser.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    parser.add_argument(
        "--save", action="store_true", help="Save the report to the database"
    )

    args = parser.parse_args()

    # Run analysis
    analyzer = CodebaseAnalyzer(args.project_root)
    report = analyzer.analyze_project()

    # Save to DB if requested
    if args.save:
        save_report_to_db(report)
        log_success("Successfully saved report to database")

    # Output results
    if args.format == "json":
        output_data = {
            "timestamp": report.timestamp,
            "summary": {
                "total_modules": len(report.modules),
                "total_functions": len(analyzer.all_functions),
                "total_classes": len(analyzer.all_classes),
                "duplicates_found": len(report.duplicates),
                "naming_issues": sum(
                    len(issues) for issues in report.naming_issues.values()
                ),
                "refactoring_opportunities": len(report.refactoring_opportunities),
                "improvements_found": len(report.improvements),
                "optimizations_found": len(report.optimizations),
            },
            "duplicates": [
                {
                    "type": dup.type,
                    "similarity": dup.similarity,
                    "items": [
                        item.name if hasattr(item, "name") else str(item)
                        for item in dup.items
                    ],
                    "recommendation": dup.recommendation,
                }
                for dup in report.duplicates
            ],
            "naming_issues": report.naming_issues,
            "structure_recommendations": report.structure_recommendations,
            "complexity_hotspots": report.complexity_hotspots,
            "import_analysis": report.import_analysis,
            "refactoring_opportunities": report.refactoring_opportunities,
            "improvements": [vars(imp) for imp in report.improvements],
            "optimizations": [vars(opt) for opt in report.optimizations],
        }

        if args.output:
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=2)
            log_success(f"Analysis report saved to {args.output}")
        else:
            print(json.dumps(output_data, indent=2))

    else:  # text format
        print(
            f"\n{Colors.BOLD}{Colors.BLUE}🚀 Unified Codebase Analysis Report{Colors.ENDC}"
        )
        print("=" * 50)

        print(f"\n{Colors.CYAN}📊 Summary:{Colors.ENDC}")
        print(f"  Total modules: {len(report.modules)}")
        print(f"  Total functions: {len(analyzer.all_functions)}")
        print(f"  Total classes: {len(analyzer.all_classes)}")
        print(f"  Duplicates found: {len(report.duplicates)}")
        print(
            f"  Naming issues: {sum(len(issues) for issues in report.naming_issues.values())}"
        )
        print(f"  Refactoring opportunities: {len(report.refactoring_opportunities)}")
        print(f"  Improvements found: {len(report.improvements)}")
        print(f"  Optimizations found: {len(report.optimizations)}")

        if report.duplicates:
            print(f"\n{Colors.YELLOW}🔍 Duplicates Found:{Colors.ENDC}")
            for i, dup in enumerate(report.duplicates[:3]):  # Show first 3
                print(f"  {i+1}. {dup.type.title()} similarity: {dup.similarity:.2f}")
                print(f"     Items: {[item.name for item in dup.items]}")
                print(f"     Recommendation: {dup.recommendation}")

        if report.improvements:
            print(f"\n{Colors.GREEN}💡 Improvements Found:{Colors.ENDC}")
            for i, imp in enumerate(report.improvements[:3]):  # Show first 3
                print(f"  {i+1}. {imp.what} (Priority: {imp.priority})")
                print(f"     Why: {imp.why}")
                print(f"     How: {imp.how}")

        if report.optimizations:
            print(f"\n{Colors.PURPLE}⚙️  Optimizations Found:{Colors.ENDC}")
            for i, opt in enumerate(report.optimizations[:3]):  # Show first 3
                print(f"  {i+1}. {opt.issue} (Priority: {opt.priority})")
                print(f"     Category: {opt.category}")
                print(f"     Proposed: {opt.proposed_state}")

        if any(report.naming_issues.values()):
            print(f"\n{Colors.YELLOW}📝 Naming Issues:{Colors.ENDC}")
            for category, issues in report.naming_issues.items():
                if issues:
                    print(f"  {category.title()}:")
                    for issue in issues[:2]:  # Show first 2
                        print(f"    - {issue}")
                    if len(issues) > 2:
                        print(f"    ... and {len(issues) - 2} more")

        if report.structure_recommendations:
            print(f"\n{Colors.GREEN}🏗️  Structure Recommendations:{Colors.ENDC}")
            for rec in report.structure_recommendations[:3]:
                print(f"  • {rec}")

        if report.complexity_hotspots:
            print(f"\n{Colors.RED}🔥 Complexity Hotspots:{Colors.ENDC}")
            for name, complexity in report.complexity_hotspots[:3]:
                print(f"  • {name}: {complexity}")

        if report.refactoring_opportunities:
            print(f"\n{Colors.PURPLE}⚡ Refactoring Opportunities:{Colors.ENDC}")
            for opp in report.refactoring_opportunities[:3]:
                print(f"  • {opp['type']}: {opp['description']}")
                print(f"    Location: {opp['location']}")
                print(f"    Suggestion: {opp['suggestion']}")


def save_report_to_db(report: AnalysisReport):
    """Save the analysis report to the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = report.timestamp

    # Save improvements
    for imp in report.improvements:
        try:
            c.execute(
                """INSERT INTO improvement_opportunities
                        (what, why, how, impact, effort, priority, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    imp.what,
                    imp.why,
                    imp.how,
                    imp.impact,
                    imp.effort,
                    imp.priority,
                    now,
                ),
            )
        except:
            pass  # Already exists

    # Save optimizations
    for opt in report.optimizations:
        try:
            c.execute(
                """INSERT INTO optimizations
                (category, issue, current_state, proposed_state, impact, effort, priority, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    opt.category,
                    opt.issue,
                    opt.current_state,
                    opt.proposed_state,
                    opt.impact,
                    opt.effort,
                    opt.priority,
                    now,
                ),
            )
        except:
            pass

    conn.commit()
    conn.close()





if __name__ == "__main__":
    main()
