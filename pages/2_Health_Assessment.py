"""Health Assessment Form Page for HealthRisk AI."""

import streamlit as st
from src.ui_components import inject_custom_css, render_hero
from src.validation import validate_health_inputs, calculate_bmi
from src.recommendation_engine import assess_bmi
from src.predict import RiskPredictor

inject_custom_css()

render_hero(
    title="Health Assessment",
    subtitle=(
        "Enter your biometric, lipid, glycemic, and lifestyle measurements. Only essential fields are required; "
        "optional values refine your assessment. Biologically plausible ranges are validated in real time."
    ),
    badge_text="Step 1: Clinical & Lifestyle Input"
)

# Check for demo preset from Home page
if "demo_preset" in st.session_state:
    preset = st.session_state.pop("demo_preset")
    if preset == "moderate":
        st.session_state["form_age"] = 48
        st.session_state["form_sex"] = "Male"
        st.session_state["form_height"] = 172.0
        st.session_state["form_weight"] = 78.0
        st.session_state["form_waist"] = 92.0
        st.session_state["form_sys_bp"] = 132.0
        st.session_state["form_dia_bp"] = 86.0
        st.session_state["form_hr"] = 74.0
        st.session_state["form_chol_tot"] = 215.0
        st.session_state["form_chol_ldl"] = 138.0
        st.session_state["form_chol_hdl"] = 44.0
        st.session_state["form_trig"] = 165.0
        st.session_state["form_fasting_glu"] = 104.0
        st.session_state["form_hba1c"] = 5.8
        st.session_state["form_activity"] = 90
        st.session_state["form_sleep"] = 6.5
        st.session_state["form_water"] = 2.0
        st.session_state["form_smoking"] = "Former"
        st.session_state["form_alcohol"] = "Occasional"
        st.session_state["form_fruit_veg"] = 3
        st.session_state["form_sugary_drinks"] = 3
        st.session_state["form_fh_dia"] = True
        st.session_state["form_fh_heart"] = False
        st.session_state["form_diet_type"] = "Vegetarian"
        st.session_state["form_cuisine"] = "South Indian"
        st.session_state["form_allergies"] = []
        st.session_state["form_budget"] = 400
        st.info("Loaded demo profile: 48-year-old male with borderline BP, impaired fasting glucose, and moderate lipid elevation.")
    elif preset == "high":
        st.session_state["form_age"] = 62
        st.session_state["form_sex"] = "Female"
        st.session_state["form_height"] = 158.0
        st.session_state["form_weight"] = 82.0
        st.session_state["form_waist"] = 101.0
        st.session_state["form_sys_bp"] = 154.0
        st.session_state["form_dia_bp"] = 96.0
        st.session_state["form_hr"] = 82.0
        st.session_state["form_chol_tot"] = 265.0
        st.session_state["form_chol_ldl"] = 175.0
        st.session_state["form_chol_hdl"] = 36.0
        st.session_state["form_trig"] = 260.0
        st.session_state["form_fasting_glu"] = 155.0
        st.session_state["form_hba1c"] = 7.8
        st.session_state["form_activity"] = 30
        st.session_state["form_sleep"] = 5.5
        st.session_state["form_water"] = 1.5
        st.session_state["form_smoking"] = "Current"
        st.session_state["form_alcohol"] = "Frequent"
        st.session_state["form_fruit_veg"] = 1
        st.session_state["form_sugary_drinks"] = 8
        st.session_state["form_fh_dia"] = True
        st.session_state["form_fh_heart"] = True
        st.session_state["form_diet_type"] = "Vegetarian"
        st.session_state["form_cuisine"] = "South Indian"
        st.session_state["form_allergies"] = []
        st.session_state["form_budget"] = 450
        st.info("Loaded demo profile: 62-year-old female with stage 2 hypertension, diabetic range fasting glycemia, and high LDL.")

# Live BMI Calculator Card in upper section
st.markdown("### 1. Anthropometrics & Core Biometrics")
col_b1, col_b2, col_b3, col_b4 = st.columns(4)

with col_b1:
    age_val = st.number_input(
        "Age (years) *",
        min_value=18,
        max_value=120,
        value=st.session_state.get("form_age", 35),
        step=1,
        help="Adult age (18-120). MINORS NOTE: Standard adult BMI cutoffs do not apply to minors (<18 yrs)."
    )

with col_b2:
    sex_opts = ["Male", "Female", "Other"]
    curr_sex = st.session_state.get("form_sex", "Male")
    sex_idx = sex_opts.index(curr_sex) if curr_sex in sex_opts else 0
    sex_val = st.selectbox(
        "Biological Sex *",
        options=sex_opts,
        index=sex_idx,
        help="Used for sex-stratified clinical lipid thresholds (e.g., HDL targets)."
    )

with col_b3:
    height_val = st.number_input(
        "Height (cm) *",
        min_value=100.0,
        max_value=250.0,
        value=float(st.session_state.get("form_height", 170.0)),
        step=0.5,
        help="Measured barefoot standing upright."
    )

with col_b4:
    weight_val = st.number_input(
        "Weight (kg) *",
        min_value=25.0,
        max_value=300.0,
        value=float(st.session_state.get("form_weight", 70.0)),
        step=0.5,
        help="Measured in light clothing."
    )

# Live BMI display
current_bmi = calculate_bmi(height_val, weight_val)
if current_bmi:
    bmi_eval = assess_bmi(current_bmi, age=age_val)
    st.markdown(f"""
    <div style="background: rgba(0, 210, 186, 0.08); border-left: 4px solid #00D2BA; border-radius: 8px; padding: 0.8rem 1.2rem; margin: 0.8rem 0 1.5rem 0;">
        <span style="font-weight: 700; color: #00D2BA;">Live Calculated BMI:</span>
        <span style="font-size: 1.25rem; font-weight: 800; color: #F8FAFC; margin: 0 0.5rem;">{current_bmi} kg/m²</span>
        <span class="badge badge-{bmi_eval['badge_color']}">{bmi_eval['category']}</span>
        <span style="font-size: 0.85rem; color: #94A3B8; margin-left: 0.75rem;">Formula: Weight(kg) / [Height(m)]²</span>
    </div>
    """, unsafe_allow_html=True)

col_w1, col_w2 = st.columns(2)
with col_w1:
    waist_input = st.number_input(
        "Waist Circumference (cm) (Optional)",
        min_value=40.0,
        max_value=200.0,
        value=float(st.session_state.get("form_waist", 84.0)),
        step=0.5,
        help="Measured at the midpoint between the lower margin of the last palpable rib and the top of the iliac crest."
    )
with col_w2:
    st.markdown("""
    <div style="font-size: 0.85rem; color: #94A3B8; padding-top: 1.5rem;">
        <em>Clinical Note:</em> For Asian Indian adults, abdominal adiposity cutoffs are waist &ge; 90 cm for men and &ge; 80 cm for women (ICMR / WHO Asian guidelines).
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Section 2: Blood Pressure & Vitals
st.markdown("### 2. Blood Pressure & Resting Vitals")
col_bp1, col_bp2, col_bp3 = st.columns(3)

with col_bp1:
    sys_val = st.number_input(
        "Systolic Blood Pressure (mmHg) *",
        min_value=70.0,
        max_value=260.0,
        value=float(st.session_state.get("form_sys_bp", 120.0)),
        step=1.0,
        help="Top number (peak arterial pressure during heart contraction). Normal: < 120 mmHg."
    )

with col_bp2:
    dia_val = st.number_input(
        "Diastolic Blood Pressure (mmHg) *",
        min_value=40.0,
        max_value=160.0,
        value=float(st.session_state.get("form_dia_bp", 80.0)),
        step=1.0,
        help="Bottom number (arterial pressure between heart beats). Normal: < 80 mmHg."
    )

with col_bp3:
    hr_val = st.number_input(
        "Resting Heart Rate (bpm) (Optional)",
        min_value=35.0,
        max_value=200.0,
        value=float(st.session_state.get("form_hr", 72.0)),
        step=1.0,
        help="Measured after 5 minutes of seated rest. Normal resting range: 60-100 bpm."
    )

st.markdown("---")

# Section 3: Lipid Profile
st.markdown("### 3. Lipid Profile (mg/dL) (Optional but Recommended)")
st.caption("Leave empty or toggle if unmeasured. Missing measurements will be preserved as 'Unassessed' and will never be inferred as healthy.")

col_lp_toggle1, col_lp_toggle2 = st.columns([1, 4])
has_lipids = st.checkbox("I have recent Lipid Panel lab results", value=True)

if has_lipids:
    col_l1, col_l2, col_l3, col_l4, col_l5 = st.columns(5)
    with col_l1:
        chol_tot_val = st.number_input(
            "Total Cholesterol",
            min_value=70.0,
            max_value=500.0,
            value=float(st.session_state.get("form_chol_tot", 195.0)),
            step=1.0,
            help="Desirable: < 200 mg/dL"
        )
    with col_l2:
        chol_ldl_val = st.number_input(
            "LDL Cholesterol",
            min_value=20.0,
            max_value=350.0,
            value=float(st.session_state.get("form_chol_ldl", 115.0)),
            step=1.0,
            help="Optimal: < 100 mg/dL, Near Optimal: 100-129 mg/dL"
        )
    with col_l3:
        chol_hdl_val = st.number_input(
            "HDL Cholesterol",
            min_value=10.0,
            max_value=130.0,
            value=float(st.session_state.get("form_chol_hdl", 48.0)),
            step=1.0,
            help="Protective: >= 50 (females), >= 40 (males)"
        )
    with col_l4:
        trig_val = st.number_input(
            "Triglycerides",
            min_value=30.0,
            max_value=1500.0,
            value=float(st.session_state.get("form_trig", 145.0)),
            step=1.0,
            help="Normal: < 150 mg/dL"
        )
    with col_l5:
        vldl_val = st.number_input(
            "VLDL (Optional)",
            min_value=2.0,
            max_value=200.0,
            value=float(st.session_state.get("form_vldl", 25.0)),
            step=1.0,
            help="Normal: 5-30 mg/dL"
        )
else:
    chol_tot_val = None
    chol_ldl_val = None
    chol_hdl_val = None
    trig_val = None
    vldl_val = None

st.markdown("---")

# Section 4: Glycemic Markers
st.markdown("### 4. Blood Glucose & Glycemic Markers")
st.caption(
    "Fasting, postprandial, random, and HbA1c are distinct diagnostic indicators with individual clinical thresholds. "
    "They are evaluated separately with timing context and are NEVER substituted for one another."
)

has_glucose = st.checkbox("I have Blood Glucose or HbA1c lab results", value=True)

if has_glucose:
    cg1, cg2 = st.columns(2)
    with cg1:
        fasting_glu_val = st.number_input(
            "Fasting Blood Glucose (mg/dL)",
            min_value=40.0,
            max_value=500.0,
            value=float(st.session_state.get("form_fasting_glu", 92.0)),
            step=1.0,
            help="Measured after >= 8 hours of overnight fasting. Normal: 70-99 mg/dL."
        )
        fasting_timing = st.selectbox(
            "Fasting Measurement Timing",
            options=["Morning after 8-12 hr fast", "Morning after 6-8 hr fast", "Not strictly fasted"],
            index=0
        )

        postprandial_glu_val = st.number_input(
            "Postprandial Blood Glucose (mg/dL) (Optional)",
            min_value=40.0,
            max_value=500.0,
            value=float(st.session_state.get("form_pp_glu", 130.0)),
            step=1.0,
            help="Measured exactly 2 hours after the start of a meal. Normal: < 140 mg/dL."
        )
        pp_timing = st.selectbox(
            "Postprandial Timing Context",
            options=["Exactly 2 hours post-meal", "1-2 hours post-meal", "More than 2 hours post-meal"],
            index=0
        )

    with cg2:
        hba1c_val = st.number_input(
            "HbA1c Glycated Hemoglobin (%)",
            min_value=3.5,
            max_value=18.0,
            value=float(st.session_state.get("form_hba1c", 5.4)),
            step=0.1,
            help="Reflects 3-month average glycemia. Normal: < 5.7%, Prediabetes: 5.7-6.4%, Diabetes: >= 6.5%."
        )
        hba1c_timing = st.selectbox(
            "HbA1c Lab Test Recency",
            options=["Within past 3 months", "3-6 months ago", "Over 6 months ago"],
            index=0
        )

        random_glu_val = st.number_input(
            "Random Blood Glucose (mg/dL) (Optional)",
            min_value=40.0,
            max_value=500.0,
            value=float(st.session_state.get("form_random_glu", 110.0)),
            step=1.0,
            help="Measured at any unspecified time. Normal: < 140 mg/dL (asymptomatic)."
        )
        random_timing = st.selectbox(
            "Random Timing Context",
            options=["Any time of day without fasting preparation", "Before bedtime", "Post-exercise"],
            index=0
        )
else:
    fasting_glu_val = None
    fasting_timing = "Not recorded"
    postprandial_glu_val = None
    pp_timing = "Not recorded"
    hba1c_val = None
    hba1c_timing = "Not recorded"
    random_glu_val = None
    random_timing = "Not recorded"

st.markdown("---")

# Section 5: Optional Kidney and Liver Markers
with st.expander("5. Optional Renal & Hepatic Function Markers (Click to expand)"):
    st.write("Optional laboratory values used to review kidney filtration or liver enzyme patterns.")
    ck1, ck2, ck3 = st.columns(3)
    with ck1:
        creat_val = st.number_input(
            "Serum Creatinine (mg/dL)",
            min_value=0.2,
            max_value=15.0,
            value=float(st.session_state.get("form_creat", 0.95)),
            step=0.05,
            help="Normal adult range typically 0.6 - 1.3 mg/dL."
        )
        egfr_val = st.number_input(
            "eGFR (mL/min/1.73m²)",
            min_value=5.0,
            max_value=160.0,
            value=float(st.session_state.get("form_egfr", 95.0)),
            step=1.0,
            help="Estimated glomerular filtration rate. Normal: >= 90 mL/min/1.73m²."
        )
    with ck2:
        alt_val = st.number_input(
            "ALT / SGPT (U/L)",
            min_value=2.0,
            max_value=600.0,
            value=float(st.session_state.get("form_alt", 26.0)),
            step=1.0,
            help="Alanine aminotransferase (liver enzyme). Normal typically < 40-50 U/L."
        )
        ast_val = st.number_input(
            "AST / SGOT (U/L)",
            min_value=2.0,
            max_value=600.0,
            value=float(st.session_state.get("form_ast", 24.0)),
            step=1.0,
            help="Aspartate aminotransferase. Normal typically < 40 U/L."
        )
    with ck3:
        bili_val = st.number_input(
            "Total Bilirubin (mg/dL)",
            min_value=0.1,
            max_value=20.0,
            value=float(st.session_state.get("form_bili", 0.8)),
            step=0.1,
            help="Normal adult range: 0.2 - 1.2 mg/dL."
        )

st.markdown("---")

# Section 6: Lifestyle & Family History
st.markdown("### 6. Lifestyle & Family History")
col_ls1, col_ls2, col_ls3 = st.columns(3)

with col_ls1:
    act_val = st.number_input(
        "Moderate/Vigorous Exercise (min/week)",
        min_value=0,
        max_value=1440,
        value=int(st.session_state.get("form_activity", 150)),
        step=15,
        help="WHO guideline: at least 150-300 min/week of moderate aerobic activity."
    )
    sleep_val = st.number_input(
        "Average Nightly Sleep (hours)",
        min_value=2.0,
        max_value=16.0,
        value=float(st.session_state.get("form_sleep", 7.0)),
        step=0.5,
        help="Optimal adult sleep: 7 to 9 hours nightly."
    )
    water_val = st.number_input(
        "Daily Water Intake (Liters)",
        min_value=0.2,
        max_value=10.0,
        value=float(st.session_state.get("form_water", 2.5)),
        step=0.25,
        help="Target: 2.0 to 3.0 Liters daily."
    )

with col_ls2:
    smk_opts = ["Never", "Former", "Current"]
    curr_smk = st.session_state.get("form_smoking", "Never")
    smk_idx = smk_opts.index(curr_smk) if curr_smk in smk_opts else 0
    smk_val = st.selectbox(
        "Tobacco Smoking Status",
        options=smk_opts,
        index=smk_idx,
        help="Current or former cigarette, beedi, or cigar use."
    )

    alc_opts = ["Never", "Occasional", "Frequent"]
    curr_alc = st.session_state.get("form_alcohol", "Never")
    alc_idx = alc_opts.index(curr_alc) if curr_alc in alc_opts else 0
    alc_val = st.selectbox(
        "Alcohol Consumption",
        options=alc_opts,
        index=alc_idx,
        help="Occasional: 1-2 drinks/month; Frequent: multiple drinks/week."
    )

    fruit_veg_val = st.number_input(
        "Fruit & Vegetable Servings / Day",
        min_value=0,
        max_value=15,
        value=int(st.session_state.get("form_fruit_veg", 3)),
        step=1,
        help="1 serving = 1 cup raw leafy greens or 1/2 cup cooked vegetables or 1 medium fruit."
    )

with col_ls3:
    sugary_val = st.number_input(
        "Sugary Drinks / Week",
        min_value=0,
        max_value=50,
        value=int(st.session_state.get("form_sugary_drinks", 2)),
        step=1,
        help="Sweetened sodas, packaged juices, sweetened tea/coffee."
    )

    fh_dia_val = st.checkbox(
        "Family History of Type 2 Diabetes (Parents/Siblings)",
        value=bool(st.session_state.get("form_fh_dia", False))
    )

    fh_heart_val = st.checkbox(
        "Family History of Premature Heart Disease",
        value=bool(st.session_state.get("form_fh_heart", False)),
        help="First-degree male relative < 55 yrs or female relative < 65 yrs with heart attack or stroke."
    )

st.markdown("---")

# Section 7: Preferences & Cultural Nutrition
st.markdown("### 7. Nutrition Preferences & Regional Focus")
col_p1, col_p2, col_p3 = st.columns(3)

with col_p1:
    diet_opts = ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"]
    curr_diet = st.session_state.get("form_diet_type", "Vegetarian")
    diet_idx = diet_opts.index(curr_diet) if curr_diet in diet_opts else 0
    diet_type_val = st.selectbox("Dietary Pattern *", options=diet_opts, index=diet_idx)

    cuisine_opts = ["South Indian", "North Indian", "Other"]
    curr_cuis = st.session_state.get("form_cuisine", "South Indian")
    cuis_idx = cuisine_opts.index(curr_cuis) if curr_cuis in cuisine_opts else 0
    cuisine_val = st.selectbox("Regional Cuisine Focus", options=cuisine_opts, index=cuis_idx)

with col_p2:
    allergy_choices = ["Peanuts", "Tree Nuts", "Dairy / Lactose", "Gluten", "Soy", "Shellfish", "Fish", "Eggs"]
    curr_allergies = st.session_state.get("form_allergies", [])
    allergies_val = st.multiselect(
        "Declared Food Allergies & Sensitivities",
        options=allergy_choices,
        default=[a for a in curr_allergies if a in allergy_choices],
        help="Dishes containing these allergens will be strictly excluded from your meal plan."
    )

    meals_val = st.selectbox(
        "Meals per Day",
        options=[2, 3, 4],
        index=1,
        help="3 meals (Breakfast, Lunch, Dinner) or 4 (including wholesome Mid-Day snack)."
    )

with col_p3:
    budget_val = st.number_input(
        "Estimated Daily Meal Budget (INR)",
        min_value=50,
        max_value=5000,
        value=int(st.session_state.get("form_budget", 350)),
        step=50,
        help="Provides budget-conscious ingredient guidance for local markets."
    )

    goal_opts = [
        "Cardiometabolic Risk Reduction",
        "General Health & Longevity",
        "Weight Management",
        "Blood Sugar Control",
        "Heart Health"
    ]
    goal_val = st.selectbox("Primary Health Goal", options=goal_opts, index=0)

st.markdown("---")

# Submit & Run Assessment Button
if st.button("Analyze Health Profile & Run ML Prediction", type="primary", use_container_width=True):
    raw_payload = {
        "age": age_val,
        "sex": sex_val,
        "height_cm": height_val,
        "weight_kg": weight_val,
        "waist_cm": waist_input,
        "systolic_bp": sys_val,
        "diastolic_bp": dia_val,
        "resting_heart_rate": hr_val,
        "cholesterol_total": chol_tot_val,
        "cholesterol_ldl": chol_ldl_val,
        "cholesterol_hdl": chol_hdl_val,
        "triglycerides": trig_val,
        "cholesterol_vldl": vldl_val,
        "fasting_glucose": fasting_glu_val,
        "fasting_glucose_timing": fasting_timing,
        "postprandial_glucose": postprandial_glu_val,
        "postprandial_glucose_timing": pp_timing,
        "random_glucose": random_glu_val,
        "random_glucose_timing": random_timing,
        "hba1c": hba1c_val,
        "hba1c_timing": hba1c_timing,
        "serum_creatinine": creat_val,
        "egfr": egfr_val,
        "alt_sgpt": alt_val,
        "ast_sgot": ast_val,
        "total_bilirubin": bili_val,
        "physical_activity_min_per_week": act_val,
        "sleep_hours": sleep_val,
        "water_liters": water_val,
        "smoking_status": smk_val,
        "alcohol_frequency": alc_val,
        "fruit_veg_servings": fruit_veg_val,
        "sugary_drinks_per_week": sugary_val,
        "family_history_diabetes": fh_dia_val,
        "family_history_heart_disease": fh_heart_val,
        "diet_type": diet_type_val,
        "cuisine": cuisine_val,
        "allergies": allergies_val,
        "goal": goal_val,
        "meals_per_day": meals_val,
        "daily_budget_inr": budget_val
    }

    # Validate inputs
    is_valid, errors, warnings, sanitized = validate_health_inputs(raw_payload)

    if not is_valid:
        st.error("Please correct the following errors before proceeding:")
        for fld, err_msg in errors.items():
            st.error(f"• **{fld.replace('_', ' ').title()}**: {err_msg}")
    else:
        # Display physiological warnings if any
        if warnings:
            for w_key, w_msg in warnings.items():
                st.warning(f"Advisory: {w_msg}")

        # Run Prediction
        try:
            predictor = RiskPredictor()
            prediction_output = predictor.predict(sanitized)
            
            # Store in session state
            st.session_state["user_profile"] = sanitized
            st.session_state["prediction_result"] = prediction_output
            st.session_state["has_assessment"] = True

            st.success("Assessment processed successfully! Redirecting to Prediction Results...")
            st.switch_page("pages/3_Prediction_Results.py")
        except Exception as e:
            st.error(f"Error during ML inference: {str(e)}")
