#!/usr/bin/env python3
"""AI Task Classifier - Analyze task complexity and route to optimal provider"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Import existing systems
try:
    from smart_ai_router import SmartAIRouter
    from enhanced_health_monitor import EnhancedHealthMonitor
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

class TaskComplexity(str, Enum):
    """Task complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"

class TaskCategory(str, Enum):
    """Task categories for classification"""
    TEXT_GENERATION = "text_generation"
    CODE_ANALYSIS = "code_analysis"
    DECISION_MAKING = "decision_making"
    CREATIVE_WRITING = "creative_writing"
    DATA_ANALYSIS = "data_analysis"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"

@dataclass
class TaskFeatures:
    """Features extracted from task for classification"""
    text_length: int
    code_blocks: int
    technical_terms: int
    question_count: int
    complexity_indicators: List[str]
    domain_specific: bool
    requires_reasoning: bool
    creative_elements: bool

@dataclass
class TaskClassification:
    """Result of task classification"""
    task_id: str
    complexity: TaskComplexity
    category: TaskCategory
    confidence: float
    features: TaskFeatures
    recommended_provider: str
    alternative_providers: List[str]
    reasoning: str
    estimated_cost: float
    estimated_time: float

class AITaskClassifier:
    """Intelligent task classifier for optimal provider routing"""
    
    # Complexity indicators
    SIMPLE_INDICATORS = [
        "format", "fix typo", "simple question", "basic", "straightforward",
        "quick", "brief", "short", "yes/no", "true/false"
    ]
    
    MODERATE_INDICATORS = [
        "analyze", "compare", "explain", "describe", "summarize", "review",
        "evaluate", "discuss", "outline", "plan", "design"
    ]
    
    COMPLEX_INDICATORS = [
        "architect", "optimize", "refactor", "debug complex", "research",
        "comprehensive analysis", "strategic", "multi-step", "algorithm",
        "system design", "performance tuning", "security audit"
    ]
    
    # Technical terms that indicate complexity
    TECHNICAL_TERMS = [
        "algorithm", "architecture", "database", "api", "framework",
        "microservices", "kubernetes", "docker", "aws", "cloud",
        "machine learning", "ai", "neural network", "optimization",
        "scalability", "performance", "security", "encryption"
    ]
    
    def __init__(self):
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Required dependencies not available")
        
        self.ai_router = SmartAIRouter()
        self.health_monitor = EnhancedHealthMonitor()
        self.classification_history = []
    
    def extract_features(self, task_text: str) -> TaskFeatures:
        """Extract features from task text for classification"""
        text_lower = task_text.lower()
        
        # Basic metrics
        text_length = len(task_text)
        code_blocks = len(re.findall(r'```[\s\S]*?```|`[^`]+`', task_text))
        question_count = text_lower.count('?')
        
        # Technical complexity
        technical_terms = sum(1 for term in self.TECHNICAL_TERMS if term in text_lower)
        
        # Complexity indicators
        complexity_indicators = []
        for indicator in self.SIMPLE_INDICATORS:
            if indicator in text_lower:
                complexity_indicators.append(f"simple:{indicator}")
        
        for indicator in self.MODERATE_INDICATORS:
            if indicator in text_lower:
                complexity_indicators.append(f"moderate:{indicator}")
        
        for indicator in self.COMPLEX_INDICATORS:
            if indicator in text_lower:
                complexity_indicators.append(f"complex:{indicator}")
        
        # Domain and reasoning analysis
        domain_specific = technical_terms > 2 or any(term in text_lower for term in [
            "specific", "domain", "specialized", "expert", "professional"
        ])
        
        requires_reasoning = any(term in text_lower for term in [
            "why", "how", "analyze", "reason", "logic", "because", "therefore",
            "compare", "contrast", "evaluate", "assess"
        ])
        
        creative_elements = any(term in text_lower for term in [
            "creative", "story", "poem", "write", "compose", "generate",
            "brainstorm", "imagine", "invent"
        ])
        
        return TaskFeatures(
            text_length=text_length,
            code_blocks=code_blocks,
            technical_terms=technical_terms,
            question_count=question_count,
            complexity_indicators=complexity_indicators,
            domain_specific=domain_specific,
            requires_reasoning=requires_reasoning,
            creative_elements=creative_elements
        )
    
    def classify_complexity(self, features: TaskFeatures) -> Tuple[TaskComplexity, float]:
        """Classify task complexity based on features"""
        score = 0
        confidence_factors = []
        
        # Text length scoring
        if features.text_length > 1000:
            score += 2
            confidence_factors.append("long_text")
        elif features.text_length > 200:
            score += 1
            confidence_factors.append("medium_text")
        
        # Code complexity
        if features.code_blocks > 0:
            score += features.code_blocks
            confidence_factors.append("code_present")
        
        # Technical terms
        if features.technical_terms > 5:
            score += 3
            confidence_factors.append("highly_technical")
        elif features.technical_terms > 2:
            score += 2
            confidence_factors.append("technical")
        elif features.technical_terms > 0:
            score += 1
            confidence_factors.append("some_technical")
        
        # Complexity indicators
        complex_count = sum(1 for ind in features.complexity_indicators if ind.startswith("complex:"))
        moderate_count = sum(1 for ind in features.complexity_indicators if ind.startswith("moderate:"))
        simple_count = sum(1 for ind in features.complexity_indicators if ind.startswith("simple:"))
        
        score += complex_count * 3 + moderate_count * 2 - simple_count
        
        # Domain and reasoning
        if features.domain_specific:
            score += 2
            confidence_factors.append("domain_specific")
        
        if features.requires_reasoning:
            score += 2
            confidence_factors.append("requires_reasoning")
        
        # Determine complexity
        if score >= 8:
            complexity = TaskComplexity.COMPLEX
            confidence = min(0.95, 0.6 + (score - 8) * 0.05)
        elif score >= 4:
            complexity = TaskComplexity.MODERATE
            confidence = min(0.9, 0.5 + (score - 4) * 0.1)
        else:
            complexity = TaskComplexity.SIMPLE
            confidence = min(0.85, 0.4 + max(0, 4 - score) * 0.1)
        
        return complexity, confidence
    
    def classify_category(self, task_text: str, features: TaskFeatures) -> TaskCategory:
        """Classify task category based on content"""
        text_lower = task_text.lower()
        
        # Code analysis
        if features.code_blocks > 0 or any(term in text_lower for term in [
            "code", "function", "class", "method", "variable", "bug", "debug"
        ]):
            return TaskCategory.CODE_ANALYSIS
        
        # Decision making
        if any(term in text_lower for term in [
            "decide", "choose", "recommend", "should", "better", "option",
            "alternative", "pros and cons", "evaluate"
        ]):
            return TaskCategory.DECISION_MAKING
        
        # Creative writing
        if features.creative_elements or any(term in text_lower for term in [
            "story", "poem", "creative", "write", "compose", "narrative"
        ]):
            return TaskCategory.CREATIVE_WRITING
        
        # Data analysis
        if any(term in text_lower for term in [
            "data", "analyze", "statistics", "metrics", "chart", "graph",
            "trend", "pattern", "correlation"
        ]):
            return TaskCategory.DATA_ANALYSIS
        
        # Translation
        if any(term in text_lower for term in [
            "translate", "translation", "language", "french", "spanish",
            "german", "chinese", "japanese"
        ]):
            return TaskCategory.TRANSLATION
        
        # Summarization
        if any(term in text_lower for term in [
            "summarize", "summary", "brief", "overview", "key points",
            "main ideas", "tldr"
        ]):
            return TaskCategory.SUMMARIZATION
        
        # Question answering
        if features.question_count > 0 or any(term in text_lower for term in [
            "what", "how", "why", "when", "where", "who", "explain"
        ]):
            return TaskCategory.QUESTION_ANSWERING
        
        # Default to text generation
        return TaskCategory.TEXT_GENERATION
    
    def select_optimal_provider(self, complexity: TaskComplexity, 
                              category: TaskCategory) -> Tuple[str, List[str], str]:
        """Select optimal provider based on classification"""
        # Get current provider health
        dashboard = self.health_monitor.generate_dashboard_data()
        healthy_providers = [
            p for p in dashboard["providers"] 
            if p["health"]["status"] == "healthy"
        ]
        
        if not healthy_providers:
            return "openrouter-free", [], "No healthy providers available, using fallback"
        
        # Provider preferences by complexity and category
        provider_preferences = {
            TaskComplexity.SIMPLE: {
                "preferred": ["openrouter-free", "gemini-flash"],
                "acceptable": ["claude-haiku", "gpt-3.5"]
            },
            TaskComplexity.MODERATE: {
                "preferred": ["gemini-flash", "claude-haiku"],
                "acceptable": ["gpt-3.5", "claude-sonnet"]
            },
            TaskComplexity.COMPLEX: {
                "preferred": ["claude-sonnet", "gpt-4"],
                "acceptable": ["claude-haiku", "gemini-flash"]
            }
        }
        
        # Category-specific adjustments
        if category == TaskCategory.CODE_ANALYSIS:
            if complexity == TaskComplexity.SIMPLE:
                provider_preferences[complexity]["preferred"] = ["gemini-flash", "claude-haiku"]
        elif category == TaskCategory.CREATIVE_WRITING:
            provider_preferences[complexity]["preferred"].insert(0, "claude-sonnet")
        
        preferences = provider_preferences.get(complexity, provider_preferences[TaskComplexity.MODERATE])
        
        # Find best available provider
        healthy_provider_names = [p["health"]["provider"] for p in healthy_providers]
        
        # Try preferred providers first
        for provider in preferences["preferred"]:
            if provider in healthy_provider_names:
                alternatives = [p for p in preferences["acceptable"] if p in healthy_provider_names and p != provider]
                return provider, alternatives[:3], f"Optimal for {complexity} {category} tasks"
        
        # Fall back to acceptable providers
        for provider in preferences["acceptable"]:
            if provider in healthy_provider_names:
                alternatives = [p for p in preferences["preferred"] if p in healthy_provider_names and p != provider]
                return provider, alternatives[:3], f"Acceptable for {complexity} {category} tasks"
        
        # Last resort - any healthy provider
        best_provider = healthy_provider_names[0]
        return best_provider, healthy_provider_names[1:4], "Using available healthy provider"
    
    def classify_task(self, task_text: str, task_id: str = None) -> TaskClassification:
        """Classify a task and recommend optimal provider"""
        if not task_id:
            task_id = f"task-{int(datetime.now().timestamp())}"
        
        # Extract features
        features = self.extract_features(task_text)
        
        # Classify complexity and category
        complexity, confidence = self.classify_complexity(features)
        category = self.classify_category(task_text, features)
        
        # Select optimal provider
        recommended_provider, alternatives, reasoning = self.select_optimal_provider(complexity, category)
        
        # Estimate cost and time
        estimated_cost = self.ai_router.estimate_cost(
            recommended_provider, 
            len(task_text), 
            len(task_text) * 2  # Rough output estimate
        )
        
        # Time estimation based on complexity
        time_estimates = {
            TaskComplexity.SIMPLE: 2.0,
            TaskComplexity.MODERATE: 5.0,
            TaskComplexity.COMPLEX: 15.0
        }
        estimated_time = time_estimates.get(complexity, 5.0)
        
        classification = TaskClassification(
            task_id=task_id,
            complexity=complexity,
            category=category,
            confidence=confidence,
            features=features,
            recommended_provider=recommended_provider,
            alternative_providers=alternatives,
            reasoning=reasoning,
            estimated_cost=estimated_cost,
            estimated_time=estimated_time
        )
        
        # Store in history
        self.classification_history.append(classification)
        
        return classification
    
    def get_classification_stats(self) -> Dict:
        """Get statistics about classification history"""
        if not self.classification_history:
            return {"error": "No classification history available"}
        
        total = len(self.classification_history)
        
        # Complexity distribution
        complexity_counts = {}
        for classification in self.classification_history:
            complexity_counts[classification.complexity] = complexity_counts.get(classification.complexity, 0) + 1
        
        # Category distribution
        category_counts = {}
        for classification in self.classification_history:
            category_counts[classification.category] = category_counts.get(classification.category, 0) + 1
        
        # Provider usage
        provider_counts = {}
        for classification in self.classification_history:
            provider = classification.recommended_provider
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
        
        # Average confidence
        avg_confidence = sum(c.confidence for c in self.classification_history) / total
        
        return {
            "total_classifications": total,
            "complexity_distribution": {k: (v/total)*100 for k, v in complexity_counts.items()},
            "category_distribution": {k: (v/total)*100 for k, v in category_counts.items()},
            "provider_usage": {k: (v/total)*100 for k, v in provider_counts.items()},
            "average_confidence": avg_confidence,
            "total_estimated_cost": sum(c.estimated_cost for c in self.classification_history),
            "total_estimated_time": sum(c.estimated_time for c in self.classification_history)
        }

def main():
    """CLI interface for task classification"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ai_task_classifier.py <command> [args...]")
        print("Commands:")
        print("  classify <task_text> - Classify a task")
        print("  classify-file <file_path> - Classify task from file")
        print("  stats - Show classification statistics")
        print("  test - Run test classifications")
        return
    
    if not DEPENDENCIES_AVAILABLE:
        print("Error: Required dependencies not available")
        return
    
    classifier = AITaskClassifier()
    command = sys.argv[1]
    
    if command == "classify":
        if len(sys.argv) < 3:
            print("Usage: classify <task_text>")
            return
        
        task_text = sys.argv[2]
        classification = classifier.classify_task(task_text)
        print(json.dumps(asdict(classification), indent=2))
    
    elif command == "classify-file":
        if len(sys.argv) < 3:
            print("Usage: classify-file <file_path>")
            return
        
        file_path = Path(sys.argv[2])
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return
        
        task_text = file_path.read_text()
        classification = classifier.classify_task(task_text, f"file-{file_path.name}")
        print(json.dumps(asdict(classification), indent=2))
    
    elif command == "stats":
        stats = classifier.get_classification_stats()
        print(json.dumps(stats, indent=2))
    
    elif command == "test":
        # Test with sample tasks
        test_tasks = [
            "Fix this typo in the word 'recieve'",
            "Analyze the performance implications of using microservices vs monolith architecture",
            "Write a creative story about a robot learning to paint",
            "Summarize the key points from this 500-word article",
            "Debug this complex algorithm that's causing memory leaks in production"
        ]
        
        for i, task in enumerate(test_tasks, 1):
            print(f"\n=== Test {i} ===")
            classification = classifier.classify_task(task, f"test-{i}")
            print(f"Task: {task}")
            print(f"Complexity: {classification.complexity}")
            print(f"Category: {classification.category}")
            print(f"Provider: {classification.recommended_provider}")
            print(f"Confidence: {classification.confidence:.2f}")
            print(f"Cost: ${classification.estimated_cost:.4f}")

if __name__ == "__main__":
    main()
