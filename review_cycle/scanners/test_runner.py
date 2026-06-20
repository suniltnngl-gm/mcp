import subprocess
from pathlib import Path
from typing import List

from review_cycle.models import ScanFinding


HOME = Path.home()
PROJECT_DIR = HOME / "Public" / "project"


class TestRunner:
    def __init__(self, project_dir: Path = PROJECT_DIR):
        self.project_dir = project_dir

    def scan(self) -> List[ScanFinding]:
        findings = []
        venv_python = (
            self.project_dir / ".venv" / "bin" / "python"
        )
        python_cmd = str(venv_python) if venv_python.exists() else "python3"
        test_dir = self.project_dir / "tests"
        if not test_dir.exists():
            findings.append(
                ScanFinding(
                    repo="project",
                    category="test_missing",
                    severity="info",
                    summary="No tests/ directory found",
                    detail=f"Expected at {test_dir}",
                    file_path=str(self.project_dir),
                    suggested_action="Consider adding test infrastructure",
                    score=0.2,
                )
            )
            return findings

        try:
            result = subprocess.run(
                [python_cmd, "-m", "pytest", "tests/", "--tb=short", "-q"],
                cwd=self.project_dir,
                capture_output=True,
                text=True,
                timeout=120,
            )
            passed = result.returncode == 0
            output = result.stdout + result.stderr
            lines = output.strip().splitlines()
            summary_line = ""
            for line in reversed(lines):
                if "passed" in line or "failed" in line or "error" in line:
                    summary_line = line
                    break
            findings.append(
                ScanFinding(
                    repo="project",
                    category="test_result",
                    severity="info" if passed else "critical",
                    summary=f"Tests {'PASSED' if passed else 'FAILED'}",
                    detail=summary_line or output[:500],
                    file_path=str(test_dir),
                    suggested_action=(
                        "Tests pass — no action needed"
                        if passed
                        else "Review test output and fix failures"
                    ),
                    score=0.0 if passed else 0.8,
                )
            )
            if not passed:
                fail_lines = [
                    l for l in lines
                    if "FAILED" in l or "ERROR" in l
                ]
                for fl in fail_lines[:5]:
                    findings.append(
                        ScanFinding(
                            repo="project",
                            category="test_failure",
                            severity="critical",
                            summary=f"Test failure: {fl}",
                            detail=fl,
                            suggested_action="Fix the failing test",
                            score=0.7,
                        )
                    )
        except subprocess.TimeoutExpired:
            findings.append(
                ScanFinding(
                    repo="project",
                    category="test_timeout",
                    severity="warning",
                    summary="Test suite timed out (>120s)",
                    detail="Test suite took longer than 120 seconds",
                    file_path=str(test_dir),
                    suggested_action="Check for hanging tests or increase timeout",
                    score=0.5,
                )
            )
        except FileNotFoundError:
            findings.append(
                ScanFinding(
                    repo="project",
                    category="test_no_runner",
                    severity="warning",
                    summary="pytest not found",
                    detail=f"Could not run pytest at {self.project_dir}",
                    suggested_action="Install pytest",
                    score=0.4,
                )
            )
        return findings
