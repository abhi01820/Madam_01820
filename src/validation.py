"""Input validation and sanitization for HealthRisk AI.

Validates required and optional clinical and lifestyle inputs against
biologically plausible ranges and returns clear, human-friendly error messages.
Ensures invalid inputs never crash the application.
"""

from typing import Any, Dict, List, Optional, Tuple


# Biologically plausible and clinically acceptable ranges
VALIDATION_RANGES = {
    # Anthropometrics
    "age": {"min": 18, "max": 120, "unit": "years", "required": True, "label": "Age"},
    "height_cm": {"min": 100.0, "max": 250.0, "unit": "cm", "required": True, "label": "Height"},
    "weight_kg": {"min": 25.0, "max": 300.0, "unit": "kg", "required": True, "label": "Weight"},
    "waist_cm": {"min": 40.0, "max": 200.0, "unit": "cm", "required": False, "label": "Waist circumference"},
    
    # Blood pressure & Vitals
    "systolic_bp": {"min": 70.0, "max": 260.0, "unit": "mmHg", "required": True, "label": "Systolic BP"},
    "diastolic_bp": {"min": 40.0, "max": 160.0, "unit": "mmHg", "required": True, "label": "Diastolic BP"},
    "resting_heart_rate": {"min": 35.0, "max": 200.0, "unit": "bpm", "required": False, "label": "Resting Heart Rate"},
    
    # Lipids (mg/dL)
    "cholesterol_total": {"min": 70.0, "max": 500.0, "unit": "mg/dL", "required": False, "label": "Total Cholesterol"},
    "cholesterol_ldl": {"min": 20.0, "max": 350.0, "unit": "mg/dL", "required": False, "label": "LDL Cholesterol"},
    "cholesterol_hdl": {"min": 10.0, "max": 130.0, "unit": "mg/dL", "required": False, "label": "HDL Cholesterol"},
    "triglycerides": {"min": 30.0, "max": 1500.0, "unit": "mg/dL", "required": False, "label": "Triglycerides"},
    "cholesterol_vldl": {"min": 2.0, "max": 200.0, "unit": "mg/dL", "required": False, "label": "VLDL Cholesterol"},
    
    # Glycemic markers (mg/dL or %)
    "fasting_glucose": {"min": 40.0, "max": 500.0, "unit": "mg/dL", "required": False, "label": "Fasting Blood Glucose"},
    "postprandial_glucose": {"min": 40.0, "max": 500.0, "unit": "mg/dL", "required": False, "label": "Postprandial Glucose"},
    "random_glucose": {"min": 40.0, "max": 500.0, "unit": "mg/dL", "required": False, "label": "Random Blood Glucose"},
    "hba1c": {"min": 3.5, "max": 18.0, "unit": "%", "required": False, "label": "HbA1c"},
    
    # Renal & Hepatic (Optional)
    "serum_creatinine": {"min": 0.2, "max": 15.0, "unit": "mg/dL", "required": False, "label": "Serum Creatinine"},
    "egfr": {"min": 5.0, "max": 160.0, "unit": "mL/min/1.73m²", "required": False, "label": "eGFR"},
    "alt_sgpt": {"min": 2.0, "max": 600.0, "unit": "U/L", "required": False, "label": "ALT (SGPT)"},
    "ast_sgot": {"min": 2.0, "max": 600.0, "unit": "U/L", "required": False, "label": "AST (SGOT)"},
    "total_bilirubin": {"min": 0.1, "max": 20.0, "unit": "mg/dL", "required": False, "label": "Total Bilirubin"},
    
    # Lifestyle
    "physical_activity_min_per_week": {"min": 0.0, "max": 1440.0, "unit": "min/week", "required": False, "label": "Weekly Exercise"},
    "sleep_hours": {"min": 2.0, "max": 16.0, "unit": "hours/day", "required": False, "label": "Daily Sleep"},
    "water_liters": {"min": 0.2, "max": 10.0, "unit": "liters/day", "required": False, "label": "Daily Water Intake"},
    "fruit_veg_servings": {"min": 0.0, "max": 15.0, "unit": "servings/day", "required": False, "label": "Fruit/Vegetable Servings"},
    "sugary_drinks_per_week": {"min": 0.0, "max": 50.0, "unit": "drinks/week", "required": False, "label": "Sugary Drinks per Week"},
    "daily_budget_inr": {"min": 50.0, "max": 10000.0, "unit": "INR", "required": False, "label": "Daily Meal Budget"},
}

CATEGORICAL_ALLOWED = {
    "sex": ["Male", "Female", "Other"],
    "smoking_status": ["Never", "Former", "Current"],
    "alcohol_frequency": ["Never", "Occasional", "Frequent"],
    "diet_type": ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"],
    "cuisine": ["South Indian", "North Indian", "Other"],
    "goal": [
        "General Health & Longevity",
        "Cardiometabolic Risk Reduction",
        "Weight Management",
        "Blood Sugar Control",
        "Heart Health"
    ],
    "meals_per_day": [2, 3, 4, 5]
}


def calculate_bmi(height_cm: Optional[float], weight_kg: Optional[float]) -> Optional[float]:
    """Calculate BMI safely from height in cm and weight in kg."""
    if height_cm is None or weight_kg is None:
        return None
    try:
        h = float(height_cm)
        w = float(weight_kg)
        if h <= 0 or w <= 0:
            return None
        height_m = h / 100.0
        bmi = w / (height_m ** 2)
        return round(bmi, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def validate_health_inputs(raw_data: Dict[str, Any]) -> Tuple[bool, Dict[str, str], Dict[str, str], Dict[str, Any]]:
    """Validate all user-supplied health inputs.
    
    Returns:
        is_valid (bool): True if all required fields are valid and no numeric range errors exist.
        errors (dict): Field-specific error messages that block processing.
        warnings (dict): Advisory notes or physiological consistency flags.
        sanitized (dict): Clean typed dictionary with validated numbers or None.
    """
    errors: Dict[str, str] = {}
    warnings: Dict[str, str] = {}
    sanitized: Dict[str, Any] = {}

    # Check numeric ranges
    for field, rule in VALIDATION_RANGES.items():
        raw_val = raw_data.get(field)
        is_req = rule["required"]
        label = rule["label"]
        min_v = rule["min"]
        max_v = rule["max"]
        unit = rule["unit"]

        if raw_val is None or (isinstance(raw_val, str) and raw_val.strip() == ""):
            if is_req:
                errors[field] = f"{label} is required."
                sanitized[field] = None
            else:
                sanitized[field] = None
            continue

        try:
            val_float = float(raw_val)
            if val_float < min_v or val_float > max_v:
                errors[field] = (
                    f"{label} must be between {min_v} and {max_v} {unit}. "
                    f"Got {val_float}."
                )
                sanitized[field] = None
            else:
                # Keep int if field is age
                if field == "age":
                    sanitized[field] = int(val_float)
                else:
                    sanitized[field] = round(val_float, 2)
        except (ValueError, TypeError):
            errors[field] = f"{label} must be a valid numeric value."
            sanitized[field] = None

    # Check categoricals
    for cat_field, allowed_opts in CATEGORICAL_ALLOWED.items():
        val = raw_data.get(cat_field)
        if val is None or val == "":
            if cat_field in ["sex", "diet_type"]:
                errors[cat_field] = f"Please select a valid {cat_field.replace('_', ' ')}."
                sanitized[cat_field] = allowed_opts[0]
            else:
                sanitized[cat_field] = allowed_opts[0]
        else:
            # Match case-insensitively or exact
            matched = next((opt for opt in allowed_opts if str(opt).lower() == str(val).lower()), None)
            if matched is not None:
                sanitized[cat_field] = matched
            else:
                errors[cat_field] = f"Invalid option for {cat_field}. Allowed: {', '.join(map(str, allowed_opts))}."
                sanitized[cat_field] = allowed_opts[0]

    # Booleans & Lists
    sanitized["family_history_diabetes"] = bool(raw_data.get("family_history_diabetes", False))
    sanitized["family_history_heart_disease"] = bool(raw_data.get("family_history_heart_disease", False))
    
    allergies = raw_data.get("allergies", [])
    if isinstance(allergies, list):
        sanitized["allergies"] = [str(a).strip() for a in allergies if str(a).strip()]
    elif isinstance(allergies, str):
        sanitized["allergies"] = [a.strip() for a in allergies.split(",") if a.strip()]
    else:
        sanitized["allergies"] = []

    # Timestamp context selectors (e.g. "when was it taken")
    for marker in ["fasting_glucose", "postprandial_glucose", "random_glucose", "hba1c"]:
        timing_key = f"{marker}_timing"
        sanitized[timing_key] = raw_data.get(timing_key, "Not specified")

    # Physiological Consistency Warnings
    # Systolic vs Diastolic
    sys_bp = sanitized.get("systolic_bp")
    dia_bp = sanitized.get("diastolic_bp")
    if sys_bp is not None and dia_bp is not None:
        if sys_bp <= dia_bp:
            errors["systolic_bp"] = "Systolic blood pressure must be higher than diastolic blood pressure."
        elif sys_bp - dia_bp < 15:
            warnings["blood_pressure"] = "Pulse pressure (Systolic - Diastolic) is unusually narrow (< 15 mmHg)."
        elif sys_bp - dia_bp > 100:
            warnings["blood_pressure"] = "Pulse pressure is wide (> 100 mmHg); please re-verify with a calm repeat reading."

    # BMI calculation
    bmi = calculate_bmi(sanitized.get("height_cm"), sanitized.get("weight_kg"))
    sanitized["bmi"] = bmi

    # Pediatric BMI note
    age = sanitized.get("age")
    if age is not None and age < 18:
        warnings["age_pediatric"] = (
            "Standard adult BMI cutoff categories do not apply to individuals under 18 years old. "
            "Pediatric percentiles must be used instead."
        )

    is_valid = len(errors) == 0
    return is_valid, errors, warnings, sanitized


def detect_emergency_flags(data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Detect dangerously abnormal clinical values requiring prompt medical attention.
    
    References:
    - AHA/ACC 2017: Hypertensive crisis (Systolic > 180 mmHg or Diastolic > 120 mmHg)
    - ADA 2024: Severe hypoglycemia (< 54 mg/dL) or severe hyperglycemia (> 300 mg/dL)
    - Clinical cardiology: Extreme tachycardia (> 140 bpm) or severe bradycardia (< 40 bpm)
    """
    flags = []

    sys_bp = data.get("systolic_bp")
    dia_bp = data.get("diastolic_bp")
    if (sys_bp is not None and sys_bp >= 180) or (dia_bp is not None and dia_bp >= 120):
        flags.append({
            "category": "Hypertensive Crisis Range",
            "message": (
                f"Systolic BP ({sys_bp} mmHg) or Diastolic BP ({dia_bp} mmHg) is in the "
                "emergency hypertensive crisis range (>= 180/120 mmHg). If accompanied by chest pain, "
                "shortness of breath, severe headache, or numbness, seek emergency medical care immediately."
            ),
            "severity": "CRITICAL"
        })

    fg = data.get("fasting_glucose")
    pg = data.get("postprandial_glucose")
    rg = data.get("random_glucose")

    for g_val, g_label in [(fg, "Fasting glucose"), (pg, "Postprandial glucose"), (rg, "Random glucose")]:
        if g_val is not None:
            if g_val < 54:
                flags.append({
                    "category": "Severe Hypoglycemia",
                    "message": (
                        f"{g_label} is critically low ({g_val} mg/dL < 54 mg/dL). "
                        "Consume 15-20g of fast-acting carbohydrate (e.g., fruit juice, glucose tablets) "
                        "immediately and consult medical personnel if symptoms persist."
                    ),
                    "severity": "CRITICAL"
                })
            elif g_val >= 300:
                flags.append({
                    "category": "Marked Hyperglycemia",
                    "message": (
                        f"{g_label} is severely elevated ({g_val} mg/dL >= 300 mg/dL). "
                        "Marked hyperglycemia carries risk of acute metabolic complications. "
                        "Contact a physician or urgent healthcare clinic promptly."
                    ),
                    "severity": "HIGH"
                })

    hr = data.get("resting_heart_rate")
    if hr is not None:
        if hr > 140:
            flags.append({
                "category": "Severe Resting Tachycardia",
                "message": (
                    f"Resting heart rate is notably elevated ({hr} bpm). If resting calmly and heart rate "
                    "remains above 130-140 bpm, seek medical evaluation."
                ),
                "severity": "HIGH"
            })
        elif hr < 40:
            flags.append({
                "category": "Marked Resting Bradycardia",
                "message": (
                    f"Resting heart rate is very low ({hr} bpm). Unless you are a highly conditioned endurance athlete, "
                    "this warrants clinical review."
                ),
                "severity": "MEDIUM"
            })

    return flags
