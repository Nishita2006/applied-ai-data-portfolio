import streamlit as st
import pandas as pd
from lost_found_matcher import get_top_matches


# App title
st.title("Campus Lost & Found AI Matcher")

# Short description
st.write("This app helps match lost item reports with possible found item reports.")

# Load dataset
data = pd.read_csv("Resume-projects/campus-lost-found-ai-matcher/data/lost_found_posts.csv")

# Show dataset preview
st.subheader("Dataset Preview")
st.dataframe(data.head())

# Show basic counts
st.subheader("Post Type Counts")
st.write(data["post_type"].value_counts())

lost_data = data[data["post_type"] == "lost"].copy()
found_data = data[data["post_type"] == "found"].copy()

st.subheader("Select a Lost Item")

lost_options = lost_data["post_id"] + " - " + lost_data["item_name"]

selected_option = st.selectbox(
    "Choose a lost item:",
    lost_options
)

selected_post_id = selected_option.split(" - ")[0]

selected_lost_item = lost_data[lost_data["post_id"] == selected_post_id]

st.subheader("Selected Lost Item Details")
st.dataframe(selected_lost_item)
if st.button("Find Matches"):
    selected_lost_row = selected_lost_item.iloc[0]

    top_matches = get_top_matches(
        selected_lost_row,
        found_data,
        use_hybrid=True,
        top_k=5
    )

    st.subheader("Top 5 Possible Found Item Matches")

    st.dataframe(top_matches[[
        "post_id",
        "item_name",
        "hybrid_score",
        "confidence_label",
        "match_reasons"
    ]])


st.subheader("Project Results Dashboard")

st.image(
    "Resume-projects/campus-lost-found-ai-matcher/outputs/accuracy_comparison.png",
    caption="Text-only vs Hybrid Matcher Accuracy"
)

st.image(
    "Resume-projects/campus-lost-found-ai-matcher/outputs/category_distribution.png",
    caption="Overall Category Distribution"
)

st.image(
    "Resume-projects/campus-lost-found-ai-matcher/outputs/top_locations.png",
    caption="Top 10 Campus Locations"
)