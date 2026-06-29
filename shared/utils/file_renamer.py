#!/usr/bin/env python3
"""File renaming tool with flexible naming convention."""

import os
import shutil
import sys
from pathlib import Path
import re


class FileRenamer:
    def __init__(self):
        self.channels = ["nightly", "preview", "latest"]
        self.extensions = ["sh", "py", "js", "md", "yml", "yaml", "json"]
    
    def parse_target_name(self, target_name: str) -> dict:
        """Parse target name: 'file_name_channel_version.ext' or 'file_name_channel.ext'"""
        # Pattern: filename_channel_version.ext or filename_channel.ext
        pattern = r'^(.+)_(nightly|preview|latest)(?:_v?(\d+))?\.([a-zA-Z0-9]+)$'
        match = re.match(pattern, target_name)
        
        if not match:
            raise ValueError(f"Invalid target name format: {target_name}")
        
        file_name, channel, version, extension = match.groups()
        
        return {
            "file_name": file_name,
            "channel": channel,
            "version": int(version) if version else None,
            "extension": extension,
            "strict_name": f"{file_name}_{channel}.{extension}",
            "versioned_name": f"{file_name}_{channel}_v{version}.{extension}" if version else None
        }
    
    def rename_file(self, source_path: str, target_name: str, copy_mode: bool = True) -> dict:
        """Rename file according to strict naming convention."""
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        parsed = self.parse_target_name(target_name)
        channel = parsed["channel"]
        
        # Only allow strict naming (no versions in filename)
        if parsed["version"]:
            raise ValueError("Version numbers not allowed in filenames. Use registry for version management.")
        
        # Create channel directory if needed
        channel_dir = Path(channel)
        channel_dir.mkdir(exist_ok=True)
        
        # Use strict naming only
        target_path = channel_dir / parsed["strict_name"]
        
        # Handle existing files via registry
        if target_path.exists():
            from .version_registry import VersionRegistry
            registry = VersionRegistry()
            registry.set_purpose(str(target_path), "backup", schedule_days=30)
            
            backup_path = target_path.with_suffix(f".backup{target_path.suffix}")
            shutil.move(target_path, backup_path)
            print(f"📦 Backed up via registry: {backup_path}")
        
        # Copy or move file
        if copy_mode:
            shutil.copy2(source, target_path)
            operation = "copied"
        else:
            shutil.move(source, target_path)
            operation = "moved"
        
        # Make executable if shell script
        if parsed["extension"] == "sh":
            target_path.chmod(0o755)
        
        # Register in version registry
        from .version_registry import VersionRegistry
        registry = VersionRegistry()
        registry.register_file(str(target_path), "active")
        
        result = {
            "operation": operation,
            "source": str(source),
            "target": str(target_path),
            "channel": channel,
            "strict_format": True,
            "registered": True,
            "accessible_via": self._get_access_methods(parsed)
        }
        
        return result
    
    def _get_access_methods(self, parsed: dict) -> list:
        """Get methods to access the renamed file."""
        methods = []
        channel = parsed["channel"]
        
        if parsed["extension"] == "py":
            if parsed["version"]:
                methods.append(f"./{channel}.sh {parsed['version']}")
            else:
                methods.append(f"python3 {channel}/{parsed['strict_name']}")
        elif parsed["extension"] == "sh":
            methods.append(f"./{parsed['strict_name']}")
        else:
            methods.append(f"cat {channel}/{parsed['strict_name']}")
        
        return methods
    
    def auto_rename(self, source_path: str, channel: str, extension: str = None) -> dict:
        """Auto-rename file with smart naming."""
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source_path}")
        
        # Extract base name
        base_name = source.stem
        if not extension:
            extension = source.suffix[1:] if source.suffix else "py"
        
        # Generate target name (strict format)
        target_name = f"{base_name}_{channel}.{extension}"
        
        return self.rename_file(source_path, target_name)
    
    def list_channel_files(self, channel: str = None) -> dict:
        """List files in channels."""
        if channel and channel not in self.channels:
            raise ValueError(f"Invalid channel: {channel}")
        
        channels_to_check = [channel] if channel else self.channels
        result = {}
        
        for ch in channels_to_check:
            ch_dir = Path(ch)
            if ch_dir.exists():
                files = []
                for file_path in ch_dir.iterdir():
                    if file_path.is_file():
                        # Parse file name
                        name = file_path.name
                        is_versioned = bool(re.search(r'_v\d+\.', name))
                        is_strict = not is_versioned and f"_{ch}." in name
                        
                        files.append({
                            "name": name,
                            "path": str(file_path),
                            "size": file_path.stat().st_size,
                            "type": "versioned" if is_versioned else "strict" if is_strict else "other",
                            "executable": file_path.suffix == ".sh" and os.access(file_path, os.X_OK)
                        })
                
                result[ch] = sorted(files, key=lambda x: x["name"])
            else:
                result[ch] = []
        
        return result
    
    def promote_to_strict(self, channel: str, versioned_file: str) -> dict:
        """Promote versioned file to strict naming."""
        ch_dir = Path(channel)
        versioned_path = ch_dir / versioned_file
        
        if not versioned_path.exists():
            raise FileNotFoundError(f"Versioned file not found: {versioned_path}")
        
        # Parse versioned name to get strict name
        pattern = r'^(.+)_(nightly|preview|latest)_v\d+\.([a-zA-Z0-9]+)$'
        match = re.match(pattern, versioned_file)
        
        if not match:
            raise ValueError(f"Not a versioned file: {versioned_file}")
        
        file_name, channel_name, extension = match.groups()
        strict_name = f"{file_name}_{channel_name}.{extension}"
        strict_path = ch_dir / strict_name
        
        # Backup existing strict file if exists
        if strict_path.exists():
            backup_path = strict_path.with_suffix(f".backup.{strict_path.suffix}")
            shutil.move(strict_path, backup_path)
            print(f"📦 Backed up existing strict file: {backup_path}")
        
        # Copy versioned to strict
        shutil.copy2(versioned_path, strict_path)
        
        return {
            "promoted": str(versioned_path),
            "to_strict": str(strict_path),
            "channel": channel
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="File renaming tool with flexible naming")
    parser.add_argument("action", choices=["rename", "auto", "list", "promote"])
    parser.add_argument("--source", help="Source file path")
    parser.add_argument("--target", help="Target name (e.g., 'tool_nightly_v1.py' or 'tool_nightly.py')")
    parser.add_argument("--channel", choices=["nightly", "preview", "latest"], help="Target channel")
    parser.add_argument("--extension", help="File extension")
    parser.add_argument("--move", action="store_true", help="Move instead of copy")
    parser.add_argument("--versioned-file", help="Versioned file to promote")
    
    args = parser.parse_args()
    
    renamer = FileRenamer()
    
    try:
        if args.action == "rename":
            if not args.source or not args.target:
                print("❌ --source and --target required for rename")
                return 1
            
            result = renamer.rename_file(args.source, args.target, not args.move)
            
            print(f"✅ File {result['operation']}: {result['source']} → {result['target']}")
            print(f"📁 Channel: {result['channel']}")
            print(f"🎯 Format: {'Strict' if result['strict_format'] else 'Versioned (temporary)'}")
            print(f"🚀 Access via:")
            for method in result['accessible_via']:
                print(f"   {method}")
        
        elif args.action == "auto":
            if not args.source or not args.channel:
                print("❌ --source and --channel required for auto rename")
                return 1
            
            result = renamer.auto_rename(args.source, args.channel, args.extension)
            
            print(f"✅ Auto-renamed: {result['source']} → {result['target']}")
            print(f"🎯 Strict format (permanent naming)")
            print(f"🚀 Access via:")
            for method in result['accessible_via']:
                print(f"   {method}")
        
        elif args.action == "list":
            files = renamer.list_channel_files(args.channel)
            
            print("📋 Channel Files:")
            for channel, channel_files in files.items():
                print(f"\n{channel.upper()}:")
                if channel_files:
                    for file_info in channel_files:
                        type_icon = "🔢" if file_info["type"] == "versioned" else "📌" if file_info["type"] == "strict" else "📄"
                        exec_icon = "⚡" if file_info["executable"] else ""
                        print(f"  {type_icon}{exec_icon} {file_info['name']} ({file_info['size']} bytes)")
                else:
                    print("  No files")
            
            print(f"\n🎯 Naming Convention:")
            print(f"  📌 Strict: filename_channel.ext (permanent)")
            print(f"  🔢 Versioned: filename_channel_v1.ext (temporary)")
        
        elif args.action == "promote":
            if not args.channel or not args.versioned_file:
                print("❌ --channel and --versioned-file required for promote")
                return 1
            
            result = renamer.promote_to_strict(args.channel, args.versioned_file)
            
            print(f"⬆️  Promoted: {result['promoted']} → {result['to_strict']}")
            print(f"🎯 Now using strict naming (permanent)")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
