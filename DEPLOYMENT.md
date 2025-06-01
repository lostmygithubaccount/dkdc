# dkdc Deployment Guide

Simple, streamlined deployment for dkdc websites and applications.

## Quick Deploy

### First Time Setup

```bash
# On your VPS (as root)
curl -sSL https://raw.githubusercontent.com/lostmygithubaccount/dkdc/main/bin/deploy.sh | bash
```

This automatically:
- Installs Docker and dependencies
- Sets up firewall and security
- Clones the repository
- Starts all services
- Configures SSL certificates

### Update Deployment

From your local machine:

```bash
# Push changes to GitHub first
git push origin main

# Then deploy
./bin/deploy-update.sh
```

Or manually on the server:

```bash
ssh root@your-server
cd /opt/dkdc
./bin/update.sh
```

## Architecture

### Services

| Service | URL | Description |
|---------|-----|-------------|
| nginx | - | Reverse proxy & static file server |
| dkdc.dev | https://dkdc.dev | Primary website (Zola static site) |
| dkdc.io | https://dkdc.io | Secondary website (Zola static site) |
| app.dkdc.io | https://app.dkdc.io | Panel data visualization app |
| postgres | localhost:5432 | DuckDB catalog database |

### How It Works

1. **Development**: Zola sites run in development mode with hot reload
2. **Production**: Static sites are built and served directly by nginx
3. **Updates**: Pull from git, rebuild static sites, reload nginx

## Common Tasks

### Update Website Content

1. Edit content in `websites/dkdc.dev/content/` or `websites/dkdc.io/content/`
2. Commit and push to GitHub
3. Run `./bin/deploy-update.sh`

### Add a New Blog Post

```bash
# For dkdc.dev
cd websites/dkdc.dev/content/posts
create new-post.md

# For dkdc.io  
cd websites/dkdc.io/content/posts
create new-post.md
```

### View Logs

```bash
# All services
ssh root@your-server "cd /opt/dkdc && docker compose logs -f"

# Specific service
ssh root@your-server "cd /opt/dkdc && docker compose logs -f nginx"
```

### Restart Services

```bash
# All services
ssh root@your-server "cd /opt/dkdc && docker compose restart"

# Just rebuild static sites
ssh root@your-server "cd /opt/dkdc && ./bin/build-static.sh"
```

### SSL Certificate Renewal

Certificates auto-renew via cron. To manually renew:

```bash
ssh root@your-server "cd /opt/dkdc && ./bin/ssl-setup.sh renew"
```

## Troubleshooting

### Site Not Updating?

1. Check if changes are pushed to GitHub
2. Verify build succeeded: `./bin/build-static.sh`
3. Check nginx logs: `docker compose logs nginx`

### SSL Issues?

```bash
# Check certificate status
ssh root@your-server "certbot certificates"

# Restart nginx
ssh root@your-server "cd /opt/dkdc && docker compose restart nginx"
```

### General Health Check

```bash
ssh root@your-server "cd /opt/dkdc && ./bin/health-check.sh"
```

## Quick Reference

```bash
# Deploy updates
./bin/deploy-update.sh

# View live logs
ssh root@$VPS_IP "cd /opt/dkdc && docker compose logs -f"

# Rebuild static sites
ssh root@$VPS_IP "cd /opt/dkdc && ./bin/build-static.sh"

# Check status
ssh root@$VPS_IP "cd /opt/dkdc && docker compose ps"
```