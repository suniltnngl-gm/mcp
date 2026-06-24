#!/usr/bin/env python3
"""Language Detector for Code Reviews

This module provides utilities to detect the programming language of a file
based on its extension.
"""

from pathlib import Path
from typing import Dict


class LanguageDetector:
    """Auto-detect file language and route to appropriate reviewer"""
    
    LANGUAGE_MAP: Dict[str, str] = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.go': 'golang',
        '.rs': 'rust',
        '.java': 'java',
        '.rb': 'ruby',
        '.php': 'php',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'c_header',
        '.hpp': 'cpp_header',
        '.cs': 'csharp',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.sh': 'bash',
        '.bat': 'batch',
        '.ps1': 'powershell',
        '.sql': 'sql',
    }
    
    def detect(self, filepath: Path) -> str:
        """Detect language from file extension"""
        return self.LANGUAGE_MAP.get(filepath.suffix.lower(), 'unknown')


if __name__ == "__main__":
    # Example usage
    detector = LanguageDetector()
    
    print(f"Python file: {detector.detect(Path("main.py"))}")
    print(f"JavaScript file: {detector.detect(Path("script.js"))}")
    print(f"TypeScript file: {detector.detect(Path("app.ts"))}")
    print(f"Unknown file: {detector.detect(Path("document.txt"))}")
    print(f"Markdown file: {detector.detect(Path("README.md"))}")
