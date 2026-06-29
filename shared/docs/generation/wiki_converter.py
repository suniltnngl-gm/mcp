#!/usr/bin/env python3
"""Convert documents to wiki and build knowledge base."""

from pathlib import Path
import shutil
import re

WORKSPACE = Path('/media/sunil-kr/workspace/user-projects')
WIKI_DIR = WORKSPACE / 'current/wiki-system/wiki'
KB_DIR = WORKSPACE / 'current/wiki-system/knowledge-base'

IGNORE_DIRS = {'node_modules', '.venv', 'archive', '__pycache__', '.git'}

def sanitize_name(name):
    """Convert filename to wiki-friendly name."""
    name = name.replace('.md', '')
    name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    return name

def categorize_doc(path):
    """Determine document category."""
    path_str = str(path).lower()
    
    if 'readme' in path_str:
        return 'overview'
    elif any(x in path_str for x in ['adr', 'architecture', 'design']):
        return 'architecture'
    elif any(x in path_str for x in ['guide', 'tutorial', 'how-to']):
        return 'guides'
    elif any(x in path_str for x in ['api', 'reference']):
        return 'reference'
    elif any(x in path_str for x in ['workflow', 'process']):
        return 'workflows'
    else:
        return 'general'

def build_wiki():
    """Build wiki from all markdown documents."""
    
    # Create wiki structure
    categories = ['overview', 'architecture', 'guides', 'reference', 'workflows', 'general']
    for cat in categories:
        (WIKI_DIR / cat).mkdir(parents=True, exist_ok=True)
    
    # Find all markdown files
    docs = []
    for md_file in WORKSPACE.rglob('*.md'):
        if any(ignore in md_file.parts for ignore in IGNORE_DIRS):
            continue
        docs.append(md_file)
    
    print(f"Found {len(docs)} documents to convert\n")
    
    # Convert to wiki
    converted = {}
    for doc in docs:
        category = categorize_doc(doc)
        rel_path = doc.relative_to(WORKSPACE)
        wiki_name = f"{sanitize_name(doc.stem)}_{sanitize_name(doc.parent.name)}.md"
        wiki_file = WIKI_DIR / category / wiki_name
        
        # Copy with metadata
        content = doc.read_text(errors='ignore')
        wiki_content = f"""---
source: {rel_path}
category: {category}
---

{content}
"""
        wiki_file.write_text(wiki_content)
        
        if category not in converted:
            converted[category] = []
        converted[category].append(wiki_name)
    
    # Create index
    index = WIKI_DIR / 'INDEX.md'
    index_content = "# Wiki Index\n\n"
    for cat in categories:
        if cat in converted:
            index_content += f"\n## {cat.title()}\n\n"
            for doc in sorted(converted[cat]):
                index_content += f"- [{doc}]({cat}/{doc})\n"
    
    index.write_text(index_content)
    
    print(f"✅ Converted {len(docs)} documents to wiki")
    print(f"📁 Categories: {', '.join(converted.keys())}")
    print(f"📄 Index: wiki/INDEX.md")
    
    return converted

def build_knowledge_base():
    """Build searchable knowledge base."""
    KB_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create KB index
    kb_index = []
    
    for wiki_file in WIKI_DIR.rglob('*.md'):
        if wiki_file.name == 'INDEX.md':
            continue
        
        content = wiki_file.read_text(errors='ignore')
        
        # Extract metadata
        metadata = {}
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                for line in parts[1].strip().split('\n'):
                    if ':' in line:
                        key, val = line.split(':', 1)
                        metadata[key.strip()] = val.strip()
        
        kb_index.append({
            'file': str(wiki_file.relative_to(WIKI_DIR)),
            'title': wiki_file.stem,
            'category': metadata.get('category', 'unknown'),
            'source': metadata.get('source', 'unknown')
        })
    
    # Write KB index
    kb_file = KB_DIR / 'index.txt'
    with open(kb_file, 'w') as f:
        for entry in kb_index:
            f.write(f"{entry['category']}|{entry['title']}|{entry['file']}|{entry['source']}\n")
    
    print(f"\n✅ Built knowledge base with {len(kb_index)} entries")
    print(f"📊 KB Index: knowledge-base/index.txt")

if __name__ == '__main__':
    print("🔄 Converting documents to wiki...\n")
    converted = build_wiki()
    build_knowledge_base()
    print("\n✨ Wiki and knowledge base ready!")
