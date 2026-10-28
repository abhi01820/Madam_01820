"""Prediction Results and Clinical Factor Breakdown Page for HealthRisk AI."""

import streamlit as st
from src.ui_components import (
    inject_custom_css,
    render_hero,
    render_emergency_banner,
    render_metric_card,
    create_risk_gauge_chart,
    create_radar_profile,
    create_probability_distribution_chart,
    render_footer
)
from src.validation import detect_emergency_flags
from src.recommendation_engine import (
    assess_bmi,
    assess_blood_pressure,
    assess_cholesterol,
    assess_glucose,
    generate_diet_recommendations,
    generate_lifestyle_recommendations
)

inject_custom_css()

render_hero(
    title="Prediction Results & Clinical Analysis",
    subtitle=(
        "Comprehensive synthesis of your cardiometabolic metrics, machine learning synthetic risk classification, "
        "and rule-based clinical factor analysis."
    ),
    badge_text="Step 2: Analytics & Insights"
)

# Verify profile in session state
user_profile = st.session_state.get("user_profile")
prediction_result = st.session_state.get("prediction_result")

if not user_profile or not prediction_result:
    st.warning("No assessment data found. Please complete the Health Assessment first or load a sample profile.")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Go to Health Assessment", type="primary"):
            st.switch_page("pages/2_Health_Assessment.py")
    with col_b:
        if st.button("Load Demo Profile"):
            st.session_state["demo_preset"] = "moderate"
            st.switch_page("pages/2_Health_Assessment.py")
    st.stop()

# 1. Check for Emergency Clinical Out-of-Range Flags
emergency_flags = detect_emergency_flags(user_profile)
if emergency_flags:
    render_emergency_banner(emergency_flags)

# 2. Main Risk Category Classification Banner
predicted_category = prediction_result["predicted_category"]
probabilities = prediction_result.get("probabilities", {})

if "Higher" in predicted_category:
    badge_bg = "rgba(255, 90, 95, 0.15)"
    badge_border = "#FF5A5F"
    badge_text_color = "#FF5A5F"
elif "Moderate" in predicted_category:
    badge_bg = "rgba(255, 190, 11, 0.15)"
    badge_border = "#FFBE0B"
    badge_text_color = "#FFBE0B"
else:
    badge_bg = "rgba(0, 210, 186, 0.15)"
    badge_border = "#00D2BA"
    badge_text_color = "#00D2BA"

confidence_pct = probabilities.get(predicted_category, 0.0) * 100

st.markdown(f"""
<div style="background: {badge_bg}; border: 2px solid {badge_border}; border-radius: 16px; padding: 1.5rem 2rem; margin-bottom: 2rem;">
    <div style="font-size: 0.85rem; font-weight: 700; color: #94A3B8; letter-spacing: 0.05em; text-transform: uppercase;">
        Machine Learning Model Output • Trained Pipeline
    </div>
    <div style="font-size: 2.2rem; font-weight: 800; color: {badge_text_color}; margin: 0.3rem 0;">
        {predicted_category}
    </div>
    <div style="font-size: 1rem; color: #F8FAFC; max-width: 850px; line-height: 1.5;">
        Estimated Model Confidence: <strong>{confidence_pct:.1f}%</strong>.
        <em>Important Note:</em> This label is an artificial, multi-factorial category derived from synthetic data patterns.
        It is strictly educational and does not constitute a clinical disease diagnosis or absolute probability of illness.
    </div>
</div>
""", unsafe_allow_html=True)

# 3. Interactive Visualizations Section
st.markdown("### Interactive Visualizations")
col_vis1, col_vis2 = st.columns([1, 1.2])

with col_vis1:
    st.markdown("##### Synthetic Risk Intensity Index")
    fig_gauge = create_risk_gauge_chart(predicted_category, probabilities)
    st.plotly_chart(fig_gauge, use_container_width=True)

    fig_prob = create_probability_distribution_chart(probabilities)
    st.plotly_chart(fig_prob, use_container_width=True)

with col_vis2:
    st.markdown("##### Patient Multi-Pillar Radar vs Healthy Target")
    fig_radar = create_radar_profile(user_profile)
    st.plotly_chart(fig_radar, use_container_width=True)
    st.caption(
        "Radar visualization maps key biometric pillars normalized on a 0-100 scale. "
        "The dashed cyan region marks target healthy bounds; shaded red region reflects current recorded profile."
    )

st.markdown("---")

# 4. Detailed Clinical Pillar Status Cards
st.markdown("### Clinical Measurement Breakdown & Reference Status")

# Assessments
bmi_eval = assess_bmi(user_profile.get("bmi"), age=user_profile.get("age"))
bp_eval = assess_blood_pressure(user_profile.get("systolic_bp"), user_profile.get("diastolic_bp"))
lipid_eval = assess_cholesterol(
    user_profile.get("cholesterol_total"),
    user_profile.get("cholesterol_ldl"),
    user_profile.get("cholesterol_hdl"),
    user_profile.get("triglycerides"),
    sex=user_profile.get("sex", "Male")
)
glucose_eval = assess_glucose(
    fasting=user_profile.get("fasting_glucose"),
    postprandial=user_profile.get("postprandial_glucose"),
    random_val=user_profile.get("random_glucose"),
    hba1c=user_profile.get("hba1c")
)

# Row 1: BMI & Blood Pressure
c_cd1, c_cd2 = st.columns(2)

with c_cd1:
    render_metric_card(
        name="Body Mass Index (BMI)",
        value=user_profile.get("bmi"),
        unit="kg/m²",
        category=bmi_eval["category"],
        badge_color=bmi_eval["badge_color"],
        source="WHO 2004 Criteria"
    )
    st.caption(bmi_eval["message"])

with c_cd2:
    bp_val_str = f"{user_profile.get('systolic_bp')}/{user_profile.get('diastolic_bp')}" if user_profile.get('systolic_bp') else None
    render_metric_card(
        name="Blood Pressure (Systolic / Diastolic)",
        value=bp_val_str,
        unit="mmHg",
        category=bp_eval["category"],
        badge_color=bp_eval["badge_color"],
        source="ACC/AHA 2017 Guidelines"
    )
    st.caption(bp_eval["message"])

# Row 2: Lipids Grid
st.markdown("##### Lipid Profile Status (NCEP ATP III Reference)")
cl1, cl2, cl3, cl4 = st.columns(4)

tot_c = lipid_eval["assessments"]["total"]
with cl1:
    render_metric_card(
        name="Total Cholesterol",
        value=tot_c["value"],
        unit="mg/dL",
        category=tot_c["category"].split(" (")[0],
        badge_color=tot_c["badge"],
        source="NCEP ATP III"
    )

ldl_c = lipid_eval["assessments"]["ldl"]
with cl2:
    render_metric_card(
        name="LDL Cholesterol",
        value=ldl_c["value"],
        unit="mg/dL",
        category=ldl_c["category"].split(" (")[0],
        badge_color=ldl_c["badge"],
        source="NCEP ATP III"
    )

hdl_c = lipid_eval["assessments"]["hdl"]
with cl3:
    render_metric_card(
        name="HDL Cholesterol",
        value=hdl_c["value"],
        unit="mg/dL",
        category=hdl_c["category"].split(" (")[0],
        badge_color=hdl_c["badge"],
        source="Sex-stratified ATP III"
    )

tg_c = lipid_eval["assessments"]["triglycerides"]
with cl4:
    render_metric_card(
        name="Triglycerides",
        value=tg_c["value"],
        unit="mg/dL",
        category=tg_c["category"].split(" (")[0],
        badge_color=tg_c["badge"],
        source="NCEP ATP III"
    )

# Row 3: Glucose Markers
st.markdown("##### Glycemic Markers Status (ADA 2024 Standards)")
cg1, cg2, cg3, cg4 = st.columns(4)

fg_m = glucose_eval["markers"]["fasting_glucose"]
with cg1:
    render_metric_card(
        name="Fasting Glucose",
        value=fg_m["value"],
        unit="mg/dL",
        category=fg_m["category"].split(" (")[0],
        badge_color=fg_m["badge"],
        timing=user_profile.get("fasting_glucose_timing"),
        source="ADA 2024"
    )

pp_m = glucose_eval["markers"]["postprandial_glucose"]
with cg2:
    render_metric_card(
        name="Postprandial Glucose",
        value=pp_m["value"],
        unit="mg/dL",
        category=pp_m["category"].split(" (")[0],
        badge_color=pp_m["badge"],
        timing=user_profile.get("postprandial_glucose_timing"),
        source="ADA 2024"
    )

hb_m = glucose_eval["markers"]["hba1c"]
with cg3:
    render_metric_card(
        name="HbA1c",
        value=hb_m["value"],
        unit="%",
        category=hb_m["category"].split(" (")[0],
        badge_color=hb_m["badge"],
        timing=user_profile.get("hba1c_timing"),
        source="ADA 2024"
    )

rg_m = glucose_eval["markers"]["random_glucose"]
with cg4:
    render_metric_card(
        name="Random Glucose",
        value=rg_m["value"],
        unit="mg/dL",
        category=rg_m["category"].split(" (")[0],
        badge_color=rg_m["badge"],
        timing=user_profile.get("random_glucose_timing"),
        source="ADA 2024"
    )

st.markdown("---")

# 5. Top Contributing Risk Factors
st.markdown("### Top Contributing Risk & Protective Factors")
contributing = prediction_result.get("contributing_factors", [])

if contributing:
    for factor in contributing:
        impact = factor["impact"]
        color = "#FF5A5F" if "Risk" in impact or "High" in impact else "#00D2BA"
        st.markdown(f"""
        <div style="background: rgba(19, 28, 46, 0.6); border-left: 4px solid {color}; border-radius: 10px; padding: 1rem 1.25rem; margin-bottom: 0.8rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                <span style="font-size: 1.05rem; font-weight: 700; color: #F8FAFC;">{factor['factor']}</span>
                <span style="font-size: 0.85rem; font-weight: 700; color: {color};">{factor['impact']} ({factor['value']})</span>
            </div>
            <div style="font-size: 0.9rem; color: #94A3B8;">{factor['description']}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("All recorded parameters align closely with healthy baseline thresholds.")

st.markdown("---")

# 6. Rule-Based Diet & Lifestyle Recommendations
st.markdown("### Evidence-Based Diet & Lifestyle Guidance")
diet_recs = generate_diet_recommendations(user_profile)
life_recs = generate_lifestyle_recommendations(user_profile)

col_r1, col_r2 = st.columns(2)

with col_r1:
    st.markdown("##### Nutritional & Dietary Adjustments")
    for rec in diet_recs:
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size: 1.05rem; font-weight: 700; color: #00D2BA; margin-bottom: 0.4rem;">
                {rec['title']}
            </div>
            <div style="font-size: 0.9rem; color: #CBD5E1; line-height: 1.5; margin-bottom: 0.5rem;">
                {rec['body']}
            </div>
            <div style="font-size: 0.75rem; color: #64748B;">Reference: {rec['source']}</div>
        </div>
        """, unsafe_allow_html=True)

with col_r2:
    st.markdown("##### Physical Activity & Habit Adjustments")
    for lrec in life_recs:
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size: 1.05rem; font-weight: 700; color: #3A86FF; margin-bottom: 0.4rem;">
                {lrec['title']}
            </div>
            <div style="font-size: 0.9rem; color: #CBD5E1; line-height: 1.5; margin-bottom: 0.5rem;">
                {lrec['body']}
            </div>
            <div style="font-size: 0.75rem; color: #64748B;">Reference: {lrec['source']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# 7. Next Steps & Diet Planner CTA
st.markdown("### Recommended Next Steps")
st.markdown("""
1. **Schedule a Clinical Follow-up**: Share your actual lab results with your primary care physician or registered dietitian for comprehensive evaluation.
2. **Re-verify Blood Pressure**: Record 2 seated readings per day (morning and evening) for 5-7 days using an upper-arm automated cuff.
3. **Explore Tailored Meals**: Review our South Indian cultural meal planner designed for your specific diet type and allergy profile.
""")

if st.button("Generate Tailored South Indian Meal Plan", type="primary", use_container_width=True):
    st.switch_page("pages/4_Diet_Planner.py")

render_footer()

