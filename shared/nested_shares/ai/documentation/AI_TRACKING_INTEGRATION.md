# AI Tracking Integration

Complete integration of session and action tracking across AI orchestration tools.

## Overview

All AI tools now include built-in tracking for:
- **Session Tracking**: User requests, AI thinking, actions, and summaries
- **Action Tracking**: AI operations with costs, performance, and outcomes

## Integrated Tools

### 1. Discussion Manager (`discussion_manager.py`)
**Tracking**: Session + Action

**What's Tracked**:
- Discussion creation (session start/complete)
- AI participant messages (action log)
- Provider, tokens, latency per message
- Discussion context (topic, participants, message count)

**Usage**:
```python
from discussion_manager import DiscussionManager

# Tracking enabled by default
manager = DiscussionManager(enable_tracking=True)

# Create discussion - automatically tracked
disc_id = manager.create_discussion(
    topic="Architecture decision",
    participants=["architect-ai", "cost-optimizer-ai"]
)

# Add message - AI messages tracked
manager.add_message(disc_id, "architect-ai", "My recommendation...")
```

**Logs**:
- `session_history.jsonl`: Discussion creation sessions
- `ai_action_history.jsonl`: AI participant messages

### 2. AI Orchestra (`ai_orchestra.py`)
**Tracking**: Session + Action

**What's Tracked**:
- Orchestration start/completion (session)
- Multi-agent collaboration (action)
- Agents count, iterations, latency
- Recommendations generated

**Usage**:
```python
from ai_orchestra import AIOrchestra

# Tracking enabled by default
orchestra = AIOrchestra(enable_tracking=True)

# Analyze scenario - automatically tracked
results = orchestra.analyze_scenario(
    scenario="Production issue...",
    iterations=2
)
```

**Logs**:
- `session_history.jsonl`: Orchestration sessions
- `ai_action_history.jsonl`: Multi-agent actions

### 3. Unified Review (`unified_review.py`)
**Tracking**: Session + Action

**What's Tracked**:
- Review sessions (directory scans)
- Individual file reviews (actions)
- File info, findings count, latency
- Success/failure status

**Usage**:
```python
from unified_review import UnifiedReview

# Tracking enabled by default
reviewer = UnifiedReview(enable_tracking=True)

# Review file - automatically tracked
findings = reviewer.review_file(Path("myfile.py"))

# Review directory - session + actions tracked
results = reviewer.review_directory(Path("./src"))
```

**Logs**:
- `session_history.jsonl`: Review sessions
- `ai_action_history.jsonl`: File review actions

## Tracking Files

### Session History (`session_history.jsonl`)
Tracks complete user workflows:
```json
{
  "session_id": "20251210-035749",
  "timestamp": "2025-12-10T03:57:49.123456",
  "user_request": "Review code quality",
  "ai_thinking": "Planning analysis strategy...",
  "actions": [
    {
      "purpose": "Scan directory",
      "action": "Found 15 files",
      "result": "Ready to review",
      "cost": 0.0
    }
  ],
  "completion_summary": "Reviewed 15 files, found 23 issues",
  "cost": 0.05,
  "duration": 12.34
}
```

### AI Action History (`ai_action_history.jsonl`)
Tracks individual AI operations:
```json
{
  "id": "20251210-035749-123456",
  "timestamp": "2025-12-10T03:57:49.123456",
  "action_type": "review",
  "provider": "gpt-4",
  "model": "code-review",
  "input_tokens": 1500,
  "output_tokens": 300,
  "cost": 0.045,
  "latency": 2.3,
  "success": true,
  "context": {
    "file": "myfile.py",
    "lines": 150,
    "findings": 5
  },
  "result": "Found 5 issues"
}
```

## Manual Tracking

For custom workflows:

```python
from session_tracker import SessionTracker
from ai_action_tracker import AIActionTracker

# Initialize
session = SessionTracker("session_history.jsonl")
action = AIActionTracker("ai_action_history.jsonl")

# Start session
session_id = session.start_session("Custom workflow")
session.add_thinking("Planning approach...")

# Log AI action
action_id = action.log_action(
    action_type="custom",
    provider="gpt-4",
    model="gpt-4-turbo",
    input_tokens=100,
    output_tokens=50,
    cost=0.003,
    latency=1.5,
    success=True,
    context={"task": "analysis"},
    result="Completed successfully"
)

# Add to session
session.add_action(
    purpose="AI analysis",
    action="Custom task",
    result="Success",
    cost=0.003
)

# Complete
session.complete_session("Workflow completed")
```

## Benefits

### Cost Tracking
- Monitor AI usage costs per tool
- Identify expensive operations
- Optimize provider selection

### Performance Monitoring
- Track latency per operation
- Identify bottlenecks
- Optimize workflows

### Pattern Analysis
- Analyze common workflows
- Identify optimization opportunities
- Learn from usage patterns

### Debugging
- Full context for issues
- Trace AI decisions
- Reproduce problems

## Example Script

Run the integration example:
```bash
cd shared-tools/nested-shares/ai/orchestration
python3 tracking_integration_example.py
```

This demonstrates:
1. Code review with tracking
2. Manual session tracking
3. Discussion manager tracking
4. AI orchestra tracking
5. Viewing tracking history

## Files Modified

1. **discussion_manager.py**
   - Added session_tracker and ai_action_tracker imports
   - Integrated tracking in `__init__`, `create_discussion`, `add_message`
   - Tracks discussion creation and AI participant messages

2. **ai_orchestra.py**
   - Added tracking imports
   - Integrated tracking in `AIOrchestra.__init__` and `analyze_scenario`
   - Tracks orchestration sessions and multi-agent actions

3. **unified_review.py** (NEW)
   - Created with built-in tracking
   - Tracks review sessions and file review actions
   - Includes mock AI review for demonstration

4. **tracking_integration_example.py** (NEW)
   - Comprehensive examples of all tracking features
   - 5 examples covering all use cases
   - Demonstrates both automatic and manual tracking

## Configuration

### Enable/Disable Tracking

All tools support tracking control:
```python
# Enable (default)
tool = Tool(enable_tracking=True)

# Disable
tool = Tool(enable_tracking=False)
```

### Custom Log Files

```python
# Custom paths
session = SessionTracker("custom/path/sessions.jsonl")
action = AIActionTracker("custom/path/actions.jsonl")
```

## Next Steps

1. **Cost Analysis Tool**: Analyze tracking data for cost insights
2. **Performance Dashboard**: Visualize latency and performance
3. **Pattern Analyzer**: Identify optimization opportunities
4. **Real AI Integration**: Replace mock reviews with actual AI calls
5. **Alerting**: Monitor for expensive or slow operations

## Status

✅ **COMPLETE** - All tracking integration tasks finished:
- [x] Add tracking to discussion_manager.py
- [x] Add tracking to ai_orchestra.py
- [x] Add tracking to unified_review.py
- [x] Create integration example script
- [x] Update documentation

## Location

```
shared-tools/nested-shares/ai/
├── discussions/
│   └── discussion_manager.py (tracking integrated)
├── orchestration/
│   ├── session_tracker.py
│   ├── ai_action_tracker.py
│   ├── ai_orchestra.py (tracking integrated)
│   ├── unified_review.py (NEW, with tracking)
│   ├── tracking_integration_example.py (NEW)
│   ├── session_history.jsonl (generated)
│   └── ai_action_history.jsonl (generated)
└── AI_TRACKING_INTEGRATION.md (this file)
```
