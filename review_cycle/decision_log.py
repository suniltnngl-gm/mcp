"""Decision log — records priority, schedule, and reschedule decisions with data snapshots.

Persists to ~/Public/.opencode/decision_log.json + writes markdown to .opencode/decisions/
so autokb picks them up on next scan.

Each entry includes: timestamp, type, chosen_phase, reason, critical data snapshot.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DECISION_LOG = Path.home() / "Public" / ".opencode" / "decision_log.json"
DECISIONS_DIR = Path.home() / "Public" / ".opencode" / "decisions"

TYPE_PRIORITY = "priority"
TYPE_SCHEDULE = "schedule"
TYPE_RESCHEDULE = "reschedule"
TYPE_VALIDATE = "validate"


def _load():
    if DECISION_LOG.exists():
        try:
            return json.loads(DECISION_LOG.read_text())
        except (json.JSONDecodeError, Exception):
            return {"decisions": [], "reschedules": []}
    return {"decisions": [], "reschedules": []}


def _save(data):
    DECISION_LOG.parent.mkdir(parents=True, exist_ok=True)
    DECISION_LOG.write_text(json.dumps(data, indent=2, default=str))


def _collect_live_data() -> dict:
    """Grab a lightweight snapshot of critical metrics for the decision record."""
    try:
        from review_cycle.data_collector import snapshot
        s = snapshot()
        return {
            "timestamp": s["timestamp"],
            "env_critical_missing": s["env"]["critical_missing"],
            "tools_ready": sum(1 for v in s["tools"].values() if v["available"]),
            "tools_total": len(s["tools"]),
            "vote_top": {
                "phase": s["vote"][0]["phase"],
                "score": s["vote"][0]["weighted"],
                "blocked_by": s["vote"][0]["blocked_by"],
            } if s.get("vote") else None,
            "prepost": {
                str(pn): {"ready": i["prepare_ready"], "total": i["prepare_total"]}
                for pn, i in s.get("prepost", {}).items()
            } if s.get("prepost") else {},
        }
    except Exception:
        return {"note": "data_collector unavailable"}


def _write_kb_entry(entry: dict):
    """Write decision as markdown so autokb indexes it on next scan."""
    DECISIONS_DIR.mkdir(parents=True, exist_ok=True)
    dt = entry["timestamp"][:19].replace(":", "-")
    slug = f"decision-{entry['id']:03d}-phase-{entry['chosen_phase']}-{dt}"
    ctx = entry.get("data", {})
    ctx_lines = []
    if ctx.get("env_critical_missing"):
        ctx_lines.append(f"- **Missing keys:** {', '.join(ctx['env_critical_missing'])}")
    ctx_lines.append(f"- **Tools:** {ctx.get('tools_ready', '?')}/{ctx.get('tools_total', '?')} available")
    if ctx.get("vote_top"):
        v = ctx["vote_top"]
        ctx_lines.append(f"- **Vote top:** Phase {v['phase']} ({v['score']}/100)")
    for pn, pi in sorted(ctx.get("prepost", {}).items()):
        icon = "✅" if pi["ready"] == pi["total"] else f"{pi['ready']}/{pi['total']}"
        ctx_lines.append(f"- **Phase {pn} prep:** {icon}")
    ctx_md = "\n".join(ctx_lines)
    md = f"""# Decision #{entry['id']} — Phase {entry['chosen_phase']}

- **Type:** {entry['type']}
- **Timestamp:** {entry['timestamp']}
- **Reason:** {entry['reason']}

## Context

{ctx_md}
"""
    (DECISIONS_DIR / f"{slug}.md").write_text(md)


def log_decision(chosen_phase: int, reason: str, decision_type: str = TYPE_PRIORITY,
                 extra: dict | None = None) -> dict:
    data = _load()
    entry = {
        "id": len(data["decisions"]) + 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": decision_type,
        "chosen_phase": chosen_phase,
        "reason": reason,
        "data": _collect_live_data(),
    }
    if extra:
        entry["extra"] = extra
    data["decisions"].append(entry)
    _save(data)
    _write_kb_entry(entry)
    return entry


def log_reschedule(phase: int, from_date: str, to_date: str, reason: str) -> dict:
    data = _load()
    entry = {
        "id": len(data["reschedules"]) + 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": phase,
        "from_date": from_date,
        "to_date": to_date,
        "reason": reason,
        "data": _collect_live_data(),
    }
    data["reschedules"].append(entry)
    _save(data)
    return entry


def get_history(limit: int = 5) -> list:
    data = _load()
    return data["decisions"][-limit:]


def get_reschedules(limit: int = 5) -> list:
    data = _load()
    return data["reschedules"][-limit:]


def print_history():
    data = _load()
    decisions = data.get("decisions", [])
    reschedules = data.get("reschedules", [])

    print()
    if not decisions and not reschedules:
        print("  (no decisions logged)")
        print()
        return

    if decisions:
        print("  ── Priority Decisions ──")
        for d in reversed(decisions[-5:]):
            dt = d["timestamp"][:19]
            phase = d.get("chosen_phase", "?")
            rtype = {"priority": "🎯", "schedule": "📅", "reschedule": "🔄", "validate": "🔍"}.get(d["type"], "•")
            print(f"  {rtype} #{d['id']} [{dt}] Phase {phase}")
            print(f"       {d['reason'][:120]}")
            if d.get("data", {}).get("vote_top"):
                v = d["data"]["vote_top"]
                print(f"       Vote: #{v['phase']} ({v['score']}/100) blocked_by={v.get('blocked_by', [])}")
            print()

    if reschedules:
        print("  ── Reschedule Events ──")
        for r in reversed(reschedules[-5:]):
            dt = r["timestamp"][:19]
            print(f"  🔄 [{dt}] Phase {r['phase']}: {r.get('from_date','?')} → {r.get('to_date','?')}")
            print(f"       Reason: {r['reason'][:120]}")
            print()

    print(f"  Total: {len(decisions)} decisions, {len(reschedules)} reschedules")
    print()


def validate(phase: int) -> dict:
    """Search KB for context relevant to a phase. Returns {found, term, count, preview}."""
    result = {"phase": phase, "found": False, "terms": [], "matches": 0, "preview": ""}
    index_file = Path.home() / ".opencode" / "autokb" / "index.json"
    if not index_file.exists():
        result["note"] = "KB not indexed"
        return result
    try:
        import subprocess
        phase_name = f"phase {phase}"
        search_dirs = [
            Path.home() / "Public" / "project" / "autokb",
            Path.home() / "Public" / ".opencode",
        ]

        rg = subprocess.run(["which", "rg"], capture_output=True, text=True, timeout=5)
        has_rg = rg.returncode == 0

        matches = set()
        for sd in search_dirs:
            if not sd.exists():
                continue
            if has_rg:
                r = subprocess.run(
                    ["rg", "-il", phase_name, "--glob", "*.md", str(sd)],
                    capture_output=True, text=True, timeout=10,
                )
                if r.stdout.strip():
                    for line in r.stdout.strip().splitlines():
                        matches.add(line)
            else:
                r2 = subprocess.run(
                    ["grep", "-ril", phase_name, "--include=*.md", str(sd)],
                    capture_output=True, text=True, timeout=10,
                )
                if r2.stdout.strip():
                    for line in r2.stdout.strip().splitlines():
                        matches.add(line)

        if matches:
            result["found"] = True
            result["matches"] = len(matches)
            preview_lines = list(matches)[:5]
            result["preview"] = "\n".join(preview_lines)[:300]
    except Exception as e:
        result["note"] = str(e)
    return result


def print_validate(v: dict):
    print(f"\n  🔍 KB Validate — Phase {v['phase']}")
    if v.get("note"):
        print(f"       ⚠ {v['note']}")
    elif v["found"]:
        print(f"       ✅ {v['matches']} relevant documents found")
        if v["preview"]:
            for line in v["preview"].splitlines()[:5]:
                print(f"       {line}")
    else:
        print("       ℹ No specific KB context found (phase may be new)")
    print()


def main():
    args = sys.argv[1:]
    if not args:
        print_history()
        return
    cmd = args[0]
    if cmd == "reschedule":
        phase = int(args[1]) if len(args) > 1 else None
        from_date = args[2] if len(args) > 2 else "?"
        to_date = args[3] if len(args) > 3 else "?"
        reason = " ".join(args[4:]) if len(args) > 4 else "no reason"
        if phase:
            e = log_reschedule(phase, from_date, to_date, reason)
            print(f"  🔄 Reschedule #{e['id']} logged: Phase {phase} → {to_date}")
        else:
            print("  Usage: decision reschedule <phase> <from> <to> <reason>")
    elif cmd == "history":
        print_history()
    elif cmd == "validate":
        phase = int(args[1]) if len(args) > 1 else None
        if phase:
            print_validate(validate(phase))
        else:
            print("  Usage: decision validate <phase>")
    elif cmd == "log":
        phase = int(args[1]) if len(args) > 1 else None
        reason = " ".join(args[2:]) if len(args) > 2 else "no reason given"
        if phase:
            v = validate(phase)
            if v["found"]:
                print(f"  📚 KB found {v['matches']} relevant document(s) for Phase {phase}")
            e = log_decision(phase, reason)
            print(f"  ✅ Decision #{e['id']} logged: Phase {phase}")
        else:
            print("  Usage: decision log <phase> <reason>")
    else:
        print("  Usage: decision <log|reschedule|history|validate> [args]")


if __name__ == "__main__":
    main()
