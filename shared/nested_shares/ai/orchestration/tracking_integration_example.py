#!/usr/bin/env python3
"""
AI Tracking Integration Example
Demonstrates how to use tracking-enabled AI tools
"""

import sys
from pathlib import Path

# Add orchestration to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "discussions"))

from session_tracker import SessionTracker
from ai_action_tracker import AIActionTracker
from unified_review import UnifiedReview

def example_1_review_with_tracking():
    """Example 1: Code review with automatic tracking"""
    print("\n" + "="*60)
    print("Example 1: Code Review with Tracking")
    print("="*60)
    
    # Create reviewer with tracking enabled
    reviewer = UnifiedReview(enable_tracking=True)
    
    # Review current file
    current_file = Path(__file__)
    findings = reviewer.review_file(current_file)
    
    print(f"\n✅ Reviewed {current_file.name}")
    print(f"   Found {len(findings)} issues")
    print(f"   Tracking logged to: ai_action_history.jsonl")

def example_2_manual_tracking():
    """Example 2: Manual session tracking"""
    print("\n" + "="*60)
    print("Example 2: Manual Session Tracking")
    print("="*60)
    
    # Initialize trackers
    session = SessionTracker("session_history.jsonl")
    action = AIActionTracker("ai_action_history.jsonl")
    
    # Start session
    session_id = session.start_session("Example AI workflow")
    print(f"\n📝 Started session: {session_id}")
    
    # Add thinking
    session.add_thinking("Planning to analyze code quality and suggest improvements")
    
    # Simulate AI action
    action_id = action.log_action(
        action_type="code_analysis",
        provider="example-ai",
        model="gpt-4",
        input_tokens=150,
        output_tokens=75,
        cost=0.005,
        latency=1.2,
        success=True,
        context={"task": "code_quality_check"},
        result="Found 3 improvement opportunities"
    )
    print(f"🤖 Logged AI action: {action_id}")
    
    # Add action to session
    session.add_action(
        purpose="Analyze code quality",
        action="AI code analysis",
        result="3 improvements suggested",
        cost=0.005
    )
    
    # Complete session
    session.complete_session("Successfully analyzed code and provided recommendations")
    print(f"✅ Session completed")

def example_3_discussion_tracking():
    """Example 3: Discussion manager with tracking"""
    print("\n" + "="*60)
    print("Example 3: Discussion Manager (Tracking Built-in)")
    print("="*60)
    
    try:
        from discussion_manager import DiscussionManager
        
        # Create manager with tracking
        manager = DiscussionManager(enable_tracking=True)
        
        # Create discussion
        disc_id = manager.create_discussion(
            topic="Code optimization strategy",
            participants=["architect-ai", "cost-optimizer-ai"]
        )
        
        print(f"\n💬 Created discussion: {disc_id}")
        print(f"   Tracking automatically logged")
        print(f"   Session: discussion creation")
        print(f"   Actions: will log AI participant messages")
        
    except ImportError:
        print("\n⚠️  discussion_manager not available in path")

def example_4_orchestra_tracking():
    """Example 4: AI Orchestra with tracking"""
    print("\n" + "="*60)
    print("Example 4: AI Orchestra (Tracking Built-in)")
    print("="*60)
    
    print("\n🎭 AI Orchestra includes automatic tracking:")
    print("   • Session tracking for orchestration runs")
    print("   • Action tracking for multi-agent collaboration")
    print("   • Logs: agents, iterations, latency, recommendations")
    print("\nUsage:")
    print("   from ai_orchestra import AIOrchestra")
    print("   orchestra = AIOrchestra(enable_tracking=True)")
    print("   results = orchestra.analyze_scenario(scenario)")

def example_5_view_history():
    """Example 5: View tracking history"""
    print("\n" + "="*60)
    print("Example 5: View Tracking History")
    print("="*60)
    
    # Check if history files exist
    session_file = Path("session_history.jsonl")
    action_file = Path("ai_action_history.jsonl")
    
    if session_file.exists():
        lines = session_file.read_text().strip().split('\n')
        print(f"\n📊 Session History: {len(lines)} sessions")
        print(f"   File: {session_file}")
    else:
        print(f"\n📊 Session History: No sessions yet")
    
    if action_file.exists():
        lines = action_file.read_text().strip().split('\n')
        print(f"\n🤖 AI Action History: {len(lines)} actions")
        print(f"   File: {action_file}")
    else:
        print(f"\n🤖 AI Action History: No actions yet")

def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("AI Tracking Integration Examples")
    print("="*60)
    print("\nDemonstrating tracking-enabled AI tools:")
    print("  • unified_review.py - Code review with tracking")
    print("  • discussion_manager.py - AI discussions with tracking")
    print("  • ai_orchestra.py - Multi-agent orchestration with tracking")
    
    # Run examples
    example_1_review_with_tracking()
    example_2_manual_tracking()
    example_3_discussion_tracking()
    example_4_orchestra_tracking()
    example_5_view_history()
    
    print("\n" + "="*60)
    print("✅ All examples completed!")
    print("="*60)
    print("\nTracking files created:")
    print("  • session_history.jsonl - User sessions and workflows")
    print("  • ai_action_history.jsonl - AI actions with costs and performance")
    print("\nBenefits:")
    print("  ✓ Track AI usage and costs")
    print("  ✓ Monitor performance and latency")
    print("  ✓ Analyze patterns and optimize")
    print("  ✓ Debug issues with full context")
    print()

if __name__ == '__main__':
    main()
