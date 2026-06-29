#!/usr/bin/env python3
"""Call Gemini API for discussion responses"""

import os
import sys
import json
import requests

def call_gemini(prompt: str, api_key: str = None, max_tokens: int = 2048) -> dict:
    """Call Gemini API with prompt, return full response data"""
    
    if not api_key:
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        return {"error": "No API key found. Set GEMINI_API_KEY or GOOGLE_API_KEY"}
    
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": max_tokens,
            "topK": 40,
            "topP": 0.95
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        text = data['candidates'][0]['content']['parts'][0]['text']
        finish_reason = data['candidates'][0].get('finishReason', 'UNKNOWN')
        
        return {
            "text": text,
            "finish_reason": finish_reason,
            "truncated": finish_reason == "MAX_TOKENS",
            "length": len(text)
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 gemini_caller.py '<prompt>' [max_tokens]")
        sys.exit(1)
    
    max_tokens = int(sys.argv[2]) if len(sys.argv) > 2 else 2048
    result = call_gemini(sys.argv[1], max_tokens=max_tokens)
    
    if "error" in result:
        print(f"ERROR: {result['error']}")
    else:
        print(result['text'])
        if result['truncated']:
            print(f"\n⚠️  Response truncated at {result['length']} chars", file=sys.stderr)
