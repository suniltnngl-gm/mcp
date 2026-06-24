#!/usr/bin/env python3
"""AI-Assisted Code Review Module
Leverages LLM providers to perform intelligent code quality analysis

Usage:
  uv run python -m review_modules.ai_code_reviewer /path/to/project
  OR
  uv run python review_modules/ai_code_reviewer.py /path/to/project
"""

import json
import subprocess # Added for Gemini CLI integration
import time # Added for timing CLI calls

# Import existing provider infrastructure
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .review_cache import ReviewCache
from .git_diff_helper import GitDiffHelper
from .language_detector import LanguageDetector
from .metrics_collector import MetricsCollector
from code_review_toolkit.common_types import AIReviewFinding
from concurrent.futures import ThreadPoolExecutor, as_completed


class AICodeReviewer:
    """AI-powered code review using LLM providers"""

    REVIEW_ASPECTS = {
        "security": "Identify security vulnerabilities, injection risks, authentication issues",
        "performance": "Detect performance bottlenecks, inefficient algorithms, resource leaks",
        "maintainability": "Find code smells, complex logic, poor naming, lack of modularity",
        "style": "Check code style consistency, PEP8 compliance, best practices",
        "documentation": "Evaluate docstrings, comments, API documentation quality",
    }

    def __init__(self, provider: str = "gemini_api", model: Optional[str] = None, improvement_manager: Optional[ImprovementManager] = None, enable_cache: bool = True, cache_ttl_hours: int = 24):
        """Initialize AI Code Reviewer

        Args:
            provider: "gemini_api" or "openai_api"
            model: Optional model name (uses defaults if not specified)
            improvement_manager: Optional ImprovementManager instance
            enable_cache: Enable caching to reduce API calls (default: True)
            cache_ttl_hours: Cache time-to-live in hours (default: 24)

        """
        self.provider = provider
        self.model = model
        self.findings: List[AIReviewFinding] = []
        self.improvement_manager = improvement_manager # Store ImprovementManager instance
        
        # Initialize cache
        self.enable_cache = enable_cache
        self.cache = ReviewCache(ttl_hours=cache_ttl_hours) if enable_cache else None
        self.language_detector = LanguageDetector()
        self.metrics_collector = MetricsCollector()

    def _call_llm(self, prompt: str) -> Tuple[bool, str]:
        """Call the configured LLM provider using Gemini CLI"""
        start_time = time.time()
        try:
            if self.provider == "gemini_api":
                # Use gemini CLI directly
                model_name = self.model if self.model else "gemini-2.5-flash" # Use configured model or default
                command = ["gemini", "-m", model_name, "-p", prompt, "--output-format", "json"]
                print(f"DEBUG: Executing Gemini CLI command: {' '.join(command[:4])} ...") # Log command, truncate prompt
                process = subprocess.run(command, capture_output=True, text=True, check=False, timeout=60) # Added timeout
                end_time = time.time()
                print(f"DEBUG: Gemini CLI call took {end_time - start_time:.2f} seconds.")

                if process.returncode != 0:
                    error_msg = f"Gemini CLI command failed with exit code {process.returncode}. Stderr: {process.stderr.strip()}"
                    print(f"ERROR: {error_msg}")
                    return False, error_msg
                else:
                    return True, process.stdout
            else:
                return False, f"Unknown provider or provider not configured for CLI: {self.provider}"
        except subprocess.TimeoutExpired:
            end_time = time.time()
            error_msg = f"Gemini CLI command timed out after {end_time - start_time:.2f} seconds."
            print(f"ERROR: {error_msg}")
            return False, error_msg
        except FileNotFoundError:
            error_msg = "Gemini CLI not found. Please ensure it's installed and in your PATH."
            print(f"ERROR: {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"An unexpected error occurred during Gemini CLI call: {e}"
            print(f"ERROR: {error_msg}")
            return False, error_msg

    def _build_batched_review_prompt(self, batch: List[Dict], aspects: List[str], root_dir: Path) -> str:
        """Build a structured prompt for code review of a batch of files."""
        aspects_desc = "\n".join(
            [f"- {aspect}: {self.REVIEW_ASPECTS[aspect]}" for aspect in aspects],
        )

        files_content = []
        for item in batch:
            filepath = item["filepath"]
            content = item["content"]
            files_content.append(f"""--- File: {filepath.relative_to(root_dir)} ---
```
{content}
```""")

        prompt = f"""You are an expert code reviewer. Analyze the following code files for quality issues.

Review Aspects:
{aspects_desc}

{'\n\n'.join(files_content)}

Provide your analysis in JSON format with the following structure:
{{
  "findings": [
    {{
      "file": "<relative_filepath>",
      "line": <line_number or null>,
      "severity": "<critical|high|medium|low|info>",
      "category": "<security|performance|maintainability|style|documentation>",
      "issue": "<brief description of the issue>",
      "suggestion": "<actionable suggestion to fix>",
      "confidence": <0.0-1.0>
    }}
  ]
}}

For each finding, ensure the "file" field accurately reflects the relative path of the file it pertains to.
Focus on actionable findings. If the code is good, return an empty findings array.
Output ONLY valid JSON, no additional text."""

        return prompt

    def _parse_llm_response(
        self,
        response: str,
    ) -> List[AIReviewFinding]:
        """Parse LLM response into structured findings from a batched response."""
        findings = []

        try:
            # Try to extract JSON from response
            response = response.strip()

            # Remove markdown code blocks if present
            if response.startswith("```"):
                lines = response.split("\n")
                response = "\n".join(lines[1:-1]) if len(lines) > 2 else response
                response = response.replace("```json", "").replace("```", "").strip()

            data = json.loads(response)

            for finding_data in data.get("findings", []):
                # The 'file' field should now be present in the finding_data from the LLM
                file_path_str = finding_data.get("file", "unknown_file")
                finding = AIReviewFinding(
                    file=file_path_str,
                    line=finding_data.get("line"),
                    severity=finding_data.get("severity", "info"),
                    category=finding_data.get("category", "maintainability"),
                    issue=finding_data.get("issue", ""),
                    suggestion=finding_data.get("suggestion", ""),
                    confidence=finding_data.get("confidence", 0.5),
                )
                findings.append(finding)
        except json.JSONDecodeError as e:
            # If JSON parsing fails, create a generic finding
            print(f"Warning: Failed to parse LLM response as JSON: {e}")
            print(f"Response was: {response[:200]}")
        except Exception as e:
            print(f"Warning: Error parsing LLM response: {e}")

        return findings



    def _review_batch(
        self,
        batch: List[Dict],
        aspects: List[str],
        root_dir: Path,
    ) -> Tuple[bool, List[AIReviewFinding]]:
        """Review a batch of files using AI with caching support."""
        if not batch:
            return True, []

        # Check cache for each file in batch
        cached_findings = []
        files_to_review = []
        
        if self.enable_cache and self.cache:
            for item in batch:
                filepath = item["filepath"]
                content = item["content"]
                cache_key = self.cache.get_cache_key(filepath, content)
                
                cached = self.cache.get(cache_key)
                if cached:
                    print(f"  ✓ Cache hit: {filepath.name}")
                    cached_findings.extend(cached)
                else:
                    files_to_review.append(item)
        else:
            files_to_review = batch

        # If all files were cached, return cached results
        if not files_to_review:
            self.findings.extend(cached_findings)
            return True, cached_findings

        # Review uncached files
        prompt = self._build_batched_review_prompt(files_to_review, aspects, root_dir)
        success, response = self._call_llm(prompt)

        if not success:
            print(f"LLM call failed for batch: {response}")
            return False, cached_findings

        # Parse findings for the batch
        batch_findings = self._parse_llm_response(response)
        
        # Cache findings for each file
        if self.enable_cache and self.cache:
            for item in files_to_review:
                filepath = item["filepath"]
                content = item["content"]
                cache_key = self.cache.get_cache_key(filepath, content)
                
                # Extract findings for this specific file
                file_findings = [f for f in batch_findings if f.file == str(filepath.relative_to(root_dir))]
                self.cache.set(cache_key, file_findings)
        
        # Combine cached and new findings
        all_findings = cached_findings + batch_findings
        self.findings.extend(all_findings)

        return True, all_findings

    def review_file(self, filepath: Path, aspects: List[str], root_dir: Path) -> List[AIReviewFinding]:
        """Review a single file using AI with caching support."""
        try:
                print(f"Reviewing {filepath.name} (Language: {self.language_detector.detect(filepath)})")
                code = filepath.read_text()
                if len(code) > 10000: # Skip very large files (>10KB)
                print(f"Skipping {filepath}: File too large for AI review")
                return []
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return []

        item = {"filepath": filepath, "content": content}
        success, findings = self._review_batch([item], aspects, root_dir)
        if not success:
            return []
        return findings

    def review_directory(
        self,
        root_dir: Path,
        patterns: List[str] = None,
        aspects: List[str] = None,
        max_files: int = 10,
        incremental: bool = False,
        git_base: Optional[str] = None,
        include_untracked: bool = False,
        parallel: bool = True,
        max_workers: int = 4,
    ) -> Tuple[bool, str, str]:
        """Review multiple files in a directory

        Args:
            root_dir: Root directory to scan
            patterns: File patterns to include (e.g., ["*.py"])
            aspects: Review aspects to focus on
            max_files: Maximum number of files to review
            incremental: If True, only review changed files using git diff
            git_base: Base branch/commit for git diff (e.g., 'main', 'HEAD~1')
            include_untracked: Include untracked files in git diff mode
            parallel: If True, review files in parallel
            max_workers: Maximum number of parallel workers

        Returns:
            Tuple of (success, stdout, stderr)

        """
        if patterns is None:
            patterns = ["*.py"]  # Default to Python files

        if aspects is None:
            aspects = ["security", "performance", "maintainability"]

        # Find files to review
        if incremental:
            # Use git diff to find changed files
            git_helper = GitDiffHelper(root_dir)
            
            if not git_helper.is_git_repo():
                return False, "", "Incremental mode requires a git repository"
            
            # Auto-detect base branch if not provided
            if git_base is None:
                success, default_branch, error = git_helper.get_default_branch()
                if success:
                    git_base = default_branch
                    print(f"Auto-detected base branch: {git_base}")
                else:
                    print(f"Warning: Could not detect default branch, using HEAD")
                    git_base = None
            
            success, files_to_review, error = git_helper.get_changed_files(
                base=git_base,
                include_untracked=include_untracked,
                file_patterns=patterns,
            )
            
            if not success:
                return False, "", f"Failed to get changed files: {error}"
            
            print(f"Incremental mode: Found {len(files_to_review)} changed files")
        else:
            # Full directory scan (original behavior)
            files_to_review = []
            for pattern in patterns:
                files_to_review.extend(root_dir.rglob(pattern))

            # Filter out test files, migrations, and virtual environments
            files_to_review = [
                f
                for f in files_to_review
                if not any(
                    part in f.parts
                    for part in [
                        ".venv",
                        "__pycache__",
                        "node_modules",
                        "migrations",
                        ".git",
                    ]
                )
            ]

        # Limit number of files
        files_to_review = files_to_review[:max_files]

        if not files_to_review:
            mode = "incremental" if incremental else "full"
            return True, f"No files found to review ({mode} mode)", ""

        print(f"\n--- AI Code Review ({self.provider}) ---")
        print(
            f"Reviewing {len(files_to_review)} files with aspects: {', '.join(aspects)}",
        )

        overall_success = True
        
        if parallel:
            from .parallel_reviewer import ParallelReviewer
            parallel_reviewer = ParallelReviewer(max_workers=max_workers)
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_file = {
                    executor.submit(self.review_file, filepath, aspects, root_dir): filepath
                    for filepath in files_to_review
                }
                
                for future in as_completed(future_to_file):
                    filepath = future_to_file[future]
                    try:
                        findings = future.result()
                        self.findings.extend(findings)
                        print(f"✓ Reviewed {filepath.name}")
                    except Exception as e:
                        print(f"✗ Failed to review {filepath.name}: {e}")
                        overall_success = False
        else:
            for filepath in files_to_review:
                findings = self.review_file(filepath, aspects, root_dir)
                self.findings.extend(findings)

        # Generate summary
        stdout = f"AI Review Complete: Reviewed {len(files_to_review)} files\n"
        stdout += f"Total findings: {len(self.findings)}\n"

        if self.findings:
            by_severity = {}
            for finding in self.findings:
                by_severity[finding.severity] = by_severity.get(finding.severity, 0) + 1

            stdout += "Findings by severity:\n"
            for severity in ["critical", "high", "medium", "low", "info"]:
                if severity in by_severity:
                    stdout += f"  {severity}: {by_severity[severity]}\n"

        stderr = "" if overall_success else "Some files failed to review"

        # Print cache statistics
        if self.enable_cache and self.cache:
            self.cache.print_stats()

        # Record review outcome with ImprovementManager
        if self.improvement_manager:
            review_outcome = self.get_review_summary()
            review_outcome["status"] = "success" if overall_success else "failure"
            self.improvement_manager.record_review(review_outcome)

        # Record metrics
        self.metrics_collector.record_review({
            "status": "success" if overall_success else "failure",
            "files_reviewed": len(files_to_review),
            "findings_count": len(self.findings),
            "api_calls": self.cache.get_stats()["total_requests"] if self.cache else 0, # Assuming each cache miss is an API call
            "cost_estimate": self.cache.get_stats()["saved_api_calls"] * 0.001 if self.cache else 0, # Placeholder cost
            "severity_breakdown": {severity: count for severity, count in self.get_review_summary()["findings_by_severity"].items()},
        })

        return overall_success, stdout, stderr

    def get_findings(self) -> List[AIReviewFinding]:
        """Get all findings from the review"""
        return self.findings

    def export_findings(self, output_path: Path):
        """Export findings to JSON file"""
        findings_data = [asdict(f) for f in self.findings]
        output_path.write_text(json.dumps(findings_data, indent=2))

    def get_review_summary(self) -> Dict:
        """Generate a summary of the AI review findings."""
        summary = {
            "total_findings": len(self.findings),
            "findings_by_severity": {},
            "findings_by_category": {},
        }

        for finding in self.findings:
            summary["findings_by_severity"][finding.severity] = (
                summary["findings_by_severity"].get(finding.severity, 0) + 1
            )
            summary["findings_by_category"][finding.category] = (
                summary["findings_by_category"].get(finding.category, 0) + 1
            )
        return summary


def run_ai_review(
    root_dir: Path,
    provider: str = "gemini_api",
    aspects: List[str] = None,
    max_files: int = 10,
    improvement_manager: Optional[ImprovementManager] = None,
) -> Tuple[bool, str, str]:
    """Main entry point for AI code review

    Args:
        root_dir: Root directory to review
        provider: LLM provider to use
        aspects: Review aspects to focus on
        max_files: Maximum number of files to review

    Returns:
        Tuple of (success, stdout, stderr)

    """
    reviewer = AICodeReviewer(provider=provider, improvement_manager=improvement_manager)
    return reviewer.review_directory(root_dir, aspects=aspects, max_files=max_files)


if __name__ == "__main__":
    # Test the AI reviewer
    import sys

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    # Instantiate ImprovementManager for the main block example
    im = ImprovementManager()
    reviewer = AICodeReviewer(provider="gemini_api", improvement_manager=im)
    success, stdout, stderr = reviewer.review_directory(root, max_files=3)

    print("\n" + stdout)
    if stderr:
        print("Errors:", stderr)

    # Export findings
    if reviewer.findings:
        output_file = root / "ai_review_findings.json"
        reviewer.export_findings(output_file)
        print(f"\nFindings exported to: {output_file}")
