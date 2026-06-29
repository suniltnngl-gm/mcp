#!/usr/bin/env python3
"""Real AI Client - Integration with actual AI providers"""

import json
import time
import requests
from typing import Dict, Optional, Any
from dataclasses import dataclass

try:
    from api_key_manager import api_key_manager
    from cache_manager import intelligent_cache
    from logging_config import orchestration_logger
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

@dataclass
class AIResponse:
    """Structured AI response"""
    content: str
    provider: str
    model: str
    tokens_used: int
    cost: float
    latency: float
    cached: bool = False

class RealAIClient:
    """Real AI provider client with caching and error handling"""
    
    def __init__(self):
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Required dependencies not available")
        
        self.session = requests.Session()
        self.session.timeout = 30
        
    def generate_response(self, prompt: str, provider: str = "openrouter-free", 
                         model: str = None, max_tokens: int = 1000) -> AIResponse:
        """Generate AI response with real provider integration"""
        
        # Check cache first
        cache_params = {"model": model, "max_tokens": max_tokens}
        cached_response = intelligent_cache.get(provider, prompt, cache_params)
        
        if cached_response:
            orchestration_logger.info("Cache hit for AI request", 
                                    provider=provider, cached=True)
            return AIResponse(**cached_response, cached=True)
        
        # Get provider configuration
        config = api_key_manager.get_provider_config(provider)
        if not config or not config.api_key:
            # Fallback to mock response
            return self._generate_mock_response(prompt, provider, model or provider)
        
        start_time = time.time()
        
        try:
            # Generate real AI response
            if provider == "openrouter-free":
                response = self._call_openrouter(prompt, config, model, max_tokens)
            elif provider == "claude-sonnet":
                response = self._call_anthropic(prompt, config, model, max_tokens)
            elif provider == "gpt-4":
                response = self._call_openai(prompt, config, model, max_tokens)
            elif provider == "gemini-flash":
                response = self._call_google(prompt, config, model, max_tokens)
            else:
                # Unsupported provider, use mock
                response = self._generate_mock_response(prompt, provider, model or provider)
            
            latency = time.time() - start_time
            
            # Cache successful response
            cache_data = {
                "content": response.content,
                "provider": response.provider,
                "model": response.model,
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "latency": latency,
                "cached": False
            }
            intelligent_cache.set(provider, prompt, cache_data, cache_params, ttl=3600)
            
            orchestration_logger.info("AI response generated", 
                                    provider=provider, model=response.model,
                                    tokens=response.tokens_used, cost=response.cost,
                                    latency=latency)
            
            return response
            
        except Exception as e:
            orchestration_logger.error("AI request failed", 
                                     provider=provider, error=str(e))
            # Fallback to mock response
            return self._generate_mock_response(prompt, provider, model or provider)
    
    def _call_openrouter(self, prompt: str, config, model: str = None, 
                        max_tokens: int = 1000) -> AIResponse:
        """Call OpenRouter API"""
        model = model or "microsoft/phi-3-mini-128k-instruct:free"
        
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-orchestration-platform.local",
            "X-Title": "AI Orchestration Platform"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        response = self.session.post(
            f"{config.base_url}/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        tokens_used = result.get("usage", {}).get("total_tokens", len(prompt.split()) + len(content.split()))
        
        # OpenRouter free tier cost
        cost = 0.0
        
        return AIResponse(
            content=content,
            provider="openrouter-free",
            model=model,
            tokens_used=tokens_used,
            cost=cost,
            latency=0.0  # Will be set by caller
        )
    
    def _call_anthropic(self, prompt: str, config, model: str = None, 
                       max_tokens: int = 1000) -> AIResponse:
        """Call Anthropic Claude API"""
        model = model or "claude-3-haiku-20240307"
        
        headers = {
            "x-api-key": config.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = self.session.post(
            f"{config.base_url}/v1/messages",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        
        result = response.json()
        content = result["content"][0]["text"]
        tokens_used = result.get("usage", {}).get("total_tokens", len(prompt.split()) + len(content.split()))
        
        # Estimate cost (Claude Haiku: $0.25/1K input, $1.25/1K output)
        input_tokens = len(prompt.split()) * 1.3  # Rough estimate
        output_tokens = len(content.split()) * 1.3
        cost = (input_tokens / 1000 * 0.25) + (output_tokens / 1000 * 1.25)
        
        return AIResponse(
            content=content,
            provider="claude-sonnet",
            model=model,
            tokens_used=tokens_used,
            cost=cost,
            latency=0.0
        )
    
    def _call_openai(self, prompt: str, config, model: str = None, 
                    max_tokens: int = 1000) -> AIResponse:
        """Call OpenAI API"""
        model = model or "gpt-3.5-turbo"
        
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        response = self.session.post(
            f"{config.base_url}/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        tokens_used = result.get("usage", {}).get("total_tokens", len(prompt.split()) + len(content.split()))
        
        # Estimate cost (GPT-3.5: $0.50/1K input, $1.50/1K output)
        input_tokens = result.get("usage", {}).get("prompt_tokens", len(prompt.split()) * 1.3)
        output_tokens = result.get("usage", {}).get("completion_tokens", len(content.split()) * 1.3)
        cost = (input_tokens / 1000 * 0.50) + (output_tokens / 1000 * 1.50)
        
        return AIResponse(
            content=content,
            provider="gpt-4",
            model=model,
            tokens_used=tokens_used,
            cost=cost,
            latency=0.0
        )
    
    def _call_google(self, prompt: str, config, model: str = None, 
                    max_tokens: int = 1000) -> AIResponse:
        """Call Google Gemini API"""
        model = model or "gemini-1.5-flash"
        
        # Google API uses different format
        url = f"{config.base_url}/v1beta/models/{model}:generateContent"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        params = {"key": config.api_key}
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.7
            }
        }
        
        response = self.session.post(url, headers=headers, params=params, json=data)
        response.raise_for_status()
        
        result = response.json()
        content = result["candidates"][0]["content"]["parts"][0]["text"]
        tokens_used = len(prompt.split()) + len(content.split())  # Rough estimate
        
        # Estimate cost (Gemini Flash: $0.075/1K input, $0.30/1K output)
        input_tokens = len(prompt.split()) * 1.3
        output_tokens = len(content.split()) * 1.3
        cost = (input_tokens / 1000 * 0.075) + (output_tokens / 1000 * 0.30)
        
        return AIResponse(
            content=content,
            provider="gemini-flash",
            model=model,
            tokens_used=tokens_used,
            cost=cost,
            latency=0.0
        )
    
    def _generate_mock_response(self, prompt: str, provider: str, model: str) -> AIResponse:
        """Generate mock response as fallback"""
        mock_responses = {
            "architect-ai": f"From an architectural perspective: {prompt[:50]}... requires careful system design consideration.",
            "cost-optimizer-ai": f"Cost analysis: {prompt[:50]}... suggests budget-conscious approach needed.",
            "devops-ai": f"DevOps perspective: {prompt[:50]}... requires operational efficiency focus.",
            "security-ai": f"Security assessment: {prompt[:50]}... needs security evaluation and controls."
        }
        
        # Generate contextual mock response
        if any(role in prompt.lower() for role in mock_responses.keys()):
            for role, response in mock_responses.items():
                if role in prompt.lower():
                    content = response
                    break
        else:
            content = f"Mock response from {provider}: Analysis of '{prompt[:50]}...' completed. [No API key configured]"
        
        return AIResponse(
            content=content,
            provider=provider,
            model=model,
            tokens_used=len(prompt.split()) + len(content.split()),
            cost=0.0,  # Mock responses are free
            latency=0.1  # Simulate fast mock response
        )

# Global client instance
real_ai_client = RealAIClient() if DEPENDENCIES_AVAILABLE else None

def main():
    """Test real AI client"""
    if not DEPENDENCIES_AVAILABLE:
        print("❌ Dependencies not available")
        return
    
    print("🤖 Testing Real AI Client")
    print("=" * 40)
    
    # Test with different providers
    test_prompt = "Explain the benefits of microservices architecture in 2 sentences."
    
    providers = ["openrouter-free", "claude-sonnet", "gpt-4", "gemini-flash"]
    
    for provider in providers:
        print(f"\n🔍 Testing {provider}...")
        try:
            response = real_ai_client.generate_response(test_prompt, provider)
            print(f"✅ Response: {response.content[:100]}...")
            print(f"   Provider: {response.provider}")
            print(f"   Model: {response.model}")
            print(f"   Tokens: {response.tokens_used}")
            print(f"   Cost: ${response.cost:.4f}")
            print(f"   Cached: {response.cached}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test caching
    print(f"\n💾 Testing cache (second request)...")
    response2 = real_ai_client.generate_response(test_prompt, "openrouter-free")
    print(f"✅ Cached response: {response2.cached}")

if __name__ == "__main__":
    main()
