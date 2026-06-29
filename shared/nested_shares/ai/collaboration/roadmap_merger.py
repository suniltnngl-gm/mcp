#!/usr/bin/env python3
"""Merge roadmap documents into unified master roadmap"""

from pathlib import Path
from datetime import datetime

def merge_roadmaps():
    """Merge IMPROVEMENT_ROADMAP.md and SAFETY_INTEGRATED_ROADMAP.md"""
    
    orchestration_path = Path("/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares/ai/orchestration")
    
    improvement_file = orchestration_path / "IMPROVEMENT_ROADMAP.md"
    safety_file = orchestration_path / "SAFETY_INTEGRATED_ROADMAP.md"
    master_file = orchestration_path / "MASTER_ROADMAP.md"
    
    # Read source files
    improvement_content = improvement_file.read_text() if improvement_file.exists() else "# Improvement Roadmap\n(File not found)"
    safety_content = safety_file.read_text() if safety_file.exists() else "# Safety Roadmap\n(File not found)"
    
    # Create unified master roadmap
    master_content = f"""# Master AI Orchestration Roadmap

*Consolidated from IMPROVEMENT_ROADMAP.md and SAFETY_INTEGRATED_ROADMAP.md*
*Generated: {datetime.now().isoformat()}*

## Improvement Roadmap Section

{improvement_content}

---

## Safety Integration Section

{safety_content}

---

## Consolidation Metadata

- **Source Files:** IMPROVEMENT_ROADMAP.md, SAFETY_INTEGRATED_ROADMAP.md
- **Consolidation Date:** {datetime.now().strftime('%Y-%m-%d')}
- **Archive Policy:** All duplicates preserved in archive/
- **Framework Status:** Gemini-Kiro collaboration active
"""
    
    # Write master roadmap
    master_file.write_text(master_content)
    
    return {
        "master_file": str(master_file),
        "source_files": [str(improvement_file), str(safety_file)],
        "status": "merged"
    }

if __name__ == "__main__":
    result = merge_roadmaps()
    print(f"✅ Created master roadmap: {result['master_file']}")
    print(f"✅ Merged {len(result['source_files'])} source files")
