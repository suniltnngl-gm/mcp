"""Auto-discovering, cross-repo knowledge base indexer.

Scans all active repos, builds a ranked inverted index of terms,
and provides fast unified search across code, docs, KB.md, and osenv/kb.py.
"""

import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


HOME = Path.home()
BASE = HOME / "Public"
INDEX_DIR = HOME / ".opencode" / "autokb"
INDEX_FILE = INDEX_DIR / "index.json"
KB_MD = BASE / ".opencode" / "KB.md"
OSENV_KB = HOME / ".config" / "osenv" / "knowledge.json"

ACTIVE_REPOS: Dict[str, Path] = {
    "Workspace": BASE / "Workspace",
    "project": BASE / "project",
    "repositories": BASE / "repositories",
    ".opencode": BASE / ".opencode",
    "coding-agent": BASE / "coding-agent",
    "next-steps": BASE / "next-steps",
    "shared-tools": BASE / "shared-tools",
    "firebase-app": BASE / "Workspace" / "firebase-app",
}

INCLUDE_EXTS = {".md", ".py", ".js", ".jsx", ".ts", ".tsx", ".sh", ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".env.example", ".txt"}
EXCLUDE_DIRS = {".git", "node_modules", "__pycache__", ".venv", ".ruff_cache", ".pytest_cache", "backups", ".next-step"}
EXCLUDE_PATTERNS = [re.compile(p) for p in [r"\.git/", r"node_modules/", r"\.venv/", r"__pycache__/", r"\.pytest_cache/"]]


@dataclass
class IndexEntry:
    path: str
    repo: str
    ext: str
    lines: int
    mtime: str
    source: str = ""  # traceable source (session, connector, or file ref)
    terms: Dict[str, List[int]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "repo": self.repo,
            "ext": self.ext,
            "lines": self.lines,
            "mtime": self.mtime,
            "source": self.source,
            "terms": self.terms,
        }


@dataclass
class SearchResult:
    path: str
    repo: str
    ext: str
    score: float
    matches: List[Tuple[int, str]]  # (line_num, line_text)
    context_before: List[str] = field(default_factory=list)
    context_after: List[str] = field(default_factory=list)


class AutoKBIndexer:
    def __init__(self):
        self.entries: List[IndexEntry] = []
        self.term_index: Dict[str, List[Tuple[int, List[int]]]] = defaultdict(list)

    def scan(self, force: bool = False) -> int:
        self.entries = []
        self.term_index.clear()
        for repo_name, repo_path in ACTIVE_REPOS.items():
            if not repo_path.exists():
                continue
            self._scan_repo(repo_name, repo_path)
        self._index_kb_md()
        self._index_osenv_kb()
        self._build_term_index()
        self._save()
        return len(self.entries)

    def _scan_repo(self, repo_name: str, repo_path: Path) -> None:
        try:
            import subprocess as sp
            result = sp.run(
                ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                cwd=repo_path, capture_output=True, text=True, timeout=60,
            )
            files = [f for f in result.stdout.splitlines() if f.strip()]
        except Exception:
            files = []
            for p in repo_path.rglob("*"):
                rel = p.relative_to(repo_path)
                if any(pat.search(str(rel)) for pat in EXCLUDE_PATTERNS):
                    continue
                if p.is_file():
                    files.append(str(rel))

        for rel_path in files:
            if not any(rel_path.endswith(ext) for ext in INCLUDE_EXTS):
                continue
            full_path = repo_path / rel_path
            if not full_path.exists() or full_path.stat().st_size == 0:
                continue
            try:
                text = full_path.read_text(encoding="utf-8", errors="replace")
                lines = text.splitlines()
                entry = IndexEntry(
                    path=str(full_path),
                    repo=repo_name,
                    ext=full_path.suffix,
                    lines=len(lines),
                    mtime=datetime.fromtimestamp(
                        full_path.stat().st_mtime, tz=timezone.utc
                    ).isoformat(),
                    source=f"file:{rel_path}",
                    terms=self._extract_terms(text, lines),
                )
                self.entries.append(entry)
            except (OSError, UnicodeDecodeError):
                pass

    def _extract_terms(self, text: str, lines: List[str]) -> Dict[str, List[int]]:
        terms: Dict[str, List[int]] = {}
        word_re = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]{2,}")
        for i, line in enumerate(lines):
            for m in word_re.finditer(line):
                word = m.group().lower()
                if word in terms:
                    if len(terms[word]) < 20:
                        terms[word].append(i)
                else:
                    terms[word] = [i]
        return terms

    def _index_kb_md(self) -> None:
        if not KB_MD.exists():
            return
        try:
            text = KB_MD.read_text(encoding="utf-8")
            lines = text.splitlines()
            entry = IndexEntry(
                path=str(KB_MD),
                repo=".opencode",
                ext=".md",
                lines=len(lines),
                mtime=datetime.fromtimestamp(KB_MD.stat().st_mtime, tz=timezone.utc).isoformat(),
                source="kbfile:.opencode/KB.md",
                terms=self._extract_terms(text, lines),
            )
            self.entries.append(entry)
        except OSError:
            pass

    def _index_osenv_kb(self) -> None:
        if not OSENV_KB.exists():
            return
        try:
            data = json.loads(OSENV_KB.read_text(encoding="utf-8"))
            text = json.dumps(data, indent=2)
            lines = text.splitlines()
            entry = IndexEntry(
                path=str(OSENV_KB),
                repo="osenv",
                ext=".json",
                lines=len(lines),
                mtime=datetime.fromtimestamp(OSENV_KB.stat().st_mtime, tz=timezone.utc).isoformat(),
                source="osenv:kb.json",
                terms=self._extract_terms(text, lines),
            )
            self.entries.append(entry)
        except (OSError, json.JSONDecodeError):
            pass

    def _build_term_index(self) -> None:
        self.term_index.clear()
        for idx, entry in enumerate(self.entries):
            for term, positions in entry.terms.items():
                self.term_index[term].append((idx, positions))

    def _save(self) -> None:
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "version": 2,
            "generated": datetime.now(timezone.utc).isoformat(),
            "repos": list(ACTIVE_REPOS.keys()) + (["osenv"] if OSENV_KB.exists() else []),
            "entries_count": len(self.entries),
            "terms_count": len(self.term_index),
            "entries": [e.to_dict() for e in self.entries],
            "term_index": {t: [(idx, pos) for idx, pos in positions]
                          for t, positions in self.term_index.items()},
        }
        INDEX_FILE.write_text(json.dumps(data, indent=2))
        print(f"Indexed {len(self.entries)} files, {len(self.term_index)} unique terms → {INDEX_FILE}")


class AutoKBSearcher:
    def __init__(self, index_path: Path = INDEX_FILE):
        self.index_path = index_path
        self.data: Optional[dict] = None
        self.entries: List[dict] = []
        self.term_index: Dict[str, List[Tuple[int, List[int]]]] = {}

    def load(self) -> bool:
        if not self.index_path.exists():
            return False
        try:
            self.data = json.loads(self.index_path.read_text(encoding="utf-8"))
            self.entries = self.data.get("entries", [])
            self.term_index = {
                t: [(idx, pos) for idx, pos in positions]
                for t, positions in self.data.get("term_index", {}).items()
            }
            return True
        except (json.JSONDecodeError, OSError):
            return False

    def search(self, query: str, top_k: int = 20) -> List[SearchResult]:
        if not self.data:
            if not self.load():
                return []
        terms = self._tokenize(query)
        if not terms:
            return []
        scored: Dict[int, float] = defaultdict(float)
        match_positions: Dict[int, List[Tuple[str, int]]] = defaultdict(list)
        for term in terms:
            matches = self.term_index.get(term, [])
            for entry_idx, positions in matches:
                entry = self.entries[entry_idx]
                repo_bonus = {"project": 1.0, "osenv": 1.2, ".opencode": 1.3}.get(
                    entry.get("repo", ""), 0.8
                )
                ext_bonus = {".md": 1.5, ".py": 1.2, ".sh": 0.9}.get(
                    entry.get("ext", ""), 0.7
                )
                recency = self._recency_score(entry.get("mtime", ""))
                density = len(positions) / max(entry.get("lines", 1), 1) * 10
                score = (len(positions) * 0.5 + density * 2.0) * repo_bonus * ext_bonus * recency
                scored[entry_idx] += score
                for pos in positions[:3]:
                    match_positions[entry_idx].append((term, pos))

        ranked = sorted(scored.items(), key=lambda x: -x[1])[:top_k]
        results = []
        for entry_idx, score in ranked:
            entry = self.entries[entry_idx]
            path = entry.get("path", "")
            lines_in_file = self._get_lines(path, match_positions.get(entry_idx, []))
            results.append(
                SearchResult(
                    path=path,
                    repo=entry.get("repo", "?"),
                    ext=entry.get("ext", ""),
                    score=round(score, 2),
                    matches=lines_in_file,
                )
            )
        return results

    def search_fast(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """Use ripgrep for instant content search, fallback to index."""
        results = []
        for repo_name, repo_path in ACTIVE_REPOS.items():
            if not repo_path.exists():
                continue
            try:
                rg_result = subprocess.run(
                    ["rg", "-n", "-i", "-g", "!.git", "-g", "!node_modules",
                     "-g", "!.venv", "--max-count", "5", query, str(repo_path)],
                    capture_output=True, text=True, timeout=30,
                )
                file_matches: Dict[str, List[Tuple[int, str]]] = defaultdict(list)
                for line in rg_result.stdout.splitlines():
                    parts = line.split(":", 2)
                    if len(parts) >= 3:
                        file_matches[parts[0]].append((int(parts[1]), parts[2]))
                for fpath, matches in file_matches.items():
                    fpath_p = Path(fpath)
                    ext = fpath_p.suffix
                    repo_bonus = {"project": 1.0, "osenv": 1.2, ".opencode": 1.3}.get(repo_name, 0.8)
                    ext_bonus = {".md": 1.5, ".py": 1.2, ".sh": 0.9}.get(ext, 0.7)
                    score = round(min(len(matches) * 2.0, 10.0) * repo_bonus * ext_bonus, 2)
                    results.append(
                        SearchResult(
                            path=fpath,
                            repo=repo_name,
                            ext=ext,
                            score=score,
                            matches=matches[:3],
                        )
                    )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        results.sort(key=lambda r: -r.score)
        return results[:top_k]

    def _tokenize(self, query: str) -> List[str]:
        words = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{2,}", query.lower())
        stopwords = {"the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
                     "her", "was", "one", "our", "out", "has", "have", "been", "some", "same",
                     "into", "than", "that", "them", "then", "these", "they", "this", "will",
                     "with", "what", "which", "when", "where", "how", "who", "does", "done"}
        return [w for w in words if w not in stopwords and len(w) >= 3]

    def _recency_score(self, mtime_str: str) -> float:
        try:
            mtime = datetime.fromisoformat(mtime_str)
            days_old = (datetime.now(timezone.utc) - mtime).days
            if days_old <= 1:
                return 1.5
            if days_old <= 7:
                return 1.2
            if days_old <= 30:
                return 1.0
            return 0.7
        except (ValueError, TypeError):
            return 1.0

    def _get_lines(self, path: str, term_positions: List[Tuple[str, int]]) -> List[Tuple[int, str]]:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            seen = set()
            result = []
            for _, line_num in term_positions:
                if line_num < len(lines) and line_num not in seen:
                    seen.add(line_num)
                    result.append((line_num + 1, lines[line_num].rstrip()))
            return result[:5]
        except OSError:
            return []


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AutoKB — cross-repo knowledge search")
    parser.add_argument("command", nargs="?", default="search",
                        choices=["scan", "search", "stats"],
                        help="Command: scan (rebuild index), search (query), stats")
    parser.add_argument("query", nargs="*", help="Search query terms")
    parser.add_argument("--top-k", type=int, default=15, help="Max results (default: 15)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--fast", action="store_true", help="Use ripgrep (slower but more precise)")
    parser.add_argument("--explain", action="store_true", help="Add AI explanation of results")

    args = parser.parse_args()

    if args.command == "scan":
        indexer = AutoKBIndexer()
        count = indexer.scan()
        print(f"Indexed {count} files")
        return

    if args.command == "stats":
        indexer = AutoKBIndexer()
        searcher = AutoKBSearcher()
        if searcher.load():
            data = searcher.data
            print(f"Index: {data.get('entries_count', 0)} files, {data.get('terms_count', 0)} terms")
            print(f"Generated: {data.get('generated', '?')}")
            print(f"Repos: {', '.join(data.get('repos', []))}")
            print(f"Index size: {INDEX_FILE.stat().st_size / 1024:.1f} KB")
        else:
            print("No index found. Run 'autokb scan' first.")
        return

    if args.command == "search":
        query = " ".join(args.query) if args.query else ""
        if not query:
            print("Usage: autokb search <query> [--json] [--fast]")
            return
        searcher = AutoKBSearcher()
        if not searcher.load():
            print("No index found. Running scan first...")
            indexer = AutoKBIndexer()
            indexer.scan()
            searcher.load()
        if args.fast:
            results = searcher.search_fast(query, top_k=args.top_k)
        else:
            results = searcher.search(query, top_k=args.top_k)
        if args.json:
            print(json.dumps([
                {"path": r.path, "repo": r.repo, "score": r.score,
                 "matches": [{"line": ln, "text": txt} for ln, txt in r.matches]}
                for r in results
            ], indent=2))
        else:
            if not results:
                print(f"No results for '{query}'")
                return
            print(f"Top {len(results)} results for '{query}':")
            print()
            for r in results:
                print(f"  [{r.repo}] {r.path}")
                print(f"  Score: {r.score}")
                for line_num, line_text in r.matches[:2]:
                    text = line_text[:120].strip()
                    print(f"    L{line_num}: {text}")
                print()
            if args.explain and os.environ.get("OLLAMA_API_KEY"):
                try:
                    from ai_assist.summarize import explain_search_results
                    result_dicts = [
                        {"repo": r.repo, "path": r.path, "score": r.score}
                        for r in results[:5]
                    ]
                    explanation = explain_search_results(query, result_dicts)
                    print(f"  🤖 {explanation}")
                except Exception as e:
                    print(f"  ⚠️  AI explanation unavailable: {e}")


if __name__ == "__main__":
    main()
