"""Brain — self-improving lesson cache inspired by Perplexity Brain.

Stores corrections as reusable lessons, links them to source context,
and feeds back into gap detection to suppress known false positives.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HOME = Path.home()
BRAIN_DIR = HOME / ".opencode" / "brain"
LESSONS_FILE = BRAIN_DIR / "lessons.json"
CONTEXT_FILE = BRAIN_DIR / "context_graph.json"


def _ensure_dir():
    BRAIN_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "lessons": [], "context_entries": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"version": 1, "lessons": [], "context_entries": []}


def _save_json(path: Path, data: dict):
    _ensure_dir()
    path.write_text(json.dumps(data, indent=2, default=str))


class LessonCache:
    """Persistent lesson store — tracks corrections and suppresses repeat findings."""

    def __init__(self):
        self.data = _load_json(LESSONS_FILE)
        self.lessons: List[dict] = self.data.get("lessons", [])
        self._dirty = False

    def add_lesson(self, task: str, correction: str, source: str,
                   category: str = "general", suppress: bool = True) -> str:
        lid = f"L{len(self.lessons) + 1:04d}"
        lesson = {
            "id": lid,
            "task": task,
            "correction": correction,
            "source": source,
            "category": category,
            "applied": True,
            "suppress": suppress,
            "suppressed_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.lessons.append(lesson)
        self._dirty = True
        return lid

    def find_lesson(self, task: str, category: str = "") -> Optional[dict]:
        for l in reversed(self.lessons):
            if l["task"] == task:
                if category and l.get("category", "") != category:
                    continue
                return l
            if category and l.get("category", "") == category:
                parts = task.lower().split()
                task_words = l["task"].lower().split()
                if any(w in parts for w in task_words):
                    return l
        return None

    def should_suppress(self, category: str, task: str) -> Tuple[bool, str]:
        lesson = self.find_lesson(task, category)
        if lesson and lesson.get("suppress", True) and lesson.get("applied", True):
            return True, lesson["id"]
        return False, ""

    def record_suppressed(self, lesson_id: str):
        for l in self.lessons:
            if l["id"] == lesson_id:
                l["suppressed_count"] = l.get("suppressed_count", 0) + 1
                l["updated_at"] = datetime.now(timezone.utc).isoformat()
                self._dirty = True
                break

    def stats(self) -> dict:
        return {
            "total_lessons": len(self.lessons),
            "applied": sum(1 for l in self.lessons if l.get("applied")),
            "active_suppressions": sum(1 for l in self.lessons
                                       if l.get("suppress") and l.get("applied")),
            "total_suppressed": sum(l.get("suppressed_count", 0) for l in self.lessons),
        }

    def save(self):
        if self._dirty:
            self.data["lessons"] = self.lessons
            _save_json(LESSONS_FILE, self.data)
            self._dirty = False


class ContextGraph:
    """Traceable context graph — links entries to their source sessions/files.

    Mirrors Perplexity Brain's LLM wiki concept: an automatically built
    web of entries that reference the original sources.
    """

    def __init__(self):
        self.data = _load_json(CONTEXT_FILE)
        self.entries: List[dict] = self.data.get("context_entries", [])
        self._dirty = False

    def add_entry(self, title: str, content: str, source_type: str,
                  source_path: str, tags: Optional[List[str]] = None,
                  repo: str = "", score: float = 1.0):
        eid = f"E{len(self.entries) + 1:04d}"
        entry = {
            "id": eid,
            "title": title,
            "content": content[:500],
            "source_type": source_type,
            "source_path": source_path,
            "tags": tags or [],
            "repo": repo,
            "score": score,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.entries.append(entry)
        self._dirty = True
        return eid

    def link_to_source(self, eid: str) -> Optional[str]:
        """Return the source path for a context entry."""
        for e in self.entries:
            if e["id"] == eid:
                return e.get("source_path")
        return None

    def synthesize_lessons(self, lessons: LessonCache):
        """Overnight step: convert unresolved lessons into context entries."""
        for l in lessons.lessons:
            if l.get("applied") and not any(
                e["title"] == l["task"] for e in self.entries
            ):
                self.add_entry(
                    title=l["task"],
                    content=l["correction"],
                    source_type="lesson",
                    source_path=l["source"],
                    tags=["lesson", l.get("category", "general")],
                )
        self._dirty = True

    def stats(self) -> dict:
        return {
            "total_entries": len(self.entries),
            "by_type": {t: sum(1 for e in self.entries if e["source_type"] == t)
                        for t in set(e["source_type"] for e in self.entries)},
        }

    def save(self):
        if self._dirty:
            self.data["context_entries"] = self.entries
            _save_json(CONTEXT_FILE, self.data)
            self._dirty = False


def overnight_sync():
    """The 'overnight' step — synthesize lessons into context graph."""
    lessons = LessonCache()
    graph = ContextGraph()
    graph.synthesize_lessons(lessons)
    graph.save()
    lessons.save()
    return {"lessons_added": len(lessons.lessons),
            "context_entries": len(graph.entries)}
