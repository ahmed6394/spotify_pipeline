#!/bin/bash
# Script to view Docker container logs

set -e

cd "$(dirname "$0")"

echo "📋 Docker Container Logs"
echo "========================"
echo ""
echo "Press Ctrl+C to exit"
echo ""

# Follow logs from both containers
docker-compose logs -f
