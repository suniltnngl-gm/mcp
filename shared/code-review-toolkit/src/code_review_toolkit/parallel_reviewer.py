#!/usr/bin/env python3
"""Parallel Reviewer for Code Reviews

This module provides a simple way to run reviews on multiple files in parallel,
significantly speeding up the process.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List

from .ai_reviewer import AICodeReviewer, AIReviewFinding


class ParallelReviewer:
    """Process multiple files in parallel"""

    def __init__(self, max_workers: int = 4):
        """Initialize the parallel reviewer

        Args:
            max_workers: Maximum number of parallel threads
        """
        self.max_workers = max_workers

    def review_batch_parallel(
        self, 
        files: List[Path], 
        reviewer: AICodeReviewer
    ) -> List[AIReviewFinding]:
        """Review multiple files concurrently

        Args:
            files: List of file paths to review
            reviewer: An instance of AICodeReviewer

        Returns:
            A list of all findings from the review
        """
        all_findings = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all review tasks
            future_to_file = {
                executor.submit(reviewer.review_file, f): f 
                for f in files
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                filepath = future_to_file[future]
                try:
                    findings = future.result()
                    all_findings.extend(findings)
                    print(f"✓ Reviewed {filepath.name}")
                except Exception as e:
                    print(f"✗ Failed to review {filepath.name}: {e}")
        
        return all_findings
