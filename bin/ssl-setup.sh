#!/usr/bin/env bash

# SSL Certificate Setup Script for dkdc
# This script sets up Let's Encrypt SSL certificates for all domains

set -euo pipefail

DOMAINS="dkdc.dev dkdc.io dkdc.ai app.dkdc.io"
EMAIL="cody@dkdc.dev"

function log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

function check_nginx_config() {
    log "Checking nginx configuration..."
    docker compose exec nginx nginx -t
}

function reload_nginx() {
    log "Reloading nginx..."
    docker compose exec nginx nginx -s reload
}

function setup_initial_certs() {
    log "Setting up initial SSL certificates..."
    
    # Create temporary nginx config without SSL for initial setup
    cp nginx/conf.d/default.conf nginx/conf.d/default.conf.bak
    
    # Create a minimal config for HTTP only during cert generation
    cat > nginx/conf.d/temp.conf << 'EOF'
server {
    listen 80;
    server_name dkdc.dev dkdc.io app.dkdc.io;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$host$request_uri;
    }
}
EOF

    # Remove SSL config temporarily
    mv nginx/conf.d/default.conf nginx/conf.d/default.conf.ssl
    
    # Reload nginx with HTTP-only config
    reload_nginx
    
    # Run certbot
    log "Running certbot for domains: $DOMAINS"
    docker compose run --rm certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        --force-renewal \
        $(echo $DOMAINS | sed 's/\([^ ]*\)/-d \1/g')
    
    # Restore SSL config
    mv nginx/conf.d/default.conf.ssl nginx/conf.d/default.conf
    rm nginx/conf.d/temp.conf
    
    # Reload nginx with SSL config
    reload_nginx
    
    log "SSL certificates setup completed!"
}

function renew_certs() {
    log "Renewing SSL certificates..."
    docker compose run --rm certbot renew
    reload_nginx
    log "SSL certificates renewed!"
}

function setup_cron() {
    log "Setting up automatic renewal cron job..."
    
    # Create renewal script
    cat > bin/ssl-renew.sh << 'EOF'
#!/usr/bin/env bash
cd $(dirname $0)/..
./bin/ssl-setup.sh renew >> /var/log/ssl-renewal.log 2>&1
EOF
    
    chmod +x bin/ssl-renew.sh
    
    # Add to crontab (runs twice daily)
    (crontab -l 2>/dev/null; echo "0 12 * * * $(pwd)/bin/ssl-renew.sh") | crontab -
    
    log "Cron job setup completed!"
}

case "${1:-setup}" in
    "setup")
        setup_initial_certs
        setup_cron
        ;;
    "renew")
        renew_certs
        ;;
    "cron")
        setup_cron
        ;;
    *)
        echo "Usage: $0 [setup|renew|cron]"
        echo "  setup - Initial SSL certificate setup (default)"
        echo "  renew - Renew existing certificates"
        echo "  cron  - Setup automatic renewal cron job"
        exit 1
        ;;
esac

log "SSL setup completed successfully!"