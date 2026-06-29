# AI Tools Quick Reference

## Quick Access

```bash
cd shared-tools/nested-shares/ai/
./use_ai_tools.sh list
```

## 16 Tools in 5 Categories

### 🎼 Orchestration (3)
- `ai_orchestra.py` - Core orchestration
- `enhanced_orchestra.py` - Advanced features
- `orchestra_cli.py` - CLI interface

### 🔌 Providers (4)
- `providers.py` - Multi-provider support
- `load_balancer.py` - Load balancing
- `health_monitor.py` - Health monitoring
- `providers_alt.py` - Alternative configs

### 🧠 Context (3)
- `auto_context_manager.py` - Auto context
- `context_reset_mitigation.py` - Reset prevention
- `universal_context_guard.py` - Protection

### ⚙️ Config (2)
- `ai_autoconfig.py` - Auto configuration
- `auto_restructure.py` - Code restructuring

### 📚 Learning (3)
- `feedback_learning_engine.py` - Feedback learning
- `strategic_expansion_manager.py` - Strategic growth
- `data_persistence.py` - Data persistence

## Common Commands

```bash
# Check provider health
python3 providers/health_monitor.py --check-all

# Auto-configure
python3 config/ai_autoconfig.py --setup

# Run orchestration
python3 orchestration/orchestra_cli.py --task analyze

# Use quick access
./use_ai_tools.sh orchestrate
./use_ai_tools.sh health
```

## Python Quick Start

```python
# Basic usage
from ai.providers import providers
provider = providers.ProviderManager()
response = provider.complete('openai', "Your prompt")

# With load balancing
from ai.providers import load_balancer
balancer = load_balancer.LoadBalancer(['openai', 'anthropic'])
response = balancer.complete("Your prompt")

# With context
from ai.context import auto_context_manager
context = auto_context_manager.ContextManager()
context.add_message("user", "Hello")
```

See `AI_ORCHESTRATION_GUIDE.md` for complete documentation.
