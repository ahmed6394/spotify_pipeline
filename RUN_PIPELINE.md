# Running the Spotify Pipeline

## Quick Start

1. **Ensure your CSV is in place**:
   ```bash
   ls data/spotify_data.csv  # Should exist
   ```

2. **Start the pipeline**:
   ```bash
   cd spotify_pipeline
   ./start.sh
   ```
   
   Or manually:
   ```bash
   export DYLD_LIBRARY_PATH=~/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH
   uv run dagster dev
   ```

3. **Open the UI**: http://localhost:3000

4. **Click "Materialize all"** to run the entire pipeline

## What the Pipeline Does

```
1. raw_spotify_csv       → Loads data/spotify_data.csv
2. spotify_cleaned       → Cleans data, creates verdict label
3. spotify_features      → One-hot encodes genre, prepares features
4. train_test_split      → Splits into train (80%) / test (20%)
5. xgboost_model         → Trains model, saves to models/xgboost_model.pkl
6. model_predictions     → Makes predictions on test data, saves to models/test_predictions.csv
```

## Output

- **Trained Model**: `models/xgboost_model.pkl`
- **Test Predictions**: `models/test_predictions.csv` (with actual, predicted, probabilities)
- **Metrics**: Visible in Dagster UI (accuracy, precision, recall)

## Load the Trained Model

```python
import pickle

with open('models/xgboost_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Use for predictions
predictions = model.predict(X_new)
```
