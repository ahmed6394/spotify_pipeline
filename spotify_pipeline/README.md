# Spotify Dagster Pipeline

A simple Dagster pipeline for training a Spotify track popularity prediction model.

## Project Structure

```
spotify_pipeline/
├── src/spotify_pipeline/
│   ├── defs/
│   │   ├── __init__.py          # Pipeline definitions
│   │   ├── data_assets.py       # Data loading, cleaning, feature engineering
│   │   ├── model_assets.py      # Model training
│   │   └── resources.py         # Configuration
│   └── definitions.py           # Entry point
├── data/                        # Data output directory
├── models/                      # Trained models directory
└── pyproject.toml
```

## Getting started

### Prerequisites

**macOS users**: Install OpenMP for XGBoost:
```bash
brew install libomp

# If you have Homebrew in a custom location, set this environment variable:
export DYLD_LIBRARY_PATH=~/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH
# Or add it to your ~/.zshrc to make it permanent:
echo 'export DYLD_LIBRARY_PATH=~/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH' >> ~/.zshrc
```

### Installing dependencies

**Option 1: uv** (Recommended)

Ensure [`uv`](https://docs.astral.sh/uv/) is installed following their [official documentation](https://docs.astral.sh/uv/getting-started/installation/).

Create a virtual environment, and install the required dependencies using _sync_:

```bash
uv sync
```

Then, activate the virtual environment:

| OS | Command |
| --- | --- |
| MacOS | ```source .venv/bin/activate``` |
| Windows | ```.venv\Scripts\activate``` |

**Option 2: pip**

Install the python dependencies with [pip](https://pypi.org/project/pip/):

```bash
python3 -m venv .venv
```

Then activate the virtual environment:

| OS | Command |
| --- | --- |
| MacOS | ```source .venv/bin/activate``` |
| Windows | ```.venv\Scripts\activate``` |

Install the required dependencies:

```bash
pip install -e ".[dev]"
```

### Running Dagster

Start the Dagster UI web server:

```bash
dg dev
```

Open http://localhost:3000 in your browser to see the project.

## Pipeline Assets

The pipeline consists of 5 assets that run in sequence:

1. **raw_spotify_csv** - Downloads and loads Spotify data from Kaggle
2. **spotify_cleaned** - Cleans data (removes nulls, filters zero popularity, creates verdict)
3. **spotify_features** - Engineers features (one-hot encodes genre, prepares for modeling)
4. **train_test_split** - Splits data into train/test sets (80/20)
5. **xgboost_model** - Trains XGBoost classifier and saves to `models/xgboost_model.pkl`

## Running the Pipeline

### Via UI (Recommended)

1. Start Dagster: `dg dev`
2. Open http://localhost:3000
3. Click "Materialize all" to run the entire pipeline

### Via Command Line

Materialize all assets:
```bash
uv run dagster asset materialize --select '*'
```

Or run specific parts:
```bash
# Just data preparation
uv run dagster asset materialize --select raw_spotify_csv+

# Train model only
uv run dagster asset materialize --select xgboost_model
```

## Output

- **Models**: Saved to `models/xgboost_model.pkl`
- **Logs**: Check the Dagster UI for metrics (accuracy, precision, recall)

## Learn more

To learn more about this template and Dagster in general:

- [Dagster Documentation](https://docs.dagster.io/)
- [Dagster University](https://courses.dagster.io/)
- [Dagster Slack Community](https://dagster.io/slack)
