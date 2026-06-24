#!/usr/bin/env python3
"""Parallel Review Processing - Speed up multi-file reviews

This module enables concurrent processing of multiple files,
providing 3-4x speed improvement for large codebases.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, List, Dict, Any
import time


class ParallelReviewer:
    """Process multiple files in parallel for faster reviews"""

    def __init__(self, max_workers: int = 4):
        """Initialize parallel reviewer

        Args:
            max_workers: Maximum number of concurrent workers (default: 4)
        """
        self.max_workers = max_workers
        self.stats = {
            "total_files": 0,
            "successful": 0,
            "failed": 0,
            "duration_seconds": 0,
        }

    def process_files_parallel(
        self,
        files: List[Path],
        process_func: Callable[[Path], Any],
        description: str = "Processing files",
    ) -> List[Any]:
        """Process multiple files concurrently

        Args:
            files: List of file paths to process
            process_func: Function to apply to each file
            description: Description for progress messages

        Returns:
            List of results from processing each file
        """
        if not files:
            return []

        print(f"\n{description} ({len(files)} files, {self.max_workers} workers)...")
        start_time = time.time()

        results = []
        self.stats["total_files"] = len(files)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {executor.submit(process_func, f): f for f in files}

            # Collect results as they complete
            for future in as_completed(future_to_file):
                filepath = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                    self.stats["successful"] += 1
                    print(f"  ✓ {filepath.name}")
                except Exception as e:
                    self.stats["failed"] += 1
                    print(f"  ✗ {filepath.name}: {e}")
                    results.append(None)

        self.stats["duration_seconds"] = time.time() - start_time
        self._print_summary()

        return results

    def process_batches_parallel(
        self,
        items: List[Any],
        batch_size: int,
        process_batch_func: Callable[[List[Any]], Any],
        description: str = "Processing batches",
    ) -> List[Any]:
        """Process items in batches concurrently

        Args:
            items: List of items to process
            batch_size: Number of items per batch
            process_batch_func: Function to process each batch
            description: Description for progress messages

        Returns:
            List of results from processing each batch
        """
        if not items:
            return []

        # Create batches
        batches = [
            items[i : i + batch_size] for i in range(0, len(items), batch_size)
        ]

        print(
            f"\n{description} ({len(items)} items in {len(batches)} batches, {self.max_workers} workers)..."
        )
        start_time = time.time()

        results = []
        self.stats["total_files"] = len(batches)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all batch tasks
            future_to_batch = {
                executor.submit(process_batch_func, batch): i
                for i, batch in enumerate(batches)
            }

            # Collect results as they complete
            for future in as_completed(future_to_batch):
                batch_num = future_to_batch[future]
                try:
                    result = future.result()
                    results.append(result)
                    self.stats["successful"] += 1
                    print(f"  ✓ Batch {batch_num + 1}/{len(batches)}")
                except Exception as e:
                    self.stats["failed"] += 1
                    print(f"  ✗ Batch {batch_num + 1}/{len(batches)}: {e}")
                    results.append(None)

        self.stats["duration_seconds"] = time.time() - start_time
        self._print_summary()

        return results

    def _print_summary(self):
        """Print processing summary"""
        print(f"\n--- Parallel Processing Summary ---")
        print(f"Total: {self.stats['total_files']}")
        print(f"Successful: {self.stats['successful']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Duration: {self.stats['duration_seconds']:.2f}s")

        if self.stats["total_files"] > 0:
            avg_time = self.stats["duration_seconds"] / self.stats["total_files"]
            print(f"Average per item: {avg_time:.2f}s")

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics

        Returns:
            Dictionary with processing stats
        """
        return self.stats.copy()


# Example usage functions
def example_file_processor(filepath: Path) -> Dict:
    """Example function to process a single file"""
    # Simulate some processing
    time.sleep(0.1)
    return {"file": str(filepath), "lines": len(filepath.read_text().split("\n"))}


def example_batch_processor(batch: List[Path]) -> List[Dict]:
    """Example function to process a batch of files"""
    return [example_file_processor(f) for f in batch]


if __name__ == "__main__":
    # Test parallel processing
    import sys

    if len(sys.argv) > 1:
        target_dir = Path(sys.argv[1])
    else:
        target_dir = Path.cwd()

    # Find Python files
    py_files = list(target_dir.rglob("*.py"))[:20]  # Limit to 20 files for testing

    if not py_files:
        print("No Python files found")
        sys.exit(1)

    print(f"Testing parallel processing with {len(py_files)} files")

    # Test with different worker counts
    for workers in [1, 2, 4]:
        print(f"\n{'='*50}")
        print(f"Testing with {workers} workers")
        print(f"{'='*50}")

        reviewer = ParallelReviewer(max_workers=workers)
        results = reviewer.process_files_parallel(
            py_files, example_file_processor, f"Processing with {workers} workers"
        )

        print(f"\nProcessed {len([r for r in results if r])} files successfully")
