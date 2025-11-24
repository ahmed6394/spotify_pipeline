# src/spotify_pipeline/defs/data_assets.py

"""Dagster assets that reproduce the loading, cleaning, and feature
engineering steps from the exploratory Spotify notebook.

Each asset keeps the heavy Pandas/Numpy work close to the notebook while
maintaining clear orchestration boundaries for Dagster.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import pandas as pd
from dagster import AssetIn, Output, asset
from sklearn.model_selection import train_test_split as sk_train_test_split


POPULARITY_THRESHOLD = 85
SEED = 42


@dataclass
class FeatureSet:
    """Container passed between the feature engineering and split assets."""

    features: pd.DataFrame
    target: pd.Series


def _resolve_csv_path(file_config) -> Path:
    """Figure out where the CSV lives (resource override or Kaggle download)."""
    
    if file_config.spotify_csv_path:
        return Path(file_config.spotify_csv_path).expanduser().resolve()

    # Fallback to KaggleHub download
    try:
        import kagglehub
    except ImportError as exc:
        raise RuntimeError(
            "kagglehub is required to download the Spotify dataset. "
            "Install it or provide `file_config.spotify_csv_path`."
        ) from exc

    dataset_dir = Path(kagglehub.dataset_download("amitanshjoshi/spotify-1million-tracks"))
    csv_path = dataset_dir / "spotify_data.csv"
    return csv_path


# -----------------------------------------------------------
# 1. Load raw data
# -----------------------------------------------------------

@asset(description="Load the raw Spotify CSV from local disk or Kaggle")
def raw_spotify_csv(context) -> Output[pd.DataFrame]:
    file_config = context.resources.file_config
    csv_path = _resolve_csv_path(file_config)
    context.log.info(f"Loading CSV from: {csv_path}")
    df = pd.read_csv(csv_path)
    return Output(
        df,
        metadata={
            "rows": df.shape[0],
            "columns": df.shape[1],
            "source": str(csv_path),
        },
    )


def _ensure_year_column(df: pd.DataFrame) -> pd.DataFrame:
    if "year" in df.columns and df["year"].notna().all():
        return df

    if "release_date" not in df.columns:
        raise ValueError("Dataset missing both 'year' and 'release_date' columns.")

    df = df.copy()
    df["year"] = pd.to_datetime(df["release_date"], errors="coerce").dt.year
    return df.dropna(subset=["year"])


def _add_duration_flags(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    duration = df["duration_ms"]
    q1 = duration.quantile(0.25)
    q95 = duration.quantile(0.95)
    df["long_duration"] = (duration > q95).astype(int)
    df["short_duration"] = (duration < q1).astype(int)
    return df


def _build_verdict_column(df: pd.DataFrame) -> pd.Series:
    yearly_thresholds = (
        df.groupby("year")["popularity"].quantile(POPULARITY_THRESHOLD / 100).to_dict()
    )
    return df.apply(
        lambda row: int(
            row["popularity"]
            >= yearly_thresholds.get(row["year"], POPULARITY_THRESHOLD)
        ),
        axis=1,
    )


# -----------------------------------------------------------
# 2. Clean data
# -----------------------------------------------------------

@asset(
    ins={"df": AssetIn("raw_spotify_csv")},
    description="Drop nulls/zeros, derive verdict & helper features",
)
def spotify_cleaned(df: pd.DataFrame) -> Output[pd.DataFrame]:
    working_df = df.copy()
    working_df = working_df.dropna()
    working_df = working_df[working_df["popularity"] > 0]
    working_df = _ensure_year_column(working_df)

    if {"artist_name", "track_id"}.issubset(working_df.columns):
        working_df["artist_song_count"] = (
            working_df.groupby("artist_name")["track_id"].transform("count")
        )

    working_df["verdict"] = _build_verdict_column(working_df)
    working_df = _add_duration_flags(working_df)

    return Output(
        working_df,
        metadata={
            "rows": working_df.shape[0],
            "columns": working_df.shape[1],
            "positive_class_pct": float(working_df["verdict"].mean() * 100),
        },
    )


def _hot_encode_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    if column_name not in df.columns:
        return df
    one_hot = pd.get_dummies(df[column_name], prefix=column_name, dtype=int)
    return pd.concat([df.drop(columns=[column_name]), one_hot], axis=1)


def _sanitize_model_frame(df: pd.DataFrame) -> FeatureSet:
    drop_candidates = [
        "popularity",
        "random_popularity",
        "random_verdict",
        "verdict",
        "Unnamed: 0",
        "artist_name",
        "track_name",
        "track_id",
        "year",
        "release_date",
    ]

    features = df.drop(columns=[c for c in drop_candidates if c in df.columns])
    target = df["verdict"].astype(int)

    if "genre" in features.columns:
        features = _hot_encode_column(features, "genre")

    # Ensure deterministic column order for downstream models.
    features = features.sort_index(axis=1)

    return FeatureSet(features=features, target=target)


# -----------------------------------------------------------
# 3. Feature engineering
# -----------------------------------------------------------

@asset(
    ins={"df": AssetIn("spotify_cleaned")},
    description="One-hot encode genre & return modeling matrix",
)
def spotify_features(df: pd.DataFrame) -> Output[FeatureSet]:
    feature_set = _sanitize_model_frame(df)
    return Output(
        feature_set,
        metadata={
            "feature_columns": len(feature_set.features.columns),
            "rows": feature_set.features.shape[0],
        },
    )


# -----------------------------------------------------------
# 4. Train/Test split
# -----------------------------------------------------------

@asset(
    ins={"feature_set": AssetIn("spotify_features")},
    description="Split features into X_train, X_test, y_train, y_test",
)
def train_test_split(feature_set: FeatureSet) -> Output[Dict[str, Any]]:
    X_train, X_test, y_train, y_test = sk_train_test_split(
        feature_set.features,
        feature_set.target,
        test_size=0.2,
        random_state=SEED,
        stratify=feature_set.target,
    )

    split_payload: Dict[str, Any] = {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
    }

    return Output(
        split_payload,
        metadata={
            "train_rows": X_train.shape[0],
            "test_rows": X_test.shape[0],
            "features": X_train.shape[1],
        },
    )
