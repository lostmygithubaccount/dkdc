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
    
    # Make sure certbot webroot directory exists
    mkdir -p nginx/certbot-webroot
    
    # Check if nginx is running with current config
    if ! docker compose ps nginx | grep -q "Up"; then
        log "Nginx not running, starting services..."
        docker compose up -d nginx
        sleep 5
    fi
    
    # Run certbot for each domain separately to handle failures better
    for domain in $DOMAINS; do
        if [ "$domain" = "dkdc.ai" ]; then
            log "Skipping dkdc.ai (alias domain)"
            continue
        fi
        
        log "Requesting certificate for $domain..."
        docker compose run --rm certbot certonly \
            --webroot \
            --webroot-path=/var/www/certbot \
            --email $EMAIL \
            --agree-tos \
            --no-eff-email \
            --non-interactive \
            -d $domain || {
            log "Failed to get certificate for $domain, continuing..."
        }
    done
    
    # Check if any certificates were obtained
    if docker compose exec nginx ls /etc/letsencrypt/live/ 2>/dev/null | grep -q "dkdc"; then
        log "Certificates obtained, activating SSL configuration..."
        
        # Copy SSL template to active config if it exists
        if [ -f nginx/conf.d/ssl.conf.template ]; then
            cp nginx/conf.d/ssl.conf.template nginx/conf.d/ssl.conf
            log "SSL configuration activated"
        fi
        
        # Reload nginx
        reload_nginx
    else
        log "Warning: No certificates were obtained. Sites will run on HTTP only."
    fi
    
    log "SSL setup process completed!"
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