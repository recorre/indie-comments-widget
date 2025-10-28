# Deployment Scripts and Configuration Files

This document contains the actual deployment scripts and configuration files referenced in the main deployment plan.

## Deployment Scripts

### scripts/deploy.sh
```bash
#!/bin/bash

# Comprehensive deployment script for Comment Widget System
# Supports staging and production environments

set -e

ENVIRONMENT=${1:-staging}
VERSION=${2:-latest}

echo "🚀 Deploying Comment Widget System to $ENVIRONMENT"

# Validate environment
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo "❌ Invalid environment. Use 'staging' or 'production'"
    exit 1
fi

# Backend deployment
echo "📦 Deploying backend..."
cd backend

if [[ "$ENVIRONMENT" == "production" ]]; then
    vercel --prod
else
    vercel --staging
fi

# Frontend deployment
echo "🎨 Deploying frontend..."
cd ../frontend

if [[ "$ENVIRONMENT" == "production" ]]; then
    vercel --prod
else
    vercel --staging
fi

# Widget build
echo "🔧 Building widget..."
cd ../widget
npm run build

echo "✅ Deployment complete!"
echo "🌐 Backend URL: $(vercel ls | grep backend | awk '{print $3}')"
echo "🎨 Frontend URL: $(vercel ls | grep frontend | awk '{print $3}')"
echo "📦 Widget CDN: https://cdn.jsdelivr.net/gh/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^.]*\).*/\1/')@$VERSION/dist/"
```

### scripts/rollback.sh
```bash
#!/bin/bash

# Rollback deployment script
set -e

TARGET_VERSION=${1:-previous}
SERVICE=${2:-all}  # backend, frontend, widget, or all

echo "🔄 Rolling back $SERVICE to $TARGET_VERSION"

# Get previous deployment info
if [[ "$TARGET_VERSION" == "previous" ]]; then
    # Get last successful deployment from Vercel
    PREVIOUS_DEPLOYMENT=$(vercel ls --json | jq -r '.[] | select(.state == "READY") | .uid' | head -2 | tail -1)
else
    PREVIOUS_DEPLOYMENT=$TARGET_VERSION
fi

case $SERVICE in
    "backend")
        echo "Rolling back backend..."
        vercel rollback $PREVIOUS_DEPLOYMENT --yes
        ;;
    "frontend")
        echo "Rolling back frontend..."
        cd frontend
        vercel rollback $PREVIOUS_DEPLOYMENT --yes
        ;;
    "widget")
        echo "Rolling back widget..."
        # Rollback to previous Git tag
        git tag -d $(git describe --tags --abbrev=0)
        git push origin :refs/tags/$(git describe --tags --abbrev=0)
        ;;
    "all")
        echo "Rolling back all services..."
        vercel rollback $PREVIOUS_DEPLOYMENT --yes
        cd frontend
        vercel rollback $PREVIOUS_DEPLOYMENT --yes
        cd ..
        # Rollback widget tag
        ;;
    *)
        echo "❌ Invalid service. Use: backend, frontend, widget, or all"
        exit 1
        ;;
esac

echo "✅ Rollback complete"
```

### scripts/seed_production.py
```python
#!/usr/bin/env python3
"""
Production database seeding script
"""

import os
import sys
import httpx
from dotenv import load_dotenv

# Load environment
load_dotenv()

API_KEY = os.getenv("NOCODEBACKEND_API_KEY")
INSTANCE = os.getenv("INSTANCE", "production_instance")
BASE_URL = "https://openapi.nocodebackend.com"

async def seed_production_data():
    """Seed production database with initial data"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        # Create demo user
        demo_user = {
            "name": "Demo User",
            "email": "demo@commentwidget.com",
            "password_hash": "hashed_password",
            "plan_level": "free",
            "is_supporter": 0
        }

        response = await client.post(
            f"{BASE_URL}/create/users",
            json=demo_user,
            headers=headers,
            params={"Instance": INSTANCE}
        )
        response.raise_for_status()
        user_id = response.json()["id"]

        # Create demo thread
        demo_thread = {
            "usuario_proprietario_id": user_id,
            "external_page_id": "demo-thread",
            "url": "https://commentwidget.com/demo",
            "title": "Demo Discussion Thread"
        }

        response = await client.post(
            f"{BASE_URL}/create/threads",
            json=demo_thread,
            headers=headers,
            params={"Instance": INSTANCE}
        )
        response.raise_for_status()

        # Create sample comments
        sample_comments = [
            {
                "thread_referencia_id": response.json()["id"],
                "author_name": "Alice",
                "author_email_hash": "hash1",
                "content": "This is a great commenting system!",
                "is_approved": 1
            },
            {
                "thread_referencia_id": response.json()["id"],
                "author_name": "Bob",
                "author_email_hash": "hash2",
                "content": "I agree, very user-friendly.",
                "is_approved": 1
            }
        ]

        for comment in sample_comments:
            await client.post(
                f"{BASE_URL}/create/comments",
                json=comment,
                headers=headers,
                params={"Instance": INSTANCE}
            )

if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_production_data())
    print("✅ Production data seeded successfully")
```

## CI/CD Workflow Files

### .github/workflows/deploy-backend.yml
```yaml
name: Deploy Backend to Vercel

on:
  push:
    branches: [ main ]
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt

    - name: Run tests
      run: |
        cd backend
        python -m pytest tests/ -v

    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v25
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
        vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
        working-directory: ./backend
```

### .github/workflows/deploy-frontend.yml
```yaml
name: Deploy Frontend to Vercel

on:
  push:
    branches: [ main ]
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend.yml'

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        cd frontend
        pip install -r requirements.txt

    - name: Build static files
      run: |
        cd frontend
        python build_static.py

    - name: Deploy to Vercel
      uses: amondnet/vercel-action@v25
      with:
        vercel-token: ${{ secrets.VERCEL_TOKEN }}
        vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
        vercel-project-id: ${{ secrets.VERCEL_FRONTEND_PROJECT_ID }}
        working-directory: ./frontend
```

### .github/workflows/build-widget.yml
```yaml
name: Build and Deploy Widget

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]
    paths:
      - 'widget/**'
      - '.github/workflows/build-widget.yml'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Install dependencies
      run: |
        cd widget
        npm install

    - name: Run tests
      run: |
        cd widget
        npm test

    - name: Build widget
      run: |
        cd widget
        npm run build

    - name: Create GitHub release
      if: startsWith(github.ref, 'refs/tags/')
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}

    - name: Deploy to CDN (jsDelivr)
      run: |
        # Files are automatically available via jsDelivr
        # URL: https://cdn.jsdelivr.net/gh/{username}/{repo}@{tag}/dist/
        echo "Widget deployed to CDN"
```

## Configuration Files

### backend/vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "50mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "NOCODEBACKEND_API_KEY": "@nocodebackend_api_key",
    "INSTANCE": "@instance",
    "ENVIRONMENT": "production"
  },
  "functions": {
    "api/index.py": {
      "maxDuration": 30
    }
  }
}
```

### frontend/vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/app.py"
    }
  ],
  "env": {
    "BACKEND_URL": "@backend_url",
    "ENVIRONMENT": "production"
  }
}
```

### docker-compose.yml (Development)
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - NOCODEBACKEND_API_KEY=${NOCODEBACKEND_API_KEY}
      - INSTANCE=${INSTANCE}
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - BACKEND_URL=http://backend:8000
    volumes:
      - ./frontend:/app
    depends_on:
      - backend
```

### backend/Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000"]
```

### frontend/Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 3000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "3000"]
```

## Environment Templates

### backend/.env.production
```bash
# NoCodeBackend Configuration
NOCODEBACKEND_API_KEY=your_production_api_key
INSTANCE=your_production_instance

# Application Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# CORS Settings
ALLOWED_ORIGINS=https://dashboard.commentwidget.com,https://*.yoursite.com

# Webhook Configuration
WEBHOOK_URL=https://your-webhook-endpoint.com/webhook

# Security
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

### frontend/.env.production
```bash
# API Configuration
BACKEND_URL=https://api.commentwidget.com
WIDGET_CDN_URL=https://cdn.jsdelivr.net/gh/username/repo@main/dist/

# Analytics
GOOGLE_ANALYTICS_ID=GA_MEASUREMENT_ID

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_ERROR_REPORTING=true

# Security
SECRET_KEY=your-frontend-secret-key
```

## Health Check Scripts

### scripts/health-check.sh
```bash
#!/bin/bash

# Health check script for production monitoring
set -e

BACKEND_URL=${1:-"https://api.commentwidget.com"}
FRONTEND_URL=${2:-"https://dashboard.commentwidget.com"}
WIDGET_URL=${3:-"https://cdn.jsdelivr.net/gh/username/repo@main/dist/comment-widget.min.js"}

echo "🔍 Running health checks..."

# Backend health check
echo "Checking backend..."
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BACKEND_URL}/health")
if [[ "$BACKEND_STATUS" == "200" ]]; then
    echo "✅ Backend: Healthy"
else
    echo "❌ Backend: Unhealthy (Status: $BACKEND_STATUS)"
    exit 1
fi

# Frontend health check
echo "Checking frontend..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
if [[ "$FRONTEND_STATUS" == "200" ]]; then
    echo "✅ Frontend: Healthy"
else
    echo "❌ Frontend: Unhealthy (Status: $FRONTEND_STATUS)"
    exit 1
fi

# Widget CDN check
echo "Checking widget CDN..."
WIDGET_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$WIDGET_URL")
if [[ "$WIDGET_STATUS" == "200" ]]; then
    echo "✅ Widget CDN: Healthy"
else
    echo "❌ Widget CDN: Unhealthy (Status: $WIDGET_STATUS)"
    exit 1
fi

echo "🎉 All services are healthy!"
```

### scripts/monitor.sh
```bash
#!/bin/bash

# Monitoring script for production metrics
set -e

BACKEND_URL=${1:-"https://api.commentwidget.com"}

echo "📊 Collecting metrics..."

# API Response time
echo "Measuring API response time..."
API_RESPONSE_TIME=$(curl -s -o /dev/null -w "%{time_total}" "${BACKEND_URL}/health" | awk '{print $1 * 1000}')
echo "API Response Time: ${API_RESPONSE_TIME}ms"

# Comment creation rate (last hour)
echo "Checking comment creation rate..."
COMMENTS_CREATED=$(curl -s "${BACKEND_URL}/comments?limit=1000" | jq '.data | length')
echo "Comments in last 1000: $COMMENTS_CREATED"

# Error rate check
echo "Checking for recent errors..."
ERROR_COUNT=$(curl -s "${BACKEND_URL}/logs/errors" | jq '.count // 0')
echo "Recent errors: $ERROR_COUNT"

# Threshold checks
if (( $(echo "$API_RESPONSE_TIME > 2000" | bc -l) )); then
    echo "⚠️  WARNING: API response time is high (${API_RESPONSE_TIME}ms)"
fi

if [[ "$ERROR_COUNT" -gt 10 ]]; then
    echo "⚠️  WARNING: High error count ($ERROR_COUNT)"
fi

echo "✅ Monitoring complete"
```

## Usage Instructions

### Setting up CI/CD
1. Create the `.github/workflows/` directory
2. Copy the workflow files above
3. Set up the following secrets in your GitHub repository:
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`
   - `VERCEL_FRONTEND_PROJECT_ID`

### Running Deployments
```bash
# Deploy to staging
./scripts/deploy.sh staging

# Deploy to production
./scripts/deploy.sh production v1.0.0

# Rollback backend
./scripts/rollback.sh previous backend

# Health check
./scripts/health-check.sh

# Monitoring
./scripts/monitor.sh
```

### Setting up Docker (Optional)
```bash
# Build and run locally
docker-compose up --build

# Run in background
docker-compose up -d

# Stop services
docker-compose down
```

These scripts and configurations provide a complete deployment toolkit for the Comment Widget System, supporting both development and production environments with comprehensive monitoring and rollback capabilities.