#!/usr/bin/env python3
"""Version registry - manages versions without polluting file names."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class VersionRegistry:
    def __init__(self, workspace_root: str = "."):
        self.root = Path(workspace_root).resolve()
        self.registry_file = self.root / "data" / "version_registry.json"
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """Load version registry."""
        if self.registry_file.exists():
            with open(self.registry_file) as f:
                return json.load(f)
        return {
            "files": {},
            "schedules": {},
            "metadata": {"created": datetime.now().isoformat()}
        }
    
    def _save_registry(self):
        """Save version registry."""
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register_file(self, strict_path: str, purpose: str = "active") -> str:
        """Register file with strict naming only."""
        # Validate strict naming: filename_channel.ext
        path = Path(strict_path)
        name = path.name
        
        if not self._is_strict_naming(name):
            raise ValueError(f"File must follow strict naming: filename_channel.ext, got: {name}")
        
        file_id = str(path)
        
        if file_id not in self.registry["files"]:
            self.registry["files"][file_id] = {
                "created": datetime.now().isoformat(),
                "versions": [],
                "current_purpose": purpose,
                "history": []
            }
        
        # Add version entry
        version_entry = {
            "timestamp": datetime.now().isoformat(),
            "purpose": purpose,
            "size": path.stat().st_size if path.exists() else 0,
            "checksum": self._calculate_checksum(path) if path.exists() else None
        }
        
        self.registry["files"][file_id]["versions"].append(version_entry)
        self.registry["files"][file_id]["current_purpose"] = purpose
        
        self._save_registry()
        return file_id
    
    def _is_strict_naming(self, filename: str) -> bool:
        """Check if filename follows strict naming convention."""
        import re
        pattern = r'^[a-zA-Z0-9_-]+_(nightly|preview|latest)\.[a-zA-Z0-9]+$'
        return bool(re.match(pattern, filename))
    
    def _calculate_checksum(self, path: Path) -> str:
        """Calculate file checksum."""
        import hashlib
        if not path.exists():
            return None
        
        hash_md5 = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def set_purpose(self, file_path: str, purpose: str, schedule_days: int = None):
        """Set file purpose (active, backup, deprecated, cleanup)."""
        file_id = str(Path(file_path))
        
        if file_id not in self.registry["files"]:
            self.register_file(file_path, purpose)
            return
        
        # Update purpose
        self.registry["files"][file_id]["current_purpose"] = purpose
        
        # Add to history
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": f"set_purpose_{purpose}",
            "previous_purpose": self.registry["files"][file_id].get("current_purpose", "unknown")
        }
        self.registry["files"][file_id]["history"].append(history_entry)
        
        # Schedule if needed
        if schedule_days and purpose in ["backup", "deprecated", "cleanup"]:
            self._schedule_action(file_id, purpose, schedule_days)
        
        self._save_registry()
    
    def _schedule_action(self, file_id: str, action: str, days: int):
        """Schedule action for file."""
        from datetime import timedelta
        
        schedule_date = datetime.now() + timedelta(days=days)
        schedule_id = f"{action}_{file_id}_{int(schedule_date.timestamp())}"
        
        self.registry["schedules"][schedule_id] = {
            "file_id": file_id,
            "action": action,
            "scheduled_date": schedule_date.isoformat(),
            "status": "scheduled"
        }
    
    def transform_existing_naming(self, source_path: str) -> Dict:
        """Transform existing naming patterns to strict naming."""
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        # Analyze existing naming patterns
        analysis = self._analyze_existing_name(source.name)
        
        # Generate strict name
        strict_name = self._generate_strict_name(analysis)
        
        # Determine target channel directory
        channel = analysis["suggested_channel"]
        target_path = self.root / channel / strict_name
        
        # Create transformation plan
        transformation = {
            "source": str(source),
            "target": str(target_path),
            "analysis": analysis,
            "strict_name": strict_name,
            "channel": channel,
            "registry_entry": {
                "purpose": "active",
                "transformed_from": str(source),
                "original_pattern": analysis["pattern"]
            }
        }
        
        return transformation
    
    def _analyze_existing_name(self, filename: str) -> Dict:
        """Analyze existing naming patterns."""
        import re
        
        # Common patterns to detect
        patterns = {
            "versioned": r'(.+)_v(\d+)\.(.+)',
            "dated": r'(.+)_(\d{4}\d{2}\d{2})\.(.+)',
            "suffixed": r'(.+)_(old|new|temp|backup|test|experimental|stable|prod)\.(.+)',
            "channel_versioned": r'(.+)_(nightly|preview|latest)_v(\d+)\.(.+)',
            "simple": r'(.+)\.(.+)'
        }
        
        for pattern_name, pattern in patterns.items():
            match = re.match(pattern, filename)
            if match:
                groups = match.groups()
                
                if pattern_name == "versioned":
                    base_name, version, ext = groups
                    return {
                        "pattern": pattern_name,
                        "base_name": base_name,
                        "version": version,
                        "extension": ext,
                        "suggested_channel": "latest",
                        "purpose": "backup" if int(version) > 1 else "active"
                    }
                
                elif pattern_name == "suffixed":
                    base_name, suffix, ext = groups
                    channel_map = {
                        "experimental": "nightly",
                        "test": "preview",
                        "stable": "latest",
                        "prod": "latest",
                        "old": "latest",
                        "backup": "latest",
                        "temp": "preview"
                    }
                    return {
                        "pattern": pattern_name,
                        "base_name": base_name,
                        "suffix": suffix,
                        "extension": ext,
                        "suggested_channel": channel_map.get(suffix, "latest"),
                        "purpose": "backup" if suffix in ["old", "backup"] else "active"
                    }
                
                elif pattern_name == "channel_versioned":
                    base_name, channel, version, ext = groups
                    return {
                        "pattern": pattern_name,
                        "base_name": base_name,
                        "channel": channel,
                        "version": version,
                        "extension": ext,
                        "suggested_channel": channel,
                        "purpose": "backup" if int(version) > 1 else "active"
                    }
                
                else:  # simple
                    base_name, ext = groups
                    return {
                        "pattern": pattern_name,
                        "base_name": base_name,
                        "extension": ext,
                        "suggested_channel": "latest",
                        "purpose": "active"
                    }
        
        # Fallback
        return {
            "pattern": "unknown",
            "base_name": Path(filename).stem,
            "extension": Path(filename).suffix[1:],
            "suggested_channel": "latest",
            "purpose": "active"
        }
    
    def _generate_strict_name(self, analysis: Dict) -> str:
        """Generate strict naming from analysis."""
        base_name = analysis["base_name"]
        channel = analysis["suggested_channel"]
        extension = analysis["extension"]
        
        # Clean base name
        import re
        base_name = re.sub(r'_(old|new|temp|backup|test|experimental|stable|prod)$', '', base_name)
        base_name = re.sub(r'_v\d+$', '', base_name)
        
        return f"{base_name}_{channel}.{extension}"
    
    def execute_transformation(self, transformation: Dict, copy_mode: bool = True) -> Dict:
        """Execute naming transformation."""
        source = Path(transformation["source"])
        target = Path(transformation["target"])
        
        # Create target directory
        target.parent.mkdir(parents=True, exist_ok=True)
        
        # Handle existing target
        if target.exists():
            self.set_purpose(str(target), "backup", schedule_days=30)
            backup_path = target.with_suffix(f".backup{target.suffix}")
            target.rename(backup_path)
        
        # Copy or move file
        if copy_mode:
            import shutil
            shutil.copy2(source, target)
            operation = "copied"
        else:
            source.rename(target)
            operation = "moved"
        
        # Register in registry
        file_id = self.register_file(str(target), transformation["registry_entry"]["purpose"])
        
        # Add transformation metadata
        self.registry["files"][file_id]["transformation"] = transformation["registry_entry"]
        self._save_registry()
        
        return {
            "operation": operation,
            "source": str(source),
            "target": str(target),
            "registry_id": file_id,
            "strict_naming": True
        }
    
    def list_by_purpose(self, purpose: str = None) -> Dict:
        """List files by purpose."""
        result = {}
        
        for file_id, file_info in self.registry["files"].items():
            file_purpose = file_info["current_purpose"]
            
            if purpose and file_purpose != purpose:
                continue
            
            if file_purpose not in result:
                result[file_purpose] = []
            
            result[file_purpose].append({
                "path": file_id,
                "versions": len(file_info["versions"]),
                "created": file_info["created"],
                "last_updated": file_info["versions"][-1]["timestamp"] if file_info["versions"] else None
            })
        
        return result
    
    def cleanup_scheduled(self, dry_run: bool = False) -> Dict:
        """Execute scheduled cleanup actions."""
        results = {"processed": [], "errors": []}
        current_time = datetime.now()
        
        for schedule_id, schedule_info in self.registry["schedules"].items():
            if schedule_info["status"] != "scheduled":
                continue
            
            scheduled_time = datetime.fromisoformat(schedule_info["scheduled_date"])
            if current_time < scheduled_time:
                continue
            
            try:
                file_id = schedule_info["file_id"]
                action = schedule_info["action"]
                
                if dry_run:
                    results["processed"].append(f"Would {action}: {file_id}")
                else:
                    if action == "cleanup":
                        file_path = Path(file_id)
                        if file_path.exists():
                            file_path.unlink()
                        self.registry["files"][file_id]["current_purpose"] = "deleted"
                    
                    schedule_info["status"] = "completed"
                    results["processed"].append(f"Completed {action}: {file_id}")
            
            except Exception as e:
                results["errors"].append(f"Error processing {schedule_id}: {str(e)}")
        
        if not dry_run:
            self._save_registry()
        
        return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Version registry with strict naming")
    parser.add_argument("action", choices=["register", "transform", "list", "cleanup", "schedule"])
    parser.add_argument("--file", help="File path")
    parser.add_argument("--purpose", choices=["active", "backup", "deprecated", "cleanup"], default="active")
    parser.add_argument("--schedule-days", type=int, help="Schedule action in N days")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    
    args = parser.parse_args()
    
    registry = VersionRegistry()
    
    try:
        if args.action == "register":
            if not args.file:
                print("❌ --file required")
                return 1
            
            file_id = registry.register_file(args.file, args.purpose)
            print(f"✅ Registered: {file_id}")
            print(f"🎯 Purpose: {args.purpose}")
        
        elif args.action == "transform":
            if not args.file:
                print("❌ --file required")
                return 1
            
            transformation = registry.transform_existing_naming(args.file)
            
            print(f"📋 Transformation Plan:")
            print(f"  Source: {transformation['source']}")
            print(f"  Target: {transformation['target']}")
            print(f"  Pattern: {transformation['analysis']['pattern']}")
            print(f"  Channel: {transformation['channel']}")
            print(f"  Strict: {transformation['strict_name']}")
            
            if not args.dry_run:
                result = registry.execute_transformation(transformation)
                print(f"✅ {result['operation'].title()}: {result['source']} → {result['target']}")
        
        elif args.action == "list":
            files = registry.list_by_purpose(args.purpose)
            
            print("📋 Registry Contents:")
            for purpose, file_list in files.items():
                print(f"\n{purpose.upper()}:")
                for file_info in file_list:
                    print(f"  📄 {file_info['path']} ({file_info['versions']} versions)")
        
        elif args.action == "cleanup":
            results = registry.cleanup_scheduled(args.dry_run)
            
            print(f"🧹 Cleanup {'Simulation' if args.dry_run else 'Results'}:")
            for item in results["processed"]:
                print(f"  ✅ {item}")
            for error in results["errors"]:
                print(f"  ❌ {error}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
