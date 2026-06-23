import streamlit as st
import pandas as pd
from pathlib import Path

from lost_found_matcher import get_top_matches


# -----------------------------
# Page setup
# -----------------------------

st.set_page_config(
    page_title="Campus Lost & Found AI Matcher",
    page_icon="🎒",
    layout="wide"
)


# -----------------------------
# Custom CSS styling
# -----------------------------

st.markdown("""
<style>
.main {
    padding-top: 1.5rem;
}

.hero {
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
    padding: 2.2rem;
    border-radius: 20px;
    margin-bottom: 2rem;
}

.hero h1 {
    color: white;
    font-size: 3rem;
    margin-bottom: 0.5rem;
}

.hero p {
    color: #d1d5db;
    font-size: 1.15rem;
    line-height: 1.6;
}

.section-title {
    font-size: 1.6rem;
    font-weight: 700;
    margin-top: 2rem;
    margin-bottom: 1rem;
}

.small-note {
    color: #6b7280;
    font-size: 0.95rem;
    margin-bottom: 1rem;
}

.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 10px;
    padding: 0.65rem 1.4rem;
    border: none;
    font-weight: 600;
}

.stButton>button:hover {
    background-color: #1d4ed8;
    color: white;
}
</style>
""", unsafe_allow_html=True)


# -----------------------------
# File paths
# -----------------------------

PROJECT_ROOT = Path("Resume-projects/campus-lost-found-ai-matcher")

DATA_PATH = PROJECT_ROOT / "data" / "lost_found_posts.csv"
OUTPUTS_PATH = PROJECT_ROOT / "outputs"

ACCURACY_CHART = OUTPUTS_PATH / "accuracy_comparison.png"
CATEGORY_CHART = OUTPUTS_PATH / "category_distribution.png"
LOCATION_CHART = OUTPUTS_PATH / "top_locations.png"


# -----------------------------
# Load data
# -----------------------------

data = pd.read_csv(DATA_PATH)

lost_data = data[data["post_type"] == "lost"].copy()
found_data = data[data["post_type"] == "found"].copy()


# -----------------------------
# Hero section
# -----------------------------

st.markdown("""
<div class="hero">
    <h1>🎒 Campus Lost & Found AI Matcher</h1>
    <p>
    Find possible matches for lost campus items using NLP text similarity,
    hybrid metadata scoring, confidence labels, and explainable match reasons.
    </p>
</div>
""", unsafe_allow_html=True)


# -----------------------------
# Metrics
# -----------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Posts", len(data))

with col2:
    st.metric("Lost Reports", len(lost_data))

with col3:
    st.metric("Found Reports", len(found_data))


# -----------------------------
# Dataset preview
# -----------------------------

st.markdown('<div class="section-title">📌 Dataset Preview</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="small-note">A sample of the synthetic campus lost and found dataset used for matching.</div>',
    unsafe_allow_html=True
)

st.dataframe(data.head(), use_container_width=True)


# -----------------------------
# Post type counts
# -----------------------------

st.markdown('<div class="section-title">📊 Post Type Counts</div>', unsafe_allow_html=True)

post_counts = data["post_type"].value_counts().reset_index()
post_counts.columns = ["Post Type", "Count"]

st.dataframe(post_counts, use_container_width=True)


# -----------------------------
# Select lost item
# -----------------------------

st.markdown('<div class="section-title">🔎 Select a Lost Item</div>', unsafe_allow_html=True)

lost_options = lost_data["post_id"] + " - " + lost_data["item_name"]

selected_option = st.selectbox(
    "Choose a lost item:",
    lost_options
)

selected_post_id = selected_option.split(" - ")[0]

selected_lost_item = lost_data[lost_data["post_id"] == selected_post_id]
selected_lost_row = selected_lost_item.iloc[0]

st.markdown('<div class="section-title">🧾 Selected Lost Item Details</div>', unsafe_allow_html=True)
st.dataframe(selected_lost_item, use_container_width=True)


# -----------------------------
# Find matches
# -----------------------------

if st.button("Find Matches"):
    top_matches = get_top_matches(
        selected_lost_row,
        found_data,
        use_hybrid=True,
        top_k=5
    )

    display_matches = top_matches[[
        "post_id",
        "item_name",
        "hybrid_score",
        "confidence_label",
        "match_reasons"
    ]].copy()

    display_matches["hybrid_score"] = display_matches["hybrid_score"].round(3)

    st.markdown('<div class="section-title">✅ Top 5 Possible Found Item Matches</div>', unsafe_allow_html=True)

    st.dataframe(display_matches, use_container_width=True)

    best_match = display_matches.iloc[0]

    st.success(
        f"Best match: {best_match['post_id']} - {best_match['item_name']} "
        f"with {best_match['confidence_label']} confidence."
    )


# -----------------------------
# Dashboard
# -----------------------------

st.markdown('<div class="section-title">📈 Project Results Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="small-note">Evaluation results and dataset visualizations from the matching system.</div>',
    unsafe_allow_html=True
)

st.image(
    str(ACCURACY_CHART),
    caption="Text-only vs Hybrid Matcher Accuracy",
    use_container_width=True
)

col4, col5 = st.columns(2)

with col4:
    st.image(
        str(CATEGORY_CHART),
        caption="Overall Category Distribution",
        use_container_width=True
    )

with col5:
    st.image(
        str(LOCATION_CHART),
        caption="Top 10 Campus Locations",
        use_container_width=True
    )


# -----------------------------
# Footer
# -----------------------------

st.markdown("---")
st.markdown(
    "Built with Python, Streamlit, Pandas, Scikit-learn, and Matplotlib."
)