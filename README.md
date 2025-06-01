# dkdc

***The monorepo for me.***

## Quick Start

### Local Development

```bash
# Start all services with hot reload
./bin/up.sh

# Services available at:
# - http://localhost:1313 (dkdc.dev)
# - http://localhost:1314 (dkdc.io)
# - http://localhost:3007 (app.dkdc.io)
```

### Production Deployment

```bash
# First time setup (on VPS as root)
curl -sSL https://raw.githubusercontent.com/lostmygithubaccount/dkdc/main/bin/deploy.sh | bash

# Deploy updates (from local machine)
./bin/deploy-update.sh
```

## What's Inside

- **dkdc.dev**: Primary website (Zola static site)
- **dkdc.io**: Secondary website (Zola static site) 
- **app.dkdc.io**: Panel data visualization app
- **PostgreSQL**: Data catalog for DuckDB

## Common Tasks

### Update Website Content

1. Edit files in `websites/*/content/`
2. Test locally: `./bin/up.sh`
3. Deploy: `git push && ./bin/deploy-update.sh`

### Add a Blog Post

```bash
# Create new post
echo "+++
title = 'My New Post'
date = $(date +%Y-%m-%d)
+++

# Content here" > websites/dkdc.dev/content/posts/my-new-post.md

# Deploy
git add . && git commit -m "Add new post" && git push
./bin/deploy-update.sh
```

### View Production Logs

```bash
ssh root@$VPS_IP "cd /opt/dkdc && docker compose logs -f"
```

## Production URLs

- https://dkdc.dev
- https://dkdc.io
- https://app.dkdc.io

## Key Scripts

| Script | Purpose |
|--------|---------|  
| `./bin/up.sh` | Start local development |
| `./bin/deploy-update.sh` | Deploy updates to production |
| `./bin/build-static.sh` | Build static sites (runs on server) |
| `./bin/ssl-setup.sh` | Manage SSL certificates |
| `./bin/health-check.sh` | Check service health |

