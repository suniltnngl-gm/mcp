#!/usr/bin/env python3
"""
Jules API Client - Minimal integration for automated code improvements
Integrates with lean versioning system for systematic improvements
"""

import os
import json
import requests
from typing import Dict, List, Optional

class JulesClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('JULES_API_KEY')
        self.base_url = "https://jules.googleapis.com/v1alpha"
        self.headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def list_sources(self) -> List[Dict]:
        """Get available GitHub repositories"""
        response = requests.get(f"{self.base_url}/sources", headers=self.headers)
        return response.json().get('sources', [])
    
    def create_improvement_session(self, source: str, prompt: str, title: str = None) -> Dict:
        """Create session for code improvement with auto PR"""
        data = {
            "prompt": prompt,
            "sourceContext": {
                "source": source,
                "githubRepoContext": {"startingBranch": "main"}
            },
            "automationMode": "AUTO_CREATE_PR",
            "title": title or f"Improvement: {prompt[:50]}..."
        }
        response = requests.post(f"{self.base_url}/sessions", headers=self.headers, json=data)
        return response.json()
    
    def get_session(self, session_id: str) -> Dict:
        """Get session status and outputs"""
        response = requests.get(f"{self.base_url}/sessions/{session_id}", headers=self.headers)
        return response.json()
    
    def send_message(self, session_id: str, message: str) -> None:
        """Send follow-up message to session"""
        data = {"prompt": message}
        requests.post(f"{self.base_url}/sessions/{session_id}:sendMessage", 
                     headers=self.headers, json=data)

def main():
    """CLI interface for Jules API"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: jules_api_client.py <command> [args...]")
        print("Commands: sources, improve <source> <prompt>, status <session_id>")
        return
    
    client = JulesClient()
    command = sys.argv[1]
    
    if command == "sources":
        sources = client.list_sources()
        for source in sources:
            print(f"{source['name']} ({source['id']})")
    
    elif command == "improve" and len(sys.argv) >= 4:
        source, prompt = sys.argv[2], " ".join(sys.argv[3:])
        session = client.create_improvement_session(source, prompt)
        print(f"Session created: {session['id']}")
        print(f"Title: {session['title']}")
    
    elif command == "status" and len(sys.argv) >= 3:
        session_id = sys.argv[2]
        session = client.get_session(session_id)
        print(f"Status: {session.get('status', 'Running')}")
        if 'outputs' in session:
            for output in session['outputs']:
                if 'pullRequest' in output:
                    pr = output['pullRequest']
                    print(f"PR: {pr['url']}")

if __name__ == "__main__":
    main()
