"""Unit tests for input validation and emergency detection."""

import pytest
from src.validation import validate_health_inputs, calculate_bmi, detect_emergency_flags


def test_calculate_bmi():
    # 70kg, 175cm -> 70 / (1.75^2) = 22.86
    assert calculate_bmi(175, 70) == 22.86
    # Missing / None
    assert calculate_bmi(None, 70) is None
    assert calculate_bmi(175, None) is None
    # Zero / Negative
    assert calculate_bmi(0, 70) is None
    assert calculate_bmi(175, -5) is None
    # Invalid strings
    assert calculate_bmi("abc", 70) is None


def test_validation_valid_complete():
    raw_input = {
        "age": 45,
        "sex": "Male",
        "height_cm": 175,
        "weight_kg": 75,
        "waist_cm": 88,
        "systolic_bp": 125,
        "diastolic_bp": 82,
        "resting_heart_rate": 72,
        "cholesterol_total": 210,
        "cholesterol_ldl": 130,
        "cholesterol_hdl": 48,
        "triglycerides": 160,
        "fasting_glucose": 95,
        "hba1c": 5.5,
        "physical_activity_min_per_week": 180,
        "sleep_hours": 7.5,
        "water_liters": 2.5,
        "smoking_status": "Never",
        "alcohol_frequency": "Occasional",
        "fruit_veg_servings": 4,
        "sugary_drinks_per_week": 1,
        "family_history_diabetes": False,
        "family_history_heart_disease": True,
        "diet_type": "Vegetarian",
        "cuisine": "South Indian",
        "allergies": ["Peanuts"]
    }

    is_valid, errors, warnings, sanitized = validate_health_inputs(raw_input)
    assert is_valid is True
    assert len(errors) == 0
    assert sanitized["bmi"] == 24.49
    assert sanitized["diet_type"] == "Vegetarian"
    assert sanitized["allergies"] == ["Peanuts"]


def test_validation_missing_optionals():
    # Provide only required fields: age, sex, height_cm, weight_kg, systolic_bp, diastolic_bp, diet_type
    minimal_input = {
        "age": 30,
        "sex": "Female",
        "height_cm": 160,
        "weight_kg": 55,
        "systolic_bp": 115,
        "diastolic_bp": 75,
        "diet_type": "Vegan"
    }

    is_valid, errors, warnings, sanitized = validate_health_inputs(minimal_input)
    assert is_valid is True
    assert len(errors) == 0
    # Optional fields should be None in sanitized dict
    assert sanitized["cholesterol_total"] is None
    assert sanitized["fasting_glucose"] is None
    assert sanitized["serum_creatinine"] is None
    assert sanitized["bmi"] == 21.48


def test_validation_invalid_numeric_ranges():
    bad_input = {
        "age": 150,  # exceeds max 120
        "height_cm": 40,  # below min 100
        "weight_kg": -10,  # negative
        "systolic_bp": 350,  # above max 260
        "diastolic_bp": "not_a_number"
    }

    is_valid, errors, warnings, sanitized = validate_health_inputs(bad_input)
    assert is_valid is False
    assert "age" in errors
    assert "height_cm" in errors
    assert "weight_kg" in errors
    assert "systolic_bp" in errors
    assert "diastolic_bp" in errors


def test_validation_systolic_le_diastolic():
    inverted_bp = {
        "age": 40,
        "sex": "Male",
        "height_cm": 170,
        "weight_kg": 70,
        "systolic_bp": 80,
        "diastolic_bp": 120,
        "diet_type": "Vegetarian"
    }

    is_valid, errors, warnings, sanitized = validate_health_inputs(inverted_bp)
    assert is_valid is False
    assert "systolic_bp" in errors
    assert "higher than diastolic" in errors["systolic_bp"]


def test_pediatric_warning():
    pediatric_input = {
        "age": 16,
        "sex": "Female",
        "height_cm": 155,
        "weight_kg": 48,
        "systolic_bp": 110,
        "diastolic_bp": 70,
        "diet_type": "Vegetarian"
    }
    # Age is below min 18, so should produce error
    is_valid, errors, warnings, sanitized = validate_health_inputs(pediatric_input)
    assert "age" in errors


def test_emergency_flags():
    # Hypertensive crisis test
    crisis_data = {"systolic_bp": 185, "diastolic_bp": 122}
    flags = detect_emergency_flags(crisis_data)
    assert any(f["category"] == "Hypertensive Crisis Range" for f in flags)
    assert any(f["severity"] == "CRITICAL" for f in flags)

    # Severe hypoglycemia
    hypo_data = {"fasting_glucose": 48}
    flags_hypo = detect_emergency_flags(hypo_data)
    assert any(f["category"] == "Severe Hypoglycemia" for f in flags_hypo)

    # Severe hyperglycemia
    hyper_data = {"random_glucose": 340}
    flags_hyper = detect_emergency_flags(hyper_data)
    assert any(f["category"] == "Marked Hyperglycemia" for f in flags_hyper)

    # Normal values should produce no emergency flags
    normal_data = {"systolic_bp": 118, "diastolic_bp": 78, "fasting_glucose": 88, "resting_heart_rate": 70}
    assert len(detect_emergency_flags(normal_data)) == 0
