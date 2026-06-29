#!/usr/bin/env python3
"""Version manager for consolidation modules - easy creation and renaming."""

import shutil
import sys
from pathlib import Path
from datetime import datetime


class VersionManager:
    def __init__(self, workspace_root: str = "."):
        self.root = Path(workspace_root).resolve()
        self.channels = ["nightly", "preview", "latest"]
    
    def create_new_version(self, channel: str, source_file: str = None) -> str:
        """Create new version in specified channel."""
        if channel not in self.channels:
            raise ValueError(f"Invalid channel. Use: {', '.join(self.channels)}")
        
        channel_dir = self.root / channel
        channel_dir.mkdir(exist_ok=True)
        
        # Find next version number
        existing_versions = list(channel_dir.glob(f"{channel}_v*.py"))
        if existing_versions:
            versions = [int(f.stem.split('_v')[1]) for f in existing_versions]
            next_version = max(versions) + 1
        else:
            next_version = 1
        
        new_file = channel_dir / f"{channel}_v{next_version}.py"
        
        if source_file and Path(source_file).exists():
            # Copy from source file
            shutil.copy2(source_file, new_file)
            print(f"✅ Created {channel} v{next_version} from {source_file}")
        else:
            # Create template
            template = self._generate_template(channel, next_version)
            new_file.write_text(template)
            print(f"✅ Created {channel} v{next_version} template")
        
        return str(new_file)
    
    def rename_to_channel(self, source_file: str, target_channel: str) -> str:
        """Rename any file to join the versioned ecosystem."""
        source_path = Path(source_file)
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_file}")
        
        if target_channel not in self.channels:
            raise ValueError(f"Invalid channel. Use: {', '.join(self.channels)}")
        
        # Create new version in target channel
        new_version_file = self.create_new_version(target_channel, source_file)
        
        print(f"🔄 Renamed {source_file} → {new_version_file}")
        print(f"💡 Original file preserved at: {source_file}")
        print(f"🚀 New file accessible via: {target_channel}.sh")
        
        return new_version_file
    
    def promote_version(self, from_channel: str, version: int, to_channel: str) -> str:
        """Promote version from one channel to another."""
        if from_channel not in self.channels or to_channel not in self.channels:
            raise ValueError(f"Invalid channels. Use: {', '.join(self.channels)}")
        
        source_file = self.root / from_channel / f"{from_channel}_v{version}.py"
        if not source_file.exists():
            raise FileNotFoundError(f"Source version not found: {source_file}")
        
        # Create new version in target channel
        target_file = self.create_new_version(to_channel, str(source_file))
        
        print(f"⬆️  Promoted {from_channel} v{version} → {to_channel}")
        print(f"📁 Source preserved: {source_file}")
        print(f"📁 Target created: {target_file}")
        
        return target_file
    
    def list_versions(self) -> dict:
        """List all versions across channels."""
        versions = {}
        
        for channel in self.channels:
            channel_dir = self.root / channel
            if channel_dir.exists():
                files = list(channel_dir.glob(f"{channel}_v*.py"))
                versions[channel] = sorted([
                    {
                        "version": int(f.stem.split('_v')[1]),
                        "file": str(f),
                        "size": f.stat().st_size,
                        "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                    }
                    for f in files
                ], key=lambda x: x["version"])
            else:
                versions[channel] = []
        
        return versions
    
    def _generate_template(self, channel: str, version: int) -> str:
        """Generate template for new version."""
        status_map = {
            "nightly": "EXPERIMENTAL",
            "preview": "PREVIEW", 
            "latest": "STABLE"
        }
        
        emoji_map = {
            "nightly": "🌙",
            "preview": "🔍",
            "latest": "✅"
        }
        
        status = status_map[channel]
        emoji = emoji_map[channel]
        
        return f'''#!/usr/bin/env python3
"""{channel.title()} v{version} - {status} consolidation version."""

import sys
from pathlib import Path

def main():
    print("{emoji} {channel.title()} v{version} - {status}")
    print("Status: {status}")
    print("Features: Add your features here")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("\\nUsage: {channel}.sh {version} [options]")
        print("Options:")
        print("  --help     Show this help")
        print("  --version  Show version info")
        return 0
    
    if len(sys.argv) > 1 and sys.argv[1] == "--version":
        print("{channel}_v{version}.py - Version {version}.0.0-{status.lower()}")
        return 0
    
    print("Running {channel} v{version}...")
    # Add your logic here
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Version manager for consolidation modules")
    parser.add_argument("action", choices=["create", "rename", "promote", "list"])
    parser.add_argument("--channel", choices=["nightly", "preview", "latest"], help="Target channel")
    parser.add_argument("--source", help="Source file path")
    parser.add_argument("--from-channel", help="Source channel for promotion")
    parser.add_argument("--version", type=int, help="Version number for promotion")
    parser.add_argument("--to-channel", help="Target channel for promotion")
    
    args = parser.parse_args()
    
    manager = VersionManager()
    
    try:
        if args.action == "create":
            if not args.channel:
                print("❌ --channel required for create action")
                return 1
            
            result = manager.create_new_version(args.channel, args.source)
            print(f"🎯 Use: {args.channel}.sh to run latest version")
            
        elif args.action == "rename":
            if not args.source or not args.channel:
                print("❌ --source and --channel required for rename action")
                return 1
            
            result = manager.rename_to_channel(args.source, args.channel)
            
        elif args.action == "promote":
            if not all([args.from_channel, args.version, args.to_channel]):
                print("❌ --from-channel, --version, and --to-channel required for promote action")
                return 1
            
            result = manager.promote_version(args.from_channel, args.version, args.to_channel)
            
        elif args.action == "list":
            versions = manager.list_versions()
            
            print("📋 Version Overview:")
            for channel, channel_versions in versions.items():
                print(f"\\n{channel.upper()}:")
                if channel_versions:
                    for v in channel_versions:
                        print(f"  v{v['version']} - {v['file']} ({v['size']} bytes)")
                else:
                    print("  No versions")
            
            print(f"\\n🚀 Usage:")
            print(f"  nightly.sh [version]  # Run nightly version")
            print(f"  preview.sh [version]  # Run preview version") 
            print(f"  latest.sh [version]   # Run latest version")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
