"""Unit tests for ML risk predictor and inference pipeline."""

import pytest
from src.predict import RiskPredictor, CLASS_NAMES


@pytest.fixture
def predictor():
    return RiskPredictor()


def test_predictor_initialization(predictor):
    assert predictor.pipeline is not None
    assert len(predictor.feature_cols) > 0
    assert predictor.class_names == CLASS_NAMES


def test_prediction_output_shape(predictor):
    sample_input = {
        "age": 45,
        "sex": "Male",
        "height_cm": 172.0,
        "weight_kg": 72.0,
        "waist_cm": 86.0,
        "bmi": 24.34,
        "systolic_bp": 120.0,
        "diastolic_bp": 78.0,
        "resting_heart_rate": 70.0,
        "cholesterol_total": 190.0,
        "cholesterol_ldl": 110.0,
        "cholesterol_hdl": 52.0,
        "triglycerides": 140.0,
        "fasting_glucose": 92.0,
        "hba1c": 5.4,
        "physical_activity_min_per_week": 180,
        "sleep_hours": 7.5,
        "water_liters": 2.5,
        "smoking_status": "Never",
        "alcohol_frequency": "Occasional",
        "fruit_veg_servings": 4,
        "sugary_drinks_per_week": 1,
        "family_history_diabetes": 0,
        "family_history_heart_disease": 0,
        "serum_creatinine": 0.9,
        "alt_sgpt": 25.0
    }

    result = predictor.predict(sample_input)
    assert "predicted_category" in result
    assert result["predicted_category"] in CLASS_NAMES
    assert "probabilities" in result
    assert isinstance(result["probabilities"], dict)
    for c in CLASS_NAMES:
        assert c in result["probabilities"]
    # Probabilities should sum to approximately 1.0
    total_p = sum(result["probabilities"].values())
    assert 0.98 <= total_p <= 1.02
    assert "contributing_factors" in result
    assert isinstance(result["contributing_factors"], list)


def test_prediction_with_missing_optional_values(predictor):
    # Only minimal features provided, rest are None
    minimal_input = {
        "age": 50,
        "sex": "Female",
        "height_cm": 162.0,
        "weight_kg": 64.0,
        "bmi": 24.38,
        "systolic_bp": 122.0,
        "diastolic_bp": 80.0,
        "smoking_status": "Never",
        "alcohol_frequency": "Never"
    }

    # Should not crash; missing fields imputed by pipeline
    result = predictor.predict(minimal_input)
    assert result["predicted_category"] in CLASS_NAMES
    assert len(result["probabilities"]) == 3


def test_high_risk_profile(predictor):
    # Multiple elevated risk markers
    high_risk_input = {
        "age": 65,
        "sex": "Male",
        "height_cm": 170.0,
        "weight_kg": 98.0,
        "bmi": 33.91,
        "waist_cm": 108.0,
        "systolic_bp": 165.0,
        "diastolic_bp": 102.0,
        "resting_heart_rate": 88.0,
        "cholesterol_total": 280.0,
        "cholesterol_ldl": 185.0,
        "cholesterol_hdl": 34.0,
        "triglycerides": 310.0,
        "fasting_glucose": 175.0,
        "hba1c": 8.2,
        "physical_activity_min_per_week": 0,
        "smoking_status": "Current",
        "alcohol_frequency": "Frequent",
        "family_history_diabetes": 1,
        "family_history_heart_disease": 1
    }

    result = predictor.predict(high_risk_input)
    # Risk should NOT be lower risk category
    assert result["predicted_category"] in ["Moderate synthetic risk category", "Higher synthetic risk category"]
    assert len(result["contributing_factors"]) > 0
