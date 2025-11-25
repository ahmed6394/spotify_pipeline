#!/usr/bin/env bash
# Quick start script for the Spotify Dagster pipeline

set -e

echo "🎵 Starting Spotify Dagster Pipeline Setup"
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Must run from spotify_pipeline directory"
    exit 1
fi

# Check for libomp on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! brew list libomp &>/dev/null; then
        echo "📦 Installing libomp for XGBoost..."
        brew install libomp
    fi
    
    # Set environment variable for custom Homebrew location
    if [ -d "$HOME/homebrew/opt/libomp/lib" ]; then
        echo "🔧 Setting DYLD_LIBRARY_PATH for libomp..."
        export DYLD_LIBRARY_PATH="$HOME/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH"
        
        # Add to shell config if not already there
        if ! grep -q "DYLD_LIBRARY_PATH.*libomp" ~/.zshrc 2>/dev/null; then
            echo 'export DYLD_LIBRARY_PATH=~/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH' >> ~/.zshrc
            echo "✅ Added libomp to ~/.zshrc"
        fi
    fi
fi

# Install dependencies
echo "📦 Installing dependencies with uv..."
uv sync

# Create directories
echo "📁 Creating output directories..."
mkdir -p ../data
mkdir -p ../models

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the pipeline:"
echo "   export DYLD_LIBRARY_PATH=~/homebrew/opt/libomp/lib:\$DYLD_LIBRARY_PATH"
echo "   dg dev"
echo ""
echo "Then open http://localhost:3000 and click 'Materialize all'"
echo ""
