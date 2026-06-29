import re
from pathlib import Path

from rich.console import Console

from scripts.config_manager import is_path_ignored

console = Console()


class SecurityMonitor:
    """Monitors project security."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def security_scan(self) -> dict:
        """Comprehensive security scan."""
        console.print("🛡️ Running security scan...")

        security_results = {}

        # 1. Check for hardcoded secrets
        console.print("  🔍 Scanning for hardcoded secrets...")
        secret_patterns = [
            r"sk-[a-zA-Z0-9]{48}",  # OpenAI API keys
            r"gsk_[a-zA-Z0-9]{52}",  # Google API keys
            r"anthropic_[a-zA-Z0-9]{32}",  # Anthropic keys
            r"password\s*=\s*['\"][^'\"]+['\"]",  # Hardcoded passwords
            r"token\s*=\s*['\"][^'\"]+['\"]",  # Hardcoded tokens
        ]

        secret_findings = []
        for py_file in self.project_root.rglob("*.py"):
            if is_path_ignored(py_file):
                continue

            try:
                content = py_file.read_text()
                for pattern in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        secret_findings.append(
                            {
                                "file": str(py_file.relative_to(self.project_root)),
                                "pattern": pattern,
                                "matches": len(matches),
                            }
                        )
            except Exception:
                continue

        security_results["secret_scan"] = {
            "findings": secret_findings,
            "clean": len(secret_findings) == 0,
        }

        # 2. Check .env file security
        console.print("  🔐 Checking .env security...")
        env_file = self.project_root / ".env"
        env_security = {
            "env_exists": env_file.exists(),
            "in_gitignore": False,
            "has_example": (self.project_root / ".env.example").exists(),
        }

        gitignore_file = self.project_root / ".gitignore"
        if gitignore_file.exists():
            gitignore_content = gitignore_file.read_text()
            env_security["in_gitignore"] = ".env" in gitignore_content

        security_results["env_security"] = env_security

        # 3. Check file permissions
        console.print("  📋 Checking file permissions...")
        sensitive_files = [".env", "ai_orchestra.db"]
        permission_issues = []

        for file_name in sensitive_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                # Check if file is world-readable (simplified check)
                stat_info = file_path.stat()
                if stat_info.st_mode & 0o044:  # World or group readable
                    permission_issues.append(
                        {"file": file_name, "issue": "File may be readable by others"}
                    )

        security_results["permissions"] = {
            "issues": permission_issues,
            "clean": len(permission_issues) == 0,
        }

        return security_results
