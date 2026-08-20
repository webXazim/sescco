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

# Image conversion can take several minutes on an established media volume.
# Keep it out of the health-critical startup path; deploy.sh runs it after
# Gunicorn is healthy. It remains opt-in here for one-off maintenance jobs.
if [ "${OPTIMIZE_PUBLIC_IMAGES:-0}" = "1" ]; then
  python manage.py optimize_public_images
fi

if [ "${RUN_COLLECTSTATIC:-1}" = "1" ]; then
  python scripts/build_css_bundle.py
  python manage.py collectstatic --noinput
fi

exec "$@"
