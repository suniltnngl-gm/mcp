#!/bin/bash
# Unified backup orchestration: runs periodic + pre-edit backups.
# Usage: ./orchestrated_backup.sh              (full backup)
#        ./orchestrated_backup.sh pre <file>   (pre-edit snapshot)

set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKUP_ROOT="$BASE_DIR/backups"
LOG_FILE="$BACKUP_ROOT/orchestration.log"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p "$BACKUP_ROOT"

log() {
  echo "[$TIMESTAMP] $*" | tee -a "$LOG_FILE"
}

case "${1:-}" in
  pre)
    FILE="${2:-}"
    if [ -z "$FILE" ]; then
      echo "Usage: $0 pre <file>"
      exit 1
    fi
    log "Pre-edit backup: $FILE"
    bash "$BASE_DIR/pre_edit_backup.sh" "$FILE"
    ;;
  *)
    log "Starting periodic snapshot backup..."
    bash "$BASE_DIR/simple_backup.sh"
    log "Periodic backup complete."
    ;;
esac
