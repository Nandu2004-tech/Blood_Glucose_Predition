
"""
Dr. Diabetic — Blood Sugar Hike Prediction
Model training, validation, evaluation, and persistence.

Target:
    Blood Sugar Levels Hike (%)

Run from the project root:
    python backend/model.py
"""

from pathlib import Path
import json
import warnings

import joblib
import numpy as np
import pandas as pd
import sklearn

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import (
    KFold,
    cross_validate,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "db" / "DB1.csv"
MODEL_PATH = (
    Path(__file__).resolve().parent
    / "gradient_boosting_regressor_model.pkl"
)
METRICS_PATH = BASE_DIR / "output" / "model_metrics.json"
PREDICTIONS_PATH = BASE_DIR / "output" / "test_predictions.csv"

TARGET = "Blood Sugar Levels Hike (%)"
RANDOM_STATE = 42
TEST_SIZE = 0.20


# --------------------------------------------------
# 2. LOAD AND VALIDATE DATA
# --------------------------------------------------

def load_dataset():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}\n"
            "Check the location of db/DB1.csv."
        )

    data = pd.read_csv(DATA_PATH)

    if data.empty:
        raise ValueError("The dataset is empty.")

    # Remove whitespace around column names.
    data.columns = data.columns.astype(str).str.strip()

    if data.columns.duplicated().any():
        duplicates = data.columns[data.columns.duplicated()].tolist()
        raise ValueError(f"Duplicate column names found: {duplicates}")

    if TARGET not in data.columns:
        raise ValueError(
            f"Target '{TARGET}' not found.\n"
            f"Available columns: {data.columns.tolist()}"
        )

    # A row without a target cannot be used for supervised training.
    data[TARGET] = pd.to_numeric(data[TARGET], errors="coerce")
    data = data.dropna(subset=[TARGET]).copy()

    # Remove infinite target values.
    data = data[np.isfinite(data[TARGET])].copy()

    # Drop exact duplicate rows.
    original_rows = len(data)
    data = data.drop_duplicates().reset_index(drop=True)
    duplicates_removed = original_rows - len(data)

    if len(data) < 10:
        raise ValueError(
            f"Only {len(data)} valid rows remain. "
            "At least 10 rows are required by this training script; "
            "a larger dataset is strongly recommended."
        )

    X = data.drop(columns=[TARGET]).copy()
    y = data[TARGET].copy()

    if X.shape[1] == 0:
        raise ValueError("No input features were found.")

    # Remove entirely empty columns: their values cannot be imputed.
    empty_columns = X.columns[X.isna().all()].tolist()

    if empty_columns:
        warnings.warn(
            f"Dropping entirely empty columns: {empty_columns}"
        )
        X = X.drop(columns=empty_columns)

    if X.shape[1] == 0:
        raise ValueError("No usable input features remain.")

    # Convert infinity in numeric input columns to missing values.
    for column in X.select_dtypes(include=np.number).columns:
        X[column] = X[column].replace(
            [np.inf, -np.inf], np.nan
        )

    print("\n" + "=" * 55)
    print("DATASET SUMMARY")
    print("=" * 55)
    print(f"Dataset path:        {DATA_PATH}")
    print(f"Valid rows:          {len(X)}")
    print(f"Input features:      {X.shape[1]}")
    print(f"Duplicates removed:  {duplicates_removed}")
    print(f"Target:              {TARGET}")
    print("\nTarget statistics:")
    print(y.describe().round(4))
    print("\nInput columns:")
    print(X.columns.tolist())

    return X, y


# --------------------------------------------------
# 3. BUILD PREPROCESSING AND MODEL PIPELINE
# --------------------------------------------------

def build_model(X):
    categorical_cols = X.select_dtypes(
        include=["object", "category", "bool", "string"]
    ).columns.tolist()

    numeric_cols = [
        column for column in X.columns
        if column not in categorical_cols
    ]

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
    ])

    categorical_pipeline = Pipeline([
        (
            "imputer",
            SimpleImputer(strategy="most_frequent"),
        ),
        (
            "encoder",
            OneHotEncoder(handle_unknown="ignore"),
        ),
    ])

    transformers = []

    if numeric_cols:
        transformers.append(
            ("numeric", numeric_pipeline, numeric_cols)
        )

    if categorical_cols:
        transformers.append(
            ("categorical", categorical_pipeline, categorical_cols)
        )

    preprocessing = ColumnTransformer(
        transformers=transformers,
        remainder="drop",
    )

    regressor = GradientBoostingRegressor(
        n_estimators=150,
        learning_rate=0.05,
        max_depth=3,
        min_samples_leaf=2,
        loss="squared_error",
        random_state=RANDOM_STATE,
    )

    pipeline = Pipeline([
        ("preprocessing", preprocessing),
        ("regressor", regressor),
    ])

    print("\nPreprocessing configuration:")
    print(f"Numeric columns:     {numeric_cols}")
    print(f"Categorical columns: {categorical_cols}")

    return pipeline


# --------------------------------------------------
# 4. EVALUATION HELPERS
# --------------------------------------------------

def calculate_metrics(y_true, predictions):
    mse = mean_squared_error(y_true, predictions)

    return {
        "MAE": float(mean_absolute_error(y_true, predictions)),
        "MSE": float(mse),
        "RMSE": float(np.sqrt(mse)),
        "R2": (
            float(r2_score(y_true, predictions))
            if len(y_true) >= 2
            else None
        ),
    }


# --------------------------------------------------
# 5. TRAIN, VALIDATE, AND SAVE
# --------------------------------------------------

def train_model():
    X, y = load_dataset()

    # Keep the test set untouched until final evaluation.
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    if len(X_train) < 5 or len(X_test) < 2:
        raise ValueError(
            "Not enough training/test rows. "
            "Use a larger dataset or revise TEST_SIZE."
        )

    model = build_model(X_train)

    # Baseline: predicts the training target mean.
    baseline = DummyRegressor(strategy="mean")
    baseline.fit(X_train, y_train)
    baseline_predictions = baseline.predict(X_test)
    baseline_metrics = calculate_metrics(
        y_test, baseline_predictions
    )

    # Cross-validation is performed on training data only.
    cv_splits = min(5, len(X_train))

    if cv_splits >= 2:
        cv = KFold(
            n_splits=cv_splits,
            shuffle=True,
            random_state=RANDOM_STATE,
        )

        cv_results = cross_validate(
            model,
            X_train,
            y_train,
            cv=cv,
            scoring={
                "mae": "neg_mean_absolute_error",
                "rmse": "neg_root_mean_squared_error",
                "r2": "r2",
            },
            return_train_score=False,
            error_score="raise",
        )

        cv_metrics = {
            "folds": cv_splits,
            "mae_mean": float(
                -cv_results["test_mae"].mean()
            ),
            "mae_std": float(
                cv_results["test_mae"].std()
            ),
            "rmse_mean": float(
                -cv_results["test_rmse"].mean()
            ),
            "r2_mean": float(
                cv_results["test_r2"].mean()
            ),
        }
    else:
        cv_metrics = None

    # Fit on the full training partition.
    model.fit(X_train, y_train)

    # Evaluate once on the held-out test partition.
    predictions = model.predict(X_test)
    model_metrics = calculate_metrics(y_test, predictions)

    print("\n" + "=" * 55)
    print("MODEL EVALUATION")
    print("=" * 55)
    print(f"Training rows: {len(X_train)}")
    print(f"Testing rows:  {len(X_test)}")

    print("\nBaseline (mean predictor):")
    for metric, value in baseline_metrics.items():
        print(f"{metric:8}: {value}")

    print("\nGradient Boosting:")
    for metric, value in model_metrics.items():
        print(f"{metric:8}: {value}")

    if cv_metrics:
        print("\nTraining-set cross-validation:")
        for metric, value in cv_metrics.items():
            print(f"{metric:12}: {value}")

    # The model should outperform the baseline to demonstrate
    # predictive value. This comparison alone does not prove
    # clinical usefulness or generalization to new populations.
    if model_metrics["MAE"] < baseline_metrics["MAE"]:
        print("\nBaseline comparison: lower test MAE than baseline.")
    else:
        print(
            "\nWarning: model did not improve on baseline test MAE. "
            "Review features, target quality, and validation design."
        )

    # Store predictions for further error analysis.
    output_dir = BASE_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    prediction_report = pd.DataFrame({
        "actual_target": y_test.to_numpy(),
        "predicted_target": predictions,
        "absolute_error": np.abs(
            y_test.to_numpy() - predictions
        ),
    })

    prediction_report.to_csv(
        PREDICTIONS_PATH,
        index=False,
    )

    report = {
        "target": TARGET,
        "dataset_path": str(DATA_PATH),
        "total_rows": int(len(X)),
        "training_rows": int(len(X_train)),
        "testing_rows": int(len(X_test)),
        "features": X.columns.tolist(),
        "model": "GradientBoostingRegressor",
        "sklearn_version": sklearn.__version__,
        "random_state": RANDOM_STATE,
        "test_metrics": model_metrics,
        "baseline_test_metrics": baseline_metrics,
        "cross_validation": cv_metrics,
        "note": (
            "Research prototype metrics only. "
            "Clinical validity has not been established."
        ),
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, allow_nan=False)

    # Save preprocessing and estimator together so inference
    # can use the same transformations as training.
    model_bundle = {
        "model": model,
        "input_columns": X.columns.tolist(),
        "target_column": TARGET,
        "metrics": model_metrics,
        "baseline_metrics": baseline_metrics,
        "sklearn_version": sklearn.__version__,
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(model_bundle, MODEL_PATH)

    print("\n" + "=" * 55)
    print("SAVED OUTPUTS")
    print("=" * 55)
    print(f"Model bundle:      {MODEL_PATH}")
    print(f"Metrics report:    {METRICS_PATH}")
    print(f"Test predictions:  {PREDICTIONS_PATH}")
    print("\nTraining completed.")


if __name__ == "__main__":
    train_model()
