# HealthRisk AI 🩺

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-1.66-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.9-F7931E.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

An educational health analytics prototype and cardiometabolic decision-support tool. Users enter health measurements (anthropometrics, blood pressure, lipids, glycemic markers, lifestyle habits, and dietary preferences). The app validates inputs against physiological ranges, runs an offline Scikit-learn machine learning pipeline, explains contributing risk factors in transparent language, provides evidence-based lifestyle guidance, and generates a personalized South Indian cultural meal plan.

> [!IMPORTANT]
> **Educational & Prototype Disclaimer:** HealthRisk AI is strictly an educational demonstration. **This is NOT a medical diagnostic tool or healthcare device.** Predictive labels ("Lower / Moderate / Higher synthetic risk category") represent synthetic model outputs, never clinical diagnoses or absolute disease probabilities. Always consult a licensed healthcare professional for medical advice.

---

## Key Features

1. **Bold, Expressive UI**: Modern dark theme, glassmorphism cards, Google Fonts (`Space Grotesk` & `Plus Jakarta Sans`), and animated-feeling Plotly gauge, radar, and bar visualizations.
2. **Deterministic Range & Consistency Validation**: Validates all numbers against biologically plausible bounds. Checks physiological constraints (e.g., systolic must exceed diastolic). Never infers missing data as healthy.
3. **Emergency Clinical Alert Banner**: Immediately triggers high-visibility warnings for critical findings:
   - Hypertensive Crisis ($\ge 180 / 120\text{ mmHg}$)
   - Severe Hypoglycemia ($< 54\text{ mg/dL}$)
   - Marked Hyperglycemia ($\ge 300\text{ mg/dL}$)
   - Severe Resting Tachycardia ($> 140\text{ bpm}$)
4. **Zero-Leakage ML Pipeline**: Preprocessing (`StandardScaler`, `OneHotEncoder`, median/mode imputers) is fit strictly on training partitions using Scikit-learn `Pipeline` + `ColumnTransformer`. Evaluates Logistic Regression baseline vs Random Forest.
5. **Rule-Based Clinical Recommendation Engine**: Formulates guidance on sodium restriction, complex unpolished grains, heart-smart fats, and WHO aerobic activity targets based on authoritative guidelines (WHO, ACC/AHA, NCEP ATP III, ADA 2024, ICMR-NIN).
6. **Cultural South Indian Meal Planner**: Generates daily meal plans respecting diet types (Vegetarian, Vegan, Eggetarian, Non-Vegetarian), cuisine preferences, and strict allergen exclusion (peanuts, gluten, dairy, etc.). Qualitatively described with portion awareness without fabricating calories or macros.

---

## Real Evaluation Metrics (Synthetic Dataset)

Trained on a reproducible synthetic dataset ($N = 2,500$ rows, 28 columns, fixed seed `42`) with 80/20 stratified train/test split ($N_{\text{test}} = 500$):

| Model Candidate | Test Accuracy | F1 Score (Macro) | F1 Score (Weighted) | Precision (Macro) | Recall (Macro) | Selected |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression Baseline** | **81.60%** | **0.8131** | **0.8155** | **0.8317** | **0.7992** | **Yes (Best)** |
| **Random Forest Classifier** | 77.20% | 0.7082 | 0.7645 | 0.8525 | 0.6637 | No |

*Top Predictive Features:* `diastolic_bp`, `systolic_bp`, `bmi`, `fasting_glucose`, `age`, `waist_cm`, `cholesterol_total`, `cholesterol_ldl`, `triglycerides`, `weight_kg`.

---

## Repository Structure

```
Madam-AI&DS/
│
├── app.py                      # Main Streamlit navigation coordinator
├── requirements.txt            # Pinned dependency requirements
├── README.md                   # Complete documentation
├── .gitignore                  # Git ignore rules (venv, checkpoints, cache)
│
├── .streamlit/
│   └── config.toml             # Custom theme colors (dark vibrant palette)
│
├── data/
│   └── healthrisk_ai_synthetic_demo.csv  # 2,500-row reproducible synthetic dataset
│
├── models/
│   ├── risk_classifier.joblib  # Serialized scikit-learn pipeline artifact
│   └── model_metrics.json      # Actual test evaluation metrics & confusion matrix
│
├── src/
│   ├── __init__.py
│   ├── validation.py           # Biological ranges, required/optional checks, emergency flags
│   ├── train_model.py          # Synthetic generator, EDA, zero-leakage training pipeline
│   ├── recommendation_engine.py# Evidence-based clinical rules, South Indian meal planner
│   ├── predict.py              # Model inference wrapper & individual factor scoring
│   └── ui_components.py        # Custom CSS, glassmorphism cards, Plotly charts
│
├── pages/
│   ├── 1_Home.py               # Hero, quick demo loader, supported measurements
│   ├── 2_Health_Assessment.py  # Comprehensive input form with live BMI calculation
│   ├── 3_Prediction_Results.py # Risk classification, radar/gauge charts, factor breakdown
│   ├── 4_Diet_Planner.py       # Custom South Indian meal plan generator & budget tips
│   ├── 5_Model_Information.py  # Model card, confusion matrix heatmap, limitations
│   └── 6_About_and_Disclaimer.py # Authoritative clinical citations & medical disclaimer
│
└── tests/
    ├── __init__.py
    ├── test_validation.py      # Unit tests for input ranges & emergency alert logic
    ├── test_recommendations.py # Tests for clinical rules & meal plan allergen filtering
    └── test_prediction.py      # Tests for model inference shape & edge cases
```

---

## Local Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/HealthRisk-AI.git
cd HealthRisk-AI
```

### 2. Create and Activate a Virtual Environment
- **On Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
- **On macOS / Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Training Workflow & Model Generation

The training pipeline generates the synthetic dataset, performs EDA, trains both baseline and Random Forest models, logs actual metrics, and exports the model artifact:

```bash
python src/train_model.py
```

Expected output:
```
=== DATASET EDA SUMMARY ===
Rows: 2500, Columns: 28
Duplicates: 0
Class Distribution: {'Moderate synthetic risk category': 1252, 'Lower synthetic risk category': 1015, 'Higher synthetic risk category': 233}

Baseline LR Accuracy: 0.8160 | F1 Macro: 0.8131
Random Forest Accuracy: 0.7720 | F1 Macro: 0.7082

Best Model: Logistic Regression Baseline
Saved model pipeline to models/risk_classifier.joblib
```

---

## Running the Automated Test Suite

Execute the full suite of 19 unit tests across validation, clinical rules, and model predictions:

```bash
pytest -v
```

All 19 tests will pass with zero errors:
```
============================= 19 passed in 5.00s ==============================
```

---

## Launching the Streamlit Application

Run the app locally with:

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`.

---

## Pushing to GitHub & Deploying to Streamlit Cloud

### 1. Initialize and Push to GitHub
```bash
git init
git add .
git commit -m "feat: initial commit for HealthRisk AI"
git branch -M main
git remote add origin https://github.com/<your-username>/HealthRisk-AI.git
git push -u origin main
```

### 2. Deploy to Streamlit Community Cloud
1. Visit [share.streamlit.io](https://share.streamlit.io) and log in with GitHub.
2. Click **"New App"**.
3. Select your repository: `<your-username>/HealthRisk-AI`.
4. Set the **Main file path** to: `app.py`.
5. Click **"Deploy!"**.
- *Note:* The application requires zero environment variables, zero API keys, and has no external database dependencies. All file paths use `Path(__file__).resolve().parent`, guaranteeing seamless execution on Streamlit Community Cloud.

---

## Authoritative Clinical References

- **BMI & Asian Cutoffs:** WHO Expert Consultation (Lancet 2004; 363: 157-163).
- **Hypertension & Blood Pressure:** 2017 ACC/AHA Guideline (J Am Coll Cardiol 2018; 71: e127-e248).
- **Lipid Management:** NCEP Adult Treatment Panel III (ATP III) Guidelines (Circulation 2002; 106: 3143).
- **Glycemic Thresholds:** American Diabetes Association (ADA) Standards of Care in Diabetes 2024.
- **Dietary Guidelines:** ICMR - National Institute of Nutrition (NIN) Dietary Guidelines for Indians (2024).

---

## License

This project is licensed under the MIT License.

