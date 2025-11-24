# 🎸 Spotify Popularity Prediction - Complete Setup

## 📁 Project Structure

```
Spotify/
├── data/
│   ├── spotify_data.csv              # Original dataset
│   └── dagster_output/               # Readable pipeline outputs
│       ├── 01_raw_data.csv
│       ├── 02_cleaned_data.csv
│       ├── 03_features.csv
│       ├── 03_target.csv
│       ├── 03_feature_names.txt
│       ├── 04_X_train.csv
│       ├── 04_X_test.csv
│       ├── 04_y_train.csv
│       └── 04_y_test.csv
├── models/
│   ├── xgboost_model.pkl            # Trained model
│   ├── model_metadata.json          # Model performance info
│   └── test_predictions.csv         # Test set predictions
└── spotify_pipeline/
    ├── api.py                       # FastAPI application
    ├── test_api.py                  # Python API test script
    ├── test_api_curl.sh            # Curl API test script
    ├── start.sh                     # Start Dagster UI
    ├── start_api.sh                # Start FastAPI server
    ├── API_README.md               # API documentation
    └── src/
        └── spotify_pipeline/
            ├── definitions.py
            └── assets/
                ├── __init__.py
                ├── data_assets.py   # Data pipeline (4 assets)
                ├── model_assets.py  # Model training (2 assets)
                └── resources.py
```

## 🚀 Complete Workflow

### Step 1: Train the Model with Dagster

```bash
cd /Users/zerfaouiabdallah/Spotify/spotify_pipeline
./start.sh
```

- Open http://localhost:3000
- Click **"Materialize all"** to run the complete pipeline
- Wait for all 6 assets to complete (green checkmarks)

**Assets created:**
1. `raw_spotify_csv` - Load data
2. `spotify_cleaned` - Clean and create verdict
3. `spotify_features` - Feature engineering
4. `train_test_split` - Split data
5. `xgboost_model` - Train model
6. `model_predictions` - Generate predictions

### Step 2: Start the FastAPI Server

Open a new terminal:

```bash
cd /Users/zerfaouiabdallah/Spotify/spotify_pipeline
./start_api.sh
```

- API available at: http://localhost:8000
- Interactive docs: http://localhost:8000/docs

### Step 3: Test the API

**Option A: Python Script**
```bash
uv run python test_api.py
```

**Option B: Curl Script**
```bash
./test_api_curl.sh
```

**Option C: Manual curl**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "acousticness": 0.1,
    "danceability": 0.7,
    "duration_ms": 200000,
    "energy": 0.8,
    "explicit": 0,
    "instrumentalness": 0.0,
    "key": 5,
    "liveness": 0.1,
    "loudness": -5.0,
    "mode": 1,
    "speechiness": 0.05,
    "tempo": 120.0,
    "time_signature": 4,
    "valence": 0.6,
    "artist_song_count": 10,
    "genre": "pop"
  }'
```

**Option D: Interactive Swagger UI**
- Visit http://localhost:8000/docs
- Click on `/predict` endpoint
- Click "Try it out"
- Modify the example JSON
- Click "Execute"

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/model-info` | Model metadata and performance |
| GET | `/features` | List of required features |
| POST | `/predict` | Single prediction |
| POST | `/predict-batch` | Batch predictions |

## 📊 Pipeline Output Files

All pipeline outputs are saved in human-readable formats:

### Data Pipeline Outputs (`data/dagster_output/`)
- **01_raw_data.csv** - Original CSV data
- **02_cleaned_data.csv** - After cleaning + verdict column
- **03_features.csv** - Feature matrix (one-hot encoded)
- **03_target.csv** - Target labels
- **03_feature_names.txt** - List of feature names
- **04_X_train.csv** - Training features
- **04_X_test.csv** - Test features
- **04_y_train.csv** - Training labels
- **04_y_test.csv** - Test labels

### Model Outputs (`models/`)
- **xgboost_model.pkl** - Trained XGBoost model
- **model_metadata.json** - Hyperparameters and performance metrics
- **test_predictions.csv** - Predictions with probabilities

## 🔧 Configuration

### Model Hyperparameters
```python
n_estimators = 600
max_depth = 6
learning_rate = 0.1
colsample_bytree = 0.8
subsample = 0.9
scale_pos_weight = 30  # Handle class imbalance
```

### Pipeline Constants
```python
POPULARITY_THRESHOLD = 85  # Yearly percentile
SEED = 42  # Random seed
TEST_SIZE = 0.2  # 80/20 split
```

## 🐛 Troubleshooting

### Issue: "Model not found"
**Solution:** Run the Dagster pipeline first to train the model
```bash
./start.sh
# Then materialize all assets in UI
```

### Issue: "Feature names not found"
**Solution:** Complete the full pipeline run to generate all output files

### Issue: XGBoost library error on macOS
**Solution:** The startup scripts automatically set `DYLD_LIBRARY_PATH`
```bash
export DYLD_LIBRARY_PATH=~/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH
```

### Issue: Port already in use
**Solution:** Change the port in the startup script or kill the process
```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>
```

## 📦 Dependencies

Core dependencies (automatically installed):
- `dagster==1.12.3` - Pipeline orchestration
- `dagster-webserver==1.12.3` - UI server
- `xgboost>=3.1.1` - ML model
- `scikit-learn>=1.7.2` - ML utilities
- `pandas>=2.3.3` - Data manipulation
- `fastapi>=0.115.0` - API framework
- `uvicorn>=0.32.0` - ASGI server

## 🎯 Quick Reference Commands

```bash
# Install dependencies
uv sync

# Start Dagster UI
./start.sh

# Start FastAPI server
./start_api.sh

# Test API (Python)
uv run python test_api.py

# Test API (curl)
./test_api_curl.sh

# Check pipeline status
uv run python -c "from spotify_pipeline.definitions import defs; print(f'Assets: {len(defs.assets)}')"

# Check API health
curl http://localhost:8000/health
```

## 📈 Model Performance

The model's performance metrics are available at:
- **API endpoint:** http://localhost:8000/model-info
- **JSON file:** `models/model_metadata.json`

Typical metrics:
- Overall accuracy: ~85-90%
- Precision/Recall for both classes
- Training/Test sample counts
- Number of features used

## 🎵 Example Prediction

**Input:**
```json
{
  "acousticness": 0.1,
  "danceability": 0.7,
  "energy": 0.8,
  "genre": "pop",
  "tempo": 120.0,
  ...
}
```

**Output:**
```json
{
  "prediction": 1,
  "probability_not_popular": 0.15,
  "probability_popular": 0.85,
  "confidence": 0.85,
  "verdict": "Popular"
}
```

## 📚 Additional Resources

- **Dagster Docs:** https://docs.dagster.io
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **XGBoost Docs:** https://xgboost.readthedocs.io
- **API README:** See `API_README.md` for detailed API documentation
- **Pipeline README:** See `RUN_PIPELINE.md` for pipeline details

---

**Created:** November 2025  
**Project:** Spotify Track Popularity Prediction  
**Stack:** Dagster + XGBoost + FastAPI
