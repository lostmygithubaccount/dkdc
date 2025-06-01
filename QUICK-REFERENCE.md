# dkdc Quick Reference

## 🚀 Most Common Commands

```bash
# Deploy updates (after git push)
./bin/deploy-update.sh

# View live logs
./bin/dkdc logs

# Check status
./bin/dkdc status
```

## 📝 Add Content

### New Blog Post (dkdc.dev)

```bash
cd websites/dkdc.dev/content/posts
cat > my-post.md << 'EOF'
+++
title = "My New Post"
date = 2025-06-01
+++

Your content here...
EOF

git add . && git commit -m "Add new post" && git push
./bin/deploy-update.sh
```

### New Page

```bash
cd websites/dkdc.dev/content/pages
# Create your-page.md with content

git add . && git commit -m "Add new page" && git push  
./bin/deploy-update.sh
```

## 🛠️ Development

```bash
# Start local dev (with hot reload)
./bin/up.sh

# Visit:
# - http://localhost:1313 (dkdc.dev)
# - http://localhost:1314 (dkdc.io) 
# - http://localhost:3007 (app.dkdc.io)
```

## 🔧 Server Management

```bash
# SSH to server
ssh root@$VPS_IP

# On server - update manually
cd /opt/dkdc
./bin/update.sh

# View logs on server
docker compose logs -f

# Rebuild static sites only
./bin/build-static.sh
```

## 🔐 SSL Certificates

```bash
# Check certificate status
./bin/dkdc ssl status

# Renew certificates (auto-renews via cron)
./bin/dkdc ssl renew
```

## 📦 Backup

```bash
# Create and download backup
./bin/dkdc backup
```

## 🎯 Using the dkdc CLI

```bash
# First, set your VPS IP
export VPS_IP=your.server.ip

# Then use commands
./bin/dkdc deploy       # Deploy updates
./bin/dkdc logs         # View all logs
./bin/dkdc logs nginx   # View specific service
./bin/dkdc status       # Check health
./bin/dkdc restart      # Restart services
```

## 🚨 Troubleshooting

```bash
# Site not updating?
1. Check GitHub push succeeded
2. ./bin/dkdc logs nginx
3. ./bin/dkdc status

# SSL issues?
./bin/dkdc ssl status
./bin/dkdc restart

# General health check
./bin/dkdc status
```

## 📍 URLs

- Local: http://localhost:1313, :1314, :3007
- Prod: https://dkdc.dev, https://dkdc.io, https://app.dkdc.io