#!/usr/bin/env bash

# Production Deployment Script for dkdc
# Designed for DigitalOcean VPS deployment

set -euo pipefail

# Configuration
REPO_URL="https://github.com/lostmygithubaccount/dkdc.git"
DEPLOY_USER="dkdc"
DEPLOY_DIR="/opt/dkdc"
DOMAINS="dkdc.dev dkdc.io dkdc.ai app.dkdc.io"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

function warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

function error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

function check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root"
        exit 1
    fi
}

function install_dependencies() {
    log "Installing system dependencies..."
    
    apt update
    apt install -y \
        curl \
        git \
        docker.io \
        docker-compose \
        ufw \
        fail2ban \
        htop \
        tree \
        unzip
    
    # Install Docker Compose v2 if not available
    if ! command -v docker compose &> /dev/null; then
        log "Installing Docker Compose v2..."
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    fi
    
    # Start Docker service
    systemctl enable docker
    systemctl start docker
    
    log "Dependencies installed successfully!"
}

function setup_user() {
    log "Setting up deployment user..."
    
    # Create user if doesn't exist
    if ! id "$DEPLOY_USER" &>/dev/null; then
        useradd -m -s /bin/bash -G docker "$DEPLOY_USER"
        log "Created user: $DEPLOY_USER"
    else
        log "User $DEPLOY_USER already exists"
        usermod -a -G docker "$DEPLOY_USER"
    fi
    
    # Setup directory
    mkdir -p "$DEPLOY_DIR"
    chown "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_DIR"
}

function configure_firewall() {
    log "Configuring firewall..."
    
    # Reset UFW to defaults
    ufw --force reset
    
    # Default policies
    ufw default deny incoming
    ufw default allow outgoing
    
    # SSH access
    ufw allow ssh
    
    # HTTP/HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Enable firewall
    ufw --force enable
    
    log "Firewall configured successfully!"
}

function configure_fail2ban() {
    log "Configuring fail2ban..."
    
    # Create jail configuration for nginx
    cat > /etc/fail2ban/jail.d/nginx.conf << 'EOF'
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10

[nginx-botsearch]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2
EOF

    systemctl enable fail2ban
    systemctl restart fail2ban
    
    log "Fail2ban configured successfully!"
}

function setup_ssl_directories() {
    log "Setting up SSL directories..."
    
    # Create Let's Encrypt directories
    mkdir -p /etc/letsencrypt
    mkdir -p /var/lib/letsencrypt
    mkdir -p "$DEPLOY_DIR/nginx/certbot-webroot"
    
    chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_DIR"
}

function clone_repository() {
    log "Cloning repository..."
    
    if [ -d "$DEPLOY_DIR/.git" ]; then
        log "Repository already exists, updating..."
        sudo -u "$DEPLOY_USER" bash << 'EOF'
cd /opt/dkdc
git pull origin main
EOF
        log "Repository updated"
    else
        log "Cloning fresh repository..."
        rm -rf "$DEPLOY_DIR"
        
        # Clone as root, then fix ownership
        git clone "$REPO_URL" "$DEPLOY_DIR"
        chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_DIR"
        log "Repository cloned"
    fi
}

function setup_environment() {
    log "Setting up environment..."
    
    sudo -u "$DEPLOY_USER" bash << 'EOF'
cd /opt/dkdc

# Make scripts executable
chmod +x bin/*.sh

# Create logs directory
mkdir -p logs
EOF
}

function configure_docker_logging() {
    log "Configuring Docker logging..."
    
    # Configure Docker daemon for log rotation
    cat > /etc/docker/daemon.json << 'EOF'
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    }
}
EOF

    systemctl restart docker
}

function setup_monitoring() {
    log "Setting up basic monitoring..."
    
    # Create a simple health check script
    cat > "$DEPLOY_DIR/bin/health-check.sh" << 'EOF'
#!/usr/bin/env bash

# Simple health check for dkdc services
cd $(dirname $0)/..

echo "=== DKDC Health Check ===" 
echo "Timestamp: $(date)"
echo

echo "=== Docker Status ==="
docker compose ps

echo
echo "=== Service Health ==="
for service in nginx dkdc-dev dkdc-io app1; do
    if docker compose exec $service curl -f http://localhost:80 >/dev/null 2>&1; then
        echo "$service: HEALTHY"
    else
        echo "$service: UNHEALTHY"
    fi
done

echo
echo "=== Disk Usage ==="
df -h /

echo
echo "=== Memory Usage ==="
free -h

echo
echo "=== Load Average ==="
uptime
EOF

    chmod +x "$DEPLOY_DIR/bin/health-check.sh"
    chown "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_DIR/bin/health-check.sh"
    
    # Setup cron for health checks
    sudo -u "$DEPLOY_USER" bash << 'EOF'
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/dkdc/bin/health-check.sh >> /opt/dkdc/logs/health-check.log 2>&1") | crontab -
EOF

    log "Health monitoring setup completed!"
}

function deploy_services() {
    log "Deploying services..."
    
    sudo -u "$DEPLOY_USER" bash << 'EOF'
cd /opt/dkdc

# Build and start services in production mode
DKDC_ENV=prod ./bin/up.sh

# Wait for services to be ready
sleep 10

# Check service status
docker compose ps
EOF
}

function setup_ssl() {
    log "Setting up SSL certificates..."
    
    sudo -u "$DEPLOY_USER" bash << 'EOF'
cd /opt/dkdc
./bin/ssl-setup.sh setup
EOF
}

function print_success() {
    log "🎉 Deployment completed successfully!"
    echo
    echo -e "${BLUE}=== Deployment Summary ===${NC}"
    echo -e "Deploy directory: ${GREEN}$DEPLOY_DIR${NC}"
    echo -e "Deploy user: ${GREEN}$DEPLOY_USER${NC}"
    echo -e "Domains: ${GREEN}$DOMAINS${NC}"
    echo
    echo -e "${BLUE}=== Next Steps ===${NC}"
    echo -e "1. Point your domains to this server's IP address"
    echo -e "2. Run SSL setup: ${YELLOW}sudo -u $DEPLOY_USER $DEPLOY_DIR/bin/ssl-setup.sh${NC}"
    echo -e "3. Check service status: ${YELLOW}sudo -u $DEPLOY_USER docker compose -f $DEPLOY_DIR/docker-compose.yaml ps${NC}"
    echo -e "4. View logs: ${YELLOW}sudo -u $DEPLOY_USER docker compose -f $DEPLOY_DIR/docker-compose.yaml logs${NC}"
    echo
    echo -e "${GREEN}Your dkdc deployment is ready!${NC}"
}

function main() {
    log "Starting dkdc production deployment..."
    
    check_root
    install_dependencies
    setup_user
    configure_firewall
    configure_fail2ban
    setup_ssl_directories
    clone_repository
    setup_environment
    configure_docker_logging
    setup_monitoring
    deploy_services
    
    print_success
}

# Script entry point
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "update")
        clone_repository
        deploy_services
        ;;
    "ssl")
        setup_ssl
        ;;
    "health")
        sudo -u "$DEPLOY_USER" /opt/dkdc/bin/health-check.sh
        ;;
    *)
        echo "Usage: $0 [deploy|update|ssl|health]"
        echo "  deploy - Full production deployment (default)"
        echo "  update - Update code and restart services"
        echo "  ssl    - Setup SSL certificates"
        echo "  health - Run health check"
        exit 1
        ;;
esac