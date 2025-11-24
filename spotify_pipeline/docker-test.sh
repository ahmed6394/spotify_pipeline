#!/bin/bash
# Script to test Docker containers after startup

set -e

API_URL="http://localhost:8000"
DAGSTER_URL="http://localhost:3000"

echo "🧪 Testing Spotify Pipeline Docker Containers"
echo "=============================================="
echo ""

# Function to check if service is responding
check_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=0
    
    echo "🔍 Checking $name at $url..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✅ $name is responding"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo "   Attempt $attempt/$max_attempts..."
        sleep 2
    done
    
    echo "❌ $name failed to respond after $max_attempts attempts"
    return 1
}

# Check if containers are running
echo "📦 Checking if containers are running..."
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Containers are not running!"
    echo "Run: ./docker-start.sh"
    exit 1
fi
echo "✅ Containers are running"
echo ""

# Check Dagster
if check_service "$DAGSTER_URL" "Dagster"; then
    echo ""
else
    echo "❌ Dagster health check failed"
    echo "Check logs: docker-compose logs dagster"
    exit 1
fi

# Check API
if check_service "$API_URL" "API"; then
    echo ""
else
    echo "❌ API health check failed"
    echo "Check logs: docker-compose logs api"
    exit 1
fi

# Test API health endpoint
echo "🏥 Testing API health endpoint..."
if response=$(curl -s "$API_URL/health"); then
    echo "✅ Health endpoint working"
    echo "Response: $response"
else
    echo "❌ Health endpoint failed"
    exit 1
fi
echo ""

# Check if model exists
echo "🤖 Checking if model exists..."
if docker-compose exec -T api test -f /app/models/xgboost_model.pkl; then
    echo "✅ Model file found in container"
    
    # Try a prediction
    echo ""
    echo "🎵 Testing prediction endpoint..."
    prediction=$(curl -s -X POST "$API_URL/predict" \
      -H "Content-Type: application/json" \
      -d '{
        "acousticness": 0.1,
        "danceability": 0.7,
        "duration_ms": 200000,
        "energy": 0.8,
        "explicit": 0,
        "instrumentalness": 0.0,
        "key": 5,
        "liveness": 0.1,
        "loudness": -5.0,
        "mode": 1,
        "speechiness": 0.05,
        "tempo": 120.0,
        "time_signature": 4,
        "valence": 0.6,
        "artist_song_count": 10,
        "genre": "pop"
      }')
    
    if [ $? -eq 0 ]; then
        echo "✅ Prediction endpoint working"
        echo "Response: $prediction"
    else
        echo "❌ Prediction failed"
    fi
else
    echo "⚠️  Model file not found"
    echo "To train the model:"
    echo "  1. Open http://localhost:3000"
    echo "  2. Click 'Materialize all'"
    echo "  3. Wait for completion"
fi
echo ""

# Show container stats
echo "📊 Container Status:"
docker-compose ps
echo ""

echo "=============================================="
echo "✅ All tests completed!"
echo ""
echo "🎯 Services:"
echo "   - Dagster UI: http://localhost:3000"
echo "   - API:        http://localhost:8000"
echo "   - API Docs:   http://localhost:8000/docs"
echo ""
