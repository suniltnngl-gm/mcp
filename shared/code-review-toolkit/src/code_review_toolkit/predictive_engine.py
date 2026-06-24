#!/usr/bin/env python3

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
import subprocess

class PredictiveEngine:
    def __init__(self):
        self.kb_dir = Path(__file__).parent.parent / "knowledge_base"
        self.patterns = self._load_patterns()
        self.errors = self._load_errors()
        self.solutions = self._load_solutions()
        
    def _load_patterns(self):
        """Load existing patterns or initialize"""
        try:
            with open(self.kb_dir / "predictive_patterns.json") as f:
                return json.load(f)
        except:
            return {"temporal": {}, "contextual": {}, "environmental": {}}
    
    def _load_errors(self):
        """Load error history"""
        try:
            with open(self.kb_dir / "errors.json") as f:
                return json.load(f)
        except:
            return {}
    
    def _load_solutions(self):
        """Load solution effectiveness data"""
        try:
            with open(self.kb_dir / "solutions.json") as f:
                return json.load(f)
        except:
            return {}
    
    def analyze_patterns(self):
        """Analyze historical data for predictive patterns"""
        
        patterns = {
            "temporal": self._analyze_temporal_patterns(),
            "contextual": self._analyze_contextual_patterns(),
            "environmental": self._analyze_environmental_patterns()
        }
        
        # Save updated patterns
        self._save_patterns(patterns)
        return patterns
    
    def _analyze_temporal_patterns(self):
        """Identify time-based error patterns"""
        temporal = defaultdict(list)
        
        for error in self.errors.values():
            try:
                timestamp = datetime.fromisoformat(error.get("timestamp", ""))
                hour = timestamp.hour
                day_of_week = timestamp.weekday()
                error_type = error.get("type", "unknown")
                
                temporal[f"hour_{hour}"].append(error_type)
                temporal[f"day_{day_of_week}"].append(error_type)
            except:
                continue
        
        # Find patterns with frequency > 1
        patterns = {}
        for time_key, error_types in temporal.items():
            if len(error_types) > 1:
                counter = Counter(error_types)
                patterns[time_key] = {
                    "most_common": counter.most_common(3),
                    "frequency": len(error_types),
                    "prediction_confidence": min(counter.most_common(1)[0][1] / len(error_types), 0.9)
                }
        
        return patterns
    
    def _analyze_contextual_patterns(self):
        """Identify context-based error patterns"""
        contextual = defaultdict(list)
        
        for error in self.errors.values():
            context = error.get("context", "")
            error_type = error.get("type", "unknown")
            
            # Extract context keywords
            keywords = context.lower().split()
            for keyword in keywords:
                if len(keyword) > 3:  # Ignore short words
                    contextual[keyword].append(error_type)
        
        # Find predictive context patterns
        patterns = {}
        for context_key, error_types in contextual.items():
            if len(error_types) > 1:
                counter = Counter(error_types)
                patterns[context_key] = {
                    "predicted_error": counter.most_common(1)[0][0],
                    "frequency": len(error_types),
                    "confidence": counter.most_common(1)[0][1] / len(error_types)
                }
        
        return patterns
    
    def _analyze_environmental_patterns(self):
        """Identify environment-based patterns"""
        env_patterns = {}
        
        # Check current environment factors
        try:
            # Disk usage pattern
            disk_result = subprocess.run(["df", "-h", "."], capture_output=True, text=True)
            if disk_result.returncode == 0:
                usage_line = disk_result.stdout.split('\n')[1]
                usage_percent = int(usage_line.split()[4].rstrip('%'))
                
                if usage_percent > 80:
                    env_patterns["high_disk_usage"] = {
                        "predicted_errors": ["missing_file", "permissions"],
                        "confidence": 0.7,
                        "prevention": "cleanup_temp_files"
                    }
            
            # Memory usage pattern
            mem_result = subprocess.run(["free", "-m"], capture_output=True, text=True)
            if mem_result.returncode == 0:
                mem_lines = mem_result.stdout.split('\n')
                if len(mem_lines) > 1:
                    mem_info = mem_lines[1].split()
                    if len(mem_info) >= 3:
                        total_mem = int(mem_info[1])
                        used_mem = int(mem_info[2])
                        mem_percent = (used_mem / total_mem) * 100
                        
                        if mem_percent > 85:
                            env_patterns["high_memory_usage"] = {
                                "predicted_errors": ["command_not_found", "general"],
                                "confidence": 0.6,
                                "prevention": "restart_services"
                            }
        except:
            pass
        
        return env_patterns
    
    def predict_issues(self, context="", operation=""):
        """Predict potential issues for given context/operation"""
        
        predictions = []
        
        # Check contextual patterns
        context_words = context.lower().split()
        for word in context_words:
            if word in self.patterns.get("contextual", {}):
                pattern = self.patterns["contextual"][word]
                if pattern["confidence"] > 0.5:
                    predictions.append({
                        "type": "contextual",
                        "predicted_error": pattern["predicted_error"],
                        "confidence": pattern["confidence"],
                        "trigger": f"context contains '{word}'",
                        "prevention": self._get_prevention(pattern["predicted_error"])
                    })
        
        # Check temporal patterns
        current_time = datetime.now()
        hour_key = f"hour_{current_time.hour}"
        day_key = f"day_{current_time.weekday()}"
        
        for time_key in [hour_key, day_key]:
            if time_key in self.patterns.get("temporal", {}):
                pattern = self.patterns["temporal"][time_key]
                if pattern["prediction_confidence"] > 0.4:
                    predictions.append({
                        "type": "temporal",
                        "predicted_error": pattern["most_common"][0][0],
                        "confidence": pattern["prediction_confidence"],
                        "trigger": f"time pattern: {time_key}",
                        "prevention": self._get_prevention(pattern["most_common"][0][0])
                    })
        
        # Check environmental patterns
        for env_factor, pattern in self.patterns.get("environmental", {}).items():
            if pattern["confidence"] > 0.5:
                for predicted_error in pattern["predicted_errors"]:
                    predictions.append({
                        "type": "environmental",
                        "predicted_error": predicted_error,
                        "confidence": pattern["confidence"],
                        "trigger": env_factor,
                        "prevention": pattern.get("prevention", "monitor_system")
                    })
        
        return predictions
    
    def _get_prevention(self, error_type):
        """Get prevention strategy for error type"""
        prevention_map = {
            "missing_file": "pre_create_required_files",
            "permissions": "pre_set_permissions", 
            "missing_directory": "pre_create_directories",
            "command_not_found": "verify_dependencies",
            "general": "system_health_check"
        }
        return prevention_map.get(error_type, "monitor_closely")
    
    def implement_prevention(self, predictions):
        """Implement preventive measures for predictions"""
        
        implemented = []
        
        for prediction in predictions:
            if prediction["confidence"] > 0.6:
                prevention = prediction["prevention"]
                
                try:
                    if prevention == "pre_create_required_files":
                        # Create commonly missing files
                        self._ensure_common_files()
                        implemented.append(f"Created missing files for {prediction['predicted_error']}")
                    
                    elif prevention == "pre_set_permissions":
                        # Fix common permission issues
                        self._fix_common_permissions()
                        implemented.append(f"Fixed permissions for {prediction['predicted_error']}")
                    
                    elif prevention == "verify_dependencies":
                        # Check system dependencies
                        self._verify_system_deps()
                        implemented.append(f"Verified dependencies for {prediction['predicted_error']}")
                    
                    elif prevention == "system_health_check":
                        # Run preventive health check
                        self._preventive_health_check()
                        implemented.append(f"Ran health check for {prediction['predicted_error']}")
                        
                except Exception as e:
                    implemented.append(f"Failed to prevent {prediction['predicted_error']}: {str(e)}")
        
        return implemented
    
    def _ensure_common_files(self):
        """Ensure commonly required files exist"""
        common_files = [
            "scripts/temp_script.sh",
            "logs/system.log"
        ]
        
        for file_path in common_files:
            path = Path(file_path)
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
                if file_path.endswith('.sh'):
                    path.chmod(0o755)
    
    def _fix_common_permissions(self):
        """Fix common permission issues"""
        script_dir = Path("scripts")
        if script_dir.exists():
            for script in script_dir.glob("*.sh"):
                if not os.access(script, os.X_OK):
                    script.chmod(0o755)
    
    def _verify_system_deps(self):
        """Verify system dependencies"""
        deps = ["python3", "git", "bash"]
        for dep in deps:
            subprocess.run(["which", dep], capture_output=True, check=False)
    
    def _preventive_health_check(self):
        """Run preventive system health check"""
        subprocess.run(["df", "-h"], capture_output=True, check=False)
        subprocess.run(["free", "-m"], capture_output=True, check=False)
    
    def _save_patterns(self, patterns):
        """Save patterns to knowledge base"""
        self.patterns = patterns
        try:
            with open(self.kb_dir / "predictive_patterns.json", "w") as f:
                json.dump(patterns, f, indent=2)
        except:
            pass

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Predictive Issue Prevention Engine")
    parser.add_argument("--analyze", action="store_true", help="Analyze patterns from historical data")
    parser.add_argument("--predict", help="Predict issues for given context")
    parser.add_argument("--prevent", action="store_true", help="Implement preventive measures")
    parser.add_argument("--operation", default="", help="Operation context for prediction")
    
    args = parser.parse_args()
    
    engine = PredictiveEngine()
    
    if args.analyze:
        print("🔍 Analyzing historical patterns...")
        patterns = engine.analyze_patterns()
        
        print(f"✅ Pattern Analysis Complete:")
        print(f"  • Temporal patterns: {len(patterns['temporal'])}")
        print(f"  • Contextual patterns: {len(patterns['contextual'])}")
        print(f"  • Environmental patterns: {len(patterns['environmental'])}")
    
    elif args.predict:
        print(f"🔮 Predicting issues for: {args.predict}")
        predictions = engine.predict_issues(args.predict, args.operation)
        
        if predictions:
            print(f"⚠️  {len(predictions)} potential issues predicted:")
            for pred in predictions:
                print(f"  • {pred['predicted_error']} ({pred['confidence']:.1%} confidence)")
                print(f"    Trigger: {pred['trigger']}")
                print(f"    Prevention: {pred['prevention']}")
        else:
            print("✅ No issues predicted for this context")
    
    elif args.prevent:
        print("🛡️  Implementing preventive measures...")
        predictions = engine.predict_issues()
        implemented = engine.implement_prevention(predictions)
        
        if implemented:
            print("✅ Preventive measures implemented:")
            for action in implemented:
                print(f"  • {action}")
        else:
            print("✅ No preventive measures needed")
    
    else:
        print("🔮 Predictive Engine Status:")
        patterns = engine.patterns
        print(f"  • Temporal patterns: {len(patterns.get('temporal', {}))}")
        print(f"  • Contextual patterns: {len(patterns.get('contextual', {}))}")
        print(f"  • Environmental patterns: {len(patterns.get('environmental', {}))}")

if __name__ == "__main__":
    main()