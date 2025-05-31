#!/usr/bin/env bash

# dkdc Container Startup Script
# Handles both development and production environments

set -euo pipefail

# Default environment
ENVIRONMENT="${DKDC_ENV:-dev}"

# Colors for output
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

function run_command() {
    local command="$1"
    log "Running: $command"
    eval "$command"
}

function show_help() {
    echo "Usage: $0 [OPTIONS] [SERVICES...]"
    echo
    echo "Options:"
    echo "  -e, --env ENV     Set environment (dev|prod) [default: dev]"
    echo "  -h, --help        Show this help message"
    echo "  --build           Force rebuild of containers"
    echo "  --pull            Pull latest images before starting"
    echo
    echo "Services:"
    echo "  If no services specified, all services will be started"
    echo "  Available services: nginx, dkdc-dev, dkdc-io, app1, dkdc-dl-catalog"
    echo
    echo "Examples:"
    echo "  $0                    # Start all services in dev mode"
    echo "  $0 -e prod            # Start all services in production mode"
    echo "  $0 --build dkdc-dev   # Rebuild and start dkdc-dev service"
    echo "  $0 -e prod nginx app1 # Start only nginx and app1 in production"
    echo
    echo "Environment Variables:"
    echo "  DKDC_ENV=prod         # Set production environment"
}

function check_environment() {
    case "$ENVIRONMENT" in
        "dev"|"development")
            ENVIRONMENT="dev"
            log "Starting in development mode"
            ;;
        "prod"|"production")
            ENVIRONMENT="prod"
            log "Starting in production mode"
            warn "Production mode requires proper SSL setup and domain configuration"
            ;;
        *)
            echo "Error: Invalid environment '$ENVIRONMENT'. Use 'dev' or 'prod'"
            exit 1
            ;;
    esac
}

function setup_dev_environment() {
    log "Setting up development environment..."
    
    # Ensure development ports are exposed
    export COMPOSE_PROFILES="development"
    
    # Check if we need to expose ports directly for development
    if [[ "$ENVIRONMENT" == "dev" ]] && [[ ! -f "docker-compose.override.yaml" ]]; then
        log "Creating development override for direct port access..."
        
        cat > docker-compose.override.yaml << 'EOF'
# Development overrides - direct port access
services:
  dkdc-dev:
    ports:
      - "1313:1313"
  dkdc-io:
    ports:
      - "1314:1314"
  app1:
    ports:
      - "3007:3007"
  
  # Disable nginx and certbot in development
  nginx:
    profiles: ["production"]
  certbot:
    profiles: ["production"]
EOF
        log "Development override created. Services will be accessible on direct ports."
    fi
}

function setup_prod_environment() {
    log "Setting up production environment..."
    
    # Ensure production profiles are active
    export COMPOSE_PROFILES="production"
    
    # Remove development overrides if they exist
    if [[ -f "docker-compose.override.yaml" ]]; then
        warn "Removing development overrides for production deployment"
        rm -f docker-compose.override.yaml
    fi
    
    # Check if SSL certificates exist
    if [[ ! -d "/etc/letsencrypt/live" ]] && [[ ! -d "./ssl" ]]; then
        warn "SSL certificates not found. Run './bin/ssl-setup.sh' after starting services."
    fi
}

function start_services() {
    local services=("$@")
    local build_flag=""
    local pull_flag=""
    
    # Handle build and pull flags
    if [[ "${BUILD:-false}" == "true" ]]; then
        build_flag="--build"
        log "Force rebuilding containers..."
    fi
    
    if [[ "${PULL:-false}" == "true" ]]; then
        pull_flag="--pull always"
        log "Pulling latest images..."
    fi
    
    # Start services
    if [[ ${#services[@]} -eq 0 ]]; then
        log "Starting all services..."
        run_command "docker compose up -d $build_flag $pull_flag"
    else
        log "Starting services: ${services[*]}"
        run_command "docker compose up -d $build_flag $pull_flag ${services[*]}"
    fi
    
    # Wait a moment for services to start
    sleep 5
    
    # Show status
    log "Service status:"
    docker compose ps
    
    # Show access information
    show_access_info
}

function show_access_info() {
    echo
    echo -e "${BLUE}=== Access Information ===${NC}"
    
    if [[ "$ENVIRONMENT" == "dev" ]]; then
        echo -e "Development URLs:"
        echo -e "  dkdc.dev:     ${GREEN}http://localhost:1313${NC}"
        echo -e "  dkdc.io:      ${GREEN}http://localhost:1314${NC}"
        echo -e "  app.dkdc.io:  ${GREEN}http://localhost:3007${NC}"
        echo -e "  postgres:     ${GREEN}localhost:5432${NC} (dkdc/dkdc)"
    else
        echo -e "Production URLs:"
        echo -e "  dkdc.dev:     ${GREEN}https://dkdc.dev${NC}"
        echo -e "  dkdc.io:      ${GREEN}https://dkdc.io${NC}"
        echo -e "  app.dkdc.io:  ${GREEN}https://app.dkdc.io${NC}"
    fi
    
    echo
    echo -e "${BLUE}=== Useful Commands ===${NC}"
    echo -e "  View logs:    ${YELLOW}docker compose logs -f${NC}"
    echo -e "  Stop all:     ${YELLOW}docker compose down${NC}"
    echo -e "  Restart:      ${YELLOW}docker compose restart${NC}"
    echo -e "  Shell access: ${YELLOW}docker compose exec <service> bash${NC}"
}

# Parse command line arguments
BUILD=false
PULL=false
SERVICES=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        --build)
            BUILD=true
            shift
            ;;
        --pull)
            PULL=true
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
        *)
            SERVICES+=("$1")
            shift
            ;;
    esac
done

# Main execution
log "Starting dkdc services..."

check_environment

case "$ENVIRONMENT" in
    "dev")
        setup_dev_environment
        ;;
    "prod")
        setup_prod_environment
        ;;
esac

start_services "${SERVICES[@]+"${SERVICES[@]}"}"

log "🚀 dkdc is running in $ENVIRONMENT mode!"
