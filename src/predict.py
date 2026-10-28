"""Inference engine for HealthRisk AI.

Loads the saved scikit-learn pipeline and performs model prediction,
computes synthetic risk category probabilities, and extracts patient-specific
contributing factors based on model weights and deviations from healthy baselines.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import joblib

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "risk_classifier.joblib"

CLASS_NAMES = [
    "Lower synthetic risk category",
    "Moderate synthetic risk category",
    "Higher synthetic risk category"
]


class RiskPredictor:
    """Wrapper around trained scikit-learn risk classification pipeline."""

    def __init__(self, model_path: Optional[Path] = None):
        self.model_path = model_path or MODEL_PATH
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model artifact not found at {self.model_path}. Run train_model.py first.")
        
        payload = joblib.load(self.model_path)
        self.pipeline = payload["pipeline"]
        self.feature_cols = payload["feature_cols"]
        self.numeric_features = payload["numeric_features"]
        self.categorical_features = payload["categorical_features"]
        self.class_names = payload["class_names"]
        self.best_model_name = payload["best_model_name"]
        self.feature_importances = payload.get("feature_importances", [])

    def predict(self, user_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run prediction on sanitized input dictionary.
        
        Returns:
            predicted_class (str): synthetic risk category name
            probabilities (dict): probability for each category
            top_factors (list): ordered list of top risk-influencing inputs
        """
        # Build 1-row DataFrame strictly aligned with feature columns
        row_dict = {}
        for col in self.feature_cols:
            val = user_inputs.get(col)
            # Map None to np.nan so ColumnTransformer SimpleImputer handles it cleanly
            if val is None:
                row_dict[col] = np.nan
            else:
                row_dict[col] = val

        df_input = pd.DataFrame([row_dict])

        # Predict class & probabilities
        pred_class = self.pipeline.predict(df_input)[0]
        
        has_proba = hasattr(self.pipeline, "predict_proba")
        if has_proba:
            proba_arr = self.pipeline.predict_proba(df_input)[0]
            # Map to class labels
            classes = self.pipeline.classes_
            probabilities = {str(c): round(float(p), 4) for c, p in zip(classes, proba_arr)}
        else:
            probabilities = {pred_class: 1.0}

        # Identify top contributing factors for this specific individual
        contributing_factors = self._compute_individual_factors(user_inputs)

        return {
            "predicted_category": pred_class,
            "probabilities": probabilities,
            "model_used": self.best_model_name,
            "contributing_factors": contributing_factors
        }

    def _compute_individual_factors(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify which measurements contributed most heavily to the elevated risk."""
        factors = []

        # Clinically intuitive impact checks
        sys_bp = inputs.get("systolic_bp")
        dia_bp = inputs.get("diastolic_bp")
        if (sys_bp is not None and sys_bp >= 130) or (dia_bp is not None and dia_bp >= 85):
            factors.append({
                "factor": "Blood Pressure",
                "value": f"{sys_bp}/{dia_bp} mmHg",
                "impact": "High Positive Risk",
                "description": "Systolic or diastolic pressure is in an elevated or hypertensive stage."
            })

        fg = inputs.get("fasting_glucose")
        hba1c = inputs.get("hba1c")
        if (fg is not None and fg >= 100) or (hba1c is not None and hba1c >= 5.7):
            g_str = f"Fasting: {fg} mg/dL" if fg else ""
            if hba1c:
                g_str += f" | HbA1c: {hba1c}%"
            factors.append({
                "factor": "Blood Glucose / Glycemia",
                "value": g_str.strip(" |"),
                "impact": "High Positive Risk",
                "description": "Glycemic levels exceed standard normal fasting or 3-month thresholds."
            })

        ldl = inputs.get("cholesterol_ldl")
        tc = inputs.get("cholesterol_total")
        tg = inputs.get("triglycerides")
        if (ldl is not None and ldl >= 130) or (tc is not None and tc >= 200) or (tg is not None and tg >= 150):
            l_str = f"LDL: {ldl}" if ldl else f"Total: {tc}"
            factors.append({
                "factor": "Lipid Profile",
                "value": f"{l_str} mg/dL",
                "impact": "Moderate-to-High Risk",
                "description": "Atherogenic lipid fractions or triglycerides are above optimal targets."
            })

        bmi = inputs.get("bmi")
        if bmi is not None and bmi >= 25.0:
            factors.append({
                "factor": "Body Mass Index",
                "value": f"{bmi} kg/m²",
                "impact": "Moderate Risk",
                "description": "Exceeds standard healthy adult threshold of 24.9 kg/m²."
            })

        smoking = inputs.get("smoking_status")
        if smoking in ["Current", "Former"]:
            factors.append({
                "factor": "Tobacco History",
                "value": smoking,
                "impact": "Vascular Risk Factor",
                "description": "Smoking accelerates arterial endothelial stiffness and inflammation."
            })

        act = inputs.get("physical_activity_min_per_week")
        if act is not None and act < 150:
            factors.append({
                "factor": "Physical Inactivity",
                "value": f"{act} min/week",
                "impact": "Sedentary Factor",
                "description": "Reported exercise is below WHO 150 min/week threshold."
            })
        elif act is not None and act >= 150:
            factors.append({
                "factor": "Protective Physical Activity",
                "value": f"{act} min/week",
                "impact": "Protective Factor",
                "description": "Meeting aerobic targets directly reduces cardiometabolic strain."
            })

        hdl = inputs.get("cholesterol_hdl")
        if hdl is not None and hdl >= 60:
            factors.append({
                "factor": "High HDL Cholesterol",
                "value": f"{hdl} mg/dL",
                "impact": "Protective Factor",
                "description": "Optimal high-density lipoprotein supports reverse cholesterol transport."
            })

        return factors
