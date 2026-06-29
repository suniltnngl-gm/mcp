#!/usr/bin/env python3
"""
Week 2: Performance Baseline Creator
===================================
"""

import json
import statistics
import time
from datetime import datetime
from pathlib import Path

# Try to import project modules
try:
    from ai_load_balancer import AdvancedLoadBalancer
    from ai_provider_manager import SmartProviderRouter

    AI_MODULES_AVAILABLE = True
except ImportError:
    AI_MODULES_AVAILABLE = False
    print("⚠️ AI Orchestra modules not available - using mock data")


def create_performance_baseline():
    """Create comprehensive performance baseline"""

    baseline_data = {
        "timestamp": datetime.now().isoformat(),
        "system_info": {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform,
        },
        "test_scenarios": [],
        "summary_metrics": {},
    }

    if not AI_MODULES_AVAILABLE:
        # Create mock baseline for testing
        baseline_data["mock_data"] = True
        baseline_data["summary_metrics"] = {
            "avg_response_time": 2.5,
            "p95_response_time": 4.2,
            "success_rate": 0.75,
            "total_tests": 10,
        }
    else:
        # Real performance testing
        test_prompts = [
            "What is machine learning?",
            "Explain neural networks in simple terms.",
            "How does artificial intelligence work?",
            "Describe cloud computing benefits.",
            "What are software engineering principles?",
            "Explain database normalization.",
            "Compare REST vs GraphQL APIs.",
            "How does version control work?",
            "Describe microservices architecture.",
            "What are design patterns in programming?",
        ]

        router = SmartProviderRouter()
        response_times = []
        success_count = 0

        for i, prompt in enumerate(test_prompts):
            start_time = time.time()
            try:
                response = router.generate(prompt, strategy="balanced")
                response_time = time.time() - start_time
                response_times.append(response_time)

                success = not response.startswith("❌")
                if success:
                    success_count += 1

                scenario = {
                    "test_id": i + 1,
                    "prompt": prompt[:50] + "...",
                    "response_time": response_time,
                    "success": success,
                    "response_length": len(response),
                }
                baseline_data["test_scenarios"].append(scenario)

                print(
                    f"Test {i+1}/10: {'✅' if success else '❌'} {response_time:.2f}s"
                )

            except Exception as e:
                scenario = {
                    "test_id": i + 1,
                    "prompt": prompt[:50] + "...",
                    "error": str(e),
                    "success": False,
                }
                baseline_data["test_scenarios"].append(scenario)
                print(f"Test {i+1}/10: ❌ Error - {e}")

        # Calculate summary metrics
        if response_times:
            baseline_data["summary_metrics"] = {
                "avg_response_time": statistics.mean(response_times),
                "median_response_time": statistics.median(response_times),
                "p95_response_time": (
                    statistics.quantiles(response_times, n=20)[18]
                    if len(response_times) > 5
                    else max(response_times)
                ),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "success_rate": success_count / len(test_prompts),
                "total_tests": len(test_prompts),
                "successful_tests": success_count,
            }

    # Save baseline
    Path("benchmarks/baseline").mkdir(parents=True, exist_ok=True)
    with open(
        f"benchmarks/baseline/performance_baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        "w",
    ) as f:
        json.dump(baseline_data, f, indent=2)

    # Save as current baseline
    with open("benchmarks/baseline/current_baseline.json", "w") as f:
        json.dump(baseline_data, f, indent=2)

    print("\n🎯 Performance Baseline Created!")
    if "summary_metrics" in baseline_data:
        metrics = baseline_data["summary_metrics"]
        print(f"Average Response Time: {metrics.get('avg_response_time', 'N/A'):.2f}s")
        print(f"Success Rate: {metrics.get('success_rate', 'N/A'):.1%}")

    return baseline_data


if __name__ == "__main__":
    import sys

    create_performance_baseline()
