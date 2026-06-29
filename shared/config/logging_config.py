#!/usr/bin/env python3
"""Logging Configuration - Structured logging for AI orchestration"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class StructuredLogger:
    """Structured logging with JSON format"""
    
    def __init__(self, name: str, log_dir: str = "/media/sunil-kr/workspace/user-projects/shared-tools/nested-shares/ai/orchestration/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
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
