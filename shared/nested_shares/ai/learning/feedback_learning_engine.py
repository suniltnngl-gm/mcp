#!/usr/bin/env python3
"""
🧠 AI Orchestra 2.0 - Feedback-Driven Learning Engine
=====================================================

Intelligent learning system that analyzes execution results, conducts case studies,
and adapts improvement suggestions based on feedback and historical data.

Features:
- Execution feedback analysis
- Case study framework
- Pattern recognition and learning
- Adaptive improvement suggestions
- Historical data analysis
- Performance optimization based on learnings
"""

import json
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from expandable_strategic_framework import StrategicFramework


class FeedbackType(Enum):
    EXECUTION_SUCCESS = "execution_success"
    EXECUTION_FAILURE = "execution_failure"
    PERFORMANCE_METRIC = "performance_metric"
    SYSTEM_OBSERVATION = "system_observation"
    USER_FEEDBACK = "user_feedback"
    CASE_STUDY_RESULT = "case_study_result"


class LearningConfidence(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class FeedbackEntry:
    """Individual feedback entry for learning"""

    id: str
    timestamp: str
    feedback_type: FeedbackType
    source_proposal_id: str | None
    category: str
    feedback_data: dict[str, Any]
    confidence: LearningConfidence
    impact_score: float  # 0.0 to 1.0
    learned_patterns: list[str]
    applied_improvements: list[str]


@dataclass
class CaseStudy:
    """Case study for learning and improvement"""

    id: str
    title: str
    description: str
    category: str
    problem_statement: str
    analysis_date: str
    findings: list[str]
    recommendations: list[str]
    implementation_proposals: list[str]
    success_metrics: list[str]
    confidence_level: LearningConfidence
    related_feedback: list[str]


@dataclass
class LearningPattern:
    """Learned pattern from feedback analysis"""

    id: str
    pattern_type: str
    category: str
    description: str
    frequency: int
    confidence: LearningConfidence
    success_rate: float
    recommendations: list[str]
    examples: list[str]


class FeedbackLearningEngine:
    """Main learning engine for feedback-driven improvements"""

    def __init__(self, base_dir: Path = Path(".")):
        self.base_dir = base_dir
        self.framework = StrategicFramework(base_dir)

        # Setup learning directories
        self.learning_dir = base_dir / "learning_engine"
        self.feedback_dir = self.learning_dir / "feedback"
        self.case_studies_dir = self.learning_dir / "case_studies"
        self.patterns_dir = self.learning_dir / "patterns"

        self._ensure_directories()

        # Learning state
        self.feedback_entries: dict[str, FeedbackEntry] = {}
        self.case_studies: dict[str, CaseStudy] = {}
        self.learned_patterns: dict[str, LearningPattern] = {}

        # Learning configuration
        self.learning_config = {
            "min_feedback_for_pattern": 3,
            "confidence_threshold": 0.7,
            "success_rate_threshold": 0.6,
            "max_case_studies": 50,
            "pattern_evolution_rate": 0.1,
        }

        # Load existing learning data
        self._load_learning_data()

    def _ensure_directories(self):
        """Create necessary learning directories"""
        for directory in [
            self.learning_dir,
            self.feedback_dir,
            self.case_studies_dir,
            self.patterns_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def _load_learning_data(self):
        """Load existing learning data"""
        # Load feedback entries
        feedback_file = self.learning_dir / "feedback_entries.json"
        if feedback_file.exists():
            with open(feedback_file) as f:
                data = json.load(f)
                for entry_id, entry_data in data.items():
                    try:
                        # Handle enum values that may be stored as strings
                        feedback_type_value = entry_data["feedback_type"]
                        if isinstance(feedback_type_value, str):
                            # Remove 'FeedbackType.' prefix if present
                            feedback_type_value = feedback_type_value.replace(
                                "FeedbackType.", ""
                            )
                            entry_data["feedback_type"] = FeedbackType(
                                feedback_type_value
                            )
                        else:
                            entry_data["feedback_type"] = FeedbackType(
                                feedback_type_value
                            )

                        confidence_value = entry_data["confidence"]
                        if isinstance(confidence_value, str):
                            # Remove 'LearningConfidence.' prefix if present
                            confidence_value = confidence_value.replace(
                                "LearningConfidence.", ""
                            )
                            entry_data["confidence"] = LearningConfidence(
                                confidence_value
                            )
                        else:
                            entry_data["confidence"] = LearningConfidence(
                                confidence_value
                            )

                        self.feedback_entries[entry_id] = FeedbackEntry(**entry_data)
                    except (ValueError, KeyError) as e:
                        # Skip invalid entries
                        print(
                            f"Warning: Skipping invalid feedback entry {entry_id}: {e}"
                        )
                        continue

        # Load case studies
        case_studies_file = self.learning_dir / "case_studies.json"
        if case_studies_file.exists():
            with open(case_studies_file) as f:
                data = json.load(f)
                for study_id, study_data in data.items():
                    try:
                        confidence_value = study_data["confidence_level"]
                        if isinstance(confidence_value, str):
                            confidence_value = confidence_value.replace(
                                "LearningConfidence.", ""
                            )
                        study_data["confidence_level"] = LearningConfidence(
                            confidence_value
                        )
                        self.case_studies[study_id] = CaseStudy(**study_data)
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Skipping invalid case study {study_id}: {e}")
                        continue

        # Load learned patterns
        patterns_file = self.learning_dir / "learned_patterns.json"
        if patterns_file.exists():
            with open(patterns_file) as f:
                data = json.load(f)
                for pattern_id, pattern_data in data.items():
                    try:
                        confidence_value = pattern_data["confidence"]
                        if isinstance(confidence_value, str):
                            confidence_value = confidence_value.replace(
                                "LearningConfidence.", ""
                            )
                        pattern_data["confidence"] = LearningConfidence(
                            confidence_value
                        )
                        self.learned_patterns[pattern_id] = LearningPattern(
                            **pattern_data
                        )
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Skipping invalid pattern {pattern_id}: {e}")
                        continue

    def _save_learning_data(self):
        """Save learning data to files"""
        # Save feedback entries
        feedback_file = self.learning_dir / "feedback_entries.json"
        feedback_data = {
            entry_id: asdict(entry) for entry_id, entry in self.feedback_entries.items()
        }
        with open(feedback_file, "w") as f:
            json.dump(feedback_data, f, indent=2, default=str)

        # Save case studies
        case_studies_file = self.learning_dir / "case_studies.json"
        studies_data = {
            study_id: asdict(study) for study_id, study in self.case_studies.items()
        }
        with open(case_studies_file, "w") as f:
            json.dump(studies_data, f, indent=2, default=str)

        # Save learned patterns
        patterns_file = self.learning_dir / "learned_patterns.json"
        patterns_data = {
            pattern_id: asdict(pattern)
            for pattern_id, pattern in self.learned_patterns.items()
        }
        with open(patterns_file, "w") as f:
            json.dump(patterns_data, f, indent=2, default=str)

    def add_feedback(
        self,
        feedback_type: FeedbackType,
        category: str,
        feedback_data: dict[str, Any],
        source_proposal_id: str | None = None,
        confidence: LearningConfidence = LearningConfidence.MEDIUM,
        impact_score: float = 0.5,
    ) -> str:
        """Add feedback entry for learning"""

        entry_id = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        feedback_entry = FeedbackEntry(
            id=entry_id,
            timestamp=datetime.now().isoformat(),
            feedback_type=feedback_type,
            source_proposal_id=source_proposal_id,
            category=category,
            feedback_data=feedback_data,
            confidence=confidence,
            impact_score=impact_score,
            learned_patterns=[],
            applied_improvements=[],
        )

        self.feedback_entries[entry_id] = feedback_entry

        # Trigger pattern analysis
        self._analyze_feedback_patterns()

        return entry_id

    def conduct_case_study(
        self, title: str, category: str, problem_statement: str
    ) -> str:
        """Conduct a case study analysis"""

        study_id = f"case_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Analyze the problem based on category
        analysis_results = self._analyze_case_study_problem(problem_statement, category)

        case_study = CaseStudy(
            id=study_id,
            title=title,
            description=f"Case study analyzing {category} issues: {problem_statement}",
            category=category,
            problem_statement=problem_statement,
            analysis_date=datetime.now().isoformat(),
            findings=analysis_results["findings"],
            recommendations=analysis_results["recommendations"],
            implementation_proposals=analysis_results["implementation_proposals"],
            success_metrics=analysis_results["success_metrics"],
            confidence_level=analysis_results["confidence_level"],
            related_feedback=analysis_results["related_feedback"],
        )

        self.case_studies[study_id] = case_study

        # Generate feedback from case study
        self.add_feedback(
            feedback_type=FeedbackType.CASE_STUDY_RESULT,
            category=category,
            feedback_data={
                "case_study_id": study_id,
                "findings_count": len(case_study.findings),
                "recommendations_count": len(case_study.recommendations),
            },
            confidence=case_study.confidence_level,
            impact_score=0.8,
        )

        return study_id

    def _analyze_case_study_problem(
        self, problem_statement: str, category: str
    ) -> dict[str, Any]:
        """Analyze a case study problem and generate insights"""

        findings = []
        recommendations = []
        implementation_proposals = []
        success_metrics = []
        related_feedback = []

        # Analyze based on category
        if "cleanup" in category.lower() or "cleanup" in problem_statement.lower():
            findings.extend(
                [
                    "Complex preparation scripts create maintenance overhead",
                    "Generated artifacts require manual cleanup",
                    "Directory structures become cluttered over time",
                    "Automation scripts should be self-cleaning",
                ]
            )

            recommendations.extend(
                [
                    "Implement automated cleanup procedures",
                    "Use temporary directories for intermediate files",
                    "Create cleanup validation and verification",
                    "Design scripts with cleanup-first approach",
                ]
            )

            implementation_proposals.extend(
                [
                    "Create cleanup automation proposal",
                    "Implement directory lifecycle management",
                    "Add cleanup validation to existing scripts",
                ]
            )

            success_metrics.extend(
                [
                    "Reduced manual cleanup time by 90%",
                    "Zero leftover artifacts after execution",
                    "Automated cleanup success rate > 95%",
                ]
            )

        elif "naming" in category.lower() or "renaming" in problem_statement.lower():
            findings.extend(
                [
                    "Inconsistent naming conventions across project",
                    "Legacy naming patterns reduce readability",
                    "Manual renaming is error-prone and time-consuming",
                    "Naming conventions affect maintainability",
                ]
            )

            recommendations.extend(
                [
                    "Establish consistent naming conventions",
                    "Implement automated renaming tools",
                    "Create naming validation checks",
                    "Develop naming pattern recognition",
                ]
            )

            implementation_proposals.extend(
                [
                    "Create intelligent renaming automation",
                    "Implement naming convention validator",
                    "Add naming pattern analysis tools",
                ]
            )

            success_metrics.extend(
                [
                    "95% naming convention compliance",
                    "Reduced naming-related errors by 80%",
                    "Automated renaming accuracy > 98%",
                ]
            )

        # Find related feedback entries
        for entry in self.feedback_entries.values():
            if category.lower() in entry.category.lower() or any(
                keyword in str(entry.feedback_data).lower()
                for keyword in problem_statement.lower().split()[:3]
            ):
                related_feedback.append(entry.id)

        confidence_level = (
            LearningConfidence.HIGH
            if len(related_feedback) > 2
            else LearningConfidence.MEDIUM
        )

        return {
            "findings": findings,
            "recommendations": recommendations,
            "implementation_proposals": implementation_proposals,
            "success_metrics": success_metrics,
            "confidence_level": confidence_level,
            "related_feedback": related_feedback[:5],  # Limit to top 5
        }

    def _analyze_feedback_patterns(self):
        """Analyze feedback entries to identify patterns"""

        # Group feedback by category
        category_feedback = defaultdict(list)
        for entry in self.feedback_entries.values():
            category_feedback[entry.category].append(entry)

        # Analyze patterns for each category
        for category, entries in category_feedback.items():
            if len(entries) >= self.learning_config["min_feedback_for_pattern"]:
                pattern = self._extract_category_pattern(category, entries)
                if pattern:
                    self.learned_patterns[pattern.id] = pattern

    def _extract_category_pattern(
        self, category: str, entries: list[FeedbackEntry]
    ) -> LearningPattern | None:
        """Extract learning pattern from category feedback"""

        # Calculate success rate
        success_entries = [
            e for e in entries if e.feedback_type == FeedbackType.EXECUTION_SUCCESS
        ]
        failure_entries = [
            e for e in entries if e.feedback_type == FeedbackType.EXECUTION_FAILURE
        ]

        total_executions = len(success_entries) + len(failure_entries)
        success_rate = len(success_entries) / max(total_executions, 1)

        if success_rate < self.learning_config["success_rate_threshold"]:
            return None  # Not enough success to form a pattern

        # Extract common patterns from feedback data
        common_issues = []
        recommendations = []
        examples = []

        # Analyze failure patterns
        failure_reasons = []
        for entry in failure_entries:
            if "error" in entry.feedback_data:
                failure_reasons.append(entry.feedback_data["error"])

        # Find most common failure patterns
        failure_counter = Counter(failure_reasons)
        if failure_counter:
            most_common = failure_counter.most_common(3)
            for reason, count in most_common:
                common_issues.append(
                    f"Common failure: {reason} (occurred {count} times)"
                )

        # Generate recommendations based on success patterns
        success_data = [entry.feedback_data for entry in success_entries]
        if success_data:
            recommendations.extend(
                [
                    f"Success rate: {success_rate:.1%} in {category}",
                    f"Based on {len(success_entries)} successful executions",
                    "Continue applying successful patterns from this category",
                ]
            )

        # Create examples
        examples = [
            f"{entry.feedback_type.value}: {entry.feedback_data}"
            for entry in entries[:3]
        ]

        pattern_id = f"pattern_{category.lower()}_{datetime.now().strftime('%Y%m%d')}"

        return LearningPattern(
            id=pattern_id,
            pattern_type="category_analysis",
            category=category,
            description=f"Learned pattern for {category} based on {len(entries)} feedback entries",
            frequency=len(entries),
            confidence=(
                LearningConfidence.HIGH
                if success_rate > 0.8
                else LearningConfidence.MEDIUM
            ),
            success_rate=success_rate,
            recommendations=recommendations,
            examples=examples,
        )

    def get_adaptive_suggestions(
        self, category: str, proposal_data: dict[str, Any]
    ) -> list[str]:
        """Get adaptive suggestions based on learned patterns"""

        suggestions = []

        # Check learned patterns for this category
        relevant_patterns = [
            pattern
            for pattern in self.learned_patterns.values()
            if pattern.category.lower() == category.lower()
        ]

        for pattern in relevant_patterns:
            if pattern.confidence in [
                LearningConfidence.HIGH,
                LearningConfidence.VERY_HIGH,
            ]:
                suggestions.extend(pattern.recommendations)

        # Check case study recommendations
        relevant_studies = [
            study
            for study in self.case_studies.values()
            if study.category.lower() == category.lower()
        ]

        for study in relevant_studies:
            if study.confidence_level in [
                LearningConfidence.HIGH,
                LearningConfidence.VERY_HIGH,
            ]:
                suggestions.extend(study.recommendations[:2])  # Top 2 recommendations

        return list(set(suggestions))  # Remove duplicates

    def generate_learning_report(self) -> dict[str, Any]:
        """Generate comprehensive learning report"""

        report = {
            "timestamp": datetime.now().isoformat(),
            "learning_summary": {
                "total_feedback_entries": len(self.feedback_entries),
                "total_case_studies": len(self.case_studies),
                "learned_patterns": len(self.learned_patterns),
                "categories_analyzed": len(
                    set(entry.category for entry in self.feedback_entries.values())
                ),
            },
            "feedback_analysis": self._analyze_feedback_distribution(),
            "case_study_insights": self._analyze_case_study_insights(),
            "pattern_effectiveness": self._analyze_pattern_effectiveness(),
            "recommendations": self._generate_learning_recommendations(),
        }

        # Save report
        report_file = (
            self.learning_dir
            / f"learning_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        return report

    def _analyze_feedback_distribution(self) -> dict[str, Any]:
        """Analyze feedback distribution and trends"""

        feedback_by_type = defaultdict(int)
        feedback_by_category = defaultdict(int)

        for entry in self.feedback_entries.values():
            feedback_by_type[entry.feedback_type.value] += 1
            feedback_by_category[entry.category] += 1

        return {
            "by_type": dict(feedback_by_type),
            "by_category": dict(feedback_by_category),
            "confidence_distribution": {
                conf.value: sum(
                    1
                    for entry in self.feedback_entries.values()
                    if entry.confidence == conf
                )
                for conf in LearningConfidence
            },
        }

    def _analyze_case_study_insights(self) -> dict[str, Any]:
        """Analyze insights from case studies"""

        total_findings = sum(
            len(study.findings) for study in self.case_studies.values()
        )
        total_recommendations = sum(
            len(study.recommendations) for study in self.case_studies.values()
        )

        category_studies = defaultdict(int)
        for study in self.case_studies.values():
            category_studies[study.category] += 1

        return {
            "total_findings": total_findings,
            "total_recommendations": total_recommendations,
            "studies_by_category": dict(category_studies),
            "average_findings_per_study": total_findings
            / max(len(self.case_studies), 1),
            "average_recommendations_per_study": total_recommendations
            / max(len(self.case_studies), 1),
        }

    def _analyze_pattern_effectiveness(self) -> dict[str, Any]:
        """Analyze effectiveness of learned patterns"""

        if not self.learned_patterns:
            return {"message": "No learned patterns available"}

        avg_success_rate = statistics.mean(
            pattern.success_rate for pattern in self.learned_patterns.values()
        )
        high_confidence_patterns = sum(
            1
            for pattern in self.learned_patterns.values()
            if pattern.confidence
            in [LearningConfidence.HIGH, LearningConfidence.VERY_HIGH]
        )

        return {
            "average_success_rate": avg_success_rate,
            "high_confidence_patterns": high_confidence_patterns,
            "total_patterns": len(self.learned_patterns),
            "patterns_by_category": {
                category: sum(
                    1
                    for pattern in self.learned_patterns.values()
                    if pattern.category == category
                )
                for category in set(
                    pattern.category for pattern in self.learned_patterns.values()
                )
            },
        }

    def _generate_learning_recommendations(self) -> list[str]:
        """Generate recommendations based on learning analysis"""

        recommendations = []

        # Based on feedback volume
        if len(self.feedback_entries) < 10:
            recommendations.append(
                "Collect more execution feedback to improve learning accuracy"
            )

        # Based on case studies
        if len(self.case_studies) < 3:
            recommendations.append(
                "Conduct more case studies to identify improvement patterns"
            )

        # Based on pattern confidence
        low_confidence_patterns = sum(
            1
            for pattern in self.learned_patterns.values()
            if pattern.confidence == LearningConfidence.LOW
        )

        if low_confidence_patterns > len(self.learned_patterns) * 0.5:
            recommendations.append(
                "Gather more data to improve pattern confidence levels"
            )

        # Category-specific recommendations
        categories = set(entry.category for entry in self.feedback_entries.values())
        if len(categories) < 5:
            recommendations.append(
                "Expand feedback collection across more improvement categories"
            )

        return recommendations


def main():
    """Demonstrate the feedback learning engine"""
    print("🧠 AI Orchestra 2.0 - Feedback-Driven Learning Engine")
    print("=" * 60)

    engine = FeedbackLearningEngine()

    # Simulate some feedback from our cleanup experience
    print("\n📥 Adding feedback from cleanup experience...")

    cleanup_feedback_id = engine.add_feedback(
        feedback_type=FeedbackType.SYSTEM_OBSERVATION,
        category="cleanup",
        feedback_data={
            "observation": "Complex preparation scripts created leftover directories",
            "impact": "Manual cleanup was required",
            "solution": "Automated cleanup tools were needed",
        },
        confidence=LearningConfidence.HIGH,
        impact_score=0.8,
    )

    print(f"✅ Added cleanup feedback: {cleanup_feedback_id}")

    # Conduct Case Study 1: Cleanup Automation
    print("\n📊 Conducting Case Study 1: Cleanup Automation...")

    cleanup_study_id = engine.conduct_case_study(
        title="Automated Cleanup for Strategic Overhaul Preparation",
        category="cleanup",
        problem_statement="Original preparation scripts created complex directory structures and artifacts that required manual cleanup, leading to maintenance overhead and potential inconsistencies.",
    )

    print(f"✅ Completed cleanup case study: {cleanup_study_id}")

    # Get adaptive suggestions for cleanup category
    print("\n🎯 Getting adaptive suggestions for cleanup improvements...")
    suggestions = engine.get_adaptive_suggestions("cleanup", {"type": "automation"})

    if suggestions:
        print("📋 Adaptive Suggestions:")
        for i, suggestion in enumerate(suggestions[:5], 1):
            print(f"  {i}. {suggestion}")

    # Save learning data
    engine._save_learning_data()

    # Generate learning report
    print("\n📊 Generating learning report...")
    report = engine.generate_learning_report()

    print("📊 Learning Report Summary:")
    print(
        f"  • Feedback entries: {report['learning_summary']['total_feedback_entries']}"
    )
    print(f"  • Case studies: {report['learning_summary']['total_case_studies']}")
    print(f"  • Learned patterns: {report['learning_summary']['learned_patterns']}")
    print(
        f"  • Categories analyzed: {report['learning_summary']['categories_analyzed']}"
    )

    print("\n✅ Feedback learning engine demonstration complete!")


if __name__ == "__main__":
    main()
