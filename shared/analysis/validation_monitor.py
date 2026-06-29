#!/usr/bin/env python3

import json
import os
from datetime import datetime
from pathlib import Path

def monitor_validation_activity():
    """Monitor real-time validation activity"""
    
    kb_dir = Path(__file__).parent.parent / "knowledge_base"
    
    # Check validation logs
    validation_stats = {
        "timestamp": datetime.now().isoformat(),
        "reality_checks_run": 0,
        "misunderstandings_detected": 0,
        "errors_learned": 0,
        "workflows_enhanced": 0
    }
    
    # Count enhanced workflows
    scripts_dir = Path(__file__).parent
    enhanced_count = 0
    
    for script in scripts_dir.glob("*.sh"):
        if script.name in ["cli.sh", "health_check.sh", "advanced_testing.sh", 
                          "production_readiness.sh", "ai_workflow.sh", 
                          "custom_development.sh", "analytics_insights.sh"]:
            try:
                content = script.read_text()
                if "validation_wrapper.sh" in content:
                    enhanced_count += 1
            except:
                pass
    
    validation_stats["workflows_enhanced"] = enhanced_count
    
    # Load recent activity from knowledge base
    try:
        if (kb_dir / "errors.json").exists():
            with open(kb_dir / "errors.json") as f:
                errors = json.load(f)
                validation_stats["errors_learned"] = len(errors)
    except:
        pass
    
    print(f"🔍 Validation Integration Status:")
    print(f"  ✓ Enhanced Workflows: {validation_stats['workflows_enhanced']}/7")
    print(f"  ✓ Errors in Knowledge Base: {validation_stats['errors_learned']}")
    print(f"  ✓ Integration Active: {'Yes' if enhanced_count > 0 else 'No'}")
    
    return validation_stats

if __name__ == "__main__":
    monitor_validation_activity()
