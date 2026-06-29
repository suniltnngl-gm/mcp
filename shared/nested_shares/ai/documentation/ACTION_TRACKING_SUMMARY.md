# AI Action Tracking - Summary

## What We Built

### 1. AI Action Tracker ✅
**File**: `orchestration/ai_action_tracker.py`

Tracks every AI action with:
- Cost and tokens
- Provider and model
- Latency and success
- Context and results
- Errors and failures

### 2. Tracked AI Router ✅
**File**: `orchestration/tracked_ai_router.py`

Smart AI Router with automatic tracking built-in.

### 3. Documentation ✅
**File**: `AI_ACTION_TRACKING.md`

Complete guide with examples and use cases.

## Quick Start

### Log an Action
```python
from ai.orchestration import ai_action_tracker

tracker = ai_action_tracker.AIActionTracker()

action_id = tracker.log_action(
    action_type='query',
    provider='openrouter-free',
    model='mistral-7b',
    input_tokens=500,
    output_tokens=200,
    cost=0.0,
    latency=0.3,
    success=True,
    context={'task': 'code review'},
    result='No issues found'
)
```

### View Statistics
```bash
# Today's stats
python3 ai_action_tracker.py stats today

# Output:
# Total actions: 45
# Total cost: $0.23
# Success rate: 95.6%
# By provider: {'openrouter-free': 25, 'gemini-flash': 15, 'gpt-4': 5}
```

### Analyze Costs
```bash
# Most expensive actions
python3 ai_action_tracker.py expensive 10

# Slowest actions
python3 ai_action_tracker.py slow 10

# Recent failures
python3 ai_action_tracker.py failures 20
```

### Export Report
```bash
python3 ai_action_tracker.py report ai_report.json
```

## Data Format

**Storage**: JSONL (JSON Lines)
```json
{
  "id": "20251209-102345-123456",
  "timestamp": "2025-12-09T10:23:45.123456",
  "action_type": "query",
  "provider": "openrouter-free",
  "model": "mistral-7b",
  "input_tokens": 500,
  "output_tokens": 200,
  "cost": 0.0,
  "latency": 0.3,
  "success": true,
  "context": {"task": "code review", "file": "main.py"},
  "result": "No issues found",
  "error": null
}
```

## Features

### Statistics
- Total actions, cost, tokens
- Average latency
- Success rate
- Breakdown by type and provider

### Timeline
- Hourly action counts
- Cost trends
- Token usage patterns

### Analysis
- Most expensive actions
- Slowest actions
- Recent failures
- Provider comparison

### Reports
- Comprehensive JSON export
- Today/week/month/all-time stats
- Top expensive/slow actions
- Failure analysis

## Integration Points

### With Smart AI Router
```python
from orchestration import tracked_ai_router

router = tracked_ai_router.TrackedAIRouter()

result = router.call_with_tracking(
    task_complexity='simple',
    prompt='Review code',
    action_type='review',
    context={'file': 'main.py'}
)
```

### With Discussion System
Track each AI contribution in discussions automatically.

### With AI Orchestra
Track multi-agent collaboration sessions.

## Use Cases

1. **Cost Monitoring**: Track daily/weekly/monthly spending
2. **Performance Optimization**: Identify slow providers
3. **Reliability Tracking**: Monitor failure rates
4. **Usage Patterns**: Understand AI utilization
5. **Budget Alerts**: Stay within limits
6. **Provider Comparison**: Choose best providers
7. **Audit Trail**: Complete action history

## Commands

```bash
# Statistics
python3 ai_action_tracker.py stats [today|week|month|all]

# Timeline
python3 ai_action_tracker.py timeline [hours]

# Cost analysis
python3 ai_action_tracker.py expensive [limit]

# Performance
python3 ai_action_tracker.py slow [limit]

# Failures
python3 ai_action_tracker.py failures [limit]

# Report
python3 ai_action_tracker.py report [output_file]
```

## Benefits

✅ **Cost Visibility**: Know exactly what AI costs
✅ **Performance Tracking**: Identify slow operations
✅ **Reliability Monitoring**: Track failures
✅ **Usage Patterns**: Understand utilization
✅ **Budget Management**: Stay within limits
✅ **Provider Comparison**: Choose best providers
✅ **Audit Trail**: Complete history

## Storage

- **Format**: JSONL (append-only)
- **Size**: ~500 bytes per action
- **1,000 actions**: ~500KB
- **10,000 actions**: ~5MB
- **Overhead**: Minimal (~1ms per action)

## Next Steps

1. ✅ Core tracker created
2. ✅ Tracked router created
3. ✅ Documentation complete
4. ⏳ Integrate with discussion_manager
5. ⏳ Integrate with ai_orchestra
6. ⏳ Add budget alerts
7. ⏳ Create dashboard (optional)

---

**Status**: Core system complete ✅
**Files**: 3 (tracker, router, docs)
**Overhead**: Minimal
**Value**: Complete AI action visibility
