#!/usr/bin/env python3
"""Vote on which phase to build next — weighted by value, effort, readiness, risk."""

import json
import sys
from pathlib import Path

BASE = Path.home() / "Public"
ENV_FILE = BASE / "ENV" / ".env"

PHASES = {
    19: {
        "name": "Hugging Face Hub CLI",
        "value": 8,
        "effort": 7,
        "readiness": 3,
        "risk": 2,
        "criticism": "HF_TOKEN is manual; free tier rate limits (60 req/hr); large models impractical on 3.7GB RAM",
        "vote_note": "Blocked by HF_TOKEN — but highest raw value",
    },
    20: {
        "name": "GitHub Automation",
        "value": 7,
        "effort": 8,
        "readiness": 9,
        "risk": 2,
        "criticism": "Issue noise without dedup; rate limits; PR label accuracy depends on repo structure",
        "vote_note": "Ready now — gh authenticated, no blockers",
    },
    21: {
        "name": "Web Dashboard",
        "value": 9,
        "effort": 6,
        "readiness": 5,
        "risk": 4,
        "criticism": "Nice-to-have vs need-to-have; maintenance surface; Supabase 500MB limit",
        "vote_note": "Highest value but blocked by Supabase keys",
    },
    22: {
        "name": "Cloud Storage Sync",
        "value": 6,
        "effort": 8,
        "readiness": 4,
        "risk": 3,
        "criticism": "Untested restore = no backup; 2GB Dropbox limit; rclone OAuth setup manual",
        "vote_note": "Lowest value but quick win if rclone is installed",
    },
    23: {
        "name": "Deploy Apps",
        "value": 7,
        "effort": 9,
        "readiness": 8,
        "risk": 3,
        "criticism": "Render cold starts (30s+); no custom domain on free tier; Vercel 10s function timeout",
        "vote_note": "Fastest to ship — 45min total",
    },
}

WEIGHTS = {
    "value": 3,
    "effort": 1,
    "readiness": 2,
    "risk": -1,
}


def compute_scores() -> list:
    results = []
    for pid, p in PHASES.items():
        raw = (
            p["value"] * WEIGHTS["value"]
            + p["effort"] * WEIGHTS["effort"]
            + p["readiness"] * WEIGHTS["readiness"]
            + p["risk"] * WEIGHTS["risk"]
        )
        max_raw = 10 * sum(abs(w) for w in WEIGHTS.values())
        normalized = round(raw / max_raw * 100)

        # Check real-world readiness
        env_keys = set()
        if ENV_FILE.exists():
            with open(ENV_FILE) as f:
                for line in f:
                    if "=" in line and not line.startswith("#"):
                        env_keys.add(line.split("=", 1)[0].strip())

        blocked_by = []
        if pid == 19 and "HF_TOKEN" not in env_keys:
            blocked_by.append("HF_TOKEN")
        if pid == 21:
            if "SUPABASE_URL" not in env_keys:
                blocked_by.append("SUPABASE_URL")
            if "SUPABASE_KEY" not in env_keys:
                blocked_by.append("SUPABASE_KEY")

        results.append({
            "phase": pid,
            "name": p["name"],
            "scores": {
                "value": p["value"],
                "effort": p["effort"],
                "readiness": p["readiness"],
                "risk": p["risk"],
            },
            "weighted": normalized,
            "blocked_by": blocked_by,
            "criticism": p["criticism"],
            "vote_note": p["vote_note"],
        })

    results.sort(key=lambda r: r["weighted"], reverse=True)
    return results


def main():
    scores = compute_scores()

    if "--json" in sys.argv:
        print(json.dumps(scores, indent=2))
        return

    print()
    print("  ════════════════════════════════════════")
    print("   PHASE VOTE — Weighted Score")
    print("  ════════════════════════════════════════")
    print()
    print(f"  Weights: value×{WEIGHTS['value']} + effort×{WEIGHTS['effort']}")
    print(f"           + readiness×{WEIGHTS['readiness']} + risk×{WEIGHTS['risk']} (normalized 0-100)")
    print()

    for i, s in enumerate(scores):
        rank = i + 1
        icon = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
        blocked = f" ⛔ {', '.join(s['blocked_by'])}" if s["blocked_by"] else " ✅ Ready"
        print(f"  {icon} #{rank} Phase {s['phase']:2d} — {s['name']:30s} {s['weighted']:3d}/100{blocked}")
        print(f"      V:{s['scores']['value']}  E:{s['scores']['effort']}  R:{s['scores']['readiness']}  ⚠:{s['scores']['risk']}")
        print(f"      💬 {s['vote_note']}")
        print(f"      ⚠ {s['criticism']}")
        print()

    top = scores[0]
    if top["blocked_by"]:
        print(f"  ▶ Winner: Phase {top['phase']} (score {top['weighted']}) but blocked by {', '.join(top['blocked_by'])}")
        unblocked = [s for s in scores if not s["blocked_by"]]
        if unblocked:
            u = unblocked[0]
            print(f"  ▶ Best unblocked: Phase {u['phase']} — {u['name']} (score {u['weighted']})")
    else:
        print(f"  ▶ Build now: Phase {top['phase']} — {top['name']} (score {top['weighted']})")
    print()


if __name__ == "__main__":
    main()
