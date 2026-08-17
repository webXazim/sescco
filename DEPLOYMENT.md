Below is the complete sequence for a fresh Ubuntu VPS, using:

- Staging domain: `sescco.a2tdev.com`
- Deployment user: `deploy`
- Project directory: `/opt/sites/sescco`
- Internal application port: `8081`
- Host-level Nginx for multiple websites
- Docker Compose for Django, PostgreSQL, and internal Caddy

Replace these placeholders before running commands:

```text
VPS_IP
YOUR_REPOSITORY_URL
YOUR_REAL_EMAIL
YOUR_PUBLIC_SSH_KEY
```

## 1. Cloudflare DNS

Create or update:

```text
Type: A
Name: sescco
Content: VPS_IP
Proxy status: DNS only (gray cloud temporarily)
TTL: Auto
```

Keep it DNS-only until HTTPS is installed.

## 2. Connect as root

From your computer:

```sh
ssh root@VPS_IP
```

Confirm the server IP:

```sh
curl -4 https://icanhazip.com
```

It must match the Cloudflare A record.

## 3. Update Ubuntu

```sh
apt update
DEBIAN_FRONTEND=noninteractive apt full-upgrade -y

apt install -y \
  git \
  curl \
  ca-certificates \
  nginx \
  certbot \
  python3-certbot-nginx \
  dnsutils \
  ufw \
  unattended-upgrades

timedatectl set-timezone Asia/Riyadh
systemctl enable --now unattended-upgrades
systemctl enable --now nginx
```

If Ubuntu reports that a reboot is required:

```sh
test -f /var/run/reboot-required && cat /var/run/reboot-required
```

Reboot if necessary:

```sh
reboot
```

Reconnect afterward:

```sh
ssh root@VPS_IP
```

## 4. Create the deployment user

```sh
adduser deploy
usermod -aG sudo deploy
```

Create its SSH directory:

```sh
install -d -m 700 -o deploy -g deploy /home/deploy/.ssh
nano /home/deploy/.ssh/authorized_keys
```

Paste your public SSH key into the file, save, and exit.

Set ownership and permissions:

```sh
chown deploy:deploy /home/deploy/.ssh/authorized_keys
chmod 600 /home/deploy/.ssh/authorized_keys
```

Verify:

```sh
id deploy
sudo -l -U deploy
```

## 5. Test the deploy user

Keep the root session open.

Open another terminal:

```sh
ssh deploy@VPS_IP
```

Test sudo:

```sh
sudo -v
sudo whoami
```

Expected:

```text
root
```

Continue using the `deploy` session.

## 6. Prepare the project directory

```sh
sudo mkdir -p /opt/sites
sudo chown deploy:deploy /opt/sites

cd /opt/sites
git clone YOUR_REPOSITORY_URL sescco
cd /opt/sites/sescco
```

Confirm the project:

```sh
ls -la
git status
```

You should see:

```text
docker-compose.yml
Dockerfile
manage.py
scripts/
```

## 7. Install Docker

Run the included Ubuntu bootstrap script:

```sh
cd /opt/sites/sescco
sudo sh scripts/bootstrap_droplet.sh
```

Verify Docker:

```sh
sudo docker --version
sudo docker compose version
sudo systemctl status docker --no-pager
```

Enable Docker and containerd during boot:

```sh
sudo systemctl enable docker
sudo systemctl enable containerd
```

## 8. Configure Docker log rotation

```sh
sudo mkdir -p /etc/docker
```

Create the daemon configuration:

```sh
sudo tee /etc/docker/daemon.json >/dev/null <<'EOF'
{
  "log-driver": "local"
}
EOF
```

Restart Docker:

```sh
sudo systemctl restart docker
sudo systemctl status docker --no-pager
```

## 9. Verify the firewall

The project bootstrap script should already allow SSH, HTTP, and HTTPS:

```sh
sudo ufw status verbose
```

Expected allowed ports:

```text
22/tcp
80/tcp
443/tcp
```

If necessary:

```sh
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

Do not allow these publicly:

```text
5432
8081
8441
```

Also ensure the IONOS firewall allows inbound `22`, `80`, and `443`.

## 10. Confirm staging DNS

```sh
dig +short sescco.a2tdev.com
```

While Cloudflare is DNS-only, it should return the VPS IP.

You can also check:

```sh
getent hosts sescco.a2tdev.com
```

## 11. Deploy the project

```sh
cd /opt/sites/sescco

sudo sh scripts/deploy.sh \
  --domain sescco.a2tdev.com \
  --email YOUR_REAL_EMAIL \
  --project sescco-stage \
  --behind-proxy \
  --http-port 8081 \
  --https-port 8441 \
  --seed
```

This will:

- Generate `.env`
- Generate secure Django and PostgreSQL passwords
- Build Docker images
- Start PostgreSQL
- Run Django migrations
- Collect static files
- Seed CMS and localization content
- Start Gunicorn and internal Caddy
- Run deployment checks and audits

## 12. Check the containers

```sh
cd /opt/sites/sescco
sudo docker compose ps
```

View logs:

```sh
sudo docker compose logs --tail=200 web
sudo docker compose logs --tail=200 db
sudo docker compose logs --tail=200 caddy
```

All containers should be running and healthy.

Confirm the internal port is loopback-only:

```sh
sudo ss -lntp | grep -E ':8081|:8441'
```

It should show `127.0.0.1`, not `0.0.0.0`.

## 13. Configure Nginx

Create the configuration:

```sh
sudo tee /etc/nginx/sites-available/sescco-stage >/dev/null <<'EOF'
server {
    listen 80;
    listen [::]:80;

    server_name sescco.a2tdev.com;

    client_max_body_size 16M;

    location / {
        proxy_pass http://127.0.0.1:8081;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 30s;
        proxy_send_timeout 90s;
        proxy_read_timeout 90s;
    }
}
EOF
```

Enable the site:

```sh
sudo ln -s /etc/nginx/sites-available/sescco-stage /etc/nginx/sites-enabled/sescco-stage
sudo rm -f /etc/nginx/sites-enabled/default
```

Validate and reload:

```sh
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl status nginx --no-pager
```

Test routing:

```sh
curl -I http://sescco.a2tdev.com
```

An HTTPS redirect is acceptable.

## 14. Obtain the HTTPS certificate

Keep Cloudflare set to DNS-only during this step:

```sh
sudo certbot --nginx \
  -d sescco.a2tdev.com \
  --redirect \
  --agree-tos \
  --email YOUR_REAL_EMAIL \
  --no-eff-email
```

Test certificate renewal:

```sh
sudo certbot renew --dry-run
sudo systemctl status certbot.timer --no-pager
```

## 15. Test HTTPS directly

```sh
curl -I https://sescco.a2tdev.com/
curl -fsS https://sescco.a2tdev.com/healthz/
```

Expected health response:

```json
{"status":"ok","service":"sescco","ready":true}
```

Additional checks:

```sh
curl -I https://sescco.a2tdev.com/admin/
curl -I https://sescco.a2tdev.com/services/
curl -I https://sescco.a2tdev.com/projects/
curl -I https://sescco.a2tdev.com/sitemap.xml
curl -I https://sescco.a2tdev.com/robots.txt
```

## 16. Enable the Cloudflare proxy

After HTTPS works directly:

1. Open Cloudflare DNS.
2. Change `sescco.a2tdev.com` to **Proxied**—orange cloud.
3. Open SSL/TLS → Overview.
4. Select **Full (strict)**.
5. Do not use Flexible mode.

Wait a few minutes and test again:

```sh
curl -I https://sescco.a2tdev.com/
curl -fsS https://sescco.a2tdev.com/healthz/
```

## 17. Create the Django administrator

```sh
cd /opt/sites/sescco
sudo docker compose exec web python manage.py createsuperuser
```

Then open:

```text
https://sescco.a2tdev.com/admin/
```

## 18. Configure production email

Edit the environment:

```sh
sudo nano /opt/sites/sescco/.env
```

Configure:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=YOUR_SMTP_HOST
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=YOUR_SMTP_USERNAME
EMAIL_HOST_PASSWORD=YOUR_SMTP_PASSWORD
DEFAULT_FROM_EMAIL=info@sescco.com
SERVER_EMAIL=info@sescco.com
```

Apply the changes without reseeding CMS content:

```sh
cd /opt/sites/sescco
sudo sh scripts/deploy.sh
```

## 19. Disable direct root SSH login

Only continue after confirming that `ssh deploy@VPS_IP` works.

Create the SSH hardening configuration:

```sh
sudo tee /etc/ssh/sshd_config.d/00-production-hardening.conf >/dev/null <<'EOF'
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
EOF
```

Validate:

```sh
sudo sshd -t
```

If it produces no errors:

```sh
sudo systemctl reload ssh
```

Open another terminal and verify:

```sh
ssh deploy@VPS_IP
sudo whoami
```

Only close the original root session after this succeeds.

## 20. Create the first backup

```sh
cd /opt/sites/sescco
sudo sh scripts/backup_postgres.sh
sudo ls -lh backups
```

Copy backups to another server or storage provider regularly.

## 21. Normal future deployment command

```sh
ssh deploy@VPS_IP
cd /opt/sites/sescco
git pull
sudo sh scripts/deploy.sh
```

Normal deployments preserve CMS content. Use `-s` or `--seed` only when the
full canonical site seed should be applied again.

Check after deploying:

```sh
sudo docker compose ps
sudo docker compose logs --tail=100 web caddy db
curl -fsS https://sescco.a2tdev.com/healthz/
```

## 22. Useful operational commands

```sh
cd /opt/sites/sescco

# Container status
sudo docker compose ps

# Follow logs
sudo docker compose logs -f web caddy db

# Restart the stack
sudo docker compose restart

# Django production check
sudo docker compose exec -T web python manage.py check --deploy

# Database migrations
sudo docker compose exec -T web python manage.py migrate --noinput

# Refresh static files
sudo docker compose exec -T web python manage.py collectstatic --noinput

# Stop while preserving data
sudo docker compose down

# Start again
sudo docker compose up -d --wait
```

Never run this in production:

```sh
docker compose down -v
```

The `-v` option would delete the project’s PostgreSQL, media, static, and certificate volumes.
