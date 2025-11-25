"""FastAPI application for serving XGBoost model predictions."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pathlib import Path
import pickle
import pandas as pd
from typing import Optional, List
import json

app = FastAPI(
    title="Spotify Popularity Prediction API",
    description="Predict if a track will be popular based on its features",
    version="1.0.0"
)


def _find_project_root() -> Path:
    """Find the Spotify project root directory."""
    current = Path.cwd()
    
    # Try to find Spotify folder
    for parent in [current, current.parent, current.parent.parent]:
        if parent.name == "Spotify" or (parent / "data").exists():
            return parent
    
    return current.parent if current.name == "spotify_pipeline" else current


def load_model():
    """Load the trained XGBoost model."""
    project_root = _find_project_root()
    model_path = project_root / "models" / "xgboost_model.pkl"
    
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found at {model_path}. "
            "Please run the Dagster pipeline first to train the model."
        )
    
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    
    return model


def load_feature_names():
    """Load the expected feature names from the training pipeline."""
    project_root = _find_project_root()
    feature_names_path = project_root / "data" / "dagster_output" / "03_feature_names.txt"
    
    if not feature_names_path.exists():
        # Try to load from a trained model's feature data
        features_path = project_root / "data" / "dagster_output" / "03_features.csv"
        if features_path.exists():
            df = pd.read_csv(features_path, nrows=0)
            return list(df.columns)
        raise FileNotFoundError(
            f"Feature names not found. Please run the Dagster pipeline first."
        )
    
    with open(feature_names_path, "r") as f:
        feature_names = [line.strip() for line in f.readlines()]
    
    return feature_names


# Load model and feature names at startup
try:
    model = load_model()
    feature_names = load_feature_names()
    print(f"✅ Model loaded successfully!")
    print(f"✅ Expected {len(feature_names)} features")
except Exception as e:
    print(f"⚠️  Warning: Could not load model at startup: {e}")
    print("Make sure to run the Dagster pipeline first!")
    model = None
    feature_names = []


class TrackFeatures(BaseModel):
    """Input features for a track prediction."""
    acousticness: float = Field(..., ge=0, le=1, description="Acousticness of the track (0-1)")
    danceability: float = Field(..., ge=0, le=1, description="Danceability of the track (0-1)")
    duration_ms: float = Field(..., gt=0, description="Duration in milliseconds")
    energy: float = Field(..., ge=0, le=1, description="Energy of the track (0-1)")
    explicit: int = Field(..., ge=0, le=1, description="Whether track is explicit (0 or 1)")
    instrumentalness: float = Field(..., ge=0, le=1, description="Instrumentalness (0-1)")
    key: int = Field(..., ge=0, le=11, description="Musical key (0-11)")
    liveness: float = Field(..., ge=0, le=1, description="Liveness (0-1)")
    loudness: float = Field(..., description="Loudness in dB")
    mode: int = Field(..., ge=0, le=1, description="Mode (0=minor, 1=major)")
    speechiness: float = Field(..., ge=0, le=1, description="Speechiness (0-1)")
    tempo: float = Field(..., gt=0, description="Tempo in BPM")
    time_signature: int = Field(..., ge=1, le=7, description="Time signature")
    valence: float = Field(..., ge=0, le=1, description="Valence/positivity (0-1)")
    artist_song_count: Optional[int] = Field(1, description="Number of songs by this artist")
    genre: Optional[str] = Field("pop", description="Genre of the track")
    
    class Config:
        schema_extra = {
            "example": {
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
        }


class PredictionResponse(BaseModel):
    """Response model for predictions."""
    prediction: int = Field(..., description="Predicted class (0=not popular, 1=popular)")
    probability_not_popular: float = Field(..., description="Probability of not being popular")
    probability_popular: float = Field(..., description="Probability of being popular")
    confidence: float = Field(..., description="Confidence score (max probability)")
    verdict: str = Field(..., description="Human-readable verdict")


def preprocess_features(track: TrackFeatures) -> pd.DataFrame:
    """Preprocess input features to match training format."""
    # Create base features dictionary
    features_dict = track.dict()
    
    # Calculate duration-based features
    project_root = _find_project_root()
    data_path = project_root / "data" / "spotify_data.csv"
    
    # Use reasonable defaults for duration thresholds if we can't load data
    q1, q95 = 180000, 300000  # Default values
    
    if data_path.exists():
        try:
            df = pd.read_csv(data_path)
            if 'duration_ms' in df.columns:
                q1 = df['duration_ms'].quantile(0.25)
                q95 = df['duration_ms'].quantile(0.95)
        except:
            pass
    
    features_dict['long_duration'] = 1 if track.duration_ms > q95 else 0
    features_dict['short_duration'] = 1 if track.duration_ms < q1 else 0
    
    # One-hot encode genre
    genre = features_dict.pop('genre')
    
    # Create DataFrame with base features
    df = pd.DataFrame([features_dict])
    
    # Add all possible genre columns as 0
    for feature_name in feature_names:
        if feature_name.startswith('genre_'):
            df[feature_name] = 0
    
    # Set the correct genre to 1
    genre_col = f'genre_{genre}'
    if genre_col in df.columns:
        df[genre_col] = 1
    
    # Ensure all expected features are present in correct order
    for feature_name in feature_names:
        if feature_name not in df.columns:
            df[feature_name] = 0
    
    # Reorder columns to match training
    df = df[feature_names]
    
    return df


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Spotify Popularity Prediction API",
        "status": "running",
        "model_loaded": model is not None,
        "num_features": len(feature_names),
        "endpoints": {
            "predict": "/predict (POST)",
            "health": "/health (GET)",
            "features": "/features (GET)",
            "model_info": "/model-info (GET)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please run the Dagster pipeline first."
        )
    
    return {
        "status": "healthy",
        "model_loaded": True,
        "num_features": len(feature_names)
    }


@app.get("/features")
async def get_features():
    """Get the list of required features."""
    return {
        "num_features": len(feature_names),
        "features": feature_names
    }


@app.get("/model-info")
async def get_model_info():
    """Get model metadata and performance information."""
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please run the Dagster pipeline first."
        )
    
    project_root = _find_project_root()
    metadata_path = project_root / "models" / "model_metadata.json"
    
    if not metadata_path.exists():
        return {
            "message": "Model metadata not found",
            "model_type": "XGBoost Classifier"
        }
    
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    
    return metadata


@app.post("/predict", response_model=PredictionResponse)
async def predict(track: TrackFeatures):
    """Make a prediction for a track."""
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please run the Dagster pipeline first."
        )
    
    try:
        # Preprocess features
        features_df = preprocess_features(track)
        
        # Make prediction
        prediction = model.predict(features_df)[0]
        probabilities = model.predict_proba(features_df)[0]
        
        # Create response
        response = PredictionResponse(
            prediction=int(prediction),
            probability_not_popular=float(probabilities[0]),
            probability_popular=float(probabilities[1]),
            confidence=float(max(probabilities)),
            verdict="Popular" if prediction == 1 else "Not Popular"
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction error: {str(e)}"
        )


@app.post("/predict-batch")
async def predict_batch(tracks: List[TrackFeatures]):
    """Make predictions for multiple tracks."""
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please run the Dagster pipeline first."
        )
    
    try:
        results = []
        for track in tracks:
            features_df = preprocess_features(track)
            prediction = model.predict(features_df)[0]
            probabilities = model.predict_proba(features_df)[0]
            
            results.append({
                "prediction": int(prediction),
                "probability_not_popular": float(probabilities[0]),
                "probability_popular": float(probabilities[1]),
                "confidence": float(max(probabilities)),
                "verdict": "Popular" if prediction == 1 else "Not Popular"
            })
        
        return {"predictions": results}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch prediction error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
