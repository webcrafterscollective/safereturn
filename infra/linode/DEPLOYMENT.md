<!-- Linode deployment guide for Docker Compose + Caddy + FastAPI fullstack template. -->
# Linode Deployment (Ubuntu LTS)

## 1) Create VM and SSH access

```bash
# On local machine
ssh-keygen -t ed25519 -C "deploy-key"
```

- Create Linode Compute instance (Ubuntu 24.04 LTS recommended).
- Add your public SSH key during provisioning.

## 2) DNS setup

Create DNS A record:
- `app.example.com -> <linode-public-ip>`

## 3) Firewall rules

Allow:
- `22/tcp` (SSH)
- `80/tcp` (HTTP)
- `443/tcp` (HTTPS)

Deny:
- All other inbound traffic.
- Do not expose PostgreSQL (`5432`) publicly.

## 4) Install Docker

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

Log out/in once after adding user to docker group.

## 5) Prepare app directory

```bash
sudo mkdir -p /srv/fastapi-fullstack-prod
sudo chown -R $USER:$USER /srv/fastapi-fullstack-prod
cd /srv/fastapi-fullstack-prod
```

Copy files into this directory:
- `docker-compose.prod.yml`
- `infra/caddy/Caddyfile`

## 6) Set server secrets and env

Create `.env` in `/srv/fastapi-fullstack-prod`:

```bash
cat > .env <<'EOF'
APP_NAME=fastapi-fullstack-prod
ENVIRONMENT=prod
LOG_LEVEL=INFO
JWT_SECRET=<long-random-value>
SECRET_KEY=<long-random-value>
ACCESS_TOKEN_TTL_MINUTES=15
REFRESH_TOKEN_TTL_DAYS=7
POSTGRES_DB=app_db
POSTGRES_USER=app_user
POSTGRES_PASSWORD=<strong-password>
DATABASE_URL=postgresql+asyncpg://app_user:<strong-password>@postgres:5432/app_db
CORS_ALLOWED_ORIGINS=https://app.example.com
TRUSTED_HOSTS=app.example.com
PROMETHEUS_ENABLED=true
FRONTEND_DIST_PATH=/app/web_dist
DOMAIN=app.example.com
API_IMAGE=ghcr.io/<org>/<repo>/api:latest
EOF
chmod 600 .env
```

## 7) Login to GHCR

```bash
echo "<ghcr-token>" | docker login ghcr.io -u <github-username> --password-stdin
```

## 8) Deploy

```bash
cd /srv/fastapi-fullstack-prod
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

## 9) Run Alembic migrations

```bash
docker compose -f docker-compose.prod.yml run --rm api alembic -c apps/api/alembic.ini upgrade head
```

## 10) Verify health

```bash
curl -fsS https://app.example.com/health/live
curl -fsS https://app.example.com/health/ready
curl -fsS https://app.example.com/doc > /dev/null
```

## Deploy from CI

CD workflow connects over SSH and runs the same commands using:
- `LINODE_HOST`
- `LINODE_USER`
- `LINODE_SSH_KEY`
- `PROD_ENV_VARS`
- `GHCR_TOKEN`

## Rollback

```bash
cd /srv/fastapi-fullstack-prod
export API_IMAGE=ghcr.io/<org>/<repo>/api:<previous-tag>
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

Then validate:

```bash
curl -fsS https://app.example.com/health/ready
```

## Postgres backup

Use script `infra/scripts/backup_postgres.sh` and schedule nightly cron:

```bash
chmod +x infra/scripts/backup_postgres.sh
crontab -e
# 2 AM daily
0 2 * * * /srv/fastapi-fullstack-prod/infra/scripts/backup_postgres.sh >> /var/log/pg_backup.log 2>&1
```

Optional: upload backups to Linode Object Storage using `rclone` or `aws s3 cp` compatible endpoint.
