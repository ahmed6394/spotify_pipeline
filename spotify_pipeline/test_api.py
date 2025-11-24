"""
Example script to test the Spotify Prediction API.

This script shows how to:
1. Send a single prediction request
2. Send a batch of predictions
3. Get model information
"""

import requests
import json
import pandas as pd
from pathlib import Path


def find_project_root():
    """Find the Spotify project root directory."""
    current = Path.cwd()
    
    for parent in [current, current.parent, current.parent.parent]:
        if parent.name == "Spotify" or (parent / "data").exists():
            return parent
    
    return current.parent if current.name == "spotify_pipeline" else current


# API base URL
API_URL = "http://localhost:8000"


def test_health():
    """Test the health endpoint."""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_model_info():
    """Get model information."""
    print("📊 Getting model information...")
    response = requests.get(f"{API_URL}/model-info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_single_prediction():
    """Test a single prediction."""
    print("🎵 Testing single prediction...")
    
    # Example track features (you can modify these)
    track = {
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
    }
    
    response = requests.post(f"{API_URL}/predict", json=track)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_prediction_from_csv():
    """Load a real track from CSV and predict."""
    print("📁 Testing prediction with real CSV data...")
    
    # Load a sample from the CSV
    project_root = find_project_root()
    csv_path = project_root / "data" / "spotify_data.csv"
    
    if not csv_path.exists():
        print(f"❌ CSV file not found at {csv_path}")
        return
    
    # Load the CSV and get a random sample
    df = pd.read_csv(csv_path)
    sample = df.sample(n=1).iloc[0]
    
    print(f"Track: {sample.get('track_name', 'Unknown')} by {sample.get('artist_name', 'Unknown')}")
    print(f"Actual popularity: {sample.get('popularity', 'N/A')}")
    print()
    
    # Prepare features for API
    track = {
        "acousticness": float(sample.get("acousticness", 0)),
        "danceability": float(sample.get("danceability", 0)),
        "duration_ms": float(sample.get("duration_ms", 200000)),
        "energy": float(sample.get("energy", 0)),
        "explicit": int(sample.get("explicit", 0)),
        "instrumentalness": float(sample.get("instrumentalness", 0)),
        "key": int(sample.get("key", 0)),
        "liveness": float(sample.get("liveness", 0)),
        "loudness": float(sample.get("loudness", 0)),
        "mode": int(sample.get("mode", 0)),
        "speechiness": float(sample.get("speechiness", 0)),
        "tempo": float(sample.get("tempo", 120)),
        "time_signature": int(sample.get("time_signature", 4)),
        "valence": float(sample.get("valence", 0)),
        "artist_song_count": int(sample.get("artist_song_count", 1)) if "artist_song_count" in sample else 1,
        "genre": str(sample.get("genre", "pop"))
    }
    
    response = requests.post(f"{API_URL}/predict", json=track)
    print(f"Status: {response.status_code}")
    print(f"Prediction: {json.dumps(response.json(), indent=2)}")
    print()


def test_batch_prediction():
    """Test batch predictions."""
    print("📦 Testing batch prediction...")
    
    tracks = [
        {
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
        },
        {
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
        }
    ]
    
    response = requests.post(f"{API_URL}/predict-batch", json=tracks)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def main():
    """Run all tests."""
    print("=" * 60)
    print("🎸 Spotify Prediction API Test Suite")
    print("=" * 60)
    print()
    
    try:
        # Test basic endpoints
        test_health()
        test_model_info()
        
        # Test predictions
        test_single_prediction()
        test_prediction_from_csv()
        test_batch_prediction()
        
        print("=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API")
        print("Make sure the API is running: ./start_api.sh")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
