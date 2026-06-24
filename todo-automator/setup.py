#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="git-todo-monitor",
    version="1.0.0",
    author="Git Todo Monitor Contributors",
    description="Automated git monitoring with AI-powered todo summaries and GitHub integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/git-todo-monitor",
    py_modules=[
        "git_todo_monitor",
        "github_integration",
        "task_manager",
        "roadmap_planner",
        "test_monitor"
    ],
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.9",
    install_requires=[
        "gitpython>=3.1.0",
        "ollama>=0.4.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pylint>=2.0.0",
            "black>=22.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "git-todo-monitor=git_todo_monitor:main",
        ],
    },
    scripts=["monitor", "setup_cron.sh", "install_commit_hook.sh"],
    include_package_data=True,
)
