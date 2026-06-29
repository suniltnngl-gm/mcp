#!/usr/bin/env python3
"""Hybrid AI - Cloud orchestrates local model for optimal cost/performance"""

import json
from typing import Dict, Optional
from llama_cpp_wrapper import LlamaCppWrapper

class HybridAI:
    """Cloud AI orchestrates local llama.cpp for automated workflows"""
    
    def __init__(self, binary_path: str = "./llama.cpp/main", 
                 model_path: str = "./models/phi-3-mini-q4.gguf"):
        self.local_ai = LlamaCppWrapper(binary_path, model_path)
        self.local_available = self.local_ai.available
    
    def _call_local(self, prompt: str, timeout: int = 20) -> Optional[str]:
        """Call local llama.cpp"""
        if not self.local_available:
            return None
        return self.local_ai.generate(prompt, timeout=timeout)
    
    def orchestrated_workflow(self, task: str, code: str = None) -> Dict:
        """
        Cloud AI creates workflow, local model executes simple steps
        
        Workflow:
        1. Cloud AI analyzes task and breaks it down
        2. Cloud AI identifies simple vs complex steps
        3. Local model handles simple steps (formatting, syntax)
        4. Cloud AI handles complex steps (logic, architecture)
        5. Cloud AI synthesizes results
        """
        
        # Step 1: Cloud AI plans workflow (use smart_ai_router)
        plan_prompt = f"""Break down this task into simple and complex steps:
Task: {task}
{f"Code: {code[:200]}..." if code else ""}

Output JSON:
{{
  "simple_steps": ["step1", "step2"],
  "complex_steps": ["step3", "step4"]
}}"""
        
        # Simulate cloud response (in real use, call smart_ai_router)
        plan = {
            "simple_steps": ["Check syntax", "Format code", "Add comments"],
            "complex_steps": ["Analyze logic", "Suggest improvements"]
        }
        
        results = {
            "task": task,
            "plan": plan,
            "simple_results": [],
            "complex_results": [],
            "cost": 0.0
        }
        
        # Step 2: Execute simple steps with local model
        if self.local_available:
            for step in plan["simple_steps"]:
                prompt = f"{step}: {code[:500] if code else task}"
                result = self._call_local(prompt, timeout=15)
                if result:
                    results["simple_results"].append({
                        "step": step,
                        "result": result[:200],
                        "provider": "llama.cpp-phi3",
                        "cost": 0.0
                    })
        
        # Step 3: Cloud handles complex steps (placeholder)
        for step in plan["complex_steps"]:
            results["complex_results"].append({
                "step": step,
                "result": f"[Cloud AI would analyze: {step}]",
                "provider": "gemini-flash",
                "cost": 0.05
            })
            results["cost"] += 0.05
        
        return results
    
    def automated_code_review(self, code: str) -> Dict:
        """
        Cloud AI orchestrates local model for code review
        
        Process:
        1. Local: Quick syntax/style check (fast, free)
        2. Cloud: Analyze results, decide if deeper review needed
        3. Local: Format suggestions (if needed)
        4. Cloud: Complex logic review (if needed)
        """
        
        results = {
            "quick_check": None,
            "deep_review": None,
            "cost": 0.0
        }
        
        # Step 1: Local quick check
        if self.local_available:
            quick = self.local_ai.quick_check(code[:500], "Quick syntax and style check")
            results["quick_check"] = {
                "result": quick[:200] if quick else "Local AI unavailable",
                "provider": "llama.cpp-phi3",
                "cost": 0.0
            }
        
        # Step 2: Cloud decides if deep review needed (simulate)
        needs_deep = "error" in (results["quick_check"]["result"] or "").lower()
        
        if needs_deep:
            results["deep_review"] = {
                "result": "[Cloud AI would perform deep analysis]",
                "provider": "gemini-flash",
                "cost": 0.10
            }
            results["cost"] = 0.10
        
        return results
    
    def batch_processing(self, tasks: list) -> Dict:
        """
        Cloud AI batches tasks for local model
        
        Process:
        1. Cloud analyzes all tasks
        2. Cloud groups similar simple tasks
        3. Local processes batch (model stays warm)
        4. Cloud processes complex tasks
        5. Cloud synthesizes all results
        """
        
        results = {
            "total_tasks": len(tasks),
            "local_processed": 0,
            "cloud_processed": 0,
            "cost": 0.0
        }
        
        # Cloud groups tasks (simulate)
        simple_tasks = [t for t in tasks if len(t) < 100]
        complex_tasks = [t for t in tasks if len(t) >= 100]
        
        # Local batch processing
        if self.local_available and simple_tasks:
            for task in simple_tasks:
                result = self._call_local(task, timeout=10)
                if result:
                    results["local_processed"] += 1
        
        # Cloud processing
        results["cloud_processed"] = len(complex_tasks)
        results["cost"] = len(complex_tasks) * 0.05
        
        return results
    
    def smart_fallback(self, prompt: str, complexity: str = "simple") -> Dict:
        """
        Try local first, fallback to cloud if needed
        Cloud monitors and decides when to fallback
        """
        
        result = {
            "response": None,
            "provider": None,
            "cost": 0.0,
            "latency": 0.0
        }
        
        # Try local for simple tasks
        if complexity == "simple" and self.local_available:
            import time
            start = time.time()
            response = self._call_local(prompt, timeout=15)
            latency = time.time() - start
            
            if response and latency < 15:  # If fast enough
                result["response"] = response
                result["provider"] = "llama.cpp-phi3"
                result["latency"] = latency
                return result
        
        # Fallback to cloud
        result["response"] = "[Cloud AI response]"
        result["provider"] = "gemini-flash"
        result["cost"] = 0.05
        result["latency"] = 1.0
        
        return result

def main():
    """Demo hybrid AI system"""
    
    hybrid = HybridAI()
    
    print("=== Hybrid AI System (llama.cpp) ===\n")
    print(f"Local AI available: {hybrid.local_available}\n")
    
    # Demo 1: Orchestrated workflow
    print("1. Orchestrated Workflow:")
    result = hybrid.orchestrated_workflow(
        "Review this code for bugs",
        "def add(a, b): return a + b"
    )
    print(f"   Simple steps: {len(result['simple_results'])} (local, free)")
    print(f"   Complex steps: {len(result['complex_results'])} (cloud, ${result['cost']:.2f})")
    print()
    
    # Demo 2: Automated code review
    print("2. Automated Code Review:")
    result = hybrid.automated_code_review("def test(): pass")
    print(f"   Quick check: {result['quick_check']['provider']}")
    print(f"   Deep review: {'Yes' if result['deep_review'] else 'No'}")
    print(f"   Cost: ${result['cost']:.2f}")
    print()
    
    # Demo 3: Batch processing
    print("3. Batch Processing:")
    tasks = ["format code", "check syntax", "analyze complex logic here" * 10]
    result = hybrid.batch_processing(tasks)
    print(f"   Local: {result['local_processed']} tasks (free)")
    print(f"   Cloud: {result['cloud_processed']} tasks (${result['cost']:.2f})")
    print()
    
    # Demo 4: Smart fallback
    print("4. Smart Fallback:")
    result = hybrid.smart_fallback("Quick syntax check", "simple")
    print(f"   Provider: {result['provider']}")
    print(f"   Cost: ${result['cost']:.2f}")
    print(f"   Latency: {result['latency']:.1f}s")

if __name__ == '__main__':
    main()
