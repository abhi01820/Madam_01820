"""Unit tests for clinical recommendation engine and meal plan generation."""

import pytest
from src.recommendation_engine import (
    assess_bmi,
    assess_cholesterol,
    assess_blood_pressure,
    assess_glucose,
    generate_diet_recommendations,
    generate_lifestyle_recommendations,
    generate_meal_plan,
    is_meal_suitable,
    MEAL_DATABASE
)


def test_assess_bmi():
    # Normal
    res = assess_bmi(22.5)
    assert res["status"] == "Available"
    assert res["category"] == "Normal Weight"
    assert res["badge_color"] == "normal"

    # Overweight
    res_ov = assess_bmi(27.4)
    assert res_ov["category"] == "Overweight"
    assert res_ov["badge_color"] == "warning"

    # Obesity Class I
    res_ob = assess_bmi(32.1)
    assert res_ob["category"] == "Obesity Class I"
    assert res_ob["badge_color"] == "abnormal"

    # Missing
    res_missing = assess_bmi(None)
    assert res_missing["status"] == "Missing"
    assert res_missing["category"] == "Unassessed"
    assert res_missing["badge_color"] == "neutral"


def test_assess_blood_pressure():
    # Normal
    res_norm = assess_blood_pressure(115, 75)
    assert res_norm["category"] == "Normal Blood Pressure"
    assert res_norm["badge_color"] == "normal"

    # Stage 1
    res_s1 = assess_blood_pressure(134, 84)
    assert res_s1["category"] == "Stage 1 Hypertension"

    # Stage 2
    res_s2 = assess_blood_pressure(145, 92)
    assert res_s2["category"] == "Stage 2 Hypertension"

    # Hypertensive crisis
    res_crisis = assess_blood_pressure(185, 110)
    assert res_crisis["category"] == "Hypertensive Crisis"
    assert res_crisis["badge_color"] == "critical"

    # Missing
    res_none = assess_blood_pressure(None, 80)
    assert res_none["status"] == "Missing"


def test_assess_cholesterol():
    # Complete normal
    res = assess_cholesterol(total=180, ldl=90, hdl=55, triglycerides=120, sex="Male")
    assert res["status"] == "Available"
    assert res["assessments"]["total"]["badge"] == "normal"
    assert res["assessments"]["ldl"]["badge"] == "normal"

    # High LDL & Triglycerides
    res_high = assess_cholesterol(total=250, ldl=165, hdl=35, triglycerides=220, sex="Male")
    assert res_high["assessments"]["ldl"]["badge"] == "abnormal"
    assert len(res_high["flags"]) >= 2

    # Completely missing
    res_none = assess_cholesterol(None, None, None, None)
    assert res_none["status"] == "Missing"
    assert res_none["assessments"]["total"]["category"] == "Unassessed"


def test_assess_glucose():
    # Evaluates separately without substituting
    res = assess_glucose(fasting=108, postprandial=None, random_val=None, hba1c=5.9)
    assert res["markers"]["fasting_glucose"]["category"].startswith("Impaired Fasting Glucose")
    assert res["markers"]["postprandial_glucose"]["category"] == "Unassessed"
    assert res["markers"]["hba1c"]["category"].startswith("Prediabetes Range")
    assert res["markers"]["random_glucose"]["category"] == "Unassessed"


def test_diet_recommendations_safety():
    # Hypertension user should get sodium moderation
    htn_user = {"systolic_bp": 145, "diastolic_bp": 92}
    recs = generate_diet_recommendations(htn_user)
    titles = [r["title"] for r in recs]
    assert any("Sodium" in t for t in titles)

    # Check that recommendation text does NOT unilaterally push high potassium
    rec_texts = " ".join([r["body"] for r in recs])
    assert "potassium chloride" not in rec_texts.lower() or "avoid" in rec_texts.lower()


def test_meal_plan_diet_type_compliance():
    # Vegan plan must never have dairy, eggs, meat
    vegan_plan = generate_meal_plan(diet_type="Vegan", cuisine="South Indian", random_seed=42)
    for meal_time, dish in vegan_plan["schedule"].items():
        assert "Vegan" in dish.get("diet_types", ["Vegan"])
        allergens = [a.lower() for a in dish.get("allergens", [])]
        assert "dairy / lactose" not in allergens
        assert "eggs" not in allergens
        assert "fish" not in allergens

    # Vegetarian plan must never have meat or fish
    veg_plan = generate_meal_plan(diet_type="Vegetarian", cuisine="South Indian", random_seed=42)
    for meal_time, dish in veg_plan["schedule"].items():
        allergens = [a.lower() for a in dish.get("allergens", [])]
        assert "fish" not in allergens
        assert "shellfish" not in allergens


def test_meal_plan_allergy_exclusion():
    # Test strict exclusion of Gluten and Dairy
    plan = generate_meal_plan(
        diet_type="Vegetarian",
        cuisine="South Indian",
        allergies=["Gluten", "Dairy / Lactose"],
        random_seed=123
    )
    for meal_time, dish in plan["schedule"].items():
        dish_allergens = [a.lower() for a in dish.get("allergens", [])]
        assert "gluten" not in dish_allergens
        assert "dairy / lactose" not in dish_allergens


def test_meal_plan_qualitative_nature():
    # Meal plans must have portion guidance and short explanations, but NOT invented calories
    plan = generate_meal_plan(diet_type="Vegetarian", cuisine="South Indian", random_seed=99)
    for meal_time, dish in plan["schedule"].items():
        assert "portion_guidance" in dish
        assert "why_it_helps" in dish
        # Make sure no fabricated calorie numbers
        assert "calories" not in dish
        assert "kcal" not in dish
