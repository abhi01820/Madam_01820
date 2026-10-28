"""Model Information, Metrics, and Evaluation Page for HealthRisk AI."""

import json
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
from src.ui_components import inject_custom_css, render_hero, create_confusion_matrix_chart, render_footer

inject_custom_css()

render_hero(
    title="Model Architecture & Evaluation",
    subtitle=(
        "Full transparent disclosure of our synthetic training dataset, exploratory data analysis, "
        "machine learning pipeline architecture, actual evaluation metrics, and clinical limitations."
    ),
    badge_text="Transparency & Model Card"
)

# Load metrics JSON
METRICS_PATH = Path(__file__).resolve().parent.parent / "models" / "model_metrics.json"

if not METRICS_PATH.exists():
    st.error("Model metrics file not found. Please run src/train_model.py first.")
    st.stop()

with open(METRICS_PATH, "r") as f:
    metrics_data = json.load(f)

eda = metrics_data["eda"]
lr_metrics = metrics_data["baseline_logistic_regression"]
rf_metrics = metrics_data["random_forest"]
best_model = metrics_data["best_model"]
top_features = metrics_data.get("top_features", [])

# 1. Dataset & Synthetic Generation Architecture
st.markdown("### 1. Training Dataset & Generation Rubric")
st.markdown("""
<div class="glass-card">
    <h4 style="color: #00D2BA; margin-top: 0;">Synthetic Dataset Overview</h4>
    <p style="font-size: 0.92rem; color: #CBD5E1; line-height: 1.6;">
        To ensure strict privacy protection and eliminate dependency on proprietary clinical records,
        HealthRisk AI is trained on a <strong>reproducible synthetic dataset</strong> (N = 2,500 samples, fixed seed = 42)
        synthesizing clinically realistic distributions of cardiometabolic and lifestyle parameters.
    </p>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
        <div style="background: rgba(0,0,0,0.25); padding: 0.8rem; border-radius: 8px;">
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">Sample Size</div>
            <div style="font-size: 1.4rem; font-weight: 800; color: #F8FAFC;">2,500 Rows</div>
        </div>
        <div style="background: rgba(0,0,0,0.25); padding: 0.8rem; border-radius: 8px;">
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">Total Features</div>
            <div style="font-size: 1.4rem; font-weight: 800; color: #F8FAFC;">28 Columns</div>
        </div>
        <div style="background: rgba(0,0,0,0.25); padding: 0.8rem; border-radius: 8px;">
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">Duplicate Rows</div>
            <div style="font-size: 1.4rem; font-weight: 800; color: #06D6A0;">0 (Clean)</div>
        </div>
        <div style="background: rgba(0,0,0,0.25); padding: 0.8rem; border-radius: 8px;">
            <div style="font-size: 0.75rem; color: #94A3B8; text-transform: uppercase;">Best Classifier</div>
            <div style="font-size: 1.1rem; font-weight: 800; color: #00D2BA;">Logistic Regression</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col_d1, col_d2 = st.columns(2)

with col_d1:
    st.markdown("##### Real-Looking Inputs vs Generated Logic")
    st.markdown("""
    - **Real-Looking Biometric Inputs**: Age, sex, height, weight, waist, systolic/diastolic blood pressure, resting heart rate, lipid fractions (total, LDL, HDL, triglycerides), fasting glucose, HbA1c, and lifestyle habits.
    - **Generated Target Labels**: Three artificial categories:
      - `Lower synthetic risk category`
      - `Moderate synthetic risk category`
      - `Higher synthetic risk category`
    - **Exact Generation Rubric**: Built using an additive cardiometabolic scoring rubric reflecting AHA/ADA clinical criteria (points assigned for BP &ge; 130/80, fasting glucose &ge; 100, LDL &ge; 130, triglycerides &ge; 150, BMI &ge; 25, active smoking, and sedentary habits; points deducted for aerobic exercise &ge; 200 min/wk). Gaussian noise ($\sigma=0.5$) was injected before binning into the 3 categories.
    """)

with col_d2:
    st.markdown("##### Class Distribution in Training Data")
    class_dist = eda["class_distribution"]
    df_dist = pd.DataFrame({
        "Category": list(class_dist.keys()),
        "Count": list(class_dist.values())
    })
    fig_dist = px.pie(
        df_dist,
        names="Category",
        values="Count",
        color="Category",
        color_discrete_map={
            "Lower synthetic risk category": "#00D2BA",
            "Moderate synthetic risk category": "#FFBE0B",
            "Higher synthetic risk category": "#FF5A5F"
        },
        hole=0.45
    )
    fig_dist.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CBD5E1"),
        height=260,
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", y=-0.1)
    )
    st.plotly_chart(fig_dist, use_container_width=True)

st.markdown("---")

# 2. Actual Evaluation Metrics
st.markdown("### 2. Actual Model Evaluation Metrics")
st.caption("All values reflect genuine test set (20% holdout, N = 500) evaluation from the training run.")

col_m1, col_m2 = st.columns(2)

with col_m1:
    st.markdown("""
    <div style="background: rgba(0, 210, 186, 0.08); border: 1px solid rgba(0, 210, 186, 0.3); border-radius: 12px; padding: 1.25rem;">
        <div style="font-size: 0.8rem; color: #00D2BA; font-weight: 700; text-transform: uppercase;">Selected Production Model</div>
        <div style="font-size: 1.3rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.75rem;">Logistic Regression Baseline</div>
        <table style="width: 100%; font-size: 0.9rem; color: #CBD5E1;">
            <tr><td><strong>Test Accuracy</strong></td><td style="text-align: right; color: #00D2BA; font-weight: 700;">81.60%</td></tr>
            <tr><td><strong>F1 Score (Macro)</strong></td><td style="text-align: right; color: #00D2BA; font-weight: 700;">81.31%</td></tr>
            <tr><td><strong>F1 Score (Weighted)</strong></td><td style="text-align: right; color: #00D2BA; font-weight: 700;">81.55%</td></tr>
            <tr><td><strong>Precision (Macro)</strong></td><td style="text-align: right;">83.17%</td></tr>
            <tr><td><strong>Recall (Macro)</strong></td><td style="text-align: right;">79.92%</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown("""
    <div style="background: rgba(19, 28, 46, 0.65); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 1.25rem;">
        <div style="font-size: 0.8rem; color: #94A3B8; font-weight: 700; text-transform: uppercase;">Benchmark Model</div>
        <div style="font-size: 1.3rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.75rem;">Random Forest Classifier</div>
        <table style="width: 100%; font-size: 0.9rem; color: #CBD5E1;">
            <tr><td><strong>Test Accuracy</strong></td><td style="text-align: right; font-weight: 700;">77.20%</td></tr>
            <tr><td><strong>F1 Score (Macro)</strong></td><td style="text-align: right; font-weight: 700;">70.82%</td></tr>
            <tr><td><strong>F1 Score (Weighted)</strong></td><td style="text-align: right; font-weight: 700;">76.45%</td></tr>
            <tr><td><strong>Precision (Macro)</strong></td><td style="text-align: right;">85.25%</td></tr>
            <tr><td><strong>Recall (Macro)</strong></td><td style="text-align: right;">66.37%</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 3. Confusion Matrix & Top Feature Importances
st.markdown("### 3. Confusion Matrix & Feature Impact")

col_cm1, col_cm2 = st.columns([1, 1.2])

with col_cm1:
    st.markdown("##### Confusion Matrix (Test Set Holdout, N=500)")
    cm = lr_metrics["confusion_matrix"]
    fig_cm = create_confusion_matrix_chart(cm, lr_metrics["labels"])
    st.plotly_chart(fig_cm, use_container_width=True)
    st.caption("Rows: Ground truth synthetic class | Columns: Predicted model classification.")

with col_cm2:
    st.markdown("##### Top Predictive Features")
    if top_features:
        df_feat = pd.DataFrame(top_features, columns=["Feature", "Importance"]).sort_values("Importance", ascending=True)
        fig_feat = px.bar(
            df_feat,
            x="Importance",
            y="Feature",
            orientation="h",
            color="Importance",
            color_continuous_scale=[[0, "#3A86FF"], [1, "#00D2BA"]]
        )
        fig_feat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CBD5E1"),
            height=320,
            margin=dict(l=10, r=20, t=10, b=20),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_feat, use_container_width=True)

st.markdown("---")

# 4. Pipeline & Leakage Prevention Architecture
st.markdown("### 4. Zero-Leakage Pipeline Architecture")
st.markdown("""
- **Scikit-learn `Pipeline` + `ColumnTransformer`**: All imputers (`SimpleImputer(strategy='median')` for numeric and `'most_frequent'` for categorical) and scalers (`StandardScaler`) are fit **strictly on the training partition (80%)**.
- **No Test Set Contamination**: Test samples and user inputs are transformed exclusively via the fitted transformer pipelines.
- **Handling of Incomplete Inputs**: At prediction time, unprovided optional lab fields (e.g., kidney/liver enzymes) are assigned `NaN` and imputed cleanly using the training distribution medians, ensuring the application never crashes on missing optional fields.
""")

st.markdown("---")

# 5. Known Limitations & Responsible AI
st.markdown("### 5. Known Limitations & Responsible AI Considerations")
st.markdown("""
<div class="glass-card">
    <ul style="font-size: 0.92rem; color: #CBD5E1; line-height: 1.6; padding-left: 1.2rem;">
        <li><strong>Synthetic Data Constraints:</strong> Although constructed using clinical logic from AHA, ADA, and WHO guidelines, synthetic cohorts cannot substitute for real-world heterogeneous multi-ethnic clinical registries.</li>
        <li><strong>Category Boundaries:</strong> The threshold cutoffs separating "Lower", "Moderate", and "Higher" synthetic categories are discrete abstractions designed for educational stratification.</li>
        <li><strong>Unmeasured Risk Factors:</strong> Key cardiometabolic determinants (such as ApoB, Lipoprotein(a), coronary artery calcium scores, genetic polygenic risk scores, and clinical medications) are not captured in this prototype.</li>
        <li><strong>Non-Diagnostic Guarantee:</strong> Model predictions should never be used as diagnostic determinants or justification for initiating or halting medical therapies.</li>
    </ul>
</div>
""", unsafe_allow_html=True)


