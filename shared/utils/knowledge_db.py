#!/usr/bin/env python3
"""
Knowledge Database for Gemini Automation
Searchable storage for gemini responses and insights
"""

import sqlite3
import json
import sys
from datetime import datetime
from pathlib import Path

class KnowledgeDB:
    def __init__(self, db_path="data/knowledge.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    prompt TEXT,
                    response TEXT,
                    category TEXT,
                    tokens_used INTEGER,
                    processed BOOLEAN DEFAULT FALSE
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    insight TEXT,
                    priority TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            """)
            
            # Enable FTS for search
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS search_index 
                USING fts5(session_id, prompt, response, insights)
            """)
    
    def store_session(self, session_data):
        """Store gemini session data"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO sessions 
                (id, timestamp, prompt, response, category, tokens_used, processed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_data['id'],
                session_data['timestamp'],
                session_data['prompt'],
                session_data['response'],
                self._categorize_prompt(session_data['prompt']),
                session_data.get('stats', {}).get('tokens', {}).get('total', 0),
                session_data.get('processed', False)
            ))
            
            # Update search index
            conn.execute("""
                INSERT OR REPLACE INTO search_index 
                (session_id, prompt, response, insights)
                VALUES (?, ?, ?, ?)
            """, (
                session_data['id'],
                session_data['prompt'],
                session_data['response'],
                ""  # Will be populated when insights are extracted
            ))
    
    def search(self, query, limit=10):
        """Search knowledge base"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # FTS search
            results = conn.execute("""
                SELECT s.*, rank
                FROM search_index si
                JOIN sessions s ON si.session_id = s.id
                WHERE search_index MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit)).fetchall()
            
            return [dict(row) for row in results]
    
    def get_insights_by_category(self, category):
        """Get insights by category"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            results = conn.execute("""
                SELECT s.prompt, s.response, i.insight, i.priority
                FROM sessions s
                LEFT JOIN insights i ON s.id = i.session_id
                WHERE s.category = ?
                ORDER BY s.timestamp DESC
            """, (category,)).fetchall()
            
            return [dict(row) for row in results]
    
    def _categorize_prompt(self, prompt):
        """Categorize prompt based on keywords"""
        categories = {
            'code_quality': ['quality', 'improve', 'refactor'],
            'architecture': ['architecture', 'pattern', 'design'],
            'testing': ['test', 'coverage', 'scenario'],
            'security': ['security', 'vulnerability', 'secure'],
            'documentation': ['documentation', 'docs', 'document'],
            'workflow': ['workflow', 'automation', 'process']
        }
        
        prompt_lower = prompt.lower()
        for category, keywords in categories.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return category
        return 'general'

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 knowledge_db.py <command> [args]")
        print("Commands: import, search, insights")
        return
    
    db = KnowledgeDB()
    command = sys.argv[1]
    
    if command == "import":
        # Import from JSON responses file
        json_file = Path("data/gemini_responses.json")
        if json_file.exists():
            with open(json_file) as f:
                data = json.load(f)
                for session in data.get('sessions', []):
                    db.store_session(session)
            print(f"Imported {len(data.get('sessions', []))} sessions")
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: python3 knowledge_db.py search <query>")
            return
        
        query = " ".join(sys.argv[2:])
        results = db.search(query)
        
        for result in results:
            print(f"\n--- Session {result['id']} ---")
            print(f"Prompt: {result['prompt']}")
            print(f"Response: {result['response'][:200]}...")
    
    elif command == "insights":
        category = sys.argv[2] if len(sys.argv) > 2 else None
        if category:
            insights = db.get_insights_by_category(category)
            print(f"\n=== {category.upper()} INSIGHTS ===")
            for insight in insights:
                print(f"• {insight['response'][:100]}...")
        else:
            print("Available categories: code_quality, architecture, testing, security, documentation, workflow")

if __name__ == "__main__":
    main()
