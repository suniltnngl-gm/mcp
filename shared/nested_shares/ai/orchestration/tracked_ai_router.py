#!/usr/bin/env python3
"""Smart AI Router with Action Tracking"""

import time
from smart_ai_router import SmartAIRouter
from ai_action_tracker import AIActionTracker

class TrackedAIRouter(SmartAIRouter):
    """AI Router with automatic action tracking"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tracker = AIActionTracker()
    
    def call_with_tracking(self, task_complexity: str, prompt: str,
                          action_type: str = 'query', context: dict = None):
        """Make AI call with automatic tracking"""
        
        # Select provider
        provider, reason = self.select_provider(task_complexity)
        
        # Get fallback chain
        fallbacks = self.get_fallback_chain(provider)
        
        # Try primary provider
        start = time.time()
        try:
            # Simulate AI call (replace with actual call)
            response = f"Response from {provider}"
            input_tokens = len(prompt.split()) * 2  # Rough estimate
            output_tokens = len(response.split()) * 2
            latency = time.time() - start
            cost = self.estimate_cost(provider, input_tokens, output_tokens)
            
            # Record usage in router
            self.record_usage(provider, input_tokens, output_tokens, latency, True)
            
            # Track action
            action_id = self.tracker.log_action(
                action_type=action_type,
                provider=provider,
                model=self.PROVIDERS[provider].name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                latency=latency,
                success=True,
                context=context or {'complexity': task_complexity, 'reason': reason},
                result=response[:100]  # First 100 chars
            )
            
            return {
                'success': True,
                'provider': provider,
                'response': response,
                'action_id': action_id,
                'cost': cost,
                'latency': latency
            }
            
        except Exception as e:
            latency = time.time() - start
            
            # Record failure
            self.record_usage(provider, 0, 0, latency, False)
            
            # Track failed action
            self.tracker.log_action(
                action_type=action_type,
                provider=provider,
                model=self.PROVIDERS[provider].name,
                input_tokens=0,
                output_tokens=0,
                cost=0,
                latency=latency,
                success=False,
                context=context or {'complexity': task_complexity},
                error=str(e)
            )
            
            # Try fallback
            if fallbacks:
                print(f"⚠️  {provider} failed, trying {fallbacks[0]}...")
                # Recursive call with fallback (simplified)
                return {'success': False, 'error': str(e), 'fallback_available': True}
            
            return {'success': False, 'error': str(e)}

def main():
    """Example usage"""
    router = TrackedAIRouter()
    
    # Make tracked AI call
    result = router.call_with_tracking(
        task_complexity='simple',
        prompt='Review this code for bugs',
        action_type='review',
        context={'file': 'main.py', 'lines': 150}
    )
    
    print(f"Success: {result['success']}")
    print(f"Provider: {result.get('provider')}")
    print(f"Cost: ${result.get('cost', 0):.4f}")
    print(f"Latency: {result.get('latency', 0):.2f}s")
    print(f"Action ID: {result.get('action_id')}")
    
    # View stats
    print("\n=== Today's Stats ===")
    stats = router.tracker.get_stats('today')
    print(f"Total actions: {stats['total_actions']}")
    print(f"Total cost: ${stats['total_cost']}")

if __name__ == '__main__':
    main()
