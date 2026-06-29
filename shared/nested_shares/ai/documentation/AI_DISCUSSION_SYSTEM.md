# AI Discussion System - Unlocked Conversations

**Problem**: AI conversations are locked to single sessions. No way to have persistent, multi-session discussions where multiple AIs can contribute asynchronously.

**Solution**: Discussion threads with persistent state, multiple AI participants, and cross-session continuity.

## Architecture

### 1. Discussion Thread Storage

```json
{
  "discussion_id": "arch-decision-001",
  "topic": "Should we use microservices or monolith?",
  "created": "2025-12-09T20:00:00Z",
  "status": "active",
  "participants": ["architect-ai", "cost-optimizer-ai", "devops-ai"],
  "context": {
    "workspace": "/user-projects",
    "related_files": ["src/main.py", "docs/architecture.md"],
    "tags": ["architecture", "decision", "high-priority"]
  },
  "messages": [
    {
      "id": "msg-001",
      "participant": "architect-ai",
      "timestamp": "2025-12-09T20:00:00Z",
      "content": "Analyzing current codebase...",
      "references": ["src/main.py:100-150"],
      "sentiment": "analytical"
    },
    {
      "id": "msg-002",
      "participant": "cost-optimizer-ai",
      "timestamp": "2025-12-09T20:05:00Z",
      "content": "Microservices would increase costs by 40%...",
      "references": ["cost_analysis.json"],
      "sentiment": "cautious"
    }
  ],
  "decisions": [],
  "action_items": []
}
```

### 2. AI Participant Profiles

```json
{
  "architect-ai": {
    "role": "Software Architect",
    "expertise": ["system design", "scalability", "patterns"],
    "provider": "gpt-4",
    "personality": "analytical, thorough, considers trade-offs"
  },
  "cost-optimizer-ai": {
    "role": "Cost Analyst",
    "expertise": ["cloud costs", "optimization", "budgeting"],
    "provider": "gemini-flash",
    "personality": "pragmatic, data-driven, budget-conscious"
  },
  "devops-ai": {
    "role": "DevOps Engineer",
    "expertise": ["deployment", "monitoring", "reliability"],
    "provider": "claude-haiku",
    "personality": "practical, operations-focused, risk-aware"
  }
}
```

### 3. Discussion Manager

```python
class DiscussionManager:
    """Manage persistent AI discussions"""
    
    def create_discussion(self, topic, participants, context):
        """Start new discussion thread"""
        
    def add_message(self, discussion_id, participant, content):
        """AI adds message to discussion"""
        
    def get_context(self, discussion_id):
        """Get full discussion context for AI"""
        
    def resume_discussion(self, discussion_id):
        """Resume discussion in new session"""
        
    def invite_participant(self, discussion_id, participant):
        """Add new AI to discussion"""
        
    def reach_consensus(self, discussion_id):
        """Analyze if consensus reached"""
        
    def extract_decisions(self, discussion_id):
        """Extract actionable decisions"""
```

## Use Cases

### Use Case 1: Architecture Decision
```bash
# Start discussion
python3 ai_discussion.py create \
  --topic "Microservices vs Monolith" \
  --participants architect-ai,cost-optimizer-ai,devops-ai \
  --context workspace=/user-projects

# Each AI contributes (can be hours/days apart)
python3 ai_discussion.py contribute arch-decision-001 architect-ai
python3 ai_discussion.py contribute arch-decision-001 cost-optimizer-ai
python3 ai_discussion.py contribute arch-decision-001 devops-ai

# Check consensus
python3 ai_discussion.py consensus arch-decision-001

# Extract decision
python3 ai_discussion.py decide arch-decision-001
```

### Use Case 2: Code Review Discussion
```bash
# Create review discussion
python3 ai_discussion.py create \
  --topic "Review PR #123" \
  --participants security-ai,performance-ai,style-ai \
  --context file=src/new_feature.py

# AIs review asynchronously
python3 ai_discussion.py contribute code-review-123 security-ai
# Output: "Found potential SQL injection on line 45..."

python3 ai_discussion.py contribute code-review-123 performance-ai
# Output: "N+1 query detected, suggest eager loading..."

# Get summary
python3 ai_discussion.py summary code-review-123
```

### Use Case 3: Ongoing Workspace Optimization
```bash
# Long-running discussion
python3 ai_discussion.py create \
  --topic "Workspace Optimization Strategy" \
  --participants optimizer-ai,organizer-ai,automation-ai \
  --context workspace=/user-projects \
  --duration ongoing

# Daily contributions
0 9 * * * python3 ai_discussion.py daily-update workspace-opt-001

# Weekly summaries
0 9 * * 1 python3 ai_discussion.py weekly-summary workspace-opt-001
```

## Key Features

### 1. Persistent State
- Discussions stored in JSON files
- Can be resumed anytime
- Full history preserved
- Context maintained

### 2. Asynchronous Participation
- AIs contribute when invoked
- No need for all participants online
- Can span hours, days, weeks
- Each AI reads full history before contributing

### 3. Multi-Provider Support
- Different AIs use different providers
- Cost-optimized per participant role
- Fallback if provider unavailable

### 4. Context Awareness
- Links to workspace files
- References code/docs
- Tracks related discussions
- Maintains topic focus

### 5. Decision Extraction
- Identifies consensus
- Extracts action items
- Tracks decisions made
- Links to implementation

## Implementation

### File Structure
```
ai/discussions/
├── discussion_manager.py      # Core manager
├── participants.json          # AI participant profiles
├── threads/                   # Discussion storage
│   ├── arch-decision-001.json
│   ├── code-review-123.json
│   └── workspace-opt-001.json
├── templates/                 # Discussion templates
│   ├── architecture.json
│   ├── code-review.json
│   └── optimization.json
└── summaries/                 # Generated summaries
    └── weekly/
```

### Core Components

**1. Discussion Thread** (`discussion_thread.py`)
```python
class DiscussionThread:
    def __init__(self, topic, participants, context):
        self.id = generate_id()
        self.topic = topic
        self.participants = participants
        self.context = context
        self.messages = []
        self.status = 'active'
    
    def add_message(self, participant, content):
        """Add message from AI participant"""
        
    def get_full_context(self):
        """Get complete discussion for AI"""
        
    def check_consensus(self):
        """Analyze if consensus reached"""
```

**2. AI Participant** (`ai_participant.py`)
```python
class AIParticipant:
    def __init__(self, name, role, provider):
        self.name = name
        self.role = role
        self.provider = provider
    
    def contribute(self, discussion):
        """Read discussion and contribute"""
        context = discussion.get_full_context()
        prompt = self._build_prompt(context)
        response = self._call_provider(prompt)
        discussion.add_message(self.name, response)
    
    def _build_prompt(self, context):
        """Build prompt with role and discussion context"""
        return f"""
        You are {self.role}.
        
        Discussion Topic: {context['topic']}
        
        Previous Messages:
        {context['messages']}
        
        Your expertise: {self.expertise}
        
        Provide your perspective on this topic.
        """
```

**3. Consensus Analyzer** (`consensus_analyzer.py`)
```python
class ConsensusAnalyzer:
    def analyze(self, discussion):
        """Determine if consensus reached"""
        messages = discussion.messages
        
        # Use AI to analyze agreement
        prompt = f"""
        Analyze these AI perspectives and determine:
        1. Is there consensus?
        2. What is agreed upon?
        3. What are remaining disagreements?
        
        Messages: {messages}
        """
        
        analysis = call_ai(prompt)
        return analysis
```

## Advanced Features

### 1. Discussion Branching
```python
# Create branch for alternative approach
python3 ai_discussion.py branch arch-decision-001 \
  --topic "Alternative: Serverless approach" \
  --participants architect-ai,cost-optimizer-ai
```

### 2. Cross-Discussion References
```python
# Reference another discussion
discussion.add_reference("See arch-decision-001 for context")
```

### 3. Human Participation
```python
# Human adds input
python3 ai_discussion.py add-human-input arch-decision-001 \
  --content "Budget constraint: max $500/month"
```

### 4. Discussion Templates
```json
{
  "template": "architecture-decision",
  "required_participants": ["architect-ai", "cost-optimizer-ai"],
  "optional_participants": ["security-ai", "devops-ai"],
  "phases": [
    "problem-analysis",
    "solution-proposals",
    "trade-off-analysis",
    "decision"
  ],
  "decision_criteria": ["cost", "scalability", "maintainability"]
}
```

### 5. Automated Facilitation
```python
class DiscussionFacilitator:
    """AI that guides discussion"""
    
    def facilitate(self, discussion):
        """Guide discussion to conclusion"""
        
        # Check if all participants contributed
        # Identify missing perspectives
        # Ask clarifying questions
        # Summarize progress
        # Prompt for decisions
```

## Integration with Workspace

### 1. File Registry Discussions
```bash
# Discuss file organization
python3 ai_discussion.py create \
  --topic "Optimize file registry structure" \
  --participants organizer-ai,performance-ai \
  --context registry=file_registry.json
```

### 2. Code Review Discussions
```bash
# Multi-AI code review
python3 ai_discussion.py create \
  --topic "Review smart_ai_router.py" \
  --participants security-ai,performance-ai,style-ai \
  --context file=smart_ai_router.py
```

### 3. Automation Strategy Discussions
```bash
# Long-term automation planning
python3 ai_discussion.py create \
  --topic "Workspace automation roadmap" \
  --participants automation-ai,efficiency-ai,cost-ai \
  --duration ongoing
```

## Benefits

### vs. Single-Session Conversations
- ✅ Persistent across sessions
- ✅ Multiple AI perspectives
- ✅ Asynchronous contributions
- ✅ Decision tracking
- ✅ Context preservation

### vs. Manual Coordination
- ✅ Automated facilitation
- ✅ Consensus detection
- ✅ Action item extraction
- ✅ Cost-optimized per role

### vs. Human-Only Discussions
- ✅ 24/7 availability
- ✅ Instant expertise access
- ✅ Consistent analysis
- ✅ Documented reasoning

## Cost Optimization

### Provider Selection by Role
- **Architect AI**: gpt-4 (needs deep reasoning)
- **Cost Optimizer AI**: gemini-flash (data analysis)
- **DevOps AI**: claude-haiku (practical advice)
- **Style Checker AI**: openrouter-free (simple rules)

### Estimated Costs
- Architecture discussion (3 AIs, 5 rounds): **$0.50**
- Code review (3 AIs, 2 rounds): **$0.15**
- Daily optimization check (2 AIs, 1 round): **$0.05**

**Monthly**: ~$5-10 for active workspace discussions

## Example: Complete Architecture Discussion

```bash
# Day 1: Start discussion
$ python3 ai_discussion.py create \
  --topic "Migrate to microservices?" \
  --participants architect-ai,cost-optimizer-ai,devops-ai

Discussion created: arch-decision-001

# Day 1: Architect contributes
$ python3 ai_discussion.py contribute arch-decision-001 architect-ai

architect-ai: "Analyzed codebase. Current monolith has 3 clear domains:
- User management (high traffic)
- Payment processing (security critical)
- Analytics (batch processing)

Recommendation: Extract payment processing first (security isolation).
Keep others in monolith initially."

# Day 2: Cost optimizer contributes
$ python3 ai_discussion.py contribute arch-decision-001 cost-optimizer-ai

cost-optimizer-ai: "Cost analysis:
- Current: $200/month (single server)
- Microservices: $450/month (3 services + orchestration)
- Hybrid (payment only): $280/month

Recommendation: Hybrid approach saves $170/month vs full microservices."

# Day 3: DevOps contributes
$ python3 ai_discussion.py contribute arch-decision-001 devops-ai

devops-ai: "Operational considerations:
- Deployment complexity increases 3x
- Monitoring needs: distributed tracing
- Network latency: service-to-service calls

Recommendation: Start with payment service extraction. Proven patterns exist."

# Day 4: Check consensus
$ python3 ai_discussion.py consensus arch-decision-001

Consensus reached: 3/3 participants agree
Decision: Extract payment service to microservice, keep rest as monolith

Action items:
1. Design payment service API
2. Set up service infrastructure
3. Implement distributed tracing
4. Plan gradual migration

# Extract decision document
$ python3 ai_discussion.py export arch-decision-001 --format markdown

# Output: docs/decisions/arch-decision-001.md
```

## Next Steps

1. **Build core system** (discussion_manager.py)
2. **Define participant profiles** (participants.json)
3. **Create CLI interface** (ai_discussion.py)
4. **Integrate with smart_ai_router** (cost optimization)
5. **Add to AI orchestration guide**

---

**Status**: Design complete, ready for implementation
**Estimated effort**: 8-10 hours
**Cost impact**: +$5-10/month for active discussions
**Value**: Persistent AI collaboration across sessions
