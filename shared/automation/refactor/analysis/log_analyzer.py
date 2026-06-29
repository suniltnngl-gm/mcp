#!/usr/bin/env python3
"""Lightweight Log Analysis without numpy dependency"""
import json
import os
from datetime import datetime
from pathlib import Path
import requests
from typing import List, Dict


class LogAnalyzer:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.kb_dir = Path("config/knowledge_base")
        self.logs_dir = Path("logs")

    def chunk_logs(self, log_text: str, chunk_size: int = 1500) -> List[str]:
        """Split logs into chunks"""
        lines = log_text.split("\n")
        chunks = []
        current_chunk = []
        current_size = 0

        for line in lines:
            if current_size + len(line) > chunk_size and current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = [line]
                current_size = len(line)
            else:
                current_chunk.append(line)
                current_size += len(line)

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    def analyze_with_llm(self, log_chunks: List[str]) -> Dict:
        """LLM analysis with structured output"""
        # Take most relevant chunks (first few + any with ERROR/WARN)
        priority_chunks = []
        error_chunks = []

        for chunk in log_chunks:
            if any(
                keyword in chunk.upper()
                for keyword in ["ERROR", "FAIL", "EXCEPTION", "WARN"]
            ):
                error_chunks.append(chunk)
            else:
                priority_chunks.append(chunk)

        # Combine priority chunks (errors first)
        selected_chunks = (error_chunks + priority_chunks)[:3]
        context = "\n---\n".join(selected_chunks)

        prompt = f"""Analyze these log entries and provide JSON response:

LOGS:
{context}

Provide JSON with:
{{
  "summary": "1-sentence summary of main issues",
  "severity": "low|medium|high|critical",
  "issues_found": ["issue1", "issue2"],
  "next_steps": ["step1", "step2", "step3"],
  "code_suggestions": [{{"file": "path", "fix": "solution"}}]
}}"""

        if self.openai_key:
            return self._openai_analysis(prompt)
        else:
            return self._fallback_analysis(selected_chunks)

    def _openai_analysis(self, prompt: str) -> Dict:
        """OpenAI analysis"""
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_key}"},
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                },
                timeout=30,
            )

            if response.status_code == 200:
                return json.loads(response.json()["choices"][0]["message"]["content"])
        except Exception:
            pass

        return {"error": "OpenAI API failed"}

    def _fallback_analysis(self, chunks: List[str]) -> Dict:
        """Simple pattern-based analysis when no API"""
        issues = []
        severity = "low"

        for chunk in chunks:
            if "ERROR" in chunk.upper():
                issues.append("Error detected in logs")
                severity = "high"
            elif "FAIL" in chunk.upper():
                issues.append("Failure detected")
                severity = "medium"
            elif "WARN" in chunk.upper():
                issues.append("Warning found")
                if severity == "low":
                    severity = "medium"

        if not issues:
            issues = ["No critical issues detected"]

        return {
            "summary": f"Found {len(issues)} issues in log analysis",
            "severity": severity,
            "issues_found": issues,
            "next_steps": [
                "Review detailed logs",
                "Check system status",
                "Monitor for patterns",
            ],
            "code_suggestions": [],
        }

    def analyze_logs(self, log_file: str = None) -> Dict:
        """Main analysis pipeline"""
        # Load logs
        if log_file:
            log_path = Path(log_file)
        else:
            log_path = self.logs_dir / "system.log"

        if not log_path.exists():
            return {"error": f"Log file not found: {log_path}"}

        try:
            with open(log_path) as f:
                log_text = f.read()
        except Exception:
            return {"error": f"Cannot read log file: {log_path}"}

        if not log_text.strip():
            return {"error": "Log file is empty"}

        # Process
        chunks = self.chunk_logs(log_text)
        analysis = self.analyze_with_llm(chunks)

        # Save results
        results = {
            "timestamp": datetime.now().isoformat(),
            "log_file": str(log_path),
            "chunks_processed": len(chunks),
            "analysis": analysis,
        }

        self.kb_dir.mkdir(exist_ok=True)
        try:
            with open(self.kb_dir / "log_analysis_results.json", "w") as f:
                json.dump(results, f, indent=2)
        except Exception:
            pass

        return results


def main():
    import sys

    analyzer = LogAnalyzer()

    if len(sys.argv) > 1 and sys.argv[1] == "analyze":
        log_file = sys.argv[2] if len(sys.argv) > 2 else None

        results = analyzer.analyze_logs(log_file)

        if "error" in results:
            print(f"❌ {results['error']}")
            return

        analysis = results["analysis"]
        print("🔍 LOG ANALYSIS")
        print("=" * 30)
        print(f"📄 File: {results['log_file']}")
        print(f"📊 Chunks: {results['chunks_processed']}")
        print()

        if "summary" in analysis:
            print(f"📝 {analysis['summary']}")
        if "severity" in analysis:
            print(f"⚠️  Severity: {analysis['severity'].upper()}")

        if "issues_found" in analysis:
            print("\n🎯 Issues:")
            for issue in analysis["issues_found"]:
                print(f"  • {issue}")

        if "next_steps" in analysis:
            print("\n🚀 Next Steps:")
            for i, step in enumerate(analysis["next_steps"], 1):
                print(f"  {i}. {step}")
    else:
        print("Usage: python intelligent_log_analyzer_lite.py analyze [log_file]")


if __name__ == "__main__":
    main()
