#!/bin/bash
# Script to start the FastAPI server

set -e

echo "🚀 Starting Spotify Prediction API..."
echo ""

# Set XGBoost library path for macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    export DYLD_LIBRARY_PATH=~/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH
    echo "✅ XGBoost library path configured for macOS"
fi

# Navigate to spotify_pipeline directory
cd "$(dirname "$0")"

# Install dependencies if needed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed"
    echo "Install it with: pip install uv"
    exit 1
fi

echo "📦 Installing dependencies..."
uv sync

echo ""
echo "✅ Starting API server on http://localhost:8000"
echo "📖 API docs available at http://localhost:8000/docs"
echo ""

# Run the FastAPI server
uv run uvicorn api:app --reload --host 0.0.0.0 --port 8000
