"""Pytest configuration"""
import pytest
from pathlib import Path


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def sample_python_file(temp_project_dir):
    """Create a sample Python file"""
    file_path = temp_project_dir / "sample.py"
    file_path.write_text("""
def hello():
    print("Hello, world!")
    return True
""")
    return file_path
