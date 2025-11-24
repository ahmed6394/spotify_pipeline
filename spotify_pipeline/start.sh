#!/usr/bin/env bash
# Start Dagster dev server with proper environment

# Set library path for XGBoost on macOS
export DYLD_LIBRARY_PATH=~/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH

echo "🚀 Starting Dagster dev server..."
echo "📍 Open http://localhost:3000 in your browser"
echo ""

uv run dagster dev
