# DigitalOcean Droplet Deployment

This project is ready to run on an Ubuntu DigitalOcean Droplet with Docker Compose, PostgreSQL, Gunicorn, and Caddy. Caddy is the public web server and will request/renew HTTPS certificates automatically when your domain DNS points to the droplet.

## 1. Create The Droplet

Use an Ubuntu LTS droplet with at least 1 GB RAM. Add your SSH key during droplet creation.

Point DNS records to the droplet IP:

```text
A     example.com       DROPLET_IP
A     www.example.com   DROPLET_IP
```

## 2. Bootstrap The Server

SSH into the droplet, clone or upload this project, then run:

```sh
sudo sh scripts/bootstrap_droplet.sh
```

This installs Docker, Docker Compose, Git, and enables the firewall for SSH, HTTP, and HTTPS.

## 3. Configure Production Environment

Copy the production template:

```sh
cp .env.production.example .env
```

Edit `.env` and set real values:

```env
SITE_DOMAIN=example.com, www.example.com
ACME_EMAIL=admin@example.com
SECRET_KEY=replace-with-a-long-random-secret
ALLOWED_HOSTS=example.com,www.example.com
CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
POSTGRES_PASSWORD=replace-db-password
DATABASE_URL=postgres://company_profile:replace-db-password@db:5432/company_profile
```

Keep `POSTGRES_PASSWORD` and the password inside `DATABASE_URL` identical.

## 4. Deploy

```sh
sh scripts/deploy.sh
```

The deployment starts PostgreSQL, waits for it to become healthy, runs migrations, collects static files, starts Gunicorn, and exposes the site through Caddy on ports 80 and 443.

Create the first admin user:

```sh
docker compose exec web python manage.py createsuperuser
```

## 5. Operations

View logs:

```sh
docker compose logs -f web
docker compose logs -f caddy
docker compose logs -f db
```

Restart after code changes:

```sh
sh scripts/deploy.sh
```

Run Django checks:

```sh
docker compose exec web python manage.py check --deploy
```

Back up PostgreSQL:

```sh
sh scripts/backup_postgres.sh
```

Restore PostgreSQL:

```sh
sh scripts/restore_postgres.sh backups/postgres_YYYYmmdd_HHMMSS.dump
```

Stop the stack:

```sh
docker compose down
```

## Local Docker Smoke Test

For local testing on `http://localhost`, set these values in `.env`:

```env
SITE_DOMAIN=http://localhost
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

Then run:

```sh
docker compose up --build
```
