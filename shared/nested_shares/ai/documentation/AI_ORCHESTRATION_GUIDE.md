# AI Orchestration Workflows Guide

Complete guide for using the 16 AI orchestration tools in nested-shares/ai/

## Overview

**16 AI tools** organized in **5 subcategories**:
- orchestration/ (3 tools)
- providers/ (4 tools)
- context/ (3 tools)
- config/ (2 tools)
- learning/ (3 tools)

## Quick Start

```bash
# Access AI tools
cd shared-tools/nested-shares/ai/

# Use quick access script
./use_ai_tools.sh list
./use_ai_tools.sh orchestrate
```

## 1. Orchestration (3 tools)

### ai_orchestra.py - Core Orchestration Engine
**Purpose**: Main AI orchestration and coordination

```python
from ai.orchestration import ai_orchestra

# Initialize orchestra
orchestra = ai_orchestra.Orchestra()

# Coordinate multiple AI tasks
result = orchestra.coordinate([
    {'task': 'analyze', 'input': 'code.py'},
    {'task': 'suggest', 'input': 'improvements'}
])
```

**Use cases:**
- Multi-step AI workflows
- Task coordination
- Result aggregation

### enhanced_orchestra.py - Enhanced Features
**Purpose**: Advanced orchestration with additional features

```python
from ai.orchestration import enhanced_orchestra

# Enhanced orchestration
enhanced = enhanced_orchestra.EnhancedOrchestra()

# With caching and optimization
result = enhanced.execute_optimized(tasks, cache=True)
```

**Use cases:**
- Performance optimization
- Caching strategies
- Advanced workflows

### orchestra_cli.py - CLI Interface
**Purpose**: Command-line interface for orchestration

```bash
# Run orchestration from CLI
python3 orchestration/orchestra_cli.py --task analyze --input file.py

# Interactive mode
python3 orchestration/orchestra_cli.py --interactive
```

**Use cases:**
- Scripting and automation
- CI/CD integration
- Quick testing

## 2. Providers (4 tools)

### providers.py - Multi-Provider Support
**Purpose**: Manage multiple AI providers (OpenAI, Anthropic, Gemini, etc.)

```python
from ai.providers import providers

# Initialize providers
provider_manager = providers.ProviderManager()

# Use specific provider
response = provider_manager.complete('openai', prompt="Explain AI")

# Auto-select best provider
response = provider_manager.auto_complete(prompt="Explain AI")
```

**Supported providers:**
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- And more...

### load_balancer.py - Load Balancing
**Purpose**: Distribute requests across providers

```python
from ai.providers import load_balancer

# Initialize load balancer
balancer = load_balancer.LoadBalancer(['openai', 'anthropic', 'gemini'])

# Automatic load balancing
response = balancer.complete("Complex query")
```

**Features:**
- Round-robin distribution
- Failover support
- Rate limit handling

### health_monitor.py - Provider Health
**Purpose**: Monitor provider availability and performance

```bash
# Check all providers
python3 providers/health_monitor.py --check-all

# Monitor continuously
python3 providers/health_monitor.py --monitor --interval 60

# Get status report
python3 providers/health_monitor.py --report
```

**Monitors:**
- API availability
- Response times
- Error rates
- Rate limits

### providers_alt.py - Alternative Configurations
**Purpose**: Alternative provider configurations

```python
from ai.providers import providers_alt

# Use alternative config
alt_provider = providers_alt.AlternativeProvider()
```

## 3. Context Management (3 tools)

### auto_context_manager.py - Automatic Context
**Purpose**: Automatically manage conversation context

```python
from ai.context import auto_context_manager

# Initialize context manager
context_mgr = auto_context_manager.ContextManager()

# Automatic context tracking
context_mgr.add_message("user", "Hello")
context_mgr.add_message("assistant", "Hi there!")

# Get optimized context
context = context_mgr.get_context(max_tokens=4000)
```

**Features:**
- Automatic context pruning
- Token limit management
- Conversation history

### context_reset_mitigation.py - Reset Prevention
**Purpose**: Prevent context resets and maintain continuity

```python
from ai.context import context_reset_mitigation

# Initialize mitigation
mitigator = context_reset_mitigation.ResetMitigator()

# Detect potential resets
if mitigator.detect_reset(response):
    mitigator.recover_context()
```

**Prevents:**
- Context loss
- Conversation breaks
- State inconsistencies

### universal_context_guard.py - Context Protection
**Purpose**: Universal context protection across providers

```python
from ai.context import universal_context_guard

# Initialize guard
guard = universal_context_guard.ContextGuard()

# Protected execution
with guard.protect():
    response = provider.complete(prompt)
```

**Protects:**
- Context integrity
- State consistency
- Error recovery

## 4. Configuration (2 tools)

### ai_autoconfig.py - Auto Configuration
**Purpose**: Automatic AI configuration and setup

```bash
# Auto-configure AI tools
python3 config/ai_autoconfig.py --setup

# Detect and configure providers
python3 config/ai_autoconfig.py --detect-providers

# Validate configuration
python3 config/ai_autoconfig.py --validate
```

**Configures:**
- API keys
- Provider settings
- Default parameters
- Environment variables

### auto_restructure.py - Code Restructuring
**Purpose**: Automatic code restructuring with AI

```python
from ai.config import auto_restructure

# Initialize restructurer
restructurer = auto_restructure.AutoRestructure()

# Restructure code
new_code = restructurer.restructure_file("legacy_code.py")
```

**Features:**
- AI-powered refactoring
- Code modernization
- Pattern detection

## 5. Learning & Intelligence (3 tools)

### feedback_learning_engine.py - Feedback Learning
**Purpose**: Learn from user feedback and improve

```python
from ai.learning import feedback_learning_engine

# Initialize learning engine
learner = feedback_learning_engine.FeedbackLearner()

# Record feedback
learner.record_feedback(
    prompt="Original prompt",
    response="AI response",
    rating=4,
    comments="Good but could be better"
)

# Apply learning
learner.apply_learning()
```

**Learns from:**
- User ratings
- Corrections
- Preferences
- Patterns

### strategic_expansion_manager.py - Strategic Growth
**Purpose**: Manage strategic AI expansion and capabilities

```python
from ai.learning import strategic_expansion_manager

# Initialize manager
manager = strategic_expansion_manager.ExpansionManager()

# Analyze expansion opportunities
opportunities = manager.analyze_opportunities()

# Execute expansion
manager.expand_capabilities(opportunities)
```

**Manages:**
- Capability expansion
- Provider addition
- Feature growth
- Strategic planning

### data_persistence.py - Data Persistence
**Purpose**: Persist AI data, context, and learning

```python
from ai.learning import data_persistence

# Initialize persistence
persistence = data_persistence.DataPersistence()

# Save context
persistence.save_context(context_id, context_data)

# Load context
context = persistence.load_context(context_id)

# Save learning data
persistence.save_learning(learning_data)
```

**Persists:**
- Conversation history
- Learning data
- User preferences
- Configuration

## Common Workflows

### Workflow 1: Basic AI Request
```python
from ai.providers import providers
from ai.context import auto_context_manager

# Setup
provider = providers.ProviderManager()
context = auto_context_manager.ContextManager()

# Execute
context.add_message("user", "Explain quantum computing")
response = provider.complete("openai", context.get_context())
context.add_message("assistant", response)
```

### Workflow 2: Load-Balanced Multi-Provider
```python
from ai.providers import load_balancer
from ai.providers import health_monitor

# Check health
monitor = health_monitor.HealthMonitor()
healthy_providers = monitor.get_healthy_providers()

# Load balance
balancer = load_balancer.LoadBalancer(healthy_providers)
response = balancer.complete("Complex query")
```

### Workflow 3: Orchestrated Multi-Step
```python
from ai.orchestration import ai_orchestra
from ai.context import universal_context_guard

# Setup
orchestra = ai_orchestra.Orchestra()
guard = universal_context_guard.ContextGuard()

# Execute with protection
with guard.protect():
    result = orchestra.coordinate([
        {'task': 'analyze', 'input': 'data.csv'},
        {'task': 'summarize', 'input': 'analysis'},
        {'task': 'recommend', 'input': 'summary'}
    ])
```

### Workflow 4: Learning from Feedback
```python
from ai.providers import providers
from ai.learning import feedback_learning_engine

# Execute and learn
provider = providers.ProviderManager()
learner = feedback_learning_engine.FeedbackLearner()

response = provider.complete("openai", prompt)
learner.record_feedback(prompt, response, rating=5)
learner.apply_learning()
```

## Best Practices

1. **Always check provider health** before heavy usage
2. **Use context management** for long conversations
3. **Enable load balancing** for reliability
4. **Record feedback** to improve over time
5. **Persist important data** for recovery
6. **Use orchestration** for complex workflows
7. **Auto-configure** for easy setup

## Troubleshooting

### Provider Issues
```bash
# Check provider health
python3 providers/health_monitor.py --check-all

# Validate configuration
python3 config/ai_autoconfig.py --validate
```

### Context Issues
```python
# Reset context if needed
context_mgr.reset()

# Use context guard for protection
with guard.protect():
    # Your code here
```

### Performance Issues
```python
# Use load balancer
balancer = load_balancer.LoadBalancer(providers)

# Enable caching
enhanced.execute_optimized(tasks, cache=True)
```

## Quick Reference

| Tool | Category | Purpose | Usage |
|------|----------|---------|-------|
| ai_orchestra.py | Orchestration | Core coordination | Python API |
| enhanced_orchestra.py | Orchestration | Advanced features | Python API |
| orchestra_cli.py | Orchestration | CLI interface | Bash |
| providers.py | Providers | Multi-provider | Python API |
| load_balancer.py | Providers | Load balancing | Python API |
| health_monitor.py | Providers | Health checks | Bash/Python |
| providers_alt.py | Providers | Alt configs | Python API |
| auto_context_manager.py | Context | Auto context | Python API |
| context_reset_mitigation.py | Context | Reset prevention | Python API |
| universal_context_guard.py | Context | Protection | Python API |
| ai_autoconfig.py | Config | Auto setup | Bash |
| auto_restructure.py | Config | Code refactor | Python API |
| feedback_learning_engine.py | Learning | Feedback | Python API |
| strategic_expansion_manager.py | Learning | Growth | Python API |
| data_persistence.py | Learning | Persistence | Python API |

---

**Total Tools**: 16
**Categories**: 5
**Last Updated**: December 2025
