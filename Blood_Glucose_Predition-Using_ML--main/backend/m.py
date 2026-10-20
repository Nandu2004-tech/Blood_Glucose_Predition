
from pathlib import Path
import json
import warnings

import joblib
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # Save plots without opening a GUI.
import matplotlib.pyplot as plt
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
from sklearn.model_selection import train_test_split, KFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# ==================================================
# 1. PROJECT PATHS AND CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "db" / "DB1.csv"
MODEL_PATH = (
    BASE_DIR / "backend" / "gradient_boosting_regressor_model.pkl"
)
RESULTS_PATH = BASE_DIR / "test_results.csv"
OUTPUT_DIR = BASE_DIR / "output"

METRICS_PATH = OUTPUT_DIR / "model_metrics.json"
PLOT_PATH = OUTPUT_DIR / "actual_vs_predicted.png"

TARGET = "Blood Sugar Levels Hike (%)"
RANDOM_STATE = 42
TEST_SIZE = 0.20


# ==================================================
# 2. LOAD AND VALIDATE DATASET
# ==================================================

def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}"
        )

    data = pd.read_csv(DATA_PATH)
    data.columns = data.columns.astype(str).str.strip()

    if data.columns.duplicated().any():
        raise ValueError("Duplicate column names found in CSV.")

    if TARGET not in data.columns:
        raise ValueError(
            f"Target '{TARGET}' not found. "
            f"Available columns: {data.columns.tolist()}"
        )

    # Convert the target to numeric and remove invalid rows.
    data[TARGET] = pd.to_numeric(data[TARGET], errors="coerce")
    data = data.replace([np.inf, -np.inf], np.nan)
    data = data.dropna(subset=[TARGET]).copy()
    data = data.drop_duplicates().reset_index(drop=True)

    if len(data) < 10:
        raise ValueError(
            f"Only {len(data)} valid rows found. "
            "More data is recommended for reliable evaluation."
        )

    X = data.drop(columns=[TARGET]).copy()
    y = data[TARGET].copy()

    # Entirely empty columns cannot provide useful information.
    empty_columns = X.columns[X.isna().all()].tolist()

    if empty_columns:
        warnings.warn(f"Dropping empty columns: {empty_columns}")
        X = X.drop(columns=empty_columns)

    if X.empty:
        raise ValueError("No usable input features found.")

    print("\n========== DATASET SUMMARY ==========")
    print(f"Dataset: {DATA_PATH}")
    print(f"Rows: {len(data)}")
    print(f"Features: {X.shape[1]}")
    print(f"Target: {TARGET}")
    print("\nColumns:")
    print(X.columns.tolist())
    print("\nTarget summary:")
    print(y.describe())

    return X, y


# ==================================================
# 3. BUILD PREPROCESSING PIPELINE
# ==================================================

def build_model(X):
    categorical_cols = X.select_dtypes(
        include=["object", "category", "bool", "string"]
    ).columns.tolist()

    numeric_cols = [
        col for col in X.columns
        if col not in categorical_cols
    ]

    transformers = []

    if numeric_cols:
        numeric_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median"))
        ])

        transformers.append(
            ("numeric", numeric_pipeline, numeric_cols)
        )

    if categorical_cols:
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

        transformers.append(
            ("categorical", categorical_pipeline, categorical_cols)
        )

    preprocessing = ColumnTransformer(
        transformers=transformers,
        remainder="drop",
    )

    model = Pipeline([
        ("preprocessing", preprocessing),
        (
            "regressor",
            GradientBoostingRegressor(
                n_estimators=150,
                learning_rate=0.05,
                max_depth=3,
                min_samples_leaf=2,
                random_state=RANDOM_STATE,
            ),
        ),
    ])

    print("\nNumeric features:", numeric_cols)
    print("Categorical features:", categorical_cols)

    return model


# ==================================================
# 4. EVALUATION METRICS
# ==================================================

def evaluate(y_true, y_pred):
    mse = mean_squared_error(y_true, y_pred)

    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "MSE": float(mse),
        "RMSE": float(np.sqrt(mse)),
        "R2": (
            float(r2_score(y_true, y_pred))
            if len(y_true) >= 2
            else None
        ),
    }


# ==================================================
# 5. TRAIN AND TEST MODEL
# ==================================================

def train_model():
    X, y = load_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    if len(X_train) < 5 or len(X_test) < 2:
        raise ValueError("Insufficient rows for this train/test split.")

    model = build_model(X_train)

    # Baseline model: always predicts the training-set mean.
    baseline = DummyRegressor(strategy="mean")
    baseline.fit(X_train, y_train)

    baseline_pred = baseline.predict(X_test)
    baseline_metrics = evaluate(y_test, baseline_pred)

    # Cross-validation uses only the training partition.
    folds = min(5, len(X_train))
    cv = KFold(
        n_splits=folds,
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
    )

    cv_metrics = {
        "folds": folds,
        "mean_mae": float(-cv_results["test_mae"].mean()),
        "mean_rmse": float(-cv_results["test_rmse"].mean()),
        "mean_r2": float(cv_results["test_r2"].mean()),
    }

    # Fit final pipeline using training data only.
    model.fit(X_train, y_train)

    # Evaluate on held-out test data.
    predictions = model.predict(X_test)
    model_metrics = evaluate(y_test, predictions)

    print("\n========== MODEL EVALUATION ==========")
    print(f"Training rows: {len(X_train)}")
    print(f"Testing rows: {len(X_test)}")

    print("\nGradient Boosting:")
    for name, value in model_metrics.items():
        print(f"{name:8}: {value}")

    print("\nBaseline:")
    for name, value in baseline_metrics.items():
        print(f"{name:8}: {value}")

    print("\nCross-validation on training set:")
    for name, value in cv_metrics.items():
        print(f"{name:12}: {value}")

    if model_metrics["MAE"] < baseline_metrics["MAE"]:
        print("\nModel has lower test MAE than the baseline.")
    else:
        print(
            "\nWARNING: Model did not outperform the baseline "
            "on test MAE. Investigate data and features."
        )

    # ==============================================
    # 6. SAVE ACTUAL VS PREDICTED RESULTS
    # ==============================================

    results_df = pd.DataFrame({
        "actual_target": y_test.to_numpy(),
        "predicted_target": predictions,
        "absolute_error": np.abs(
            y_test.to_numpy() - predictions
        ),
    })

    # Include original test features for error analysis.
    feature_results = X_test.reset_index(drop=True).copy()
    results_df = pd.concat(
        [feature_results, results_df.reset_index(drop=True)],
        axis=1,
    )

    results_df.to_csv(RESULTS_PATH, index=False)

    print("\nTest predictions saved to:", RESULTS_PATH)

    # ==============================================
    # 7. SAVE ACTUAL VS PREDICTED PLOT
    # ==============================================

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(9, 6))
    plt.scatter(y_test, predictions, alpha=0.75)

    low = min(float(y_test.min()), float(predictions.min()))
    high = max(float(y_test.max()), float(predictions.max()))

    if low == high:
        low -= 1
        high += 1

    plt.plot(
        [low, high],
        [low, high],
        "k--",
        linewidth=2,
        label="Perfect prediction",
    )

    plt.xlabel(f"Actual {TARGET}")
    plt.ylabel(f"Predicted {TARGET}")
    plt.title("Actual vs Predicted — Gradient Boosting")
    plt.legend()
    plt.grid(alpha=0.2)
    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=160)
    plt.close()

    print("Evaluation plot saved to:", PLOT_PATH)

    # ==============================================
    # 8. SAVE MODEL BUNDLE
    # ==============================================

    # Save the complete pipeline so inference repeats the
    # same imputation and categorical encoding as training.
    bundle = {
        "model": model,
        "input_columns": X.columns.tolist(),
        "target_column": TARGET,
        "metrics": model_metrics,
        "baseline_metrics": baseline_metrics,
        "cross_validation": cv_metrics,
        "sklearn_version": sklearn.__version__,
    }

    joblib.dump(bundle, MODEL_PATH)
    print("Model saved to:", MODEL_PATH)

    # ==============================================
    # 9. SAVE METRICS REPORT
    # ==============================================

    report = {
        "target": TARGET,
        "model": "GradientBoostingRegressor",
        "total_rows": int(len(X)),
        "training_rows": int(len(X_train)),
        "testing_rows": int(len(X_test)),
        "features": X.columns.tolist(),
        "test_metrics": model_metrics,
        "baseline_metrics": baseline_metrics,
        "cross_validation": cv_metrics,
        "sklearn_version": sklearn.__version__,
        "note": (
            "Research prototype only; clinical validity "
            "has not been established."
        ),
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4, allow_nan=False)

    print("Metrics report saved to:", METRICS_PATH)
    print("\nTraining completed successfully.")


if __name__ == "__main__":
    train_model()
