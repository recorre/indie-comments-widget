# 🚀 Deployment Guide

This comprehensive guide covers deploying the Comment Widget System to production with Docker, security hardening, monitoring, and performance optimizations.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
- [Environment Configuration](#environment-configuration)
- [Security Hardening](#security-hardening)
- [Monitoring & Logging](#monitoring--logging)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)

## 📋 Prerequisites

### System Requirements
- **Docker**: 20.10+ with Docker Compose
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk**: 10GB free space
- **Network**: Stable internet connection

### Software Dependencies
```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Accounts & Services
- **NoCodeBackend**: Production API instance
- **Domain Registrar**: For SSL certificates
- **Monitoring**: Optional (Sentry, Prometheus, Grafana)
- **CDN**: Optional (jsDelivr, Cloudflare)

## 🚀 Quick Start

### One-Command Production Setup
```bash
# Clone repository
git clone https://github.com/yourusername/comment-widget.git
cd comment-widget

# Run production setup
./scripts/setup_production.sh

# Edit environment variables
nano .env.production

# Deploy to production
./scripts/deploy_production.sh
```

## 🏠 Local Development

### Using Docker Compose (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Development Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn api.index:app --reload

# Frontend (new terminal)
cd frontend
pip install -r requirements.txt
python app.py

# Widget (new terminal)
cd widget
npm install
npm run dev
```

## 🏭 Production Deployment

### Automated Deployment
```bash
# Run setup script
./scripts/setup_production.sh

# Edit production environment
nano .env.production

# Deploy with production compose
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
curl https://yourdomain.com/health
```

### Manual Deployment Steps

#### 1. Environment Setup
```bash
# Create production environment file
cp .env.example .env.production

# Edit with production values
nano .env.production
```

#### 2. SSL Certificate Setup
```bash
# Install certbot
sudo apt install certbot

# Get SSL certificates
sudo certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
```

#### 3. Database Initialization
```bash
# Start PostgreSQL
docker-compose -f docker-compose.prod.yml up -d postgres

# Run initialization
docker-compose -f docker-compose.prod.yml exec postgres psql -U comment_widget -d comment_widget -f /docker-entrypoint-initdb.d/init.sql
```

#### 4. Service Deployment
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d --build

# Verify services
docker-compose -f docker-compose.prod.yml ps
```

#### 5. Health Checks
```bash
# Check all services
curl https://api.yourdomain.com/health
curl https://dashboard.yourdomain.com/health
curl https://cdn.yourdomain.com/comment-widget.min.js
```

## ⚙️ Environment Configuration

### Production Environment Variables
```bash
# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# NoCodeBackend
NOCODEBACKEND_API_KEY=your_production_key
INSTANCE=production_instance

# Security
SECRET_KEY=your_64_char_secret
JWT_SECRET_KEY=your_64_char_jwt_secret

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://dashboard.yourdomain.com

# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600

# External Services
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
GOOGLE_ANALYTICS_ID=GA_MEASUREMENT_ID

# URLs
BACKEND_URL=https://api.yourdomain.com
WIDGET_CDN_URL=https://cdn.jsdelivr.net/gh/username/repo@main/dist/
```

### Environment File Structure
```
.env.production      # Production environment
.env.staging         # Staging environment
.env.local           # Local development
```

## 🔒 Security Hardening

### Container Security
- **Non-root users**: All containers run as non-root
- **Minimal base images**: Alpine Linux for smaller attack surface
- **No privileged containers**: No privileged mode or host mounts

### Network Security
- **Internal networks**: Services communicate via Docker networks
- **No exposed ports**: Only Nginx exposes external ports
- **Rate limiting**: Implemented at Nginx level
- **SSL/TLS**: End-to-end encryption with Let's Encrypt

### Application Security
- **CORS policy**: Strict origin validation
- **Input validation**: Comprehensive input sanitization
- **XSS protection**: DOMPurify for widget content
- **CSRF protection**: Token-based protection

### Infrastructure Security
```bash
# Firewall configuration
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Fail2Ban for SSH protection
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

## 📊 Monitoring & Logging

### Application Monitoring
```bash
# Prometheus metrics
curl http://localhost:8000/metrics

# Health checks
curl http://localhost:8000/health
```

### Logging Configuration
- **Structured logging**: JSON format for production
- **Log rotation**: Automatic log rotation and cleanup
- **Centralized logging**: Optional ELK stack integration

### Error Tracking
- **Sentry integration**: Real-time error tracking
- **Custom alerts**: Configurable error thresholds
- **Performance monitoring**: Response time tracking

## ⚡ Performance Optimization

### Container Optimization
- **Multi-stage builds**: Minimal production images
- **Layer caching**: Optimized Docker layer ordering
- **Resource limits**: CPU and memory constraints

### Application Optimization
- **Gzip compression**: Enabled for all responses
- **Static file caching**: 1-year cache headers for assets
- **Connection pooling**: Database connection reuse
- **Async processing**: Non-blocking I/O operations

### CDN Integration
- **Widget distribution**: jsDelivr CDN for global delivery
- **Asset optimization**: Minified and compressed files
- **Cache invalidation**: Version-based cache busting

## 🔧 Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Validate configuration
docker-compose -f docker-compose.prod.yml config

# Check resource usage
docker stats
```

#### SSL Certificate Issues
```bash
# Renew certificates
sudo certbot renew

# Reload Nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

#### Database Connection Issues
```bash
# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres

# Test connection
docker-compose -f docker-compose.prod.yml exec postgres psql -U comment_widget -d comment_widget -c "SELECT 1;"
```

#### Performance Issues
```bash
# Monitor resource usage
docker stats

# Check application metrics
curl http://localhost:8000/metrics

# Analyze slow queries
docker-compose -f docker-compose.prod.yml exec postgres psql -U comment_widget -d comment_widget -c "SELECT * FROM pg_stat_activity;"
```

### Rollback Procedures
```bash
# Stop current deployment
docker-compose -f docker-compose.prod.yml down

# Restore from backup
./scripts/backup_production.sh --restore

# Restart with previous version
docker-compose -f docker-compose.prod.yml up -d
```

## 📞 Support

- **Documentation**: [docs/PRODUCTION_DEPLOYMENT.md](docs/PRODUCTION_DEPLOYMENT.md)
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## 🔄 Updates & Maintenance

### Regular Maintenance Tasks
```bash
# Update Docker images
docker-compose -f docker-compose.prod.yml pull

# Renew SSL certificates
sudo certbot renew

# Rotate logs
./scripts/maintenance.sh

# Backup data
./scripts/backup_production.sh
```

### Monitoring Alerts
- **Disk usage > 80%**: Expand storage or cleanup
- **Memory usage > 90%**: Scale resources or optimize
- **Error rate > 5%**: Investigate and fix issues
- **Response time > 2s**: Performance optimization needed