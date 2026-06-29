#!/usr/bin/env python3
"""Backup Manager: Automated database backups with rotation"""
import shutil
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/media/sunil-kr/workspace/workspace-system/workspace_knowledge.db")
BACKUP_DIR = Path(__file__).parent / "backups"


def backup_database():
    """Create timestamped backup"""
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"workspace_{timestamp}.db"

    shutil.copy2(DB_PATH, backup_path)
    size = backup_path.stat().st_size / 1024
    print(f"✓ Backup created: {backup_path.name} ({size:.1f} KB)")
    return backup_path


def rotate_backups():
    """Keep 7 daily, 4 weekly, 12 monthly"""
    if not BACKUP_DIR.exists():
        return

    backups = sorted(BACKUP_DIR.glob("workspace_*.db"))
    now = datetime.now()

    keep = set()
    # Keep last 7 days
    for i in range(7):
        date = (now - timedelta(days=i)).strftime("%Y%m%d")
        for b in backups:
            if date in b.name:
                keep.add(b)
                break

    # Keep 4 weekly (Mondays)
    for i in range(4):
        date = now - timedelta(weeks=i)
        monday = date - timedelta(days=date.weekday())
        date_str = monday.strftime("%Y%m%d")
        for b in backups:
            if date_str in b.name:
                keep.add(b)
                break

    # Keep 12 monthly (1st of month)
    for i in range(12):
        month = now.month - i
        year = now.year
        while month < 1:
            month += 12
            year -= 1
        date_str = f"{year}{month:02d}01"
        for b in backups:
            if date_str in b.name:
                keep.add(b)
                break

    # Remove old backups
    removed = 0
    for backup in backups:
        if backup not in keep:
            backup.unlink()
            removed += 1

    print(f"✓ Rotation: kept {len(keep)}, removed {removed}")


def list_backups():
    """List all backups"""
    if not BACKUP_DIR.exists():
        print("No backups found")
        return

    backups = sorted(BACKUP_DIR.glob("workspace_*.db"), reverse=True)
    print(f"\n📦 BACKUPS ({len(backups)} total)")
    print("-" * 60)
    for b in backups[:10]:
        size = b.stat().st_size / 1024
        mtime = datetime.fromtimestamp(b.stat().st_mtime)
        age = datetime.now() - mtime
        print(f"  {b.name:30} {size:6.1f} KB  {age.days}d ago")
    if len(backups) > 10:
        print(f"  ... and {len(backups) - 10} more")


def restore_backup(backup_name):
    """Restore from backup"""
    backup_path = BACKUP_DIR / backup_name
    if not backup_path.exists():
        print(f"✗ Backup not found: {backup_name}")
        return False

    # Create safety backup of current
    safety = (
        DB_PATH.parent / f"workspace_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    )
    shutil.copy2(DB_PATH, safety)

    # Restore
    shutil.copy2(backup_path, DB_PATH)
    print(f"✓ Restored from: {backup_name}")
    print(f"✓ Safety backup: {safety.name}")
    return True


if __name__ == "__main__":
    import sys
    from datetime import timedelta

    if len(sys.argv) < 2:
        print("Usage:")
        print("  backup_manager.py backup   - Create backup")
        print("  backup_manager.py rotate   - Rotate old backups")
        print("  backup_manager.py list     - List backups")
        print("  backup_manager.py restore <name> - Restore backup")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "backup":
        backup_database()
        rotate_backups()
    elif cmd == "rotate":
        rotate_backups()
    elif cmd == "list":
        list_backups()
    elif cmd == "restore" and len(sys.argv) > 2:
        restore_backup(sys.argv[2])
    else:
        print("Invalid command")
