#!/usr/bin/env python3
"""Lightweight Naming Convention Checker"""

import re
import sys
from enum import Enum
from pathlib import Path


class NamingConvention(Enum):
    SNAKE_CASE = "snake_case"
    CAMEL_CASE = "camelCase"
    PASCAL_CASE = "PascalCase"
    KEBAB_CASE = "kebab-case"
    SCREAMING_SNAKE_CASE = "SCREAMING_SNAKE_CASE"
    MIXED = "mixed"
    UNKNOWN = "unknown"


def detect_naming_convention(name: str) -> NamingConvention:
    if re.match(r"^[A-Z][A-Z0-9_]*$", name):
        return NamingConvention.SCREAMING_SNAKE_CASE
    elif re.match(r"^[A-Z][a-zA-Z0-9]*$", name):
        return NamingConvention.PASCAL_CASE
    elif re.match(r"^[a-z][a-zA-Z0-9]*$", name) and any(c.isupper() for c in name):
        return NamingConvention.CAMEL_CASE
    elif re.match(r"^[a-z][a-z0-9_]*$", name):
        return NamingConvention.SNAKE_CASE
    elif "-" in name and re.match(r"^[a-z][a-z0-9-]*$", name):
        return NamingConvention.KEBAB_CASE
    elif any(c.isupper() for c in name) and any(c.islower() for c in name):
        return NamingConvention.MIXED
    else:
        return NamingConvention.UNKNOWN


def get_preferred_convention(file_path: str) -> NamingConvention:
    if file_path.endswith(".py"):
        return NamingConvention.SNAKE_CASE
    elif any(doc_ext in file_path for doc_ext in [".md", ".rst", ".txt"]):
        return NamingConvention.SCREAMING_SNAKE_CASE
    else:
        return NamingConvention.SNAKE_CASE


def check_file_naming(file_path: str):
    file_name = Path(file_path).name

    # Allow exceptions for CLI files
    exceptions = {
        "orchestra_cli.py",  # Main CLI interface
        "ai_provider_manager.py",  # Core manager
        "ai_orchestra.py",  # Main module
    }

    if file_name in exceptions:
        return 0

    current_convention = detect_naming_convention(file_name)
    preferred_convention = get_preferred_convention(file_path)

    if current_convention != preferred_convention:
        print(
            f"Naming convention violation in {file_path}: "
            f"'{file_name}' is {current_convention.value}, "
            f"should be {preferred_convention.value}"
        )
        return 1
    return 0


if __name__ == "__main__":
    exit_code = 0
    for file_path in sys.argv[1:]:
        exit_code |= check_file_naming(file_path)
    sys.exit(exit_code)
