# Agent Log

## Overview
This document systematically records all significant actions, decisions, and their rationale (why, what, how, when) taken by the agent during project development. The log provides a complete audit trail for all agent activities.

## Logging System

### 1. Log Structure
Each log entry follows this format:

```json
{
  "timestamp": "2026-06-12T14:30:45.123Z",
  "session_id": "session-uuid",
  "agent_id": "antigravity-agent-v1",
  "action": "action_description",
  "context": {
    "file": "path/to/file.py",
    "line": 42,
    "stack_trace": "optional_stack_trace"
  },
  "decision": {
    "rationale": "Why this action was taken",
    "alternatives_considered": ["option1", "option2"],
    "impact": "Expected impact"
  },
  "result": {
    "success": true,
    "output": "brief_description_of_output",
    "side_effects": []
  },
  "metadata": {
    "triggered_by": "user_request|system_event|automated_task",
    "priority": "high|medium|low",
    "category": "file_operation|analysis|execution|planning"
  }
}
```

### 2. Log Categories

#### File Operations
- File reads
- File writes
- File modifications
- File deletions

#### Analysis Operations
- Code analysis
- Pattern recognition
- Dependency analysis
- Architecture decisions

#### Execution Operations
- Tool executions
- Command runs
- API calls
- Database operations

#### Planning Operations
- Task planning
- Strategy decisions
- Resource allocation
- Timeline estimation

## Log Format

### Plain Text Format
For human-readable logs:

```
[2026-06-12 14:30:45] [SESSION-12345] [AGENT] [FILE_OP] 
Action: Reading file /home/sunil-kr/Public/project/PLAN.md
Rationale: User requested project overview
Decision: Open and analyze project structure
Result: Success - 190 lines, 4 sections
Side effects: None
Priority: Medium
```

### Structured Format
For machine-readable logs:

```json
{
  "timestamp": "2026-06-12T14:30:45.123Z",
  "session_id": "session-12345",
  "level": "INFO",
  "category": "file_operation",
  "action": "read_file",
  "target": "/home/sunil-kr/Public/project/PLAN.md",
  "rationale": "User requested project overview",
  "decision": {
    "choice": "open_and_analyze",
    "alternatives": ["provide_summary", "list_contents", "analyze_structure"],
    "criteria": ["comprehensive", "user_friendly", "actionable"]
  },
  "result": {
    "status": "success",
    "output": "Extracted project goal, roadmap, assumptions",
    "impact": "Grounded agent understanding"
  },
  "metadata": {
    "source": "user_request",
    "urgency": "normal",
    "requires_followup": false
  }
}
```

## Log Rotation

### 1. Rotation Policy
- Rotate daily based on timestamp
- Keep last 30 days of logs
- Compress old logs to save space
- Maintain separate files for different log levels

### 2. Naming Convention
```
agent_log_2026-06-12.jsonl
agent_log_2026-06-13.jsonl
agent_log_2026-06-14.jsonl
```

### 3. Compression
```bash
# Compress logs older than 7 days
find /path/to/logs -name "agent_log_*.jsonl" -mtime +7 -exec gzip {} \;
```

## Log Analysis

### 1. Key Metrics
- Action frequency by category
- Average execution time per action
- Success rate by tool
- Decision patterns
- Resource usage

### 2. Search Capabilities
- Filter by date range
- Filter by action type
- Filter by result status
- Filter by impact level

## Integration with ERROR_REGISTRY.md

### 1. Cross-Reference
Each error log entry should reference the corresponding log entry:

```json
{
  "error_id": "ERR-001",
  "timestamp": "2026-06-01T20:15:30.456Z",
  "action_reference": "2026-06-01T20:14:20.789Z",
  "action": "create_venv",
  "problem": "python3 -m venv failed",
  "resolution": "Switched to uv venv",
  "impact": "User intervention required"
}
```

### 2. Log Entry Template
```python
def log_action(action, context, decision, result):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": current_session_id,
        "agent_id": "antigravity-agent-v1",
        "action": action,
        "context": context,
        "decision": decision,
        "result": result,
        "metadata": {
            "triggered_by": "user|system|auto",
            "priority": "high|medium|low",
            "category": "file|analysis|execution|planning"
        }
    }
    
    # Write to log file
    with open(f"agent_log_{datetime.now().strftime('%Y-%m-%d')}.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    # Also check if error occurred
    if not result["success"]:
        record_error(log_entry)
    
    return log_entry
```

## Log Consumption

### 1. Manual Review
View recent logs:
```bash
# Show last 10 entries
tail -10 agent_log_*.jsonl

# Filter by action type
grep -i "file_operation" agent_log_*.jsonl | tail -20

# Filter by date
cat agent_log_2026-06-12.jsonl
grep "success.*false" agent_log_*.jsonl
```

### 2. Automated Analysis
Parse logs for insights:

```python
import json
from collections import defaultdict
from datetime import datetime

class LogAnalyzer:
    def __init__(self, log_dir):
        self.log_dir = log_dir
        self.logs = []
    
    def load_logs(self, days=1):
        cutoff = datetime.now() - timedelta(days=days)
        for filename in os.listdir(self.log_dir):
            if filename.startswith("agent_log_") and filename.endswith(".jsonl"):
                date_str = filename.replace("agent_log_", "").replace(".jsonl", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if file_date >= cutoff:
                    with open(os.path.join(self.log_dir, filename), "r") as f:
                        for line in f:
                            self.logs.append(json.loads(line))
    
    def get_action_frequency(self):
        frequency = defaultdict(int)
        for log in self.logs:
            frequency[log["category"]] += 1
        return dict(frequency)
    
    def get_success_rate(self):
        successful = sum(1 for log in self.logs if log["result"]["success"])
        return successful / len(self.logs) if self.logs else 0
```

## Monitoring and Alerting

### 1. Alert Conditions
- Error rate > 20%
- Repeated failed actions
- Long-running operations
- Resource exhaustion

### 2. Alert Format
```json
{
  "alert_type": "HIGH_ERROR_RATE",
  "timestamp": "2026-06-12T15:30:00.000Z",
  "severity": "HIGH",
  "message": "Error rate exceeded 20% threshold (23%)",
  "action": "Review recent agent logs and investigate failed operations",
  "threshold": 0.20
}
```

## Security Considerations

### 1. Access Control
- Restrict log file permissions to agent user only
- Use encryption for sensitive log entries
- Implement audit trail for log access

### 2. Log Sanitization
- Remove sensitive data before logging
- Mask passwords, tokens, API keys
- Hash personally identifiable information

## Future Enhancements

### 1. Real-time Monitoring
- Implement log streaming for real-time monitoring
- Add WebSocket support for live log viewing
- Create dashboard for log visualization

### 2. AI-Powered Analysis
- Use ML models to detect anomalies
- Predict likely errors based on patterns
- Recommend optimizations based on log data

### 3. Integration
- Connect with monitoring systems (Prometheus, Grafana)
- Export logs to SIEM systems
- Integrate with issue tracking systems

## Maintenance

### 1. Regular Cleanup
```bash
# Remove old logs
find /path/to/logs -name "agent_log_*.jsonl.gz" -mtime +90 -delete

# Compress large files
find /path/to/logs -name "agent_log_*.jsonl" -size +100M -exec gzip {} \;
```

### 2. Log Health Check
```python
def check_log_health():
    # Check for corrupt files
    for log_file in get_log_files():
        try:
            with open(log_file, "r") as f:
                for line in f:
                    json.loads(line)  # Validate JSON
        except json.JSONDecodeError:
            raise LogError(f"Corrupt log file: {log_file}")
    
    # Check for missing dates
    # ... implementation
```

## API for External Tools

### 1. Query Logs
```
GET /api/logs?action=read_file&from=2026-06-12T00:00:00Z&to=2026-06-13T00:00:00Z
```

### 2. Search Logs
```
GET /api/logs/search?query=file_operation&target=PROJECT.md
```

### 3. Get Statistics
```
GET /api/logs/stats?period=daily
```

This comprehensive logging system provides full visibility into agent operations while maintaining security and performance.