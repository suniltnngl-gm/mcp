#!/usr/bin/env bash
# Overnight Brain sync — run via cron at 2 AM daily.
# Adds to crontab:  crontab -e
#   0 2 * * * /home/sunil-kr/Public/project/brain/overnight.sh >> /home/sunil-kr/.opencode/brain/cron.log 2>&1

set -euo pipefail
BASE="/home/sunil-kr/Public"
export OLLAMA_API_KEY="${OLLAMA_API_KEY:-$(grep OLLAMA_API_KEY "$BASE/ENV/.env" 2>/dev/null | cut -d= -f2- | tr -d ' "')}"

cd "$BASE/project"

echo "=== Brain overnight sync: $(date) ==="

# Step 1: Run review cycle
uv run python3 -m review_cycle.main 2>&1 | tail -3

# Step 2: Run auto pipeline (plan only, no apply)
uv run python3 -m autofix run 2>&1 | grep -E '(Brain|AI|Score|Findings|suppressed)'

# Step 3: Brain overnight sync
uv run python3 -m brain sync 2>&1

# Step 4: AI summary
if [ -n "$OLLAMA_API_KEY" ]; then
    uv run python3 -m ai_assist summarize 2>&1
fi

echo "=== Complete: $(date) ==="
