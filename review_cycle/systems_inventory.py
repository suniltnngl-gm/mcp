#!/usr/bin/env python3
"""Inventory local system, cloud keys, and existing tools to avoid rebuilding what's free."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path.home() / "Public"
ENV_FILE = BASE / "ENV" / ".env"

PHASE_TIMINGS = {
    19: {"total": "1.5h", "tasks": {"19.1": "20min", "19.2": "30min", "19.3": "20min", "19.4": "15min"}},
    20: {"total": "1h", "tasks": {"20.1": "25min", "20.2": "20min", "20.3": "20min"}},
    21: {"total": "2h", "tasks": {"21.1": "30min", "21.2": "1h", "21.3": "20min"}},
    22: {"total": "1h", "tasks": {"22.1": "25min", "22.2": "30min", "22.3": "15min"}},
    23: {"total": "45min", "tasks": {"23.1": "30min", "23.2": "15min"}},
}


def check_cmd(name: str, ver_flag: str = "--version") -> dict:
    path = shutil.which(name)
    if not path:
        return {"available": False, "path": None, "version": None, "status": "missing"}
    try:
        r = subprocess.run([name, ver_flag], capture_output=True, text=True, timeout=5)
        ver = (r.stdout or r.stderr).splitlines()[0] if (r.stdout or r.stderr) else "ok"
    except Exception:
        ver = "error"
    return {
        "available": True,
        "path": path,
        "version": ver[:80],
        "status": "ready",
    }


def check_env_keys() -> dict:
    keys = {}
    if not ENV_FILE.exists():
        return {"status": "missing", "file": str(ENV_FILE), "keys": {}}
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                keys[k.strip()] = f"set ({len(v.strip())} chars)" if v.strip() else "empty"
    return {
        "status": "present",
        "file": str(ENV_FILE),
        "keys": keys,
    }


def check_cloud_auth() -> dict:
    """Check which cloud CLIs are authenticated."""
    auth = {}
    gh_check = subprocess.run(
        ["gh", "auth", "status"], capture_output=True, text=True, timeout=5
    )
    auth["github_cli"] = "authenticated" if gh_check.returncode == 0 else gh_check.stderr.strip()

    return auth


def inventory() -> dict:
    tools = {
        "bash": check_cmd("bash"),
        "curl": check_cmd("curl"),
        "git": check_cmd("git"),
        "python3": check_cmd("python3"),
        "uv": check_cmd("uv"),
        "node": check_cmd("node"),
        "npm": check_cmd("npm"),
        "fnm": check_cmd("fnm"),
        "gh": check_cmd("gh"),
        "jq": check_cmd("jq"),
        "docker": check_cmd("docker"),
        "rclone": check_cmd("rclone"),
        "vercel": check_cmd("vercel"),
        "supabase": check_cmd("supabase"),
    }

    env = check_env_keys()

    cloud_auth = check_cloud_auth()

    return {
        "tools": tools,
        "env_file": env,
        "cloud_auth": cloud_auth,
    }


def compute_gaps(state: dict) -> dict:
    """Compute what needs to be built for each phase based on what already exists."""
    tools = state["tools"]
    env_keys = state["env_file"].get("keys", {})
    cloud = state["cloud_auth"]

    ENV_PHASE_MAP = {
        "HF_TOKEN": ("19", "Hugging Face Hub CLI"),
        "GITHUB_TOKEN": ("20", "GitHub Automation"),
        "SUPABASE_URL": ("21a", "Web Dashboard — Supabase DB"),
        "SUPABASE_KEY": ("21a", "Web Dashboard — Supabase DB"),
        "VERCEL_TOKEN": ("21b", "Web Dashboard — Vercel frontend"),
        "DROPBOX_ACCESS_TOKEN": ("22", "Cloud Storage Sync"),
    }

    gaps = {}

    # Phase 19 — HF Hub CLI
    gaps["19"] = {
        "name": "Hugging Face Hub CLI",
        "needs_build": "HF_TOKEN" not in env_keys,
        "missing_keys": [] if "HF_TOKEN" in env_keys else ["HF_TOKEN"],
        "tools_ready": tools.get("curl", {}).get("available", False)
        and tools.get("python3", {}).get("available", False),
        "note": "HF_TOKEN needs to be set in ENV/.env" if "HF_TOKEN" not in env_keys else "Ready to go",
    }

    # Phase 20 — GitHub Automation
    gaps["20"] = {
        "name": "GitHub Automation",
        "needs_build": False,
        "missing_keys": [],
        "tools_ready": tools.get("gh", {}).get("available", False),
        "note": f"gh CLI: {cloud.get('github_cli', 'unknown')}",
    }

    # Phase 21 — Web Dashboard
    supabase_ready = tools.get("supabase", {}).get("available", False)
    vercel_ready = tools.get("vercel", {}).get("available", False)
    supabase_keys = all(k in env_keys for k in ("SUPABASE_URL", "SUPABASE_KEY"))
    gaps["21"] = {
        "name": "Web Dashboard",
        "needs_build": not supabase_ready or not vercel_ready or not supabase_keys,
        "missing_keys": [],
        "tools_ready": supabase_ready and vercel_ready,
        "note": "Needs: supabase CLI + vercel CLI + SUPABASE_URL/SUPABASE_KEY in ENV",
    }
    if "SUPABASE_URL" not in env_keys:
        gaps["21"]["missing_keys"].append("SUPABASE_URL")
    if "SUPABASE_KEY" not in env_keys:
        gaps["21"]["missing_keys"].append("SUPABASE_KEY")
    if not supabase_ready:
        gaps["21"]["missing_keys"].append("supabase CLI (npm install -g supabase)")
    if not vercel_ready:
        gaps["21"]["missing_keys"].append("vercel CLI (npm install -g vercel)")

    # Phase 22 — Cloud Storage Sync
    db_token = "DROPBOX_ACCESS_TOKEN" in env_keys
    rclone_ready = tools.get("rclone", {}).get("available", False)
    gaps["22"] = {
        "name": "Cloud Storage Sync",
        "needs_build": not db_token or not rclone_ready,
        "missing_keys": [],
        "tools_ready": db_token and rclone_ready,
        "note": f"Dropbox token: {'✅' if db_token else '❌'}, rclone: {'✅' if rclone_ready else '❌'}",
    }
    if not rclone_ready:
        gaps["22"]["missing_keys"].append("rclone (apt install rclone)")

    # Phase 23 — Deploy Apps
    gaps["23"] = {
        "name": "Deploy Apps",
        "needs_build": not vercel_ready,
        "missing_keys": [] if vercel_ready else ["vercel CLI"],
        "tools_ready": vercel_ready and tools.get("git", {}).get("available", False),
        "note": "Vercel handles frontend; Render for backend APIs (no CLI needed)",
    }

    return gaps


def main():
    state = inventory()
    gaps = compute_gaps(state)

    if "--json" in sys.argv:
        print(json.dumps({"inventory": state, "gaps": gaps}, indent=2, default=str))
        return

    print()
    print("  ════════════════════════════════════════")
    print("   SYSTEMS INVENTORY — Local + Cloud")
    print("  ════════════════════════════════════════")
    print()

    print("  ── Local Tools ──")
    for name, info in state["tools"].items():
        icon = "✅" if info["available"] else "❌"
        ver = info["version"] or ""
        print(f"    {icon} {name:12s} {ver}")
    print()

    print("  ── Cloud Keys (ENV/.env) ──")
    for k, v in state["env_file"].get("keys", {}).items():
        icon = "✅" if "set" in v else "⚠"
        print(f"    {icon} {k:30s} {v}")
    missing_hf = "HF_TOKEN" not in state["env_file"].get("keys", {})
    if missing_hf:
        print(f"    ❌ HF_TOKEN                       missing — needed for Phase 19")
    print()

    print("  ── Cloud Auth ──")
    for k, v in state["cloud_auth"].items():
        icon = "✅" if v == "authenticated" else "⚠"
        print(f"    {icon} {k:20s} {v}")
    print()

    print("  ── Phase Gaps (what needs building) ──")
    tot_build_time = 0
    for phase_num in sorted(gaps.keys()):
        g = gaps[phase_num]
        status = "🛠 BUILD" if g["needs_build"] else "✅ READY"
        timing = PHASE_TIMINGS.get(int(phase_num), {})
        eta = timing.get("total", "?")
        print(f"    Phase {phase_num}: {g['name']:30s} {status}  ⏱{eta}")
        if g["needs_build"]:
            for mk in g["missing_keys"]:
                print(f"       └ missing: {mk}")
            tot_val = timing.get("total", "0")
            if tot_val.endswith("h"):
                tot_build_time += float(tot_val.replace("h", "")) * 60
            elif tot_val.endswith("min"):
                tot_build_time += float(tot_val.replace("min", ""))
        print(f"       {g['note']}")
        print()

    ready_count = sum(1 for g in gaps.values() if not g["needs_build"])
    build_count = sum(1 for g in gaps.values() if g["needs_build"])
    print(f"  Summary: {ready_count} phases ready, {build_count} need build (~{tot_build_time:.0f}min total)")
    print()


if __name__ == "__main__":
    main()
