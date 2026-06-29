#!/usr/bin/env python3
"""Week 1: Basic Audit Tools"""

import json
import subprocess
from datetime import datetime
from pathlib import Path


def run_audit_tools():
    """Run basic audit and analysis tools"""
    print("📊 Running AI Orchestra Audit Tools...")

    # Ensure reports directory exists
    reports_dir = Path("reports/baseline")
    reports_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "timestamp": datetime.now().isoformat(),
        "audit_type": "basic",
        "tools_run": [],
    }

    # Test for available tools
    tools = [
        ("python", ["-m", "pylint", "--version"], "Pylint static analysis"),
        ("python", ["-m", "mypy", "--version"], "MyPy type checking"),
        ("python", ["-m", "bandit", "--version"], "Bandit security analysis"),
    ]

    print("\n🔍 Checking available analysis tools:")
    for tool_name, cmd, description in tools:
        try:
            result = subprocess.run(
                [tool_name] + cmd, capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print(f"  ✅ {description} - Available")
                results["tools_run"].append(
                    {
                        "tool": description,
                        "status": "available",
                        "version_info": result.stdout.strip()[:100],
                    }
                )
            else:
                print(f"  ⚠️ {description} - Not available")
                results["tools_run"].append(
                    {"tool": description, "status": "not_available"}
                )
        except Exception as e:
            print(f"  ❌ {description} - Error: {e}")
            results["tools_run"].append(
                {"tool": description, "status": "error", "error": str(e)}
            )

    # Basic file analysis
    print("\n📁 Basic codebase analysis:")
    python_files = list(Path(".").rglob("*.py"))
    python_files = [
        f for f in python_files if "venv" not in str(f) and "__pycache__" not in str(f)
    ]

    results["basic_stats"] = {
        "python_files": len(python_files),
        "total_lines": 0,
        "files_analyzed": [],
    }

    total_lines = 0
    for py_file in python_files[:20]:  # Analyze first 20 files
        try:
            content = py_file.read_text()
            lines = len(content.splitlines())
            total_lines += lines
            results["basic_stats"]["files_analyzed"].append(
                {"file": str(py_file), "lines": lines}
            )
        except Exception as e:
            print(f"  ⚠️ Could not analyze {py_file}: {e}")

    results["basic_stats"]["total_lines"] = total_lines
    print(f"  📊 Found {len(python_files)} Python files")
    print(f"  📊 Analyzed {len(results['basic_stats']['files_analyzed'])} files")
    print(f"  📊 Total lines analyzed: {total_lines}")

    # Save results
    with open(reports_dir / "basic_audit.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n✅ Audit complete! Results saved to reports/baseline/basic_audit.json")
    print("\n📋 Install missing tools with:")
    print("  pip install pylint mypy bandit radon")

    return results


if __name__ == "__main__":
    run_audit_tools()
