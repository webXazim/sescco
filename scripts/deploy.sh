#!/bin/sh
set -eu

usage() {
  cat <<'EOF'
Usage:
  sudo sh scripts/deploy.sh --domain example.com --email admin@example.com [options]
  sh scripts/deploy.sh [--env-file .env] [--no-seed]

Options:
  --domain NAME       Primary domain; required only when creating a new .env
  --email ADDRESS     ACME/Let's Encrypt email; required with --domain
  --project NAME      Unique Docker Compose project name (default: domain slug)
  --behind-proxy      Bind to loopback; shared proxy terminates public TLS
  --bind ADDRESS      0.0.0.0 for the public stack or 127.0.0.1 behind a proxy
  --http-port PORT    Host HTTP port (default: 80)
  --https-port PORT   Host HTTPS port (default: 443)
  --env-file PATH     Environment file (default: .env)
  --no-seed           Deploy without refreshing the idempotent CMS seed
  --skip-install      Do not install Docker automatically when it is missing
  -h, --help          Show this help
EOF
}

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
cd "$PROJECT_DIR"

ENV_FILE=.env
DOMAIN=
ACME_EMAIL_VALUE=
PROJECT_NAME=
BIND_VALUE=0.0.0.0
HTTP_PORT_VALUE=80
HTTPS_PORT_VALUE=443
RUN_SEED=1
SKIP_INSTALL=0
BEHIND_PROXY=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --domain) DOMAIN=${2:?Missing value for --domain}; shift 2 ;;
    --email) ACME_EMAIL_VALUE=${2:?Missing value for --email}; shift 2 ;;
    --project) PROJECT_NAME=${2:?Missing value for --project}; shift 2 ;;
    --behind-proxy) BEHIND_PROXY=1; BIND_VALUE=127.0.0.1; shift ;;
    --bind) BIND_VALUE=${2:?Missing value for --bind}; shift 2 ;;
    --http-port) HTTP_PORT_VALUE=${2:?Missing value for --http-port}; shift 2 ;;
    --https-port) HTTPS_PORT_VALUE=${2:?Missing value for --https-port}; shift 2 ;;
    --env-file) ENV_FILE=${2:?Missing value for --env-file}; shift 2 ;;
    --no-seed) RUN_SEED=0; shift ;;
    --skip-install) SKIP_INSTALL=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if ! command -v docker >/dev/null 2>&1; then
  if [ "$SKIP_INSTALL" = 1 ]; then
    echo "Docker is not installed and --skip-install was supplied." >&2
    exit 1
  fi
  if [ "$(id -u)" -ne 0 ]; then
    echo "Docker is missing. Re-run this command with sudo so it can be installed." >&2
    exit 1
  fi
  echo "Docker not found; preparing this Ubuntu VPS first..."
  sh "$SCRIPT_DIR/bootstrap_droplet.sh"
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose v2 is required (the 'docker compose' command)." >&2
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  if [ -z "$DOMAIN" ] || [ -z "$ACME_EMAIL_VALUE" ]; then
    echo "Missing $ENV_FILE. Supply --domain and --email to create it securely." >&2
    echo "Example: sudo sh scripts/deploy.sh --domain example.com --email admin@example.com" >&2
    exit 1
  fi
  case "$DOMAIN$ACME_EMAIL_VALUE$PROJECT_NAME" in
    *[!A-Za-z0-9.@_-]*) echo "Domain, email, and project values may only contain letters, numbers, dot, @, underscore, and hyphen." >&2; exit 2 ;;
  esac
  case "$BIND_VALUE" in
    *[!0-9a-fA-F.:]*) echo "Invalid bind address: $BIND_VALUE" >&2; exit 2 ;;
  esac
  case "$HTTP_PORT_VALUE$HTTPS_PORT_VALUE" in
    *[!0-9]*) echo "HTTP and HTTPS ports must be numeric." >&2; exit 2 ;;
  esac
  if [ "$BEHIND_PROXY" = 1 ] && { [ "$HTTP_PORT_VALUE" = 80 ] || [ "$HTTPS_PORT_VALUE" = 443 ]; }; then
    echo "--behind-proxy requires unique --http-port and --https-port values." >&2
    exit 2
  fi

  if [ -z "$PROJECT_NAME" ]; then
    PROJECT_NAME=$(printf '%s' "$DOMAIN" | tr '[:upper:]' '[:lower:]' | tr '.' '-' | tr -cd 'a-z0-9_-')
  fi
  SECRET_KEY_VALUE=$(openssl rand -hex 48)
  POSTGRES_PASSWORD_VALUE=$(openssl rand -hex 32)
  SITE_ADDRESS_VALUE=$DOMAIN
  if [ "$BEHIND_PROXY" = 1 ]; then
    SITE_ADDRESS_VALUE=http://$DOMAIN
  fi
  umask 077
  cat > "$ENV_FILE" <<EOF
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
SECRET_KEY=$SECRET_KEY_VALUE
COMPOSE_PROJECT_NAME=$PROJECT_NAME
BIND_ADDRESS=$BIND_VALUE
HTTP_PORT=$HTTP_PORT_VALUE
HTTPS_PORT=$HTTPS_PORT_VALUE
SITE_DOMAIN=$SITE_ADDRESS_VALUE
ACME_EMAIL=$ACME_EMAIL_VALUE
ALLOWED_HOSTS=$DOMAIN
CSRF_TRUSTED_ORIGINS=https://$DOMAIN
DATABASE_URL=postgres://company_profile:$POSTGRES_PASSWORD_VALUE@db:5432/company_profile
DATABASE_HOST=db
DATABASE_PORT=5432
POSTGRES_DB=company_profile
POSTGRES_USER=company_profile
POSTGRES_PASSWORD=$POSTGRES_PASSWORD_VALUE
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
USE_X_FORWARDED_HOST=True
SECURE_HSTS_SECONDS=31536000
DATABASE_CONN_MAX_AGE=60
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_TIMEOUT=15
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=info@$DOMAIN
SERVER_EMAIL=info@$DOMAIN
MEDIA_ROOT=media
MEDIA_URL=/media/
CAREER_MAX_UPLOAD_SIZE=8388608
CAREER_APPLICATION_RATE_LIMIT_COUNT=5
CAREER_APPLICATION_RATE_LIMIT_WINDOW=3600
EOF
  echo "Created secure production environment: $ENV_FILE"
fi

compose() {
  APP_ENV_FILE="$ENV_FILE" docker compose --env-file "$ENV_FILE" "$@"
}

echo "Validating Docker Compose configuration..."
compose config --quiet

echo "Building and starting the isolated site stack..."
compose pull db caddy
compose build --pull web
# --wait makes this command fail if PostgreSQL or Gunicorn never becomes healthy.
compose up -d --remove-orphans --wait --wait-timeout 180

if [ "$RUN_SEED" = 1 ]; then
  echo "Loading the idempotent production CMS seed and running deployment audits..."
  compose exec -T web python manage.py seed_sescco_production \
    --run-audit --run-language-audit --run-asset-audit --run-admin-audit --run-final-audit
fi

echo "Running Django's production deployment checks..."
compose exec -T web python manage.py check --deploy

echo "Validating Caddy and checking the application health endpoint..."
compose exec -T caddy caddy validate --config /etc/caddy/Caddyfile
HEALTH_HOST=$(sed -n 's/^ALLOWED_HOSTS=\([^,]*\).*/\1/p' "$ENV_FILE")
compose exec -T -e HEALTHCHECK_HOST="$HEALTH_HOST" web python -c "import os, urllib.request; r=urllib.request.Request('http://127.0.0.1:8000/healthz/', headers={'Host':os.environ['HEALTHCHECK_HOST'],'X-Forwarded-Proto':'https'}); print(urllib.request.urlopen(r, timeout=10).read().decode())"
printf '\nDeployment complete.\n'
compose ps
