#!/bin/bash

# Production Environment Setup Script
# This script sets up the production environment for the Comment Widget System

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENV_FILE=".env.production"
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    log_success "Dependencies check passed"
}

create_env_file() {
    log_info "Setting up environment configuration..."

    if [ -f "$ENV_FILE" ]; then
        log_warning "Environment file $ENV_FILE already exists. Creating backup..."
        mkdir -p "$BACKUP_DIR"
        cp "$ENV_FILE" "$BACKUP_DIR/"
        log_info "Backup created at $BACKUP_DIR/$ENV_FILE"
    fi

    # Create production environment file
    cat > "$ENV_FILE" << EOF
# Production Environment Configuration
# Generated on $(date)

# Application Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# NoCodeBackend Configuration
NOCODEBACKEND_API_KEY=${NOCODEBACKEND_API_KEY:-"your_production_api_key_here"}
INSTANCE=${INSTANCE:-"production_instance"}

# Security
SECRET_KEY=${SECRET_KEY:-"$(openssl rand -hex 32)"}
JWT_SECRET_KEY=${JWT_SECRET_KEY:-"$(openssl rand -hex 32)"}

# CORS Settings
ALLOWED_ORIGINS=https://yourdomain.com,https://dashboard.yourdomain.com

# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600

# Database (PostgreSQL - optional)
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-"$(openssl rand -hex 16)"}

# External Services
SENTRY_DSN=${SENTRY_DSN:-""}
GOOGLE_ANALYTICS_ID=${GOOGLE_ANALYTICS_ID:-""}

# URLs
BACKEND_URL=https://api.yourdomain.com
WIDGET_CDN_URL=https://cdn.jsdelivr.net/gh/yourusername/comment-widget@main/dist/

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_ERROR_REPORTING=true
PROMETHEUS_METRICS_ENABLED=true

# SSL/TLS (if using certbot)
SSL_CERT_PATH=/etc/letsencrypt/live/yourdomain.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/yourdomain.com/privkey.pem
EOF

    log_success "Environment file created at $ENV_FILE"
    log_warning "Please edit $ENV_FILE with your actual production values"
}

setup_ssl() {
    log_info "Setting up SSL certificates..."

    # Create SSL directory structure
    mkdir -p nginx/ssl

    # Check if certbot is available
    if command -v certbot &> /dev/null; then
        log_info "Certbot found. Run the following commands to get SSL certificates:"
        echo "sudo certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com -d dashboard.yourdomain.com"
        echo "sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/"
        echo "sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/"
    else
        log_warning "Certbot not found. Please install certbot and obtain SSL certificates manually"
        log_info "Self-signed certificates will be used for now"
    fi
}

setup_nginx() {
    log_info "Setting up Nginx configuration..."

    mkdir -p nginx

    # Create nginx configuration
    cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Enable gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=widget:10m rate=100r/s;

    # Upstream servers
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    upstream widget {
        server widget:80;
    }

    server {
        listen 80;
        server_name yourdomain.com dashboard.yourdomain.com api.yourdomain.com;

        # Redirect all HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.yourdomain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

        # Rate limiting for API
        limit_req zone=api burst=20 nodelay;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeout settings
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # Health check endpoint
        location /health {
            proxy_pass http://backend/health;
            access_log off;
        }
    }

    server {
        listen 443 ssl http2;
        server_name dashboard.yourdomain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeout settings
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
    }

    server {
        listen 443 ssl http2;
        server_name cdn.yourdomain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # CORS headers for widget
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, OPTIONS";
        add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept";

        # Rate limiting for widget
        limit_req zone=widget burst=100 nodelay;

        location / {
            proxy_pass http://widget;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Cache static assets
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF

    log_success "Nginx configuration created"
}

setup_monitoring() {
    log_info "Setting up monitoring configuration..."

    mkdir -p monitoring/prometheus monitoring/grafana/provisioning/datasources

    # Create Prometheus configuration
    cat > monitoring/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'comment-widget-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'comment-widget-frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']
    scrape_interval: 15s
EOF

    # Create Grafana datasource configuration
    cat > monitoring/grafana/provisioning/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

    log_success "Monitoring configuration created"
}

create_backup_script() {
    log_info "Creating backup script..."

    cat > scripts/backup_production.sh << 'EOF'
#!/bin/bash

# Production Backup Script
set -e

BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Creating production backup..."

# Backup environment files
cp .env.production "$BACKUP_DIR/" 2>/dev/null || true

# Backup database if using PostgreSQL
if docker-compose ps postgres | grep -q "Up"; then
    echo "Backing up PostgreSQL database..."
    docker-compose exec postgres pg_dump -U comment_widget comment_widget > "$BACKUP_DIR/database.sql"
fi

# Backup Redis data
if docker-compose ps redis | grep -q "Up"; then
    echo "Backing up Redis data..."
    docker-compose exec redis redis-cli save
    docker cp $(docker-compose ps -q redis):/data/dump.rdb "$BACKUP_DIR/redis_dump.rdb"
fi

# Create compressed archive
tar -czf "${BACKUP_DIR}.tar.gz" -C backups "$(basename $BACKUP_DIR)"

echo "Backup completed: ${BACKUP_DIR}.tar.gz"

# Cleanup old backups (keep last 7 days)
find backups -name "*.tar.gz" -mtime +7 -delete
EOF

    chmod +x scripts/backup_production.sh
    log_success "Backup script created"
}

main() {
    log_info "Starting production environment setup..."

    check_dependencies
    create_env_file
    setup_ssl
    setup_nginx
    setup_monitoring
    create_backup_script

    log_success "Production environment setup completed!"
    echo
    log_info "Next steps:"
    echo "1. Edit .env.production with your actual values"
    echo "2. Obtain SSL certificates and place them in nginx/ssl/"
    echo "3. Update nginx/nginx.conf with your domain names"
    echo "4. Run: docker-compose -f docker-compose.prod.yml up -d"
    echo "5. Test the deployment"
    echo
    log_warning "Remember to:"
    echo "- Change default passwords"
    echo "- Configure firewall rules"
    echo "- Set up log rotation"
    echo "- Configure monitoring alerts"
}

# Run main function
main "$@"
EOF

    chmod +x scripts/setup_production.sh
    log_success "Production setup script created"
}

main() {
    log_info "Starting production environment setup..."

    check_dependencies
    create_env_file
    setup_ssl
    setup_nginx
    setup_monitoring
    create_backup_script

    log_success "Production environment setup completed!"
    echo
    log_info "Next steps:"
    echo "1. Edit .env.production with your actual values"
    echo "2. Obtain SSL certificates and place them in nginx/ssl/"
    echo "3. Update nginx/nginx.conf with your domain names"
    echo "4. Run: docker-compose -f docker-compose.prod.yml up -d"
    echo "5. Test the deployment"
    echo
    log_warning "Remember to:"
    echo "- Change default passwords"
    echo "- Configure firewall rules"
    echo "- Set up log rotation"
    echo "- Configure monitoring alerts"
}

# Run main function
main "$@"