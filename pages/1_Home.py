"""Home Page for HealthRisk AI."""

import streamlit as st
from src.ui_components import inject_custom_css, render_hero

inject_custom_css()

# Hero Section
render_hero(
    title="HealthRisk AI",
    subtitle=(
        "An intelligent, transparent cardiometabolic risk analytics and personalized lifestyle prototype. "
        "Enter your health measurements to explore multi-factorial synthetic risk categorization, clinical threshold benchmarks, "
        "and culturally tailored South Indian nutritional meal planning."
    ),
    badge_text="Educational Prototype • Non-Diagnostic"
)

# Experimental Model Notice
st.markdown("""
<div class="notice-pill">
    <strong>Prototype & Educational Disclaimer:</strong> This application demonstrates applied machine learning pipelines,
    evidence-based clinical validation rules, and nutritional engineering. <strong>This is NOT a medical diagnostic device or healthcare provider.</strong>
    All predictive labels ("Lower / Moderate / Higher synthetic risk category") represent synthetic model outputs,
    never clinical diagnoses or absolute disease probabilities. Always consult a licensed physician for medical guidance.
</div>
""", unsafe_allow_html=True)

# Primary Call to Action
col_cta1, col_cta2 = st.columns([1.5, 1])
with col_cta1:
    st.markdown("### Begin Your Health Analytics Assessment")
    st.write(
        "Complete a comprehensive, validated clinical evaluation across anthropometrics, blood pressure, "
        "lipid fractions, glycemic markers, and lifestyle habits. Results are processed locally in real time."
    )
    if st.button("Start Health Assessment", type="primary", use_container_width=True):
        st.switch_page("pages/2_Health_Assessment.py")

with col_cta2:
    st.markdown("### Quick Demo Mode")
    st.write("Want to test the app without typing every measurement? Load an illustrative profile:")
    col_demo1, col_demo2 = st.columns(2)
    with col_demo1:
        if st.button("Load Moderate Risk Profile", use_container_width=True):
            st.session_state["demo_preset"] = "moderate"
            st.switch_page("pages/2_Health_Assessment.py")
    with col_demo2:
        if st.button("Load Higher Risk Profile", use_container_width=True):
            st.session_state["demo_preset"] = "high"
            st.switch_page("pages/2_Health_Assessment.py")

st.markdown("---")

# Supported Measurements Grid
st.markdown("### Supported Health Measurements & Pillars")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="glass-card">
        <h4 style="color: #00D2BA; margin-top:0;">1. Anthropometrics & Vitals</h4>
        <p style="font-size: 0.9rem; color: #94A3B8;">
            • <strong>Age & Biological Sex</strong><br>
            • <strong>Height (cm) & Weight (kg)</strong><br>
            • <strong>Automatic BMI Calculation</strong> (with pediatric advisory notice)<br>
            • <strong>Waist Circumference (cm)</strong><br>
            • <strong>Resting Heart Rate (bpm)</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <h4 style="color: #3A86FF; margin-top:0;">4. Glycemic Markers</h4>
        <p style="font-size: 0.9rem; color: #94A3B8;">
            • <strong>Fasting Blood Glucose (mg/dL)</strong><br>
            • <strong>Postprandial Glucose (mg/dL)</strong><br>
            • <strong>Random Blood Glucose (mg/dL)</strong><br>
            • <strong>HbA1c Glycated Hemoglobin (%)</strong><br>
            • <em>Explicit timing context selectors; never substituted for one another.</em>
        </p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="glass-card">
        <h4 style="color: #FFBE0B; margin-top:0;">2. Blood Pressure</h4>
        <p style="font-size: 0.9rem; color: #94A3B8;">
            • <strong>Systolic & Diastolic BP (mmHg)</strong><br>
            • <strong>ACC/AHA 2017 Categorization</strong> (Normal, Elevated, Stage 1, Stage 2)<br>
            • <strong>Hypertensive Crisis Emergency Alert</strong> (>= 180 / 120 mmHg)<br>
            • <strong>Pulse Pressure Plausibility Check</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <h4 style="color: #C084FC; margin-top:0;">5. Lifestyle & Family History</h4>
        <p style="font-size: 0.9rem; color: #94A3B8;">
            • <strong>Weekly Aerobic Exercise (min/wk)</strong><br>
            • <strong>Daily Sleep Duration (hrs)</strong><br>
            • <strong>Water Intake (L/day)</strong><br>
            • <strong>Smoking & Alcohol Status</strong><br>
            • <strong>Fruit & Veg Servings / Sugary Drinks</strong><br>
            • <strong>Family History of Diabetes / Heart Disease</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="glass-card">
        <h4 style="color: #06D6A0; margin-top:0;">3. Lipid Profile</h4>
        <p style="font-size: 0.9rem; color: #94A3B8;">
            • <strong>Total Cholesterol (mg/dL)</strong><br>
            • <strong>LDL Cholesterol (mg/dL)</strong><br>
            • <strong>HDL Cholesterol (mg/dL)</strong><br>
            • <strong>Triglycerides (mg/dL)</strong><br>
            • <strong>Optional VLDL (mg/dL)</strong><br>
            • <em>NCEP ATP III Guideline cutoffs applied.</em>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <h4 style="color: #F87171; margin-top:0;">6. Diet & Regional Nutrition</h4>
        <p style="font-size: 0.9rem; color: #94A3B8;">
            • <strong>Diet Type</strong>: Vegetarian, Vegan, Eggetarian, Non-Veg<br>
            • <strong>Cuisine Focus</strong>: South Indian, North Indian, Pan-Indian<br>
            • <strong>Strict Allergen Exclusion Filtering</strong><br>
            • <strong>Qualitative Portion & Health Guidance</strong><br>
            • <strong>INR Daily Budget Awareness</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Architectural & Transparency Highlights
st.markdown("### System Architecture & Transparency Highlights")
col_arch1, col_arch2 = st.columns(2)

with col_arch1:
    st.markdown("""
    - **No Cloud APIs or External Data Exfiltration**: Entirely local Scikit-learn inference pipeline.
    - **Strict Preprocessing Alignment**: Same `ColumnTransformer` with median/mode imputation on test/predict runtime.
    - **Transparent Clinical References**: WHO 2004, ACC/AHA 2017, NCEP ATP III, and ADA 2024 Standards of Care.
    """)

with col_arch2:
    st.markdown("""
    - **Safety-First Recommendation Logic**: Never prescribes crash diets, medication alterations, or high potassium unilaterally.
    - **No Missing-Data Hallucinations**: Missing or unassessed lab measurements are distinctly styled in dashed grey, never marked 'healthy'.
    - **Cultural Nutrition**: Focuses on unpolished millets, lentils, whole grams, and regional Indian preparation methods.
    """)


