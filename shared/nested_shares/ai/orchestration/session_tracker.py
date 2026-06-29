#!/usr/bin/env python3
"""Session Tracker - Track user requests, AI thinking, actions, and summaries"""

import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class SessionEntry:
    timestamp: str
    session_id: str
    user_request: str
    ai_thinking: str
    actions: List[dict]  # [{purpose, action, result}]
    completion_summary: str
    cost: float = 0.0
    duration: float = 0.0

class SessionTracker:
    """Track complete AI sessions with user context"""
    
    def __init__(self, history_file: str = "session_history.jsonl"):
        self.history_file = Path(history_file)
        self.current_session = None
        self.session_start = None
    
    def start_session(self, user_request: str) -> str:
        """Start tracking a new session"""
        self.session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.session_start = datetime.now()
        self.current_session = {
            'session_id': self.session_id,
            'timestamp': self.session_start.isoformat(),
            'user_request': user_request,
            'ai_thinking': '',
            'actions': [],
            'completion_summary': '',
            'cost': 0.0,
            'duration': 0.0
        }
        return self.session_id
    
    def add_thinking(self, thinking: str):
        """Add AI thinking/reasoning"""
        if self.current_session:
            self.current_session['ai_thinking'] = thinking
    
    def add_action(self, purpose: str, action: str, result: str, cost: float = 0.0):
        """Add an action taken"""
        if self.current_session:
            self.current_session['actions'].append({
                'purpose': purpose,
                'action': action,
                'result': result,
                'cost': cost
            })
            self.current_session['cost'] += cost
    
    def complete_session(self, summary: str):
        """Complete session with summary"""
        if self.current_session:
            duration = (datetime.now() - self.session_start).total_seconds()
            self.current_session['completion_summary'] = summary
            self.current_session['duration'] = round(duration, 2)
            
            # Save to file
            with open(self.history_file, 'a') as f:
                f.write(json.dumps(self.current_session) + '\n')
            
            self.current_session = None
            self.session_start = None
    
    def get_recent_sessions(self, limit: int = 10) -> List[dict]:
        """Get recent sessions"""
        if not self.history_file.exists():
            return []
        
        sessions = []
        with open(self.history_file) as f:
            for line in f:
                sessions.append(json.loads(line))
        
        return sessions[-limit:]
    
    def search_sessions(self, query: str, limit: int = 20) -> List[dict]:
        """Search sessions by user request or summary"""
        if not self.history_file.exists():
            return []
        
        matches = []
        with open(self.history_file) as f:
            for line in f:
                session = json.loads(line)
                if (query.lower() in session['user_request'].lower() or
                    query.lower() in session['completion_summary'].lower()):
                    matches.append(session)
        
        return matches[-limit:]
    
    def get_stats(self) -> dict:
        """Get session statistics"""
        if not self.history_file.exists():
            return {'total_sessions': 0}
        
        sessions = []
        with open(self.history_file) as f:
            for line in f:
                sessions.append(json.loads(line))
        
        total_cost = sum(s['cost'] for s in sessions)
        total_actions = sum(len(s['actions']) for s in sessions)
        avg_duration = sum(s['duration'] for s in sessions) / len(sessions) if sessions else 0
        
        return {
            'total_sessions': len(sessions),
            'total_cost': round(total_cost, 4),
            'total_actions': total_actions,
            'avg_duration': round(avg_duration, 2),
            'avg_actions_per_session': round(total_actions / len(sessions), 1) if sessions else 0
        }
    
    def print_session(self, session: dict):
        """Print session in readable format"""
        print(f"\n{'='*60}")
        print(f"Session: {session['session_id']}")
        print(f"Time: {session['timestamp']}")
        print(f"Duration: {session['duration']}s")
        print(f"Cost: ${session['cost']:.4f}")
        print(f"{'='*60}\n")
        
        print(f"👤 User Request:\n{session['user_request']}\n")
        
        if session['ai_thinking']:
            print(f"🤔 AI Thinking:\n{session['ai_thinking']}\n")
        
        if session['actions']:
            print(f"⚡ Actions ({len(session['actions'])}):")
            for i, action in enumerate(session['actions'], 1):
                print(f"\n  {i}. {action['purpose']}")
                print(f"     Action: {action['action']}")
                print(f"     Result: {action['result']}")
                if action.get('cost', 0) > 0:
                    print(f"     Cost: ${action['cost']:.4f}")
        
        print(f"\n✅ Summary:\n{session['completion_summary']}\n")

def main():
    """CLI interface"""
    import sys
    
    tracker = SessionTracker()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  session_tracker.py recent [limit]")
        print("  session_tracker.py search <query>")
        print("  session_tracker.py show <session_id>")
        print("  session_tracker.py stats")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'recent':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        sessions = tracker.get_recent_sessions(limit)
        
        print(f"\n=== Recent Sessions ({len(sessions)}) ===\n")
        for session in sessions:
            print(f"{session['session_id']} - {session['user_request'][:60]}...")
            print(f"  Actions: {len(session['actions'])} | Cost: ${session['cost']:.4f} | Duration: {session['duration']}s")
            print(f"  Summary: {session['completion_summary'][:80]}...\n")
    
    elif cmd == 'search':
        query = ' '.join(sys.argv[2:])
        sessions = tracker.search_sessions(query)
        
        print(f"\n=== Search Results: '{query}' ({len(sessions)}) ===\n")
        for session in sessions:
            print(f"{session['session_id']} - {session['user_request'][:60]}...")
            print(f"  Summary: {session['completion_summary'][:80]}...\n")
    
    elif cmd == 'show':
        session_id = sys.argv[2]
        sessions = tracker.get_recent_sessions(1000)
        session = next((s for s in sessions if s['session_id'] == session_id), None)
        
        if session:
            tracker.print_session(session)
        else:
            print(f"Session {session_id} not found")
    
    elif cmd == 'stats':
        stats = tracker.get_stats()
        print(f"\n=== Session Statistics ===\n")
        print(f"Total sessions: {stats['total_sessions']}")
        print(f"Total cost: ${stats['total_cost']}")
        print(f"Total actions: {stats['total_actions']}")
        print(f"Avg duration: {stats['avg_duration']}s")
        print(f"Avg actions/session: {stats['avg_actions_per_session']}")

if __name__ == '__main__':
    main()
