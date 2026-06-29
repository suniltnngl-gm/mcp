"""
🗄️ Unified Data Persistence System - JSON Fallback & Comprehensive Storage
=======================================================================

Complete data persistence solution with:
- SQLite primary storage with JSON fallback
- Provider metrics and health data persistence
- Configuration backup and versioning
- Intelligent caching with TTL
- Comprehensive logging with rotation
- Automatic migration and recovery
"""

import gzip
import hashlib
import json
import logging
import os
import shutil
import sqlite3
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

# Rich for beautiful output
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


@dataclass
class ProviderMetrics:
    """Provider performance metrics."""

    provider_name: str
    success_rate: float
    avg_response_time: float
    total_requests: int
    failed_requests: int
    rate_limited_count: int
    last_success: datetime | None
    last_failure: datetime | None
    cost_per_request: float
    uptime_percentage: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "provider_name": self.provider_name,
            "success_rate": self.success_rate,
            "avg_response_time": self.avg_response_time,
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "rate_limited_count": self.rate_limited_count,
            "last_success": (
                self.last_success.isoformat() if self.last_success else None
            ),
            "last_failure": (
                self.last_failure.isoformat() if self.last_failure else None
            ),
            "cost_per_request": self.cost_per_request,
            "uptime_percentage": self.uptime_percentage,
        }


class UnifiedDataManager:
    """
    Unified data persistence manager with JSON fallback and comprehensive storage.

    Features:
    - SQLite primary storage with automatic JSON fallback
    - Provider metrics tracking and history
    - Configuration backup with versioning
    - Intelligent caching with TTL
    - Comprehensive logging
    - Automatic cleanup and maintenance
    """

    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir or os.path.expanduser("~/.ai_orchestra"))
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Storage paths
        self.db_path = self.base_dir / "orchestra.db"
        self.json_dir = self.base_dir / "json_backup"
        self.cache_dir = self.base_dir / "cache"
        self.logs_dir = self.base_dir / "logs"
        self.config_backup_dir = self.base_dir / "config_backups"

        # Create directories
        for directory in [
            self.json_dir,
            self.cache_dir,
            self.logs_dir,
            self.config_backup_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        # Thread lock for concurrent access
        self._lock = threading.Lock()

        # Setup logging
        self._setup_logging()

        # Initialize database
        self._init_database()

        # Load cached data
        self._metrics_cache = {}
        self._config_cache = {}
        self._load_cache()

        self.logger.info("UnifiedDataManager initialized")

    def _setup_logging(self):
        """Setup comprehensive logging system."""
        # Main logger
        self.logger = logging.getLogger("ai_orchestra")
        self.logger.setLevel(logging.INFO)

        # Console handler
        if not any(isinstance(h, logging.StreamHandler) for h in self.logger.handlers):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

        # File handler with rotation
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )
        if not any(
            isinstance(h, RotatingFileHandler)
            and getattr(h, "baseFilename", "").endswith("orchestra.log")
            for h in self.logger.handlers
        ):
            file_handler = RotatingFileHandler(
                self.logs_dir / "orchestra.log",
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
            )
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)

        # Provider-specific loggers
        self.provider_logger = logging.getLogger("ai_orchestra.providers")
        if not any(
            isinstance(h, RotatingFileHandler) for h in self.provider_logger.handlers
        ):
            provider_handler = RotatingFileHandler(
                self.logs_dir / "providers.log",
                maxBytes=5 * 1024 * 1024,  # 5MB
                backupCount=3,
            )
            provider_handler.setFormatter(file_formatter)
            self.provider_logger.addHandler(provider_handler)

        # Security/audit logger
        self.audit_logger = logging.getLogger("ai_orchestra.audit")
        if not any(
            isinstance(h, RotatingFileHandler) for h in self.audit_logger.handlers
        ):
            audit_handler = RotatingFileHandler(
                self.logs_dir / "audit.log",
                maxBytes=5 * 1024 * 1024,  # 5MB
                backupCount=10,  # Keep more audit logs
            )
            audit_handler.setFormatter(file_formatter)
            self.audit_logger.addHandler(audit_handler)

    def _init_database(self):
        """Initialize SQLite database with fallback to JSON."""
        try:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self._create_tables()
            self.use_database = True
            self.logger.info("SQLite database initialized successfully")
        except Exception as e:
            self.logger.warning(
                f"Failed to initialize SQLite database: {e}. Using JSON fallback."
            )
            self.use_database = False
            self.conn = None

    def _create_tables(self):
        """Create database tables."""
        if not self.conn:
            return

        cursor = self.conn.cursor()

        # Provider metrics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS provider_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_name TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                success_rate REAL,
                avg_response_time REAL,
                total_requests INTEGER,
                failed_requests INTEGER,
                rate_limited_count INTEGER,
                cost_per_request REAL,
                uptime_percentage REAL,
                metadata TEXT
            )
        """
        )

        # Provider health history
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS provider_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_name TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                response_time REAL,
                error_message TEXT,
                health_score REAL
            )
        """
        )

        # Configuration backups
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS config_backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                config_data TEXT NOT NULL,
                version INTEGER,
                checksum TEXT
            )
        """
        )

        # Cache entries
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cache_entries (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ttl INTEGER,
                access_count INTEGER DEFAULT 0
            )
        """
        )

        # Audit log
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                action TEXT NOT NULL,
                details TEXT,
                user_context TEXT,
                status TEXT
            )
        """
        )

        self.conn.commit()

    @contextmanager
    def _db_session(self):
        """Database session context manager with automatic rollback."""
        if not self.use_database or not self.conn:
            yield None
            return

        cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()

    def _get_json_path(self, data_type: str, provider_name: str = None) -> Path:
        """Get JSON file path for fallback storage."""
        if provider_name:
            return self.json_dir / f"{data_type}_{provider_name}.json"
        return self.json_dir / f"{data_type}.json"

    def _save_to_json(self, data_type: str, data: Any, provider_name: str = None):
        """Save data to JSON with atomic write."""
        json_path = self._get_json_path(data_type, provider_name)
        temp_path = json_path.with_suffix(".tmp")

        try:
            with open(temp_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

            # Atomic move
            temp_path.rename(json_path)

        except Exception as e:
            self.logger.error(f"Failed to save JSON {data_type}: {e}")
            if temp_path.exists():
                temp_path.unlink()

    def _load_from_json(self, data_type: str, provider_name: str = None, default=None):
        """Load data from JSON with error handling."""
        json_path = self._get_json_path(data_type, provider_name)

        if not json_path.exists():
            return default if default is not None else {}

        try:
            with open(json_path) as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load JSON {data_type}: {e}")
            return default if default is not None else {}

    # Provider Metrics Management
    def save_provider_metrics(self, metrics: ProviderMetrics):
        """Save provider metrics with dual storage."""
        with self._lock:
            timestamp = datetime.utcnow()

            # Try database first
            if self.use_database:
                try:
                    with self._db_session() as cursor:
                        cursor.execute(
                            """
                            INSERT INTO provider_metrics
                            (provider_name, success_rate, avg_response_time, total_requests,
                             failed_requests, rate_limited_count, cost_per_request,
                             uptime_percentage, metadata)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                            (
                                metrics.provider_name,
                                metrics.success_rate,
                                metrics.avg_response_time,
                                metrics.total_requests,
                                metrics.failed_requests,
                                metrics.rate_limited_count,
                                metrics.cost_per_request,
                                metrics.uptime_percentage,
                                json.dumps(metrics.to_dict()),
                            ),
                        )

                    self.provider_logger.info(
                        f"Saved metrics for {metrics.provider_name}"
                    )

                except Exception as e:
                    self.logger.warning(
                        f"Database save failed, using JSON fallback: {e}"
                    )
                    self.use_database = False

            # JSON fallback or primary storage
            if not self.use_database:
                history = self._load_from_json(
                    "metrics", metrics.provider_name, default=[]
                )
                history.append(
                    {"timestamp": timestamp.isoformat(), **metrics.to_dict()}
                )

                # Keep only last 1000 entries per provider
                if len(history) > 1000:
                    history = history[-1000:]

                self._save_to_json("metrics", history, metrics.provider_name)

            # Update cache
            self._metrics_cache[metrics.provider_name] = metrics

    def get_provider_metrics(
        self, provider_name: str, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get provider metrics history."""
        # Try database first
        if self.use_database:
            try:
                with self._db_session() as cursor:
                    cursor.execute(
                        """
                        SELECT * FROM provider_metrics
                        WHERE provider_name = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    """,
                        (provider_name, limit),
                    )

                    return [dict(row) for row in cursor.fetchall()]

            except Exception as e:
                self.logger.warning(f"Database read failed, using JSON fallback: {e}")

        # JSON fallback
        history = self._load_from_json("metrics", provider_name, [])
        return history[-limit:] if history else []

    def get_all_provider_metrics(self) -> dict[str, ProviderMetrics]:
        """Get latest metrics for all providers."""
        return self._metrics_cache.copy()

    # Provider Health Management
    def save_provider_health(
        self,
        provider_name: str,
        status: str,
        response_time: float = None,
        error_message: str = None,
        health_score: float = None,
    ):
        """Save provider health check result."""
        with self._lock:
            timestamp = datetime.utcnow()

            health_data = {
                "provider_name": provider_name,
                "timestamp": timestamp.isoformat(),
                "status": status,
                "response_time": response_time,
                "error_message": error_message,
                "health_score": health_score or (1.0 if status == "healthy" else 0.0),
            }

            # Try database first
            if self.use_database:
                try:
                    with self._db_session() as cursor:
                        cursor.execute(
                            """
                            INSERT INTO provider_health
                            (provider_name, status, response_time, error_message, health_score)
                            VALUES (?, ?, ?, ?, ?)
                        """,
                            (
                                provider_name,
                                status,
                                response_time,
                                error_message,
                                health_score,
                            ),
                        )

                except Exception as e:
                    self.logger.warning(f"Health save to database failed: {e}")
                    self.use_database = False

            # JSON fallback
            if not self.use_database:
                health_history = self._load_from_json(
                    "health", provider_name, default=[]
                )
                health_history.append(health_data)

                # Keep only last 24 hours of health data
                cutoff = timestamp - timedelta(hours=24)
                health_history = [
                    h
                    for h in health_history
                    if datetime.fromisoformat(h["timestamp"]) > cutoff
                ]

                self._save_to_json("health", health_history, provider_name)

            self.provider_logger.info(f"Health check: {provider_name} - {status}")

    def get_provider_health_history(
        self, provider_name: str, hours: int = 24
    ) -> list[dict[str, Any]]:
        """Get provider health history."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        # Try database first
        if self.use_database:
            try:
                with self._db_session() as cursor:
                    cursor.execute(
                        """
                        SELECT * FROM provider_health
                        WHERE provider_name = ? AND timestamp > ?
                        ORDER BY timestamp DESC
                    """,
                        (provider_name, cutoff.isoformat()),
                    )

                    return [dict(row) for row in cursor.fetchall()]

            except Exception as e:
                self.logger.warning(f"Health read from database failed: {e}")

        # JSON fallback
        health_history = self._load_from_json("health", provider_name, [])
        return [
            h for h in health_history if datetime.fromisoformat(h["timestamp"]) > cutoff
        ]

    # Configuration Management
    def backup_configuration(
        self, config_type: str, config_data: dict[str, Any], version: int = None
    ) -> str:
        """Backup configuration with versioning."""
        with self._lock:
            timestamp = datetime.utcnow()
            config_json = json.dumps(config_data, indent=2, sort_keys=True)
            checksum = hashlib.md5(config_json.encode()).hexdigest()

            # Auto-increment version if not provided
            if version is None:
                version = self._get_next_config_version(config_type)

            backup_data = {
                "config_type": config_type,
                "timestamp": timestamp.isoformat(),
                "config_data": config_data,
                "version": version,
                "checksum": checksum,
            }

            # Try database first
            if self.use_database:
                try:
                    with self._db_session() as cursor:
                        cursor.execute(
                            """
                            INSERT INTO config_backups
                            (config_type, config_data, version, checksum)
                            VALUES (?, ?, ?, ?)
                        """,
                            (config_type, config_json, version, checksum),
                        )

                except Exception as e:
                    self.logger.warning(f"Config backup to database failed: {e}")
                    self.use_database = False

            # JSON fallback
            if not self.use_database:
                backup_file = (
                    self.config_backup_dir
                    / f"{config_type}_v{version}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
                )
                with open(backup_file, "w") as f:
                    json.dump(backup_data, f, indent=2)

                # Also maintain latest backup
                latest_file = self.config_backup_dir / f"{config_type}_latest.json"
                with open(latest_file, "w") as f:
                    json.dump(backup_data, f, indent=2)

            self.audit_logger.info(f"Configuration backed up: {config_type} v{version}")
            return f"{config_type}_v{version}"

    def restore_configuration(
        self, config_type: str, version: int = None
    ) -> dict[str, Any] | None:
        """Restore configuration from backup."""
        # Try database first
        if self.use_database:
            try:
                with self._db_session() as cursor:
                    if version:
                        cursor.execute(
                            """
                            SELECT config_data FROM config_backups
                            WHERE config_type = ? AND version = ?
                        """,
                            (config_type, version),
                        )
                    else:
                        cursor.execute(
                            """
                            SELECT config_data FROM config_backups
                            WHERE config_type = ?
                            ORDER BY timestamp DESC LIMIT 1
                        """,
                            (config_type,),
                        )

                    row = cursor.fetchone()
                    if row:
                        return json.loads(row["config_data"])

            except Exception as e:
                self.logger.warning(f"Config restore from database failed: {e}")

        # JSON fallback
        if version:
            # Find specific version
            pattern = f"{config_type}_v{version}_*.json"
            backup_files = list(self.config_backup_dir.glob(pattern))
            if backup_files:
                with open(backup_files[0]) as f:
                    backup_data = json.load(f)
                return backup_data.get("config_data")
        else:
            # Get latest
            latest_file = self.config_backup_dir / f"{config_type}_latest.json"
            if latest_file.exists():
                with open(latest_file) as f:
                    backup_data = json.load(f)
                return backup_data.get("config_data")

        return None

    def _get_next_config_version(self, config_type: str) -> int:
        """Get next version number for configuration type."""
        if self.use_database:
            try:
                with self._db_session() as cursor:
                    cursor.execute(
                        """
                        SELECT MAX(version) FROM config_backups
                        WHERE config_type = ?
                    """,
                        (config_type,),
                    )

                    result = cursor.fetchone()
                    return (result[0] or 0) + 1

            except Exception as e:
                self.logger.warning(f"Version query failed: {e}")

        # JSON fallback - scan files
        pattern = f"{config_type}_v*.json"
        backup_files = list(self.config_backup_dir.glob(pattern))

        max_version = 0
        for file in backup_files:
            try:
                # Extract version from filename
                version_part = file.stem.split("_v")[1].split("_")[0]
                version = int(version_part)
                max_version = max(max_version, version)
            except (IndexError, ValueError):
                continue

        return max_version + 1

    # Cache Management
    def cache_set(self, key: str, value: Any, ttl: int = 3600):
        """Set cache entry with TTL."""
        with self._lock:
            timestamp = datetime.utcnow()

            # Serialize value
            if isinstance(value, dict | list):
                serialized_value = json.dumps(value, default=str)
            else:
                serialized_value = str(value)

            cache_data = {
                "key": key,
                "value": serialized_value,
                "timestamp": timestamp.isoformat(),
                "ttl": ttl,
                "access_count": 0,
            }

            # Try database first
            if self.use_database:
                try:
                    with self._db_session() as cursor:
                        cursor.execute(
                            """
                            INSERT OR REPLACE INTO cache_entries
                            (key, value, timestamp, ttl, access_count)
                            VALUES (?, ?, ?, ?, ?)
                        """,
                            (key, serialized_value, timestamp.isoformat(), ttl, 0),
                        )

                except Exception as e:
                    self.logger.warning(f"Cache save to database failed: {e}")
                    self.use_database = False

            # JSON fallback
            if not self.use_database:
                cache_file = self.cache_dir / "cache_data.json"
                if cache_file.exists():
                    try:
                        with open(cache_file) as f:
                            cache_dict = json.load(f)
                    except Exception:
                        cache_dict = {}
                else:
                    cache_dict = {}
                cache_dict[key] = cache_data

                # Clean expired entries
                self._cleanup_json_cache(cache_dict)

                with open(cache_file, "w") as f:
                    json.dump(cache_dict, f, indent=2)

    def cache_get(self, key: str) -> Any | None:
        """Get cache entry if not expired."""
        # Try database first
        if self.use_database:
            try:
                with self._db_session() as cursor:
                    cursor.execute(
                        """
                        SELECT value, timestamp, ttl, access_count FROM cache_entries
                        WHERE key = ?
                    """,
                        (key,),
                    )

                    row = cursor.fetchone()
                    if row:
                        stored_time = datetime.fromisoformat(row["timestamp"])
                        if datetime.utcnow() - stored_time < timedelta(
                            seconds=row["ttl"]
                        ):
                            # Update access count
                            cursor.execute(
                                """
                                UPDATE cache_entries SET access_count = access_count + 1
                                WHERE key = ?
                            """,
                                (key,),
                            )

                            # Try to deserialize JSON
                            try:
                                return json.loads(row["value"])
                            except json.JSONDecodeError:
                                return row["value"]

            except Exception as e:
                self.logger.warning(f"Cache read from database failed: {e}")

        # JSON fallback
        cache_file = self.cache_dir / "cache_data.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    cache_dict = json.load(f)
            except Exception:
                cache_dict = {}
        else:
            cache_dict = {}

        if key in cache_dict:
            entry = cache_dict[key]
            stored_time = datetime.fromisoformat(entry["timestamp"])

            if datetime.utcnow() - stored_time < timedelta(seconds=entry["ttl"]):
                # Update access count
                entry["access_count"] += 1
                with open(cache_file, "w") as f:
                    json.dump(cache_dict, f, indent=2)

                # Try to deserialize JSON
                try:
                    return json.loads(entry["value"])
                except json.JSONDecodeError:
                    return entry["value"]

        return None

    def _cleanup_json_cache(self, cache_dict: dict[str, Any]):
        """Clean expired entries from JSON cache."""
        current_time = datetime.utcnow()
        expired_keys = []

        for key, entry in cache_dict.items():
            try:
                stored_time = datetime.fromisoformat(entry["timestamp"])
                if current_time - stored_time >= timedelta(seconds=entry["ttl"]):
                    expired_keys.append(key)
            except (KeyError, ValueError):
                expired_keys.append(key)  # Malformed entry

        for key in expired_keys:
            del cache_dict[key]

    # Audit Logging
    def log_action(
        self,
        action: str,
        details: str = None,
        user_context: str = None,
        status: str = "success",
    ):
        """Log action for audit trail."""
        timestamp = datetime.utcnow()

        audit_data = {
            "timestamp": timestamp.isoformat(),
            "action": action,
            "details": details,
            "user_context": user_context,
            "status": status,
        }

        # Try database first
        if self.use_database:
            try:
                with self._db_session() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO audit_log (action, details, user_context, status)
                        VALUES (?, ?, ?, ?)
                    """,
                        (action, details, user_context, status),
                    )

            except Exception as e:
                self.logger.warning(f"Audit log to database failed: {e}")
                self.use_database = False

        # JSON fallback
        if not self.use_database:
            audit_history = self._load_from_json("audit", default=[])
            audit_history.append(audit_data)

            # Keep only last 10000 audit entries
            if len(audit_history) > 10000:
                audit_history = audit_history[-10000:]

            self._save_to_json("audit", audit_history)

        self.audit_logger.info(f"{action}: {details}")

    # Data Export and Import
    def export_all_data(self, export_path: str = None) -> str:
        """Export all data to compressed JSON archive."""
        export_path = (
            export_path
            or self.base_dir
            / f"export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json.gz"
        )

        export_data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "export_version": "1.0",
            "data": {},
        }

        # Export provider metrics
        all_metrics = {}
        for provider_name in self._metrics_cache:
            all_metrics[provider_name] = self.get_provider_metrics(
                provider_name, limit=1000
            )
        export_data["data"]["provider_metrics"] = all_metrics

        # Export health data
        health_data = {}
        for provider_name in self._metrics_cache:
            health_data[provider_name] = self.get_provider_health_history(
                provider_name, hours=168
            )  # 1 week
        export_data["data"]["health_history"] = health_data

        # Export configuration backups
        if self.use_database:
            try:
                with self._db_session() as cursor:
                    cursor.execute(
                        "SELECT * FROM config_backups ORDER BY timestamp DESC"
                    )
                    export_data["data"]["config_backups"] = [
                        dict(row) for row in cursor.fetchall()
                    ]
            except Exception:
                pass

        # Compress and save
        with gzip.open(export_path, "wt", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)

        self.logger.info(f"Data exported to {export_path}")
        return str(export_path)

    def import_data(self, import_path: str):
        """Import data from compressed JSON archive."""
        try:
            with gzip.open(import_path, "rt", encoding="utf-8") as f:
                import_data = json.load(f)

            # Import provider metrics
            if "provider_metrics" in import_data.get("data", {}):
                for _provider_name, metrics_list in import_data["data"][
                    "provider_metrics"
                ].items():
                    for metrics_data in metrics_list:
                        # Convert back to ProviderMetrics object
                        if (
                            "last_success" in metrics_data
                            and metrics_data["last_success"]
                        ):
                            metrics_data["last_success"] = datetime.fromisoformat(
                                metrics_data["last_success"]
                            )
                        if (
                            "last_failure" in metrics_data
                            and metrics_data["last_failure"]
                        ):
                            metrics_data["last_failure"] = datetime.fromisoformat(
                                metrics_data["last_failure"]
                            )

                        metrics = ProviderMetrics(**metrics_data)
                        self.save_provider_metrics(metrics)

            # Import health data
            if "health_history" in import_data.get("data", {}):
                for _provider_name, health_list in import_data["data"][
                    "health_history"
                ].items():
                    for health_data in health_list:
                        self.save_provider_health(
                            provider_name=health_data["provider_name"],
                            status=health_data["status"],
                            response_time=health_data.get("response_time"),
                            error_message=health_data.get("error_message"),
                            health_score=health_data.get("health_score"),
                        )

            self.logger.info(f"Data imported from {import_path}")

        except Exception as e:
            self.logger.error(f"Failed to import data: {e}")
            raise

    # System Maintenance
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data beyond retention period."""
        cutoff = datetime.utcnow() - timedelta(days=days_to_keep)

        if self.use_database:
            try:
                with self._db_session() as cursor:
                    # Clean old metrics
                    cursor.execute(
                        """
                        DELETE FROM provider_metrics
                        WHERE timestamp < ?
                    """,
                        (cutoff.isoformat(),),
                    )

                    # Clean old health data
                    cursor.execute(
                        """
                        DELETE FROM provider_health
                        WHERE timestamp < ?
                    """,
                        (cutoff.isoformat(),),
                    )

                    # Clean expired cache entries
                    cursor.execute(
                        """
                        DELETE FROM cache_entries
                        WHERE datetime(timestamp, '+' || ttl || ' seconds') < ?
                    """,
                        (datetime.utcnow().isoformat(),),
                    )

                    self.logger.info(
                        f"Cleaned database records older than {days_to_keep} days"
                    )

            except Exception as e:
                self.logger.warning(f"Database cleanup failed: {e}")

        # JSON cleanup
        cutoff_str = cutoff.isoformat()

        # Clean metrics files
        for metrics_file in self.json_dir.glob("metrics_*.json"):
            try:
                history = self._load_from_json(
                    "metrics", metrics_file.stem.replace("metrics_", "")
                )
                cleaned_history = [
                    h for h in history if h.get("timestamp", "") > cutoff_str
                ]

                if len(cleaned_history) != len(history):
                    self._save_to_json(
                        "metrics",
                        cleaned_history,
                        metrics_file.stem.replace("metrics_", ""),
                    )

            except Exception as e:
                self.logger.warning(f"Failed to clean {metrics_file}: {e}")

        # Clean old config backups (keep more for safety)
        config_cutoff = datetime.utcnow() - timedelta(days=days_to_keep * 3)
        for backup_file in self.config_backup_dir.glob("*.json"):
            if "latest" in backup_file.name:
                continue  # Keep latest files

            try:
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_time < config_cutoff:
                    backup_file.unlink()

            except Exception as e:
                self.logger.warning(f"Failed to clean {backup_file}: {e}")

    def _load_cache(self):
        """Load cached data on startup."""
        # Load latest metrics into cache
        try:
            if self.use_database:
                with self._db_session() as cursor:
                    cursor.execute(
                        """
                    SELECT DISTINCT provider_name FROM provider_metrics
                """
                    )
                providers = [row[0] for row in cursor.fetchall()]

                for provider in providers:
                    latest_rows = self.get_provider_metrics(provider, limit=1)
                    if latest_rows:
                        row = latest_rows[0]
                        # Prefer metadata field if present
                        if "metadata" in row and row["metadata"]:
                            try:
                                metrics_data = json.loads(row["metadata"])
                            except Exception:
                                metrics_data = {}
                        else:
                            # Fallback: map known fields
                            metrics_data = {
                                "provider_name": row.get("provider_name", provider),
                                "success_rate": row.get("success_rate", 0.0),
                                "avg_response_time": row.get("avg_response_time", 0.0),
                                "total_requests": row.get("total_requests", 0),
                                "failed_requests": row.get("failed_requests", 0),
                                "rate_limited_count": row.get("rate_limited_count", 0),
                                "last_success": None,
                                "last_failure": None,
                                "cost_per_request": row.get("cost_per_request", 0.0),
                                "uptime_percentage": row.get("uptime_percentage", 0.0),
                            }
                        # Convert timestamps
                        if (
                            "last_success" in metrics_data
                            and metrics_data["last_success"]
                        ):
                            try:
                                metrics_data["last_success"] = datetime.fromisoformat(
                                    metrics_data["last_success"]
                                )
                            except Exception:
                                metrics_data["last_success"] = None
                        if (
                            "last_failure" in metrics_data
                            and metrics_data["last_failure"]
                        ):
                            try:
                                metrics_data["last_failure"] = datetime.fromisoformat(
                                    metrics_data["last_failure"]
                                )
                            except Exception:
                                metrics_data["last_failure"] = None

                        # Filter to dataclass fields
                        allowed = set(ProviderMetrics.__annotations__.keys())
                        filtered = {
                            k: v for k, v in metrics_data.items() if k in allowed
                        }

                        # Create ProviderMetrics object
                        self._metrics_cache[provider] = ProviderMetrics(**filtered)

        except Exception as e:
            self.logger.warning(f"Failed to load cache: {e}")

    # Status and Statistics
    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status."""
        status = {
            "database": {
                "type": "SQLite" if self.use_database else "JSON",
                "path": str(self.db_path) if self.use_database else str(self.json_dir),
                "status": "connected" if self.use_database else "fallback",
            },
            "storage": {
                "base_dir": str(self.base_dir),
                "total_size": self._get_directory_size(self.base_dir),
                "cache_entries": len(self._get_cache_stats()),
                "log_files": len(list(self.logs_dir.glob("*.log*"))),
            },
            "providers": {
                "tracked_providers": len(self._metrics_cache),
                "total_requests": sum(
                    m.total_requests for m in self._metrics_cache.values()
                ),
                "avg_success_rate": (
                    sum(m.success_rate for m in self._metrics_cache.values())
                    / len(self._metrics_cache)
                    if self._metrics_cache
                    else 0
                ),
            },
        }

        return status

    def _get_directory_size(self, directory: Path) -> str:
        """Get directory size in human readable format."""
        total_size = sum(f.stat().st_size for f in directory.rglob("*") if f.is_file())

        for unit in ["B", "KB", "MB", "GB"]:
            if total_size < 1024:
                return f"{total_size:.1f} {unit}"
            total_size /= 1024
        return f"{total_size:.1f} TB"

    def _get_cache_stats(self) -> dict[str, int]:
        """Get cache statistics."""
        if self.use_database:
            try:
                with self._db_session() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM cache_entries")
                    total = cursor.fetchone()[0]

                    cursor.execute(
                        """
                        SELECT COUNT(*) FROM cache_entries
                        WHERE datetime(timestamp, '+' || ttl || ' seconds') > datetime('now')
                    """
                    )
                    valid = cursor.fetchone()[0]

                    return {"total": total, "valid": valid, "expired": total - valid}

            except Exception:
                pass

        # JSON fallback
        cache_dict = self._load_from_json("cache", default={})
        current_time = datetime.utcnow()

        total = len(cache_dict)
        valid = 0

        for entry in cache_dict.values():
            try:
                stored_time = datetime.fromisoformat(entry["timestamp"])
                if current_time - stored_time < timedelta(seconds=entry["ttl"]):
                    valid += 1
            except (KeyError, ValueError):
                continue

        return {"total": total, "valid": valid, "expired": total - valid}

    def show_status_dashboard(self):
        """Display comprehensive status dashboard."""
        status = self.get_system_status()

        # Main status panel
        status_table = Table(title="📊 AI Orchestra Data System Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="green")
        status_table.add_column("Details", style="yellow")

        # Database status
        db_status = status["database"]
        status_table.add_row(
            "Database",
            (
                f"✅ {db_status['type']}"
                if db_status["status"] == "connected"
                else f"⚠️ {db_status['type']} (Fallback)"
            ),
            f"Path: {db_status['path']}",
        )

        # Storage status
        storage = status["storage"]
        status_table.add_row(
            "Storage",
            f"📁 {storage['total_size']}",
            f"Cache: {storage['cache_entries']} entries, Logs: {storage['log_files']} files",
        )

        # Provider metrics
        providers = status["providers"]
        status_table.add_row(
            "Providers",
            f"🤖 {providers['tracked_providers']} tracked",
            f"Requests: {providers['total_requests']}, Success: {providers['avg_success_rate']:.1%}",
        )

        console.print(status_table)

        # Cache statistics
        cache_stats = self._get_cache_stats()
        cache_panel = Panel(
            f"Total: {cache_stats['total']} | Valid: {cache_stats['valid']} | Expired: {cache_stats['expired']}",
            title="💾 Cache Statistics",
            border_style="blue",
        )
        console.print(cache_panel)

    # Backup and Recovery
    def create_full_backup(self) -> str:
        """Create full system backup."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.base_dir / f"backup_{timestamp}"
        backup_dir.mkdir(exist_ok=True)

        try:
            # Copy database
            if self.use_database and self.db_path.exists():
                shutil.copy2(self.db_path, backup_dir / "orchestra.db")

            # Copy JSON files
            if self.json_dir.exists():
                shutil.copytree(self.json_dir, backup_dir / "json_backup")

            # Copy cache
            if self.cache_dir.exists():
                shutil.copytree(self.cache_dir, backup_dir / "cache")

            # Copy config backups
            if self.config_backup_dir.exists():
                shutil.copytree(self.config_backup_dir, backup_dir / "config_backups")

            # Copy logs (latest only)
            logs_backup = backup_dir / "logs"
            logs_backup.mkdir(exist_ok=True)
            for log_file in self.logs_dir.glob("*.log"):
                shutil.copy2(log_file, logs_backup)

            # Create manifest
            manifest = {
                "backup_timestamp": timestamp,
                "backup_type": "full",
                "included_components": [
                    "database",
                    "json_files",
                    "cache",
                    "config_backups",
                    "logs",
                ],
                "system_status": self.get_system_status(),
            }

            with open(backup_dir / "manifest.json", "w") as f:
                json.dump(manifest, f, indent=2)

            # Compress backup
            backup_archive = f"{backup_dir}.tar.gz"
            shutil.make_archive(str(backup_dir), "gztar", str(backup_dir))

            # Remove uncompressed directory
            shutil.rmtree(backup_dir)

            self.log_action("full_backup_created", f"Backup saved to {backup_archive}")
            return backup_archive

        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            raise

    def restore_from_backup(self, backup_path: str):
        """Restore system from backup."""
        backup_path = Path(backup_path)

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        # Extract backup
        restore_dir = self.base_dir / "restore_temp"
        shutil.unpack_archive(str(backup_path), str(restore_dir))

        try:
            # Read manifest
            manifest_path = restore_dir / "manifest.json"
            if manifest_path.exists():
                with open(manifest_path) as f:
                    manifest = json.load(f)
                    self.logger.info(
                        f"Restoring backup from {manifest['backup_timestamp']}"
                    )

            # Restore database
            db_backup = restore_dir / "orchestra.db"
            if db_backup.exists():
                if self.conn:
                    self.conn.close()
                shutil.copy2(db_backup, self.db_path)
                self._init_database()

            # Restore JSON files
            json_backup = restore_dir / "json_backup"
            if json_backup.exists():
                if self.json_dir.exists():
                    shutil.rmtree(self.json_dir)
                shutil.copytree(json_backup, self.json_dir)

            # Restore cache
            cache_backup = restore_dir / "cache"
            if cache_backup.exists():
                if self.cache_dir.exists():
                    shutil.rmtree(self.cache_dir)
                shutil.copytree(cache_backup, self.cache_dir)

            # Restore config backups
            config_backup = restore_dir / "config_backups"
            if config_backup.exists():
                if self.config_backup_dir.exists():
                    shutil.rmtree(self.config_backup_dir)
                shutil.copytree(config_backup, self.config_backup_dir)

            # Reload cache
            self._load_cache()

            self.log_action("system_restored", f"Restored from {backup_path}")

        except Exception as e:
            self.logger.error(f"Restore failed: {e}")
            raise
        finally:
            # Cleanup temp directory
            if restore_dir.exists():
                shutil.rmtree(restore_dir)

    # Migration utilities
    def migrate_to_database(self):
        """Migrate JSON data to SQLite database."""
        if self.use_database:
            self.logger.info("Already using database")
            return

        try:
            # Reinitialize database
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self._create_tables()

            # Migrate metrics
            for metrics_file in self.json_dir.glob("metrics_*.json"):
                provider_name = metrics_file.stem.replace("metrics_", "")
                history = self._load_from_json("metrics", provider_name, [])

                for entry in history:
                    if "provider_name" in entry:
                        # Convert to ProviderMetrics and save
                        if "last_success" in entry and entry["last_success"]:
                            entry["last_success"] = datetime.fromisoformat(
                                entry["last_success"]
                            )
                        if "last_failure" in entry and entry["last_failure"]:
                            entry["last_failure"] = datetime.fromisoformat(
                                entry["last_failure"]
                            )

                        metrics = ProviderMetrics(**entry)
                        self.save_provider_metrics(metrics)

            # Migrate health data
            for health_file in self.json_dir.glob("health_*.json"):
                provider_name = health_file.stem.replace("health_", "")
                history = self._load_from_json("health", provider_name, [])

                for entry in history:
                    self.save_provider_health(
                        provider_name=entry["provider_name"],
                        status=entry["status"],
                        response_time=entry.get("response_time"),
                        error_message=entry.get("error_message"),
                        health_score=entry.get("health_score"),
                    )

            self.use_database = True
            self.logger.info("Successfully migrated JSON data to SQLite database")

        except Exception as e:
            self.logger.error(f"Migration failed: {e}")
            self.use_database = False
            raise

    def __del__(self):
        """Cleanup on destruction."""
        if hasattr(self, "conn") and self.conn:
            self.conn.close()


class DataPersistenceHelper:
    """Helper class for easy data persistence operations."""

    def __init__(self, data_manager: UnifiedDataManager = None):
        self.dm = data_manager or UnifiedDataManager()

    def log_provider_request(
        self, provider_name: str, success: bool, response_time: float, cost: float = 0.0
    ):
        """Log a single provider request."""
        # Get current metrics or create new
        current_metrics = self.dm._metrics_cache.get(provider_name)

        if current_metrics:
            # Update existing metrics
            total = current_metrics.total_requests + 1
            failed = current_metrics.failed_requests + (0 if success else 1)
            success_rate = (total - failed) / total

            # Update average response time
            old_avg = current_metrics.avg_response_time
            new_avg = (
                (old_avg * current_metrics.total_requests) + response_time
            ) / total

            updated_metrics = ProviderMetrics(
                provider_name=provider_name,
                success_rate=success_rate,
                avg_response_time=new_avg,
                total_requests=total,
                failed_requests=failed,
                rate_limited_count=current_metrics.rate_limited_count,
                last_success=(
                    datetime.utcnow() if success else current_metrics.last_success
                ),
                last_failure=(
                    datetime.utcnow() if not success else current_metrics.last_failure
                ),
                cost_per_request=cost,
                uptime_percentage=current_metrics.uptime_percentage,
            )
        else:
            # Create new metrics
            updated_metrics = ProviderMetrics(
                provider_name=provider_name,
                success_rate=1.0 if success else 0.0,
                avg_response_time=response_time,
                total_requests=1,
                failed_requests=0 if success else 1,
                rate_limited_count=0,
                last_success=datetime.utcnow() if success else None,
                last_failure=datetime.utcnow() if not success else None,
                cost_per_request=cost,
                uptime_percentage=100.0 if success else 0.0,
            )

        self.dm.save_provider_metrics(updated_metrics)

    def log_rate_limit(self, provider_name: str):
        """Log rate limit event."""
        current_metrics = self.dm._metrics_cache.get(provider_name)
        if current_metrics:
            updated_metrics = ProviderMetrics(
                provider_name=provider_name,
                success_rate=current_metrics.success_rate,
                avg_response_time=current_metrics.avg_response_time,
                total_requests=current_metrics.total_requests,
                failed_requests=current_metrics.failed_requests,
                rate_limited_count=current_metrics.rate_limited_count + 1,
                last_success=current_metrics.last_success,
                last_failure=current_metrics.last_failure,
                cost_per_request=current_metrics.cost_per_request,
                uptime_percentage=current_metrics.uptime_percentage,
            )
            self.dm.save_provider_metrics(updated_metrics)

        self.dm.save_provider_health(
            provider_name, "rate_limited", error_message="Rate limit exceeded"
        )

    def get_provider_summary(self, provider_name: str) -> dict[str, Any]:
        """Get comprehensive provider summary."""
        metrics = self.dm._metrics_cache.get(provider_name)
        health_history = self.dm.get_provider_health_history(provider_name, hours=24)

        if not metrics:
            return {"provider_name": provider_name, "status": "no_data"}

        # Calculate recent health
        recent_health = [h for h in health_history if h["status"] == "healthy"]
        health_percentage = (
            (len(recent_health) / len(health_history)) * 100 if health_history else 0
        )

        return {
            "provider_name": provider_name,
            "success_rate": metrics.success_rate,
            "avg_response_time": metrics.avg_response_time,
            "total_requests": metrics.total_requests,
            "rate_limited_count": metrics.rate_limited_count,
            "recent_health_percentage": health_percentage,
            "cost_per_request": metrics.cost_per_request,
            "last_success": (
                metrics.last_success.isoformat() if metrics.last_success else None
            ),
            "uptime_percentage": metrics.uptime_percentage,
        }


# Global instance
data_manager = UnifiedDataManager()
persistence_helper = DataPersistenceHelper(data_manager)


if __name__ == "__main__":
    """Demo and testing of data persistence system."""

    console.print(
        Panel("🗄️ AI Orchestra Data Persistence System Demo", style="bold blue")
    )

    # Test metrics saving
    console.print("\n📊 Testing Provider Metrics...")
    test_metrics = ProviderMetrics(
        provider_name="test_provider",
        success_rate=0.95,
        avg_response_time=1.2,
        total_requests=100,
        failed_requests=5,
        rate_limited_count=2,
        last_success=datetime.utcnow(),
        last_failure=datetime.utcnow() - timedelta(hours=1),
        cost_per_request=0.001,
        uptime_percentage=98.5,
    )

    data_manager.save_provider_metrics(test_metrics)
    retrieved_metrics = data_manager.get_provider_metrics("test_provider", limit=5)
    console.print(f"✅ Saved and retrieved {len(retrieved_metrics)} metric entries")

    # Test health logging
    console.print("\n🏥 Testing Health Monitoring...")
    data_manager.save_provider_health(
        "test_provider", "healthy", response_time=0.8, health_score=1.0
    )
    data_manager.save_provider_health(
        "test_provider",
        "unhealthy",
        error_message="Connection timeout",
        health_score=0.0,
    )

    health_history = data_manager.get_provider_health_history("test_provider", hours=1)
    console.print(f"✅ Saved and retrieved {len(health_history)} health entries")

    # Test configuration backup
    console.print("\n⚙️ Testing Configuration Backup...")
    test_config = {
        "providers": ["groq", "together"],
        "load_balancing": "round_robin",
        "retry_attempts": 3,
    }

    backup_id = data_manager.backup_configuration("test_config", test_config)
    restored_config = data_manager.restore_configuration("test_config")
    console.print(f"✅ Config backed up as {backup_id} and restored successfully")

    # Test caching
    console.print("\n💾 Testing Cache System...")
    data_manager.cache_set("test_key", {"expensive": "operation_result"}, ttl=60)
    cached_value = data_manager.cache_get("test_key")
    console.print(f"✅ Cached and retrieved: {cached_value}")

    # Test audit logging
    console.print("\n📝 Testing Audit Logging...")
    data_manager.log_action(
        "test_action", "Demo action performed", "demo_user", "success"
    )
    console.print("✅ Audit log entry created")

    # Show status dashboard
    console.print("\n📈 System Status Dashboard:")
    data_manager.show_status_dashboard()

    # Test helper functions
    console.print("\n🔧 Testing Helper Functions...")
    persistence_helper.log_provider_request("test_provider", True, 1.5, 0.002)
    persistence_helper.log_rate_limit("test_provider")

    summary = persistence_helper.get_provider_summary("test_provider")
    console.print(f"✅ Provider summary: Success rate {summary['success_rate']:.1%}")

    # Test backup and cleanup
    console.print("\n💾 Testing Backup System...")
    backup_file = data_manager.create_full_backup()
    console.print(f"✅ Full backup created: {backup_file}")

    console.print("\n🧹 Testing Cleanup...")
    data_manager.cleanup_old_data(days_to_keep=1)
    console.print("✅ Old data cleanup completed")

    console.print(Panel("Demo completed successfully! 🎉", style="bold green"))
