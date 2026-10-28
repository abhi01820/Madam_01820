"""Synthetic dataset generator, EDA, and model training pipeline for HealthRisk AI.

Reproducibly generates synthetic cardiometabolic training data, executes EDA,
builds a scikit-learn Pipeline with ColumnTransformer (zero data leakage),
evaluates Logistic Regression vs Random Forest Classifier, and exports the
best model artifact with training metadata to models/risk_classifier.joblib.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
import joblib

# Paths relative to project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
DATA_PATH = DATA_DIR / "healthrisk_ai_synthetic_demo.csv"
MODEL_PATH = MODELS_DIR / "risk_classifier.joblib"
METRICS_PATH = MODELS_DIR / "model_metrics.json"

RANDOM_STATE = 42

# Define target labels
CLASS_NAMES = [
    "Lower synthetic risk category",
    "Moderate synthetic risk category",
    "Higher synthetic risk category"
]


def generate_synthetic_dataset(n_samples: int = 2500, random_seed: int = RANDOM_STATE) -> pd.DataFrame:
    """Generate reproducible synthetic health data.
    
    Synthesizes clinical measurements (demographics, blood pressure, lipids, glucose,
    lifestyle factors) and assigns artificial composite risk categories based on
    established multi-factorial cardiometabolic risk scoring rubrics.
    
    NOTE: Labels are artificial categories for education and demonstration,
    NOT clinical diagnoses or real disease probabilities.
    """
    np.random.seed(random_seed)

    # Demographics & Anthropometrics
    age = np.random.randint(20, 80, size=n_samples)
    sex = np.random.choice(["Male", "Female"], size=n_samples, p=[0.50, 0.50])
    
    # Height (cm) & Weight (kg)
    height_cm = np.where(
        sex == "Male",
        np.random.normal(172, 7.5, size=n_samples),
        np.random.normal(159, 6.8, size=n_samples)
    ).clip(140, 200)

    # Weight loosely correlated with height
    weight_kg = (
        (height_cm - 100) * 0.9 + np.random.normal(10, 14, size=n_samples)
    ).clip(42, 135)

    bmi = (weight_kg / ((height_cm / 100.0) ** 2)).round(2)
    waist_cm = (bmi * 2.8 + np.random.normal(8, 6, size=n_samples)).clip(60, 135).round(1)

    # Blood Pressure (correlated sys and dia)
    systolic_bp = (
        110 + (age - 20) * 0.45 + (bmi - 22).clip(0, 30) * 1.1 + np.random.normal(0, 12, size=n_samples)
    ).clip(85, 205).round(1)
    
    diastolic_bp = (
        0.52 * systolic_bp + 15 + np.random.normal(0, 6, size=n_samples)
    ).clip(55, 125).round(1)

    resting_heart_rate = np.random.normal(74, 9, size=n_samples).clip(48, 115).round(1)

    # Lipid profile (mg/dL)
    cholesterol_total = (
        160 + (age - 20) * 0.5 + (bmi - 22).clip(0, 30) * 1.5 + np.random.normal(0, 26, size=n_samples)
    ).clip(110, 340).round(1)

    cholesterol_hdl = np.where(
        sex == "Female",
        np.random.normal(55, 10, size=n_samples),
        np.random.normal(46, 9, size=n_samples)
    ).clip(25, 85).round(1)

    triglycerides = (
        110 + (bmi - 22).clip(0, 30) * 3.2 + np.random.normal(0, 45, size=n_samples)
    ).clip(60, 480).round(1)

    cholesterol_ldl = (cholesterol_total - cholesterol_hdl - (triglycerides / 5.0)).clip(45, 230).round(1)

    # Glycemic markers
    fasting_glucose = (
        85 + (bmi - 22).clip(0, 30) * 1.3 + (age - 20) * 0.25 + np.random.normal(0, 18, size=n_samples)
    ).clip(65, 260).round(1)

    hba1c = (
        4.6 + (fasting_glucose - 70) * 0.028 + np.random.normal(0, 0.35, size=n_samples)
    ).clip(4.4, 11.5).round(2)

    # Lifestyle factors
    physical_activity_min_per_week = np.random.choice(
        [0, 60, 120, 180, 240, 300, 360],
        size=n_samples,
        p=[0.18, 0.22, 0.24, 0.16, 0.10, 0.06, 0.04]
    )
    sleep_hours = np.random.normal(7.1, 1.1, size=n_samples).clip(4.0, 10.0).round(1)
    water_liters = np.random.normal(2.4, 0.7, size=n_samples).clip(0.8, 5.0).round(1)
    smoking_status = np.random.choice(["Never", "Former", "Current"], size=n_samples, p=[0.62, 0.22, 0.16])
    alcohol_frequency = np.random.choice(["Never", "Occasional", "Frequent"], size=n_samples, p=[0.52, 0.36, 0.12])
    fruit_veg_servings = np.random.randint(0, 8, size=n_samples)
    sugary_drinks_per_week = np.random.randint(0, 15, size=n_samples)
    family_history_diabetes = np.random.choice([0, 1], size=n_samples, p=[0.68, 0.32])
    family_history_heart_disease = np.random.choice([0, 1], size=n_samples, p=[0.72, 0.28])

    # Optional renal/liver values
    serum_creatinine = np.random.normal(0.95, 0.2, size=n_samples).clip(0.5, 2.2).round(2)
    alt_sgpt = np.random.normal(28, 12, size=n_samples).clip(10, 95).round(1)

    # Construct Composite Risk Scoring Formula
    # Documented Rubric:
    # +2 for Systolic >= 140 or Diastolic >= 90; +1 for Systolic >= 130 or Diastolic >= 80
    # +2 for Fasting Glucose >= 126 or HbA1c >= 6.5; +1 for Fasting Glucose >= 100 or HbA1c >= 5.7
    # +2 for LDL >= 160; +1 for LDL >= 130
    # +1 for low HDL (< 40 male, < 50 female)
    # +2 for Triglycerides >= 200; +1 for >= 150
    # +2 for BMI >= 30; +1 for BMI >= 25
    # +2 for Current Smoker; +1 for Former Smoker
    # +1 for Frequent Alcohol
    # -1 for Physical Activity >= 200 min/week; +1 for Activity < 60 min/week
    # +1 for Age >= 55
    # +1 for Family History of Diabetes
    # +1 for Family History of Heart Disease
    risk_score = np.zeros(n_samples)

    risk_score += np.where((systolic_bp >= 140) | (diastolic_bp >= 90), 2.0,
                           np.where((systolic_bp >= 130) | (diastolic_bp >= 80), 1.0, 0.0))

    risk_score += np.where((fasting_glucose >= 126) | (hba1c >= 6.5), 2.0,
                           np.where((fasting_glucose >= 100) | (hba1c >= 5.7), 1.0, 0.0))

    risk_score += np.where(cholesterol_ldl >= 160, 2.0,
                           np.where(cholesterol_ldl >= 130, 1.0, 0.0))

    risk_score += np.where(((sex == "Male") & (cholesterol_hdl < 40)) |
                           ((sex == "Female") & (cholesterol_hdl < 50)), 1.0, 0.0)

    risk_score += np.where(triglycerides >= 200, 2.0,
                           np.where(triglycerides >= 150, 1.0, 0.0))

    risk_score += np.where(bmi >= 30, 2.0,
                           np.where(bmi >= 25, 1.0, 0.0))

    risk_score += np.where(smoking_status == "Current", 2.0,
                           np.where(smoking_status == "Former", 1.0, 0.0))

    risk_score += np.where(alcohol_frequency == "Frequent", 1.0, 0.0)

    risk_score += np.where(physical_activity_min_per_week >= 200, -1.0,
                           np.where(physical_activity_min_per_week < 60, 1.0, 0.0))

    risk_score += np.where(age >= 55, 1.0, 0.0)
    risk_score += family_history_diabetes * 1.0
    risk_score += family_history_heart_disease * 1.0

    # Add Gaussian stochastic variation
    risk_score += np.random.normal(0, 0.5, size=n_samples)

    # Bin into 3 distinct classes
    # Cutoffs chosen for balanced and realistic distribution
    risk_category = np.where(
        risk_score < 4.0,
        "Lower synthetic risk category",
        np.where(
            risk_score < 8.0,
            "Moderate synthetic risk category",
            "Higher synthetic risk category"
        )
    )

    df = pd.DataFrame({
        "age": age,
        "sex": sex,
        "height_cm": height_cm.round(1),
        "weight_kg": weight_kg.round(1),
        "waist_cm": waist_cm,
        "bmi": bmi,
        "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp,
        "resting_heart_rate": resting_heart_rate,
        "cholesterol_total": cholesterol_total,
        "cholesterol_ldl": cholesterol_ldl,
        "cholesterol_hdl": cholesterol_hdl,
        "triglycerides": triglycerides,
        "fasting_glucose": fasting_glucose,
        "hba1c": hba1c,
        "physical_activity_min_per_week": physical_activity_min_per_week,
        "sleep_hours": sleep_hours,
        "water_liters": water_liters,
        "smoking_status": smoking_status,
        "alcohol_frequency": alcohol_frequency,
        "fruit_veg_servings": fruit_veg_servings,
        "sugary_drinks_per_week": sugary_drinks_per_week,
        "family_history_diabetes": family_history_diabetes,
        "family_history_heart_disease": family_history_heart_disease,
        "serum_creatinine": serum_creatinine,
        "alt_sgpt": alt_sgpt,
        "synthetic_risk_score": risk_score.round(2),
        "risk_category": risk_category
    })

    return df


def perform_eda(df: pd.DataFrame) -> Dict[str, Any]:
    """Execute exploratory data analysis on the dataset."""
    eda_summary = {
        "n_rows": int(len(df)),
        "n_columns": int(df.shape[1]),
        "missing_values": {col: int(cnt) for col, cnt in df.isnull().sum().items() if cnt > 0},
        "duplicate_rows": int(df.duplicated().sum()),
        "class_distribution": df["risk_category"].value_counts().to_dict(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
    }
    return eda_summary


def train_and_evaluate() -> Tuple[Dict[str, Any], Any]:
    """Execute full ML pipeline: EDA, preprocessing, model training, evaluation, and export."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Dataset Acquisition
    if DATA_PATH.exists():
        print(f"Loading existing dataset from {DATA_PATH}...")
        df = pd.read_csv(DATA_PATH)
    else:
        print(f"Generating reproducible synthetic dataset at {DATA_PATH}...")
        df = generate_synthetic_dataset(n_samples=2500, random_seed=RANDOM_STATE)
        df.to_csv(DATA_PATH, index=False)

    # 2. EDA
    eda = perform_eda(df)
    print("\n=== DATASET EDA SUMMARY ===")
    print(f"Rows: {eda['n_rows']}, Columns: {eda['n_columns']}")
    print(f"Duplicates: {eda['duplicate_rows']}")
    print(f"Class Distribution: {eda['class_distribution']}")

    # 3. Features & Target
    # Do NOT include synthetic_risk_score (the raw formula output) in training features!
    feature_cols = [
        "age", "sex", "height_cm", "weight_kg", "waist_cm", "bmi",
        "systolic_bp", "diastolic_bp", "resting_heart_rate",
        "cholesterol_total", "cholesterol_ldl", "cholesterol_hdl", "triglycerides",
        "fasting_glucose", "hba1c",
        "physical_activity_min_per_week", "sleep_hours", "water_liters",
        "smoking_status", "alcohol_frequency",
        "fruit_veg_servings", "sugary_drinks_per_week",
        "family_history_diabetes", "family_history_heart_disease",
        "serum_creatinine", "alt_sgpt"
    ]
    target_col = "risk_category"

    X = df[feature_cols]
    y = df[target_col]

    # Split train/test (80/20) with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )

    numeric_features = [
        "age", "height_cm", "weight_kg", "waist_cm", "bmi",
        "systolic_bp", "diastolic_bp", "resting_heart_rate",
        "cholesterol_total", "cholesterol_ldl", "cholesterol_hdl", "triglycerides",
        "fasting_glucose", "hba1c",
        "physical_activity_min_per_week", "sleep_hours", "water_liters",
        "fruit_veg_servings", "sugary_drinks_per_week",
        "family_history_diabetes", "family_history_heart_disease",
        "serum_creatinine", "alt_sgpt"
    ]
    categorical_features = ["sex", "smoking_status", "alcohol_frequency"]

    # Preprocessing pipelines (fit strictly on training data)
    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features)
        ]
    )

    # 4. Train Models
    # Model A: Baseline Logistic Regression
    lr_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=1000, random_state=RANDOM_STATE, C=1.0))
    ])

    # Model B: Random Forest Classifier
    rf_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=150, max_depth=10, min_samples_split=4, random_state=RANDOM_STATE, n_jobs=-1
        ))
    ])

    print("\nFitting Logistic Regression baseline...")
    lr_pipeline.fit(X_train, y_train)
    y_pred_lr = lr_pipeline.predict(X_test)

    print("Fitting Random Forest classifier...")
    rf_pipeline.fit(X_train, y_train)
    y_pred_rf = rf_pipeline.predict(X_test)

    # 5. Evaluate
    def get_metrics(y_true, y_pred, model_name: str) -> Dict[str, Any]:
        acc = accuracy_score(y_true, y_pred)
        prec_macro = precision_score(y_true, y_pred, average="macro", zero_division=0)
        rec_macro = recall_score(y_true, y_pred, average="macro", zero_division=0)
        f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)
        prec_weighted = precision_score(y_true, y_pred, average="weighted", zero_division=0)
        rec_weighted = recall_score(y_true, y_pred, average="weighted", zero_division=0)
        f1_weighted = f1_score(y_true, y_pred, average="weighted", zero_division=0)
        cm = confusion_matrix(y_true, y_pred, labels=CLASS_NAMES).tolist()
        
        return {
            "model_name": model_name,
            "accuracy": round(float(acc), 4),
            "precision_macro": round(float(prec_macro), 4),
            "recall_macro": round(float(rec_macro), 4),
            "f1_macro": round(float(f1_macro), 4),
            "precision_weighted": round(float(prec_weighted), 4),
            "recall_weighted": round(float(rec_weighted), 4),
            "f1_weighted": round(float(f1_weighted), 4),
            "confusion_matrix": cm,
            "labels": CLASS_NAMES,
            "classification_report": classification_report(y_true, y_pred, output_dict=True, zero_division=0)
        }

    metrics_lr = get_metrics(y_test, y_pred_lr, "Logistic Regression Baseline")
    metrics_rf = get_metrics(y_test, y_pred_rf, "Random Forest Classifier")

    print(f"\nBaseline LR Accuracy: {metrics_lr['accuracy']:.4f} | F1 Macro: {metrics_lr['f1_macro']:.4f}")
    print(f"Random Forest Accuracy: {metrics_rf['accuracy']:.4f} | F1 Macro: {metrics_rf['f1_macro']:.4f}")

    # Select best model based on F1 Macro
    if metrics_rf["f1_macro"] >= metrics_lr["f1_macro"]:
        best_pipeline = rf_pipeline
        best_name = "Random Forest Classifier"
        best_metrics = metrics_rf
    else:
        best_pipeline = lr_pipeline
        best_name = "Logistic Regression Baseline"
        best_metrics = metrics_lr

    print(f"\nBest Model: {best_name}")

    # Extract feature names & feature importances if Random Forest
    rf_model = rf_pipeline.named_steps["classifier"]
    cat_encoder = rf_pipeline.named_steps["preprocessor"].named_transformers_["cat"].named_steps["onehot"]
    cat_encoded_names = list(cat_encoder.get_feature_names_out(categorical_features))
    all_feature_names = numeric_features + cat_encoded_names
    feature_importances = rf_model.feature_importances_.tolist()
    importance_dict = dict(zip(all_feature_names, [round(float(v), 5) for v in feature_importances]))

    # Sort importance
    sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)

    # 6. Save Artifacts
    artifact_payload = {
        "pipeline": best_pipeline,
        "feature_cols": feature_cols,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "all_transformed_feature_names": all_feature_names,
        "class_names": CLASS_NAMES,
        "best_model_name": best_name,
        "feature_importances": sorted_importance,
        "random_state": RANDOM_STATE
    }

    joblib.dump(artifact_payload, MODEL_PATH)
    print(f"Saved model pipeline to {MODEL_PATH}")

    # Save metrics JSON for app presentation
    metrics_export = {
        "eda": eda,
        "baseline_logistic_regression": metrics_lr,
        "random_forest": metrics_rf,
        "best_model": best_name,
        "top_features": sorted_importance[:10],
        "feature_cols": feature_cols
    }

    with open(METRICS_PATH, "w") as f:
        json.dump(metrics_export, f, indent=2)
    print(f"Saved evaluation metrics to {METRICS_PATH}")

    return metrics_export, best_pipeline


if __name__ == "__main__":
    train_and_evaluate()
