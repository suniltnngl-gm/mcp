#!/usr/bin/env bash
# workspace.sh — Main entry point for ~/Public workspace
# Usage: ./workspace.sh <command> [args...]
set -euo pipefail

BASE="$HOME/Public"

# ── Colors ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# ── Project Detection ──
detect_project() {
  local pwd="$PWD"
  case "$pwd" in
    */Workspace/*)       echo "workspace" ;;
    */project/*)         echo "project" ;;
    */repositories/*)    echo "repositories" ;;
    */.opencode/*)       echo "config" ;;
    */Public)            echo "root" ;;
    *)                   echo "unknown" ;;
  esac
}

PROJECT=$(detect_project)

# ── Helpers ──
info()  { echo -e "${CYAN}$1${NC}"; }
ok()    { echo -e "${GREEN}$1${NC}"; }
warn()  { echo -e "${YELLOW}$1${NC}"; }
err()   { echo -e "${RED}$1${NC}" >&2; }
die()   { err "$1"; exit 1; }

require_cmd() {
  command -v "$1" &>/dev/null || die "Required command not found: $1"
}

# ── Commands ──

cmd_help() {
  cat <<'EOF'
workspace.sh — Main entry point for ~/Public workspace

Usage: ./workspace.sh <command> [args...]

PROJECT COMMANDS
  status              Git status + last 5 commits for current project
  sync                Run workspace sync (project/ only)
  backup              Create timestamped backup (project/ only)
  pre-backup <file>   Snapshot file before editing (project/ only)

SNAPSHOT COMMANDS
  snapshot            Full workspace snapshot (structure + knowledge + prompt)
  prompt              Generate AI onboarding prompt
  structure           Generate directory tree map
  knowledge           Generate workspace knowledge report

ENVIRONMENT COMMANDS
  osenv <args...>     Run osenv CLI (Workspace/ only)
  review-media [dir]  Analyze media files (Workspace/ only)

SETUP COMMANDS
  setup               Run one-shot tool installer (project/ only)
  shell-config        Show shell config helper info

TRACKING COMMANDS
  dashboard           Show DASHBOARD.md
  blockers            Show active blockers from DASHBOARD.md
  integrations        Show integration status from CROSS_PROJECT.md

PLAN COMMANDS (Phase 12 cross-project integrations)
  plan                Show current plan (PLAN.md Phase 12)
  next                Show next unblocked task from plan
  plan-task <n>       Show details for integration #3, #4, or #5 (#1–#4 done, #5 next)

NEXT-STEP COMMANDS (session continuity — requires `next-step` CLI)
  ns <cmd> [args..]   Run next-step command (resume, snapshot, propose, etc.)
  ns-status           Show next-step status + active proposals
  ns-sync             Snapshot current state into next-step registry

MCP COMMANDS (requires project/ MCP servers)
  mcp-list            List available MCP servers and their tools
  mcp-chat <prompt>   Chat via Ollama cloud MCP model (free)
  mcp-status          Check if MCP servers are running

AUTH COMMANDS (requires Firebase service account)
  auth-verify <token> Verify a Firebase ID token
  auth-claims <uid>   Fetch custom claims for a Firebase Auth UID

REVIEW COMMANDS (Phase 13 — automated review cycle)
  review              Run full review cycle (git + tests + tasks)
  review --fast       Run quick review (git only)
  review --scanners git tests   Run specific scanners

AUTO COMMANDS (Phase 15 — auto detect gaps, fix, rebuild KB, plan)
  auto                Run full pipeline: detect gaps → auto-fix → rebuild KB
  auto plan           Detect gaps only (no fixes, no KB rebuild)
  auto status         Show last pipeline run summary
  auto fixable        List categories that can be auto-fixed
  auto --apply        Detect + auto-fix trivial gaps + rebuild KB

AI COMMANDS (Phase 16 — Ollama cloud AI for workspace)
  ai ask <q>          Ask a question to Ollama cloud AI
  ai suggest [n]      Get AI fix suggestion for finding #n
  ai priority         AI prioritizes current findings
  ai explain <gap>    AI explains a gap type
  ai summarize        AI summarizes latest review
  ai answer <q>       AI answers with workspace context

BRAIN COMMANDS (Phase 17 — Perplexity-style self-improving memory)
  brain learn <t> <c>  Log a correction as a reusable lesson
  brain status        Show lesson/suppression stats
  brain graph         Show context graph entries by type
  brain sync          Overnight sync: lessons → context graph
  brain search <q>    Search lessons and context entries
  cron-install        Install 2 AM daily Brain sync via crontab

AUTOKB COMMANDS (Phase 14 — automated cross-repo knowledge base)
  kb-auto scan        Rebuild the knowledge index from all repos
  kb-auto <query>     Search indexed knowledge (fast, ranked)
  kb-auto find <q>    Alias for kb-auto search
  kb-auto <q> --explain Add AI explanation to search results
  kb-auto stats       Show index statistics
  kb-auto --fast <q>  Use ripgrep for precise content search

  Model shortcuts:
    mcp-gpt           Chat with gpt-oss:120b-cloud
    mcp-gemma         Chat with gemma3:12b
    mcp-mini          Chat with ministral-3:8b

KNOWLEDGE BASE COMMANDS
  kb <keyword>        Search knowledge base for keyword
  kb-deep <keyword>   Deep search ALL docs for keyword
  kb-cat <category>   List entries in a category (gotchas, tools, etc.)
  kb-tags             List all searchable tags
  kb-categories       List all KB categories
  kb-stats            Show KB statistics

INFO COMMANDS
  projects            List all projects with status
  scripts             List available scripts for current project
  which               Show detected project

SOFTR COMMANDS (Phase 21 — Softr Studio & Database API)
  softr-list          List accessible Softr databases
  softr-tables <id>   List tables in a database
  softr-query <id>    Query records from a table
  softr-user-create   Create a Softr app user
  softr-user-get      Look up a user by email
  softr-user-delete   Delete a user

REPLIT COMMANDS (Phase 22 — Replit REST API v1)
  replit-repls        List all Repls
  replit-create       Create a new Repl
  replit-deploy       Deploy a Repl to production
  replit-user         Get current Replit user info

SARVAM COMMANDS (via uvx sarvam-mcp — official Sarvam AI MCP server)
  sarvam              Show available sarvam-mcp tools
  sarvam-translate    (use sarvam-mcp translate tool via agent)
  sarvam-doc          (use sarvam-mcp vision tool via agent)

REPO SHORTCUTS
  todo                cd to project/todo-automator/
  devenv              cd to ~/Public/DevEnvSync/
  devflow             cd to ~/Public/devflow-intelligence/
  wiki                cd to ~/Public/devflow-intelligence/wiki/

HELP
  help                Show this help message

EXAMPLES
  ./workspace.sh status
  ./workspace.sh snapshot
  ./workspace.sh osenv audit
  ./workspace.sh backup
  ./workspace.sh dashboard
  ./workspace.sh todo
EOF
}

cmd_which() {
  info "Detected project: $PROJECT"
  info "Working directory: $PWD"
}

cmd_projects() {
  echo ""
  printf "%-20s %-8s %-8s %s\n" "PROJECT" "GIT" "CLEAN" "PRIMARY DOC"
  printf "%-20s %-8s %-8s %s\n" "-------" "---" "-----" "-----------"

  for proj in "Workspace" "project" "repositories" ".opencode" \
              "coding-agent" "next-steps" "shared-tools" "Docs" \
              "todo-automator" "DevEnvSync" "devflow-intelligence" \
              "devflow-intelligence"; do
    if [ -d "$BASE/$proj/.git" ]; then
      git_status="✅"
      clean=$(cd "$BASE/$proj" && git status --short 2>/dev/null | wc -l)
      if [ "$clean" -eq 0 ]; then
        clean_status="✅"
      else
        clean_status="⚠️  $clean"
      fi
    else
      git_status="❌"
      clean_status="—"
    fi

    case "$proj" in
      "Workspace")            doc=".opencode/SUMMARY.md" ;;
      "project")              doc="PLAN.md" ;;
      "repositories")         doc="api_project/CONTINUITY.md" ;;
      ".opencode")            doc="guidelines.md" ;;
      "todo-automator")       doc="ROADMAP_PLAN.md" ;;
      "DevEnvSync")           doc="REFACTOR_PROGRESS.json" ;;
      "devflow-intelligence") doc="README.md" ;;
      "devflow-intelligence") doc="README.md" ;;
      "consolidation")        doc="FINAL_STATUS.md" ;;
      "progressive-build")    doc="FINAL_REPORT.md" ;;
      *)                      doc="—" ;;
    esac

    printf "%-20s %-8s %-8s %s\n" "$proj" "$git_status" "$clean_status" "$doc"
  done
  echo ""
}

cmd_scripts() {
  info "Scripts available for project: $PROJECT"
  echo ""
  case "$PROJECT" in
    root)
      echo "  snapshot.sh              Full workspace snapshot"
      echo ""
      echo "  Subcommands available:"
      echo "    snapshot, prompt, structure, knowledge"
      ;;
    workspace)
      echo "  os-env-manager/osenv.sh  OS environment CLI"
      echo "  os-env-manager/review-media.sh  Media analyzer"
      echo "  scripts/workspace-prompt.sh  AI onboarding prompt"
      echo "  scripts/structure.sh     Directory tree map"
      echo "  knowledge.sh             Workspace knowledge report"
      echo ""
      echo "  Subcommands available:"
      echo "    osenv, review-media, snapshot, prompt, structure, knowledge"
      ;;
    project)
      echo "  workspace_sync.sh        Sync orchestrator"
      echo "  simple_backup.sh         Periodic backup"
      echo "  pre_edit_backup.sh       Pre-edit snapshot"
      echo "  setup-tools.sh           Tool installer"
      echo "  .shell-config.sh         Shell aliases (source)"
      echo "  git-setup.sh             Git helpers (source)"
      echo "  fnm-setup.sh             fnm helpers (source)"
      echo "  uv-setup.sh              uv helpers (source)"
      echo ""
      echo "  MCP servers:"
      echo "    src/llm_wrapper/mcp/ollama_cloud_server.py"
      echo "    src/llm_wrapper/mcp/osenv_server.py"
      echo "    src/llm_wrapper/mcp/cooperative_strategy.py"
      echo ""
      echo "  Subcommands available:"
      echo "    sync, backup, pre-backup, setup"
      echo "    plan, next, plan-task"
      echo "    mcp-list, mcp-status, mcp-chat, mcp-gpt, mcp-gemma, mcp-mini"
      echo "    auth-verify, auth-claims"
      ;;
    repositories)
      echo "  api_project/run.sh       Dropbox API runner"
      echo ""
      echo "  Subcommands available:"
      echo "    (use run.sh directly)"
      ;;
    config)
      echo "  No shell scripts in .opencode/"
      echo "  Use ENTRY.md for session workflow"
      ;;
    *)
      echo "  No scripts detected"
      ;;
  esac
  echo ""
}

cmd_status() {
  local dir=""
  case "$PROJECT" in
    root)        dir="$BASE" ;;
    workspace)   dir="$BASE/Workspace" ;;
    project)     dir="$BASE/project" ;;
    repositories) dir="$BASE/repositories" ;;
    config)      dir="$BASE/.opencode" ;;
    *)           dir="$PWD" ;;
  esac

  info "=== $PROJECT ==="
  echo ""
  cd "$dir"
  echo "Last 5 commits:"
  git log --oneline -5 2>/dev/null || warn "Not a git repo"
  echo ""
  echo "Working tree:"
  git status --short 2>/dev/null || warn "Not a git repo"
}

cmd_snapshot() {
  info "Running full workspace snapshot..."
  bash "$BASE/snapshot.sh"
}

cmd_prompt() {
  bash "$BASE/Workspace/scripts/workspace-prompt.sh" "${1:-$BASE/.workspace-prompt.md}"
  ok "Prompt written to ${1:-$BASE/.workspace-prompt.md}"
}

cmd_structure() {
  bash "$BASE/Workspace/scripts/structure.sh" "${1:-$BASE/structure.log}"
  ok "Structure written to ${1:-$BASE/structure.log}"
}

cmd_knowledge() {
  bash "$BASE/Workspace/knowledge.sh" "${1:-}"
}

cmd_osenv() {
  [ "$PROJECT" = "workspace" ] || die "osenv is available in Workspace/ only"
  bash "$BASE/Workspace/os-env-manager/osenv.sh" "$@"
}

cmd_review_media() {
  [ "$PROJECT" = "workspace" ] || die "review-media is available in Workspace/ only"
  bash "$BASE/Workspace/os-env-manager/review-media.sh" "$@"
}

cmd_sync() {
  [ "$PROJECT" = "project" ] || die "sync is available in project/ only"
  bash "$BASE/project/workspace_sync.sh"
}

cmd_backup() {
  [ "$PROJECT" = "project" ] || die "backup is available in project/ only"
  bash "$BASE/project/simple_backup.sh"
}

cmd_pre_backup() {
  [ "$PROJECT" = "project" ] || die "pre-backup is available in project/ only"
  [ -n "${1:-}" ] || die "Usage: workspace.sh pre-backup <file>"
  bash "$BASE/project/pre_edit_backup.sh" "$1"
}

cmd_setup() {
  [ "$PROJECT" = "project" ] || die "setup is available in project/ only"
  bash "$BASE/project/setup-tools.sh"
}

cmd_shell_config() {
  info ".shell-config.sh — source this to load project aliases"
  echo ""
  echo "  Aliases: py, ptest, pylint, pyformat, pytype, uvupdate, uvinstall"
  echo "  Functions: setup-project, check-python, check-node, check-tools"
  echo ""
  echo "  Usage: source .shell-config.sh"
}

cmd_dashboard() {
  [ -f "$BASE/.opencode/DASHBOARD.md" ] || die "DASHBOARD.md not found"
  cat "$BASE/.opencode/DASHBOARD.md"
}

cmd_blockers() {
  [ -f "$BASE/.opencode/DASHBOARD.md" ] || die "DASHBOARD.md not found"
  sed -n '/## Blockers/,/## /p' "$BASE/.opencode/DASHBOARD.md" | head -n -1
}

cmd_integrations() {
  [ -f "$BASE/.opencode/CROSS_PROJECT.md" ] || die "CROSS_PROJECT.md not found"
  sed -n '/## Integration Points/,/## Quick Reference/p' "$BASE/.opencode/CROSS_PROJECT.md" | head -n -1
}

# ── Plan Commands (Phase 12) ──

cmd_plan() {
  local plan_file="$BASE/project/PLAN.md"
  [ -f "$plan_file" ] || die "PLAN.md not found"
  echo ""
  info "=== Phase 12: Cross-Project Integrations ==="
  echo ""
  sed -n '/### Phase 12:/,/^### /p' "$plan_file" | head -n -1
  echo ""
  info "Full plan: $plan_file"
}

cmd_next() {
  local plan_file="$BASE/project/PLAN.md"
  [ -f "$plan_file" ] || die "PLAN.md not found"
  echo ""
  info "=== Next Unblocked Task ==="
  echo ""
  # Check for pending integrations
  if grep -q "⏳ Pending" "$BASE/.opencode/CROSS_PROJECT.md" 2>/dev/null; then
    local has_5=$(grep -c "| 5 |.*⏳" "$BASE/.opencode/CROSS_PROJECT.md" 2>/dev/null)
    if [ "$has_5" -gt 0 ]; then
      echo "  ✅ Integration #5 (Data Sharing — Firestore) — unblocked, ready to start"
      echo "     Description: Firestore-backed document service for MCP servers"
      echo "     Replaces local SQLite with real-time sync + auth"
      echo ""
    fi
    echo "  ─────────────────────────────────────────────"
    echo "  Run: ./workspace.sh plan          — Show full plan"
    echo "  Run: ./workspace.sh integrations  — Show status table"
  else
    echo "  ✅ All integrations complete!"
  fi
}

cmd_plan_task() {
  local num="${1:-}"
  [ -n "$num" ] || die "Usage: workspace.sh plan-task <3|4|5>"
  case "$num" in
    3) echo "Integration #3: Firebase Auth as MCP Identity"; echo ""; echo "✅ Completed — stateless token verification, 4 error types with JSON contracts"; echo "Location: project/src/llm_wrapper/mcp/firebase_auth_server.py"; echo "Status: completed";;
    4) echo "Integration #4: Shared Tools & Configs"; echo ""; echo "✅ Completed — canonical ruff/mypy/pytest configs + reusable CI workflows"; echo "Location: ~/.opencode/shared/"; echo "Status: completed";;
    5) echo "Integration #5: Data Sharing (Firestore)"; echo ""; echo "Unblocked — Firestore-backed document service for MCP servers"; echo "Replaces local SQLite with real-time sync + auth across projects"; echo "Status: pending (ready to start)";;
    *) echo "Unknown task: $num. Use 3, 4, or 5.";;
  esac
}

cmd_ns() {
  require_cmd "next-step"
  cd "$BASE"
  next-step "$@"
}

cmd_ns_status() {
  require_cmd "next-step"
  cd "$BASE"
  echo "=== Next-Step Status ==="
  next-step status --json 2>/dev/null || next-step status
  echo ""
  echo "=== Active Proposals ==="
  next-step proposals --json 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    proposals = data if isinstance(data, list) else data.get('proposals', [])
    for p in proposals:
        print(f\"  [{p.get('status','?')}] {p.get('action','')[:80]}\")
except: print('  (no proposals or non-JSON output)')
" 2>/dev/null || next-step proposals
}

cmd_ns_sync() {
  require_cmd "next-step"
  cd "$BASE"
  info "Taking next-step snapshot..."
  next-step snapshot
  info "Registering proposals..."
  next-step propose
  ok "Workspace state synced into next-step registry."
}

# ── Review Cycle Commands (Phase 13) ──

cmd_auto() {
  local project_dir="$BASE/project"
  [ -d "$project_dir/autofix" ] || die "autofix/ not found in project/"
  local first="${1:-run}"
  local rest=()
  if [ $# -gt 1 ]; then
    shift
    rest=("$@")
  fi
  case "$first" in
    run|plan|status|fixable)
      uv run --directory "$project_dir" python3 -m autofix "$first" "${rest[@]}"
      ;;
    --apply|-a)
      uv run --directory "$project_dir" python3 -m autofix run --apply "${rest[@]}"
      ;;
    *)
      uv run --directory "$project_dir" python3 -m autofix run "$@"
      ;;
  esac
}

cmd_ai() {
  local project_dir="$BASE/project"
  [ -d "$project_dir/ai_assist" ] || die "ai_assist/ not found in project/"
  local first="${1:-ask}"
  local rest=()
  if [ $# -gt 1 ]; then
    shift
    rest=("$@")
  fi
  case "$first" in
    ask|suggest|priority|explain|summarize|answer)
      uv run --directory "$project_dir" python3 -m ai_assist "$first" "${rest[@]}"
      ;;
    *)
      uv run --directory "$project_dir" python3 -m ai_assist ask "$@"
      ;;
  esac
}

cmd_brain() {
  local project_dir="$BASE/project"
  [ -d "$project_dir/brain" ] || die "brain/ not found in project/"
  local first="${1:-status}"
  local rest=()
  if [ $# -gt 1 ]; then
    shift
    rest=("$@")
  fi
  case "$first" in
    learn|status|graph|sync|search)
      uv run --directory "$project_dir" python3 -m brain "$first" "${rest[@]}"
      ;;
    *)
      uv run --directory "$project_dir" python3 -m brain status "$@"
      ;;
  esac
}

cmd_cron_install() {
  local cron_job="0 2 * * * /home/sunil-kr/Public/project/brain/overnight.sh >> /home/sunil-kr/.opencode/brain/cron.log 2>&1"
  if crontab -l 2>/dev/null | grep -q "brain/overnight"; then
    info "Cron job already installed"
  else
    (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
    info "Installed overnight Brain sync at 2 AM daily"
  fi
}

cmd_review() {
  local project_dir="$BASE/project"
  [ -d "$project_dir/review_cycle" ] || die "review_cycle/ not found in project/"
  info "Running review cycle..."
  if [[ "$*" == *"--fast"* ]]; then
    uv run --directory "$project_dir" python3 -m review_cycle.main --scanners git
  else
    uv run --directory "$project_dir" python3 -m review_cycle.main "$@"
  fi
}

# ── MCP Commands ──

cmd_mcp_list() {
  local project_dir="$BASE/project"
  [ -d "$project_dir" ] || die "project/ directory not found"
  info "MCP servers configured in project/:"
  echo ""
  uv run --directory "$project_dir" python3 -c "
import json, os
mcp_json = os.path.expanduser('$project_dir/mcp.json')
try:
    with open(mcp_json) as f:
        data = json.load(f)
    servers = data.get('mcpServers', {})
    for name, info in servers.items():
        stype = info.get('type', 'unknown')
        print(f'  [{stype}] {name}')
    if not servers:
        print('  (no servers configured)')
except FileNotFoundError:
    print(f'  mcp.json not found at {mcp_json}')
except Exception as e:
    print(f'  Error: {e}')
"
  echo ""
  info "Config file: $BASE/project/mcp.json"
}

cmd_mcp_status() {
  local project_dir="$BASE/project"
  [ -d "$project_dir" ] || die "project/ directory not found"
  local ollama_key="${OLLAMA_API_KEY:-}"
  info "MCP Server Status:"
  echo ""
  echo "  ollama_cloud_server:"
  echo "    OLLAMA_API_KEY: $( [ -n \"$ollama_key\" ] && echo '✅ set' || echo '❌ missing' )"
  echo "    Script: $project_dir/src/llm_wrapper/mcp/ollama_cloud_server.py"
  echo ""
  echo "  osenv_server:"
  echo "    Script: $project_dir/src/llm_wrapper/mcp/osenv_server.py"
  echo "    Deps: osenv modules (Workspace/os-env-manager/)"
  echo ""
  echo "  cooperative_strategy:"
  echo "    Module: $project_dir/src/llm_wrapper/mcp/cooperative_strategy.py"
  echo "    Patterns: parallel, chain, fallback, router"
  echo ""
  # Quick ping test
  if [ -n "$ollama_key" ]; then
    echo "  Testing ollama cloud connection..."
    local req='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"0.1.0","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}'
    local resp=$(echo "$req" | timeout 8 uv run --directory "$project_dir" python3 -m src.llm_wrapper.mcp.ollama_cloud_server 2>/dev/null | head -1)
    if [ -n "$resp" ]; then
      echo "$resp" | python3 -c "
import sys, json
try:
    data = json.loads(sys.stdin.read())
    srv = data.get('result', {}).get('serverInfo', {})
    if srv:
        print(f'    ✅ {srv.get(\"name\",\"?\")} v{srv.get(\"version\",\"?\")}')
    else:
        print('    ❌ Unexpected response format')
except: print('    ❌ Could not parse response')
" 2>/dev/null
    else
      echo '    ❌ Server did not respond'
    fi
  else
    echo "    ⏸️  Skipped (no OLLAMA_API_KEY)"
  fi
}

cmd_mcp_chat() {
  [ -n "${1:-}" ] || die "Usage: workspace.sh mcp-chat <prompt>"
  local ollama_key="${OLLAMA_API_KEY:-}"
  [ -n "$ollama_key" ] || die "OLLAMA_API_KEY not set"
  local model="${2:-ministral-3:8b}"
  local project_dir="$BASE/project"
  info "MCP Chat (model: $model)..."
  echo ""
  local tmp="$(mktemp)"
  cat > "$tmp" << 'EOFSCRIPT'
import os, sys
from ollama import Client
client = Client(host='https://ollama.com', headers={'Authorization': 'Bearer ' + os.environ['OLLAMA_API_KEY']})
response = client.chat(model=sys.argv[1], messages=[{'role': 'user', 'content': sys.argv[2]}])
print(response.message.content)
EOFSCRIPT
  OLLAMA_API_KEY="$ollama_key" uv run --directory "$project_dir" --with ollama python3 "$tmp" "$model" "$1" 2>/dev/null
  rm -f "$tmp"
}

cmd_mcp_gpt() {
  cmd_mcp_chat "${1:-Hello!}" "gpt-oss:120b-cloud"
}

cmd_mcp_gemma() {
  cmd_mcp_chat "${1:-Hello!}" "gemma3:12b"
}

cmd_mcp_mini() {
  cmd_mcp_chat "${1:-Hello!}" "ministral-3:8b"
}

# ── Auth Commands ──

cmd_auth_verify() {
  [ -n "${1:-}" ] || die "Usage: workspace.sh auth-verify <id_token>"
  local project_dir="$BASE/project"
  local req_init='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"0.1.0","capabilities":{},"clientInfo":{"name":"workspace-auth","version":"1"}}}'
  local req_call=$(python3 -c "
import json
print(json.dumps({
    'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call',
    'params': {
        'name': 'verify_auth_token',
        'arguments': {'id_token': '$1'}
    }
}))
")
  {
    echo "$req_init"
    sleep 2
    echo "$req_call"
  } | timeout 15 uv run --directory "$project_dir" python3 -m src.llm_wrapper.mcp.firebase_auth_server 2>/dev/null | \
  python3 -c "
import sys, json
for line in sys.stdin:
    try:
        data = json.loads(line)
        result = data.get('result')
        if result:
            content = result.get('content', [{}])[0].get('text', '')
            success = result.get('success', True)
            if success and content:
                print(json.dumps(json.loads(content), indent=2))
            elif content:
                print(f'Verification failed: {content}')
            break
    except: pass
" 2>/dev/null
}

cmd_auth_claims() {
  [ -n "${1:-}" ] || die "Usage: workspace.sh auth-claims <uid>"
  local project_dir="$BASE/project"
  local req_init='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"0.1.0","capabilities":{},"clientInfo":{"name":"workspace-auth","version":"1"}}}'
  local req_call=$(python3 -c "
import json
print(json.dumps({
    'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call',
    'params': {
        'name': 'get_user_claims',
        'arguments': {'uid': '$1'}
    }
}))
")
  {
    echo "$req_init"
    sleep 2
    echo "$req_call"
  } | timeout 15 uv run --directory "$project_dir" python3 -m src.llm_wrapper.mcp.firebase_auth_server 2>/dev/null | \
  python3 -c "
import sys, json
for line in sys.stdin:
    try:
        data = json.loads(line)
        result = data.get('result')
        if result:
            content = result.get('content', [{}])[0].get('text', '')
            success = result.get('success', True)
            if success and content:
                print(json.dumps(json.loads(content), indent=2))
            elif content:
                print(f'Lookup failed: {content}')
            break
    except: pass
" 2>/dev/null
}

cmd_kb() {
  bash "$BASE/kb.sh" "$@"
}

cmd_kb_auto() {
  local project_dir="$BASE/project"
  [ -d "$project_dir/autokb" ] || die "autokb/ not found in project/"
  local fast=0
  local args=()
  for arg in "$@"; do
    if [ "$arg" = "--fast" ]; then
      fast=1
    else
      args+=("$arg")
    fi
  done
  [ ${#args[@]} -eq 0 ] && args=("search")
  # If first arg isn't a known command, treat as search query
  case "${args[0]}" in
    scan|search|stats) ;;  # known command
    *) args=("search" "${args[@]}") ;;  # prepend search
  esac
  if [ "$fast" -eq 1 ]; then
    uv run --directory "$project_dir" python3 -m autokb search --fast "${args[@]}"
  else
    uv run --directory "$project_dir" python3 -m autokb "${args[@]}"
  fi
}

cmd_kb_deep() {
  bash "$BASE/kb.sh" --all "$@"
}

cmd_kb_cat() {
  bash "$BASE/kb.sh" --category "$@"
}

cmd_kb_tags() {
  bash "$BASE/kb.sh" --tags
}

cmd_kb_categories() {
  bash "$BASE/kb.sh" --categories
}

cmd_kb_stats() {
  bash "$BASE/kb.sh" --stats
}

# ── Repo Shortcuts ──
cmd_todo() {
  cd "$BASE/project/todo-automator" && pwd
}

cmd_devenv() {
  cd "$BASE/DevEnvSync" && pwd
}

cmd_devflow() {
  cd "$BASE/devflow-intelligence" && pwd
}

cmd_wiki() {
  cd "$BASE/devflow-intelligence/wiki" && pwd
}

cmd_softr() {
  uv run --directory "$BASE/project" python3 -c "
from src.llm_wrapper.mcp.softr_server import SoftrServer
import asyncio, json

async def main():
    s = SoftrServer()
    r = await s._list_databases()
    for c in r.content:
        print(c.text if hasattr(c, 'text') else c)
asyncio.run(main())
"
}

cmd_softr_user() {
  echo "Use mcp_softr_manager_* tools via Antigravity agent"
  echo "  softr_create_user, softr_get_user, softr_delete_user"
}

cmd_replit() {
  echo "Use mcp_replit_manager_* tools via Antigravity agent"
  echo "  replit_list_repls, replit_create_repl, replit_deploy_repl, replit_get_user"
}

cmd_sarvam() {
  echo "Use sarvam-mcp (uvx sarvam-mcp) — Sarvam AI MCP server"
  echo "  Tools: translate, transliterate, language (detect), stt, tts,"
  echo "  llm (chat), vision (doc digitization), pronunciation, code"
  echo "  workflows: voice, dub, localize, recall"
}

# ── Main Dispatch ──

COMMAND="${1:-help}"
shift 2>/dev/null || true

case "$COMMAND" in
  help|--help|-h)       cmd_help ;;
  which)                cmd_which ;;
  projects)             cmd_projects ;;
  scripts)              cmd_scripts ;;
  status)               cmd_status ;;
  snapshot)             cmd_snapshot ;;
  prompt)               cmd_prompt "$@" ;;
  structure)            cmd_structure "$@" ;;
  knowledge)            cmd_knowledge "$@" ;;
  osenv)                cmd_osenv "$@" ;;
  review-media)         cmd_review_media "$@" ;;
  sync)                 cmd_sync ;;
  backup)               cmd_backup ;;
  pre-backup)           cmd_pre_backup "$@" ;;
  setup)                cmd_setup ;;
  shell-config)         cmd_shell_config ;;
  dashboard)            cmd_dashboard ;;
  blockers)             cmd_blockers ;;
  integrations)         cmd_integrations ;;
  plan)                 cmd_plan ;;
  next)                 cmd_next ;;
  plan-task)            cmd_plan_task "$@" ;;
  kb)                   cmd_kb "$@" ;;
  kb-deep)              cmd_kb_deep "$@" ;;
  kb-cat)               cmd_kb_cat "$@" ;;
  kb-tags)              cmd_kb_tags ;;
  kb-categories)        cmd_kb_categories ;;
  kb-stats)             cmd_kb_stats ;;
  kb-auto)              cmd_kb_auto "$@" ;;
  kb-find)              cmd_kb_auto "search" "$@" ;;
  ns)                   cmd_ns "$@" ;;
  ns-status)            cmd_ns_status ;;
  ns-sync)            cmd_ns_sync ;;
  review)             cmd_review "$@" ;;
  auto)               cmd_auto "$@" ;;
  ai)                 cmd_ai "$@" ;;
  brain)              cmd_brain "$@" ;;
  cron-install)       cmd_cron_install ;;
  mcp-list)             cmd_mcp_list ;;
  mcp-status)           cmd_mcp_status ;;
  mcp-chat)             cmd_mcp_chat "$@" ;;
  mcp-gpt)              cmd_mcp_gpt "$@" ;;
  mcp-gemma)            cmd_mcp_gemma "$@" ;;
  mcp-mini)             cmd_mcp_mini "$@" ;;
  auth-verify)          cmd_auth_verify "$@" ;;
  auth-claims)          cmd_auth_claims "$@" ;;
  todo)                 cmd_todo ;;
  devenv)               cmd_devenv ;;
  devflow)              cmd_devflow ;;
  wiki)               cmd_wiki ;;
  softr-list)         cmd_softr "list_databases" ;;
  softr-tables)       cmd_softr "list_tables" "$@" ;;
  softr-query)        cmd_softr "query_records" "$@" ;;
  softr-create)       cmd_softr "create_record" "$@" ;;
  softr-user-create)  cmd_softr_user "create" "$@" ;;
  softr-user-get)     cmd_softr_user "get" "$@" ;;
  softr-user-delete)  cmd_softr_user "delete" "$@" ;;
  replit-repls)       cmd_replit "list_repls" ;;
  replit-create)      cmd_replit "create_repl" "$@" ;;
  replit-deploy)      cmd_replit "deploy_repl" "$@" ;;
  replit-user)        cmd_replit "get_user" "$@" ;;
  sarvam)             cmd_sarvam "$@" ;;
  *)
    err "Unknown command: $COMMAND"
    echo ""
    cmd_help
    exit 1
    ;;
esac
