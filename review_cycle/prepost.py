"""Prepare/Post checklists per phase — single source of truth.

Auto-detects which prepare items are already satisfied (env vars, tools).
"""

import os
import shutil
import sys

BASE = os.path.expanduser("~/Public")
ENV_PATH = os.path.join(BASE, "ENV", ".env")

# ── Prepare item tags ──
# design = design decision needed
# env    = env var to set
# tool   = tool or CLI to install/verify
# space  = directory to create
# cleanup = files to remove
# auth   = API token / permissions

PHASES: dict[int, dict] = {
    19: {
        "name": "Hugging Face Hub CLI",
        "prepare": [
            ("env", "HF_TOKEN"),
            ("auth", "Token read permission (models)"),
            ("tool", "cURL or requests available", "curl"),
            ("space", "~/Public/hf/ cache dir"),
            ("design", "Repo → phase mapping (none needed — standalone CLI)"),
        ],
        "post": [
            ("tag", "Git tag anchor-YYYYMMDDa across all touch repos"),
            ("log", "Update AGENT_LOG.md with deliverables"),
            ("plan", "Mark Phase 19 complete in PLAN.md"),
            ("dash", "Update DASHBOARD.md progress"),
            ("vote", "Re-run vote — Phase 20 may gain weight"),
            ("scan", "Run auto-scan to verify no regressions"),
            ("kb", "Rebuild KB: workspace.sh kb-auto scan"),
        ],
    },
    20: {
        "name": "GitHub Automation",
        "prepare": [
            ("design", "Define repo→GitHub name mapping (project→mcp, etc.)"),
            ("design", "Set severity threshold: which findings become issues"),
            ("design", "Define dedup strategy (use finding_id)"),
            ("design", "Define label schema (severity + category labels)"),
            ("tool", "gh CLI authenticated", "gh"),
            ("tool", "GitHub Issues enabled on all target repos"),
            ("env", "GH_TOKEN or gh auth token available"),
        ],
        "post": [
            ("tag", "Git tag anchor-YYYYMMDD across touch repos"),
            ("log", "Update AGENT_LOG.md with deliverables"),
            ("plan", "Mark Phase 20 complete in PLAN.md"),
            ("dash", "Update DASHBOARD.md progress"),
            ("vote", "Re-run vote — Phase 21 may gain weight"),
            ("scan", "Run scan to verify issue creation works"),
            ("kb", "Rebuild KB: workspace.sh kb-auto scan"),
        ],
    },
    21: {
        "name": "Web Dashboard",
        "prepare": [
            ("env", "SUPABASE_URL"),
            ("env", "SUPABASE_ANON_KEY"),
            ("tool", "Node.js via fnm (v24)", "node"),
            ("tool", "Vercel CLI installed", "vercel"),
            ("tool", "vercel --login done"),
            ("design", "Dashboard wireframe: which cards, what data"),
            ("space", "~/Public/dashboard/ or inside project/"),
        ],
        "post": [
            ("tag", "Git tag anchor-YYYYMMDD across touch repos"),
            ("log", "Update AGENT_LOG.md"),
            ("plan", "Mark Phase 21 complete"),
            ("dash", "Update DASHBOARD.md"),
            ("vote", "Re-run vote"),
            ("scan", "Run scan — verify health endpoint works"),
            ("kb", "Rebuild KB"),
            ("deploy", "Push to Vercel production"),
        ],
    },
    22: {
        "name": "Cloud Storage Sync",
        "prepare": [
            ("tool", "rclone installed", "rclone"),
            ("tool", "rclone config for Dropbox or S3"),
            ("env", "DROPBOX_ACCESS_TOKEN"),
            ("design", "What to sync: backups/, snapshots/, kb/"),
            ("design", "Schedule: daily? on-scan?"),
        ],
        "post": [
            ("tag", "Git tag anchor-YYYYMMDD"),
            ("log", "Update AGENT_LOG.md"),
            ("plan", "Mark Phase 22 complete"),
            ("dash", "Update DASHBOARD.md"),
            ("vote", "Re-run vote"),
            ("verify", "Test restore from cloud backup"),
            ("kb", "Rebuild KB"),
        ],
    },
    23: {
        "name": "Deploy Apps",
        "prepare": [
            ("tool", "Docker installed", "docker"),
            ("tool", "Vercel CLI (from Phase 21)", "vercel"),
            ("env", "RENDER_API_KEY (optional)"),
            ("design", "Which services deploy: health API, dashboard"),
            ("design", "Dockerfile for Python health endpoint"),
        ],
        "post": [
            ("tag", "Git tag anchor-YYYYMMDD"),
            ("log", "Update AGENT_LOG.md"),
            ("plan", "Mark Phase 23 complete"),
            ("dash", "Update DASHBOARD.md"),
            ("vote", "Re-run vote — Phases 26-27 next"),
            ("verify", "Test cold-start on Render"),
            ("kb", "Rebuild KB"),
        ],
    },
    26: {
        "name": "DevEnvSync Restructure",
        "prepare": [
            ("design", "Review REFACTOR_PROGRESS.json (40 tasks, 0%)"),
            ("design", "Decide: merge into project/ or stay standalone"),
            ("cleanup", "Remove planning artifacts (504-line JSON at 0%)"),
            ("tool", "Fix hardcoded Windows paths"),
        ],
        "post": [
            ("tag", "Git tag anchor-YYYYMMDD"),
            ("log", "Update AGENT_LOG.md"),
            ("plan", "Mark Phase 26 complete"),
            ("dash", "Update DASHBOARD.md"),
            ("vote", "Re-run vote"),
            ("kb", "Rebuild KB"),
        ],
    },
    27: {
        "name": "DevFlow Wiki Content",
        "prepare": [
            ("design", "Content plan: which 4/50 pages are done, which to write next"),
            ("tool", "MkDocs + Material theme", "mkdocs"),
            ("tool", "GitHub Pages deploy — already configured"),
        ],
        "post": [
            ("tag", "Git tag anchor-YYYYMMDD"),
            ("log", "Update AGENT_LOG.md"),
            ("plan", "Mark Phase 27 complete"),
            ("dash", "Update DASHBOARD.md"),
            ("verify", "Verify GitHub Pages renders correctly"),
            ("kb", "Rebuild KB"),
        ],
    },
}

PREPARE_ICONS = {"design": "📐", "env": "🔑", "tool": "🛠", "space": "📁", "cleanup": "🧹", "auth": "🔒"}
POST_ICONS = {"tag": "🏷", "log": "📝", "plan": "📋", "dash": "📊", "vote": "🗳", "scan": "🔍", "kb": "📚", "deploy": "🚀", "verify": "✅"}


def _load_env_vars() -> set[str]:
    vars_found: set[str] = set()
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    vars_found.add(line.split("=")[0].strip())
    return vars_found


def _item_icon(tp: str, desc: str) -> str:
    return PREPARE_ICONS.get(tp, "•")


def _post_icon(tp: str) -> str:
    return POST_ICONS.get(tp, "•")


def _is_done(item: tuple, env_vars: set[str]) -> bool:
    """Check if a prepare item is already satisfied."""
    tp = item[0]
    name = item[1]
    if tp == "env":
        key = name
        return key in env_vars
    if tp == "tool" and len(item) >= 3:
        bin_name = item[2]
        return shutil.which(bin_name) is not None
    # design, space, cleanup, auth — can't auto-detect, always show
    return False


def get_phase_info(phase_num: int) -> dict | None:
    return PHASES.get(phase_num)


def get_prepare(phase_num: int) -> list[tuple]:
    info = PHASES.get(phase_num)
    return list(info["prepare"]) if info else []


def get_post(phase_num: int) -> list[tuple[str, str]]:
    info = PHASES.get(phase_num)
    return list(info["post"]) if info else []


def list_unprepared(phase_num: int) -> list[tuple]:
    """Return prepare items that are NOT yet satisfied."""
    info = PHASES.get(phase_num)
    if not info:
        return []
    env_vars = _load_env_vars()
    unprepared = []
    for item in info["prepare"]:
        if not _is_done(item, env_vars):
            unprepared.append(item)
    return unprepared


def list_done(phase_num: int) -> list[tuple]:
    """Return prepare items that ARE already satisfied."""
    info = PHASES.get(phase_num)
    if not info:
        return []
    env_vars = _load_env_vars()
    done = []
    for item in info["prepare"]:
        if _is_done(item, env_vars):
            done.append(item)
    return done


def render_prepare(items: list[tuple], done_set: set[tuple]) -> str:
    lines = []
    for item in items:
        completed = item in done_set
        icon = "✅" if completed else _item_icon(item[0], item[1])
        label = item[1]
        lines.append(f"    {icon} {label}")
    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: prepost.py <phase_num> [prepare|post|status]")
        return
    phase_num = int(args[0])
    mode = args[1] if len(args) > 1 else "status"
    info = get_phase_info(phase_num)
    if not info:
        print(f"Phase {phase_num} not found")
        return

    print(f"\n  Phase {phase_num}: {info['name']}\n")

    if mode in ("prepare", "status"):
        all_items = info["prepare"]
        done_items = set(list_done(phase_num))
        print("  📋 Prepare checklist:")
        print(render_prepare(all_items, done_items))

    if mode in ("post", "status"):
        print()
        print("  ✅ Post-phase checklist:")
        for tp, desc in info["post"]:
            print(f"    {_post_icon(tp)} {desc}")
    print()


if __name__ == "__main__":
    main()
