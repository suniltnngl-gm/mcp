#!/usr/bin/env python3
import sys, os, json, requests
from pathlib import Path

api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyCx1s62jdaDmQ8_7ikXhth-GJMONWimVx0')
url = f'https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}'

prompt = sys.argv[1]
disc_id = sys.argv[2]
participant = sys.argv[3]

payload = {'contents': [{'parts': [{'text': prompt}]}], 'generationConfig': {'maxOutputTokens': 1000}}
r = requests.post(url, json=payload, timeout=30)
response_text = r.json()['candidates'][0]['content']['parts'][0]['text']

# Load discussion
disc_file = Path(f'threads/{disc_id}.json')
disc = json.loads(disc_file.read_text())

# Add message
msg_id = f"msg-{len(disc['messages'])+1:03d}"
disc['messages'].append({
    'id': msg_id,
    'participant': participant,
    'timestamp': __import__('datetime').datetime.now().isoformat(),
    'content': response_text,
    'references': []
})

disc_file.write_text(json.dumps(disc, indent=2))
print(f"Added {len(response_text)} chars from {participant}")
print(f"\n{response_text}")
