#!/usr/bin/env python3
"""
🚀 AI Orchestra - Performance Monitor
====================================
Development performance monitoring and optimization tools
"""

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil

from logging_config import setup_logging
from scripts.config_manager import is_path_ignored

# Setup logger
logger = setup_logging(__name__)


class PerformanceMonitor:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.perf_db = project_root / ".orchestration_reports" / "perf_metrics.db"
        self.perf_db.parent.mkdir(exist_ok=True)
        self.init_database()

    def init_database(self):
        """Initialize performance metrics database"""
        with sqlite3.connect(self.perf_db) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    metric_type TEXT,
                    metric_name TEXT,
                    value REAL,
                    metadata TEXT
                )
            """
            )

    def record_metric(
        self,
        metric_type: str,
        metric_name: str,
        value: float,
        metadata: dict = None,
    ):
        """Record a performance metric"""
        with sqlite3.connect(self.perf_db) as conn:
            conn.execute(
                "INSERT INTO metrics (timestamp, metric_type, metric_name, value, metadata) VALUES (?, ?, ?, ?, ?)",
                (
                    datetime.now().isoformat(),
                    metric_type,
                    metric_name,
                    value,
                    json.dumps(metadata or {}),
                ),
            )

    def get_system_metrics(self) -> dict[str, Any]:
        """Get current system performance metrics"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available_gb": psutil.virtual_memory().available / (1024**3),
            "disk_usage_percent": psutil.disk_usage("/").percent,
            "process_count": len(psutil.pids()),
            "load_average": (
                psutil.getloadavg()[0] if hasattr(psutil, "getloadavg") else 0
            ),
        }

    def get_project_metrics(self) -> dict[str, Any]:
        """Get project-specific metrics"""
        metrics = {}

        # Code metrics
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if not is_path_ignored(f)]

        total_lines = 0
        for file in python_files:
            try:
                with open(file, encoding="utf-8") as f:
                    total_lines += len(f.readlines())
            except:
                pass

        metrics.update(
            {
                "python_files_count": len(python_files),
                "total_lines_of_code": total_lines,
                "avg_lines_per_file": (
                    total_lines / len(python_files) if python_files else 0
                ),
            }
        )

        # Database size
        db_files = list(self.project_root.glob("*.db"))
        db_size_mb = (
            sum(f.stat().st_size for f in db_files) / (1024**2) if db_files else 0
        )
        metrics["database_size_mb"] = db_size_mb

        # Virtual environment size
        venv_path = self.project_root / ".venv"
        if venv_path.exists():
            try:
                import subprocess

                result = subprocess.run(
                    ["du", "-sh", str(venv_path)], capture_output=True, text=True
                )
                if result.returncode == 0:
                    size_str = result.stdout.split("\t")[0]
                    metrics["venv_size"] = size_str
            except:
                pass

        return metrics

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive performance report"""
        logger.info("Generating performance report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": self.get_system_metrics(),
            "project_metrics": self.get_project_metrics(),
        }

        # Record metrics to database
        for key, value in report["system_metrics"].items():
            if isinstance(value, int | float):
                self.record_metric("system", key, value)
        for key, value in report["project_metrics"].items():
            if isinstance(value, int | float):
                self.record_metric("project", key, value)

        return report


def main():
    parser = argparse.ArgumentParser(description="AI Orchestra Performance Monitor")
    parser.add_argument(
        "--context-in", type=str, help="Path to the input context file."
    )
    parser.parse_args()

    project_root = Path(__file__).parent.parent
    monitor = PerformanceMonitor(project_root)

    report = monitor.generate_report()

    # Output the report as a JSON object for the orchestrator
    output_context = {"performance_report": report}
    print(json.dumps(output_context))


if __name__ == "__main__":
    main()
