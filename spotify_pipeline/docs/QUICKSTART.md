# Quick Start Guide - Spotify Dagster Pipeline

## 🎯 What You Have Now

A simple, working Dagster pipeline that:
1. **Loads** Spotify data from Kaggle
2. **Cleans** the data (removes nulls, filters zeros)
3. **Engineers features** (verdict labels, one-hot encoding)
4. **Splits** into train/test sets
5. **Trains** an XGBoost model
6. **Saves** the model to `models/xgboost_model.pkl`

## 📁 Project Structure

```
spotify_pipeline/
├── src/spotify_pipeline/
│   ├── defs/
│   │   ├── __init__.py         # Pipeline definition
│   │   ├── data_assets.py      # Data loading & preprocessing (5 assets)
│   │   ├── model_assets.py     # Model training
│   │   └── resources.py        # Configuration
│   └── definitions.py          # Entry point
├── data/                       # Output directory (created)
├── models/                     # Models directory (created)
└── pyproject.toml              # Dependencies
```

## 🚀 Quick Start (3 Steps)

### 1. Run Setup Script
```bash
cd spotify_pipeline
./setup.sh
```

### 2. Set Environment Variable (macOS only)
```bash
export DYLD_LIBRARY_PATH=~/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH
```

### 3. Start Dagster
```bash
dg dev
```

Open http://localhost:3000 → Click "Materialize all"

## 📊 What Happens When You Run

```
raw_spotify_csv (downloads from Kaggle)
    ↓
spotify_cleaned (removes nulls, adds verdict column)
    ↓
spotify_features (one-hot encodes genre)
    ↓
train_test_split (80/20 split)
    ↓
xgboost_model (trains & saves to models/)
```

## 🎓 Next Steps

### Add More Models
Edit `src/spotify_pipeline/defs/model_assets.py`:

```python
@asset(ins={"split_data": AssetIn("train_test_split")})
def random_forest_model(context, file_config, split_data):
    # Train Random Forest
    pass
```

### Change Model Parameters
Edit the `xgboost_model` asset in `model_assets.py`:
- `n_estimators`: Number of trees
- `max_depth`: Tree depth
- `scale_pos_weight`: Handle class imbalance

### Customize Paths
Edit `src/spotify_pipeline/defs/__init__.py`:

```python
resources={
    "file_config": FileConfig(
        data_dir="my_data",
        models_dir="my_models",
        spotify_csv_path="/path/to/local/csv"  # Skip Kaggle download
    ),
}
```

### Schedule the Pipeline
Add to `defs/__init__.py`:

```python
from dagster import ScheduleDefinition

daily_schedule = ScheduleDefinition(
    job=define_asset_job("spotify_job", selection="*"),
    cron_schedule="0 0 * * *",  # Daily at midnight
)

defs = Definitions(
    assets=all_assets,
    schedules=[daily_schedule],
    resources=...
)
```

## 🐛 Troubleshooting

### XGBoost Import Error
```bash
brew install libomp
export DYLD_LIBRARY_PATH=~/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH
```

### Pipeline Not Loading
```bash
cd spotify_pipeline
uv run python -c "from spotify_pipeline.definitions import defs; print(defs.assets)"
```

### Check Asset Status
In the Dagster UI (http://localhost:3000):
- Green = Successfully materialized
- Gray = Not materialized yet
- Red = Failed

## 📚 Learn More

- View logs in the Dagster UI for detailed metrics
- Check `models/` for the trained model file
- Modify `POPULARITY_THRESHOLD` in `data_assets.py` to change what counts as "popular"

## 🎉 You're Done!

You now have a production-ready ML pipeline that you can:
- Run on a schedule
- Monitor in the UI
- Version with Git
- Deploy to production (Dagster Cloud, AWS, etc.)
