import streamlit as st
import pandas as pd
from difflib import SequenceMatcher


st.set_page_config(
    page_title="Campus Lost & Found AI Matcher",
    page_icon="🎒",
    layout="wide"
)


# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: #f8f5ef;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero-card {
        background: linear-gradient(135deg, #9b1c31 0%, #c23b4b 55%, #f2b36d 100%);
        padding: 2.1rem 2.3rem;
        border-radius: 22px;
        color: white;
        box-shadow: 0 14px 35px rgba(120, 20, 35, 0.22);
        margin-bottom: 1.4rem;
    }

    .hero-card h1 {
        color: white;
        font-size: 2.35rem;
        margin-bottom: 0.4rem;
        letter-spacing: -0.03em;
    }

    .hero-card p {
        color: #fff8f0;
        font-size: 1.05rem;
        max-width: 760px;
        line-height: 1.55;
    }

    .tag-row {
        margin-top: 1rem;
    }

    .tag {
        display: inline-block;
        background: rgba(255, 255, 255, 0.18);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.28);
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-right: 0.45rem;
    }

    .info-card {
        background: #ffffff;
        padding: 1rem 1.15rem;
        border-radius: 18px;
        border: 1px solid #eadfd2;
        box-shadow: 0 8px 22px rgba(70, 50, 30, 0.08);
        height: 100%;
    }

    .info-card h3 {
        margin: 0;
        color: #9b1c31;
        font-size: 1.55rem;
        font-weight: 850;
    }

    .info-card p {
        margin: 0.25rem 0 0 0;
        color: #665f57;
        font-size: 0.9rem;
        font-weight: 600;
    }

    .form-card {
        background: #ffffff;
        padding: 1.4rem;
        border-radius: 20px;
        border: 1px solid #eadfd2;
        box-shadow: 0 8px 22px rgba(70, 50, 30, 0.08);
        margin-top: 1.2rem;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 850;
        color: #2f241f;
        margin-bottom: 0.8rem;
    }

    .match-card {
        background: white;
        padding: 1.15rem 1.25rem;
        border-radius: 18px;
        border: 1px solid #eadfd2;
        box-shadow: 0 8px 22px rgba(70, 50, 30, 0.08);
        margin-bottom: 1rem;
        border-left: 6px solid #9b1c31;
    }

    .match-title {
        font-size: 1.15rem;
        font-weight: 850;
        color: #2f241f;
        margin-bottom: 0.2rem;
    }

    .match-meta {
        color: #7a7068;
        font-size: 0.9rem;
        margin-bottom: 0.7rem;
    }

    .badge-high {
        background: #e7f7ed;
        color: #167344;
        padding: 0.32rem 0.7rem;
        border-radius: 999px;
        font-weight: 800;
        font-size: 0.82rem;
    }

    .badge-medium {
        background: #fff3d8;
        color: #9a5a00;
        padding: 0.32rem 0.7rem;
        border-radius: 999px;
        font-weight: 800;
        font-size: 0.82rem;
    }

    .badge-low {
        background: #fde8e8;
        color: #a32020;
        padding: 0.32rem 0.7rem;
        border-radius: 999px;
        font-weight: 800;
        font-size: 0.82rem;
    }

    .note-box {
        background: #fff8ed;
        color: #5f5145;
        padding: 0.9rem 1rem;
        border-radius: 15px;
        border: 1px solid #f2d6a5;
        font-size: 0.9rem;
    }

    div.stButton > button:first-child {
        background: #9b1c31;
        color: white;
        border: none;
        border-radius: 13px;
        padding: 0.75rem 1rem;
        font-weight: 800;
        box-shadow: 0 8px 20px rgba(155, 28, 49, 0.22);
    }

    div.stButton > button:first-child:hover {
        background: #7e1628;
        color: white;
        border: none;
    }

    .stTextInput input, .stTextArea textarea {
        border-radius: 12px;
        background-color: #fbfaf8;
    }

    div[data-baseweb="select"] {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Helper functions
# -----------------------------
def text_similarity(text_a, text_b):
    return SequenceMatcher(None, text_a.lower(), text_b.lower()).ratio()


def keyword_overlap(text_a, text_b):
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())

    if not words_a or not words_b:
        return 0

    overlap = words_a.intersection(words_b)
    return len(overlap) / max(len(words_a), 1)


def calculate_match_score(lost_item, found_item):
    description_score = text_similarity(
        lost_item["description"],
        found_item["description"]
    )

    keyword_score = keyword_overlap(
        lost_item["description"],
        found_item["description"]
    )

    category_score = 1 if lost_item["category"] == found_item["category"] else 0
    location_score = 1 if lost_item["location"] == found_item["location"] else 0
    color_score = 1 if lost_item["color"].lower() == found_item["color"].lower() else 0

    final_score = (
        description_score * 0.40
        + keyword_score * 0.20
        + category_score * 0.20
        + location_score * 0.10
        + color_score * 0.10
    )

    return round(final_score * 100, 1)


def confidence_label(score):
    if score >= 75:
        return "High Match", "badge-high"
    elif score >= 45:
        return "Possible Match", "badge-medium"
    else:
        return "Low Match", "badge-low"


def match_reason(lost_item, found_item):
    reasons = []

    if lost_item["category"] == found_item["category"]:
        reasons.append("same category")

    if lost_item["location"] == found_item["location"]:
        reasons.append("same campus location")

    if lost_item["color"].lower() == found_item["color"].lower():
        reasons.append("matching color")

    overlap_words = set(lost_item["description"].lower().split()).intersection(
        set(found_item["description"].lower().split())
    )

    if overlap_words:
        reasons.append("similar description keywords")

    if not reasons:
        return "Ranked using general description similarity."

    return "Matched because of " + ", ".join(reasons) + "."


# -----------------------------
# Sample found-item database
# -----------------------------
found_items = pd.DataFrame(
    [
        {
            "item": "Black Water Bottle",
            "category": "Bottle",
            "color": "Black",
            "location": "Library",
            "description": "Black metal water bottle found near the study tables in the library."
        },
        {
            "item": "Blue Backpack",
            "category": "Bag",
            "color": "Blue",
            "location": "Student Center",
            "description": "Blue backpack with laptop sleeve found near the student center seating area."
        },
        {
            "item": "Silver Laptop",
            "category": "Electronics",
            "color": "Silver",
            "location": "Computer Lab",
            "description": "Silver laptop found in the computer lab after evening class."
        },
        {
            "item": "Red Notebook",
            "category": "Notebook",
            "color": "Red",
            "location": "Lecture Hall",
            "description": "Red spiral notebook found under a lecture hall desk."
        },
        {
            "item": "White AirPods Case",
            "category": "Electronics",
            "color": "White",
            "location": "Gym",
            "description": "White wireless earbuds case found near the gym entrance."
        },
    ]
)


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.title("🎒 Matcher")
    st.write("A prototype for faster campus lost-and-found support.")

    st.markdown("### Matching Signals")
    st.write("Category")
    st.write("Color")
    st.write("Location")
    st.write("Description similarity")

    st.markdown("---")
    st.caption("Built with Python, Streamlit, and text matching logic.")


# -----------------------------
# Hero
# -----------------------------
st.markdown(
    """
    <div class="hero-card">
        <h1>Campus Lost & Found AI Matcher</h1>
        <p>
        A student-friendly matching tool that ranks possible found-item matches using
        item descriptions, category, color, and campus location.
        </p>
        <div class="tag-row">
            <span class="tag">NLP-style matching</span>
            <span class="tag">Explainable scores</span>
            <span class="tag">Campus workflow</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Stats
# -----------------------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        """
        <div class="info-card">
            <h3>5</h3>
            <p>Found items</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        """
        <div class="info-card">
            <h3>4</h3>
            <p>Matching signals</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        """
        <div class="info-card">
            <h3>Top 3</h3>
            <p>Ranked results</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        """
        <div class="info-card">
            <h3>Why</h3>
            <p>Match explanation</p>
        </div>
        """,
        unsafe_allow_html=True
    )


# -----------------------------
# Form
# -----------------------------
st.markdown('<div class="form-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Submit Lost Item Details</div>', unsafe_allow_html=True)

left_col, right_col = st.columns([1, 1])

with left_col:
    item_name = st.text_input("Lost Item Name", placeholder="Example: black water bottle")

    category = st.selectbox(
        "Category",
        ["Bottle", "Bag", "Electronics", "Notebook", "Keys", "Clothing", "Other"]
    )

    color = st.text_input("Color", placeholder="Example: black")

with right_col:
    location = st.selectbox(
        "Last Seen Location",
        ["Library", "Student Center", "Computer Lab", "Lecture Hall", "Gym", "Dining Hall", "Dorm", "Other"]
    )

    description = st.text_area(
        "Description",
        placeholder="Describe the item, brand, size, stickers, or anything unique...",
        height=145
    )

search_button = st.button("Find Possible Matches", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)


# -----------------------------
# Results
# -----------------------------
if search_button:
    if not item_name or not color or not description:
        st.warning("Please fill in the item name, color, and description before searching.")
    else:
        lost_item = {
            "item": item_name,
            "category": category,
            "color": color,
            "location": location,
            "description": description
        }

        results = []

        for _, found_item in found_items.iterrows():
            score = calculate_match_score(lost_item, found_item)
            label, badge_class = confidence_label(score)

            results.append(
                {
                    "item": found_item["item"],
                    "category": found_item["category"],
                    "color": found_item["color"],
                    "location": found_item["location"],
                    "description": found_item["description"],
                    "score": score,
                    "label": label,
                    "badge_class": badge_class,
                    "reason": match_reason(lost_item, found_item)
                }
            )

        results = sorted(results, key=lambda x: x["score"], reverse=True)

        st.markdown('<div class="section-title">Top Matches</div>', unsafe_allow_html=True)

        for result in results[:3]:
            st.markdown(
                f"""
                <div class="match-card">
                    <div class="match-title">{result["item"]}</div>
                    <div class="match-meta">
                        {result["category"]} • {result["color"]} • Found near {result["location"]}
                    </div>
                    <span class="{result["badge_class"]}">{result["label"]} · {result["score"]}%</span>
                    <p style="margin-top: 0.9rem;"><strong>Description:</strong> {result["description"]}</p>
                    <p><strong>Why this matched:</strong> {result["reason"]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            """
            <div class="note-box">
            This prototype is a decision-support tool. A production version would connect to a secure campus database,
            user authentication, staff verification, and item pickup workflow.
            </div>
            """,
            unsafe_allow_html=True
        )


# -----------------------------
# Database Preview
# -----------------------------
with st.expander("View sample found-item database"):
    st.dataframe(found_items, use_container_width=True)