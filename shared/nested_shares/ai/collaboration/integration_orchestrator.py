#!/usr/bin/env python3
"""Integration Orchestrator - Uses existing systems first, creates only when necessary"""

import json
from pathlib import Path
from datetime import datetime

class IntegrationOrchestrator:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects")
        self.system_map_file = Path(__file__).parent / "discovered_systems.json"
        self.integration_log = []
        
    def mandatory_system_discovery(self, task_description: str) -> dict:
        """MANDATORY: Check existing systems before any new development"""
        
        # Extract keywords from task
        keywords = self._extract_keywords(task_description)
        
        # Search existing systems
        existing_systems = self._search_existing_systems(keywords)
        
        discovery_result = {
            "task": task_description,
            "keywords": keywords,
            "existing_systems_found": existing_systems,
            "recommendation": self._generate_recommendation(existing_systems),
            "timestamp": datetime.now().isoformat()
        }
        
        self.integration_log.append(discovery_result)
        return discovery_result
    
    def _extract_keywords(self, task: str) -> list:
        """Extract relevant keywords from task description"""
        
        # Common task patterns and their keywords
        task_patterns = {
            "duplicate": ["duplicate", "dedup", "consolidat", "merge"],
            "ai": ["ai", "orchestrat", "llm", "model", "discuss"],
            "file": ["file", "registry", "track", "catalog", "index"],
            "automation": ["auto", "script", "tool", "util", "workflow"],
            "review": ["review", "analy", "check", "validate", "inspect"],
            "collaboration": ["collab", "discuss", "merge", "consensus"]
        }
        
        keywords = []
        task_lower = task.lower()
        
        for category, patterns in task_patterns.items():
            for pattern in patterns:
                if pattern in task_lower:
                    keywords.extend(patterns)
                    break
        
        return list(set(keywords))  # Remove duplicates
    
    def _search_existing_systems(self, keywords: list) -> dict:
        """Search for existing systems matching keywords"""
        
        if not self.system_map_file.exists():
            return {"error": "System map not found - run system_discovery_rebuilder.py first"}
        
        try:
            systems = json.loads(self.system_map_file.read_text())
        except:
            return {"error": "Could not load system map"}
        
        matches = {}
        
        for category, category_systems in systems.items():
            category_matches = []
            
            for system_type, files in category_systems.items():
                for file_info in files:
                    file_name = file_info.get("name", "").lower()
                    file_path = file_info.get("path", "").lower()
                    
                    # Check if any keyword matches
                    for keyword in keywords:
                        if keyword in file_name or keyword in file_path:
                            category_matches.append({
                                "name": file_info.get("name"),
                                "path": file_info.get("path"),
                                "type": system_type,
                                "matched_keyword": keyword
                            })
                            break
            
            if category_matches:
                matches[category] = category_matches
        
        return matches
    
    def _generate_recommendation(self, existing_systems: dict) -> dict:
        """Generate integration recommendation based on existing systems"""
        
        if not existing_systems or "error" in existing_systems:
            return {
                "action": "CREATE_NEW",
                "reason": "No existing systems found",
                "priority": "LOW"
            }
        
        total_matches = sum(len(matches) for matches in existing_systems.values())
        
        if total_matches >= 5:
            return {
                "action": "USE_EXISTING",
                "reason": f"Found {total_matches} existing systems - integration required",
                "priority": "CRITICAL",
                "integration_targets": list(existing_systems.keys())
            }
        elif total_matches >= 2:
            return {
                "action": "EXTEND_EXISTING", 
                "reason": f"Found {total_matches} related systems - extend instead of create",
                "priority": "HIGH",
                "extension_targets": list(existing_systems.keys())
            }
        else:
            return {
                "action": "CREATE_WITH_INTEGRATION",
                "reason": f"Found {total_matches} system(s) - create but integrate",
                "priority": "MEDIUM"
            }
    
    def execute_integration_task(self, task: str) -> dict:
        """Execute task using integration-first approach"""
        
        print(f"🔍 MANDATORY SYSTEM DISCOVERY: {task}")
        
        # Phase 1: Discovery (MANDATORY)
        discovery = self.mandatory_system_discovery(task)
        
        print(f"📊 Found {len(discovery['existing_systems_found'])} categories with existing systems")
        print(f"🎯 Recommendation: {discovery['recommendation']['action']}")
        
        # Phase 2: Integration Decision
        recommendation = discovery['recommendation']
        
        if recommendation['action'] == 'USE_EXISTING':
            return self._use_existing_systems(discovery)
        elif recommendation['action'] == 'EXTEND_EXISTING':
            return self._extend_existing_systems(discovery)
        else:
            return self._create_with_integration(discovery)
    
    def _use_existing_systems(self, discovery: dict) -> dict:
        """Use existing systems instead of creating new ones"""
        
        existing = discovery['existing_systems_found']
        
        # Prioritize by system maturity (more files = more mature)
        priority_systems = []
        
        for category, matches in existing.items():
            for match in matches[:2]:  # Top 2 per category
                priority_systems.append({
                    "category": category,
                    "system": match['name'],
                    "path": match['path'],
                    "action": f"USE {match['name']} instead of creating new"
                })
        
        return {
            "integration_type": "USE_EXISTING",
            "systems_to_use": priority_systems,
            "next_steps": [
                "Review existing system capabilities",
                "Integrate with existing APIs",
                "Extend functionality if needed",
                "Document integration approach"
            ]
        }
    
    def _extend_existing_systems(self, discovery: dict) -> dict:
        """Extend existing systems instead of creating new ones"""
        
        return {
            "integration_type": "EXTEND_EXISTING",
            "extension_plan": "Add functionality to existing systems",
            "next_steps": [
                "Analyze existing system architecture",
                "Identify extension points",
                "Implement extensions",
                "Test integration"
            ]
        }
    
    def _create_with_integration(self, discovery: dict) -> dict:
        """Create new system but integrate with existing ones"""
        
        return {
            "integration_type": "CREATE_WITH_INTEGRATION",
            "integration_plan": "Create minimal new system with maximum integration",
            "next_steps": [
                "Design integration interfaces",
                "Create minimal viable system",
                "Integrate with existing systems",
                "Document integration patterns"
            ]
        }

# IMMEDIATE INTEGRATION EXAMPLES
def demonstrate_integration_approach():
    """Demonstrate the new integration-first approach"""
    
    orchestrator = IntegrationOrchestrator()
    
    # Example tasks that would have created redundant systems
    test_tasks = [
        "Create duplicate file detector",
        "Build AI orchestration system", 
        "Develop file registry system",
        "Create code review workflow"
    ]
    
    print("=== INTEGRATION-FIRST APPROACH DEMONSTRATION ===\n")
    
    for task in test_tasks:
        result = orchestrator.execute_integration_task(task)
        
        print(f"Task: {task}")
        print(f"Integration Type: {result['integration_type']}")
        
        if 'systems_to_use' in result:
            print("Existing Systems to Use:")
            for system in result['systems_to_use'][:2]:
                print(f"  - {system['action']}")
        
        print(f"Next Steps: {', '.join(result['next_steps'][:2])}")
        print("-" * 50)

if __name__ == "__main__":
    demonstrate_integration_approach()
