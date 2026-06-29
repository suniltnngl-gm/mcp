#!/usr/bin/env python3
"""Minimal llama.cpp wrapper for local AI inference"""

import subprocess
import os
from typing import Optional, Dict
from pathlib import Path

class LlamaCppWrapper:
    """Lightweight wrapper for llama.cpp binary"""
    
    def __init__(self, 
                 binary_path: str = "./llama.cpp/main",
                 model_path: str = "./models/phi-3-mini-q4.gguf"):
        self.binary_path = Path(binary_path)
        self.model_path = Path(model_path)
        self.available = self._check_available()
    
    def _check_available(self) -> bool:
        """Check if llama.cpp binary and model exist"""
        return self.binary_path.exists() and self.model_path.exists()
    
    def generate(self, 
                 prompt: str,
                 max_tokens: int = 512,
                 temperature: float = 0.7,
                 timeout: int = 20) -> Optional[str]:
        """
        Generate text using llama.cpp
        
        Args:
            prompt: Input prompt
            max_tokens: Max tokens to generate
            temperature: Sampling temperature
            timeout: Max execution time in seconds
            
        Returns:
            Generated text or None on error
        """
        if not self.available:
            return None
        
        try:
            result = subprocess.run([
                str(self.binary_path),
                '-m', str(self.model_path),
                '-p', prompt,
                '-n', str(max_tokens),
                '--temp', str(temperature),
                '--log-disable'
            ], 
            capture_output=True, 
            text=True,
            timeout=timeout)
            
            if result.returncode == 0:
                return result.stdout.strip()
            return None
            
        except subprocess.TimeoutExpired:
            return None
        except Exception:
            return None
    
    def quick_check(self, code: str, task: str = "syntax check") -> Optional[str]:
        """Quick code check (optimized for speed)"""
        prompt = f"{task}:\n{code[:500]}\nList issues only."
        return self.generate(prompt, max_tokens=256, temperature=0.3, timeout=10)
    
    def get_info(self) -> Dict:
        """Get wrapper status info"""
        return {
            "available": self.available,
            "binary": str(self.binary_path),
            "model": str(self.model_path),
            "binary_exists": self.binary_path.exists(),
            "model_exists": self.model_path.exists()
        }

def main():
    """Test llama.cpp wrapper"""
    wrapper = LlamaCppWrapper()
    
    print("=== llama.cpp Wrapper ===")
    info = wrapper.get_info()
    print(f"Available: {info['available']}")
    print(f"Binary: {info['binary']} ({'✓' if info['binary_exists'] else '✗'})")
    print(f"Model: {info['model']} ({'✓' if info['model_exists'] else '✗'})")
    
    if wrapper.available:
        print("\nTesting generation...")
        result = wrapper.generate("Say hello in one sentence.", max_tokens=50)
        print(f"Result: {result[:100] if result else 'Failed'}")

if __name__ == '__main__':
    main()
