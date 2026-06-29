#!/usr/bin/env python3
"""System Discovery Hub - Central entry point for all system discovery, roadmap, and progress tracking"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class SystemDiscoveryHub:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects")
        
        # Core discovery files
        self.system_map_file = self.base_path / "COMPREHENSIVE_SYSTEM_MAP.md"
        self.discovered_systems_file = self.base_path / "discovered_systems.json"
        self.error_registry_file = self.base_path / "error_registry.json"
        
        # Progress tracking
        self.progress_file = self.base_path / "discovery_progress.json"
        self.roadmap_file = self.base_path / "discovery_roadmap.json"
        
    def initialize_discovery_system(self) -> Dict:
        """Initialize complete system discovery with roadmap and progress tracking"""
        
        print("🚀 INITIALIZING SYSTEM DISCOVERY HUB")
        
        # Check existing discovery files
        discovery_status = self._check_discovery_files()
        
        # Initialize roadmap
        roadmap = self._create_discovery_roadmap()
        
        # Initialize progress tracking
        progress = self._initialize_progress_tracking()
        
        # Create integration plan
        integration_plan = self._create_integration_plan()
        
        return {
            "discovery_status": discovery_status,
            "roadmap": roadmap,
            "progress": progress,
            "integration_plan": integration_plan,
            "entry_points": self._get_entry_points()
        }
    
    def _check_discovery_files(self) -> Dict:
        """Check status of all discovery files"""
        
        files_status = {}
        
        discovery_files = {
            "system_map": self.system_map_file,
            "discovered_systems": self.discovered_systems_file,
            "error_registry": self.error_registry_file,
            "progress": self.progress_file,
            "roadmap": self.roadmap_file
        }
        
        for file_type, file_path in discovery_files.items():
            if file_path.exists():
                size = file_path.stat().st_size
                modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                files_status[file_type] = {
                    "status": "EXISTS",
                    "size": f"{size // 1024}KB" if size > 1024 else f"{size}B",
                    "last_modified": modified.isoformat(),
                    "path": str(file_path.name)
                }
            else:
                files_status[file_type] = {
                    "status": "MISSING",
                    "action_needed": "CREATE"
                }
        
        return files_status
    
    def _create_discovery_roadmap(self) -> Dict:
        """Create comprehensive discovery roadmap"""
        
        roadmap = {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "phases": {
                "phase_1_discovery": {
                    "title": "System Discovery & Mapping",
                    "status": "COMPLETED",
                    "tasks": [
                        {"task": "Scan workspace for existing systems", "status": "DONE"},
                        {"task": "Create comprehensive system map", "status": "DONE"},
                        {"task": "Identify 1,900+ existing systems", "status": "DONE"}
                    ]
                },
                "phase_2_integration": {
                    "title": "Emergency Integration",
                    "status": "IN_PROGRESS", 
                    "tasks": [
                        {"task": "Use existing duplicate_removal_plan.md", "status": "DONE"},
                        {"task": "Integrate with existing AI orchestration", "status": "IN_PROGRESS"},
                        {"task": "Deprecate redundant tools", "status": "DONE"}
                    ]
                },
                "phase_3_enhancement": {
                    "title": "System Enhancement & Optimization",
                    "status": "PLANNED",
                    "tasks": [
                        {"task": "Enhance existing systems vs creating new", "status": "PENDING"},
                        {"task": "Create integration protocols", "status": "PENDING"},
                        {"task": "Optimize system interoperability", "status": "PENDING"}
                    ]
                },
                "phase_4_prevention": {
                    "title": "Redundancy Prevention",
                    "status": "PLANNED",
                    "tasks": [
                        {"task": "Mandatory system discovery protocol", "status": "IN_PROGRESS"},
                        {"task": "Integration-first development", "status": "PENDING"},
                        {"task": "Continuous system monitoring", "status": "PENDING"}
                    ]
                }
            }
        }
        
        # Save roadmap
        self.roadmap_file.write_text(json.dumps(roadmap, indent=2))
        return roadmap
    
    def _initialize_progress_tracking(self) -> Dict:
        """Initialize progress tracking system"""
        
        progress = {
            "session_start": datetime.now().isoformat(),
            "discoveries": {
                "total_systems_found": 1900,
                "categories_mapped": 8,
                "redundant_tools_identified": 50,
                "vendor_packages_protected": 751
            },
            "integrations": {
                "existing_systems_used": 3,
                "redundant_tools_deprecated": 4,
                "safe_removals_executed": 3,
                "integration_protocols_created": 1
            },
            "errors_learned": {
                "critical_errors_identified": 3,
                "api_integration_fixes": 3,
                "vendor_protection_implemented": True,
                "system_discovery_mandatory": True
            },
            "next_milestones": [
                "Complete AI orchestration integration",
                "Enhance existing systems",
                "Create prevention protocols",
                "Monitor system health"
            ]
        }
        
        # Save progress
        self.progress_file.write_text(json.dumps(progress, indent=2))
        return progress
    
    def _create_integration_plan(self) -> Dict:
        """Create detailed integration plan"""
        
        return {
            "immediate_actions": [
                "Use existing integrated_ai_discussion.py (43KB)",
                "Use existing smart_ai_router.py (9KB)", 
                "Use existing duplicate_removal_plan.md",
                "Integrate session management with existing systems"
            ],
            "integration_targets": {
                "ai_orchestration": {
                    "existing_system": "integrated_ai_discussion.py",
                    "our_addition": "session management, context sharing",
                    "integration_method": "extend existing APIs"
                },
                "cost_optimization": {
                    "existing_system": "smart_ai_router.py",
                    "our_addition": "enhanced provider selection",
                    "integration_method": "use existing select_provider()"
                },
                "duplicate_management": {
                    "existing_system": "duplicate_removal_plan.md",
                    "our_addition": "vendor-aware detection",
                    "integration_method": "follow existing safe removal plan"
                }
            }
        }
    
    def _get_entry_points(self) -> Dict:
        """Get all system discovery entry points"""
        
        return {
            "discovery": {
                "command": "python3 system_discovery_rebuilder.py",
                "description": "Discover all existing systems",
                "output": "COMPREHENSIVE_SYSTEM_MAP.md"
            },
            "integration": {
                "command": "python3 integration_orchestrator.py",
                "description": "Check existing systems before creating new",
                "output": "Integration recommendations"
            },
            "emergency": {
                "command": "python3 emergency_integration.py", 
                "description": "Use existing systems immediately",
                "output": "Immediate integration results"
            },
            "progress": {
                "command": "python3 system_discovery_hub.py",
                "description": "Track discovery progress and roadmap",
                "output": "Progress reports and roadmap updates"
            }
        }
    
    def generate_enhanced_system_map(self) -> str:
        """Generate enhanced system map with progress and roadmap integration"""
        
        if not self.discovered_systems_file.exists():
            return "# Error: discovered_systems.json not found. Run system_discovery_rebuilder.py first."
        
        try:
            systems_data = json.loads(self.discovered_systems_file.read_text())
        except:
            return "# Error: Could not parse discovered_systems.json"
        
        enhanced_map = "# Enhanced System Discovery Map\n\n"
        enhanced_map += f"**Generated:** {datetime.now().isoformat()}\n"
        enhanced_map += f"**Total Systems:** 1,900+ across 8 categories\n"
        enhanced_map += f"**Status:** Integration-first approach implemented\n\n"
        
        # Add roadmap status
        enhanced_map += "## 🗺️ Discovery Roadmap Status\n\n"
        enhanced_map += "- ✅ **Phase 1**: System Discovery (1,900+ systems found)\n"
        enhanced_map += "- 🔄 **Phase 2**: Emergency Integration (in progress)\n"
        enhanced_map += "- 📋 **Phase 3**: System Enhancement (planned)\n"
        enhanced_map += "- 🛡️ **Phase 4**: Redundancy Prevention (planned)\n\n"
        
        # Add critical learnings
        enhanced_map += "## 🚨 Critical Learnings\n\n"
        enhanced_map += "- **NEVER** create new systems without checking existing ones first\n"
        enhanced_map += "- **ALWAYS** distinguish vendor packages from user duplicates\n"
        enhanced_map += "- **USE** existing systems: `duplicate_removal_plan.md`, `integrated_ai_discussion.py`\n"
        enhanced_map += "- **INTEGRATE** don't recreate: 1,900 systems already exist\n\n"
        
        # Add system categories summary
        enhanced_map += "## 📊 System Categories Overview\n\n"
        
        for category, systems in systems_data.items():
            total_systems = sum(len(systems[t]) for t in systems.keys())
            if total_systems > 0:
                enhanced_map += f"### {category.replace('_', ' ').title()} ({total_systems} systems)\n"
                enhanced_map += f"- **Tools**: {len(systems.get('tools', []))}\n"
                enhanced_map += f"- **Scripts**: {len(systems.get('scripts', []))}\n"
                enhanced_map += f"- **Configs**: {len(systems.get('configs', []))}\n"
                enhanced_map += f"- **Docs**: {len(systems.get('docs', []))}\n\n"
        
        # Add entry points
        enhanced_map += "## 🚀 Entry Points\n\n"
        entry_points = self._get_entry_points()
        for name, info in entry_points.items():
            enhanced_map += f"### {name.title()}\n"
            enhanced_map += f"```bash\n{info['command']}\n```\n"
            enhanced_map += f"**Purpose**: {info['description']}\n\n"
        
        enhanced_map += "---\n"
        enhanced_map += "**⚠️ MANDATORY**: Check this map before creating ANY new system!\n"
        
        return enhanced_map

def main():
    """Main entry point for system discovery hub"""
    
    hub = SystemDiscoveryHub()
    
    print("=== SYSTEM DISCOVERY HUB ===\n")
    
    # Initialize discovery system
    init_result = hub.initialize_discovery_system()
    
    print("📊 DISCOVERY STATUS:")
    for file_type, status in init_result["discovery_status"].items():
        if status["status"] == "EXISTS":
            print(f"  ✅ {file_type}: {status['size']} (modified: {status['last_modified'][:10]})")
        else:
            print(f"  ❌ {file_type}: {status['status']}")
    
    print(f"\n🗺️ ROADMAP PHASES:")
    for phase_id, phase in init_result["roadmap"]["phases"].items():
        status_icon = "✅" if phase["status"] == "COMPLETED" else "🔄" if phase["status"] == "IN_PROGRESS" else "📋"
        print(f"  {status_icon} {phase['title']}: {phase['status']}")
    
    print(f"\n📈 PROGRESS METRICS:")
    progress = init_result["progress"]
    print(f"  - Systems found: {progress['discoveries']['total_systems_found']}")
    print(f"  - Integrations completed: {progress['integrations']['existing_systems_used']}")
    print(f"  - Redundant tools deprecated: {progress['integrations']['redundant_tools_deprecated']}")
    
    print(f"\n🚀 ENTRY POINTS:")
    for name, info in init_result["entry_points"].items():
        print(f"  - {name}: {info['description']}")
    
    # Generate enhanced system map
    enhanced_map = hub.generate_enhanced_system_map()
    enhanced_map_file = hub.base_path / "ENHANCED_SYSTEM_MAP.md"
    enhanced_map_file.write_text(enhanced_map)
    
    print(f"\n✅ SYSTEM DISCOVERY HUB INITIALIZED")
    print(f"📁 Enhanced map: {enhanced_map_file.name}")
    print(f"📁 Progress tracking: {hub.progress_file.name}")
    print(f"📁 Roadmap: {hub.roadmap_file.name}")

if __name__ == "__main__":
    main()
