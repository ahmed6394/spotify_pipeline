"""Resources configuration for the Spotify pipeline."""

from dagster import ConfigurableResource
from pathlib import Path


class FileConfig(ConfigurableResource):
    """Configuration for file paths in the pipeline."""
    
    # Path to the Spotify CSV (optional - will look in data/ folder)
    spotify_csv_path: str | None = None
    
    # Output directories
    data_dir: str = "data"
    models_dir: str = "models"
    
    @property
    def data_path(self) -> Path:
        """Get the data directory as a Path object."""
        return Path(self.data_dir).expanduser().resolve()
    
    @property
    def models_path(self) -> Path:
        """Get the models directory as a Path object."""
        return Path(self.models_dir).expanduser().resolve()
