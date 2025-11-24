#!/usr/bin/env python3
"""
Quick script to get predictions for tracks from your CSV file.

Usage:
    python predict_from_csv.py                    # Predict 5 random tracks
    python predict_from_csv.py --num 10          # Predict 10 random tracks
    python predict_from_csv.py --track "Song"    # Predict specific track by name
"""

import requests
import pandas as pd
import argparse
from pathlib import Path
import sys


def find_project_root():
    """Find the Spotify project root directory."""
    current = Path.cwd()
    
    for parent in [current, current.parent, current.parent.parent]:
        if parent.name == "Spotify" or (parent / "data").exists():
            return parent
    
    return current.parent if current.name == "spotify_pipeline" else current


def load_csv():
    """Load the Spotify dataset."""
    project_root = find_project_root()
    csv_path = project_root / "data" / "spotify_data.csv"
    
    if not csv_path.exists():
        print(f"❌ Error: CSV file not found at {csv_path}")
        sys.exit(1)
    
    return pd.read_csv(csv_path)


def prepare_track_features(row):
    """Convert a CSV row to API-compatible features."""
    return {
        "acousticness": float(row.get("acousticness", 0)),
        "danceability": float(row.get("danceability", 0)),
        "duration_ms": float(row.get("duration_ms", 200000)),
        "energy": float(row.get("energy", 0)),
        "explicit": int(row.get("explicit", 0)),
        "instrumentalness": float(row.get("instrumentalness", 0)),
        "key": int(row.get("key", 0)),
        "liveness": float(row.get("liveness", 0)),
        "loudness": float(row.get("loudness", 0)),
        "mode": int(row.get("mode", 0)),
        "speechiness": float(row.get("speechiness", 0)),
        "tempo": float(row.get("tempo", 120)),
        "time_signature": int(row.get("time_signature", 4)),
        "valence": float(row.get("valence", 0)),
        "artist_song_count": int(row.get("artist_song_count", 1)) if pd.notna(row.get("artist_song_count")) else 1,
        "genre": str(row.get("genre", "pop"))
    }


def predict_track(track_features, api_url="http://localhost:8000"):
    """Get prediction for a single track."""
    try:
        response = requests.post(f"{api_url}/predict", json=track_features)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Get predictions for tracks from CSV")
    parser.add_argument("--num", type=int, default=5, help="Number of random tracks to predict")
    parser.add_argument("--track", type=str, help="Specific track name to search for")
    parser.add_argument("--artist", type=str, help="Filter by artist name")
    parser.add_argument("--api-url", type=str, default="http://localhost:8000", help="API URL")
    
    args = parser.parse_args()
    
    print("🎸 Spotify Track Prediction from CSV")
    print("=" * 60)
    print()
    
    # Check API health
    try:
        response = requests.get(f"{args.api_url}/health")
        if response.status_code != 200:
            print(f"❌ API is not healthy: {response.text}")
            sys.exit(1)
        print("✅ API is healthy and ready")
    except requests.exceptions.RequestException:
        print(f"❌ Cannot connect to API at {args.api_url}")
        print("Make sure the API is running: ./start_api.sh")
        sys.exit(1)
    
    print()
    
    # Load data
    print("📁 Loading CSV data...")
    df = load_csv()
    print(f"✅ Loaded {len(df)} tracks")
    print()
    
    # Filter data if requested
    if args.track:
        df = df[df['track_name'].str.contains(args.track, case=False, na=False)]
        if len(df) == 0:
            print(f"❌ No tracks found matching '{args.track}'")
            sys.exit(1)
        print(f"🔍 Found {len(df)} tracks matching '{args.track}'")
    
    if args.artist:
        df = df[df['artist_name'].str.contains(args.artist, case=False, na=False)]
        if len(df) == 0:
            print(f"❌ No tracks found for artist '{args.artist}'")
            sys.exit(1)
        print(f"🔍 Found {len(df)} tracks by '{args.artist}'")
    
    # Sample tracks
    num_samples = min(args.num, len(df))
    samples = df.sample(n=num_samples)
    
    print(f"🎵 Predicting {num_samples} track(s)...")
    print("=" * 60)
    print()
    
    # Make predictions
    for idx, (_, row) in enumerate(samples.iterrows(), 1):
        track_name = row.get('track_name', 'Unknown')
        artist_name = row.get('artist_name', 'Unknown')
        actual_popularity = row.get('popularity', 'N/A')
        
        print(f"Track {idx}/{num_samples}")
        print(f"  🎵 {track_name}")
        print(f"  👤 {artist_name}")
        print(f"  📊 Actual Popularity: {actual_popularity}")
        
        # Prepare and send request
        features = prepare_track_features(row)
        prediction = predict_track(features, args.api_url)
        
        if prediction:
            verdict = prediction['verdict']
            confidence = prediction['confidence'] * 100
            prob_popular = prediction['probability_popular'] * 100
            
            # Add emoji based on verdict
            emoji = "🔥" if verdict == "Popular" else "📉"
            
            print(f"  {emoji} Prediction: {verdict}")
            print(f"  💯 Confidence: {confidence:.1f}%")
            print(f"  📈 Popularity Probability: {prob_popular:.1f}%")
        else:
            print("  ❌ Prediction failed")
        
        print()
    
    print("=" * 60)
    print("✅ All predictions completed!")


if __name__ == "__main__":
    main()
