#!/usr/bin/env python3
"""System Discovery Rebuilder - Find ALL existing systems we forgot and rebuild integration"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class SystemDiscoveryRebuilder:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects")
        
        # Areas where we forgot existing systems
        self.system_categories = {
            "duplicate_detection": ["*duplicate*", "*dedup*", "*consolidat*"],
            "ai_orchestration": ["*orchestra*", "*ai_*", "*llm*", "*model*"],
            "file_management": ["*file*", "*registry*", "*index*", "*catalog*"],
            "automation": ["*auto*", "*script*", "*tool*", "*util*"],
            "analysis": ["*analy*", "*monitor*", "*track*", "*report*"],
            "collaboration": ["*collab*", "*discuss*", "*review*", "*merge*"],
            "configuration": ["*config*", "*setting*", "*env*", "*setup*"],
            "documentation": ["*doc*", "*wiki*", "*guide*", "*readme*"]
        }
    
    def discover_all_existing_systems(self) -> Dict:
        """Comprehensive discovery of ALL existing systems"""
        
        discovered_systems = {}
        
        for category, patterns in self.system_categories.items():
            discovered_systems[category] = {
                "tools": [],
                "scripts": [],
                "configs": [],
                "docs": []
            }
            
            for pattern in patterns:
                for file_path in self.workspace_path.rglob(pattern):
                    if "archive" in str(file_path) or ".git" in str(file_path):
                        continue
                        
                    if file_path.is_file():
                        file_info = {
                            "name": file_path.name,
                            "path": str(file_path.relative_to(self.workspace_path)),
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                            "type": self._classify_file(file_path)
                        }
                        
                        # Categorize by file type
                        if file_path.suffix == ".py":
                            discovered_systems[category]["tools"].append(file_info)
                        elif file_path.suffix in [".sh", ".bash"]:
                            discovered_systems[category]["scripts"].append(file_info)
                        elif file_path.suffix in [".json", ".yaml", ".yml", ".toml"]:
                            discovered_systems[category]["configs"].append(file_info)
                        elif file_path.suffix in [".md", ".txt", ".rst"]:
                            discovered_systems[category]["docs"].append(file_info)
        
        return discovered_systems
    
    def _classify_file(self, file_path: Path) -> str:
        """Classify file by content and location"""
        
        path_str = str(file_path).lower()
        
        if "shared-tools" in path_str:
            return "shared_tool"
        elif "current" in path_str:
            return "project_tool"
        elif "workspace-automation" in path_str:
            return "automation_tool"
        elif any(x in path_str for x in ["config", "setting"]):
            return "configuration"
        elif any(x in path_str for x in ["doc", "readme", "guide"]):
            return "documentation"
        else:
            return "unknown"
    
    def analyze_forgotten_systems(self, discovered: Dict) -> Dict:
        """Analyze which systems we forgot and their impact"""
        
        analysis = {
            "high_impact_forgotten": [],
            "integration_opportunities": [],
            "redundant_creations": [],
            "system_gaps": []
        }
        
        # High impact systems we forgot
        critical_patterns = {
            "duplicate_detection": ["dedup_checker.py", "duplicate_removal_plan.md"],
            "ai_orchestration": ["integrated_ai_discussion.py", "smart_ai_router.py"],
            "file_management": ["FILE_REGISTRY.md", "file_tracker.py"],
            "automation": ["project_creator.py", "smart_revival.py"]
        }
        
        for category, critical_files in critical_patterns.items():
            if category in discovered:
                category_files = []
                for file_type in discovered[category].values():
                    category_files.extend([f["name"] for f in file_type])
                
                for critical_file in critical_files:
                    if any(critical_file in existing for existing in category_files):
                        analysis["high_impact_forgotten"].append({
                            "category": category,
                            "file": critical_file,
                            "impact": "HIGH - Should have used instead of creating new"
                        })
        
        return analysis
    
    def create_integration_rebuild_plan(self, discovered: Dict, analysis: Dict) -> Dict:
        """Create plan to rebuild with proper system integration"""
        
        rebuild_plan = {
            "phase_1_discovery": {
                "action": "Map all existing systems",
                "systems_found": sum(len(cat["tools"]) + len(cat["scripts"]) + len(cat["configs"]) + len(cat["docs"]) 
                                   for cat in discovered.values()),
                "priority": "IMMEDIATE"
            },
            
            "phase_2_integration": {
                "action": "Integrate with existing systems instead of creating new",
                "integration_points": [],
                "priority": "HIGH"
            },
            
            "phase_3_consolidation": {
                "action": "Consolidate redundant systems",
                "consolidation_targets": [],
                "priority": "MEDIUM"
            },
            
            "phase_4_documentation": {
                "action": "Document all system integrations",
                "documentation_needs": ["System map", "Integration guide", "API registry"],
                "priority": "HIGH"
            }
        }
        
        # Add specific integration points
        for category, systems in discovered.items():
            if systems["tools"]:  # Has Python tools
                rebuild_plan["phase_2_integration"]["integration_points"].append({
                    "category": category,
                    "existing_tools": len(systems["tools"]),
                    "action": f"Use existing {category} tools instead of creating new ones"
                })
        
        return rebuild_plan
    
    def generate_system_map(self, discovered: Dict) -> str:
        """Generate comprehensive system map"""
        
        system_map = "# Comprehensive Existing Systems Map\n\n"
        system_map += f"Generated: {datetime.now().isoformat()}\n\n"
        
        total_systems = 0
        
        for category, systems in discovered.items():
            category_total = sum(len(systems[t]) for t in systems.keys())
            total_systems += category_total
            
            if category_total > 0:
                system_map += f"## {category.upper().replace('_', ' ')} ({category_total} systems)\n\n"
                
                for system_type, files in systems.items():
                    if files:
                        system_map += f"### {system_type.title()} ({len(files)})\n"
                        for file_info in files[:5]:  # Show first 5
                            system_map += f"- `{file_info['name']}` - {file_info['path']}\n"
                        if len(files) > 5:
                            system_map += f"- ... and {len(files) - 5} more\n"
                        system_map += "\n"
        
        system_map += f"\n**Total Systems Found: {total_systems}**\n"
        system_map += "\n⚠️ **CRITICAL**: Always check this map BEFORE creating new systems!\n"
        
        return system_map

if __name__ == "__main__":
    print("=== SYSTEM DISCOVERY REBUILDER ===")
    print("Finding ALL existing systems we forgot...\n")
    
    rebuilder = SystemDiscoveryRebuilder()
    
    # Phase 1: Discover all existing systems
    print("🔍 Phase 1: Discovering existing systems...")
    discovered = rebuilder.discover_all_existing_systems()
    
    total_found = sum(
        len(cat["tools"]) + len(cat["scripts"]) + len(cat["configs"]) + len(cat["docs"])
        for cat in discovered.values()
    )
    
    print(f"✅ Found {total_found} existing systems across {len(discovered)} categories")
    
    # Phase 2: Analyze what we forgot
    print("\n🔍 Phase 2: Analyzing forgotten systems...")
    analysis = rebuilder.analyze_forgotten_systems(discovered)
    
    print(f"⚠️  High impact systems forgotten: {len(analysis['high_impact_forgotten'])}")
    for forgotten in analysis["high_impact_forgotten"][:3]:
        print(f"   - {forgotten['category']}: {forgotten['file']}")
    
    # Phase 3: Create rebuild plan
    print("\n🔍 Phase 3: Creating integration rebuild plan...")
    rebuild_plan = rebuilder.create_integration_rebuild_plan(discovered, analysis)
    
    print("📋 REBUILD PLAN:")
    for phase, details in rebuild_plan.items():
        print(f"   {phase}: {details['action']} (Priority: {details['priority']})")
    
    # Phase 4: Generate system map
    print("\n🔍 Phase 4: Generating comprehensive system map...")
    system_map = rebuilder.generate_system_map(discovered)
    
    # Save results
    results_dir = Path(__file__).parent
    
    # Save discovered systems
    (results_dir / "discovered_systems.json").write_text(
        json.dumps(discovered, indent=2)
    )
    
    # Save system map
    (results_dir / "COMPREHENSIVE_SYSTEM_MAP.md").write_text(system_map)
    
    # Save rebuild plan
    (results_dir / "integration_rebuild_plan.json").write_text(
        json.dumps(rebuild_plan, indent=2)
    )
    
    print(f"\n✅ SYSTEM DISCOVERY COMPLETE")
    print(f"📁 Results saved:")
    print(f"   - discovered_systems.json")
    print(f"   - COMPREHENSIVE_SYSTEM_MAP.md") 
    print(f"   - integration_rebuild_plan.json")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Review COMPREHENSIVE_SYSTEM_MAP.md BEFORE any new development")
    print(f"   2. Use existing systems instead of creating new ones")
    print(f"   3. Integrate with discovered systems")
    print(f"   4. Update collaboration framework to use existing tools")
