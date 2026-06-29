# Local AI Integration - Offload Tasks from Cloud Providers

## Available: Ollama Support ✅

Your workspace already has Ollama support in `providers.py`:
- Cost: $0 (completely free)
- Max tokens: 8,192
- Response time: ~8s (hardware dependent)
- Strengths: Code review, simple queries, local privacy

## Setup Ollama

### 1. Install Ollama
```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Or download from https://ollama.com
```

### 2. Pull Models
```bash
# Fast, small model (1.5GB)
ollama pull mistral:7b

# Better quality (4GB)
ollama pull llama3:8b

# Code-focused (4GB)
ollama pull codellama:7b

# Tiny, very fast (500MB)
ollama pull phi:2.7b
```

### 3. Test
```bash
ollama run mistral "Hello, test"
```

## Integration with Smart AI Router

Update `smart_ai_router.py` to include Ollama:

```python
PROVIDERS = {
    'ollama-mistral': ProviderCost('ollama-mistral', 0.0, 0.0, 100, 8000, 'basic'),
    'ollama-llama3': ProviderCost('ollama-llama3', 0.0, 0.0, 100, 8000, 'standard'),
    'ollama-codellama': ProviderCost('ollama-codellama', 0.0, 0.0, 100, 8000, 'standard'),
    'openrouter-free': ProviderCost('openrouter-free', 0.0, 0.0, 20, 8000, 'basic'),
    'gemini-flash': ProviderCost('gemini-flash', 0.075, 0.30, 60, 32000, 'standard'),
    # ... rest
}
```

## Task Offloading Strategy

### Offload to Local (Ollama)

**Simple Tasks** (Use Ollama):
- Code formatting
- Simple code review
- Documentation generation
- Basic Q&A
- File analysis
- Syntax checking

**Benefits**:
- $0 cost
- No rate limits
- Privacy (data stays local)
- Works offline

### Keep on Cloud

**Complex Tasks** (Use Cloud):
- Architecture decisions
- Complex refactoring
- Multi-file analysis
- Strategic planning
- Advanced reasoning

**Why**:
- Better quality
- Larger context windows
- Faster for complex tasks

## Cost Comparison

### Current (All Cloud)
- 100 simple queries/day: $0.50/day
- Monthly: $15

### With Ollama Offload
- 80 simple → Ollama: $0
- 20 complex → Cloud: $0.10/day
- Monthly: $3

**Savings**: 80% ($12/month)

## Integration with Kiro

### 1. Kiro Uses Smart Router
```python
from ai.orchestration import smart_ai_router

router = smart_ai_router.SmartAIRouter()

# For simple task, router selects Ollama
provider, reason = router.select_provider('simple')
# Returns: 'ollama-mistral' (free, local)

# For complex task, router selects cloud
provider, reason = router.select_provider('complex')
# Returns: 'gpt-4' or 'claude-sonnet'
```

### 2. Automatic Fallback
If Ollama is down/slow:
```python
fallbacks = router.get_fallback_chain('ollama-mistral')
# Returns: ['openrouter-free', 'gemini-flash', ...]
```

### 3. Track Usage
```python
from ai.orchestration import ai_tracker

tracker = ai_tracker.AITracker()

tracker.action(
    purpose="Code review",
    action="Reviewed main.py with Ollama",
    result="No issues found",
    cost=0.0,  # Free!
    tokens=500,
    latency=3.2
)
```

## Ollama API Usage

### Direct Call
```python
import requests

def call_ollama(prompt: str, model: str = "mistral"):
    response = requests.post('http://localhost:11434/api/generate', json={
        'model': model,
        'prompt': prompt,
        'stream': False
    })
    return response.json()['response']

# Use it
result = call_ollama("Review this code: def add(a, b): return a + b")
```

### With Streaming
```python
def call_ollama_stream(prompt: str, model: str = "mistral"):
    response = requests.post('http://localhost:11434/api/generate', 
        json={'model': model, 'prompt': prompt, 'stream': True},
        stream=True
    )
    
    for line in response.iter_lines():
        if line:
            chunk = json.loads(line)
            if not chunk.get('done'):
                yield chunk['response']
```

## Recommended Models

### For Code Tasks
- **codellama:7b** - Best for code
- **mistral:7b** - Fast, good quality
- **phi:2.7b** - Very fast, smaller

### For General Tasks
- **llama3:8b** - Best quality
- **mistral:7b** - Good balance
- **phi:2.7b** - Speed priority

### For Chat/Q&A
- **llama3:8b** - Best conversation
- **mistral:7b** - Good responses

## Performance Tips

### 1. Keep Model Loaded
```bash
# Pre-load model (stays in memory)
ollama run mistral ""
```

### 2. Use Smaller Models for Simple Tasks
- phi:2.7b for formatting, simple checks
- mistral:7b for code review
- llama3:8b for complex analysis

### 3. Batch Similar Requests
Process multiple files in one session to keep model warm.

## Integration Example

```python
from ai.orchestration import smart_ai_router, ai_tracker
import requests

class LocalAIRouter(smart_ai_router.SmartAIRouter):
    """Router with Ollama support"""
    
    def call_ollama(self, prompt: str, model: str = "mistral"):
        """Call local Ollama"""
        try:
            response = requests.post('http://localhost:11434/api/generate', 
                json={'model': model, 'prompt': prompt, 'stream': False},
                timeout=30
            )
            return response.json()['response']
        except Exception as e:
            print(f"Ollama failed: {e}, falling back to cloud")
            return None
    
    def smart_call(self, task_complexity: str, prompt: str):
        """Smart routing with Ollama"""
        
        # Try Ollama for simple tasks
        if task_complexity == 'simple':
            result = self.call_ollama(prompt)
            if result:
                return {'provider': 'ollama-mistral', 'response': result, 'cost': 0.0}
        
        # Fallback to cloud
        provider, _ = self.select_provider(task_complexity)
        # ... call cloud provider
```

## Kiro Workflow

### 1. User Request
```
User: "Review this code for bugs"
```

### 2. Kiro Analyzes
```python
# Kiro determines: simple task
complexity = 'simple'
```

### 3. Router Selects
```python
provider = router.select_provider('simple')
# Returns: 'ollama-mistral' (free, local)
```

### 4. Execute Locally
```python
result = call_ollama(prompt)
# Runs on your machine, $0 cost
```

### 5. Track
```python
tracker.action(
    purpose="Code review",
    action="Ollama reviewed code",
    result="No issues found",
    cost=0.0
)
```

## Benefits

✅ **Cost Savings**: 80% reduction
✅ **Privacy**: Data stays local
✅ **No Rate Limits**: Unlimited usage
✅ **Offline**: Works without internet
✅ **Fast**: For simple tasks
✅ **Kiro Compatible**: Works with existing tools

## Limitations

⚠️ **Quality**: Lower than GPT-4/Claude for complex tasks
⚠️ **Context**: Smaller context windows (8K vs 200K)
⚠️ **Speed**: Slower for complex reasoning
⚠️ **Hardware**: Needs decent CPU/GPU

## Recommendation

**Hybrid Approach**:
- 70% tasks → Ollama (simple, free)
- 30% tasks → Cloud (complex, paid)

**Result**:
- 80% cost savings
- Best quality where it matters
- Kiro works seamlessly with both

## Next Steps

1. Install Ollama
2. Pull mistral:7b model
3. Update smart_ai_router.py
4. Test with simple tasks
5. Monitor savings with ai_tracker

---

**Status**: Ollama supported in providers.py
**Setup**: 10 minutes
**Savings**: 80% cost reduction
**Kiro**: Fully compatible
