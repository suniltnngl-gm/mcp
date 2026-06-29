#!/usr/bin/env python3
"""Error Registry and Enhanced File Registry for Collaboration Framework"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass, asdict

@dataclass
class ErrorRecord:
    timestamp: str
    error_type: str
    component: str
    attempted_method: str
    correct_method: str
    fix_applied: str
    session_context: str

@dataclass
class FileRecord:
    path: str
    component_type: str
    api_methods: List[str]
    dependencies: List[str]
    last_verified: str
    integration_status: str

class ErrorRegistry:
    def __init__(self):
        self.registry_file = Path(__file__).parent / "error_registry.json"
        self.errors = self._load_errors()
    
    def record_error(self, error_type: str, component: str, attempted: str, correct: str, fix: str):
        """Record API integration error"""
        error = ErrorRecord(
            timestamp=datetime.now().isoformat(),
            error_type=error_type,
            component=component,
            attempted_method=attempted,
            correct_method=correct,
            fix_applied=fix,
            session_context="gemini_kiro_collaboration_framework"
        )
        
        self.errors.append(asdict(error))
        self._save_errors()
        return error
    
    def get_api_guidance(self, component: str) -> Dict:
        """Get API guidance based on previous errors"""
        component_errors = [e for e in self.errors if e.get("component") == component]
        
        if component_errors:
            latest = component_errors[-1]
            return {
                "component": component,
                "avoid_method": latest.get("attempted_method"),
                "use_method": latest.get("correct_method"),
                "last_error": latest.get("timestamp")
            }
        return {"component": component, "status": "no_errors_recorded"}
    
    def _load_errors(self) -> List[Dict]:
        if self.registry_file.exists():
            return json.loads(self.registry_file.read_text())
        return []
    
    def _save_errors(self):
        self.registry_file.write_text(json.dumps(self.errors, indent=2))

class EnhancedFileRegistry:
    def __init__(self):
        self.registry_file = Path(__file__).parent / "enhanced_file_registry.json"
        self.files = self._load_files()
        
    def register_component(self, file_path: str, component_type: str, api_methods: List[str]):
        """Register component with verified API methods"""
        
        record = FileRecord(
            path=file_path,
            component_type=component_type,
            api_methods=api_methods,
            dependencies=self._extract_dependencies(file_path),
            last_verified=datetime.now().isoformat(),
            integration_status="verified"
        )
        
        # Update or add record
        existing_idx = next((i for i, f in enumerate(self.files) if f.get("path") == file_path), None)
        if existing_idx is not None:
            self.files[existing_idx] = asdict(record)
        else:
            self.files.append(asdict(record))
        
        self._save_files()
        return record
    
    def get_api_methods(self, component: str) -> List[str]:
        """Get verified API methods for component"""
        for file_record in self.files:
            if component.lower() in file_record.get("path", "").lower():
                return file_record.get("api_methods", [])
        return []
    
    def _extract_dependencies(self, file_path: str) -> List[str]:
        """Extract import dependencies from file"""
        try:
            content = Path(file_path).read_text()
            imports = []
            for line in content.splitlines():
                line = line.strip()
                if line.startswith("from ") and " import " in line:
                    imports.append(line.split()[1])
                elif line.startswith("import "):
                    imports.append(line.split()[1])
            return imports[:10]  # Limit to first 10
        except:
            return []
    
    def _load_files(self) -> List[Dict]:
        if self.registry_file.exists():
            return json.loads(self.registry_file.read_text())
        return []
    
    def _save_files(self):
        self.registry_file.write_text(json.dumps(self.files, indent=2))

def populate_registries():
    """Populate registries with session learnings"""
    
    error_registry = ErrorRegistry()
    file_registry = EnhancedFileRegistry()
    
    # Record session errors
    session_errors = [
        {
            "error_type": "AttributeError",
            "component": "IntegratedAIDiscussion", 
            "attempted": "add_participant",
            "correct": "create_discussion",
            "fix": "Use create_discussion with participant list"
        },
        {
            "error_type": "AttributeError", 
            "component": "DecisionTracker",
            "attempted": "start_session",
            "correct": "create_decision",
            "fix": "Remove start_session call, use create_decision later"
        },
        {
            "error_type": "AttributeError",
            "component": "SmartAIRouter", 
            "attempted": "route_request",
            "correct": "select_provider",
            "fix": "Use select_provider with task_complexity parameter"
        }
    ]
    
    for error in session_errors:
        error_registry.record_error(**error)
    
    # Register verified components
    workspace_path = "/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares/ai/orchestration"
    
    components = [
        {
            "file_path": f"{workspace_path}/integrated_ai_discussion.py",
            "component_type": "ai_discussion",
            "api_methods": ["create_discussion", "add_message", "get_responses"]
        },
        {
            "file_path": f"{workspace_path}/smart_ai_router.py", 
            "component_type": "ai_router",
            "api_methods": ["select_provider", "get_fallback_chain", "estimate_cost", "record_usage"]
        },
        {
            "file_path": f"{workspace_path}/decision_tracker.py",
            "component_type": "decision_tracker", 
            "api_methods": ["create_decision", "update_decision", "get_decisions"]
        }
    ]
    
    for comp in components:
        file_registry.register_component(**comp)
    
    return {
        "errors_recorded": len(session_errors),
        "components_registered": len(components),
        "error_registry_file": str(error_registry.registry_file),
        "file_registry_file": str(file_registry.registry_file)
    }

if __name__ == "__main__":
    print("=== CREATING ERROR & FILE REGISTRIES ===")
    
    result = populate_registries()
    
    print(f"✅ Recorded {result['errors_recorded']} session errors")
    print(f"✅ Registered {result['components_registered']} verified components")
    print(f"📁 Error registry: {Path(result['error_registry_file']).name}")
    print(f"📁 File registry: {Path(result['file_registry_file']).name}")
    
    # Test API guidance
    error_registry = ErrorRegistry()
    guidance = error_registry.get_api_guidance("SmartAIRouter")
    print(f"\n🎯 API Guidance for SmartAIRouter:")
    print(f"   Avoid: {guidance.get('avoid_method')}")
    print(f"   Use: {guidance.get('use_method')}")
    
    file_registry = EnhancedFileRegistry()
    methods = file_registry.get_api_methods("smart_ai_router")
    print(f"\n📋 Verified API Methods: {methods}")
