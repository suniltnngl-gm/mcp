# Ollama Python Library

Quick reference for the Ollama cloud API. Full tutorial at `~/.opencode/KB.md` (sections O1–O8).

## Cloud API Usage (free models)

```python
import os
from ollama import Client

client = Client(
    host='https://ollama.com',
    headers={'Authorization': 'Bearer ' + os.environ['OLLAMA_API_KEY']}
)

# Chat
response = client.chat(model='gpt-oss:120b-cloud', messages=[
    {'role': 'user', 'content': 'Hello!'},
])
print(response.message.content)

# Streaming
for part in client.chat(model='ministral-3:8b', messages=[
    {'role': 'user', 'content': 'Tell me a story'}
], stream=True):
    print(part.message.content, end='', flush=True)
```

## Free Models

- `gpt-oss:120b-cloud`
- `gpt-oss:20b-cloud`
- `gemma3:12b`
- `ministral-3:8b`
- `rnj-1:8b`

See also: `ollama.cloud` MCP server in `~/Public/project/src/llm_wrapper/mcp/ollama_cloud_server.py`.
