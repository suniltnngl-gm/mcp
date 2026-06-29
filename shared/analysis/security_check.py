#!/usr/bin/env python3
"""
🛡️ AI Orchestra - Security Checker
===================================

Scans for potential security vulnerabilities like hardcoded secrets.
"""

import argparse
import json
from pathlib import Path

from logging_config import setup_logging
from scripts.config_manager import is_path_ignored

# Setup logger
logger = setup_logging(__name__)


def check_dotenv_security(project_root: Path) -> list[str]:
    """Checks the .env file for security best practices."""
    warnings = []
    env_path = project_root / ".env"
    gitignore_path = project_root / ".gitignore"

    if not env_path.exists():
        return warnings

    try:
        env_content = env_path.read_text()
        if "sk-" in env_content:
            warnings.append(
                "Potential API key found in .env file. Ensure this file is not committed."
            )

        if gitignore_path.exists():
            gitignore_content = gitignore_path.read_text()
            if ".env" not in gitignore_content:
                warnings.append(".env file is not in .gitignore.")
        else:
            warnings.append(
                ".gitignore file not found. Cannot verify if .env is ignored."
            )

    except Exception as e:
        warnings.append(f"Error checking .env security: {e}")

    return warnings


def check_hardcoded_secrets(project_root: Path) -> list[dict]:
    """Scans Python files for hardcoded secrets."""
    findings = []
    secret_pattern = "sk-"

    for py_file in project_root.rglob("*.py"):
        if is_path_ignored(py_file):
            continue
        try:
            with open(py_file, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if secret_pattern in line:
                        findings.append(
                            {
                                "file": str(py_file.relative_to(project_root)),
                                "line_number": i,
                                "line_content": line.strip(),
                            }
                        )
        except Exception:
            # Ignore files that can't be read
            pass

    return findings


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Security Checker")
    parser.add_argument(
        "--context-in", type=str, help="Path to the input context file."
    )
    parser.parse_args()

    project_root = Path(__file__).parent.parent

    logger.info("🛡️ Running security scan...")

    dotenv_warnings = check_dotenv_security(project_root)
    hardcoded_secrets = check_hardcoded_secrets(project_root)

    for warning in dotenv_warnings:
        logger.warning(warning)

    if hardcoded_secrets:
        logger.error("Found potential hardcoded secrets!")
        for secret in hardcoded_secrets:
            logger.error(
                f"  - File: {secret['file']}, Line: {secret['line_number']}: {secret['line_content']}"
            )
    else:
        logger.info("✅ No hardcoded secrets found.")

    # Output the results as a JSON object for the orchestrator
    output_context = {
        "security_scan_results": {
            "dotenv_warnings": dotenv_warnings,
            "hardcoded_secrets": hardcoded_secrets,
        }
    }
    print(json.dumps(output_context))

    if hardcoded_secrets:
        exit(1)


if __name__ == "__main__":
    main()
