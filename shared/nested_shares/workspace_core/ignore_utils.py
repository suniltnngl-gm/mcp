"""Workspace Ignore Utilities - Daily use helpers"""

from pathlib import Path

# Daily use ignore patterns
DAILY_IGNORE_PATTERNS = [
    '.git/', '.venv/', 'venv/', 'node_modules/', '__pycache__/',
    '*.pyc', '*.pyo', '.pytest_cache/', '.mypy_cache/', '.ruff_cache/',
    '*.log', '*.tmp', '.DS_Store', 'archive/', 'artifacts/',
    '.cache/', 'dist/', 'build/', '.eggs/', '*.egg-info/'
]

def should_ignore_file(file_path: str) -> bool:
    """Check if file should be ignored for daily operations"""
    path_lower = file_path.lower()
    
    for pattern in DAILY_IGNORE_PATTERNS:
        if pattern.endswith('/'):
            # Directory pattern
            dir_pattern = pattern[:-1]
            if f"/{dir_pattern}/" in path_lower or path_lower.endswith(f"/{dir_pattern}"):
                return True
        elif pattern.startswith('*.'):
            # Extension pattern
            if path_lower.endswith(pattern[1:]):
                return True
        else:
            # Substring pattern
            if pattern in path_lower:
                return True
    
    return False

def scan_directory_filtered(directory: str, file_types: list = None) -> list:
    """Scan directory excluding ignored files"""
    directory_path = Path(directory)
    files = []
    
    for file_path in directory_path.rglob("*"):
        if file_path.is_file():
            if should_ignore_file(str(file_path)):
                continue
            
            if file_types and file_path.suffix not in file_types:
                continue
            
            files.append(file_path)
    
    return files

def get_user_files_only(directory: str) -> list:
    """Get only user-created files, excluding vendor/generated"""
    all_files = scan_directory_filtered(directory)
    vendor_patterns = ['.venv/', 'node_modules/', 'site-packages/']
    return [f for f in all_files if not any(p in str(f) for p in vendor_patterns)]
