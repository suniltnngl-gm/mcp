#!/usr/bin/env python3
import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.log_analyzer import LogAnalyzer

def main():
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
        print("Usage: python scripts/analyze_logs.py analyze [log_file]")


if __name__ == "__main__":
    main()
