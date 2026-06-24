"""Session compact — structured summary with noise-filtered user file awareness.

Generates the Goal / Constraints / Progress / Decisions / Next Steps / Context / Files
summary. Filters out vendor dirs, build artifacts, generated assets, and hidden noise.
"""

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

BASE = Path.home() / "Public"
PROJECT = BASE / "project"
DECISION_LOG = BASE / ".opencode" / "decision_log.json"
SESSIONS_FILE = BASE / ".opencode" / "sessions.json"
SCHEDULE_FILE = BASE / ".opencode" / "schedule.json"
PLAN_MD = PROJECT / "PLAN.md"
ENV_FILE = BASE / "ENV" / ".env"
KB_INDEX = Path.home() / ".opencode" / "autokb" / "index.json"

NOISE_PATTERNS = [
    "node_modules/", "vendor/", ".venv/", "__pycache__/", ".git/",
    "dist/", "build/", ".next/", "target/", ".terraform/",
    "*.pyc", "*.pyo", "*.egg-info/",
    "*.min.js", "*.min.css", "*.map",
    "*.svg", "*.png", "*.jpg", "*.jpeg", "*.gif", "*.ico", "*.woff", "*.woff2", "*.ttf", "*.eot",
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    ".gitignore", ".dockerignore", ".editorconfig",
    ".env", ".env.*",
    "*.log", ".DS_Store", "Thumbs.db",
]

NOISE_DIRS = frozenset({
    "node_modules", "vendor", ".venv", "__pycache__", ".git",
    "dist", "build", ".next", "target", ".terraform",
    ".eggs", "*.egg-info", ".mypy_cache", ".pytest_cache",
    ".ruff_cache", ".vite",
})


def is_user_file(filepath: str) -> bool:
    """Returns True if filepath looks like a user-authored file (not noise)."""
    p = filepath.replace("\\", "/")
    for pat in NOISE_PATTERNS:
        if pat.startswith("*."):
            if p.endswith(pat[1:]):
                return False
        elif pat in p:
            return False
    parts = set(p.split("/"))
    if parts & NOISE_DIRS:
        return False
    ext = Path(p).suffix.lower()
    return ext not in (".pyc", ".pyo", ".map", ".svg", ".png", ".jpg", ".jpeg",
                        ".gif", ".ico", ".woff", ".woff2", ".ttf", ".eot", ".log")


def _filter_user_files(files: list[str]) -> list[str]:
    return sorted({f for f in files if is_user_file(f)})


def _load_json(path: Path) -> dict | list | None:
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception:
        pass
    return None


def _get_goal() -> str:
    try:
        from review_cycle.auto_priority import find_next_priority, parse_plan
        from review_cycle.scheduler import estimate_remaining
        from review_cycle.vote import compute_scores
        phases, name_map, tasks = parse_plan()
        priorities = find_next_priority(phases, name_map, tasks)
        vote = compute_scores()
        rem = estimate_remaining()
        if priorities:
            p = priorities[0]
            goal = f"Advance Phase {p['phase']} ({p['name']}) — {p['done']}/{p['total']} done"
            if vote:
                top = vote[0]
                goal += f". Vote: #{top['phase']} ({top['weighted']}/100) top"
            if rem and rem["phases"] > 0:
                goal += f". ~{rem['total_hours']}h remaining across {rem['phases']} phases"
            return goal
        return "All phases complete — maintain and iterate."
    except Exception:
        return "Advance pending phases per plan."


def _get_constraints() -> list[str]:
    lines = []
    try:
        from review_cycle.data_collector import snapshot
        s = snapshot()
        e = s["env"]
        lines.append(f"Python venv + {e['key_count']} env keys set, {len(e['critical_missing'])} critical missing")
        for k in e["critical_missing"]:
            lines.append(f"Missing: {k}")
        t = s["tools"]
        ready = sum(1 for v in t["tools"].values() if v["available"])
        lines.append(f"{ready}/{len(t['tools'])} tools available")
        missing_tools = [k for k, v in t["tools"].items() if not v["available"] and k in ("rclone", "docker")]
        if missing_tools:
            lines.append(f"Missing tools: {', '.join(missing_tools)}")
        kb = s["kb"]
        if kb.get("available"):
            lines.append(f"KB: {kb['files']} files, {kb['terms']} terms, ~{kb['size_kb']}KB")
    except Exception:
        pass
    try:
        from review_cycle.prepost import get_phase_info
        for pn in (19, 20, 21, 22, 23, 26, 27):
            info = get_phase_info(pn)
            if info:
                lines.append(f"Phase {pn} prep: {len(info['prepare'])} items defined")
    except Exception:
        pass
    return lines


def _get_progress() -> tuple[list[str], list[str], list[str]]:
    done = []
    in_progress = []
    blocked = []
    try:
        from review_cycle.auto_priority import parse_plan
        phases, _name_map, _tasks = parse_plan()
        for p in phases:
            label = f"Phase {p['num']} — {p['name']} ({p['done']}/{p['total']})"
            if p["status"] == "done":
                done.append(label)
            elif p["status"] == "in_progress":
                in_progress.append(label)
            else:
                in_progress.append(label)
    except Exception:
        pass
    sessions = _load_json(SESSIONS_FILE)
    if sessions:
        for s in sessions.get("sessions", []):
            desc = s.get("description", s.get("phase", ""))
            dur = s.get("duration_seconds", 0)
            if dur and desc:
                h = int(dur // 3600)
                m = int((dur % 3600) // 60)
                dstr = f"{h}h {m}m" if h else f"{m}m"
                done.append(f"Session #{s['id']} [{s['date']}] — {desc} ({dstr})")
    # Build in-progress from active session
    if sessions and sessions.get("active"):
        a = sessions["active"]
        in_progress.append(f"Session #{a['id']} — {a.get('phase', '?')} active")
    # Blockers from env
    if ENV_FILE.exists():
        content = ENV_FILE.read_text()
        key_map = {"HF_TOKEN": "Phase 19 (Hugging Face)", "SUPABASE_URL": "Phase 21 (Dashboard)",
                    "SUPABASE_KEY": "Phase 21", "REPLIT_API_KEY": "replit_server"}
        for key, phase in key_map.items():
            if key not in content:
                blocked.append(f"{key} missing — blocks {phase}")
    # Blockers from tool gaps
    try:
        from review_cycle.systems_inventory import compute_gaps
        from review_cycle.systems_inventory import inventory as inv
        gaps = compute_gaps(inv())
        if gaps:
            for pn_str, info in gaps.items():
                if info.get("missing_tools"):
                    blocked.append(f"Phase {pn_str}: {', '.join(info['missing_tools'])} not installed")
    except Exception:
        pass
    return done[-20:], in_progress, blocked


def _get_key_decisions() -> list[dict]:
    data = _load_json(DECISION_LOG)
    if data:
        return data.get("decisions", [])[-5:]
    return []


def _get_next_steps() -> list[str]:
    steps = []
    try:
        from review_cycle.scheduler import estimate_remaining
        rem = estimate_remaining()
        if rem["phases"] > 0:
            steps.append(f"Schedule: {rem['total_hours']}h across {rem['phases']} phases, est. end {rem['end_date_est']}")
    except Exception:
        pass
    try:
        from review_cycle.vote import compute_scores
        vote = compute_scores()
        if vote:
            unblocked = [v for v in vote if not v["blocked_by"]]
            if unblocked:
                steps.append(f"Next vote: Phase {unblocked[0]['phase']} ({unblocked[0]['weighted']}/100) — {unblocked[0]['name']}")
    except Exception:
        pass
    # Add specific unblock actions
    if ENV_FILE.exists():
        content = ENV_FILE.read_text()
        if "HF_TOKEN" not in content:
            steps.append("Add HF_TOKEN to ENV/.env to unblock Phase 19")
        if "SUPABASE_URL" not in content:
            steps.append("Create Supabase project and add SUPABASE_URL + SUPABASE_KEY")
        if "REPLIT_API_KEY" not in content:
            steps.append("Add REPLIT_API_KEY to ENV/.env to unblock replit_server tests")
    # Docker/rclone
    try:
        import shutil
        if not shutil.which("rclone"):
            steps.append("Install rclone (sudo apt install rclone) for Phase 22")
        if not shutil.which("docker"):
            steps.append("Install Docker for Phase 23")
    except Exception:
        pass
    return steps


def _get_critical_context() -> list[str]:
    lines = []
    try:
        from review_cycle.data_collector import snapshot
        s = snapshot()
        g = s["git"]
        for repo, info in g.items():
            if info["dirty"] > 0:
                lines.append(f"{repo}: {info['dirty']} uncommitted changes")
        lines.append(f"Tools: {sum(1 for v in s['tools'].values() if v['available'])}/{len(s['tools'])} ready")
        pp = s["prepost"]
        if pp:
            ready_phases = [str(pn) for pn, i in sorted(pp.items()) if i["prepare_done"]]
            if ready_phases:
                lines.append(f"Ready phases: {', '.join(ready_phases)}")
            else:
                lines.append("No phases fully prepped")
    except Exception:
        pass
    # Check MCP
    mcp = Path.home() / ".gemini" / "config" / "mcp_config.json"
    if mcp.exists():
        try:
            mc = json.loads(mcp.read_text())
            lines.append(f"MCP servers: {len(mc)} wired")
        except Exception:
            pass
    # Dependency graph
    lines.append("Deps: 19→20→21→23, 19→20→22→23, 26/27 independent")
    return lines


def _get_relevant_files() -> list[dict]:
    seen: dict[str, str] = {}
    # From session history
    sessions = _load_json(SESSIONS_FILE)
    if sessions:
        for s in sessions.get("sessions", []):
            for f in s.get("files", []):
                if is_user_file(f):
                    stem = Path(f).name
                    if stem not in seen:
                        seen[stem] = f
        active = sessions.get("active")
        if active:
            for f in active.get("files", []):
                if is_user_file(f):
                    stem = Path(f).name
                    if stem not in seen:
                        seen[stem] = f
    # From git (normalize to project/ prefix for consistency)
    try:
        r = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=PROJECT, capture_output=True, text=True, timeout=10,
        )
        for line in r.stdout.strip().splitlines():
            line = line.strip()
            if line and is_user_file(line):
                stem = Path(line).name
                if stem not in seen:
                    seen[stem] = f"project/{line}"
        r2 = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=PROJECT, capture_output=True, text=True, timeout=10,
        )
        for line in r2.stdout.strip().splitlines():
            line = line.strip()
            if line and is_user_file(line):
                stem = Path(line).name
                if stem not in seen:
                    seen[stem] = f"project/{line}"
    except Exception:
        pass
    # From review_cycle itself
    try:
        for f in sorted(PROJECT.glob("review_cycle/**/*.py")):
            rel = f.relative_to(BASE)
            stem = f.name
            if stem not in seen:
                seen[stem] = str(rel)
    except Exception:
        pass
    # Sort: staged/dirty files first, then by path
    def sort_key(item):
        p = item[1]
        return (0 if p.startswith("review_cycle") else 1, p)
    return [{"name": stem, "path": path} for stem, path in sorted(seen.items(), key=sort_key)]


def generate() -> str:
    goal = _get_goal()
    constraints = _get_constraints()
    done_list, in_progress_list, blocked_list = _get_progress()
    decisions = _get_key_decisions()
    next_steps = _get_next_steps()
    context = _get_critical_context()
    files = _get_relevant_files()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [f"## Session Compact — {now}", ""]

    # Goal
    lines.append("### Goal")
    lines.append(f"- {goal}")
    lines.append("")

    # Constraints & Preferences
    if constraints:
        lines.append("### Constraints & Preferences")
        for c in constraints:
            lines.append(f"- {c}")
        lines.append("")

    # Progress
    lines.append("### Progress")
    if done_list:
        lines.append("✅ Done")
        for d in done_list:
            lines.append(f"  - {d}")
    if in_progress_list:
        lines.append("🔄 In Progress")
        for ip in in_progress_list:
            lines.append(f"  - {ip}")
    if blocked_list:
        lines.append("⛔ Blocked")
        for b in blocked_list:
            lines.append(f"  - {b}")
    lines.append("")

    # Key Decisions
    if decisions:
        lines.append("### Key Decisions")
        for d in reversed(decisions):
            dt = d["timestamp"][:19]
            phase = d.get("chosen_phase", "?")
            reason = d.get("reason", "")[:100]
            lines.append(f"- #{d['id']} [{dt}] Phase {phase}: {reason}")
        lines.append("")

    # Next Steps
    if next_steps:
        lines.append("### Next Steps")
        for i, step in enumerate(next_steps, 1):
            lines.append(f"  {i}. {step}")
        lines.append("")

    # Critical Context
    if context:
        lines.append("### Critical Context")
        for c in context:
            lines.append(f"- {c}")
        lines.append("")

    # Relevant Files (user files only, no vendor/build noise)
    if files:
        lines.append("### Relevant Files")
        for f in files:
            lines.append(f"- `{f['path']}`")
        lines.append("")

    return "\n".join(lines)


def cmd_compact():
    print(generate())


if __name__ == "__main__":
    cmd_compact()
