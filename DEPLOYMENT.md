# dkdc Deployment Guide

This guide covers deploying dkdc to a VPS (specifically DigitalOcean) with proper nginx routing and SSL certificates.

## Quick Start

### On a Fresh DigitalOcean VPS

1. **Initial Server Setup**
   ```bash
   # Run as root on the server
   curl -sSL https://raw.githubusercontent.com/lostmygithubaccount/dkdc/main/bin/deploy.sh | bash
   ```

2. **Point Your Domains**
   
   In your DNS provider (DigitalOcean, Cloudflare, etc.), create these A records:
   ```
   Type: A    Name: @           Value: YOUR_VPS_IP    TTL: 300
   Type: A    Name: app         Value: YOUR_VPS_IP    TTL: 300
   ```
   
   For `dkdc.io` domain, create:
   ```
   Type: A    Name: @           Value: YOUR_VPS_IP    TTL: 300
   ```
   
   **Important**: 
   - Only use IP addresses, no ports needed
   - nginx handles routing internally on ports 80/443
   - DNS propagation takes 5-60 minutes

3. **Setup SSL Certificates**
   ```bash
   sudo -u dkdc /opt/dkdc/bin/ssl-setup.sh
   ```

## Manual Deployment

### Prerequisites

- Ubuntu 20.04+ server
- Root access
- Domains pointed to server IP

### Step-by-Step

1. **Clone Repository**
   ```bash
   git clone https://github.com/lostmygithubaccount/dkdc.git
   cd dkdc
   ```

2. **Run Deployment Script**
   ```bash
   sudo ./bin/deploy.sh
   ```

3. **Setup SSL**
   ```bash
   sudo -u dkdc /opt/dkdc/bin/ssl-setup.sh
   ```

## Development vs Production

### Development Mode (Default)
```bash
./bin/up.sh
```
- Services accessible on direct ports:
  - dkdc.dev: http://localhost:1313
  - dkdc.io: http://localhost:1314
  - app.dkdc.io: http://localhost:3007
- No nginx or SSL setup required

### Production Mode
```bash
./bin/up.sh -e prod
```
- All traffic routed through nginx
- SSL/TLS termination
- Automatic HTTP → HTTPS redirects
- Rate limiting and security headers

## Architecture Overview

```
Internet
    ↓
Nginx (Port 80/443)
    ├── dkdc.dev → dkdc-dev:1313
    ├── dkdc.io → dkdc-io:1314
    └── app.dkdc.io → app1:3007
```

### Container Services

| Service | Purpose | Port | URL |
|---------|---------|------|-----|
| nginx | Reverse proxy & SSL | 80, 443 | All domains |
| dkdc-dev | Zola static site | 1313 | dkdc.dev |
| dkdc-io | Zola static site | 1314 | dkdc.io |
| app1 | Panel application | 3007 | app.dkdc.io |
| dkdc-dl-catalog | PostgreSQL database | 5432 | Internal |
| certbot | SSL certificate management | - | - |

## SSL Certificate Management

### Initial Setup
```bash
./bin/ssl-setup.sh setup
```

### Manual Renewal
```bash
./bin/ssl-setup.sh renew
```

### Automatic Renewal
Automatic renewal is configured via cron job during initial setup.

## Monitoring & Maintenance

### Health Check
```bash
./bin/deploy.sh health
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f nginx
docker compose logs -f dkdc-dev
```

### Service Management
```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart nginx

# Stop all services
docker compose down

# Update and redeploy
./bin/deploy.sh update
```

## Security Features

- **Firewall**: UFW configured to allow only SSH, HTTP, and HTTPS
- **Fail2ban**: Protection against brute force attacks
- **SSL/TLS**: Modern cipher suites and HSTS headers
- **Rate Limiting**: nginx rate limiting for API and static content
- **Security Headers**: X-Frame-Options, CSP, XSS protection

## Troubleshooting

### SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Test nginx configuration
docker compose exec nginx nginx -t

# Manual certificate generation
sudo certbot certonly --manual -d dkdc.dev -d dkdc.io -d app.dkdc.io
```

### Service Health Issues
```bash
# Check service status
docker compose ps

# Check individual service logs
docker compose logs nginx
docker compose logs dkdc-dev

# Restart unhealthy services
docker compose restart <service-name>
```

### DNS Issues
```bash
# Test domain resolution
nslookup dkdc.dev
dig dkdc.dev

# Test HTTP/HTTPS connectivity
curl -I http://dkdc.dev
curl -I https://dkdc.dev
```

## File Structure

```
/opt/dkdc/                    # Production deployment directory
├── bin/                      # Scripts
│   ├── deploy.sh            # Full deployment script
│   ├── up.sh                # Service startup script
│   ├── ssl-setup.sh         # SSL certificate management
│   └── health-check.sh      # Health monitoring
├── nginx/                   # Nginx configuration
│   ├── nginx.conf          # Main nginx config
│   ├── conf.d/             # Site configurations
│   └── certbot-webroot/    # Let's Encrypt webroot
├── websites/               # Static sites
├── apps/                   # Web applications
└── docker-compose.yaml    # Container orchestration
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DKDC_ENV | Environment (dev/prod) | dev |
| COMPOSE_PROFILES | Docker compose profiles | - |

## Support

For issues or questions:
- Check logs: `docker compose logs -f`
- Run health check: `./bin/deploy.sh health`
- Review this documentation
- Check nginx configuration: `docker compose exec nginx nginx -t`