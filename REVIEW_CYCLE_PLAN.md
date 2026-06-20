# Phase 13: Automated Review Cycle

## Goal
Build an automated system that periodically reviews all active repos, plans next actions, and optionally builds suggestions — closing the Plan→Build→Review loop without manual intervention.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TRIGGER LAYER                            │
│  cron (GH Actions)  │  git hook  │  manual  │  watch mode   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    SCAN LAYER                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ git      │ │ test     │ │ task     │ │ doc drift    │   │
│  │ scanner  │ │ runner   │ │ checker  │ │ detector     │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    REVIEW LAYER                             │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │ score &    │  │ compare to │  │ classify issues      │  │
│  │ prioritize │  │ baseline   │  │ (blocker/risk/chore) │  │
│  └────────────┘  └────────────┘  └──────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    PLAN LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ generate     │  │ AI discuss   │  │ select & order   │  │
│  │ proposals    │  │ & refine     │  │ next actions     │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    BUILD LAYER (optional)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ auto-fix     │  │ create PR    │  │ approval gate    │  │
│  │ known issues │  │ with diff    │  │ before apply     │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    OUTPUT LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ review       │  │ GH issue /   │  │ notification     │  │
│  │ report .md   │  │ PR body      │  │ (log file)       │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Trigger Layer
| Trigger | Implementation | Use Case |
|---------|---------------|----------|
| GitHub Actions schedule | `.github/workflows/review.yml` with `cron: '0 6 * * *'` | Daily 6am review |
| Git pre-push hook | `.git/hooks/pre-push` that runs quick scan | Catch issues before push |
| Manual | `./workspace.sh review` | On-demand review |
| Watch mode | `./workspace.sh review --watch 30` | Poll every 30 min during dev |

### 2. Scan Layer — Scanners

Each scanner produces a `ScanFinding`:

```python
@dataclass
class ScanFinding:
    repo: str                      # e.g. "project/"
    category: str                  # "git_dirty", "test_failure", "task_stale", "doc_drift"
    severity: str                  # "blocker", "critical", "warning", "info"
    summary: str                   # "3 uncommitted files in project/"
    detail: str                    # "Modified: src/foo.py, src/bar.py"
    file_path: Optional[str]       # specific file if applicable
    suggested_action: str          # "Commit these changes"
    score: float                   # 0.0–1.0 priority score
    timestamp: str                 # ISO 8601
```

| Scanner | Checks | Produces |
|---------|--------|----------|
| `git_scanner` | All 8 active repos for dirty state, unpushed commits, branch drift | Findings per repo |
| `test_runner` | Run `pytest` in project/, check test results | Pass/fail counts, failures |
| `task_checker` | Compare PLAN.md tasks against actual file state | Stale tasks, unblocked items |
| `doc_drift_detector` | Check if tracking docs match reality | Outdated entries |
| `dependency_scanner` | Check uv.lock, package.json for outdated deps | Outdated packages |
| `disk_scanner` | Check disk usage, large files, temp artifacts | Space warnings |

### 3. Review Layer

```python
@dataclass
class ReviewReport:
    timestamp: str
    findings: List[ScanFinding]
    summary: ReviewSummary
    baseline: Optional[str]        # previous report hash for diff

@dataclass
class ReviewSummary:
    total_findings: int
    blockers: int
    critical: int
    warnings: int
    infos: int
    score: float                   # 0.0–100.0 workspace health score
    trend: str                     # "improving", "stable", "declining"
```

**Scoring formula:**
```
health_score = 100
  - (blockers × 10)
  - (critical × 5)
  - (warnings × 2)
  - (infos × 0.5)
clamped to [0, 100]
```

### 4. Plan Layer

Reuses and extends `next-steps` infrastructure:

- `next-step review` → generate proposals from findings
- `next-step discuss` → AI multi-agent debate on top proposals
- Output: ordered list of proposed actions with rationales

When no AI key is available, falls back to rule-based prioritization:
```
priority = severity_weight × category_weight × recency_bonus
```

### 5. Build Layer (Auto-fix)

Auto-applies fixes for well-known patterns:

| Pattern | Auto-fix |
|---------|----------|
| Stale `Status: pending` with all subtasks done | Set to `completed` |
| Missing `.env.example` when `.env` exists | Generate from `.env` keys (values redacted) |
| Orphaned `node_modules` in non-node repos | Add to `.gitignore` |
| Outdated tracking doc entries | Patch from canonical source |

Non-trivial changes go through **approval gate**: creates a branch + PR instead of committing directly.

### 6. Output Layer

| Output | Location | Format |
|--------|----------|--------|
| Review report | `~/.opencode/reviews/<date>.md` | Markdown with findings table |
| GitHub Issue | Created in project/ repo | Structured issue body |
| Notification file | `~/.opencode/reviews/latest.json` | JSON for external consumption |
| Dashboard badge | `~/.opencode/DASHBOARD.md` | Health score line |

## Implementation Plan

### Phase 13.1: Foundation (build, ~2h)
- [ ] Create `scan_finding.py` — `ScanFinding` and `ReviewReport` dataclasses
- [ ] Build `git_scanner.py` — check 8 repos for dirty state, unpushed commits
- [ ] Build `test_runner.py` — run pytest, parse results
- [ ] Build `task_checker.py` — compare PLAN.md tasks vs file system
- [ ] Add `review` command to `workspace.sh` (manual trigger)

### Phase 13.2: Review Engine (plan+build, ~2h)
- [ ] Build scoring/prioritization module
- [ ] Add baseline comparison (diff from previous run)
- [ ] Generate markdown report
- [ ] Wire into next-steps proposal generation

### Phase 13.3: Automation (build, ~1.5h)
- [ ] Create `review.yml` GitHub Actions workflow (daily cron)
- [ ] Add watch mode to `workspace.sh review`
- [ ] Add pre-push hook support
- [ ] Notification file output

### Phase 13.4: Auto-fix & PR (build, ~2h)
- [ ] Implement auto-fix patterns (stale tasks, missing docs, gitignore)
- [ ] Add approval gate (branch + PR for non-trivial changes)
- [ ] Create PR generation module
- [ ] Wire into cooperative strategy (RouterStrategy routes auto-fix decisions)

### Phase 13.5: Scoring & Trends (build, ~1h)
- [ ] Track health score over time
- [ ] Trend detection (improving/stable/declining)
- [ ] Dashboard badge in DASHBOARD.md

## Dependencies
| Component | Depends On |
|-----------|-----------|
| Phase 13.1 | next-steps scanning infrastructure |
| Phase 13.2 | 13.1 (needs scanners to exist) |
| Phase 13.3 | 13.2 (needs review engine) |
| Phase 13.4 | 13.1 (auto-fix targets scanner findings) |
| Phase 13.5 | 13.2 (needs baseline comparison) |

## Future Possibilities
- **Web dashboard**: Render health trends with charts
- **Slack/email notifications**: Send weekly digests
- **Auto-update PLAN.md**: Mark stale tasks complete
- **Cross-repo PRs**: Fix issues across all 8 repos at once
- **AI-generated summaries**: LLM summarizes weekly trends
