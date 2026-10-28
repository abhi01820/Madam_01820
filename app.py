"""Main application entry point for HealthRisk AI.

Configures global app settings, theme, and multi-page routing.
Self-contained, offline-runnable, and ready for Streamlit Community Cloud.
"""

import streamlit as st

st.set_page_config(
    page_title="HealthRisk AI - Cardiometabolic Health Analytics",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define clean navigation groups with modern Streamlit st.navigation
pages = {
    "Overview": [
        st.Page("pages/1_Home.py", title="Home", icon=":material/home:", default=True),
    ],
    "Health Analytics": [
        st.Page("pages/2_Health_Assessment.py", title="Health Assessment", icon=":material/assignment:"),
        st.Page("pages/3_Prediction_Results.py", title="Prediction Results", icon=":material/analytics:"),
        st.Page("pages/4_Diet_Planner.py", title="Diet Planner", icon=":material/restaurant:"),
    ],
    "Transparency & Science": [
        st.Page("pages/5_Model_Information.py", title="Model Information", icon=":material/psychology:"),
        st.Page("pages/6_About_and_Disclaimer.py", title="About & Disclaimer", icon=":material/info:"),
    ]
}

pg = st.navigation(pages)
pg.run()
