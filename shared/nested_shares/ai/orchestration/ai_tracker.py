#!/usr/bin/env python3
"""Unified AI Tracker - Sessions + Actions in one system"""

import json
import time
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

@dataclass
class Action:
    purpose: str
    action: str
    result: str
    cost: float = 0.0
    tokens: int = 0
    latency: float = 0.0

@dataclass
class Session:
    id: str
    timestamp: str
    user_request: str
    ai_thinking: str
    actions: List[Action]
    summary: str
    total_cost: float
    duration: float

class AITracker:
    """Unified tracker for sessions and actions"""
    
    def __init__(self, history_file: str = "ai_history.jsonl"):
        self.history_file = Path(history_file)
        self.current_session = None
        self.session_start = None
    
    def start(self, user_request: str) -> str:
        """Start tracking session"""
        self.session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.session_start = time.time()
        self.current_session = {
            'id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'user_request': user_request,
            'ai_thinking': '',
            'actions': [],
            'summary': '',
            'total_cost': 0.0,
            'duration': 0.0
        }
        return self.session_id
    
    def think(self, thinking: str):
        """Add AI thinking"""
        if self.current_session:
            self.current_session['ai_thinking'] = thinking
    
    def action(self, purpose: str, action: str, result: str, 
               cost: float = 0.0, tokens: int = 0, latency: float = 0.0):
        """Track action"""
        if self.current_session:
            self.current_session['actions'].append({
                'purpose': purpose,
                'action': action,
                'result': result,
                'cost': cost,
                'tokens': tokens,
                'latency': latency
            })
            self.current_session['total_cost'] += cost
    
    def complete(self, summary: str):
        """Complete session"""
        if self.current_session:
            self.current_session['summary'] = summary
            self.current_session['duration'] = round(time.time() - self.session_start, 2)
            
            with open(self.history_file, 'a') as f:
                f.write(json.dumps(self.current_session) + '\n')
            
            self.current_session = None
    
    def recent(self, limit: int = 10) -> List[Dict]:
        """Get recent sessions"""
        if not self.history_file.exists():
            return []
        
        sessions = []
        with open(self.history_file) as f:
            for line in f:
                sessions.append(json.loads(line))
        return sessions[-limit:]
    
    def search(self, query: str) -> List[Dict]:
        """Search sessions"""
        if not self.history_file.exists():
            return []
        
        matches = []
        with open(self.history_file) as f:
            for line in f:
                session = json.loads(line)
                if query.lower() in session['user_request'].lower() or \
                   query.lower() in session['summary'].lower():
                    matches.append(session)
        return matches
    
    def stats(self) -> Dict:
        """Get statistics"""
        if not self.history_file.exists():
            return {'total_sessions': 0}
        
        sessions = []
        with open(self.history_file) as f:
            for line in f:
                sessions.append(json.loads(line))
        
        total_cost = sum(s['total_cost'] for s in sessions)
        total_actions = sum(len(s['actions']) for s in sessions)
        
        return {
            'total_sessions': len(sessions),
            'total_actions': total_actions,
            'total_cost': round(total_cost, 4),
            'avg_actions': round(total_actions / len(sessions), 1) if sessions else 0
        }
    
    def show(self, session_id: str):
        """Show session details"""
        sessions = self.recent(1000)
        session = next((s for s in sessions if s['id'] == session_id), None)
        
        if not session:
            print(f"Session {session_id} not found")
            return
        
        print(f"\n{'='*60}")
        print(f"Session: {session['id']}")
        print(f"Time: {session['timestamp']}")
        print(f"Duration: {session['duration']}s | Cost: ${session['total_cost']:.4f}")
        print(f"{'='*60}\n")
        
        print(f"👤 Request: {session['user_request']}\n")
        
        if session['ai_thinking']:
            print(f"🤔 Thinking: {session['ai_thinking']}\n")
        
        if session['actions']:
            print(f"⚡ Actions ({len(session['actions'])}):")
            for i, a in enumerate(session['actions'], 1):
                print(f"\n  {i}. {a['purpose']}")
                print(f"     {a['action']}")
                print(f"     → {a['result']}")
                if a['cost'] > 0:
                    print(f"     ${a['cost']:.4f} | {a['tokens']} tokens | {a['latency']:.2f}s")
        
        print(f"\n✅ {session['summary']}\n")

def main():
    import sys
    
    tracker = AITracker()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  ai_tracker.py recent [limit]")
        print("  ai_tracker.py search <query>")
        print("  ai_tracker.py show <session_id>")
        print("  ai_tracker.py stats")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'recent':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        sessions = tracker.recent(limit)
        print(f"\n=== Recent Sessions ({len(sessions)}) ===\n")
        for s in sessions:
            print(f"{s['id']} - {s['user_request'][:60]}...")
            print(f"  {len(s['actions'])} actions | ${s['total_cost']:.4f} | {s['duration']}s\n")
    
    elif cmd == 'search':
        query = ' '.join(sys.argv[2:])
        sessions = tracker.search(query)
        print(f"\n=== Search: '{query}' ({len(sessions)}) ===\n")
        for s in sessions:
            print(f"{s['id']} - {s['user_request'][:60]}...")
    
    elif cmd == 'show':
        tracker.show(sys.argv[2])
    
    elif cmd == 'stats':
        stats = tracker.stats()
        print(f"\n=== Statistics ===\n")
        print(f"Sessions: {stats['total_sessions']}")
        print(f"Actions: {stats['total_actions']}")
        print(f"Cost: ${stats['total_cost']}")
        print(f"Avg actions/session: {stats['avg_actions']}")

if __name__ == '__main__':
    main()
