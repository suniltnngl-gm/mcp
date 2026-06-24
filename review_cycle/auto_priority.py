#!/usr/bin/env python3
"""Auto-determine next priority from PLAN.md + current state."""

import re
import sys
from pathlib import Path

BASE = Path.home() / "Public"
PLAN_MD = BASE / "project" / "PLAN.md"
DASHBOARD = BASE / ".opencode" / "DASHBOARD.md"
ENV_FILE = BASE / "ENV" / ".env"

PHASE_TIMINGS = {
    19: {"total": "1.5h", "tasks": {"19.1": "20min", "19.2": "30min", "19.3": "20min", "19.4": "15min"}},
    20: {"total": "1h", "tasks": {"20.1": "25min", "20.2": "20min", "20.3": "20min"}},
    21: {"total": "2h", "tasks": {"21.1": "30min", "21.2": "1h", "21.3": "20min"}},
    22: {"total": "1h", "tasks": {"22.1": "25min", "22.2": "30min", "22.3": "15min"}},
    23: {"total": "45min", "tasks": {"23.1": "30min", "23.2": "15min"}},
}

PHASE_REASONING = {
    19: "No way to find/download models from CLI. Every ML workflow starts here — search, grab, run.",
    20: "Review cycle findings have no audit trail. Issues make them persistent. PR labels flag risk areas.",
    21: "Health is text in a markdown file. A web UI makes it glanceable — live score, trends, next action.",
    22: "All backups are local. A disk failure loses everything. Cloud sync is cheap insurance.",
    23: "Nothing is deployed — no staging, no shareable URL. Deploy catches bugs early and enables demos.",
}

try:
    from review_cycle.prepost import get_phase_info, list_done, list_unprepared
except ImportError:
    get_phase_info = list_done = list_unprepared = None


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
            "status": p["status"],
            "done": p["done"],
            "total": p["total"],
            "pending_tasks": [t["task"] for t in pending_tasks],
        })

    return priorities


def get_inventory_gaps():
    try:
        from review_cycle.systems_inventory import compute_gaps
        from review_cycle.systems_inventory import inventory as inv
        state = inv()
        return compute_gaps(state)
    except Exception:
        return None


def get_vote_top():
    try:
        from review_cycle.vote import compute_scores
        return compute_scores()
    except Exception:
        return None


def main():
    phases, phase_name_map, tasks_map = parse_plan()
    blockers = check_blockers()
    priorities = find_next_priority(phases, phase_name_map, tasks_map)
    gaps = get_inventory_gaps()
    vote = get_vote_top()

    print()

    # ── Data Freshness ──
    data_file = Path.home() / "Public" / ".opencode" / "decision_log.json"
    last_decision = None
    if data_file.exists():
        try:
            import json as _json
            d = _json.loads(data_file.read_text())
            decs = d.get("decisions", [])
            if decs:
                last_decision = decs[-1]
                dt = last_decision["timestamp"][:19]
                print(f"  📊 Last decision: #{last_decision['id']} [{dt}] Phase {last_decision.get('chosen_phase', '?')}")
                print(f"     {last_decision['reason'][:100]}")
                print()
        except Exception:
            pass

    # ── Schedule ──
    try:
        from review_cycle.scheduler import estimate_remaining
        rem = estimate_remaining()
        if rem["phases"] > 0:
            print(f"  📅 Schedule: {rem['total_hours']}h remaining across {rem['phases']} phases")
            print(f"     Est. end: {rem['end_date_est']} (~{rem['total_days_est']} days at 4h/day)")
            print()
    except Exception:
        pass

    # ── Vote ──
    if vote:
        top_unblocked = [v for v in vote if not v["blocked_by"]]
        print(f"  🗳 Vote: #{vote[0]['phase']} ({vote[0]['weighted']}/100) wins raw,",
              f"#{top_unblocked[0]['phase']} ({top_unblocked[0]['weighted']}/100) best unblocked" if top_unblocked else "")
        print()

    # ── Blockers ──
    if blockers:
        print("  ⛔ Blockers:")
        for b in blockers:
            print(f"     • {b}")
        print()

    # ── Gap Analysis ──
    if gaps:
        build_phases = [p for p in priorities if gaps.get(str(p["phase"]), {}).get("needs_build")]
        ready_phases = [p for p in priorities if not gaps.get(str(p["phase"]), {}).get("needs_build", True)]
        if build_phases and ready_phases:
            print(f"  💡 Gap analysis: {len(build_phases)} need setup, {len(ready_phases)} ready to build")
            for p in ready_phases[:1]:
                print(f"     Ready now: Phase {p['phase']} — {p['name']}")
            print()

    # ── Next Priority ──
    if priorities:
        next_p = priorities[0]
        gap = gaps.get(str(next_p["phase"]), {}) if gaps else {}
        ready_icon = "✅" if gap.get("tools_ready") and not gap.get("needs_build") else "🛠"
        pn = next_p["phase"]
        timing = PHASE_TIMINGS.get(pn, {})
        reasoning = PHASE_REASONING.get(pn, "")
        print(f"  {ready_icon} Next Priority: Phase {pn} — {next_p['name']}")
        print(f"     Progress: {next_p['done']}/{next_p['total']} done, {len(next_p['pending_tasks'])} pending")
        print(f"     ⏱ ETA: {timing.get('total', '?')}")
        if next_p['pending_tasks']:
            nt = next_p['pending_tasks'][0]
            ttime = timing.get("tasks", {}).get(nt, "")
            print(f"     Next task: {nt} {ttime}")

        # ── KB Context ──
        try:
            from review_cycle.decision_log import validate as kb_validate
            kv = kb_validate(pn)
            if kv.get("found"):
                print(f"     📚 KB: {kv['matches']} relevant doc(s) found")
        except Exception:
            pass

        print(f"     💡 Why: {reasoning}")
        if gap.get("missing_keys"):
            print(f"     ⛔ Blocked by: {', '.join(gap['missing_keys'])}")

        # ── Prepare / Post checklists with live status ──
        if list_unprepared is not None and list_done is not None:
            not_ready = list_unprepared(pn)
            ready = list_done(pn)
            pinfo = get_phase_info(pn)
            all_items = pinfo["prepare"] if pinfo else []
            total = len(all_items)
            if total and next_p["status"] == "pending":
                n_ready = len(ready)
                print(f"     📋 Prepare {n_ready}/{total} satisfied")
                for item in not_ready[:4]:
                    tp, desc = item[0], item[1]
                    icon = {"design": "📐", "env": "🔑", "tool": "🛠", "space": "📁"}.get(tp, "•")
                    print(f"        {icon} {desc}")
                if len(not_ready) > 4:
                    print(f"        • … and {len(not_ready)-4} more")
                if not not_ready:
                    print("        ✅ All prepare items satisfied — ready to build")
            if next_p["status"] == "done" and pinfo:
                post = pinfo["post"]
                print(f"     ✅ Post-phase checklist ({len(post)} items):")
                for _, item in post[:4]:
                    print(f"        • {item}")
        print()

        # ── Backlog ──
        if len(priorities) > 1:
            print("  📋 Backlog:")
            for p in priorities[1:]:
                pn2 = p["phase"]
                t2 = PHASE_TIMINGS.get(pn2, {}).get("total", "?")
                print(f"     • Phase {pn2} — {p['name']} (⏱{t2})")
            print()

        # ── Validate & Auto-Log Decision ──
        try:
            from review_cycle.decision_log import get_history, log_decision
            hist = get_history(1)
            last_phase = hist[0].get("chosen_phase") if hist else None
            if last_phase != pn:
                log_decision(pn, reasoning)
        except Exception:
            pass
    else:
        print("  ✅ All phases complete!")
        print()

    # JSON output for scripting
    if "--json" in sys.argv:
        import json as _json
        result = {
            "next": priorities[0] if priorities else None,
            "all": priorities,
            "blockers": blockers,
        }
        print(_json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
