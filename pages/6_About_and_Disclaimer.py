"""About & Clinical Disclaimer Page for HealthRisk AI."""

import streamlit as st
from src.ui_components import inject_custom_css, render_hero, render_footer

inject_custom_css()

render_hero(
    title="About & Clinical Disclaimer",
    subtitle=(
        "Core clinical references, regulatory medical disclaimers, scientific methodologies, "
        "and architectural documentation behind HealthRisk AI."
    ),
    badge_text="Ethics, Evidence & Transparency"
)

# Mandatory Prominent Medical Disclaimer
st.markdown("""
<div style="background: rgba(239, 68, 68, 0.12); border: 2px solid #EF4444; border-radius: 16px; padding: 1.5rem 2rem; margin-bottom: 2rem;">
    <h3 style="color: #F87171; margin-top: 0; display: flex; align-items: center; gap: 0.5rem;">
        IMPORTANT MEDICAL DISCLAIMER
    </h3>
    <p style="font-size: 0.95rem; color: #FEE2E2; line-height: 1.6;">
        HealthRisk AI is strictly an <strong>educational and informational technology prototype</strong> designed to illustrate
        data engineering, machine learning pipelines, and nutritional decision-support concepts.
    </p>
    <ul style="font-size: 0.92rem; color: #FEE2E2; line-height: 1.6; padding-left: 1.2rem;">
        <li><strong>Non-Diagnostic System:</strong> This software is NOT a medical device, diagnostic test, or clinical decision support system approved by the CDSCO, US FDA, EMA, or any national health agency.</li>
        <li><strong>Not Medical Advice:</strong> Content, scores, predictions, and meal plans provided by this prototype do not constitute medical, nutritional, diagnostic, or pharmacotherapeutic advice.</li>
        <li><strong>Contextual Professional Interpretation:</strong> Biological measurements and laboratory markers can vary due to acute illness, medications, diurnal variation, and sample handling. <strong>Always consult a licensed physician, cardiologist, endocrinologist, or registered dietitian</strong> to interpret your health parameters in proper medical context.</li>
        <li><strong>Emergencies:</strong> If you are experiencing symptoms such as chest tightness, crushing pain radiating to the jaw/arm, severe shortness of breath, sudden numbness, or acute confusion, do not use this app — seek immediate emergency medical care.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Clinical Guideline Citations
st.markdown("### Authoritative Clinical Guidelines & Evidence Base")
st.markdown("All deterministic evaluation rules and benchmark thresholds implemented in this system are derived from peer-reviewed clinical guidelines:")

col_ref1, col_ref2 = st.columns(2)

with col_ref1:
    st.markdown("""
    <div class="glass-card">
        <h4 style="color: #00D2BA; margin-top:0;">1. Anthropometrics & BMI</h4>
        <p style="font-size: 0.88rem; color: #CBD5E1; line-height: 1.5;">
            <strong>World Health Organization (WHO):</strong><br>
            • WHO Expert Consultation (2004). <em>Appropriate body-mass index for Asian populations and its implications for policy and intervention strategies.</em> The Lancet, 363(9403), 157-163.<br>
            • WHO Technical Report Series 854: <em>Physical status: the use and interpretation of anthropometry.</em>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <h4 style="color: #3A86FF; margin-top:0;">3. Lipid Profile & Atherosclerosis</h4>
        <p style="font-size: 0.88rem; color: #CBD5E1; line-height: 1.5;">
            <strong>National Cholesterol Education Program (NCEP):</strong><br>
            • Third Report of the National Cholesterol Education Program (NCEP) Expert Panel on Detection, Evaluation, and Treatment of High Blood Cholesterol in Adults (Adult Treatment Panel III - ATP III). <em>Circulation</em>, 106(25), 3143.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_ref2:
    st.markdown("""
    <div class="glass-card">
        <h4 style="color: #FFBE0B; margin-top:0;">2. Blood Pressure & Hypertension</h4>
        <p style="font-size: 0.88rem; color: #CBD5E1; line-height: 1.5;">
            <strong>American College of Cardiology & American Heart Association (ACC/AHA):</strong><br>
            • Whelton PK, et al. (2017). <em>2017 ACC/AHA/AAPA/ABC/ACPM/AGS/APhA/ASH/ASPC/NMA/PCNA Guideline for the Prevention, Detection, Evaluation, and Management of High Blood Pressure in Adults.</em> J Am Coll Cardiol, 71(19), e127-e248.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <h4 style="color: #06D6A0; margin-top:0;">4. Glycemic Control & Diabetes</h4>
        <p style="font-size: 0.88rem; color: #CBD5E1; line-height: 1.5;">
            <strong>American Diabetes Association (ADA):</strong><br>
            • American Diabetes Association (2024). <em>Classification and Diagnosis of Diabetes: Standards of Care in Diabetes—2024.</em> Diabetes Care, 47(Suppl. 1), S20-S42.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="glass-card">
    <h4 style="color: #C084FC; margin-top:0;">5. Indian Dietary & Lifestyle Guidelines</h4>
    <p style="font-size: 0.88rem; color: #CBD5E1; line-height: 1.5;">
        <strong>Indian Council of Medical Research - National Institute of Nutrition (ICMR-NIN):</strong><br>
        • ICMR-NIN (2024). <em>Dietary Guidelines for Indians: A Manual.</em> National Institute of Nutrition, Hyderabad, India.
        Highlights native millet incorporation, dietary fiber, moderation of refined starches, and sodium reduction.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Software Stack & Deployment Readiness
st.markdown("### Software Architecture & Cloud Deployment")
st.markdown("""
- **Python 3.11 Runtime**: Core language for model training and application logic.
- **Streamlit**: Responsive, interactive multi-page frontend framework.
- **Scikit-learn**: Zero-leakage preprocessing transformers (`ColumnTransformer`, `StandardScaler`, `SimpleImputer`) and classifier pipeline.
- **Plotly**: Client-side GPU-accelerated interactive data visualizations.
- **Joblib**: Atomic serialization and deserialization of fitted pipelines.
- **No Paid APIs or Cloud Databases**: Completely self-contained, offline-runnable, and zero-token runtime.
- **Streamlit Community Cloud Ready**: No hardcoded absolute file paths; all assets resolved relative to project root.
""")


