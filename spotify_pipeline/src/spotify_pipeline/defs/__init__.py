"""Dagster definitions for the Spotify pipeline."""

from dagster import Definitions, load_assets_from_modules

from . import data_assets, model_assets
from .resources import FileConfig


# Load all assets
all_assets = load_assets_from_modules([data_assets, model_assets])

# Define the pipeline
defs = Definitions(
    assets=all_assets,
    resources={
        "file_config": FileConfig(
            data_dir="data",
            models_dir="models",
        ),
    },
)
