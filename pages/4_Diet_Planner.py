"""Diet Planner Page for HealthRisk AI."""

import streamlit as st
import random
from src.ui_components import inject_custom_css, render_hero, render_footer
from src.recommendation_engine import generate_meal_plan

inject_custom_css()

render_hero(
    title="Cultural Diet Planner",
    subtitle=(
        "Personalized, qualitative daily meal plans with a primary South Indian regional focus. "
        "Strictly respects your chosen dietary pattern, regional preferences, and food allergies. "
        "No fabricated calories or macros — pure culinary science and portion mindfulness."
    ),
    badge_text="Step 3: Nutrition & Meal Plan"
)

# Pull preferences from session state if available, or allow on-the-fly adjustment
user_profile = st.session_state.get("user_profile", {})
diet_type_default = user_profile.get("diet_type", "Vegetarian")
cuisine_default = user_profile.get("cuisine", "South Indian")
allergies_default = user_profile.get("allergies", [])
budget_default = user_profile.get("daily_budget_inr", 350)
meals_default = user_profile.get("meals_per_day", 3)

st.markdown("### Plan Configuration & Dietary Constraints")
col_cfg1, col_cfg2, col_cfg3, col_cfg4 = st.columns(4)

with col_cfg1:
    diet_opts = ["Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"]
    sel_diet = st.selectbox(
        "Dietary Pattern",
        options=diet_opts,
        index=diet_opts.index(diet_type_default) if diet_type_default in diet_opts else 0
    )

with col_cfg2:
    cuisine_opts = ["South Indian", "North Indian", "Other"]
    sel_cuisine = st.selectbox(
        "Cuisine Preference",
        options=cuisine_opts,
        index=cuisine_opts.index(cuisine_default) if cuisine_default in cuisine_opts else 0
    )

with col_cfg3:
    allergy_choices = ["Peanuts", "Tree Nuts", "Dairy / Lactose", "Gluten", "Soy", "Shellfish", "Fish", "Eggs"]
    sel_allergies = st.multiselect(
        "Allergens to Exclude",
        options=allergy_choices,
        default=[a for a in allergies_default if a in allergy_choices]
    )

with col_cfg4:
    sel_meals_count = st.selectbox(
        "Meals per Day",
        options=[3, 4],
        index=0 if meals_default <= 3 else 1,
        format_func=lambda x: "3 Meals (Breakfast, Lunch, Dinner)" if x == 3 else "4 Meals (Includes Mid-Day Snack)"
    )

# Plan Generation & Regeneration logic
if "meal_plan_seed" not in st.session_state:
    st.session_state["meal_plan_seed"] = random.randint(1, 100000)

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("Regenerate Meal Plan", type="primary", use_container_width=True):
        st.session_state["meal_plan_seed"] = random.randint(1, 100000)

current_seed = st.session_state["meal_plan_seed"]

# Generate meal plan
plan = generate_meal_plan(
    diet_type=sel_diet,
    cuisine=sel_cuisine,
    allergies=sel_allergies,
    meals_per_day=sel_meals_count,
    random_seed=current_seed
)

st.markdown("---")

# Active Dietary Summary Pill
allergies_str = ", ".join(sel_allergies) if sel_allergies else "None declared"
st.markdown(f"""
<div style="background: rgba(0, 210, 186, 0.08); border: 1px solid rgba(0, 210, 186, 0.25); border-radius: 12px; padding: 0.8rem 1.25rem; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
    <div>
        <strong>Active Pattern:</strong> <span style="color: #00D2BA;">{sel_diet}</span> &nbsp;|&nbsp;
        <strong>Cuisine Focus:</strong> <span style="color: #3A86FF;">{sel_cuisine}</span> &nbsp;|&nbsp;
        <strong>Excluded Allergens:</strong> <span style="color: #FF5A5F;">{allergies_str}</span>
    </div>
    <div style="font-size: 0.8rem; color: #94A3B8;">
        Target Daily Budget: ~₹{budget_default} INR
    </div>
</div>
""", unsafe_allow_html=True)

# Meal Plan Display
st.markdown("### Your Custom Daily Meal Schedule")

schedule = plan["schedule"]

for meal_time, dish in schedule.items():
    cuisine_badge = f"<span class='badge' style='background: rgba(58,134,255,0.15); color: #60A5FA; border: 1px solid rgba(58,134,255,0.3);'>{dish.get('cuisine', sel_cuisine)}</span>"
    
    st.markdown(f"""
    <div class="meal-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
            <span class="meal-type-tag">{meal_time}</span>
            {cuisine_badge}
        </div>
        <div class="meal-name">{dish['name']}</div>
        <div style="font-size: 0.95rem; color: #CBD5E1; line-height: 1.5; margin-bottom: 0.75rem;">
            {dish['description']}
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 0.8rem; background: rgba(0,0,0,0.25); padding: 0.8rem 1rem; border-radius: 8px;">
            <div>
                <strong style="color: #00D2BA; font-size: 0.85rem; text-transform: uppercase;">Mindful Portion Guidance:</strong>
                <div style="font-size: 0.9rem; color: #E2E8F0; margin-top: 0.2rem;">{dish['portion_guidance']}</div>
            </div>
            <div>
                <strong style="color: #3A86FF; font-size: 0.85rem; text-transform: uppercase;">Nutritional Value & Why It Helps:</strong>
                <div style="font-size: 0.9rem; color: #E2E8F0; margin-top: 0.2rem;">{dish['why_it_helps']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Budget & Regional Ingredient Guidance
st.markdown("### Local Market Guidance & Budget Smart Swaps (South Indian Context)")
col_bg1, col_bg2 = st.columns(2)

with col_bg1:
    st.markdown("""
    <div class="glass-card">
        <h4 style="color: #00D2BA; margin-top:0;">Budget-Friendly Whole Foods</h4>
        <ul style="font-size: 0.9rem; color: #CBD5E1; padding-left: 1.2rem; line-height: 1.6;">
            <li><strong>Millets (Ragi, Thinai, Samai):</strong> Readily available in local provision shops at ₹40-70/kg, offering 3x the dietary fiber of polished white rice.</li>
            <li><strong>Lentils & Pulses:</strong> Split green moong and toor dal are high in protein and cook quickly without heavy oil.</li>
            <li><strong>Seasonal Native Vegetables:</strong> Ridge gourd (peerkangai), bottle gourd (sorakkai), snake gourd (pudalangai), and drumstick (moringa) provide high hydration, fiber, and potassium at very modest cost.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_bg2:
    st.markdown("""
    <div class="glass-card">
        <h4 style="color: #FFBE0B; margin-top:0;">Healthy Kitchen Swaps</h4>
        <ul style="font-size: 0.9rem; color: #CBD5E1; padding-left: 1.2rem; line-height: 1.6;">
            <li><strong>Swap Deep-Frying:</strong> Use steam cooking (idli, idiyappam, dhokla) or dry-roasting on cast-iron tawa instead of deep-fried vadas.</li>
            <li><strong>Cut Sneaky Sodium:</strong> Cut papad, commercial pickles, and instant rasam powders in half; rely on fresh tamarind, curry leaves, ginger, and cumin.</li>
            <li><strong>Plant Diversity:</strong> Aim for 20+ distinct botanical plant species each week (grains, legumes, greens, herbs, spices).</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.caption("Note: Meals are qualitatively curated for nutritional balance. Never engage in extreme caloric restriction without clinical supervision.")


