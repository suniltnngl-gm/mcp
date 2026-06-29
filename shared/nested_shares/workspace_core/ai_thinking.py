"""AI thinking integration for tools - secure implementation."""

import os
import json
from pathlib import Path
import subprocess

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent.parent.parent / "workspace-automation" / ".env")
except ImportError:
    pass  # Fall back to environment variables

# Try to import google-genai for Gemini
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class AIThinking:
    """Provide AI reasoning capabilities to tools."""
    
    def __init__(self, provider="auto"):
        # Auto-detect available provider
        if provider == "auto":
            if os.environ.get('GROQ_API_KEY'):
                provider = "groq"
            elif os.environ.get('OPENROUTER_API_KEY'):
                provider = "openrouter"
            elif os.environ.get('GEMINI_API_KEY'):
                provider = "gemini"
            else:
                provider = "groq"  # default
        
        self.provider = provider
        self.api_key = self._get_api_key()
        
        if provider == "openrouter":
            self.model = "openrouter/auto"
            self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        elif provider == "gemini":
            self.model = "gemini-2.5-flash"
            self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        else:  # groq
            self.model = "meta-llama/llama-4-scout-17b-16e-instruct"
            self.api_url = "https://api.groq.com/openai/v1/chat/completions"
    
    def _get_api_key(self) -> str:
        """Get API key from environment or config (secure)."""
        # Try environment variable first
        if self.provider == "openrouter":
            key = os.environ.get('OPENROUTER_API_KEY')
        elif self.provider == "gemini":
            key = os.environ.get('GEMINI_API_KEY')
        else:
            key = os.environ.get('GROQ_API_KEY')
        
        if not key:
            # Try secure config file
            config_file = Path.home() / ".config" / "workspace" / "api_keys.json"
            if config_file.exists():
                try:
                    config = json.loads(config_file.read_text())
                    key = config.get('groq_api_key')
                except:
                    pass
        
        if not key:
            if self.provider == "openrouter":
                env_var = "OPENROUTER_API_KEY"
            elif self.provider == "gemini":
                env_var = "GEMINI_API_KEY"
            else:
                env_var = "GROQ_API_KEY"
            raise ValueError(
                f"{env_var} not found. Set it via:\n"
                f"  export {env_var}='your-key'\n"
                "Or create: ~/.config/workspace/api_keys.json"
            )
        
        return key
    
    def think(self, prompt: str, context: str = "", json_mode: bool = False) -> dict:
        """Get AI thinking/reasoning on a topic."""
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        if self.provider == "gemini":
            payload = {
                "contents": [{
                    "parts": [{"text": full_prompt}]
                }]
            }
            cmd = [
                'curl', '-s', f'{self.api_url}?key={self.api_key}',
                '-H', 'Content-Type: application/json',
                '-d', json.dumps(payload)
            ]
        elif self.provider == "openrouter":
            payload = {
                "model": self.model,
                "messages": [{
                    "role": "user",
                    "content": full_prompt
                }]
            }
            if json_mode:
                payload["response_format"] = {"type": "json_object"}
            cmd = [
                'curl', '-s', self.api_url,
                '-H', 'Content-Type: application/json',
                '-H', f'Authorization: Bearer {self.api_key}',
                '-H', 'HTTP-Referer: https://github.com/workspace-automation',
                '-H', 'X-Title: Workspace Automation AI',
                '-d', json.dumps(payload)
            ]
        else:
            payload = {
                "model": self.model,
                "messages": [{
                    "role": "user",
                    "content": full_prompt
                }]
            }
            if json_mode:
                payload["response_format"] = {"type": "json_object"}
            cmd = [
                'curl', '-s', self.api_url,
                '-H', 'Content-Type: application/json',
                '-H', f'Authorization: Bearer {self.api_key}',
                '-d', json.dumps(payload)
            ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            response = json.loads(result.stdout)
            
            if self.provider == "gemini":
                if 'candidates' in response:
                    return {
                        'success': True,
                        'response': response['candidates'][0]['content']['parts'][0]['text'],
                        'model': self.model
                    }
            else:
                if 'choices' in response:
                    return {
                        'success': True,
                        'response': response['choices'][0]['message']['content'],
                        'model': self.model
                    }
            
            return {
                'success': False,
                'error': response.get('error', 'Unknown error'),
                'raw_response': response
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_code(self, code: str, question: str) -> str:
        """Analyze code with AI thinking."""
        prompt = f"Analyze this code:\n\n```python\n{code}\n```\n\nQuestion: {question}"
        result = self.think(prompt)
        return result.get('response', 'Error: ' + result.get('error', 'Unknown'))
    
    def suggest_improvements(self, tool_name: str, tool_code: str) -> list:
        """Get AI suggestions for tool improvements."""
        prompt = f"Review this tool and suggest improvements:\n\nTool: {tool_name}\n\n```python\n{tool_code[:1000]}\n```"
        result = self.think(prompt)
        
        if result['success']:
            return result['response'].split('\n')
        return []
    
    def find_alternatives(self, tool_purpose: str, existing_tools: list) -> dict:
        """Get AI help finding best alternative."""
        prompt = f"Purpose: {tool_purpose}\n\nExisting tools:\n"
        for tool in existing_tools[:5]:
            prompt += f"- {tool}\n"
        prompt += "\nWhich tool is best for this purpose? Why?"
        
        result = self.think(prompt)
        return result


def setup_api_key():
    """Helper to setup API key securely."""
    print("🔐 API Key Setup")
    print("=" * 60)
    
    config_dir = Path.home() / ".config" / "workspace"
    config_file = config_dir / "api_keys.json"
    
    print("\n   Option 1: Environment Variable (Recommended)")
    print("      export GROQ_API_KEY='your-key-here'")
    print("      echo 'export GROQ_API_KEY=\"your-key\"' >> ~/.bashrc")
    
    print("\n   Option 2: Config File")
    print(f"      mkdir -p {config_dir}")
    print(f"      echo '{{\"groq_api_key\": \"your-key\"}}' > {config_file}")
    print(f"      chmod 600 {config_file}")
    
    print("\n   ⚠️  NEVER commit API keys to git!")
    print("      Add to .gitignore: api_keys.json")


if __name__ == "__main__":
    import sys
    
    if "--setup" in sys.argv:
        setup_api_key()
    else:
        try:
            ai = AIThinking()
            result = ai.think("Explain the importance of fast language models in 2 sentences")
            if result['success']:
                print("✅ AI Thinking Test:")
                print(result['response'])
            else:
                print(f"❌ Error: {result['error']}")
        except ValueError as e:
            print(f"❌ {e}")
            print("\nRun: python3 ai_thinking.py --setup")
