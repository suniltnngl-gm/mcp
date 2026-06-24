"""Critical data collector — single snapshot of env, tools, git, vote, gaps, phases, prepost.

Output: flat dict with everything needed to make a priority/schedule decision.
"""

import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path.home() / "Public"
ENV_FILE = BASE / "ENV" / ".env"
PLAN_MD = BASE / "project" / "PLAN.md"
PROJECT_DIR = BASE / "project"


def _env_snapshot() -> dict:
    keys = {}
    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    v_stripped = v.strip()
                    keys[k.strip()] = "set" if v_stripped else "empty"
    return {
        "file_exists": ENV_FILE.exists(),
        "key_count": len(keys),
        "keys": keys,
        "critical_missing": [
            k for k in ("HF_TOKEN", "SUPABASE_URL", "SUPABASE_KEY", "REPLIT_API_KEY")
            if k not in keys
        ],
    }


def _tool_snapshot() -> dict:
    tools = ["bash", "curl", "git", "python3", "uv", "node", "npm", "fnm",
             "gh", "jq", "docker", "rclone", "vercel", "supabase"]
    result = {}
    for name in tools:
        path = shutil.which(name)
        if not path:
            result[name] = {"available": False, "version": None}
            continue
        try:
            r = subprocess.run([name, "--version"], capture_output=True, text=True, timeout=5)
            ver = (r.stdout or r.stderr).splitlines()[0][:80] if (r.stdout or r.stderr) else "ok"
        except Exception:
            ver = None
        result[name] = {"available": True, "version": ver}
    return result


def _git_snapshot() -> dict:
    data = {}
    repos = ["project", "Workspace", ".opencode", "DevEnvSync", "devflow-intelligence",
             "project/dropbox-utils", "project/todo-automator",
             "project/docs", "project/shared"]
    for r in repos:
        p = BASE / r
        if not (p / ".git").exists():
            continue
        try:
            r_dirty = subprocess.run(
                ["git", "status", "--short"], cwd=p, capture_output=True, text=True, timeout=5
            )
            dirty_count = len([l for l in r_dirty.stdout.splitlines() if l.strip()])
            r_log = subprocess.run(
                ["git", "log", "--oneline", "-1"], cwd=p, capture_output=True, text=True, timeout=5
            )
            last_commit = r_log.stdout.strip()[:60] if r_log.stdout else "?"
            data[r] = {"dirty": dirty_count, "last_commit": last_commit}
        except Exception:
            data[r] = {"dirty": -1, "last_commit": "error"}
    return data


def _vote_snapshot() -> list | None:
    try:
        from review_cycle.vote import compute_scores
        return compute_scores()
    except Exception:
        return None


def _gaps_snapshot() -> dict | None:
    try:
        from review_cycle.systems_inventory import compute_gaps
        from review_cycle.systems_inventory import inventory as inv
        return compute_gaps(inv())
    except Exception:
        return None


def _prepost_snapshot() -> dict:
    by_phase = {}
    try:
        from review_cycle.prepost import get_phase_info, list_done
        for pn in (19, 20, 21, 22, 23, 26, 27):
            info = get_phase_info(pn)
            if info:
                ready = len(list_done(pn))
                total = len(info["prepare"])
                by_phase[pn] = {
                    "name": info["name"],
                    "prepare_ready": ready,
                    "prepare_total": total,
                    "prepare_done": ready == total,
                }
    except Exception:
        pass
    return by_phase


def _kb_snapshot() -> dict:
    """Read autokb index stats."""
    index_file = Path.home() / ".opencode" / "autokb" / "index.json"
    stats = {"available": False, "files": 0, "terms": 0, "generated": None, "size_kb": 0}
    if index_file.exists():
        try:
            import json
            data = json.loads(index_file.read_text())
            stats["available"] = True
            stats["files"] = data.get("entries_count", 0)
            stats["terms"] = data.get("terms_count", 0)
            stats["generated"] = data.get("generated", "?")[:19]
            stats["size_kb"] = round(index_file.stat().st_size / 1024, 1)
            stats["repos"] = data.get("repos", [])
        except Exception:
            pass
    return stats


def _phase_status_snapshot() -> dict:
    """Parse PLAN.md for progress summary."""
    import re
    phases = {}
    try:
        with open(PLAN_MD) as f:
            for line in f:
                m = re.match(r'^\|\s*(\d+)\.\s(.+?)\s*\|\s*([✅🔄⏳])\s*\|\s*(\d+)/(\d+)', line)
                if m:
                    num = int(m.group(1))
                    phases[num] = {
                        "name": m.group(2).strip(),
                        "status": "done" if m.group(3) == "✅" else "active" if m.group(3) == "🔄" else "pending",
                        "done": int(m.group(4)),
                        "total": int(m.group(5)),
                    }
    except Exception:
        pass
    return phases


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def snapshot() -> dict:
    return {
        "timestamp": _timestamp(),
        "env": _env_snapshot(),
        "tools": _tool_snapshot(),
        "git": _git_snapshot(),
        "kb": _kb_snapshot(),
        "vote": _vote_snapshot(),
        "gaps": _gaps_snapshot(),
        "prepost": _prepost_snapshot(),
        "phases": _phase_status_snapshot(),
    }


def print_summary(s: dict):
    print(f"\n  ══ Critical Data Snapshot — {s['timestamp'][:19]} ══\n")

    e = s["env"]
    print(f"  🔑 Env: {e['key_count']} keys set, {len(e['critical_missing'])} critical missing")
    if e["critical_missing"]:
        for k in e["critical_missing"]:
            print(f"       ❌ {k}")
    print()

    t = s["tools"]
    ready = sum(1 for v in t.values() if v["available"])
    total = len(t)
    print(f"  🛠 Tools: {ready}/{total} available")
    missing = [k for k, v in t.items() if not v["available"] and k in ("rclone", "docker", "vercel", "supabase")]
    if missing:
        print(f"       Missing: {', '.join(missing)}")
    print()

    g = s["git"]
    print(f"  📁 Git: {len(g)} repos")
    for repo, info in g.items():
        status = "dirty" if info["dirty"] > 0 else "clean"
        print(f"       {repo:15s} {status} ({info['dirty']} uncommitted)")
    print()

    kb = s["kb"]
    if kb["available"]:
        print(f"  📚 KB: {kb['files']} files, {kb['terms']} terms, {kb['size_kb']}KB")
        print(f"       Generated: {kb['generated']}")
        print(f"       Repos: {', '.join(kb.get('repos', []))}")
    else:
        print("  📚 KB: not indexed (run `kb-auto scan`)")
    print()

    v = s["vote"]
    if v:
        top = v[0]
        print(f"  🗳 Vote top: Phase {top['phase']} — {top['name']} ({top['weighted']}/100)")
        if top["blocked_by"]:
            print(f"       ⛔ Blocked: {', '.join(top['blocked_by'])}")
    print()

    p = s["prepost"]
    if p:
        print("  📋 Prepost readiness:")
        for pn, info in sorted(p.items()):
            icon = "✅" if info["prepare_done"] else f"{info['prepare_ready']}/{info['prepare_total']}"
            print(f"       Phase {pn:2d} {info['name']:28s} {icon}")
    print()


def main():
    s = snapshot()
    if "--json" in sys.argv:
        import json
        print(json.dumps(s, indent=2, default=str))
    else:
        print_summary(s)


if __name__ == "__main__":
    main()
