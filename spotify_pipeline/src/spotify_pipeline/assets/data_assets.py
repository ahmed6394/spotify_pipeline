# src/spotify_pipeline/assets/data_assets.py

"""
Assets responsible for:
- Loading the raw Kaggle CSV
- Cleaning / preprocessing
- Feature engineering
- Train/test splitting
"""

from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass

import pandas as pd
from dagster import asset, Output, AssetIn
from sklearn.model_selection import train_test_split as sk_train_test_split


POPULARITY_THRESHOLD = 85
SEED = 42


@dataclass
class FeatureSet:
    """Container for features and target."""
    features: pd.DataFrame
    target: pd.Series


# -----------------------------------------------------------
# 1. Load raw data
# -----------------------------------------------------------

@asset(
    required_resource_keys={"file_config"},
    description="Load the raw Spotify CSV from data folder"
)
def raw_spotify_csv(context) -> Output[pd.DataFrame]:
    """Load Spotify data from CSV file in data/ folder."""
    import os
    
    # Try multiple possible locations
    possible_paths = [
        Path("data"),  # If running from project root
        Path("../data"),  # If running from spotify_pipeline/
        Path(__file__).parent.parent.parent.parent.parent / "data",  # Absolute from this file
        Path.cwd() / "data",  # Current working directory
        Path.cwd().parent / "data",  # Parent of current working directory
    ]
    
    data_dir = None
    for path in possible_paths:
        resolved = path.resolve()
        context.log.info(f"Trying path: {resolved}")
        if resolved.exists() and any(resolved.glob("*.csv")):
            data_dir = resolved
            break
    
    if data_dir is None:
        raise FileNotFoundError(
            f"No CSV file found. Tried paths:\n" + 
            "\n".join(f"  - {p.resolve()}" for p in possible_paths) +
            "\n\nPlease ensure spotify_data.csv is in the data/ folder."
        )
    
    context.log.info(f"Found data directory: {data_dir}")
    
    # Find the first CSV file
    csv_files = list(data_dir.glob("*.csv"))
    csv_path = csv_files[0]
    context.log.info(f"Loading data from: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    context.log.info(f"Loaded {len(df)} rows with {len(df.columns)} columns")
    
    return Output(
        df,
        metadata={
            "rows": len(df),
            "columns": len(df.columns),
            "source": str(csv_path),
        },
    )


# -----------------------------------------------------------
# 2. Clean data
# -----------------------------------------------------------

@asset(
    ins={"df": AssetIn("raw_spotify_csv")},
    description="Clean raw dataset: missing values, types, filters."
)
def spotify_cleaned(context, df: pd.DataFrame) -> Output[pd.DataFrame]:
    """Clean data: remove nulls, filter zeros, create verdict column."""
    context.log.info(f"Starting with {len(df)} rows")
    
    # Drop rows with missing values
    df = df.dropna()
    context.log.info(f"After dropping nulls: {len(df)} rows")
    
    # Filter out tracks with zero popularity
    df = df[df['popularity'] > 0]
    context.log.info(f"After filtering zero popularity: {len(df)} rows")
    
    # Ensure year column exists
    if 'year' not in df.columns and 'release_date' in df.columns:
        df['year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year
        df = df.dropna(subset=['year'])
    
    df['year'] = df['year'].astype(int)
    
    # Add artist song count feature
    if 'artist_name' in df.columns and 'track_id' in df.columns:
        df['artist_song_count'] = df.groupby('artist_name')['track_id'].transform('count')
    
    # Create verdict column (binary target: popular vs not popular)
    # Using yearly percentile threshold for fairness across years
    yearly_thresholds = df.groupby('year')['popularity'].quantile(
        POPULARITY_THRESHOLD / 100
    ).to_dict()
    
    df['verdict'] = df.apply(
        lambda row: 1 if row['popularity'] >= yearly_thresholds.get(row['year'], POPULARITY_THRESHOLD) else 0,
        axis=1
    )
    
    # Add duration-based features
    if 'duration_ms' in df.columns:
        q1 = df['duration_ms'].quantile(0.25)
        q95 = df['duration_ms'].quantile(0.95)
        df['long_duration'] = (df['duration_ms'] > q95).astype(int)
        df['short_duration'] = (df['duration_ms'] < q1).astype(int)
    
    positive_pct = df['verdict'].mean() * 100
    context.log.info(f"Positive class (popular): {positive_pct:.2f}%")
    
    return Output(
        df,
        metadata={
            "rows": len(df),
            "columns": len(df.columns),
            "positive_class_pct": float(positive_pct),
        },
    )


# -----------------------------------------------------------
# 3. Feature engineering
# -----------------------------------------------------------

@asset(
    ins={"df": AssetIn("spotify_cleaned")},
    description="Feature engineering: encoders, scalers, transformations."
)
def spotify_features(context, df: pd.DataFrame) -> Output[FeatureSet]:
    """Prepare features for modeling: one-hot encode genre, drop unnecessary columns."""
    
    # Columns to drop for modeling
    drop_cols = [
        'popularity', 'verdict',
        'Unnamed: 0', 'artist_name', 'track_name', 'track_id', 'year',
        'release_date'
    ]
    
    # Also drop random columns if they exist
    drop_cols.extend(['random_popularity', 'random_verdict'])
    
    # Drop only columns that exist
    cols_to_drop = [col for col in drop_cols if col in df.columns]
    features = df.drop(columns=cols_to_drop)
    
    # One-hot encode genre if it exists
    if 'genre' in features.columns:
        context.log.info(f"One-hot encoding 'genre' column with {features['genre'].nunique()} unique values")
        one_hot = pd.get_dummies(features['genre'], prefix='genre', dtype=int)
        features = features.drop('genre', axis=1)
        features = pd.concat([features, one_hot], axis=1)
    
    # Get target
    target = df['verdict'].astype(int)
    
    # Sort columns for deterministic order
    features = features.sort_index(axis=1)
    
    context.log.info(f"Features shape: {features.shape}")
    context.log.info(f"Feature columns: {list(features.columns)}")
    
    feature_set = FeatureSet(features=features, target=target)
    
    return Output(
        feature_set,
        metadata={
            "feature_count": len(features.columns),
            "rows": len(features),
            "feature_names": list(features.columns)[:10],  # First 10 features
        },
    )


# -----------------------------------------------------------
# 4. Train/Test split
# -----------------------------------------------------------

@asset(
    ins={"feature_set": AssetIn("spotify_features")},
    description="Split features into X_train, X_test, y_train, y_test."
)
def train_test_split(context, feature_set: FeatureSet) -> Output[Dict[str, Any]]:
    """Split data into train and test sets with stratification."""
    
    X_train, X_test, y_train, y_test = sk_train_test_split(
        feature_set.features,
        feature_set.target,
        test_size=0.2,
        random_state=SEED,
        stratify=feature_set.target,
    )
    
    context.log.info(f"Train set: {len(X_train)} samples")
    context.log.info(f"Test set: {len(X_test)} samples")
    context.log.info(f"Train positive %: {y_train.mean() * 100:.2f}%")
    context.log.info(f"Test positive %: {y_test.mean() * 100:.2f}%")
    
    split_data = {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
    }
    
    return Output(
        split_data,
        metadata={
            "train_rows": len(X_train),
            "test_rows": len(X_test),
            "features": X_train.shape[1],
            "train_positive_pct": float(y_train.mean() * 100),
            "test_positive_pct": float(y_test.mean() * 100),
        },
    )
