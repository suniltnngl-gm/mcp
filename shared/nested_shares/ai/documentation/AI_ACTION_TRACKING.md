# Smart AI Action History Tracking

## Problem

No visibility into:
- What AI actions were performed
- How much they cost
- Which providers were used
- Success/failure rates
- Performance patterns

## Solution: AI Action Tracker

**File**: `orchestration/ai_action_tracker.py`

Tracks every AI action with:
- Cost and token usage
- Provider and model
- Latency and success rate
- Context and results
- Errors and failures

## Features

### 1. Action Logging
```python
from ai.orchestration import ai_action_tracker

tracker = ai_action_tracker.AIActionTracker()

# Log an action
action_id = tracker.log_action(
    action_type='query',
    provider='openrouter-free',
    model='mistral-7b',
    input_tokens=500,
    output_tokens=200,
    cost=0.0,
    latency=0.3,
    success=True,
    context={'task': 'code review', 'file': 'main.py'},
    result='No issues found'
)
```

### 2. Statistics
```bash
# Today's stats
python3 ai_action_tracker.py stats today

# Output:
# Total actions: 45
# Total cost: $0.23
# Total tokens: 12,500
# Avg latency: 0.8s
# Success rate: 95.6%
# By type: {'query': 30, 'discussion': 10, 'review': 5}
# By provider: {'openrouter-free': 25, 'gemini-flash': 15, 'gpt-4': 5}
```

### 3. Timeline
```bash
# Last 24 hours
python3 ai_action_tracker.py timeline 24

# Output:
# 2025-12-09T08: 5 actions, $0.02, 1,200 tokens
# 2025-12-09T09: 12 actions, $0.08, 3,400 tokens
# 2025-12-09T10: 8 actions, $0.05, 2,100 tokens
```

### 4. Cost Analysis
```bash
# Most expensive actions
python3 ai_action_tracker.py expensive 10

# Output:
# $0.15 - code_gen via gpt-4 (2025-12-09T10:23:45)
# $0.08 - discussion via claude-sonnet (2025-12-09T09:15:22)
# $0.05 - review via gemini-flash (2025-12-09T08:45:10)
```

### 5. Performance Analysis
```bash
# Slowest actions
python3 ai_action_tracker.py slow 10

# Output:
# 3.2s - code_gen via gpt-4 (2025-12-09T10:23:45)
# 1.8s - discussion via claude-sonnet (2025-12-09T09:15:22)
# 0.9s - review via gemini-flash (2025-12-09T08:45:10)
```

### 6. Failure Tracking
```bash
# Recent failures
python3 ai_action_tracker.py failures 20

# Output:
# 2025-12-09T11:30:15 - query via gpt-4
#   Error: Rate limit exceeded
# 
# 2025-12-09T10:45:30 - discussion via claude-sonnet
#   Error: Timeout after 30s
```

### 7. Comprehensive Report
```bash
# Export full report
python3 ai_action_tracker.py report ai_report.json

# Includes:
# - Stats (today, week, all-time)
# - Timeline (24h)
# - Top expensive actions
# - Top slow actions
# - Recent failures
```

## Data Structure

### Action Record (JSONL)
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
  "context": {
    "task": "code review",
    "file": "main.py",
    "complexity": "simple"
  },
  "result": "No issues found",
  "error": null
}
```

## Integration

### With Smart AI Router
```python
from ai.orchestration import smart_ai_router, ai_action_tracker

router = smart_ai_router.SmartAIRouter()
tracker = ai_action_tracker.AIActionTracker()

# Select provider
provider, reason = router.select_provider('simple')

# Make AI call
start = time.time()
try:
    response = call_ai(provider, prompt)
    latency = time.time() - start
    
    # Log action
    tracker.log_action(
        action_type='query',
        provider=provider,
        model=get_model(provider),
        input_tokens=count_tokens(prompt),
        output_tokens=count_tokens(response),
        cost=router.estimate_cost(provider, input_tokens, output_tokens),
        latency=latency,
        success=True,
        context={'complexity': 'simple'},
        result=response
    )
except Exception as e:
    latency = time.time() - start
    tracker.log_action(
        action_type='query',
        provider=provider,
        model=get_model(provider),
        input_tokens=count_tokens(prompt),
        output_tokens=0,
        cost=0,
        latency=latency,
        success=False,
        context={'complexity': 'simple'},
        error=str(e)
    )
```

### With Discussion System
```python
from ai.discussions import discussion_manager
from ai.orchestration import ai_action_tracker

manager = discussion_manager.DiscussionManager()
tracker = ai_action_tracker.AIActionTracker()

# Create discussion
disc_id = manager.create_discussion("Topic", ["ai1", "ai2"])

# Each AI contribution is tracked
for participant in ["ai1", "ai2"]:
    prompt = manager.get_participant_prompt(disc_id, participant)
    
    start = time.time()
    response = call_ai(provider, prompt)
    latency = time.time() - start
    
    # Log action
    tracker.log_action(
        action_type='discussion',
        provider=provider,
        model=get_model(provider),
        input_tokens=count_tokens(prompt),
        output_tokens=count_tokens(response),
        cost=estimate_cost(provider, input_tokens, output_tokens),
        latency=latency,
        success=True,
        context={'discussion_id': disc_id, 'participant': participant},
        result=response
    )
    
    manager.add_message(disc_id, participant, response)
```

## Use Cases

### 1. Cost Monitoring
Track daily/weekly/monthly AI spending:
```bash
python3 ai_action_tracker.py stats today
python3 ai_action_tracker.py stats week
python3 ai_action_tracker.py stats month
```

### 2. Performance Optimization
Identify slow providers/models:
```bash
python3 ai_action_tracker.py slow 20
# Switch away from slow providers
```

### 3. Reliability Tracking
Monitor failure rates:
```bash
python3 ai_action_tracker.py failures 50
# Identify problematic providers
```

### 4. Usage Patterns
Understand AI usage:
```bash
python3 ai_action_tracker.py timeline 168  # Last week
# See peak usage times
```

### 5. Budget Alerts
Check if approaching budget:
```python
stats = tracker.get_stats('today')
if stats['total_cost'] > 0.80:  # 80% of $1 budget
    print("⚠️  Approaching daily budget!")
```

### 6. Provider Comparison
Compare provider performance:
```python
actions = tracker.get_actions(limit=1000)
by_provider = {}

for action in actions:
    if action.provider not in by_provider:
        by_provider[action.provider] = {
            'count': 0, 'cost': 0, 'latency': [], 'success': 0
        }
    
    by_provider[action.provider]['count'] += 1
    by_provider[action.provider]['cost'] += action.cost
    by_provider[action.provider]['latency'].append(action.latency)
    if action.success:
        by_provider[action.provider]['success'] += 1

# Analyze which provider is best
```

## Storage

**Format**: JSONL (JSON Lines)
- One action per line
- Append-only (fast writes)
- Easy to parse
- Grep-friendly

**File**: `ai_action_history.jsonl`

**Size**: ~500 bytes per action
- 1,000 actions = ~500KB
- 10,000 actions = ~5MB
- 100,000 actions = ~50MB

**Rotation**: Optional
```bash
# Archive old history
mv ai_action_history.jsonl ai_action_history_2025-12.jsonl
```

## Dashboard (Future)

Web dashboard showing:
- Real-time action stream
- Cost graphs (daily/weekly/monthly)
- Provider comparison charts
- Success rate trends
- Latency heatmaps
- Budget progress bars

## Benefits

1. **Cost Visibility**: Know exactly what AI costs
2. **Performance Tracking**: Identify slow operations
3. **Reliability Monitoring**: Track failures
4. **Usage Patterns**: Understand AI utilization
5. **Budget Management**: Stay within limits
6. **Provider Comparison**: Choose best providers
7. **Audit Trail**: Complete history of AI actions

## Commands Summary

```bash
# Statistics
python3 ai_action_tracker.py stats [today|week|month|all]

# Timeline
python3 ai_action_tracker.py timeline [hours]

# Cost analysis
python3 ai_action_tracker.py expensive [limit]

# Performance analysis
python3 ai_action_tracker.py slow [limit]

# Failure tracking
python3 ai_action_tracker.py failures [limit]

# Export report
python3 ai_action_tracker.py report [output_file]
```

## Next Steps

1. ✅ Create ai_action_tracker.py
2. ⏳ Integrate with smart_ai_router
3. ⏳ Integrate with discussion_manager
4. ⏳ Add to ai_orchestra
5. ⏳ Create dashboard (optional)

---

**Status**: Core tracker complete
**Storage**: JSONL (append-only)
**Overhead**: Minimal (~1ms per action)
**Value**: Complete AI action visibility
