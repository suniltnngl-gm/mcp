#!/usr/bin/env python3
"""Auto-determine next priority from PLAN.md + current state."""

import re
import sys
from pathlib import Path

BASE = Path.home() / "Public"
PLAN_MD = BASE / "project" / "PLAN.md"
DASHBOARD = BASE / ".opencode" / "DASHBOARD.md"
ENV_FILE = BASE / "ENV" / ".env"


def parse_plan():
    """Parse PLAN.md progress summary table and phase task tables."""
    phases = []
    in_summary = False
    in_phase = False
    current_phase = None
    current_tasks = {}
    phase_name_map = {}

    with open(PLAN_MD) as f:
        for line in f:
            # Progress Summary table: | N. Name | ✅/🔄 | N/M | N | type |
            m = re.match(r'^\|\s*(\d+)\.\s(.+?)\s*\|\s*([✅🔄⏳])\s*\|\s*(\d+)/(\d+)', line)
            if m:
                num = int(m.group(1))
                name = m.group(2).strip()
                status = m.group(3)
                done = int(m.group(4))
                total = int(m.group(5))
                pending = total - done
                phase_name_map[num] = name
                phases.append({
                    "num": num,
                    "name": name,
                    "status": "done" if status == "✅" else "in_progress" if status == "🔄" else "pending",
                    "done": done,
                    "total": total,
                    "pending": pending,
                })

            # Phase task tables: | N.N Description | ✅/🔄/⏳ | type |
            m2 = re.match(r'^\|\s*(\d+)\.(\d+)\s.+\|\s*([✅⏳🔄])\s', line)
            if m2:
                pnum = int(m2.group(1))
                tnum = int(m2.group(2))
                tstatus = m2.group(3)
                if pnum not in current_tasks:
                    current_tasks[pnum] = []
                current_tasks[pnum].append({
                    "task": f"{pnum}.{tnum}",
                    "status": tstatus,
                })

    return phases, phase_name_map, current_tasks


def check_blockers():
    """Check global blockers (missing API keys, etc.)."""
    blockers = []
    if ENV_FILE.exists():
        content = ENV_FILE.read_text()
        if "REPLIT_API_KEY" not in content:
            blockers.append("REPLIT_API_KEY missing from ENV/.env")
    else:
        blockers.append("ENV/.env not found")
    return blockers


def find_next_priority(phases, phase_name_map, tasks_map):
    """Find the next unblocked priority across all phases."""
    phased = [p for p in phases if p["status"] in ("in_progress", "pending")]
    phased.sort(key=lambda p: (0 if p["status"] == "in_progress" else 1, p["num"]))

    priorities = []
    for p in phased:
        num = p["num"]
        tasks = tasks_map.get(num, [])
        pending_tasks = [t for t in tasks if t["status"] in ("⏳", "🔄")]
        priorities.append({
            "phase": num,
            "name": p["name"],
            "done": p["done"],
            "total": p["total"],
            "pending_tasks": [t["task"] for t in pending_tasks],
        })

    return priorities


def main():
    phases, phase_name_map, tasks_map = parse_plan()
    blockers = check_blockers()
    priorities = find_next_priority(phases, phase_name_map, tasks_map)

    print()

    if blockers:
        print("  ⛔ Blockers:")
        for b in blockers:
            print(f"     • {b}")
        print()

    if priorities:
        next_p = priorities[0]
        print(f"  ▶ Next Priority: Phase {next_p['phase']} — {next_p['name']}")
        print(f"     {next_p['done']}/{next_p['total']} done, {len(next_p['pending_tasks'])} pending")
        if next_p['pending_tasks']:
            print(f"     Next task: {next_p['pending_tasks'][0]}")
        print()

        if len(priorities) > 1:
            print("  📋 Backlog:")
            for p in priorities[1:]:
                print(f"     • Phase {p['phase']} — {p['name']} ({p['done']}/{p['total']} done)")
            print()
    else:
        print("  ✅ All phases complete!")
        print()

    # JSON output for scripting
    if "--json" in sys.argv:
        import json
        result = {
            "next": priorities[0] if priorities else None,
            "all": priorities,
            "blockers": blockers,
        }
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
