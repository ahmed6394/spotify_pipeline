# Spotify Popularity Prediction API

A FastAPI application that serves predictions from the XGBoost model trained by the Dagster pipeline.

## 🚀 Quick Start

### 1. Run the Dagster Pipeline First

Before starting the API, make sure you have trained the model:

```bash
cd /Users/zerfaouiabdallah/Spotify/spotify_pipeline
./start.sh
```

Then navigate to http://localhost:3000 and click "Materialize all" to run the complete pipeline and train the model.

### 2. Start the API Server

```bash
./start_api.sh
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📡 API Endpoints

### GET `/`
Root endpoint with API information.

```bash
curl http://localhost:8000/
```

### GET `/health`
Health check endpoint to verify the model is loaded.

```bash
curl http://localhost:8000/health
```

### GET `/model-info`
Get detailed model metadata including hyperparameters and performance metrics.

```bash
curl http://localhost:8000/model-info
```

### GET `/features`
Get the list of required features for predictions.

```bash
curl http://localhost:8000/features
```

### POST `/predict`
Make a prediction for a single track.

**Request Body:**
```json
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
}
```

**Example with curl:**
```bash
curl -X POST http://localhost:8000/predict \
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
  }'
```

**Response:**
```json
{
  "prediction": 1,
  "probability_not_popular": 0.15,
  "probability_popular": 0.85,
  "confidence": 0.85,
  "verdict": "Popular"
}
```

### POST `/predict-batch`
Make predictions for multiple tracks at once.

**Request Body:**
```json
[
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
```

## 🧪 Testing the API

Run the test script to verify all endpoints:

```bash
uv run python test_api.py
```

This will:
- Check API health
- Get model information
- Make single predictions
- Test with real CSV data
- Make batch predictions

## 📊 Feature Descriptions

| Feature | Description | Range |
|---------|-------------|-------|
| `acousticness` | Confidence measure of whether the track is acoustic | 0.0 - 1.0 |
| `danceability` | How suitable a track is for dancing | 0.0 - 1.0 |
| `duration_ms` | Duration of the track in milliseconds | > 0 |
| `energy` | Perceptual measure of intensity and activity | 0.0 - 1.0 |
| `explicit` | Whether the track has explicit lyrics | 0 or 1 |
| `instrumentalness` | Predicts whether a track contains no vocals | 0.0 - 1.0 |
| `key` | The key the track is in (C=0, C#=1, etc.) | 0 - 11 |
| `liveness` | Detects presence of an audience | 0.0 - 1.0 |
| `loudness` | Overall loudness in decibels (dB) | typically -60 to 0 |
| `mode` | Modality of the track (minor=0, major=1) | 0 or 1 |
| `speechiness` | Detects presence of spoken words | 0.0 - 1.0 |
| `tempo` | Tempo in beats per minute (BPM) | > 0 |
| `time_signature` | Estimated time signature | 1 - 7 |
| `valence` | Musical positiveness conveyed by a track | 0.0 - 1.0 |
| `artist_song_count` | Number of songs by this artist in dataset | ≥ 1 |
| `genre` | Music genre | string (e.g., "pop", "rock") |

## 🐍 Python Client Example

```python
import requests

# Single prediction
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

response = requests.post("http://localhost:8000/predict", json=track)
prediction = response.json()

print(f"Prediction: {prediction['verdict']}")
print(f"Confidence: {prediction['confidence']:.2%}")
```

## 🔧 Development

### Manual Start (without script)

```bash
cd /Users/zerfaouiabdallah/Spotify/spotify_pipeline
export DYLD_LIBRARY_PATH=~/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH
uv run uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Change Port

Edit `start_api.sh` and change the `--port` parameter, or run manually:

```bash
uv run uvicorn api:app --reload --host 0.0.0.0 --port 8080
```

## 📝 Notes

- The API automatically loads the model from `models/xgboost_model.pkl`
- Feature names are loaded from `data/dagster_output/03_feature_names.txt`
- The model must be trained via the Dagster pipeline before starting the API
- Duration thresholds are calculated from the original CSV data for accurate predictions

## 🐛 Troubleshooting

**Problem**: "Model not loaded" error

**Solution**: Run the Dagster pipeline first to train the model:
```bash
./start.sh
# Then materialize all assets in the UI
```

**Problem**: "Feature names not found"

**Solution**: Make sure the Dagster pipeline has completed successfully and created the output files in `data/dagster_output/`

**Problem**: XGBoost library errors on macOS

**Solution**: Make sure the `DYLD_LIBRARY_PATH` is set (the `start_api.sh` script does this automatically)
