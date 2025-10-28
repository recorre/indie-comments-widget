#!/bin/bash

# Production Deployment Script
# This script handles the complete production deployment process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENV_FILE=".env.production"
COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if environment file exists
    if [ ! -f "$ENV_FILE" ]; then
        log_error "Environment file $ENV_FILE not found. Run setup_production.sh first."
        exit 1
    fi

    # Check if docker-compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Docker Compose file $COMPOSE_FILE not found."
        exit 1
    fi

    # Load environment variables
    set -a
    source "$ENV_FILE"
    set +a

    # Validate required environment variables
    required_vars=("NOCODEBACKEND_API_KEY" "INSTANCE" "SECRET_KEY" "JWT_SECRET_KEY")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_error "Required environment variable $var is not set in $ENV_FILE"
            exit 1
        fi
    done

    log_success "Prerequisites check passed"
}

create_backup() {
    log_info "Creating pre-deployment backup..."

    mkdir -p "$BACKUP_DIR"

    # Backup current environment
    cp "$ENV_FILE" "$BACKUP_DIR/" 2>/dev/null || true

    # Backup current docker-compose override if exists
    if [ -f "docker-compose.override.yml" ]; then
        cp "docker-compose.override.yml" "$BACKUP_DIR/"
    fi

    log_success "Backup created at $BACKUP_DIR"
}

pre_deployment_checks() {
    log_info "Running pre-deployment checks..."

    # Check if services are already running
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        log_warning "Services are currently running. They will be stopped and restarted."
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Deployment cancelled by user"
            exit 0
        fi
    fi

    # Validate docker-compose configuration
    if ! docker-compose -f "$COMPOSE_FILE" config > /dev/null; then
        log_error "Invalid Docker Compose configuration"
        exit 1
    fi

    # Check available disk space
    available_space=$(df / | tail -1 | awk '{print $4}')
    if [ "$available_space" -lt 1048576 ]; then # 1GB in KB
        log_warning "Low disk space detected: $(($available_space / 1024))MB available"
    fi

    log_success "Pre-deployment checks passed"
}

build_images() {
    log_info "Building Docker images..."

    # Build with no cache to ensure fresh builds
    docker-compose -f "$COMPOSE_FILE" build --no-cache

    log_success "Docker images built successfully"
}

deploy_services() {
    log_info "Deploying services..."

    # Stop existing services gracefully
    docker-compose -f "$COMPOSE_FILE" down --timeout 30

    # Start services
    docker-compose -f "$COMPOSE_FILE" up -d

    log_success "Services deployed successfully"
}

wait_for_services() {
    log_info "Waiting for services to be healthy..."

    local max_attempts=60
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts"

        # Check backend health
        if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
            log_success "Backend is healthy"
        else
            log_warning "Backend not ready yet"
        fi

        # Check frontend health
        if curl -f -s http://localhost:3000/health > /dev/null 2>&1; then
            log_success "Frontend is healthy"
        else
            log_warning "Frontend not ready yet"
        fi

        # Check widget service
        if curl -f -s http://localhost:8080/health > /dev/null 2>&1; then
            log_success "Widget service is healthy"
        else
            log_warning "Widget service not ready yet"
        fi

        # If all services are healthy, break
        if curl -f -s http://localhost:8000/health > /dev/null 2>&1 && \
           curl -f -s http://localhost:3000/health > /dev/null 2>&1 && \
           curl -f -s http://localhost:8080/health > /dev/null 2>&1; then
            log_success "All services are healthy!"
            return 0
        fi

        sleep 10
        ((attempt++))
    done

    log_error "Services failed to become healthy within $(($max_attempts * 10)) seconds"
    return 1
}

run_post_deployment_tests() {
    log_info "Running post-deployment tests..."

    # Test API endpoints
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        log_success "API health check passed"
    else
        log_error "API health check failed"
        return 1
    fi

    # Test frontend
    if curl -f -s -I http://localhost:3000/ | grep -q "200 OK"; then
        log_success "Frontend check passed"
    else
        log_error "Frontend check failed"
        return 1
    fi

    # Test widget files
    if curl -f -s -I http://localhost:8080/comment-widget.min.js | grep -q "200 OK"; then
        log_success "Widget file check passed"
    else
        log_error "Widget file check failed"
        return 1
    fi

    log_success "Post-deployment tests passed"
}

cleanup_old_images() {
    log_info "Cleaning up old Docker images..."

    # Remove dangling images
    docker image prune -f

    # Remove images older than 30 days (optional)
    # docker image prune -a --filter "until=720h" -f

    log_success "Docker cleanup completed"
}

send_notifications() {
    log_info "Sending deployment notifications..."

    # Here you could add Slack, email, or other notification integrations
    # For now, just log the deployment
    echo "$(date): Production deployment completed successfully" >> deployment.log

    log_success "Deployment notifications sent"
}

rollback() {
    log_error "Deployment failed. Initiating rollback..."

    # Stop current services
    docker-compose -f "$COMPOSE_FILE" down

    # Restore from backup if available
    if [ -d "$BACKUP_DIR" ]; then
        log_info "Restoring from backup..."

        # Restore environment file
        if [ -f "$BACKUP_DIR/$(basename $ENV_FILE)" ]; then
            cp "$BACKUP_DIR/$(basename $ENV_FILE)" "$ENV_FILE"
        fi

        # Restore docker-compose override
        if [ -f "$BACKUP_DIR/docker-compose.override.yml" ]; then
            cp "$BACKUP_DIR/docker-compose.override.yml" .
        fi

        # Restart services with backup configuration
        docker-compose -f "$COMPOSE_FILE" up -d

        log_success "Rollback completed"
    else
        log_error "No backup available for rollback"
    fi
}

main() {
    log_info "Starting production deployment..."

    # Trap errors for rollback
    trap rollback ERR

    check_prerequisites
    create_backup
    pre_deployment_checks
    build_images
    deploy_services

    if wait_for_services; then
        if run_post_deployment_tests; then
            cleanup_old_images
            send_notifications
            log_success "Production deployment completed successfully!"
            echo
            log_info "Services are running at:"
            echo "  - Backend API: http://localhost:8000"
            echo "  - Frontend Dashboard: http://localhost:3000"
            echo "  - Widget Files: http://localhost:8080"
            echo
            log_info "Don't forget to:"
            echo "  - Configure SSL certificates"
            echo "  - Update DNS records"
            echo "  - Configure monitoring alerts"
            echo "  - Test external access"
        else
            log_error "Post-deployment tests failed"
            exit 1
        fi
    else
        log_error "Services failed to start properly"
        exit 1
    fi
}

# Show usage if help requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Production Deployment Script"
    echo
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  --help, -h    Show this help message"
    echo
    echo "Environment:"
    echo "  Ensure .env.production exists with required variables"
    echo "  Run ./scripts/setup_production.sh first if needed"
    exit 0
fi

# Run main function
main "$@"