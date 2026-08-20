#!/bin/sh
set -eu

if [ "${DATABASE_HOST:-}" ]; then
  echo "Waiting for PostgreSQL at ${DATABASE_HOST}:${DATABASE_PORT:-5432}..."
  while ! nc -z "$DATABASE_HOST" "${DATABASE_PORT:-5432}"; do
    sleep 1
  done
fi

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
  python manage.py migrate --noinput
fi

if [ "${OPTIMIZE_PUBLIC_IMAGES:-1}" = "1" ]; then
  python manage.py optimize_public_images
fi

if [ "${RUN_COLLECTSTATIC:-1}" = "1" ]; then
  python scripts/build_css_bundle.py
  python manage.py collectstatic --noinput
fi

exec "$@"
