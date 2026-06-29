# AI Tracking Quick Reference

## Quick Start

### Use Tracking-Enabled Tools
```python
# Discussion Manager
from discussion_manager import DiscussionManager
manager = DiscussionManager()  # tracking enabled by default
disc_id = manager.create_discussion("Topic", ["ai1", "ai2"])

# AI Orchestra
from ai_orchestra import AIOrchestra
orchestra = AIOrchestra()  # tracking enabled by default
results = orchestra.analyze_scenario("Scenario")

# Unified Review
from unified_review import UnifiedReview
reviewer = UnifiedReview()  # tracking enabled by default
findings = reviewer.review_file(Path("file.py"))
```

### Manual Tracking
```python
from session_tracker import SessionTracker
from ai_action_tracker import AIActionTracker

# Start session
session = SessionTracker()
session.start_session("My task")
session.add_thinking("Planning...")
session.add_action("Step 1", "action", "result", cost=0.01)
session.complete_session("Done")

# Log AI action
action = AIActionTracker()
action.log_action(
    action_type="query",
    provider="gpt-4",
    model="gpt-4-turbo",
    input_tokens=100,
    output_tokens=50,
    cost=0.003,
    latency=1.5,
    success=True,
    context={"task": "analysis"},
    result="Success"
)
```

## Tracking Files

### session_history.jsonl
User workflows with actions and costs

### ai_action_history.jsonl
Individual AI operations with performance

## View History

```bash
# View sessions
cat session_history.jsonl | jq .

# View actions
cat ai_action_history.jsonl | jq .

# Count sessions
wc -l session_history.jsonl

# Count actions
wc -l ai_action_history.jsonl
```

## Run Example

```bash
cd shared-tools/nested-shares/ai/orchestration
python3 tracking_integration_example.py
```

## Disable Tracking

```python
tool = Tool(enable_tracking=False)
```

## Files

- `session_tracker.py` - Session tracking
- `ai_action_tracker.py` - Action tracking
- `discussion_manager.py` - With tracking
- `ai_orchestra.py` - With tracking
- `unified_review.py` - With tracking
- `tracking_integration_example.py` - Examples
- `AI_TRACKING_INTEGRATION.md` - Full docs
- `AI_TRACKING_COMPLETE.md` - Summary
