#!/usr/bin/env python3
"""AI Discussion Manager - Persistent multi-AI discussions"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Import tracking systems
sys.path.insert(0, str(Path(__file__).parent.parent / "orchestration"))
try:
    from session_tracker import SessionTracker
    from ai_action_tracker import AIActionTracker
    TRACKING_ENABLED = True
except ImportError:
    TRACKING_ENABLED = False

@dataclass
class Message:
    id: str
    participant: str
    timestamp: str
    content: str
    references: List[str] = None
    
    def __post_init__(self):
        if self.references is None:
            self.references = []

@dataclass
class Discussion:
    id: str
    topic: str
    created: str
    status: str
    participants: List[str]
    context: Dict
    messages: List[Message]
    decisions: List[str] = None
    
    def __post_init__(self):
        if self.decisions is None:
            self.decisions = []

class DiscussionManager:
    """Manage persistent AI discussions"""
    
    def __init__(self, storage_dir: str = "threads", enable_tracking: bool = True):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.participants_file = Path("participants.json")
        self.participants = self._load_participants()
        
        # Initialize tracking
        self.tracking_enabled = enable_tracking and TRACKING_ENABLED
        if self.tracking_enabled:
            # Use absolute paths relative to this file
            base_dir = Path(__file__).parent.parent / "orchestration"
            self.session_tracker = SessionTracker(str(base_dir / "session_history.jsonl"))
            self.action_tracker = AIActionTracker(str(base_dir / "ai_action_history.jsonl"))
    
    def _load_participants(self) -> Dict:
        """Load AI participant profiles"""
        if self.participants_file.exists():
            with open(self.participants_file) as f:
                return json.load(f)
        return {
            "architect-ai": {
                "role": "Software Architect",
                "expertise": ["system design", "scalability", "patterns"],
                "provider": "gpt-4",
                "personality": "analytical, thorough"
            },
            "cost-optimizer-ai": {
                "role": "Cost Analyst",
                "expertise": ["cloud costs", "optimization"],
                "provider": "gemini-flash",
                "personality": "pragmatic, budget-conscious"
            },
            "devops-ai": {
                "role": "DevOps Engineer",
                "expertise": ["deployment", "monitoring"],
                "provider": "claude-haiku",
                "personality": "practical, operations-focused"
            }
        }
    
    def create_discussion(self, topic: str, participants: List[str], 
                         context: Dict = None) -> str:
        """Create new discussion thread"""
        discussion_id = f"disc-{int(time.time())}"
        
        # Track session start
        if self.tracking_enabled:
            self.session_tracker.start_session(f"Create discussion: {topic}")
            self.session_tracker.add_thinking(f"Creating discussion with {len(participants)} participants: {', '.join(participants)}")
        
        discussion = Discussion(
            id=discussion_id,
            topic=topic,
            created=datetime.now().isoformat(),
            status="active",
            participants=participants,
            context=context or {},
            messages=[]
        )
        
        self._save_discussion(discussion)
        
        # Track action
        if self.tracking_enabled:
            self.session_tracker.add_action(
                purpose="Create discussion",
                action=f"discussion_manager.create({topic})",
                result=f"Created {discussion_id}"
            )
            self.session_tracker.complete_session(f"Discussion {discussion_id} created with {len(participants)} participants")
        
        return discussion_id
    
    def add_message(self, discussion_id: str, participant: str, 
                   content: str, references: List[str] = None):
        """Add message to discussion"""
        discussion = self._load_discussion(discussion_id)
        
        # Track AI action if participant is AI
        start_time = time.time()
        is_ai = participant in self.participants
        
        message = Message(
            id=f"msg-{len(discussion.messages)+1:03d}",
            participant=participant,
            timestamp=datetime.now().isoformat(),
            content=content,
            references=references or []
        )
        
        discussion.messages.append(message)
        self._save_discussion(discussion)
        
        # Track action
        if self.tracking_enabled and is_ai:
            latency = time.time() - start_time
            profile = self.participants.get(participant, {})
            
            self.action_tracker.log_action(
                action_type="discussion",
                provider=profile.get("provider", "unknown"),
                model=profile.get("provider", "unknown"),
                input_tokens=len(content.split()) * 2,  # Rough estimate
                output_tokens=len(content.split()),
                cost=0.0,  # Would need actual API call tracking
                latency=latency,
                success=True,
                context={
                    "discussion_id": discussion_id,
                    "topic": discussion.topic,
                    "participant": participant,
                    "message_count": len(discussion.messages)
                },
                result=f"Added message {message.id}"
            )
    
    def get_context(self, discussion_id: str) -> Dict:
        """Get full discussion context for AI"""
        discussion = self._load_discussion(discussion_id)
        
        return {
            "topic": discussion.topic,
            "participants": discussion.participants,
            "context": discussion.context,
            "messages": [
                {
                    "participant": m.participant,
                    "content": m.content,
                    "timestamp": m.timestamp
                }
                for m in discussion.messages
            ]
        }
    
    def get_participant_prompt(self, discussion_id: str, participant: str) -> str:
        """Build prompt for AI participant"""
        discussion = self._load_discussion(discussion_id)
        profile = self.participants.get(participant, {})
        
        messages_text = "\n\n".join([
            f"{m.participant} ({m.timestamp}):\n{m.content}"
            for m in discussion.messages
        ])
        
        prompt = f"""You are {profile.get('role', participant)}.

Your expertise: {', '.join(profile.get('expertise', []))}
Your personality: {profile.get('personality', 'professional')}

Discussion Topic: {discussion.topic}

Context: {json.dumps(discussion.context, indent=2)}

Previous Messages:
{messages_text if messages_text else '(No messages yet)'}

Provide your perspective on this topic. Be concise and actionable.
"""
        return prompt
    
    def list_discussions(self, status: str = None) -> List[Dict]:
        """List all discussions"""
        discussions = []
        for file in self.storage_dir.glob("*.json"):
            with open(file) as f:
                data = json.load(f)
                if status is None or data.get('status') == status:
                    discussions.append({
                        'id': data['id'],
                        'topic': data['topic'],
                        'status': data['status'],
                        'messages': len(data['messages']),
                        'created': data['created']
                    })
        return discussions
    
    def close_discussion(self, discussion_id: str, decision: str = None):
        """Close discussion with optional decision"""
        discussion = self._load_discussion(discussion_id)
        discussion.status = "closed"
        if decision:
            discussion.decisions.append(decision)
        self._save_discussion(discussion)
    
    def _load_discussion(self, discussion_id: str) -> Discussion:
        """Load discussion from storage"""
        file_path = self.storage_dir / f"{discussion_id}.json"
        with open(file_path) as f:
            data = json.load(f)
            data['messages'] = [Message(**m) for m in data['messages']]
            return Discussion(**data)
    
    def _save_discussion(self, discussion: Discussion):
        """Save discussion to storage"""
        file_path = self.storage_dir / f"{discussion.id}.json"
        data = asdict(discussion)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def print_discussion(self, discussion_id: str):
        """Print discussion in readable format"""
        discussion = self._load_discussion(discussion_id)
        
        print(f"\n{'='*60}")
        print(f"Discussion: {discussion.topic}")
        print(f"ID: {discussion.id}")
        print(f"Status: {discussion.status}")
        print(f"Participants: {', '.join(discussion.participants)}")
        print(f"{'='*60}\n")
        
        for msg in discussion.messages:
            print(f"{msg.participant} ({msg.timestamp}):")
            print(f"{msg.content}\n")
        
        if discussion.decisions:
            print(f"{'='*60}")
            print("Decisions:")
            for decision in discussion.decisions:
                print(f"  • {decision}")

def main():
    """CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  discussion_manager.py create <topic> <participant1,participant2,...>")
        print("  discussion_manager.py add <discussion_id> <participant> <message>")
        print("  discussion_manager.py show <discussion_id>")
        print("  discussion_manager.py list [active|closed]")
        print("  discussion_manager.py prompt <discussion_id> <participant>")
        print("  discussion_manager.py close <discussion_id> [decision]")
        sys.exit(1)
    
    manager = DiscussionManager()
    cmd = sys.argv[1]
    
    if cmd == 'create':
        topic = sys.argv[2]
        participants = sys.argv[3].split(',')
        disc_id = manager.create_discussion(topic, participants)
        print(f"Created discussion: {disc_id}")
    
    elif cmd == 'add':
        disc_id = sys.argv[2]
        participant = sys.argv[3]
        message = ' '.join(sys.argv[4:])
        manager.add_message(disc_id, participant, message)
        print(f"Added message from {participant}")
    
    elif cmd == 'show':
        disc_id = sys.argv[2]
        manager.print_discussion(disc_id)
    
    elif cmd == 'list':
        status = sys.argv[2] if len(sys.argv) > 2 else None
        discussions = manager.list_discussions(status)
        print(f"\n{'ID':<20} {'Topic':<40} {'Messages':<10} {'Status'}")
        print("-" * 80)
        for d in discussions:
            print(f"{d['id']:<20} {d['topic']:<40} {d['messages']:<10} {d['status']}")
    
    elif cmd == 'prompt':
        disc_id = sys.argv[2]
        participant = sys.argv[3]
        prompt = manager.get_participant_prompt(disc_id, participant)
        print(prompt)
    
    elif cmd == 'close':
        disc_id = sys.argv[2]
        decision = ' '.join(sys.argv[3:]) if len(sys.argv) > 3 else None
        manager.close_discussion(disc_id, decision)
        print(f"Closed discussion: {disc_id}")

if __name__ == '__main__':
    main()
