#!/usr/bin/env python3
"""Metrics Collector for Code Reviews

This module collects and analyzes metrics related to code review processes,
providing insights into code quality trends and cost efficiency.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List


class MetricsCollector:
    """Collect and analyze review metrics"""
    
    def __init__(self, metrics_file: Path = None):
        """Initialize MetricsCollector

        Args:
            metrics_file: Path to the JSON file for storing metrics (default: .review_metrics.json)
        """
        if metrics_file is None:
            metrics_file = Path.cwd() / ".review_metrics.json"

        self.metrics_file = metrics_file
        self.metrics = self._load_metrics()

    def _load_metrics(self) -> Dict:
        """Load metrics from file"""
        if self.metrics_file.exists():
            try:
                return json.loads(self.metrics_file.read_text())
            except json.JSONDecodeError:
                print(f"Warning: Metrics file {self.metrics_file} is corrupted. Starting new.")
        return {"reviews": []}

    def _save_metrics(self):
        """Save metrics to file"""
        self.metrics_file.write_text(json.dumps(self.metrics, indent=2))

    def record_review(self, review_data: Dict):
        """Record review session metrics"""
        review_data['timestamp'] = datetime.now().isoformat()
        self.metrics['reviews'].append(review_data)
        self._save_metrics()

    def get_trends(self) -> Dict:
        """Analyze trends over time"""
        reviews = self.metrics['reviews']
        if not reviews:
            return {}

        total_files_reviewed = sum(r.get('files_reviewed', 0) for r in reviews)
        total_findings = sum(r.get('findings_count', 0) for r in reviews)
        total_api_calls = sum(r.get('api_calls', 0) for r in reviews)
        total_cost_estimate = sum(r.get('cost_estimate', 0) for r in reviews)

        return {
            'total_reviews': len(reviews),
            'total_files_reviewed': total_files_reviewed,
            'total_findings': total_findings,
            'avg_findings_per_file': (total_findings / total_files_reviewed) if total_files_reviewed > 0 else 0,
            'total_api_calls': total_api_calls,
            'total_cost_estimate': total_cost_estimate,
            # Add more trend analysis as needed
        }

    def generate_report(self) -> str:
        """Generate a markdown report of metrics"""
        trends = self.get_trends()
        if not trends:
            return "No review metrics available to generate report."

        report = f"""
# Code Review Metrics Report

## Summary
- Total Reviews: {trends.get('total_reviews', 0)}
- Total Files Reviewed: {trends.get('total_files_reviewed', 0)}
- Total Findings: {trends.get('total_findings', 0)}
- Average Findings per File: {trends.get('avg_findings_per_file', 0):.2f}

## Cost Analysis
- Total API Calls: {trends.get('total_api_calls', 0)}
- Total Estimated Cost: ${trends.get('total_cost_estimate', 0):.4f}

## Detailed Reviews
"""
        for review in self.metrics['reviews']:
            report += f"\n### Review on {review.get('timestamp', 'N/A')}\n"
            report += f"- Status: {review.get('status', 'N/A')}\n"
            report += f"- Files Reviewed: {review.get('files_reviewed', 0)}\n"
            report += f"- Findings Count: {review.get('findings_count', 0)}\n"
            report += f"- API Calls: {review.get('api_calls', 0)}\n"
            report += f"- Estimated Cost: ${review.get('cost_estimate', 0):.4f}\n"
            if review.get('severity_breakdown'):
                report += f"- Severity Breakdown: {review['severity_breakdown']}\n"

        return report


if __name__ == "__main__":
    # Example usage
    collector = MetricsCollector()

    # Simulate a review
    collector.record_review({
        "status": "success",
        "files_reviewed": 5,
        "findings_count": 12,
        "api_calls": 3,
        "cost_estimate": 0.003,
        "severity_breakdown": {"high": 2, "medium": 5, "low": 5},
    })

    collector.record_review({
        "status": "failure",
        "files_reviewed": 10,
        "findings_count": 25,
        "api_calls": 7,
        "cost_estimate": 0.007,
        "severity_breakdown": {"critical": 1, "high": 5, "medium": 10, "low": 9},
    })

    print(collector.generate_report())
