#!/bin/bash
# Example curl commands to test the API

API_URL="http://localhost:8000"

echo "=================================="
echo "🎸 Spotify Prediction API Examples"
echo "=================================="
echo ""

# 1. Health check
echo "1️⃣  Health Check"
echo "Command: curl $API_URL/health"
curl -s $API_URL/health | python3 -m json.tool
echo ""
echo ""

# 2. Model info
echo "2️⃣  Model Information"
echo "Command: curl $API_URL/model-info"
curl -s $API_URL/model-info | python3 -m json.tool
echo ""
echo ""

# 3. Single prediction
echo "3️⃣  Single Prediction (Pop Track)"
echo 'Command: curl -X POST $API_URL/predict -H "Content-Type: application/json" -d {...}'
curl -s -X POST $API_URL/predict \
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
  }' | python3 -m json.tool
echo ""
echo ""

# 4. Another prediction (Classical - likely not popular)
echo "4️⃣  Single Prediction (Classical Track)"
curl -s -X POST $API_URL/predict \
  -H "Content-Type: application/json" \
  -d '{
    "acousticness": 0.8,
    "danceability": 0.3,
    "duration_ms": 180000,
    "energy": 0.2,
    "explicit": 0,
    "instrumentalness": 0.5,
    "key": 2,
    "liveness": 0.1,
    "loudness": -15.0,
    "mode": 0,
    "speechiness": 0.03,
    "tempo": 80.0,
    "time_signature": 4,
    "valence": 0.3,
    "artist_song_count": 5,
    "genre": "classical"
  }' | python3 -m json.tool
echo ""
echo ""

echo "=================================="
echo "✅ All examples completed!"
echo "=================================="
echo ""
echo "💡 Tip: Visit $API_URL/docs for interactive API documentation"
