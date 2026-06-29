#!/usr/bin/env python3
"""Enhanced AI Registry - Batch processing, caching, and automation integration"""

import json
import asyncio
import hashlib
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Import existing systems
try:
    from smart_ai_router import SmartAIRouter
    from ai_task_classifier import AITaskClassifier
    from enhanced_health_monitor import EnhancedHealthMonitor
    from ai_action_tracker import AIActionTracker
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

@dataclass
class FileAnalysis:
    """AI analysis result for a file"""
    file_path: str
    file_hash: str
    analysis_timestamp: str
    description: str
    tags: List[str]
    complexity: str
    category: str
    quality_score: float
    improvements: List[str]
    provider_used: str
    analysis_cost: float
    processing_time: float

@dataclass
class BatchJob:
    """Batch processing job"""
    job_id: str
    created_at: str
    status: str  # pending, running, completed, failed
    total_files: int
    processed_files: int
    failed_files: int
    total_cost: float
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error_log: List[str] = None
    
    def __post_init__(self):
        if self.error_log is None:
            self.error_log = []

class EnhancedAIRegistry:
    """Enhanced AI registry with batch processing and caching"""
    
    def __init__(self, registry_dir: str = "ai_registry_data", max_workers: int = 4):
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(exist_ok=True)
        
        # Storage files
        self.analysis_cache_file = self.registry_dir / "analysis_cache.json"
        self.batch_jobs_file = self.registry_dir / "batch_jobs.json"
        self.config_file = self.registry_dir / "config.json"
        
        # Configuration
        self.max_workers = max_workers
        self.cache_ttl_hours = 24  # Cache validity period
        
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Required dependencies not available")
        
        # Initialize AI systems
        self.ai_router = SmartAIRouter()
        self.task_classifier = AITaskClassifier()
        self.health_monitor = EnhancedHealthMonitor()
        self.action_tracker = AIActionTracker()
        
        # Load existing data
        self.analysis_cache = self._load_analysis_cache()
        self.batch_jobs = self._load_batch_jobs()
        self.config = self._load_config()
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.progress_lock = threading.Lock()
    
    def _load_analysis_cache(self) -> Dict[str, FileAnalysis]:
        """Load analysis cache from storage"""
        if self.analysis_cache_file.exists():
            with open(self.analysis_cache_file) as f:
                data = json.load(f)
                return {k: FileAnalysis(**v) for k, v in data.items()}
        return {}
    
    def _save_analysis_cache(self):
        """Save analysis cache to storage"""
        with open(self.analysis_cache_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.analysis_cache.items()}, f, indent=2)
    
    def _load_batch_jobs(self) -> Dict[str, BatchJob]:
        """Load batch jobs from storage"""
        if self.batch_jobs_file.exists():
            with open(self.batch_jobs_file) as f:
                data = json.load(f)
                return {k: BatchJob(**v) for k, v in data.items()}
        return {}
    
    def _save_batch_jobs(self):
        """Save batch jobs to storage"""
        with open(self.batch_jobs_file, 'w') as f:
            json.dump({k: asdict(v) for k, v in self.batch_jobs.items()}, f, indent=2)
    
    def _load_config(self) -> Dict:
        """Load configuration"""
        default_config = {
            "auto_analysis_enabled": False,
            "file_extensions": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".go", ".rs"],
            "exclude_patterns": ["__pycache__", ".git", "node_modules", ".venv", "dist", "build"],
            "max_file_size_mb": 1,
            "batch_size": 10,
            "cron_schedule": "0 2 * * *"  # Daily at 2 AM
        }
        
        if self.config_file.exists():
            with open(self.config_file) as f:
                config = json.load(f)
                default_config.update(config)
        
        return default_config
    
    def _save_config(self):
        """Save configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get file content hash for caching"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            return hashlib.md5(content.encode()).hexdigest()
        except Exception:
            return hashlib.md5(str(file_path.stat().st_mtime).encode()).hexdigest()
    
    def _is_cache_valid(self, analysis: FileAnalysis) -> bool:
        """Check if cached analysis is still valid"""
        analysis_time = datetime.fromisoformat(analysis.analysis_timestamp)
        return datetime.now() - analysis_time < timedelta(hours=self.cache_ttl_hours)
    
    def _should_analyze_file(self, file_path: Path) -> bool:
        """Check if file should be analyzed"""
        # Check extension
        if file_path.suffix not in self.config["file_extensions"]:
            return False
        
        # Check size
        try:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            if size_mb > self.config["max_file_size_mb"]:
                return False
        except Exception:
            return False
        
        # Check exclude patterns
        for pattern in self.config["exclude_patterns"]:
            if pattern in str(file_path):
                return False
        
        return True
    
    def analyze_file(self, file_path: Path, force_refresh: bool = False) -> Optional[FileAnalysis]:
        """Analyze a single file with AI"""
        if not self._should_analyze_file(file_path):
            return None
        
        file_hash = self._get_file_hash(file_path)
        cache_key = f"{file_path}_{file_hash}"
        
        # Check cache
        if not force_refresh and cache_key in self.analysis_cache:
            cached = self.analysis_cache[cache_key]
            if self._is_cache_valid(cached):
                return cached
        
        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            content_preview = content[:2000]  # First 2KB for analysis
            
            # Build analysis prompt
            analysis_prompt = self._build_analysis_prompt(file_path, content_preview)
            
            # Classify the analysis task
            classification = self.task_classifier.classify_task(
                analysis_prompt, f"file_analysis_{file_path.name}"
            )
            
            start_time = time.time()
            
            # Generate AI analysis (mock implementation)
            analysis_result = self._generate_file_analysis(
                file_path, content_preview, classification.recommended_provider
            )
            
            processing_time = time.time() - start_time
            
            # Create analysis record
            analysis = FileAnalysis(
                file_path=str(file_path),
                file_hash=file_hash,
                analysis_timestamp=datetime.now().isoformat(),
                description=analysis_result["description"],
                tags=analysis_result["tags"],
                complexity=classification.complexity,
                category=classification.category,
                quality_score=analysis_result["quality_score"],
                improvements=analysis_result["improvements"],
                provider_used=classification.recommended_provider,
                analysis_cost=classification.estimated_cost,
                processing_time=processing_time
            )
            
            # Cache the result
            self.analysis_cache[cache_key] = analysis
            
            # Track the action
            self.action_tracker.log_action(
                action_type="file_analysis",
                provider=classification.recommended_provider,
                model=classification.recommended_provider,
                input_tokens=len(analysis_prompt),
                output_tokens=len(str(analysis_result)),
                cost=classification.estimated_cost,
                latency=processing_time,
                success=True,
                context={
                    "file_path": str(file_path),
                    "file_size": len(content),
                    "complexity": classification.complexity
                },
                result=f"Analyzed {file_path.name}"
            )
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None
    
    def _build_analysis_prompt(self, file_path: Path, content_preview: str) -> str:
        """Build analysis prompt for AI"""
        return f"""Analyze this code file and provide structured analysis:

File: {file_path.name}
Extension: {file_path.suffix}
Content preview (first 2KB):
{content_preview}

Provide analysis in the following areas:
1. Description: One-sentence summary of what this file does
2. Tags: 3-5 relevant tags (e.g., core, api, util, config, test, deprecated)
3. Quality assessment: Rate code quality 1-10
4. Improvements: List specific improvement suggestions

Focus on code structure, patterns, and maintainability."""
    
    def _generate_file_analysis(self, file_path: Path, content: str, provider: str) -> Dict:
        """Generate AI analysis for file (mock implementation)"""
        # This would integrate with actual AI providers
        # For now, return structured mock analysis based on file characteristics
        
        file_ext = file_path.suffix.lower()
        file_name = file_path.name.lower()
        
        # Basic analysis based on file characteristics
        if "test" in file_name or "spec" in file_name:
            description = f"Test file for {file_path.stem}"
            tags = ["test", "validation", "quality"]
            quality_score = 7.5
            improvements = ["Add more edge case tests", "Improve test documentation"]
        elif file_ext == ".py":
            if "main" in file_name or "__main__" in content:
                description = f"Main entry point module"
                tags = ["core", "entry-point", "main"]
                quality_score = 8.0
                improvements = ["Add command-line argument parsing", "Improve error handling"]
            elif "config" in file_name:
                description = f"Configuration module"
                tags = ["config", "settings", "util"]
                quality_score = 7.0
                improvements = ["Add configuration validation", "Support environment variables"]
            else:
                description = f"Python module: {file_path.stem}"
                tags = ["module", "python", "core"]
                quality_score = 7.5
                improvements = ["Add type hints", "Improve documentation"]
        elif file_ext in [".js", ".ts"]:
            description = f"JavaScript/TypeScript module"
            tags = ["frontend", "javascript", "module"]
            quality_score = 7.0
            improvements = ["Add TypeScript types", "Improve error handling"]
        else:
            description = f"Source file: {file_path.name}"
            tags = ["source", "code"]
            quality_score = 6.5
            improvements = ["Review code structure", "Add documentation"]
        
        return {
            "description": description,
            "tags": tags,
            "quality_score": quality_score,
            "improvements": improvements,
            "_generated_by": provider
        }
    
    def create_batch_job(self, file_paths: List[Path], job_id: str = None) -> str:
        """Create a batch processing job"""
        if not job_id:
            job_id = f"batch_{int(time.time())}"
        
        # Filter files that should be analyzed
        valid_files = [f for f in file_paths if self._should_analyze_file(f)]
        
        job = BatchJob(
            job_id=job_id,
            created_at=datetime.now().isoformat(),
            status="pending",
            total_files=len(valid_files),
            processed_files=0,
            failed_files=0,
            total_cost=0.0
        )
        
        self.batch_jobs[job_id] = job
        self._save_batch_jobs()
        
        return job_id
    
    def process_batch_job(self, job_id: str, progress_callback=None) -> Dict:
        """Process a batch job with parallel execution"""
        if job_id not in self.batch_jobs:
            return {"error": f"Job {job_id} not found"}
        
        job = self.batch_jobs[job_id]
        if job.status != "pending":
            return {"error": f"Job {job_id} is not pending"}
        
        # Get file list (reconstruct from job - in real implementation, store file list)
        # For now, scan workspace for files
        workspace_root = Path("/media/sunil-kr/workspace/user-projects")
        file_paths = []
        
        for ext in self.config["file_extensions"]:
            file_paths.extend(workspace_root.rglob(f"*{ext}"))
        
        valid_files = [f for f in file_paths if self._should_analyze_file(f)][:job.total_files]
        
        # Update job status
        job.status = "running"
        job.start_time = datetime.now().isoformat()
        self._save_batch_jobs()
        
        # Process files in parallel
        futures = []
        for file_path in valid_files:
            future = self.executor.submit(self._process_file_for_batch, file_path, job_id)
            futures.append(future)
        
        # Collect results
        for future in as_completed(futures):
            try:
                result = future.result()
                with self.progress_lock:
                    if result["success"]:
                        job.processed_files += 1
                        job.total_cost += result.get("cost", 0)
                    else:
                        job.failed_files += 1
                        job.error_log.append(result.get("error", "Unknown error"))
                    
                    # Update progress
                    if progress_callback:
                        progress_callback(job.processed_files + job.failed_files, job.total_files)
                    
                    # Save progress periodically
                    if (job.processed_files + job.failed_files) % 5 == 0:
                        self._save_batch_jobs()
                        self._save_analysis_cache()
            
            except Exception as e:
                with self.progress_lock:
                    job.failed_files += 1
                    job.error_log.append(str(e))
        
        # Finalize job
        job.status = "completed" if job.failed_files == 0 else "completed_with_errors"
        job.end_time = datetime.now().isoformat()
        
        self._save_batch_jobs()
        self._save_analysis_cache()
        
        return {
            "job_id": job_id,
            "status": job.status,
            "processed": job.processed_files,
            "failed": job.failed_files,
            "total_cost": job.total_cost,
            "duration": self._calculate_duration(job.start_time, job.end_time)
        }
    
    def _process_file_for_batch(self, file_path: Path, job_id: str) -> Dict:
        """Process a single file for batch job"""
        try:
            analysis = self.analyze_file(file_path)
            if analysis:
                return {
                    "success": True,
                    "file": str(file_path),
                    "cost": analysis.analysis_cost
                }
            else:
                return {
                    "success": False,
                    "file": str(file_path),
                    "error": "File skipped or analysis failed"
                }
        except Exception as e:
            return {
                "success": False,
                "file": str(file_path),
                "error": str(e)
            }
    
    def _calculate_duration(self, start_time: str, end_time: str) -> float:
        """Calculate duration between timestamps"""
        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            return (end - start).total_seconds()
        except Exception:
            return 0.0
    
    def get_batch_status(self, job_id: str) -> Dict:
        """Get status of a batch job"""
        if job_id not in self.batch_jobs:
            return {"error": f"Job {job_id} not found"}
        
        job = self.batch_jobs[job_id]
        return asdict(job)
    
    def get_analysis_summary(self) -> Dict:
        """Get summary of all analyses"""
        if not self.analysis_cache:
            return {"total_files": 0, "message": "No analyses available"}
        
        total_files = len(self.analysis_cache)
        total_cost = sum(a.analysis_cost for a in self.analysis_cache.values())
        avg_quality = sum(a.quality_score for a in self.analysis_cache.values()) / total_files
        
        # Tag distribution
        all_tags = []
        for analysis in self.analysis_cache.values():
            all_tags.extend(analysis.tags)
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Complexity distribution
        complexity_counts = {}
        for analysis in self.analysis_cache.values():
            complexity_counts[analysis.complexity] = complexity_counts.get(analysis.complexity, 0) + 1
        
        return {
            "total_files": total_files,
            "total_cost": total_cost,
            "average_quality_score": avg_quality,
            "tag_distribution": dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "complexity_distribution": complexity_counts,
            "cache_size_mb": self.analysis_cache_file.stat().st_size / (1024*1024) if self.analysis_cache_file.exists() else 0
        }
    
    def setup_cron_automation(self) -> str:
        """Generate cron job setup script"""
        script_path = self.registry_dir / "auto_analysis.sh"
        
        script_content = f"""#!/bin/bash
# Auto-generated AI registry cron script
cd {Path(__file__).parent}
python3 enhanced_ai_registry.py auto-scan
"""
        
        script_path.write_text(script_content)
        script_path.chmod(0o755)
        
        cron_entry = f"{self.config['cron_schedule']} {script_path}"
        
        return f"Add this to crontab: {cron_entry}"

def main():
    """CLI interface for enhanced AI registry"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_ai_registry.py <command> [args...]")
        print("Commands:")
        print("  analyze <file_path> - Analyze single file")
        print("  batch <directory> - Create batch job for directory")
        print("  status <job_id> - Check batch job status")
        print("  summary - Show analysis summary")
        print("  auto-scan - Automated scan (for cron)")
        print("  setup-cron - Generate cron setup")
        return
    
    if not DEPENDENCIES_AVAILABLE:
        print("Error: Required dependencies not available")
        return
    
    registry = EnhancedAIRegistry()
    command = sys.argv[1]
    
    if command == "analyze":
        if len(sys.argv) < 3:
            print("Usage: analyze <file_path>")
            return
        
        file_path = Path(sys.argv[2])
        analysis = registry.analyze_file(file_path)
        if analysis:
            print(json.dumps(asdict(analysis), indent=2))
        else:
            print("File analysis failed or skipped")
    
    elif command == "batch":
        if len(sys.argv) < 3:
            print("Usage: batch <directory>")
            return
        
        directory = Path(sys.argv[2])
        if not directory.exists():
            print(f"Directory not found: {directory}")
            return
        
        # Collect files
        file_paths = []
        for ext in registry.config["file_extensions"]:
            file_paths.extend(directory.rglob(f"*{ext}"))
        
        job_id = registry.create_batch_job(file_paths)
        print(f"Created batch job: {job_id}")
        
        # Process with progress
        def progress_callback(processed, total):
            print(f"Progress: {processed}/{total} ({processed/total*100:.1f}%)")
        
        result = registry.process_batch_job(job_id, progress_callback)
        print(f"Batch job completed: {json.dumps(result, indent=2)}")
    
    elif command == "status":
        if len(sys.argv) < 3:
            print("Usage: status <job_id>")
            return
        
        job_id = sys.argv[2]
        status = registry.get_batch_status(job_id)
        print(json.dumps(status, indent=2))
    
    elif command == "summary":
        summary = registry.get_analysis_summary()
        print(json.dumps(summary, indent=2))
    
    elif command == "setup-cron":
        cron_info = registry.setup_cron_automation()
        print(cron_info)

if __name__ == "__main__":
    main()
