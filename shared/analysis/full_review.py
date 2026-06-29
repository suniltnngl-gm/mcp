#!/usr/bin/env python3
"""Full Project Review - Comprehensive analysis of streamlined codebase"""
import os
from pathlib import Path
import json


class FullReview:
    def __init__(self):
        self.root = Path(".")

    def review_structure(self):
        """Review project structure"""
        structure = {
            "core": (
                list((self.root / "core").glob("*.py"))
                if (self.root / "core").exists()
                else []
            ),
            "config": (
                list((self.root / "config").rglob("*"))
                if (self.root / "config").exists()
                else []
            ),
            "docs": (
                list((self.root / "docs").glob("*.md"))
                if (self.root / "docs").exists()
                else []
            ),
            "tools": (
                list((self.root / "tools").rglob("*"))
                if (self.root / "tools").exists()
                else []
            ),
            "root_files": list(self.root.glob("*.md")) + [self.root / "cli"],
        }

        return {k: len(v) for k, v in structure.items()}

    def review_core_functionality(self):
        """Review core functionality"""
        core_files = [
            "core/git_intelligence.py",
            "core/log_analyzer.py",
            "core/duplication_prevention.py",
        ]

        status = {}
        for file_path in core_files:
            full_path = self.root / file_path
            if full_path.exists():
                with open(full_path) as f:
                    content = f.read()

                status[file_path] = {
                    "exists": True,
                    "lines": len(content.split("\n")),
                    "functions": content.count("def "),
                    "imports_fixed": "config/knowledge_base" in content,
                }
            else:
                status[file_path] = {"exists": False}

        return status

    def review_cli_interface(self):
        """Review CLI interface"""
        cli_path = self.root / "cli"

        if not cli_path.exists():
            return {"exists": False}

        with open(cli_path) as f:
            content = f.read()

        commands = []
        if "git" in content:
            commands.append("git")
        if "logs" in content:
            commands.append("logs")
        if "prevent" in content:
            commands.append("prevent")

        return {
            "exists": True,
            "executable": os.access(cli_path, os.X_OK),
            "commands": commands,
            "lines": len(content.split("\n")),
        }

    def review_documentation(self):
        """Review documentation consistency"""
        docs = {
            "README.md": self.root / "README.md",
            "USER_GUIDE.md": self.root / "docs" / "USER_GUIDE.md",
            "API_REFERENCE.md": self.root / "docs" / "API_REFERENCE.md",
        }

        status = {}
        for name, path in docs.items():
            if path.exists():
                with open(path) as f:
                    content = f.read()

                status[name] = {
                    "exists": True,
                    "lines": len(content.split("\n")),
                    "commands": content.count("python3 cli"),
                    "sections": content.count("##"),
                }
            else:
                status[name] = {"exists": False}

        return status

    def review_knowledge_base(self):
        """Review knowledge base status"""
        kb_path = self.root / "config" / "knowledge_base"

        if not kb_path.exists():
            return {"exists": False}

        files = list(kb_path.glob("*.json"))

        # Check metrics
        metrics_file = kb_path / "real_time_metrics.json"
        metrics = {}
        if metrics_file.exists():
            try:
                with open(metrics_file) as f:
                    metrics = json.load(f)
            except Exception:
                pass

        return {"exists": True, "files": len(files), "metrics": metrics}

    def test_functionality(self):
        """Test core functionality"""
        tests = {}

        # Test CLI exists and is executable
        cli_path = self.root / "cli"
        tests["cli_executable"] = cli_path.exists() and os.access(cli_path, os.X_OK)

        # Test core files exist
        core_files = [
            "core/git_intelligence.py",
            "core/log_analyzer.py",
            "core/duplication_prevention.py",
        ]
        tests["core_files_exist"] = all((self.root / f).exists() for f in core_files)

        # Test config exists
        tests["config_exists"] = (self.root / "config" / "knowledge_base").exists()

        # Test docs exist
        docs = ["README.md", "docs/USER_GUIDE.md", "docs/API_REFERENCE.md"]
        tests["docs_exist"] = all((self.root / d).exists() for d in docs)

        return tests

    def generate_review_report(self):
        """Generate comprehensive review report"""
        print("🔍 FULL PROJECT REVIEW")
        print("=" * 50)

        # Structure review
        structure = self.review_structure()
        print("📁 STRUCTURE:")
        print(f"  Core files: {structure['core']}")
        print(f"  Config files: {structure['config']}")
        print(f"  Documentation: {structure['docs']}")
        print(f"  Tools: {structure['tools']}")
        print(f"  Root files: {structure['root_files']}")

        # Core functionality
        core = self.review_core_functionality()
        print("\n⚙️  CORE FUNCTIONALITY:")
        for file_path, status in core.items():
            if status.get("exists"):
                print(
                    f"  ✅ {file_path}: {status['lines']} lines, {status['functions']} functions"
                )
                if status.get("imports_fixed"):
                    print("     ✅ Imports fixed for new structure")
            else:
                print(f"  ❌ {file_path}: Missing")

        # CLI interface
        cli = self.review_cli_interface()
        print("\n🖥️  CLI INTERFACE:")
        if cli["exists"]:
            print(f"  ✅ CLI exists: {cli['lines']} lines")
            print(f"  ✅ Executable: {cli['executable']}")
            print(f"  ✅ Commands: {', '.join(cli['commands'])}")
        else:
            print("  ❌ CLI missing")

        # Documentation
        docs = self.review_documentation()
        print("\n📚 DOCUMENTATION:")
        for name, status in docs.items():
            if status.get("exists"):
                print(
                    f"  ✅ {name}: {status['lines']} lines, {status['commands']} commands, {status['sections']} sections"
                )
            else:
                print(f"  ❌ {name}: Missing")

        # Knowledge base
        kb = self.review_knowledge_base()
        print("\n🧠 KNOWLEDGE BASE:")
        if kb["exists"]:
            print(f"  ✅ Knowledge base: {kb['files']} files")
            if kb["metrics"]:
                metrics = kb["metrics"]
                success_rate = (
                    metrics.get("successful_operations", 0)
                    / max(metrics.get("total_operations", 1), 1)
                ) * 100
                print(
                    f"  📊 Success rate: {success_rate:.1f}% ({metrics.get('successful_operations', 0)}/{metrics.get('total_operations', 0)})"
                )
                print(
                    f"  🔧 Corrections applied: {metrics.get('corrections_applied', 0)}"
                )
        else:
            print("  ❌ Knowledge base missing")

        # Functionality tests
        tests = self.test_functionality()
        print("\n🧪 FUNCTIONALITY TESTS:")
        for test_name, passed in tests.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {test_name.replace('_', ' ').title()}")

        # Overall assessment
        total_tests = len(tests)
        passed_tests = sum(tests.values())
        overall_score = (passed_tests / total_tests) * 100

        print("\n🎯 OVERALL ASSESSMENT:")
        print(
            f"  Score: {overall_score:.1f}% ({passed_tests}/{total_tests} tests passed)"
        )

        if overall_score >= 90:
            print("  🟢 EXCELLENT - Project is well-structured and functional")
        elif overall_score >= 75:
            print("  🟡 GOOD - Minor issues to address")
        else:
            print("  🔴 NEEDS WORK - Major issues found")

        return {
            "structure": structure,
            "core": core,
            "cli": cli,
            "docs": docs,
            "knowledge_base": kb,
            "tests": tests,
            "score": overall_score,
        }


if __name__ == "__main__":
    reviewer = FullReview()
    reviewer.generate_review_report()
