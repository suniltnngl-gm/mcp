#!/usr/bin/env python3
"""Quick Start Improvements - Immediate next steps implementation"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class ImprovementStarter:
    """Bootstrap immediate improvements to the AI orchestration platform"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.improvements_completed = []
    
    def setup_api_key_management(self) -> Dict:
        """Setup secure API key management system"""
        print("🔑 Setting up API key management...")
        
        # Create secure configuration directory
        config_dir = self.base_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Create environment template
        env_template = """# AI Orchestration Platform - API Keys
# Copy this file to .env and add your actual API keys

# OpenRouter (Free tier available)
OPENROUTER_API_KEY=your_openrouter_key_here

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_key_here

# OpenAI
OPENAI_API_KEY=your_openai_key_here

# Google Gemini
GOOGLE_API_KEY=your_google_key_here

# Configuration
DEFAULT_PROVIDER=openrouter-free
ENABLE_CACHING=true
CACHE_TTL_HOURS=24
MAX_RETRIES=3
TIMEOUT_SECONDS=30
"""
        
        env_file = self.base_dir / ".env.template"
        env_file.write_text(env_template)
        
        # Create API key manager
        api_manager_code = '''#!/usr/bin/env python3
"""API Key Manager - Secure key management for AI providers"""

import os
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass

@dataclass
class ProviderConfig:
    """Configuration for AI provider"""
    api_key: str
    base_url: str
    timeout: int = 30
    max_retries: int = 3

class APIKeyManager:
    """Secure API key management"""
    
    def __init__(self, env_file: str = ".env"):
        self.env_file = Path(env_file)
        self.providers = self._load_provider_configs()
    
    def _load_provider_configs(self) -> Dict[str, ProviderConfig]:
        """Load provider configurations from environment"""
        # Load .env file if exists
        if self.env_file.exists():
            self._load_env_file()
        
        return {
            "openrouter-free": ProviderConfig(
                api_key=os.getenv("OPENROUTER_API_KEY", ""),
                base_url="https://openrouter.ai/api/v1"
            ),
            "claude-sonnet": ProviderConfig(
                api_key=os.getenv("ANTHROPIC_API_KEY", ""),
                base_url="https://api.anthropic.com"
            ),
            "gpt-4": ProviderConfig(
                api_key=os.getenv("OPENAI_API_KEY", ""),
                base_url="https://api.openai.com/v1"
            ),
            "gemini-flash": ProviderConfig(
                api_key=os.getenv("GOOGLE_API_KEY", ""),
                base_url="https://generativelanguage.googleapis.com"
            )
        }
    
    def _load_env_file(self):
        """Load environment variables from .env file"""
        with open(self.env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value
    
    def get_provider_config(self, provider: str) -> Optional[ProviderConfig]:
        """Get configuration for specific provider"""
        return self.providers.get(provider)
    
    def is_provider_configured(self, provider: str) -> bool:
        """Check if provider is properly configured"""
        config = self.get_provider_config(provider)
        return config is not None and bool(config.api_key)
    
    def get_configured_providers(self) -> List[str]:
        """Get list of properly configured providers"""
        return [
            provider for provider in self.providers
            if self.is_provider_configured(provider)
        ]

# Global instance
api_key_manager = APIKeyManager()
'''
        
        api_manager_file = self.base_dir / "api_key_manager.py"
        api_manager_file.write_text(api_manager_code)
        
        self.improvements_completed.append("api_key_management")
        
        return {
            "status": "completed",
            "files_created": [str(env_file), str(api_manager_file)],
            "next_steps": [
                "Copy .env.template to .env",
                "Add your actual API keys to .env",
                "Test with: python3 -c 'from api_key_manager import api_key_manager; print(api_key_manager.get_configured_providers())'"
            ]
        }
    
    def setup_caching_system(self) -> Dict:
        """Setup intelligent caching system"""
        print("💾 Setting up caching system...")
        
        # Create cache directory
        cache_dir = self.base_dir / "cache"
        cache_dir.mkdir(exist_ok=True)
        
        # Create cache manager
        cache_manager_code = '''#!/usr/bin/env python3
"""Cache Manager - Intelligent caching for AI responses"""

import json
import hashlib
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional, Dict

class IntelligentCache:
    """Multi-tier caching system for AI responses"""
    
    def __init__(self, cache_dir: str = "cache", default_ttl: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.default_ttl = default_ttl
        self.memory_cache = {}  # L1 cache (fastest)
        self.max_memory_items = 1000
    
    def _generate_cache_key(self, provider: str, prompt: str, params: Dict = None) -> str:
        """Generate unique cache key for request"""
        content = f"{provider}:{prompt}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cache_file(self, cache_key: str) -> Path:
        """Get cache file path for key"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, provider: str, prompt: str, params: Dict = None) -> Optional[Dict]:
        """Get cached response if available and valid"""
        cache_key = self._generate_cache_key(provider, prompt, params)
        
        # Check L1 cache (memory)
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if entry["expires_at"] > time.time():
                return entry["data"]
            else:
                del self.memory_cache[cache_key]
        
        # Check L2 cache (file)
        cache_file = self._get_cache_file(cache_key)
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    entry = json.load(f)
                
                if entry["expires_at"] > time.time():
                    # Promote to L1 cache
                    self._add_to_memory_cache(cache_key, entry)
                    return entry["data"]
                else:
                    # Expired, remove file
                    cache_file.unlink()
            except (json.JSONDecodeError, KeyError):
                # Corrupted cache file, remove it
                cache_file.unlink()
        
        return None
    
    def set(self, provider: str, prompt: str, response: Dict, 
            params: Dict = None, ttl: int = None) -> bool:
        """Cache response with TTL"""
        cache_key = self._generate_cache_key(provider, prompt, params)
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl
        
        entry = {
            "data": response,
            "created_at": time.time(),
            "expires_at": expires_at,
            "provider": provider,
            "ttl": ttl
        }
        
        # Store in L1 cache (memory)
        self._add_to_memory_cache(cache_key, entry)
        
        # Store in L2 cache (file)
        cache_file = self._get_cache_file(cache_key)
        try:
            with open(cache_file, 'w') as f:
                json.dump(entry, f)
            return True
        except Exception as e:
            print(f"Cache write error: {e}")
            return False
    
    def _add_to_memory_cache(self, cache_key: str, entry: Dict):
        """Add entry to memory cache with size limit"""
        # Remove oldest entries if at limit
        if len(self.memory_cache) >= self.max_memory_items:
            oldest_key = min(self.memory_cache.keys(), 
                           key=lambda k: self.memory_cache[k]["created_at"])
            del self.memory_cache[oldest_key]
        
        self.memory_cache[cache_key] = entry
    
    def clear_expired(self) -> int:
        """Clear expired cache entries"""
        current_time = time.time()
        removed_count = 0
        
        # Clear memory cache
        expired_keys = [
            key for key, entry in self.memory_cache.items()
            if entry["expires_at"] <= current_time
        ]
        for key in expired_keys:
            del self.memory_cache[key]
            removed_count += 1
        
        # Clear file cache
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file) as f:
                    entry = json.load(f)
                
                if entry["expires_at"] <= current_time:
                    cache_file.unlink()
                    removed_count += 1
            except (json.JSONDecodeError, KeyError):
                # Corrupted file, remove it
                cache_file.unlink()
                removed_count += 1
        
        return removed_count
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        file_count = len(list(self.cache_dir.glob("*.json")))
        memory_count = len(self.memory_cache)
        
        return {
            "memory_cache_size": memory_count,
            "file_cache_size": file_count,
            "total_cached_items": memory_count + file_count,
            "cache_directory": str(self.cache_dir),
            "memory_limit": self.max_memory_items
        }

# Global cache instance
intelligent_cache = IntelligentCache()
'''
        
        cache_manager_file = self.base_dir / "cache_manager.py"
        cache_manager_file.write_text(cache_manager_code)
        
        self.improvements_completed.append("caching_system")
        
        return {
            "status": "completed",
            "files_created": [str(cache_manager_file)],
            "cache_directory": str(cache_dir),
            "next_steps": [
                "Test caching: python3 -c 'from cache_manager import intelligent_cache; print(intelligent_cache.get_stats())'",
                "Integrate with AI responses in integrated_ai_discussion.py"
            ]
        }
    
    def setup_logging_system(self) -> Dict:
        """Setup comprehensive logging system"""
        print("📝 Setting up logging system...")
        
        # Create logs directory
        logs_dir = self.base_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Create logging configuration
        logging_config = '''#!/usr/bin/env python3
"""Logging Configuration - Structured logging for AI orchestration"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class StructuredLogger:
    """Structured logging with JSON format"""
    
    def __init__(self, name: str, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Add structured file handler
        log_file = self.log_dir / f"{name}.log"
        handler = logging.FileHandler(log_file)
        handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(handler)
        
        # Add console handler for errors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message with structured data"""
        self.logger.info(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with structured data"""
        self.logger.error(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with structured data"""
        self.logger.warning(message, extra=kwargs)

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                          'pathname', 'filename', 'module', 'lineno', 
                          'funcName', 'created', 'msecs', 'relativeCreated', 
                          'thread', 'threadName', 'processName', 'process',
                          'getMessage', 'exc_info', 'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry)

# Create loggers for different components
orchestration_logger = StructuredLogger("orchestration")
cost_logger = StructuredLogger("cost_tracking")
performance_logger = StructuredLogger("performance")
error_logger = StructuredLogger("errors")
'''
        
        logging_file = self.base_dir / "logging_config.py"
        logging_file.write_text(logging_config)
        
        self.improvements_completed.append("logging_system")
        
        return {
            "status": "completed",
            "files_created": [str(logging_file)],
            "logs_directory": str(logs_dir),
            "next_steps": [
                "Test logging: python3 -c 'from logging_config import orchestration_logger; orchestration_logger.info(\"Test message\", component=\"test\")'",
                "Integrate structured logging into all modules"
            ]
        }
    
    def create_improvement_summary(self) -> Dict:
        """Generate summary of completed improvements"""
        return {
            "completed_improvements": self.improvements_completed,
            "completion_time": datetime.now().isoformat(),
            "next_phase_ready": len(self.improvements_completed) >= 3,
            "immediate_benefits": [
                "Secure API key management",
                "Intelligent response caching",
                "Structured logging and monitoring",
                "Foundation for real AI integration"
            ],
            "next_steps": [
                "Add actual API keys to .env file",
                "Integrate caching into AI response generation",
                "Add structured logging to all operations",
                "Begin Phase 1: Real AI Integration"
            ]
        }

def main():
    """Run immediate improvements setup"""
    print("🚀 AI Orchestration Platform - Quick Start Improvements")
    print("=" * 60)
    
    starter = ImprovementStarter()
    
    # Run immediate improvements
    results = []
    
    try:
        # Setup API key management
        api_result = starter.setup_api_key_management()
        results.append(("API Key Management", api_result))
        
        # Setup caching system
        cache_result = starter.setup_caching_system()
        results.append(("Caching System", cache_result))
        
        # Setup logging system
        logging_result = starter.setup_logging_system()
        results.append(("Logging System", logging_result))
        
        # Generate summary
        summary = starter.create_improvement_summary()
        
        print("\n✅ Improvements Completed:")
        for name, result in results:
            print(f"  • {name}: {result['status']}")
        
        print(f"\n📊 Summary:")
        print(f"  • Completed: {len(summary['completed_improvements'])}/3 improvements")
        print(f"  • Ready for Phase 1: {summary['next_phase_ready']}")
        
        print(f"\n🎯 Next Steps:")
        for step in summary['next_steps']:
            print(f"  1. {step}")
        
        print(f"\n🚀 Ready to proceed with Phase 1: Real AI Integration!")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
