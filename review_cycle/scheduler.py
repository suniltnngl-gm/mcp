"""Scheduler — timeline, dependency graph, rescheduling, ETA forecast.

Phase dependency chain (from PLAN.md):
  19 → 20 → 21 → 23
  19 → 20 → 22
  26, 27 independent

Estimates based on PHASE_TIMINGS + prepost readiness.
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE = Path.home() / "Public"
SCHEDULE_FILE = BASE / ".opencode" / "schedule.json"

DEFAULT_DURATIONS = {
    19: {"hours": 1.5, "tasks": 4},
    20: {"hours": 1.0, "tasks": 3},
    21: {"hours": 2.0, "tasks": 3},
    22: {"hours": 1.0, "tasks": 3},
    23: {"hours": 0.75, "tasks": 2},
    26: {"hours": 3.0, "tasks": 4},
    27: {"hours": 4.0, "tasks": 46},
}

# Phase → [phases it depends on]
DEPENDS_ON: dict[int, list[int]] = {
    19: [],
    20: [19],
    21: [20],
    22: [20],
    23: [21, 22],
    26: [],
    27: [],
}

# Phase → phases that depend on it (reverse)
DEPENDENTS: dict[int, list[int]] = {}
for pn, deps in DEPENDS_ON.items():
    for d in deps:
        DEPENDENTS.setdefault(d, []).append(pn)


def _now_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _load():
    default = {
        "start_date": _now_str(),
        "schedule": {},
        "reschedules": [],
    }
    if SCHEDULE_FILE.exists():
        try:
            return json.loads(SCHEDULE_FILE.read_text())
        except Exception:
            return default
    return default


def _save(data):
    SCHEDULE_FILE.parent.mkdir(parents=True, exist_ok=True)
    SCHEDULE_FILE.write_text(json.dumps(data, indent=2, default=str))


def _phase_status(pn: int) -> str:
    """Check if a phase is done, active, or pending from PLAN.md."""
    import re
    try:
        plan_md = BASE / "project" / "PLAN.md"
        with open(plan_md) as f:
            for line in f:
                m = re.match(r'^\|\s*(\d+)\.\s(.+?)\s*\|\s*([✅🔄⏳])', line)
                if m and int(m.group(1)) == pn:
                    icon = m.group(3)
                    return "done" if icon == "✅" else "active" if icon == "🔄" else "pending"
    except Exception:
        pass
    return "pending"


def _work_days(hours: float, per_day: float = 4.0) -> float:
    """Convert productive hours to calendar days at per_day hours/day."""
    return max(hours / per_day, 0.5) if hours > 0 else 0


def _add_work_days(start: datetime, hours: float, per_day: float = 4.0) -> datetime:
    """Advance a date by N productive-hours worth of calendar days."""
    days = _work_days(hours, per_day)
    return start + timedelta(days=days)


def compute_base_line(start_date: str | None = None) -> dict[int, dict]:
    """Compute the ideal timeline respecting dep order and work-day pacing."""
    if start_date is None:
        start_date = _now_str()
    cursor = datetime.strptime(start_date, "%Y-%m-%d")
    schedule = {}

    # Topological order respecting deps
    ordered = []
    visited = set()
    def visit(n):
        if n in visited:
            return
        visited.add(n)
        for dep in DEPENDS_ON.get(n, []):
            visit(dep)
        ordered.append(n)
    for pn in sorted(DEPENDS_ON.keys()):
        visit(pn)

    for pn in ordered:
        dur = DEFAULT_DURATIONS.get(pn, {"hours": 1})
        hours = dur["hours"]
        status = _phase_status(pn)
        end = _add_work_days(cursor, hours) if status != "done" else cursor
        schedule[pn] = {
            "name": DEFAULT_DURATIONS.get(pn, {}).get("tasks", "?") or f"Phase {pn}",
            "status": status,
            "start": cursor.strftime("%Y-%m-%d"),
            "duration_hours": hours,
            "estimated_end": end.strftime("%Y-%m-%d"),
            "deps": DEPENDS_ON.get(pn, []),
            "dependents": DEPENDENTS.get(pn, []),
        }
        if status != "done":
            cursor = _add_work_days(cursor, hours)

    return schedule


def _build_schedule(start_date: str | None = None):
    """Build and persist the schedule."""
    data = _load()
    if start_date:
        data["start_date"] = start_date
    sched = compute_base_line(data["start_date"])
    data["schedule"] = {str(k): v for k, v in sched.items()}
    _save(data)
    return sched


def reschedule(phase: int, new_start: str, reason: str):
    """Shift a phase + all downstream dependents."""
    data = _load()
    sched = {int(k): v for k, v in data.get("schedule", {}).items()}
    if not sched:
        sched = compute_base_line(data["start_date"])
        data["schedule"] = {str(k): v for k, v in sched.items()}

    if phase not in sched:
        print(f"  Phase {phase} not in schedule")
        return

    old_start = sched[phase]["start"]
    sched[phase]["start"] = new_start
    sched[phase]["estimated_end"] = _recalc_end(new_start, phase)

    # Shift downstream dependents
    _shift_downstream(phase, new_start, sched)

    # Record reschedule
    resched_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": phase,
        "from": old_start,
        "to": new_start,
        "reason": reason,
    }
    data["reschedules"].append(resched_entry)
    data["schedule"] = {str(k): v for k, v in sched.items()}
    _save(data)

    try:
        from review_cycle.decision_log import log_reschedule as log_resched
        log_resched(phase, old_start, new_start, reason)
    except Exception:
        pass

    print(f"  🔄 Phase {phase} rescheduled: {old_start} → {new_start}")
    print(f"     Reason: {reason}")
    return sched


def _recalc_end(start_str: str, phase: int) -> str:
    start = datetime.strptime(start_str, "%Y-%m-%d")
    hours = DEFAULT_DURATIONS.get(phase, {}).get("hours", 1)
    return _add_work_days(start, hours).strftime("%Y-%m-%d")


def _shift_downstream(phase: int, new_start_str: str, sched: dict):
    """Recursively shift phases that depend on `phase`."""
    for dep_pn in DEPENDENTS.get(phase, []):
        if dep_pn in sched:
            deps = DEPENDS_ON.get(dep_pn, [])
            # Calculate earliest start from all deps
            latest_dep_end = new_start_str
            for d in deps:
                if d in sched and sched[d]["estimated_end"] > latest_dep_end:
                    latest_dep_end = sched[d]["estimated_end"]
            dep_hours = DEFAULT_DURATIONS.get(dep_pn, {}).get("hours", 1)
            dep_start = datetime.strptime(latest_dep_end, "%Y-%m-%d")
            sched[dep_pn]["start"] = dep_start.strftime("%Y-%m-%d")
            sched[dep_pn]["estimated_end"] = _add_work_days(dep_start, dep_hours).strftime("%Y-%m-%d")
            _shift_downstream(dep_pn, sched[dep_pn]["start"], sched)


def estimate_remaining() -> dict:
    sched = compute_base_line()
    total_remaining_hours = 0
    remaining = {}
    for pn, info in sched.items():
        if info["status"] == "done":
            continue
        total_remaining_hours += info["duration_hours"]
        remaining[pn] = info
    return {
        "total_hours": total_remaining_hours,
        "total_days_est": round(total_remaining_hours / 4, 1),  # 4 productive hours/day
        "phases": len(remaining),
        "end_date_est": sched.get(max(sched.keys()), {}).get("estimated_end", "?"),
        "phases_remaining": remaining,
    }


def what_if(phase: int, delay_hours: float) -> dict:
    """What-if analysis: phase X takes Y hours longer than estimated."""
    sched = compute_base_line()
    if phase not in sched:
        return {"error": f"Phase {phase} not in schedule"}

    original = sched[phase]["estimated_end"]
    # Simulate delay
    delayed_end = _add_work_days(
        datetime.strptime(sched[phase]["start"], "%Y-%m-%d"),
        sched[phase]["duration_hours"] + delay_hours,
    ).strftime("%Y-%m-%d")

    # Find all downstream phases
    impacted = []
    def collect_downstream(n):
        for d in DEPENDENTS.get(n, []):
            impacted.append(d)
            collect_downstream(d)
    collect_downstream(phase)

    return {
        "phase": phase,
        "original_end": original,
        "delay_hours": delay_hours,
        "new_end": delayed_end,
        "impacted_phases": impacted,
        "recommendation": f"Phases {', '.join(str(p) for p in impacted)} will shift by ~{delay_hours}h" if impacted else "No downstream impact",
    }


def print_schedule(sched: dict[int, dict] | None = None):
    if sched is None:
        sched = compute_base_line()
    remaining = estimate_remaining()

    print()
    print("  ── Timeline ──")
    print(f"  Total remaining: {remaining['total_hours']}h (~{remaining['total_days_est']} days)")
    print(f"  Estimated end:   {remaining['end_date_est']}")
    print()

    for pn in sorted(sched.keys()):
        info = sched[pn]
        icon = {"done": "✅", "active": "🔄", "pending": "⏳"}.get(info["status"], "•")
        deps_str = f" ← {','.join(str(d) for d in info['deps'])}" if info["deps"] else ""
        print(f"  {icon} Phase {pn:2d} {info['start']} → {info['estimated_end']}  ({info['duration_hours']}h){deps_str}")

    reschedules = _load().get("reschedules", [])
    if reschedules:
        print(f"\n  Reschedules: {len(reschedules)}")
        for r in reschedules[-3:]:
            print(f"     Phase {r['phase']}: {r.get('from','?')} → {r.get('to','?')}  — {r.get('reason','')[:60]}")
    print()


def print_deps():
    print()
    print("  ── Dependency Graph ──")
    for pn in sorted(DEPENDS_ON.keys()):
        deps = DEPENDS_ON[pn]
        deps_str = ", ".join(f"Phase {d}" for d in deps) if deps else "(none)"
        print(f"  Phase {pn:2d}  ←  depends on: {deps_str}")
    print()
    print("  ── Downstream Impact ──")
    for pn in sorted(DEPENDENTS.keys()):
        deps = DEPENDENTS[pn]
        deps_str = ", ".join(f"Phase {d}" for d in deps) if deps else "(none)"
        print(f"  Phase {pn:2d}  →  blocks: {deps_str}")
    print()


def main():
    args = sys.argv[1:]
    if not args:
        print_schedule()
        return
    cmd = args[0]
    if cmd == "timeline":
        print_schedule()
    elif cmd == "deps":
        print_deps()
    elif cmd == "reschedule":
        phase = int(args[1]) if len(args) > 1 else None
        new_start = args[2] if len(args) > 2 else _now_str()
        reason = " ".join(args[3:]) if len(args) > 3 else "manual"
        if phase:
            reschedule(phase, new_start, reason)
        else:
            print("  Usage: schedule reschedule <phase> <new_start_date> <reason>")
    elif cmd == "what-if":
        phase = int(args[1]) if len(args) > 1 else None
        delay = float(args[2]) if len(args) > 2 else 1
        if phase:
            result = what_if(phase, delay)
            print(f"\n  What-if: Phase {phase} takes {delay}h longer")
            print(f"  Original end: {result.get('original_end','?')}")
            print(f"  New end:      {result.get('new_end','?')}")
            print(f"  Impact:       {result.get('recommendation','')}")
        else:
            print("  Usage: schedule what-if <phase> <delay_hours>")
    elif cmd == "remaining":
        r = estimate_remaining()
        print(f"\n  Remaining: {r['total_hours']}h across {r['phases']} phases")
        print(f"  Estimated: {r['total_days_est']} days (4h/day), end {r['end_date_est']}")
        print()
    elif cmd == "init":
        sched = _build_schedule(args[1] if len(args) > 1 else None)
        print(f"  ✅ Schedule initialized from {_load()['start_date']}")
        print_schedule(sched)
    else:
        print("  Usage: schedule <timeline|deps|reschedule|what-if|remaining|init> [args]")


if __name__ == "__main__":
    main()
