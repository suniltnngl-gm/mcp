#!/usr/bin/env python3
"""Wiki generator for documentation."""

from pathlib import Path

def generate_wiki(docs_dir, output_dir):
    """Generate wiki from documentation."""
    docs = Path(docs_dir)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    
    for doc in docs.rglob('*.md'):
        wiki_file = output / doc.name
        wiki_file.write_text(doc.read_text())
        print(f"✓ {doc.name}")

if __name__ == '__main__':
    generate_wiki('docs', 'wiki')
