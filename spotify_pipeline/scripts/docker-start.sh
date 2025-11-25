#!/bin/bash
# Script to build and start Docker containers

set -e

echo "🐳 Building and starting Spotify Pipeline Docker containers..."
echo ""

# Navigate to the spotify_pipeline directory
cd "$(dirname "$0")"

# Build the containers
echo "📦 Building Docker images..."
docker compose build

echo ""
echo "🚀 Starting containers..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check status
echo ""
echo "📊 Container status:"
docker compose ps

echo ""
echo "✅ Services started successfully!"
echo ""
echo "🎯 Access the services:"
echo "   - Dagster UI:  http://localhost:3000"
echo "   - API:         http://localhost:8000"
echo "   - API Docs:    http://localhost:8000/docs"
echo ""
echo "📝 Useful commands:"
echo "   - View logs:        docker compose logs -f"
echo "   - View Dagster logs: docker compose logs -f dagster"
echo "   - View API logs:     docker compose logs -f api"
echo "   - Stop services:     docker compose down"
echo "   - Restart services:  docker compose restart"
echo ""
