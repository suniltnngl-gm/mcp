#!/usr/bin/env python3
"""Enhanced KB Manager with merge/priority scoring pseudocode"""
import json
import hashlib
import math
from datetime import datetime
from pathlib import Path


class EnhancedKBManager:
    def __init__(self):
        """Initialize KB manager with thresholds and paths"""
        self.kb_dir = Path("config/knowledge_base")
        self.THRESHOLDS = {
            "AUTO_APPLY": 80,
            "RISK": 0.2,
            "DEDUPE_SIMILARITY": 0.92,
            "CONFIDENCE_BOOST": 0.1,
            "CONFIDENCE_PENALTY": 0.2,
        }

    def semantic_dedupe_and_merge(self, new_entry):
        """Prevent duplicates using content hash + semantic similarity"""
        # Step 1: Check exact content hash
        content_hash = self._compute_content_hash(new_entry)
        existing = self._find_by_hash(content_hash)

        if existing:
            # Exact duplicate - just update metadata
            return self._update_existing(existing, new_entry, "exact_match")

        # Step 2: Semantic similarity check (pseudocode - would use embeddings)
        semantic_candidates = self._find_semantic_candidates(new_entry)

        for candidate in semantic_candidates:
            similarity = self._compute_similarity(
                candidate, new_entry
            )  # Would use embeddings

            if similarity > self.THRESHOLDS["DEDUPE_SIMILARITY"]:
                # Semantic duplicate - merge
                return self._merge_entries(candidate, new_entry, similarity)

        # Step 3: No duplicates found - create new entry
        new_entry["content_hash"] = content_hash
        new_entry["hit_count"] = 1
        new_entry["created_at"] = datetime.now().isoformat()

        return self._store_new_entry(new_entry)

    def calculate_priority_score(self, entry):
        """Calculate priority score for fix application"""
        # Extract factors
        severity_weight = {"critical": 5, "high": 3, "medium": 2, "low": 1}
        severity = severity_weight.get(entry.get("severity", "low"), 1)

        occurrences = entry.get("occurrences", 1)
        impact = entry.get("impact_estimate", 3)
        confidence = entry.get("confidence", 0.5)
        fix_time = entry.get("avg_fix_time_hours", 2)
        regression_risk = entry.get("regression_risk", 0.3)

        # Priority formula
        score = (
            severity * 5  # Severity weight
            + math.log(1 + occurrences) * 3  # Log frequency
            + impact * 4  # Business impact
            + confidence * 2  # Fix confidence
            - fix_time * 2  # Cost penalty
            - regression_risk * 3  # Risk penalty
        )

        return max(0, score)  # Ensure non-negative

    def should_auto_apply(self, entry):
        """Determine if fix should be auto-applied"""
        score = self.calculate_priority_score(entry)
        risk = entry.get("regression_risk", 0.5)

        return score > self.THRESHOLDS["AUTO_APPLY"] and risk < self.THRESHOLDS["RISK"]

    def update_confidence_from_outcome(self, entry_id, success):
        """Update confidence based on fix outcome"""
        entry = self._load_entry(entry_id)
        if not entry:
            return

        if success:
            entry["confidence"] = min(
                1.0, entry.get("confidence", 0.5) + self.THRESHOLDS["CONFIDENCE_BOOST"]
            )
            entry["success_count"] = entry.get("success_count", 0) + 1
        else:
            entry["confidence"] = max(
                0.0,
                entry.get("confidence", 0.5) - self.THRESHOLDS["CONFIDENCE_PENALTY"],
            )
            entry["failure_count"] = entry.get("failure_count", 0) + 1

        # Update regression risk based on failure rate
        total_attempts = entry.get("success_count", 0) + entry.get("failure_count", 0)
        if total_attempts > 0:
            failure_rate = entry.get("failure_count", 0) / total_attempts
            entry["regression_risk"] = min(1.0, failure_rate * 2)  # Scale failure rate

        self._save_entry(entry_id, entry)

    def get_prioritized_fixes(self, limit=10):
        """Get top priority fixes for application"""
        all_entries = self._load_all_entries()

        # Calculate scores and sort
        scored_entries = []
        for entry_id, entry in all_entries.items():
            score = self.calculate_priority_score(entry)
            scored_entries.append(
                {
                    "id": entry_id,
                    "entry": entry,
                    "priority_score": score,
                    "auto_apply": self.should_auto_apply(entry),
                }
            )

        # Sort by priority score
        scored_entries.sort(key=lambda x: x["priority_score"], reverse=True)

        return scored_entries[:limit]

    def _compute_content_hash(self, entry):
        """Compute SHA256 hash of normalized content"""
        # Normalize content for hashing
        normalized = {
            "pattern": entry.get("pattern", ""),
            "root_cause": entry.get("root_cause", ""),
            "fix_template": entry.get("fix_template", ""),
        }

        content = json.dumps(normalized, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def _find_semantic_candidates(self, new_entry):
        """Find semantically similar entries (pseudocode)"""
        # In real implementation, would use vector database
        # candidates = vector_db.query(
        #     vector=embed(new_entry.text),
        #     top_k=5,
        #     threshold=0.8
        # )

        # For now, return empty list (placeholder)
        return []

    def _compute_similarity(self, entry1, entry2):
        """Compute semantic similarity (pseudocode)"""
        # In real implementation:
        # vec1 = embed(entry1.text)
        # vec2 = embed(entry2.text)
        # return cosine_similarity(vec1, vec2)

        # Placeholder: simple text similarity
        text1 = f"{entry1.get('pattern', '')} {entry1.get('root_cause', '')}"
        text2 = f"{entry2.get('pattern', '')} {entry2.get('root_cause', '')}"

        # Simple Jaccard similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 and not words2:
            return 1.0

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0.0

    def _merge_entries(self, existing, new_entry, similarity):
        """Merge similar entries"""
        # Increment hit count
        existing["hit_count"] = existing.get("hit_count", 1) + 1
        existing["last_seen_at"] = datetime.now().isoformat()

        # Add source reference
        if "source_refs" not in existing:
            existing["source_refs"] = []

        new_source = new_entry.get("source_refs", ["unknown"])[0]
        if new_source not in existing["source_refs"]:
            existing["source_refs"].append(new_source)

        # Weighted average confidence
        old_confidence = existing.get("confidence", 0.5)
        new_confidence = new_entry.get("confidence", 0.5)
        existing["confidence"] = (old_confidence + new_confidence * similarity) / 2

        return existing["id"]

    def _load_all_entries(self):
        """Load all KB entries"""
        kb_file = self.kb_dir / "enhanced_kb.json"
        if kb_file.exists():
            try:
                with open(kb_file) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError, OSError):
                return {}
        return {}

    def _load_entry(self, entry_id):
        """Load single KB entry"""
        all_entries = self._load_all_entries()
        return all_entries.get(entry_id)

    def _save_entry(self, entry_id, entry):
        """Save single KB entry"""
        all_entries = self._load_all_entries()
        all_entries[entry_id] = entry

        kb_file = self.kb_dir / "enhanced_kb.json"
        self.kb_dir.mkdir(parents=True, exist_ok=True)
        with open(kb_file, "w") as f:
            json.dump(all_entries, f, indent=2)


# Example usage and testing
def demo_priority_scoring():
    """Demonstrate priority scoring"""
    kb = EnhancedKBManager()

    # Example entries
    test_entries = [
        {
            "id": "critical_security",
            "severity": "critical",
            "occurrences": 5,
            "impact_estimate": 5,
            "confidence": 0.9,
            "avg_fix_time_hours": 1,
            "regression_risk": 0.1,
        },
        {
            "id": "frequent_low_impact",
            "severity": "low",
            "occurrences": 20,
            "impact_estimate": 2,
            "confidence": 0.8,
            "avg_fix_time_hours": 0.5,
            "regression_risk": 0.05,
        },
    ]

    print("🎯 Priority Scoring Demo:")
    for entry in test_entries:
        score = kb.calculate_priority_score(entry)
        auto_apply = kb.should_auto_apply(entry)

        print(f"  {entry['id']}: score={score:.1f}, auto_apply={auto_apply}")


if __name__ == "__main__":
    demo_priority_scoring()
