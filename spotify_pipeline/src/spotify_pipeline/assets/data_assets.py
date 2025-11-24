# src/spotify_pipeline/assets/data_assets.py

"""
Assets responsible for:
- Loading the raw Kaggle CSV
- Cleaning / preprocessing
- Feature engineering
- Train/test splitting

These assets only orchestrate. 
All heavy logic lives in spotify_pipeline/ml_core/.
"""

from dagster import asset, Output, AssetIn

# -----------------------------------------------------------
# 1. Load raw data
# -----------------------------------------------------------

@asset(
    required_resource_keys={"file_config"},
    description="Load the raw Spotify CSV from local disk or S3."
)
def raw_spotify_csv(context):
    # returns a pandas DataFrame
    pass


# -----------------------------------------------------------
# 2. Clean data
# -----------------------------------------------------------

@asset(
    ins={"df": AssetIn("raw_spotify_csv")},
    description="Clean raw dataset: missing values, types, filters."
)
def spotify_cleaned(df):
    pass


# -----------------------------------------------------------
# 3. Feature engineering
# -----------------------------------------------------------

@asset(
    ins={"df": AssetIn("spotify_cleaned")},
    description="Feature engineering: encoders, scalers, transformations."
)
def spotify_features(df):
    pass


# -----------------------------------------------------------
# 4. Train/Test split
# -----------------------------------------------------------

@asset(
    ins={"df": AssetIn("spotify_features")},
    description="Split features into X_train, X_test, y_train, y_test."
)
def train_test_split(df):
    # return a dict or custom object that downstream assets can consume
    pass
