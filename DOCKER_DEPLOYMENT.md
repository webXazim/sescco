# Ubuntu VPS Docker Deployment (IONOS)

The production stack contains Django/Gunicorn, PostgreSQL 16, and Caddy. Each
deployment is isolated by `COMPOSE_PROJECT_NAME`, so its containers, database,
media, static files, and Caddy state do not overlap another site.

## Fast first deployment

Point the domain's DNS `A` record to the IONOS VPS, clone the repository, and run:

```sh
sudo sh scripts/deploy.sh --domain example.com --email admin@example.com --project example-site --seed
```

That single command:

1. installs Docker Engine/Compose on Ubuntu when they are missing;
2. creates a permission-restricted `.env` with random Django and PostgreSQL secrets;
3. builds and starts the isolated Compose stack;
4. waits for PostgreSQL and Gunicorn health checks;
5. applies migrations and collects static files;
6. loads the idempotent SESCCO CMS/localization seed and runs deployment audits;
7. validates Django, Caddy, and `/healthz/`.

The generated environment contains the primary domain only. Add `www.example.com`
to `SITE_DOMAIN` and `ALLOWED_HOSTS`, and add
`https://www.example.com` to `CSRF_TRUSTED_ORIGINS` only if its DNS record exists.

For later code or environment deployments that preserve CMS edits, use:

```sh
sh scripts/deploy.sh
```

Seeding is explicit because it intentionally refreshes canonical content fields.
Run `sh scripts/deploy.sh --seed` (or `-s`) only when the full site seed should be
applied again.

## Hosting several sites on one VPS

Every site must use a unique:

- repository directory;
- `COMPOSE_PROJECT_NAME` (for container, network, and volume isolation);
- host HTTP/HTTPS ports if it has its own Caddy container.

Only one process can own public ports `80` and `443` on one IP. There are two
supported layouts:

### One directly exposed site

Use the defaults for the public stack:

```env
COMPOSE_PROJECT_NAME=sescco
BIND_ADDRESS=0.0.0.0
HTTP_PORT=80
HTTPS_PORT=443
```

### Several sites behind one shared reverse proxy

Use one host-level/shared proxy for public ports `80/443`. Bind each project's
Caddy only to loopback and give it a unique upstream port pair:

```env
# Site A
COMPOSE_PROJECT_NAME=site_a
BIND_ADDRESS=127.0.0.1
HTTP_PORT=8081
HTTPS_PORT=8441

# Site B, in its own repository and .env
COMPOSE_PROJECT_NAME=site_b
BIND_ADDRESS=127.0.0.1
HTTP_PORT=8082
HTTPS_PORT=8442
```

The shared proxy routes each domain to its matching loopback HTTP port, for
example `127.0.0.1:8081` and `127.0.0.1:8082`. It must preserve `Host`,
`X-Forwarded-For`, and `X-Forwarded-Proto`. Loopback binding prevents visitors
from bypassing the shared proxy. Do not expose several independent Caddy
containers on `0.0.0.0:80/443`.

If the shared proxy terminates TLS, configure the per-site Caddy address as
`http://example.com` in `SITE_DOMAIN`; the outer proxy remains responsible for
the public certificate.

A new behind-proxy site can generate that configuration in one command:

```sh
sudo sh scripts/deploy.sh --domain site-b.example.com --email admin@example.com \
  --project site-b --behind-proxy --http-port 8082 --https-port 8442
```

## Existing environment file

To configure manually:

```sh
cp .env.production.example .env
chmod 600 .env
nano .env
sh scripts/deploy.sh
```

Keep `POSTGRES_PASSWORD` and the password inside `DATABASE_URL` identical. Never
reuse the same `COMPOSE_PROJECT_NAME` between unrelated projects.

## Operations

```sh
# Status and logs
docker compose ps
docker compose logs -f web caddy db

# Deploy changed code without refreshing CMS seed fields
sh scripts/deploy.sh

# Explicitly refresh canonical seeded content
sh scripts/deploy.sh --seed

# Backup and restore this isolated database
sh scripts/backup_postgres.sh
sh scripts/restore_postgres.sh backups/postgres_YYYYmmdd_HHMMSS.dump

# Stop containers but preserve data volumes
docker compose down
```

Do not use `docker compose down -v` in production; `-v` deletes the site's
PostgreSQL, media, static, and certificate volumes.

## IONOS firewall checklist

Allow inbound TCP `22`, `80`, and `443` in both the IONOS firewall policy and
Ubuntu UFW. Database port `5432` and per-site loopback ports must not be publicly
opened. The bootstrap script enables UFW rules for SSH/HTTP/HTTPS.

Before accepting applications, configure SMTP values in `.env`. Applicant files
under `/media/careers/applications/` are deliberately blocked at Caddy and are
served only by staff-authenticated dashboard download views.
