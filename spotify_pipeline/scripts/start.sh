#!/usr/bin/env bash
# Start Dagster dev server with proper environment

# Set library path for XGBoost on macOS
export DYLD_LIBRARY_PATH=~/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH

# Go to parent directory (where data/ and models/ folders are)
cd "$(dirname "$0")/.."

# Create necessary directories
mkdir -p data/dagster_storage
mkdir -p models

echo "🚀 Starting Dagster dev server from $(pwd)"
echo "📍 Data folder: $(pwd)/data"
echo "📍 Models folder: $(pwd)/models"
echo "📍 Open http://localhost:3000 in your browser"
echo ""

# Run from spotify_pipeline directory
cd spotify_pipeline
uv run dagster dev
