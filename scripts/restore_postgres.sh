#!/bin/sh
set -eu

if [ "${1:-}" = "" ]; then
  echo "Usage: sh scripts/restore_postgres.sh backups/postgres_YYYYmmdd_HHMMSS.dump"
  exit 1
fi

backup_file="$1"

if [ ! -f "$backup_file" ]; then
  echo "Backup file not found: $backup_file"
  exit 1
fi

docker compose exec -T db sh -c 'pg_restore --clean --if-exists -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < "$backup_file"

echo "Restored $backup_file"
