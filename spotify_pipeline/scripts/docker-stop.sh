#!/bin/bash
# Script to stop Docker containers

set -e

echo "🛑 Stopping Spotify Pipeline Docker containers..."
echo ""

# Navigate to the spotify_pipeline directory
cd "$(dirname "$0")"

# Stop containers
docker-compose down

echo ""
echo "✅ Containers stopped successfully!"
echo ""
echo "💡 To remove volumes as well, run: docker-compose down -v"
echo ""
