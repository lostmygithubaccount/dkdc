#!/usr/bin/env bash

# Production Deployment Script for dkdc
# Designed for DigitalOcean VPS deployment

set -euo pipefail

# Display banner
cat << 'EOF'
██████╗ ██╗  ██╗██████╗  ██████╗
██╔══██╗██║ ██╔╝██╔══██╗██╔════╝
██║  ██║█████╔╝ ██║  ██║██║     
██║  ██║██╔═██╗ ██║  ██║██║     
██████╔╝██║  ██╗██████╔╝╚██████╗
╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝

Production Deployment Script v2.0
EOF
echo

# Trap to cleanup on script failure
trap 'cleanup_on_error $LINENO $BASH_COMMAND' ERR

function cleanup_on_error() {
    local line_no=$1
    local command="$2"
    error "Script failed at line $line_no: $command"
    
    # Attempt to stop any running services
    if [ -d "$DEPLOY_DIR" ] && [ -f "$DEPLOY_DIR/docker-compose.yaml" ]; then
        warn "Attempting to stop any running services..."
        cd "$DEPLOY_DIR" && docker compose down || true
    fi
    
    error "Deployment failed. Check logs above for details."
    exit 1
}

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
    
    # Update package lists with retry
    local retry_count=0
    while ! apt update && [ $retry_count -lt 3 ]; do
        warn "Package update failed, retrying in 5 seconds..."
        sleep 5
        retry_count=$((retry_count + 1))
    done
    
    # Install basic packages first
    DEBIAN_FRONTEND=noninteractive apt install -y \
        curl \
        git \
        ca-certificates \
        gnupg \
        lsb-release \
        ufw \
        fail2ban \
        htop \
        tree \
        unzip || {
        error "Failed to install basic packages"
        exit 1
    }
    
    # Always ensure proper Docker installation with compose support
    log "Setting up Docker with Compose support..."
    
    # Remove old Docker packages if they exist
    apt remove -y docker docker-engine docker.io containerd runc || true
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Update package list and install Docker
    apt update
    DEBIAN_FRONTEND=noninteractive apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Install Docker Compose v2 if not available (fallback)
    if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
        log "Installing Docker Compose v2..."
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    fi
    
    # Start Docker service with error checking
    if ! systemctl is-enabled docker &>/dev/null; then
        systemctl enable docker
    fi
    
    if ! systemctl is-active docker &>/dev/null; then
        systemctl start docker
        sleep 5  # Wait for Docker to fully start
    fi
    
    # Verify Docker is working
    if ! docker info &>/dev/null; then
        error "Docker installation failed or service not running"
        exit 1
    fi
    
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
    
    # Only reset if UFW is not already configured properly
    if ! ufw status | grep -q "Status: active"; then
        ufw --force reset
    fi
    
    # Default policies (idempotent)
    ufw default deny incoming
    ufw default allow outgoing
    
    # SSH access (check if already allowed)
    if ! ufw status | grep -q "22/tcp"; then
        ufw allow ssh
    fi
    
    # HTTP/HTTPS (check if already allowed)
    if ! ufw status | grep -q "80/tcp"; then
        ufw allow 80/tcp
    fi
    if ! ufw status | grep -q "443/tcp"; then
        ufw allow 443/tcp
    fi
    
    # Enable firewall only if not already active
    if ! ufw status | grep -q "Status: active"; then
        ufw --force enable
    fi
    
    log "Firewall configured successfully!"
}

function configure_fail2ban() {
    log "Configuring fail2ban..."
    
    # Create jail configuration for nginx (only if not exists or different)
    if [ ! -f /etc/fail2ban/jail.d/nginx.conf ] || ! grep -q "nginx-http-auth" /etc/fail2ban/jail.d/nginx.conf; then
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
    fi

    # Enable and start fail2ban if not already running
    if ! systemctl is-enabled fail2ban &>/dev/null; then
        systemctl enable fail2ban
    fi
    
    if ! systemctl is-active fail2ban &>/dev/null; then
        systemctl start fail2ban
    else
        systemctl reload fail2ban
    fi
    
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
        # Ensure ownership is correct first
        chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_DIR"
        
        sudo -u "$DEPLOY_USER" bash << 'EOF'
set -e
cd /opt/dkdc

# Reset any local changes that might block pull
git reset --hard HEAD
git clean -fd

# Pull latest changes with retry
retry_count=0
while ! git pull origin main && [ $retry_count -lt 3 ]; do
    echo "Git pull failed, retrying in 5 seconds..."
    sleep 5
    retry_count=$((retry_count + 1))
done

if [ $retry_count -eq 3 ]; then
    echo "Error: Failed to pull repository after 3 attempts"
    exit 1
fi
EOF
        log "Repository updated"
    else
        log "Cloning fresh repository..."
        
        # Clean up any existing directory
        if [ -d "$DEPLOY_DIR" ]; then
            rm -rf "$DEPLOY_DIR"
        fi
        
        # Clone with retry mechanism
        local retry_count=0
        while ! git clone "$REPO_URL" "$DEPLOY_DIR" && [ $retry_count -lt 3 ]; do
            warn "Git clone failed, retrying in 5 seconds..."
            rm -rf "$DEPLOY_DIR"
            sleep 5
            retry_count=$((retry_count + 1))
        done
        
        if [ $retry_count -eq 3 ]; then
            error "Failed to clone repository after 3 attempts"
            exit 1
        fi
        
        # Fix ownership
        chown -R "$DEPLOY_USER:$DEPLOY_USER" "$DEPLOY_DIR"
        log "Repository cloned"
    fi
}

function setup_environment() {
    log "Setting up environment..."
    
    sudo -u "$DEPLOY_USER" bash << 'EOF'
set -e
cd /opt/dkdc

# Make scripts executable
if [ -d "bin" ]; then
    chmod +x bin/*.sh
else
    echo "Warning: bin directory not found"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Verify critical files exist
for file in "docker-compose.yaml" "bin/up.sh" "bin/ssl-setup.sh"; do
    if [ ! -f "$file" ]; then
        echo "Error: Required file $file not found"
        exit 1
    fi
done

echo "Environment setup completed"
EOF
}

function configure_docker_logging() {
    log "Configuring Docker logging..."
    
    # Only configure if not already set or different
    if [ ! -f /etc/docker/daemon.json ] || ! grep -q "log-driver" /etc/docker/daemon.json; then
        # Backup existing daemon.json if it exists
        if [ -f /etc/docker/daemon.json ]; then
            cp /etc/docker/daemon.json /etc/docker/daemon.json.backup
        fi
        
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

        # Restart Docker only if config changed
        log "Restarting Docker with new logging configuration..."
        systemctl restart docker
        
        # Wait for Docker to restart
        sleep 10
        
        # Verify Docker is running
        if ! systemctl is-active docker &>/dev/null; then
            error "Docker failed to restart after configuration change"
            exit 1
        fi
    else
        log "Docker logging already configured"
    fi
}

function setup_monitoring() {
    log "Setting up basic monitoring..."
    
    # Ensure bin directory exists
    mkdir -p "$DEPLOY_DIR/bin"
    
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
    
    # Setup cron for health checks (only if not already exists)
    sudo -u "$DEPLOY_USER" bash << 'EOF'
if ! crontab -l 2>/dev/null | grep -q "health-check.sh"; then
    (crontab -l 2>/dev/null; echo "*/5 * * * * /opt/dkdc/bin/health-check.sh >> /opt/dkdc/logs/health-check.log 2>&1") | crontab -
    echo "Health check cron job added"
else
    echo "Health check cron job already exists"
fi
EOF

    log "Health monitoring setup completed!"
}

function deploy_services() {
    log "Deploying services..."
    
    sudo -u "$DEPLOY_USER" bash << 'EOF'
set -e
cd /opt/dkdc

# Stop any existing services first (idempotent)
if docker compose ps | grep -q Up; then
    echo "Stopping existing services..."
    docker compose down || true
fi

# Clean up any orphaned containers
docker system prune -f --volumes || true

# Build and start services in production mode
echo "Starting services in production mode..."
DKDC_ENV=prod ./bin/up.sh

# Wait for services to be ready with timeout
echo "Waiting for services to start..."
local timeout=60
local count=0
while [ $count -lt $timeout ]; do
    if docker compose ps | grep -q "Up"; then
        echo "Services are starting up..."
        break
    fi
    sleep 2
    count=$((count + 2))
done

# Additional wait for services to stabilize
sleep 15

# Check service status
echo "Service status:"
docker compose ps

# Verify key services are running
if ! docker compose ps | grep -q "dkdc-dev.*Up"; then
    echo "Warning: dkdc-dev service may not be running properly"
fi
if ! docker compose ps | grep -q "nginx.*Up"; then
    echo "Warning: nginx service may not be running properly"
fi
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

function verify_system_requirements() {
    log "Verifying system requirements..."
    
    # Check if we're on Ubuntu/Debian
    if ! command -v apt &> /dev/null; then
        error "This script requires a Debian/Ubuntu system with apt package manager"
        exit 1
    fi
    
    # Check available disk space (require at least 5GB)
    local available_space=$(df / | awk 'NR==2 {print $4}')
    if [ "$available_space" -lt 5242880 ]; then  # 5GB in KB
        warn "Low disk space detected. At least 5GB recommended."
    fi
    
    # Check memory (warn if less than 2GB)
    local available_mem=$(free -k | awk 'NR==2{print $2}')
    if [ "$available_mem" -lt 2097152 ]; then  # 2GB in KB
        warn "Low memory detected. At least 2GB RAM recommended."
    fi
    
    log "System requirements verified"
}

function main() {
    log "Starting dkdc production deployment..."
    
    check_root
    verify_system_requirements
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