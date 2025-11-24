"""Model training and evaluation assets."""

from pathlib import Path
from typing import Any, Dict
import pickle

import pandas as pd
from dagster import AssetIn, Output, asset
from sklearn.metrics import classification_report, accuracy_score
from xgboost import XGBClassifier

SEED = 42


@asset(
    ins={"split_data": AssetIn("train_test_split")},
    description="Train XGBoost model on Spotify data",
)
def xgboost_model(context, split_data: Dict[str, Any]) -> Output[Dict[str, Any]]:
    """Train an XGBoost classifier and save to disk."""
    X_train = split_data["X_train"]
    y_train = split_data["y_train"]
    X_test = split_data["X_test"]
    y_test = split_data["y_test"]
    
    context.log.info(f"Training XGBoost with {X_train.shape[0]} samples, {X_train.shape[1]} features")
    
    # Train model with parameters from notebook
    model = XGBClassifier(
        random_state=SEED,
        objective='binary:logistic',
        colsample_bytree=0.8,
        learning_rate=0.1,
        max_depth=6,
        n_estimators=600,
        subsample=0.9,
        scale_pos_weight=30,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions, output_dict=True)
    
    # Save model
    file_config = context.resources.file_config
    models_dir = file_config.models_path
    models_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / "xgboost_model.pkl"
    
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    
    context.log.info(f"Model saved to: {model_path}")
    context.log.info(f"Accuracy: {accuracy:.4f}")
    
    return Output(
        {
            "model_path": str(model_path),
            "accuracy": accuracy,
            "classification_report": report,
        },
        metadata={
            "accuracy": accuracy,
            "recall_class_1": report["1"]["recall"],
            "precision_class_1": report["1"]["precision"],
            "model_path": str(model_path),
        },
    )
