"""UI components, theme styles, and interactive Plotly visualizations for HealthRisk AI."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional


def inject_custom_css():
    """Inject bold custom CSS with glassmorphism, responsive typography, and semantic badge styling."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

    /* Global Typography & Reset */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    /* Gradient Hero Container */
    .hero-container {
        background: linear-gradient(135deg, rgba(16, 24, 40, 0.95) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(0, 210, 186, 0.25);
        border-radius: 20px;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }

    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -30%;
        width: 380px;
        height: 380px;
        background: radial-gradient(circle, rgba(0, 210, 186, 0.15) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1.15;
        background: linear-gradient(135deg, #00D2BA 0%, #3A86FF 50%, #C084FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.8rem;
    }

    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.15rem;
        line-height: 1.6;
        max-width: 850px;
        margin-bottom: 1.2rem;
    }

    .hero-tag {
        display: inline-flex;
        align-items: center;
        background: rgba(0, 210, 186, 0.12);
        color: #00D2BA;
        border: 1px solid rgba(0, 210, 186, 0.3);
        padding: 0.35rem 0.9rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(19, 28, 46, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.25rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .glass-card:hover {
        border-color: rgba(0, 210, 186, 0.35);
        transform: translateY(-2px);
    }

    /* Semantic Metric Card */
    .metric-card {
        background: rgba(19, 28, 46, 0.75);
        border-radius: 14px;
        padding: 1.25rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        position: relative;
    }

    .metric-card.status-normal {
        border-left: 4px solid #06D6A0;
    }
    .metric-card.status-warning {
        border-left: 4px solid #FFBE0B;
    }
    .metric-card.status-abnormal {
        border-left: 4px solid #FF5A5F;
    }
    .metric-card.status-critical {
        border-left: 4px solid #EF4444;
        background: rgba(239, 68, 68, 0.08);
    }
    .metric-card.status-missing {
        border: 1px dashed #64748B;
        opacity: 0.75;
    }

    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-normal {
        background: rgba(6, 214, 160, 0.15);
        color: #06D6A0;
        border: 1px solid rgba(6, 214, 160, 0.3);
    }
    .badge-warning {
        background: rgba(255, 190, 11, 0.15);
        color: #FFBE0B;
        border: 1px solid rgba(255, 190, 11, 0.3);
    }
    .badge-abnormal {
        background: rgba(255, 90, 95, 0.15);
        color: #FF5A5F;
        border: 1px solid rgba(255, 90, 95, 0.3);
    }
    .badge-critical {
        background: rgba(239, 68, 68, 0.2);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    .badge-missing {
        background: rgba(100, 116, 139, 0.15);
        color: #94A3B8;
        border: 1px dashed rgba(100, 116, 139, 0.4);
    }

    /* Emergency Alert Box */
    .emergency-alert {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(185, 28, 28, 0.3) 100%);
        border: 2px solid #EF4444;
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.5rem;
        color: #FEE2E2;
    }

    .emergency-title {
        color: #FCA5A5;
        font-size: 1.15rem;
        font-weight: 800;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Meal Card */
    .meal-card {
        background: rgba(22, 33, 56, 0.65);
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .meal-type-tag {
        color: #00D2BA;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .meal-name {
        color: #F8FAFC;
        font-size: 1.2rem;
        font-weight: 700;
        margin-top: 0.25rem;
        margin-bottom: 0.5rem;
    }

    /* Notice Pill */
    .notice-pill {
        background: rgba(58, 134, 255, 0.12);
        border: 1px solid rgba(58, 134, 255, 0.3);
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 1.5rem;
        font-size: 0.9rem;
        color: #93C5FD;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_hero(title: str, subtitle: str, badge_text: str = "Prototype v1.0"):
    """Render modern gradient hero section."""
    html = f"""
    <div class="hero-container">
        <span class="hero-tag">{badge_text}</span>
        <div class="hero-title">{title}</div>
        <div class="hero-subtitle">{subtitle}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_emergency_banner(flags: List[Dict[str, str]]):
    """Render critical red warning banner if any measurement is dangerously abnormal."""
    if not flags:
        return
    
    alert_items = "".join([
        f"<li style='margin-bottom: 0.4rem;'><strong>{f['category']}</strong>: {f['message']}</li>"
        for f in flags
    ])

    html = f"""
    <div class="emergency-alert">
        <div class="emergency-title">
            URGENT CLINICAL ALERT: Marked Out-of-Range Measurements Detected
        </div>
        <div style="font-size: 0.95rem; line-height: 1.5; margin-bottom: 0.6rem;">
            One or more recorded values are within clinical critical alert thresholds:
        </div>
        <ul style="margin: 0; padding-left: 1.4rem; font-size: 0.92rem;">
            {alert_items}
        </ul>
        <div style="margin-top: 0.75rem; font-size: 0.85rem; color: #FECACA;">
            <strong>Immediate Action:</strong> This tool is non-diagnostic. If you or the individual are experiencing acute distress,
            chest pain, shortness of breath, confusion, or severe dizziness, seek emergency medical care immediately.
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_metric_card(name: str, value: Any, unit: str, category: str, badge_color: str,
                       timing: Optional[str] = None, source: Optional[str] = None):
    """Render an individual clinical measurement card with explicit semantic status."""
    is_missing = (value is None) or (category == "Unassessed")
    status_class = f"status-{badge_color}" if not is_missing else "status-missing"
    badge_class = f"badge-{badge_color}" if not is_missing else "badge-missing"

    val_display = f"{value} <span style='font-size: 0.9rem; color: #94A3B8;'>{unit}</span>" if not is_missing else "<span style='color: #64748B;'>Not recorded</span>"
    timing_display = f"<div style='font-size: 0.75rem; color: #64748B; margin-top: 0.2rem;'>Context: {timing}</div>" if timing else ""
    source_display = f"<div style='font-size: 0.7rem; color: #475569; margin-top: 0.4rem;'>Ref: {source}</div>" if source else ""

    html = f"""
    <div class="metric-card {status_class}">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.4rem;">
            <span style="font-weight: 600; font-size: 0.95rem; color: #CBD5E1;">{name}</span>
            <span class="badge {badge_class}">{category}</span>
        </div>
        <div style="font-size: 1.5rem; font-weight: 800; color: #F8FAFC;">
            {val_display}
        </div>
        {timing_display}
        {source_display}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ==============================================================================
# PLOTLY INTERACTIVE CHARTS
# ==============================================================================

def create_risk_gauge_chart(predicted_category: str, probabilities: Dict[str, float]) -> go.Figure:
    """Create an animated-feeling Plotly gauge chart displaying synthetic risk intensity."""
    # Compute composite index (0-100) based on class probabilities
    p_lower = probabilities.get("Lower synthetic risk category", 0.0)
    p_mod = probabilities.get("Moderate synthetic risk category", 0.0)
    p_high = probabilities.get("Higher synthetic risk category", 0.0)

    # Risk score mapping: Lower ~ 15, Mod ~ 50, High ~ 85
    risk_index = round((p_lower * 15 + p_mod * 50 + p_high * 85), 1)

    # Accent color based on category
    if "Higher" in predicted_category:
        gauge_color = "#FF5A5F"
    elif "Moderate" in predicted_category:
        gauge_color = "#FFBE0B"
    else:
        gauge_color = "#00D2BA"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_index,
        number={"suffix": " / 100", "font": {"size": 28, "color": "#F8FAFC", "family": "Space Grotesk"}},
        title={"text": "Synthetic Risk Category Index<br><span style='font-size:12px;color:#94A3B8;'>Probabilistic Composite (Non-Diagnostic)</span>",
               "font": {"size": 15, "color": "#CBD5E1"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#64748B"},
            "bar": {"color": gauge_color, "thickness": 0.28},
            "bgcolor": "rgba(255, 255, 255, 0.05)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 33], "color": "rgba(6, 214, 160, 0.15)"},
                {"range": [33, 66], "color": "rgba(255, 190, 11, 0.15)"},
                {"range": [66, 100], "color": "rgba(255, 90, 95, 0.18)"}
            ],
            "threshold": {
                "line": {"color": "#F8FAFC", "width": 3},
                "thickness": 0.75,
                "value": risk_index
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#CBD5E1"},
        height=260,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def create_radar_profile(user_values: Dict[str, Optional[float]]) -> go.Figure:
    """Create radar chart comparing patient metrics against standard clinical benchmarks."""
    # Define normalized indicators (0 to 100 where 50 is normal boundary)
    categories = ["Blood Pressure", "Lipids (LDL)", "Blood Glucose", "Body Mass Index", "Physical Activity"]

    # Calculate normalized scores (clamp 0-100)
    # Systolic BP: normal <= 120 -> 40; 140 -> 70; 160+ -> 100
    sys = user_values.get("systolic_bp")
    val_bp = min(max(((sys - 100) / 60.0) * 100, 15), 100) if sys else 50

    # LDL: optimal < 100 -> 35; 160 -> 75; 190+ -> 100
    ldl = user_values.get("cholesterol_ldl")
    val_ldl = min(max(((ldl - 70) / 120.0) * 100, 15), 100) if ldl else 50

    # Fasting glucose: normal < 100 -> 35; 126 -> 70; 200 -> 100
    fg = user_values.get("fasting_glucose")
    val_glu = min(max(((fg - 70) / 130.0) * 100, 15), 100) if fg else 50

    # BMI: 22 -> 35; 25 -> 50; 30 -> 75; 35 -> 100
    bmi = user_values.get("bmi")
    val_bmi = min(max(((bmi - 18.5) / 16.5) * 100, 15), 100) if bmi else 50

    # Activity: inverted (low activity = higher risk)
    # 0 min -> 90; 150 min -> 50; 300 min -> 20
    act = user_values.get("physical_activity_min_per_week")
    val_act = max(100 - ((act / 300.0) * 80), 15) if act is not None else 50

    patient_scores = [val_bp, val_ldl, val_glu, val_bmi, val_act]
    normal_benchmark = [40, 40, 40, 40, 40]

    # Close loops for radar
    categories_closed = categories + [categories[0]]
    patient_closed = patient_scores + [patient_scores[0]]
    benchmark_closed = normal_benchmark + [normal_benchmark[0]]

    fig = go.Figure()

    # Optimal Target zone
    fig.add_trace(go.Scatterpolar(
        r=benchmark_closed,
        theta=categories_closed,
        fill="toself",
        name="Target Healthy Benchmark",
        line=dict(color="#00D2BA", width=2, dash="dash"),
        fillcolor="rgba(0, 210, 186, 0.12)"
    ))

    # Patient curve
    fig.add_trace(go.Scatterpolar(
        r=patient_closed,
        theta=categories_closed,
        fill="toself",
        name="Patient Profile",
        line=dict(color="#FF5A5F", width=2.5),
        fillcolor="rgba(255, 90, 95, 0.22)"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=False, linecolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(linecolor="rgba(255,255,255,0.1)", tickfont=dict(size=11, color="#CBD5E1")),
            bgcolor="rgba(19, 28, 46, 0.5)"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CBD5E1"),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        height=330,
        margin=dict(l=30, r=30, t=20, b=40)
    )
    return fig


def create_probability_distribution_chart(probabilities: Dict[str, float]) -> go.Figure:
    """Create clean horizontal bar chart of model class probabilities."""
    labels = list(probabilities.keys())
    values = [round(v * 100, 1) for v in probabilities.values()]

    colors = []
    for label in labels:
        if "Higher" in label:
            colors.append("#FF5A5F")
        elif "Moderate" in label:
            colors.append("#FFBE0B")
        else:
            colors.append("#00D2BA")

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker=dict(color=colors, line=dict(color="rgba(255,255,255,0.2)", width=1)),
        text=[f"{v:.1f}%" for v in values],
        textposition="outside",
        textfont=dict(color="#F8FAFC", size=12, family="Space Grotesk")
    ))

    fig.update_layout(
        title={"text": "Class Likelihood Distribution", "font": {"size": 14, "color": "#CBD5E1"}},
        xaxis=dict(range=[0, 105], showgrid=True, gridcolor="rgba(255,255,255,0.06)", title="Confidence (%)"),
        yaxis=dict(autorange="reversed", tickfont=dict(color="#E2E8F0")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CBD5E1"),
        height=220,
        margin=dict(l=10, r=40, t=40, b=30)
    )
    return fig


def create_confusion_matrix_chart(cm: List[List[int]], labels: List[str]) -> go.Figure:
    """Render Plotly heatmap for model confusion matrix."""
    short_labels = ["Lower", "Moderate", "Higher"]
    fig = px.imshow(
        cm,
        x=short_labels,
        y=short_labels,
        labels=dict(x="Predicted Class", y="Actual Ground Truth", color="Cases"),
        color_continuous_scale=[[0, "#0F172A"], [0.5, "#1E3A8A"], [1.0, "#00D2BA"]],
        text_auto=True
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#CBD5E1"),
        height=320,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    fig.update_traces(textfont=dict(size=14, color="#FFFFFF"))
    return fig


def render_footer():
    """No-op footer; attribution displayed exclusively in sidebar as requested."""
    pass

