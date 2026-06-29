#!/usr/bin/env python3
"""Gemini API caller using official google-genai SDK"""

import os
import sys
from google import genai
from google.genai import types

def call_gemini(prompt: str, api_key: str = None, max_tokens: int = 2048) -> dict:
    """Call Gemini using official SDK"""
    
    if not api_key:
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        return {"error": "No API key. Set GEMINI_API_KEY"}
    
    try:
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=max_tokens,
                top_k=40,
                top_p=0.95
            )
        )
        
        return {
            "text": response.text,
            "finish_reason": str(response.candidates[0].finish_reason),
            "length": len(response.text)
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./gemini_sdk_caller.py '<prompt>' [max_tokens]")
        sys.exit(1)
    
    max_tokens = int(sys.argv[2]) if len(sys.argv) > 2 else 2048
    result = call_gemini(sys.argv[1], max_tokens=max_tokens)
    
    if "error" in result:
        print(f"ERROR: {result['error']}")
    else:
        print(result['text'])
