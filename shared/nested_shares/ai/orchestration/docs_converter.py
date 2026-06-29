#!/usr/bin/env python3
"""Docs to Wiki Converter - Automated knowledge base population"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Set

class DocsConverter:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects")
        self.kiro_cli = "kiro-cli"
    
    def scan_documentation(self) -> Dict:
        """Scan workspace for documentation files"""
        docs = {
            "markdown": list(self.workspace_path.rglob("*.md")),
            "text": list(self.workspace_path.rglob("*.txt")),
            "readme": list(self.workspace_path.rglob("README*")),
        }
        
        # Filter out already processed docs
        processed = self._get_processed_docs()
        
        for doc_type in docs:
            docs[doc_type] = [d for d in docs[doc_type] if str(d) not in processed]
        
        return docs
    
    def _get_processed_docs(self) -> Set[str]:
        """Get list of already processed documents"""
        try:
            result = subprocess.run([
                self.kiro_cli, "knowledge", "search", 
                "converted_doc", "--limit", "100"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Extract file paths from results
                paths = re.findall(r'Path: ([^\n]+)', result.stdout)
                return set(paths)
        except Exception:
            pass
        
        return set()
    
    def convert_doc_to_wiki(self, doc_path: Path) -> bool:
        """Convert single document to wiki format"""
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Enhance content with metadata
            wiki_content = self._enhance_content(content, doc_path)
            
            # Generate knowledge base name
            kb_name = self._generate_kb_name(doc_path)
            
            # Add to knowledge base
            result = subprocess.run([
                self.kiro_cli, "knowledge", "add", kb_name, wiki_content
            ], capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Failed to convert {doc_path}: {e}")
            return False
    
    def _enhance_content(self, content: str, doc_path: Path) -> str:
        """Enhance content with metadata and cross-references"""
        
        # Add metadata header
        enhanced = f"""---
source_file: {doc_path}
converted_date: {Path(__file__).stat().st_mtime}
category: {self._categorize_doc(doc_path)}
tags: {self._extract_tags(content)}
---

# {doc_path.stem.replace('_', ' ').title()}

"""
        
        # Add original content
        enhanced += content
        
        # Add cross-references
        enhanced += self._add_cross_references(content, doc_path)
        
        return enhanced
    
    def _categorize_doc(self, doc_path: Path) -> str:
        """Categorize document based on path and content"""
        path_str = str(doc_path).lower()
        
        if "ai" in path_str or "orchestration" in path_str:
            return "ai_systems"
        elif "nested-shares" in path_str:
            return "tools_organization"
        elif "workflow" in path_str or "automation" in path_str:
            return "automation"
        elif "wiki" in path_str:
            return "documentation"
        else:
            return "general"
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract relevant tags from content"""
        tags = []
        
        # Common technical terms
        tech_terms = ["python", "bash", "ai", "automation", "workflow", "merge", "split", "nested"]
        for term in tech_terms:
            if term.lower() in content.lower():
                tags.append(term)
        
        # Extract from headers
        headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        for header in headers[:3]:  # First 3 headers
            words = re.findall(r'\b\w+\b', header.lower())
            tags.extend([w for w in words if len(w) > 3])
        
        return list(set(tags))[:10]  # Limit to 10 tags
    
    def _add_cross_references(self, content: str, doc_path: Path) -> str:
        """Add cross-references to related documents"""
        refs = "\n\n## Related Documents\n"
        
        # Find related files based on keywords
        keywords = self._extract_keywords(content)
        related_files = self._find_related_files(keywords, doc_path)
        
        for related in related_files[:5]:  # Limit to 5 references
            refs += f"- [{related.stem}]({related})\n"
        
        return refs if len(related_files) > 0 else ""
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords for finding related documents"""
        # Simple keyword extraction
        words = re.findall(r'\b[A-Za-z]{4,}\b', content)
        word_freq = {}
        for word in words:
            word_freq[word.lower()] = word_freq.get(word.lower(), 0) + 1
        
        # Return most frequent words
        return sorted(word_freq.keys(), key=lambda x: word_freq[x], reverse=True)[:10]
    
    def _find_related_files(self, keywords: List[str], current_path: Path) -> List[Path]:
        """Find files related to keywords"""
        related = []
        
        for md_file in self.workspace_path.rglob("*.md"):
            if md_file == current_path:
                continue
            
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    file_content = f.read().lower()
                
                # Count keyword matches
                matches = sum(1 for keyword in keywords if keyword in file_content)
                if matches >= 2:  # At least 2 keyword matches
                    related.append(md_file)
                    
            except Exception:
                continue
        
        return related
    
    def _generate_kb_name(self, doc_path: Path) -> str:
        """Generate knowledge base entry name"""
        category = self._categorize_doc(doc_path)
        name = doc_path.stem.replace('_', '-').replace(' ', '-').lower()
        return f"{category}-{name}"
    
    def batch_convert(self, limit: int = 10) -> Dict:
        """Convert multiple documents in batch"""
        docs = self.scan_documentation()
        
        results = {
            "converted": 0,
            "failed": 0,
            "skipped": 0,
            "total_found": sum(len(files) for files in docs.values())
        }
        
        converted_count = 0
        
        for doc_type, files in docs.items():
            for doc_file in files:
                if converted_count >= limit:
                    results["skipped"] = results["total_found"] - converted_count
                    break
                
                print(f"📄 Converting: {doc_file.name}")
                
                if self.convert_doc_to_wiki(doc_file):
                    results["converted"] += 1
                    print(f"✅ Converted: {doc_file.name}")
                else:
                    results["failed"] += 1
                    print(f"❌ Failed: {doc_file.name}")
                
                converted_count += 1
        
        return results

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert docs to wiki")
    parser.add_argument("--limit", type=int, default=10, help="Max files to convert")
    parser.add_argument("--scan", action="store_true", help="Scan only, don't convert")
    
    args = parser.parse_args()
    converter = DocsConverter()
    
    if args.scan:
        docs = converter.scan_documentation()
        print("📊 Documentation Scan Results")
        print("=" * 30)
        for doc_type, files in docs.items():
            print(f"{doc_type.title()}: {len(files)} files")
            for f in files[:3]:  # Show first 3
                print(f"  - {f.name}")
            if len(files) > 3:
                print(f"  ... and {len(files) - 3} more")
    else:
        print(f"🔄 Converting up to {args.limit} documents...")
        results = converter.batch_convert(args.limit)
        
        print("\n📊 Conversion Results")
        print("=" * 20)
        print(f"✅ Converted: {results['converted']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"⏭️  Skipped: {results['skipped']}")
        print(f"📄 Total found: {results['total_found']}")

if __name__ == "__main__":
    main()
