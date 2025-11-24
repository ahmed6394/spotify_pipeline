"""Dagster definitions for the Spotify pipeline - assets folder."""

from pathlib import Path
from dagster import Definitions, load_assets_from_modules, FilesystemIOManager

from . import data_assets, model_assets
from .resources import FileConfig


# Load all assets
all_assets = load_assets_from_modules([data_assets, model_assets])

# Get the storage path - try multiple locations
possible_storage_paths = [
    Path("data/dagster_storage"),
    Path("../data/dagster_storage"),
    Path(__file__).parent.parent.parent.parent.parent / "data" / "dagster_storage",
]

storage_dir = None
for path in possible_storage_paths:
    resolved = path.resolve()
    if resolved.parent.exists():
        storage_dir = resolved
        storage_dir.mkdir(parents=True, exist_ok=True)
        break

if storage_dir is None:
    storage_dir = Path("dagster_storage")

# Define the pipeline
defs = Definitions(
    assets=all_assets,
    resources={
        "file_config": FileConfig(
            data_dir="data",
            models_dir="models",
        ),
        "io_manager": FilesystemIOManager(base_dir=str(storage_dir)),
    },
)
