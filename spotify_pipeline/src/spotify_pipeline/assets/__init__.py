"""Dagster definitions for the Spotify pipeline - assets folder."""

from pathlib import Path
from dagster import Definitions, load_assets_from_modules, FilesystemIOManager

from . import data_assets, model_assets
from .resources import FileConfig


def _find_project_root() -> Path:
    """Find the Spotify project root directory."""
    current = Path.cwd()
    
    # Try to find Spotify folder
    for parent in [current, current.parent, current.parent.parent]:
        if parent.name == "Spotify" or (parent / "data").exists():
            return parent
    
    return current.parent if current.name == "spotify_pipeline" else current


# Load all assets
all_assets = load_assets_from_modules([data_assets, model_assets])

# Get the storage path
project_root = _find_project_root()
storage_dir = project_root / "data" / "dagster_storage"
storage_dir.mkdir(parents=True, exist_ok=True)

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
