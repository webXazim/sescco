#!/bin/sh
set -eu

mkdir -p backups
timestamp="$(date +%Y%m%d_%H%M%S)"
backup_file="backups/postgres_${timestamp}.dump"

docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$backup_file"

echo "Created $backup_file"
