#!/bin/bash
# AutoGrowth Pro — Deployment script
# Usage: ./scripts/deploy.sh [server_ip]
set -e

SERVER=${1:-"your-server-ip"}

echo "🚀 Deploying AutoGrowth Pro to $SERVER"

# Build and push images (or use docker compose directly on server)
ssh root@$SERVER "mkdir -p /opt/autogrowth"
scp -r . root@$SERVER:/opt/autogrowth/
ssh root@$SERVER "cd /opt/autogrowth && cp .env.example .env && echo 'Fill in .env then run: docker compose up -d'"

echo "✅ Files deployed. SSH to server and run: docker compose up -d"
