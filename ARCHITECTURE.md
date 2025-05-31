# dkdc Architecture

## Overview

dkdc is a monorepo with nginx reverse proxy routing three domains to containerized services. Container-first approach for dev/prod parity and simple deployment.

## Request Flow

```
Internet → nginx:80/443 → {
  dkdc.dev     → dkdc-dev:1313   (Zola site)
  dkdc.io      → dkdc-io:1314    (Zola site)  
  app.dkdc.io  → app1:3007       (Panel app)
}
```

## Core Services

- **nginx**: Reverse proxy, SSL termination, security headers
- **dkdc-dev**: Zola static site generator (primary website)
- **dkdc-io**: Zola static site generator (secondary website)
- **app1**: Panel data visualization app (Python/Bokeh)
- **dkdc-dl-catalog**: PostgreSQL database
- **certbot**: Let's Encrypt SSL certificate management

## Environment Modes

### Development Mode (`./bin/up.sh`)
- Direct port exposure (1313, 1314, 3007)
- No nginx or SSL required
- Live reload for all services
- docker-compose.override.yaml created automatically

### Production Mode (`./bin/up.sh -e prod`)
- All traffic through nginx reverse proxy
- SSL/TLS termination with Let's Encrypt
- Rate limiting and security headers
- Health checks and auto-restart

## Container Details

**Base**: `ghcr.io/astral-sh/uv:debian-slim` with Python 3.13, Node.js 22, Zola
**User**: `dev` (UID 1000) with sudo access
**Caching**: Persistent volumes for uv/npm caches
**Networking**: Isolated `dkdc-network` bridge

## Security Features

- UFW firewall (SSH, HTTP, HTTPS only)
- Fail2ban protection against brute force
- Modern TLS ciphers and HSTS headers
- nginx rate limiting and security headers
- Automatic SSL certificate renewal

## Deployment Flow

### VPS Setup
1. `curl -sSL <repo>/bin/deploy.sh | bash` - Full server setup
2. Point domains to server IP 
3. `./bin/ssl-setup.sh` - Generate SSL certificates
4. Services auto-start with health monitoring

### Key Scripts
- **bin/up.sh**: Development/production startup
- **bin/deploy.sh**: Full VPS deployment with security hardening
- **bin/ssl-setup.sh**: SSL certificate management + auto-renewal
- **bin/health-check.sh**: Service monitoring (auto-generated)

## Design Philosophy

**Dev = Prod**: Same containers, different routing
**Speed**: Cached dependencies, fast startup
**Simple**: One command deployment, minimal config  
**Secure**: Firewall, SSL, rate limiting, auto-updates