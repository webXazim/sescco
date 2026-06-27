#!/bin/sh
set -eu

if [ ! -f .env ]; then
  echo "Missing .env. Copy .env.production.example to .env and fill production values first."
  exit 1
fi

docker compose pull db caddy
docker compose build --pull web
docker compose up -d --remove-orphans
docker compose exec web python manage.py check --deploy

echo "Deployment complete."
