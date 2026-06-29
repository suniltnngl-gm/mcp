#!/usr/bin/env python3
"""Semantic Search Grouping - Similarity detection and cross-category search with relevancy ranking"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict, Counter
from dataclasses import dataclass

@dataclass
class SearchResult:
    file_path: str
    category: str
    relevance_score: float
    match_type: str
    snippet: str

class SemanticSearch:
    def __init__(self):
        self.workspace_path = Path("/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares")
        self.file_index = {}
        self.category_profiles = {}
        self.semantic_groups = {}
        self._build_index()
    
    def _build_index(self):
        """Build semantic index of all files"""
        print("🔍 Building semantic index...")
        
        for cat_dir in self.workspace_path.iterdir():
            if not cat_dir.is_dir() or cat_dir.name.startswith('.'):
                continue
            
            category = cat_dir.name
            self.file_index[category] = []
            
            for file_path in cat_dir.rglob("*"):
                if file_path.is_file() and self._is_indexable(file_path):
                    file_info = self._extract_file_info(file_path, category)
                    self.file_index[category].append(file_info)
        
        self._build_category_profiles()
        self._detect_semantic_groups()
    
    def _is_indexable(self, file_path: Path) -> bool:
        """Check if file should be indexed"""
        if file_path.suffix.lower() in ['.py', '.sh', '.md', '.txt', '.json', '.yaml', '.yml']:
            return True
        return False
    
    def _extract_file_info(self, file_path: Path, category: str) -> Dict:
        """Extract semantic information from file"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')[:2000]  # First 2KB
        except:
            content = ""
        
        # Extract keywords from filename and content
        filename_keywords = self._extract_keywords(file_path.name)
        content_keywords = self._extract_keywords(content)
        
        return {
            'path': str(file_path.relative_to(self.workspace_path)),
            'name': file_path.name,
            'category': category,
            'type': file_path.suffix.lower(),
            'keywords': list(set(filename_keywords + content_keywords)),
            'content_preview': content[:200],
            'size': len(content)
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        # Clean and tokenize
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Filter meaningful words
        keywords = []
        for word in words:
            if len(word) > 2 and word not in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use']:
                keywords.append(word)
        
        return keywords[:10]  # Top 10 keywords
    
    def _build_category_profiles(self):
        """Build semantic profiles for each category"""
        for category, files in self.file_index.items():
            all_keywords = []
            file_types = Counter()
            
            for file_info in files:
                all_keywords.extend(file_info['keywords'])
                file_types[file_info['type']] += 1
            
            keyword_freq = Counter(all_keywords)
            
            self.category_profiles[category] = {
                'top_keywords': keyword_freq.most_common(20),
                'file_types': dict(file_types),
                'file_count': len(files),
                'dominant_type': file_types.most_common(1)[0][0] if file_types else 'unknown'
            }
    
    def _detect_semantic_groups(self):
        """Detect semantic similarity groups across categories"""
        categories = list(self.category_profiles.keys())
        
        for i, cat1 in enumerate(categories):
            for cat2 in categories[i+1:]:
                similarity = self._calculate_category_similarity(cat1, cat2)
                
                if similarity > 0.3:  # Threshold for semantic grouping
                    group_name = f"{cat1}-{cat2}"
                    self.semantic_groups[group_name] = {
                        'categories': [cat1, cat2],
                        'similarity': similarity,
                        'shared_keywords': self._get_shared_keywords(cat1, cat2),
                        'suggested_merge': similarity > 0.7
                    }
    
    def _calculate_category_similarity(self, cat1: str, cat2: str) -> float:
        """Calculate semantic similarity between categories"""
        profile1 = self.category_profiles[cat1]
        profile2 = self.category_profiles[cat2]
        
        # Keyword similarity
        keywords1 = set([kw[0] for kw in profile1['top_keywords']])
        keywords2 = set([kw[0] for kw in profile2['top_keywords']])
        
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))
        keyword_sim = intersection / union if union > 0 else 0
        
        # File type similarity
        types1 = set(profile1['file_types'].keys())
        types2 = set(profile2['file_types'].keys())
        type_sim = len(types1.intersection(types2)) / len(types1.union(types2)) if types1.union(types2) else 0
        
        # Combined similarity
        return (keyword_sim * 0.7) + (type_sim * 0.3)
    
    def _get_shared_keywords(self, cat1: str, cat2: str) -> List[str]:
        """Get shared keywords between categories"""
        keywords1 = set([kw[0] for kw in self.category_profiles[cat1]['top_keywords']])
        keywords2 = set([kw[0] for kw in self.category_profiles[cat2]['top_keywords']])
        return list(keywords1.intersection(keywords2))
    
    def semantic_search(self, query: str, max_results: int = 20) -> List[SearchResult]:
        """Perform semantic search across all categories"""
        query_keywords = self._extract_keywords(query)
        results = []
        
        for category, files in self.file_index.items():
            for file_info in files:
                score = self._calculate_relevance(query_keywords, file_info)
                
                if score > 0.1:  # Minimum relevance threshold
                    match_type = self._determine_match_type(query_keywords, file_info)
                    snippet = self._generate_snippet(query, file_info)
                    
                    results.append(SearchResult(
                        file_path=file_info['path'],
                        category=category,
                        relevance_score=score,
                        match_type=match_type,
                        snippet=snippet
                    ))
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:max_results]
    
    def _calculate_relevance(self, query_keywords: List[str], file_info: Dict) -> float:
        """Calculate relevance score for a file"""
        file_keywords = set(file_info['keywords'])
        query_set = set(query_keywords)
        
        if not query_set or not file_keywords:
            return 0.0
        
        # Exact matches
        exact_matches = len(query_set.intersection(file_keywords))
        
        # Partial matches (substring)
        partial_matches = 0
        for q_word in query_keywords:
            for f_word in file_keywords:
                if q_word in f_word or f_word in q_word:
                    partial_matches += 0.5
        
        # Filename bonus
        filename_bonus = 0
        for q_word in query_keywords:
            if q_word in file_info['name'].lower():
                filename_bonus += 0.3
        
        total_score = exact_matches + partial_matches + filename_bonus
        return min(total_score / len(query_keywords), 1.0)
    
    def _determine_match_type(self, query_keywords: List[str], file_info: Dict) -> str:
        """Determine type of match"""
        file_keywords = set(file_info['keywords'])
        query_set = set(query_keywords)
        
        exact_matches = len(query_set.intersection(file_keywords))
        
        if exact_matches >= len(query_keywords) * 0.8:
            return "exact"
        elif exact_matches >= len(query_keywords) * 0.5:
            return "partial"
        else:
            return "related"
    
    def _generate_snippet(self, query: str, file_info: Dict) -> str:
        """Generate relevant snippet from file content"""
        content = file_info['content_preview'].lower()
        query_lower = query.lower()
        
        # Find query in content
        if query_lower in content:
            start = max(0, content.find(query_lower) - 50)
            end = min(len(content), start + 150)
            return "..." + content[start:end] + "..."
        
        # Return first part of content
        return content[:100] + "..." if len(content) > 100 else content
    
    def get_category_suggestions(self, query: str) -> List[str]:
        """Get category suggestions based on query"""
        query_keywords = set(self._extract_keywords(query))
        suggestions = []
        
        for category, profile in self.category_profiles.items():
            category_keywords = set([kw[0] for kw in profile['top_keywords']])
            overlap = len(query_keywords.intersection(category_keywords))
            
            if overlap > 0:
                suggestions.append((category, overlap))
        
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [cat for cat, _ in suggestions[:5]]
    
    def get_semantic_groups(self) -> Dict:
        """Get detected semantic groups"""
        return self.semantic_groups
    
    def get_category_profile(self, category: str) -> Dict:
        """Get semantic profile of a category"""
        return self.category_profiles.get(category, {})
    
    def cross_category_analysis(self) -> Dict:
        """Analyze relationships across categories"""
        analysis = {
            'similar_categories': [],
            'isolated_categories': [],
            'merge_suggestions': [],
            'split_suggestions': []
        }
        
        # Find similar categories
        for group_name, group_info in self.semantic_groups.items():
            if group_info['similarity'] > 0.5:
                analysis['similar_categories'].append({
                    'categories': group_info['categories'],
                    'similarity': group_info['similarity'],
                    'shared_concepts': group_info['shared_keywords'][:5]
                })
                
                if group_info['suggested_merge']:
                    analysis['merge_suggestions'].append({
                        'categories': group_info['categories'],
                        'reason': f"High similarity ({group_info['similarity']:.2f})"
                    })
        
        # Find isolated categories
        grouped_categories = set()
        for group_info in self.semantic_groups.values():
            grouped_categories.update(group_info['categories'])
        
        for category in self.category_profiles.keys():
            if category not in grouped_categories:
                analysis['isolated_categories'].append(category)
        
        # Suggest splits for diverse categories
        for category, profile in self.category_profiles.items():
            if len(profile['file_types']) > 4 and profile['file_count'] > 50:
                analysis['split_suggestions'].append({
                    'category': category,
                    'reason': f"High diversity ({len(profile['file_types'])} types, {profile['file_count']} files)"
                })
        
        return analysis

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 semantic_search.py <command> [args]")
        print("Commands:")
        print("  search <query>     - Semantic search across categories")
        print("  groups             - Show semantic groups")
        print("  profile <category> - Show category profile")
        print("  analyze            - Cross-category analysis")
        print("  suggest <query>    - Get category suggestions")
        return
    
    search = SemanticSearch()
    command = sys.argv[1]
    
    if command == 'search' and len(sys.argv) >= 3:
        query = ' '.join(sys.argv[2:])
        results = search.semantic_search(query)
        
        print(f"🔍 Semantic Search: '{query}'")
        print("=" * 40)
        
        if not results:
            print("No results found")
            return
        
        for i, result in enumerate(results[:10], 1):
            print(f"{i}. {result.file_path}")
            print(f"   📁 {result.category} | 🎯 {result.relevance_score:.2f} | 🔗 {result.match_type}")
            print(f"   💬 {result.snippet}")
            print()
    
    elif command == 'groups':
        groups = search.get_semantic_groups()
        
        print("🔗 Semantic Groups")
        print("=" * 20)
        
        if not groups:
            print("No semantic groups detected")
            return
        
        for group_name, group_info in groups.items():
            print(f"\n📊 {group_name}")
            print(f"   Categories: {', '.join(group_info['categories'])}")
            print(f"   Similarity: {group_info['similarity']:.2f}")
            print(f"   Shared: {', '.join(group_info['shared_keywords'][:5])}")
            if group_info['suggested_merge']:
                print("   💡 Merge suggested")
    
    elif command == 'profile' and len(sys.argv) >= 3:
        category = sys.argv[2]
        profile = search.get_category_profile(category)
        
        if not profile:
            print(f"Category '{category}' not found")
            return
        
        print(f"📊 Category Profile: {category}")
        print("=" * 30)
        print(f"Files: {profile['file_count']}")
        print(f"Dominant type: {profile['dominant_type']}")
        
        print("\nTop keywords:")
        for keyword, freq in profile['top_keywords'][:10]:
            print(f"  • {keyword} ({freq})")
        
        print("\nFile types:")
        for ftype, count in profile['file_types'].items():
            print(f"  • {ftype}: {count}")
    
    elif command == 'analyze':
        analysis = search.cross_category_analysis()
        
        print("🔍 Cross-Category Analysis")
        print("=" * 30)
        
        if analysis['similar_categories']:
            print(f"\n🔗 Similar Categories ({len(analysis['similar_categories'])}):")
            for sim in analysis['similar_categories']:
                print(f"  • {' ↔ '.join(sim['categories'])} ({sim['similarity']:.2f})")
                print(f"    Shared: {', '.join(sim['shared_concepts'])}")
        
        if analysis['merge_suggestions']:
            print(f"\n🔄 Merge Suggestions ({len(analysis['merge_suggestions'])}):")
            for merge in analysis['merge_suggestions']:
                print(f"  • {' + '.join(merge['categories'])}")
                print(f"    Reason: {merge['reason']}")
        
        if analysis['split_suggestions']:
            print(f"\n📈 Split Suggestions ({len(analysis['split_suggestions'])}):")
            for split in analysis['split_suggestions']:
                print(f"  • {split['category']}")
                print(f"    Reason: {split['reason']}")
        
        if analysis['isolated_categories']:
            print(f"\n🏝️ Isolated Categories ({len(analysis['isolated_categories'])}):")
            for cat in analysis['isolated_categories']:
                print(f"  • {cat}")
    
    elif command == 'suggest' and len(sys.argv) >= 3:
        query = ' '.join(sys.argv[2:])
        suggestions = search.get_category_suggestions(query)
        
        print(f"💡 Category Suggestions for: '{query}'")
        print("=" * 40)
        
        if suggestions:
            for i, category in enumerate(suggestions, 1):
                print(f"{i}. {category}")
        else:
            print("No category suggestions found")

if __name__ == "__main__":
    main()
