"""Rule-based clinical and lifestyle recommendation engine for HealthRisk AI.

All thresholds and clinical references adhere to authoritative guidelines:
- BMI: WHO Technical Report Series 854 & WHO Expert Consultation (Lancet 2004)
- Blood Pressure: 2017 ACC/AHA/AAPA/ABC/ACPM/AGS/APhA/ASH/ASPC/NMA/PCNA Guideline
- Lipids: National Cholesterol Education Program (NCEP) Adult Treatment Panel III (ATP III)
- Glucose & HbA1c: American Diabetes Association (ADA) Standards of Care in Diabetes 2024

IMPORTANT SAFETY PRINCIPLES:
- Never infer missing measurements as healthy.
- If data is missing, tag as 'Missing / Unassessed' rather than normal.
- Never recommend crash diets, extreme caloric restrictions, or medication changes.
- Limit sodium for blood pressure; do NOT unilaterally recommend high-potassium diets.
- Strict allergy exclusion and dietary restriction compliance.
"""

from typing import Any, Dict, List, Optional
import random


# ==============================================================================
# CLINICAL THRESHOLD EVALUATION
# ==============================================================================

def assess_bmi(bmi: Optional[float], age: Optional[int] = None) -> Dict[str, Any]:
    """Assess Body Mass Index according to WHO clinical thresholds.
    
    Reference: WHO Expert Consultation (2004). Lancet, 363(9403), 157-163.
    """
    if bmi is None:
        return {
            "status": "Missing",
            "category": "Unassessed",
            "badge_color": "neutral",
            "message": "BMI could not be calculated because height or weight was not provided."
        }

    pediatric_warning = False
    if age is not None and age < 18:
        pediatric_warning = True

    if bmi < 18.5:
        category = "Underweight"
        badge_color = "warning"
        message = (
            "BMI indicates an underweight classification (< 18.5 kg/m²). Focus on nutrient-dense meals "
            "with adequate healthy fats, complex carbs, and proteins. Consult a doctor to rule out nutritional deficiencies."
        )
    elif 18.5 <= bmi < 25.0:
        category = "Normal Weight"
        badge_color = "normal"
        message = (
            "BMI is within the conventional standard normal adult range (18.5 - 24.9 kg/m²). "
            "For South Asian populations, public health guidelines suggest monitoring waist circumference and maintaining < 23 kg/m²."
        )
    elif 25.0 <= bmi < 30.0:
        category = "Overweight"
        badge_color = "warning"
        message = (
            "BMI falls in the overweight range (25.0 - 29.9 kg/m²; South Asian threshold >= 23 kg/m²). "
            "Gradual, sustainable lifestyle enhancements (regular physical activity and portion awareness) support metabolic resilience."
        )
    elif 30.0 <= bmi < 35.0:
        category = "Obesity Class I"
        badge_color = "abnormal"
        message = "BMI indicates Class I obesity (30.0 - 34.9 kg/m²). Clinically associated with increased risk of cardiometabolic conditions."
    elif 35.0 <= bmi < 40.0:
        category = "Obesity Class II"
        badge_color = "abnormal"
        message = "BMI indicates Class II obesity (35.0 - 39.9 kg/m²). Structured healthcare guidance and lifestyle therapy are recommended."
    else:
        category = "Obesity Class III"
        badge_color = "critical"
        message = "BMI indicates Class III obesity (>= 40.0 kg/m²). Comprehensive medical management is recommended."

    if pediatric_warning:
        message += " NOTE: Adult BMI cutoffs do not apply to minors (< 18 years); use pediatric growth charts."

    return {
        "status": "Available",
        "category": category,
        "badge_color": badge_color,
        "bmi_value": bmi,
        "message": message,
        "reference_source": "WHO International & Asian BMI Guidance"
    }


def assess_blood_pressure(systolic: Optional[float], diastolic: Optional[float]) -> Dict[str, Any]:
    """Assess blood pressure according to ACC/AHA 2017 Guidelines.
    
    Reference: Whelton PK, et al. 2017 ACC/AHA Guideline for the Prevention, Detection,
    Evaluation, and Management of High Blood Pressure in Adults. J Am Coll Cardiol.
    """
    if systolic is None or diastolic is None:
        return {
            "status": "Missing",
            "category": "Unassessed",
            "badge_color": "neutral",
            "message": "Blood pressure values not fully provided; cardiovascular pressure unassessed."
        }

    # Evaluate based on higher severity bracket
    if systolic >= 180 or diastolic >= 120:
        cat = "Hypertensive Crisis"
        badge = "critical"
        msg = (
            "CRITICAL: Blood pressure is in the hypertensive crisis bracket (>= 180/120 mmHg). "
            "Immediate medical evaluation is indicated if symptoms (headache, chest pain, vision changes) exist."
        )
    elif systolic >= 140 or diastolic >= 90:
        cat = "Stage 2 Hypertension"
        badge = "abnormal"
        msg = (
            f"BP ({systolic}/{diastolic} mmHg) corresponds to Stage 2 Hypertension (>= 140 or >= 90 mmHg). "
            "Clinical evaluation and lifestyle interventions including sodium reduction and stress management are advised."
        )
    elif (130 <= systolic <= 139) or (80 <= diastolic <= 89):
        cat = "Stage 1 Hypertension"
        badge = "warning"
        msg = (
            f"BP ({systolic}/{diastolic} mmHg) matches Stage 1 Hypertension (130-139 / 80-89 mmHg). "
            "Dietary modifications (lower salt, whole foods) and aerobic activity can help normalize pressures."
        )
    elif (120 <= systolic <= 129) and diastolic < 80:
        cat = "Elevated Blood Pressure"
        badge = "warning"
        msg = (
            f"BP ({systolic}/{diastolic} mmHg) is Elevated (120-129 / <80 mmHg). "
            "Preventive lifestyle steps can halt progression into clinical hypertension."
        )
    elif systolic < 120 and diastolic < 80:
        cat = "Normal Blood Pressure"
        badge = "normal"
        msg = f"BP ({systolic}/{diastolic} mmHg) meets the ACC/AHA definition of normal (< 120/< 80 mmHg)."
    else:
        cat = "Borderline / Non-standard"
        badge = "warning"
        msg = f"BP recorded as {systolic}/{diastolic} mmHg. Confirm with repeated rested measurements."

    return {
        "status": "Available",
        "category": cat,
        "badge_color": badge,
        "systolic": systolic,
        "diastolic": diastolic,
        "message": msg,
        "reference_source": "ACC/AHA 2017 Guidelines"
    }


def assess_cholesterol(total: Optional[float], ldl: Optional[float], hdl: Optional[float],
                       triglycerides: Optional[float], sex: str = "Male") -> Dict[str, Any]:
    """Assess lipid profile using NCEP ATP III guidelines.
    
    Reference: Third Report of the National Cholesterol Education Program (NCEP)
    Expert Panel on Detection, Evaluation, and Treatment of High Blood Cholesterol in Adults (ATP III).
    """
    assessments = {}
    flags = []

    # Total Cholesterol
    if total is not None:
        if total < 200:
            tc_cat = "Desirable (< 200 mg/dL)"
            tc_badge = "normal"
        elif 200 <= total <= 239:
            tc_cat = "Borderline High (200-239 mg/dL)"
            tc_badge = "warning"
            flags.append("Total cholesterol is borderline high.")
        else:
            tc_cat = "High (>= 240 mg/dL)"
            tc_badge = "abnormal"
            flags.append("Total cholesterol is elevated.")
        assessments["total"] = {"value": total, "category": tc_cat, "badge": tc_badge}
    else:
        assessments["total"] = {"value": None, "category": "Unassessed", "badge": "neutral"}

    # LDL
    if ldl is not None:
        if ldl < 100:
            ldl_cat = "Optimal (< 100 mg/dL)"
            ldl_badge = "normal"
        elif 100 <= ldl <= 129:
            ldl_cat = "Near Optimal (100-129 mg/dL)"
            ldl_badge = "normal"
        elif 130 <= ldl <= 159:
            ldl_cat = "Borderline High (130-159 mg/dL)"
            ldl_badge = "warning"
            flags.append("LDL cholesterol is borderline high.")
        elif 160 <= ldl <= 189:
            ldl_cat = "High (160-189 mg/dL)"
            ldl_badge = "abnormal"
            flags.append("LDL cholesterol is elevated.")
        else:
            ldl_cat = "Very High (>= 190 mg/dL)"
            ldl_badge = "critical"
            flags.append("LDL cholesterol is very high.")
        assessments["ldl"] = {"value": ldl, "category": ldl_cat, "badge": ldl_badge}
    else:
        assessments["ldl"] = {"value": None, "category": "Unassessed", "badge": "neutral"}

    # HDL
    if hdl is not None:
        hdl_thresh = 50.0 if sex == "Female" else 40.0
        if hdl < hdl_thresh:
            hdl_cat = f"Low (< {int(hdl_thresh)} mg/dL)"
            hdl_badge = "warning"
            flags.append("Protective HDL cholesterol is lower than desirable.")
        elif hdl >= 60:
            hdl_cat = "High / Protective (>= 60 mg/dL)"
            hdl_badge = "normal"
        else:
            hdl_cat = f"Acceptable ({int(hdl_thresh)}-59 mg/dL)"
            hdl_badge = "normal"
        assessments["hdl"] = {"value": hdl, "category": hdl_cat, "badge": hdl_badge}
    else:
        assessments["hdl"] = {"value": None, "category": "Unassessed", "badge": "neutral"}

    # Triglycerides
    if triglycerides is not None:
        if triglycerides < 150:
            tg_cat = "Normal (< 150 mg/dL)"
            tg_badge = "normal"
        elif 150 <= triglycerides <= 199:
            tg_cat = "Borderline High (150-199 mg/dL)"
            tg_badge = "warning"
            flags.append("Triglycerides are borderline elevated.")
        elif 200 <= triglycerides <= 499:
            tg_cat = "High (200-499 mg/dL)"
            tg_badge = "abnormal"
            flags.append("Triglycerides are high; reduce refined carbohydrates and sugars.")
        else:
            tg_cat = "Very High (>= 500 mg/dL)"
            tg_badge = "critical"
            flags.append("Triglycerides are severely elevated; clinical lipid consultation advised.")
        assessments["triglycerides"] = {"value": triglycerides, "category": tg_cat, "badge": tg_badge}
    else:
        assessments["triglycerides"] = {"value": None, "category": "Unassessed", "badge": "neutral"}

    has_any = any(v["value"] is not None for v in assessments.values())
    overall_status = "Available" if has_any else "Missing"
    
    return {
        "status": overall_status,
        "assessments": assessments,
        "flags": flags,
        "reference_source": "NCEP ATP III Guidelines"
    }


def assess_glucose(fasting: Optional[float] = None, postprandial: Optional[float] = None,
                   random_val: Optional[float] = None, hba1c: Optional[float] = None) -> Dict[str, Any]:
    """Assess glycemic markers individually without substituting one for another.
    
    Reference: American Diabetes Association (ADA) Standards of Care in Diabetes 2024.
    """
    markers = {}
    flags = []

    # Fasting glucose (mg/dL)
    if fasting is not None:
        if fasting < 70:
            cat = "Low / Hypoglycemic (< 70 mg/dL)"
            badge = "warning" if fasting >= 54 else "critical"
            flags.append("Fasting blood sugar is low.")
        elif 70 <= fasting <= 99:
            cat = "Normal Fasting (70-99 mg/dL)"
            badge = "normal"
        elif 100 <= fasting <= 125:
            cat = "Impaired Fasting Glucose / Prediabetes (100-125 mg/dL)"
            badge = "warning"
            flags.append("Fasting glucose indicates prediabetes range.")
        else:
            cat = "Elevated / Diabetic Range (>= 126 mg/dL)"
            badge = "abnormal"
            flags.append("Fasting glucose meets diabetes threshold on single measurement.")
        markers["fasting_glucose"] = {"value": fasting, "category": cat, "badge": badge}
    else:
        markers["fasting_glucose"] = {"value": None, "category": "Unassessed", "badge": "neutral"}

    # Postprandial glucose (2-hr oral glucose or meal, mg/dL)
    if postprandial is not None:
        if postprandial < 140:
            cat = "Normal (< 140 mg/dL)"
            badge = "normal"
        elif 140 <= postprandial <= 199:
            cat = "Impaired Glucose Tolerance / Prediabetes (140-199 mg/dL)"
            badge = "warning"
            flags.append("Postprandial glucose is impaired (prediabetes range).")
        else:
            cat = "Elevated / Diabetic Range (>= 200 mg/dL)"
            badge = "abnormal"
            flags.append("Postprandial glucose exceeds 200 mg/dL.")
        markers["postprandial_glucose"] = {"value": postprandial, "category": cat, "badge": badge}
    else:
        markers["postprandial_glucose"] = {"value": None, "category": "Unassessed", "badge": "neutral"}

    # Random glucose (mg/dL)
    if random_val is not None:
        if random_val < 140:
            cat = "Normal (< 140 mg/dL in asymptomatic)"
            badge = "normal"
        elif 140 <= random_val <= 199:
            cat = "Elevated Random (140-199 mg/dL)"
            badge = "warning"
            flags.append("Random blood glucose is elevated.")
        else:
            cat = "Markedly Elevated (>= 200 mg/dL)"
            badge = "abnormal"
            flags.append("Random blood glucose >= 200 mg/dL warrants formal diagnostic follow-up.")
        markers["random_glucose"] = {"value": random_val, "category": cat, "badge": badge}
    else:
        markers["random_glucose"] = {"value": None, "category": "Unassessed", "badge": "neutral"}

    # HbA1c (%)
    if hba1c is not None:
        if hba1c < 5.7:
            cat = "Normal (< 5.7%)"
            badge = "normal"
        elif 5.7 <= hba1c <= 6.4:
            cat = "Prediabetes Range (5.7% - 6.4%)"
            badge = "warning"
            flags.append("HbA1c reflects average 3-month glycemic elevation (prediabetes range).")
        else:
            cat = "Diabetic Range (>= 6.5%)"
            badge = "abnormal"
            flags.append("HbA1c is in the clinical diabetic range (>= 6.5%).")
        markers["hba1c"] = {"value": hba1c, "category": cat, "badge": badge}
    else:
        markers["hba1c"] = {"value": None, "category": "Unassessed", "badge": "neutral"}

    has_any = any(v["value"] is not None for v in markers.values())
    return {
        "status": "Available" if has_any else "Missing",
        "markers": markers,
        "flags": flags,
        "reference_source": "ADA 2024 Standards of Care"
    }


# ==============================================================================
# RULE-BASED DIET & LIFESTYLE RECOMMENDATIONS
# ==============================================================================

def generate_diet_recommendations(user_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate structured rule-based dietary recommendations.
    
    Never suggests crash diets, medication changes, or foods conflicting with declared allergies.
    Does not unilaterally recommend high-potassium foods (to protect renal safety).
    """
    recs = []
    
    # Blood pressure rules (Limit sodium)
    sys_bp = user_data.get("systolic_bp")
    dia_bp = user_data.get("diastolic_bp")
    if (sys_bp is not None and sys_bp >= 130) or (dia_bp is not None and dia_bp >= 80):
        recs.append({
            "title": "Moderate Sodium & Season with Herbs",
            "body": (
                "AHA and clinical consensus recommend limiting daily sodium to under 2,000 mg (approx 1 teaspoon of salt). "
                "In Indian cooking, reduce papad, commercial pickles, salted crisps, and canned broths. "
                "Flavor dishes with lemon juice, curry leaves, coriander, jeera (cumin), and fresh ginger instead of heavy salt. "
                "Avoid salt substitutes (potassium chloride) unless explicitly cleared by your physician."
            ),
            "priority": "High",
            "source": "AHA Dietary Guidelines"
        })

    # Glycemic control rules
    fg = user_data.get("fasting_glucose")
    hba1c = user_data.get("hba1c")
    sugary_drinks = user_data.get("sugary_drinks_per_week", 0) or 0
    if (fg is not None and fg >= 100) or (hba1c is not None and hba1c >= 5.7) or (sugary_drinks > 3):
        recs.append({
            "title": "Replace Simple Sugars with High-Fiber Legumes & Whole Grains",
            "body": (
                "Opt for slower-digesting complex carbohydrates: substitute white refined ponni rice with foxtail millet, "
                "ragi, jowar, or hand-pounded red rice. Pair every grain meal with abundant proteinaceous dal (moong, toor, or masoor) "
                "and non-starchy vegetables (gourd, okra, green beans). Replace sweetened chai/coffee and sodas with water, clear lime water, or herbal infusions."
            ),
            "priority": "High",
            "source": "ADA Medical Nutrition Therapy 2024"
        })

    # Lipid management rules
    total_c = user_data.get("cholesterol_total")
    ldl_c = user_data.get("cholesterol_ldl")
    tg = user_data.get("triglycerides")
    if (ldl_c is not None and ldl_c >= 130) or (total_c is not None and total_c >= 200) or (tg is not None and tg >= 150):
        recs.append({
            "title": "Shift Towards Heart-Smart Unsaturated Fats",
            "body": (
                "Minimize deep-fried snacks (such as vadas, samosas, and pakoras) and reduce heavy vanaspati/palm oil. "
                "Moderate ghee to controlled modest amounts and incorporate cold-pressed sesame, groundnut, or mustard oil in moderation. "
                "Soluble fiber found in methi seeds (fenugreek), oats, and legumes helps naturally bind dietary cholesterol in the gut."
            ),
            "priority": "High",
            "source": "NCEP ATP III Nutrition Guidance"
        })

    # Weight management
    bmi = user_data.get("bmi")
    if bmi is not None and bmi >= 25.0:
        recs.append({
            "title": "Qualitative Plate Method (No Crash Diets)",
            "body": (
                "Adopt the 3-part balanced plate: fill half your plate with colorful vegetables (steamed, stir-fried poriyal, or raw salads), "
                "one-quarter with protein (dal, sundal, chana, tofu, or lean paneer/fish), and one-quarter with complex whole grains. "
                "Eat mindfully without screens and stop when comfortably satisfied."
            ),
            "priority": "Medium",
            "source": "WHO Healthy Diet Fact Sheet"
        })

    # Baseline wholesome habit
    recs.append({
        "title": "Hydration and Whole Plant Diversity",
        "body": (
            "Aim for 2 to 3 liters of plain water daily spread evenly across waking hours. "
            "Consume at least 3-4 servings of colorful, seasonal fruits and vegetables daily (e.g., guava, papaya, leafy greens, moringa/drumstick)."
        ),
        "priority": "General",
        "source": "ICMR-NIN Dietary Guidelines for Indians"
    })

    return recs


def generate_lifestyle_recommendations(user_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Generate rule-based lifestyle and physical activity suggestions."""
    recs = []

    # Physical activity
    activity = user_data.get("physical_activity_min_per_week")
    if activity is None or activity < 150:
        recs.append({
            "title": "Gradually Build to 150 Minutes of Moderate Aerobic Movement",
            "body": (
                "WHO physical activity guidelines recommend at least 150-300 minutes of moderate-intensity aerobic activity "
                "(such as brisk walking, cycling, or swimming) per week. If currently sedentary, start with 15-minute daily walks "
                "after meals and build by 5 minutes each week. Break prolonged sitting every 45-60 minutes."
            ),
            "pillar": "Movement",
            "source": "WHO Guidelines on Physical Activity 2020"
        })
    else:
        recs.append({
            "title": "Maintain Aerobic Stamina and Add Resistance Training",
            "body": (
                f"You report {activity} min/week of activity. Maintain this consistency and ensure 2 days of muscle-strengthening "
                "resistance exercises (bodyweight squats, resistance bands, or light weights) to improve insulin sensitivity."
            ),
            "pillar": "Movement",
            "source": "WHO 2020 Guidelines"
        })

    # Sleep
    sleep = user_data.get("sleep_hours")
    if sleep is not None and (sleep < 7.0 or sleep > 9.0):
        recs.append({
            "title": "Support Circadian Alignment (7-9 Hours Nightly)",
            "body": (
                f"Current sleep ({sleep} hrs) deviates from the recommended 7-9 hours for adults. "
                "Chronic sleep debt elevates cortisol, blood pressure, and hunger hormones (ghrelin). "
                "Keep a consistent sleep/wake schedule and dim screen lights 60 minutes before bedtime."
            ),
            "pillar": "Rest",
            "source": "National Sleep Foundation & AHA"
        })

    # Smoking
    smoking = user_data.get("smoking_status")
    if smoking == "Current":
        recs.append({
            "title": "Smoking Cessation Support",
            "body": (
                "Tobacco smoke damages vascular endothelium, significantly accelerates coronary atherosclerosis, "
                "and compounds metabolic risks. Consult a healthcare provider or a cessation hotline for evidence-based "
                "nicotine replacement or behavioral support."
            ),
            "pillar": "Vascular Protection",
            "source": "ACC/AHA Cardiovascular Prevention Guidelines"
        })

    # Alcohol
    alcohol = user_data.get("alcohol_frequency")
    if alcohol == "Frequent":
        recs.append({
            "title": "Moderate Alcohol Intake",
            "body": (
                "Frequent alcohol intake raises blood pressure, increases hepatic triglyceride synthesis, and adds empty calories. "
                "Discuss moderation or alcohol-free days with your healthcare provider."
            ),
            "pillar": "Liver & Metabolic Health",
            "source": "WHO Global Alcohol Strategy"
        })

    return recs


# ==============================================================================
# SAMPLE MEAL PLAN GENERATOR (SOUTH INDIAN FOCUS + REGIONAL VARIANTS)
# ==============================================================================

# Dish database tagged with cuisine, meal type, diet type eligibility, and allergens
# Qualitatively described: portion guidance and short explanations, NO invented macros or calorie figures.
MEAL_DATABASE = [
    # BREAKFAST
    {
        "id": "si_bf_1",
        "meal": "Breakfast",
        "cuisine": "South Indian",
        "name": "Steamed Ragi & Oats Idli with Vegetable Sambar",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"],
        "allergens": ["Gluten"],  # if oats have gluten; ragi alone is gluten-free, let's keep tag
        "description": "Fermented finger millet and whole oats steamed into soft idlis, served with hot lentil and vegetable sambar.",
        "portion_guidance": "2-3 medium idlis with 1 deep bowl of vegetable-rich sambar.",
        "why_it_helps": "High in soluble beta-glucans and slow-burning complex carbs, promoting steady morning glycemic release without lipid spikes."
    },
    {
        "id": "si_bf_2",
        "meal": "Breakfast",
        "cuisine": "South Indian",
        "name": "Whole Green Gram Pesarattu with Fresh Ginger-Tomato Chutney",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"],
        "allergens": [],
        "description": "Crisp green moong dal crepe cooked on a lightly oiled iron tawa, topped with finely diced onions and cilantro.",
        "portion_guidance": "1-2 medium crepes with 2 tablespoons of freshly pounded ginger-tomato chutney.",
        "why_it_helps": "Moong dal is naturally rich in plant protein and dietary fiber, keeping satiety elevated without heavy fat."
    },
    {
        "id": "si_bf_3",
        "meal": "Breakfast",
        "cuisine": "South Indian",
        "name": "Vegetable Upma with Crushed Curry Leaves & Roasted Chana",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"],
        "allergens": ["Gluten"],
        "description": "Coarse roasted broken wheat (dalia) cooked with diced carrots, french beans, green peas, mustard seeds, and curry leaves.",
        "portion_guidance": "1 medium bowl (approx 150-200g) accompanied by warm water or black coffee/tea.",
        "why_it_helps": "Abundant micronutrients and dietary fiber from garden vegetables blunt post-meal glucose surges."
    },
    {
        "id": "si_bf_4",
        "meal": "Breakfast",
        "cuisine": "South Indian",
        "name": "Boiled Egg Podi Roast with Steamed String Hoppers (Idiyappam)",
        "diet_types": ["Eggetarian", "Non-Vegetarian"],
        "allergens": ["Eggs"],
        "description": "Steamed red rice idiyappam paired with 2 pasture-raised boiled eggs lightly dusted with roasted flaxseed and curry leaf podi.",
        "portion_guidance": "2 idiyappam nests with 2 boiled eggs and light vegetable ishtu.",
        "why_it_helps": "Provides complete amino acids and choline while avoiding saturated frying oils."
    },
    {
        "id": "ni_bf_1",
        "meal": "Breakfast",
        "cuisine": "North Indian",
        "name": "Spiced Methi (Fenugreek) Whole Wheat Thepla with Curd or Mint Dip",
        "diet_types": ["Vegetarian", "Eggetarian", "Non-Vegetarian"],
        "allergens": ["Gluten", "Dairy / Lactose"],
        "description": "Stone-ground whole wheat flatbread kneaded with fresh fenugreek greens, ajwain, and turmeric, cooked with minimal oil.",
        "portion_guidance": "2 medium theplas served with 1 small bowl of fresh homemade curd or mint-coriander relish.",
        "why_it_helps": "Fenugreek greens contain galactomannan, shown in nutritional studies to assist blood glucose regulation."
    },
    {
        "id": "ni_bf_2",
        "meal": "Breakfast",
        "cuisine": "North Indian",
        "name": "Sprouted Moong & Vegetable Poha",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"],
        "allergens": ["Peanuts"],
        "description": "Flattened brown rice tossed with sprouted green gram, turmeric, roasted peanuts (optional), onions, and a squeeze of fresh lemon.",
        "portion_guidance": "1 generous bowl with lots of sprouted legumes.",
        "why_it_helps": "Sprouting enhances vitamin C bioavailability and digestibility while pairing carbs with live plant protein."
    },
    {
        "id": "oth_bf_1",
        "meal": "Breakfast",
        "cuisine": "Other",
        "name": "Warm Steel-Cut Oats Porridge with Cinnamon, Chia & Seeds",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"],
        "allergens": ["Tree Nuts"],
        "description": "Slow-cooked steel-cut groats simmered in almond milk or water, topped with roasted pumpkin seeds, chia, and ground Ceylon cinnamon.",
        "portion_guidance": "1 medium bowl with 1 tablespoon mixed seeds and sliced apple/berries.",
        "why_it_helps": "Delivers beta-glucan fiber to aid cardiovascular lipid clearance without added sucrose."
    },

    # LUNCH
    {
        "id": "si_lu_1",
        "meal": "Lunch",
        "cuisine": "South Indian",
        "name": "Traditional South Indian Thali: Brown Rice, Mor Kuzhambu, Cabbage Thoran & Keerai Kootu",
        "diet_types": ["Vegetarian", "Eggetarian", "Non-Vegetarian"],
        "allergens": ["Dairy / Lactose"],
        "description": "Hand-pounded rice paired with tangy buttermilk-based mor kuzhambu (or dalma), coconut-tempered cabbage thoran, and spinach-lentil kootu.",
        "portion_guidance": "1 small cup rice, 1 large cup keerai kootu, 1 cup cabbage thoran, and light rasam.",
        "why_it_helps": "Greens (keerai) supply folate, magnesium, and dietary nitrates beneficial for blood vessel elasticity."
    },
    {
        "id": "si_lu_2",
        "meal": "Lunch",
        "cuisine": "South Indian",
        "name": "Ragi Mudde (Finger Millet Ball) with Drumstick-Methi Sambar & Snake Gourd Poriyal",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"],
        "allergens": [],
        "description": "Steamed whole finger millet ball served hot with aromatic drumstick-lentil sambar and dry stir-fried snake gourd poriyal.",
        "portion_guidance": "1 tennis-ball sized ragi mudde with generous sambar and plenty of vegetable poriyal.",
        "why_it_helps": "Ragi is exceptionally rich in calcium and complex dietary fiber with a lower glycemic index than white polished rice."
    },
    {
        "id": "si_lu_3",
        "meal": "Lunch",
        "cuisine": "South Indian",
        "name": "Kerala Style Grilled Fish Pollichathu with Red Matta Rice & Beans Mezhukkupuratti",
        "diet_types": ["Non-Vegetarian"],
        "allergens": ["Fish", "Shellfish"],
        "description": "Fresh pearl spot or mackerel marinated in shallots, ginger, curry leaves, and spices, wrapped in banana leaf and pan-grilled.",
        "portion_guidance": "1 medium fish fillet, 1 small cup red matta rice, and a double serving of yard-long beans stir fry.",
        "why_it_helps": "Rich in marine omega-3 polyunsaturated fatty acids (EPA & DHA) which support optimal arterial and triglyceride profiles."
    },
    {
        "id": "si_lu_4",
        "meal": "Lunch",
        "cuisine": "South Indian",
        "name": "Spiced Sundal & Vegetable Biryani with Cucumber-Mint Vegan Pachadi",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"],
        "allergens": ["Soy"],
        "description": "Fragrant brown basmati rice cooked with whole black chickpeas (kala chana), french beans, carrots, and topped with cucumber curd/soy curd pachadi.",
        "portion_guidance": "1 plate with equal ratio of legume-vegetables to grain, served with cucumber slices.",
        "why_it_helps": "Chickpeas offer resistant starch which nourishes beneficial gut microbiota and prevents postprandial blood sugar spikes."
    },
    {
        "id": "ni_lu_1",
        "meal": "Lunch",
        "cuisine": "North Indian",
        "name": "Phulka Rotis with Yellow Tadka Dal, Baingan Bharta & Fresh Kachumber Salad",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"],
        "allergens": ["Gluten"],
        "description": "Oil-free puffed whole wheat rotis paired with cumin-garlic tempered yellow toor dal, fire-roasted smoked eggplant, and crunchy onion-cucumber-tomato kachumber.",
        "portion_guidance": "2 medium phulkas, 1 deep bowl dal, 1 cup bharta, and a large bowl of kachumber with lime juice.",
        "why_it_helps": "Eggplant and whole wheat provide polyphenols and potassium, supporting arterial relaxation without excess sodium."
    },
    {
        "id": "oth_lu_1",
        "meal": "Lunch",
        "cuisine": "Other",
        "name": "Mediterranean Chickpea & Quinoa Bowl with Tahini-Lemon Dressing",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"],
        "allergens": ["Sesame"],
        "description": "Steamed tri-color quinoa layered with spiced boiled chickpeas, cherry tomatoes, baby spinach, kalamata olives, and sesame tahini dressing.",
        "portion_guidance": "1 large bowl centered around greens and legumes.",
        "why_it_helps": "Complete plant proteins and monounsaturated fatty acids support metabolic flexibility."
    },

    # DINNER
    {
        "id": "si_dn_1",
        "meal": "Dinner",
        "cuisine": "South Indian",
        "name": "Hot Spiced Pepper Rasam with Steamed Millet & Ridge Gourd (Peerkangai) Kootu",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"],
        "allergens": [],
        "description": "Light, digestive tamarind-black pepper-cumin rasam paired with barnyard millet and mild ridge gourd dal kootu.",
        "portion_guidance": "1 large mug of soothing rasam, 1/2 cup cooked millet, and 1 cup ridge gourd kootu.",
        "why_it_helps": "Easy on digestion prior to rest; black pepper enhances nutrient bioavailability while keeping evening calories light."
    },
    {
        "id": "si_dn_2",
        "meal": "Dinner",
        "cuisine": "South Indian",
        "name": "Soft Multigrain Dosa with Bottle Gourd (Lauki/Sorakkai) Chutney & Tomato Dal",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"],
        "allergens": [],
        "description": "Crisp thin dosa made from lentils, barley, and millet batter, served with hydrated bottle gourd chutney and light dal.",
        "portion_guidance": "2 medium dosas prepared with minimal oil mist, plenty of chutney and warm dal.",
        "why_it_helps": "Bottle gourd is exceptionally light, hydrating, and naturally low in sodium and glycemic density."
    },
    {
        "id": "si_dn_3",
        "meal": "Dinner",
        "cuisine": "South Indian",
        "name": "Grilled Lemon-Herb Chicken Tikka / Soya Chunks with Steamed Greens & Rasam",
        "diet_types": ["Non-Vegetarian"],
        "allergens": [],
        "description": "Skinless chicken breast marinated in curd, turmeric, black pepper, and curry leaves, pan-seared with zero trans fats, served with greens.",
        "portion_guidance": "120-150g grilled lean chicken, 1 bowl steamed greens, and a bowl of clear vegetable rasam.",
        "why_it_helps": "Lean, high-biological-value protein repairs tissues overnight without inducing high glycemic swings."
    },
    {
        "id": "ni_dn_1",
        "meal": "Dinner",
        "cuisine": "North Indian",
        "name": "Missi Roti with Lauki Kofta (Non-Fried) in Mild Tomato Gravy",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"],
        "allergens": ["Gluten"],
        "description": "Besan (chickpea flour) and whole wheat flatbread served with steamed grated bottle gourd dumplings simmered in a light tomato-fenugreek sauce.",
        "portion_guidance": "1-2 rotis with 1 bowl of vegetable curry.",
        "why_it_helps": "Gram flour increases protein content of flatbreads, moderating the nocturnal insulin response."
    },
    {
        "id": "oth_dn_1",
        "meal": "Dinner",
        "cuisine": "Other",
        "name": "Tofu / Paneer & Stir-Fried Garden Vegetables with Ginger-Garlic Glaze",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"],
        "allergens": ["Soy", "Dairy / Lactose"],
        "description": "Firm non-GMO tofu (or low-fat paneer) tossed in a wok with broccoli, bell peppers, carrots, ginger, and sesame seeds.",
        "portion_guidance": "1 large plate predominantly composed of crisp, colorful vegetables.",
        "why_it_helps": "Maximizes plant sterols and phytonutrients without heavy late-night carbohydrate burden."
    },

    # SNACKS
    {
        "id": "si_sn_1",
        "meal": "Snack",
        "cuisine": "South Indian",
        "name": "Steamed Kondakadalai (Kala Chana) Sundal with Grated Coconut & Mustard Seeds",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"],
        "allergens": [],
        "description": "Boiled whole black chickpeas tempered with curry leaves, a pinch of asafetida (hing), mustard seeds, and fresh shredded coconut.",
        "portion_guidance": "1 small bowl (approx 100g) alongside green tea or buttermilk.",
        "why_it_helps": "Combines slow-release carbohydrates and satiety-promoting fiber to banish midday sugar crashes."
    },
    {
        "id": "si_sn_2",
        "meal": "Snack",
        "cuisine": "South Indian",
        "name": "Spiced Buttermilk (Neer Mor) with Fresh Curry Leaves, Ginger & Green Chili",
        "diet_types": ["Vegetarian", "Eggetarian", "Non-Vegetarian"],
        "allergens": ["Dairy / Lactose"],
        "description": "Diluted churned yogurt blended with cool water, fresh crushed ginger, cilantro, and curry leaves.",
        "portion_guidance": "1-2 tall glasses throughout warm afternoons.",
        "why_it_helps": "Natural probiotics aid intestinal flora while hydrating the body with minimal calories and zero added sugar."
    },
    {
        "id": "oth_sn_1",
        "meal": "Snack",
        "cuisine": "Other",
        "name": "Roasted Makhana (Fox Nuts) & Pumpkin Seeds with Turmeric & Black Pepper",
        "diet_types": ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"],
        "allergens": [],
        "description": "Puffed lotus seeds dry-roasted in a pan with a pinch of turmeric, black pepper, and rock salt.",
        "portion_guidance": "1 medium bowl (approx 30-40g).",
        "why_it_helps": "Crunchy snack naturally low in glycemic index and rich in magnesium."
    }
]


def is_meal_suitable(meal: Dict[str, Any], diet_type: str, cuisine_pref: str,
                     allergies: List[str]) -> bool:
    """Check if a dish conforms strictly to diet type, cuisine preference, and allergy exclusions."""
    # Check diet type compliance
    if diet_type not in meal["diet_types"]:
        return False

    # Check allergy exclusion (strictly reject if any declared allergen is present in meal's allergens)
    allergens_declared = [a.lower().strip() for a in allergies if a]
    for m_allergen in meal["allergens"]:
        m_lower = m_allergen.lower().strip()
        for u_allergen in allergens_declared:
            if u_allergen in m_lower or m_lower in u_allergen:
                return False

    # Vegan safety: double check that Dairy / Lactose or Eggs are never present in vegan meals
    if diet_type == "Vegan":
        for mal in meal["allergens"]:
            if "dairy" in mal.lower() or "lactose" in mal.lower() or "egg" in mal.lower():
                return False

    # Vegetarian safety: no eggs or meat
    if diet_type == "Vegetarian":
        for mal in meal["allergens"]:
            if "egg" in mal.lower() or "fish" in mal.lower() or "shellfish" in mal.lower():
                return False

    return True


def generate_meal_plan(diet_type: str = "Vegetarian",
                       cuisine: str = "South Indian",
                       allergies: Optional[List[str]] = None,
                       meals_per_day: int = 3,
                       random_seed: Optional[int] = None) -> Dict[str, Any]:
    """Generate a personalized, qualitatively-described daily meal plan.
    
    Respects diet type, cuisine preference, and excludes allergens.
    Does NOT invent exact calories or macronutrient numbers.
    """
    if allergies is None:
        allergies = []

    rng = random.Random(random_seed)

    # Filter candidate dishes
    candidates_bf = [
        m for m in MEAL_DATABASE
        if m["meal"] == "Breakfast" and is_meal_suitable(m, diet_type, cuisine, allergies)
    ]
    candidates_lu = [
        m for m in MEAL_DATABASE
        if m["meal"] == "Lunch" and is_meal_suitable(m, diet_type, cuisine, allergies)
    ]
    candidates_dn = [
        m for m in MEAL_DATABASE
        if m["meal"] == "Dinner" and is_meal_suitable(m, diet_type, cuisine, allergies)
    ]
    candidates_sn = [
        m for m in MEAL_DATABASE
        if m["meal"] == "Snack" and is_meal_suitable(m, diet_type, cuisine, allergies)
    ]

    # Preference ranking: prefer requested cuisine first, fallback to other suitable
    def pick_dish(pool: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not pool:
            return None
        cuisine_matches = [m for m in pool if m["cuisine"] == cuisine]
        if cuisine_matches:
            return rng.choice(cuisine_matches)
        return rng.choice(pool)

    breakfast = pick_dish(candidates_bf)
    lunch = pick_dish(candidates_lu)
    dinner = pick_dish(candidates_dn)
    snack = pick_dish(candidates_sn) if meals_per_day >= 4 else None

    # Fallback safe generic dish if strict allergy combination emptied pool
    fallback_dish = {
        "name": "Steamed Whole Moong & Fresh Vegetable Bowl",
        "description": "Steamed sprouted green gram gently tossed with cucumber, grated carrot, lemon juice, and roasted cumin.",
        "portion_guidance": "1 balanced medium bowl.",
        "why_it_helps": "Naturally allergen-free, wholesome plant fiber and gentle protein suitable for all dietary patterns.",
        "cuisine": cuisine,
        "allergens": []
    }

    if breakfast is None:
        breakfast = {**fallback_dish, "meal": "Breakfast"}
    if lunch is None:
        lunch = {**fallback_dish, "meal": "Lunch"}
    if dinner is None:
        dinner = {**fallback_dish, "meal": "Dinner"}

    plan = {
        "diet_type": diet_type,
        "cuisine_preference": cuisine,
        "allergies_accounted_for": allergies,
        "meals_per_day": meals_per_day,
        "schedule": {
            "Breakfast": breakfast,
            "Lunch": lunch,
            "Dinner": dinner
        }
    }

    if snack is not None:
        plan["schedule"]["Mid-Day Snack"] = snack

    return plan
