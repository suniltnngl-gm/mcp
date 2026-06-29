#!/usr/bin/env python3
"""Detailed analysis of roadmap/todo/progress files"""

from file_unification_engine import FileUnificationEngine
import json

def main():
    engine = FileUnificationEngine("/media/sunil-kr/workspace/user-projects")
    files = engine.scan_files()
    analysis = engine.analyze_content(files)
    
    print("=== FILE ANALYSIS REPORT ===")
    print(f"Total files found: {len(files)}")
    
    # Group by type
    by_type = {}
    for file in files:
        if file.type not in by_type:
            by_type[file.type] = []
        by_type[file.type].append(file)
    
    for file_type, type_files in by_type.items():
        print(f"\n{file_type.upper()} files ({len(type_files)}):")
        for file in type_files[:5]:  # Show first 5
            print(f"  - {file.path}")
        if len(type_files) > 5:
            print(f"  ... and {len(type_files) - 5} more")
    
    print(f"\n=== CONSOLIDATION OPPORTUNITIES ===")
    print(f"High similarity duplicates: {len(analysis['duplicates'])}")
    print(f"Medium similarity overlaps: {len(analysis['overlaps'])}")
    
    if analysis['duplicates']:
        print("\nTop duplicates:")
        for dup in analysis['duplicates'][:3]:
            print(f"  Similarity {dup['similarity']:.2f}: {dup['files']}")
    
    # Key files for consolidation
    key_files = [f for f in files if 'orchestration' in f.path and f.type in ['roadmap', 'progress']]
    print(f"\nKey orchestration files: {len(key_files)}")
    for file in key_files:
        print(f"  - {file.type}: {file.path}")

if __name__ == "__main__":
    main()
