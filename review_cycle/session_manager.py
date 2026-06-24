"""Session manager — track work sessions with timers, task progress, auto-logging.

Commands:
    session start <phase> <desc>   Start a new session
    session status                 Show current session
    session pause                  Pause timer
    session resume                 Resume timer
    session end                    End session, log to AGENT_LOG.md
    session log [N]                Show last N sessions
    session history                Show all sessions
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SESSIONS_FILE = Path.home() / "Public" / ".opencode" / "sessions.json"
AGENT_LOG = Path.home() / "Public" / ".opencode" / "AGENT_LOG.md"

SESSION_TEMPLATE = {
    "sessions": [],
    "active": None,
}


def load():
    if SESSIONS_FILE.exists():
        try:
            data = json.loads(SESSIONS_FILE.read_text())
            if "sessions" not in data:
                data = SESSION_TEMPLATE
            return data
        except (json.JSONDecodeError, KeyError):
            return dict(SESSION_TEMPLATE)
    return dict(SESSION_TEMPLATE)


def save(data):
    SESSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SESSIONS_FILE.write_text(json.dumps(data, indent=2, default=str))


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def fmt_duration(seconds):
    h, r = divmod(int(seconds), 3600)
    m, s = divmod(r, 60)
    parts = []
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)


def cmd_start(args):
    if not args:
        print("  Usage: session start <phase_or_task> <description>")
        return
    data = load()
    if data["active"]:
        print("  ⚠ Session already active. End it first or cancel.")
        return
    phase = args[0]
    desc = " ".join(args[1:]) if len(args) > 1 else ""
    session = {
        "id": len(data["sessions"]) + 1,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "start": now_iso(),
        "phase": phase,
        "description": desc,
        "tasks": [],
        "paused": False,
        "pause_total": 0,
        "pause_start": None,
    }
    data["active"] = session
    save(data)
    print(f"  ▶ Session #{session['id']} started — {phase}" + (f": {desc}" if desc else ""))


def cmd_status():
    data = load()
    if not data["active"]:
        print("  ⏸ No active session")
        return
    s = data["active"]
    start = datetime.fromisoformat(s["start"])
    elapsed = (datetime.now(timezone.utc) - start).total_seconds() - s.get("pause_total", 0)
    status = "▶" if not s.get("paused") else "⏸"
    tasks = s.get("tasks", [])
    done = sum(1 for t in tasks if t.get("done"))
    print(f"\n  {status} Session #{s['id']}")
    print(f"     Phase:  {s['phase']}")
    if s.get("description"):
        print(f"     Desc:   {s['description']}")
    print(f"     Elapsed: {fmt_duration(elapsed)}")
    files = s.get("files", [])
    if tasks:
        print(f"     Tasks:  {done}/{len(tasks)} done")
        for t in tasks:
            icon = "✅" if t.get("done") else "⏳"
            print(f"       {icon} {t['name']}")
    if files:
        print(f"     Files:  {len(files)}")
        for f in files:
            print(f"       • {f}")
    print()


def cmd_pause():
    data = load()
    if not data["active"]:
        print("  No active session")
        return
    s = data["active"]
    if s.get("paused"):
        print("  Already paused")
        return
    s["paused"] = True
    s["pause_start"] = now_iso()
    save(data)
    print("  ⏸ Session paused")


def cmd_resume():
    data = load()
    if not data["active"]:
        print("  No active session")
        return
    s = data["active"]
    if not s.get("paused"):
        print("  Already running")
        return
    pause_start = datetime.fromisoformat(s["pause_start"])
    s["pause_total"] = s.get("pause_total", 0) + (
        datetime.now(timezone.utc) - pause_start
    ).total_seconds()
    s["paused"] = False
    s["pause_start"] = None
    save(data)
    print("  ▶ Session resumed")


def cmd_task(args):
    """Manage tasks within current session."""
    if not args:
        print("  Usage: session task add <name> | session task done <name>")
        return
    data = load()
    if not data["active"]:
        print("  No active session")
        return
    s = data["active"]
    sub = args[0]
    name = " ".join(args[1:])
    if not name:
        print("  Provide task name")
        return
    tasks = s.setdefault("tasks", [])
    if sub == "add":
        # Syntax: task add "Built <file> — <description>"
        # or just: task add <name>
        tasks.append({"name": name, "done": False})
        save(data)
        print(f"  + Task added: {name}")
    elif sub == "done":
        for t in tasks:
            if t["name"] == name:
                t["done"] = True
                save(data)
                print(f"  ✅ Task done: {name}")
                return
        print(f"  Task not found: {name}")
    else:
        print(f"  Unknown: {sub}. Use 'add' or 'done'.")


def cmd_file(args):
    """Track files modified during current session."""
    if not args:
        print("  Usage: session file add <path> | session file list")
        return
    data = load()
    if not data["active"]:
        print("  No active session")
        return
    s = data["active"]
    sub = args[0]
    tracked = s.setdefault("files", [])
    if sub == "add":
        fpath = " ".join(args[1:])
        if not fpath:
            print("  Provide file path")
            return
        if fpath not in tracked:
            tracked.append(fpath)
            save(data)
            print(f"  + File: {fpath}")
        else:
            print(f"  Already tracked: {fpath}")
    elif sub == "list":
        if tracked:
            print(f"\n  📁 Files ({len(tracked)}):")
            for f in tracked:
                print(f"    • {f}")
        else:
            print("  No files tracked")
    else:
        print(f"  Unknown: {sub}. Use 'add' or 'list'.")


def cmd_end():
    data = load()
    if not data["active"]:
        print("  No active session")
        return
    s = data["active"]
    end = datetime.now(timezone.utc)
    start = datetime.fromisoformat(s["start"])
    net_seconds = (end - start).total_seconds() - s.get("pause_total", 0)
    duration_fmt = fmt_duration(net_seconds)
    date_str = s["date"]
    desc_str = s.get("description", "")
    phase_str = s["phase"]
    tasks = s.get("tasks", [])
    done_tasks = [t["name"] for t in tasks if t.get("done")]
    total_tasks = [t["name"] for t in tasks]

    s["end"] = end.isoformat()
    s["duration_seconds"] = net_seconds
    data["sessions"].append(s)
    data["active"] = None
    save(data)

    # Append to AGENT_LOG.md
    files = s.get("files", [])
    scope = " + ".join(files) if files else phase_str
    log_lines = [
        "---",
        f"date: {date_str}",
        f"focus: {desc_str or phase_str}",
        f"duration: {duration_fmt}",
        f"scope: {scope}",
        f"milestone: {phase_str}",
        "",
    ]
    if done_tasks:
        for tname in done_tasks:
            log_lines.append(f"- {tname}")
    elif desc_str:
        log_lines.append(f"- {desc_str}")
    log_lines.append("")
    log_entry = "\n".join(log_lines)

    with open(AGENT_LOG, "a") as f:
        f.write("\n" + log_entry)

    files = s.get("files", [])
    print(f"\n  ✅ Session #{s['id']} ended — {duration_fmt}")
    if done_tasks:
        print(f"     Tasks: {len(done_tasks)}/{len(total_tasks)} done")
    if files:
        print(f"     Files: {len(files)} tracked")
    print()


def cmd_log(args):
    data = load()
    sessions = data.get("sessions", [])
    if not sessions:
        print("  No sessions logged")
        return
    n = int(args[0]) if args and args[0].isdigit() else 5
    recent = sessions[-n:]
    print(f"\n  📋 Last {len(recent)} session(s):\n")
    for s in reversed(recent):
        start = datetime.fromisoformat(s["start"])
        dur = s.get("duration_seconds", 0)
        dstr = fmt_duration(dur) if dur else "?"
        print(f"    #{s['id']} [{s['date']}] {s['phase']} — {dstr}")
        if s.get("description"):
            print(f"       {s['description']}")
        tasks = s.get("tasks", [])
        if tasks:
            done = sum(1 for t in tasks if t.get("done"))
            print(f"       Tasks: {done}/{len(tasks)} done")
        print()


def cmd_history():
    cmd_log([str(999)])


def cmd_compact():
    """Generate a structured session compact with noise-filtered relevant files."""
    try:
        from review_cycle.compact import generate
        print(generate())
    except ImportError as e:
        print(f"  compact module unavailable: {e}")
    except Exception as e:
        print(f"  Error generating compact: {e}")


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: session.py <start|status|pause|resume|end|log|history|compact|task|file> [args...]")
        return
    cmd = args[0]
    rest = args[1:]
    commands_with_args = {"start", "log", "task", "file"}
    commands_plain = {"status", "pause", "resume", "end", "history", "compact"}
    if cmd in commands_with_args:
        handler = {
            "start": cmd_start,
            "log": cmd_log,
            "task": cmd_task,
            "file": cmd_file,
        }[cmd]
        handler(rest)
    elif cmd in commands_plain:
        handler = {
            "status": cmd_status,
            "pause": cmd_pause,
            "resume": cmd_resume,
            "end": cmd_end,
            "history": cmd_history,
            "compact": cmd_compact,
        }[cmd]
        handler()
    else:
        print(f"Unknown: {cmd}")


if __name__ == "__main__":
    main()
