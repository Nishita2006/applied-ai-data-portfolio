import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# Campus Lost & Found AI Matcher
# ------------------------------------------------------------
# This project matches lost item posts with possible found item
# posts using a combination of:
# 1. NLP text similarity
# 2. Structured metadata scoring
# 3. Hybrid ranking
# 4. Explainable match reasons
# ============================================================


DATA_PATH = "Resume-projects/campus-lost-found-ai-matcher/data/lost_found_posts.csv"
OUTPUT_DIR = "Resume-projects/campus-lost-found-ai-matcher/outputs"


# ------------------------------------------------------------
# 1. Load and inspect dataset
# ------------------------------------------------------------

def load_data(file_path):
    """Load the lost and found dataset."""
    data = pd.read_csv(file_path)
    return data


def inspect_data(data):
    """Print basic dataset checks before building the matcher."""
    print("\n========== DATASET OVERVIEW ==========")
    print(data.head())

    print("\nColumns:")
    print(data.columns)

    print("\nShape:")
    print(data.shape)

    print("\nMissing values:")
    print(data.isnull().sum())

    print("\nPost type counts:")
    print(data["post_type"].value_counts())

    print("\nCategory counts:")
    print(data["category"].value_counts())

    print("\nDuplicate rows:")
    print(data.duplicated().sum())

    print("\nAre post IDs unique?")
    print(data["post_id"].is_unique)

    print("\nTop locations:")
    print(data["location"].value_counts().head(10))

    print("\nTop colors:")
    print(data["color"].value_counts().head(10))

    print("\nRows with a true match ID:")
    print(data["true_match_id"].notna().sum())

    print("\nUnmatched found posts:")
    print(data[data["post_type"] == "found"]["true_match_id"].isna().sum())


# ------------------------------------------------------------
# 2. Split dataset into lost and found posts
# ------------------------------------------------------------

def split_lost_found(data):
    """Separate lost posts and found posts."""
    lost_data = data[data["post_type"] == "lost"].copy()
    found_data = data[data["post_type"] == "found"].copy()

    print("\n========== LOST / FOUND SPLIT ==========")
    print("Lost posts shape:", lost_data.shape)
    print("Found posts shape:", found_data.shape)

    return lost_data, found_data


# ------------------------------------------------------------
# 3. Text similarity
# ------------------------------------------------------------

def calculate_text_similarity(lost_text, found_texts):
    """
    Convert one lost item description and all found item descriptions
    into TF-IDF vectors, then calculate cosine similarity.
    """
    all_text = [lost_text] + found_texts.tolist()

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_text)

    similarity_scores = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    ).flatten()

    return similarity_scores


# ------------------------------------------------------------
# 4. Metadata scoring
# ------------------------------------------------------------

def add_metadata_scores(results, lost_item):
    """
    Add scores based on structured lost/found item details:
    category, color, location, brand, and date.
    """
    # Same category = strong signal
    results["category_score"] = (
        results["category"] == lost_item["category"]
    ).astype(int)

    # Same color = useful signal
    results["color_score"] = (
        results["color"] == lost_item["color"]
    ).astype(int)

    # Item name score:
    # same item name = 1, different item name = 0
    results["item_name_score"] = (
        results["item_name"] == lost_item["item_name"]
    ).astype(int)

    # Same location = useful real-world signal
    results["location_score"] = (
        results["location"] == lost_item["location"]
    ).astype(int)

    # Brand score:
    # 1   = same brand
    # 0.5 = brand missing/unknown
    # 0   = different brand
    results["brand_score"] = 0

    same_brand = results["brand"] == lost_item["brand"]
    missing_brand = results["brand"].isna() | pd.isna(lost_item["brand"])

    results.loc[same_brand, "brand_score"] = 1
    results.loc[missing_brand, "brand_score"] = 0.5

    # Date score:
    # closer lost/found dates should increase match confidence
    results["date"] = pd.to_datetime(results["date"])
    lost_date = pd.to_datetime(lost_item["date"])

    results["date_difference"] = (
        results["date"] - lost_date
    ).abs().dt.days

    results["date_score"] = 0.1
    results.loc[results["date_difference"] <= 14, "date_score"] = 0.4
    results.loc[results["date_difference"] <= 7, "date_score"] = 0.7
    results.loc[results["date_difference"] <= 2, "date_score"] = 1.0

    return results


# ------------------------------------------------------------
# 5. Hybrid score
# ------------------------------------------------------------

def add_hybrid_score(results):
    """
    Combine text similarity and metadata scores into one final score.
    Text similarity gets the highest weight, but metadata improves
    real-world matching quality.
    """
    results["hybrid_score"] = (
    0.40 * results["similarity_score"] +
    0.15 * results["item_name_score"] +
    0.15 * results["category_score"] +
    0.10 * results["color_score"] +
    0.10 * results["location_score"] +
    0.07 * results["date_score"] +
    0.03 * results["brand_score"]
)
    return results


# ------------------------------------------------------------
# 6. Confidence label
# ------------------------------------------------------------

def get_confidence_label(score):
    """Convert hybrid score into a user-friendly confidence label."""
    if score >= 0.50:
        return "High"
    elif score >= 0.35:
        return "Medium"
    else:
        return "Low"


# ------------------------------------------------------------
# 7. Match reasons
# ------------------------------------------------------------

def get_match_reasons(row):
    """
    Explain why a found item was recommended.
    This makes the matcher more transparent and product-like.
    """
    reasons = []

    if row["item_name_score"] == 1:
        reasons.append("same item type")

    if row["category_score"] == 1:
        reasons.append("same category")

    if row["color_score"] == 1:
        reasons.append("same color")

    if row["brand_score"] == 1:
        reasons.append("same brand")
    elif row["brand_score"] == 0.5:
        reasons.append("brand unknown/partial brand match")

    if row["location_score"] == 1:
        reasons.append("same location")

    if row["date_score"] == 1:
        reasons.append("found within 2 days")
    elif row["date_score"] == 0.7:
        reasons.append("found within 1 week")
    elif row["date_score"] == 0.4:
        reasons.append("found within 2 weeks")

    if len(reasons) == 0:
        return "no strong metadata match"

    return "; ".join(reasons)


# ------------------------------------------------------------
# 8. Get top matches for one lost item
# ------------------------------------------------------------

def get_top_matches(lost_item, found_data, use_hybrid=True, top_k=5):
    """
    Match one lost item against all found items.

    If use_hybrid is False:
        rank only by text similarity.

    If use_hybrid is True:
        rank by hybrid score using text + metadata.
    """
    similarity_scores = calculate_text_similarity(
        lost_item["description"],
        found_data["description"]
    )

    results = found_data.copy()
    results["similarity_score"] = similarity_scores

    if use_hybrid:
        results = add_metadata_scores(results, lost_item)
        results = add_hybrid_score(results)

        results["confidence_label"] = results["hybrid_score"].apply(
            get_confidence_label
        )

        results["match_reasons"] = results.apply(
            get_match_reasons,
            axis=1
        )

        ranked_results = results.sort_values(
            "hybrid_score",
            ascending=False
        ).reset_index(drop=True)

    else:
        ranked_results = results.sort_values(
            "similarity_score",
            ascending=False
        ).reset_index(drop=True)

    return ranked_results.head(top_k)


# ------------------------------------------------------------
# 9. Evaluate matcher
# ------------------------------------------------------------

def evaluate_matcher(lost_data, found_data, use_hybrid=True):
    """
    Evaluate matcher using lost items that have a known true_match_id.

    Metrics:
    - Top-1 Accuracy
    - Top-3 Accuracy
    - Top-5 Accuracy
    """
    matched_lost_data = lost_data[lost_data["true_match_id"].notna()].copy()

    evaluation_results = []

    for x in range(len(matched_lost_data)):
        lost_item = matched_lost_data.iloc[x]
        true_match_id = lost_item["true_match_id"]

        ranked_matches = get_top_matches(
            lost_item,
            found_data,
            use_hybrid=use_hybrid,
            top_k=5
        )

        top_1_ids = ranked_matches.head(1)["post_id"].tolist()
        top_3_ids = ranked_matches.head(3)["post_id"].tolist()
        top_5_ids = ranked_matches.head(5)["post_id"].tolist()

        evaluation_results.append({
            "lost_id": lost_item["post_id"],
            "true_match_id": true_match_id,
            "top_1_match": top_1_ids[0],
            "top_1_correct": true_match_id in top_1_ids,
            "top_3_correct": true_match_id in top_3_ids,
            "top_5_correct": true_match_id in top_5_ids
        })

    evaluation_df = pd.DataFrame(evaluation_results)

    return evaluation_df


# ------------------------------------------------------------
# 10. Create comparison summary
# ------------------------------------------------------------

def create_comparison_summary(text_df, hybrid_df):
    """Compare text-only matcher and hybrid matcher accuracy."""
    comparison = pd.DataFrame({
        "metric": ["Top-1 Accuracy", "Top-3 Accuracy", "Top-5 Accuracy"],
        "text_only": [
            text_df["top_1_correct"].mean(),
            text_df["top_3_correct"].mean(),
            text_df["top_5_correct"].mean()
        ],
        "hybrid": [
            hybrid_df["top_1_correct"].mean(),
            hybrid_df["top_3_correct"].mean(),
            hybrid_df["top_5_correct"].mean()
        ]
    })

    return comparison


# ------------------------------------------------------------
# 11. Save outputs
# ------------------------------------------------------------

def save_outputs(text_df, hybrid_df, comparison, example_top_matches):
    """Save important project results as CSV files."""
    text_df.to_csv(f"{OUTPUT_DIR}/text_only_evaluation.csv", index=False)
    hybrid_df.to_csv(f"{OUTPUT_DIR}/hybrid_evaluation.csv", index=False)
    comparison.to_csv(f"{OUTPUT_DIR}/comparison_summary.csv", index=False)
    example_top_matches.to_csv(f"{OUTPUT_DIR}/example_top_matches.csv", index=False)


# ------------------------------------------------------------
# 12. Create charts
# ------------------------------------------------------------

def create_accuracy_chart(comparison):
    """Create bar chart comparing text-only and hybrid accuracy."""
    x = np.arange(len(comparison["metric"]))
    width = 0.35

    plt.figure(figsize=(8, 5))
    plt.bar(x - width / 2, comparison["text_only"], width, label="Text-only")
    plt.bar(x + width / 2, comparison["hybrid"], width, label="Hybrid")

    plt.xlabel("Metric")
    plt.ylabel("Accuracy")
    plt.title("Text-only vs Hybrid Matcher Accuracy")
    plt.xticks(x, comparison["metric"])
    plt.ylim(0, 1.1)
    plt.legend()
    plt.tight_layout()

    plt.savefig(f"{OUTPUT_DIR}/accuracy_comparison.png")
    plt.show()


def create_category_chart(data):
    """Create category distribution chart for the full dataset."""
    counts = data["category"].value_counts()
    categories = counts.index

    plt.figure(figsize=(9, 5))
    plt.bar(categories, counts)

    plt.title("Overall Category Distribution")
    plt.xlabel("Categories")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig(f"{OUTPUT_DIR}/category_distribution.png")
    plt.show()


def create_location_chart(data):
    """Create chart for the top 10 campus locations."""
    counts = data["location"].value_counts().head(10)
    locations = counts.index

    plt.figure(figsize=(9, 5))
    plt.bar(locations, counts)

    plt.title("Top 10 Campus Locations")
    plt.xlabel("Locations")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    plt.savefig(f"{OUTPUT_DIR}/top_locations.png")
    plt.show()


# ------------------------------------------------------------
# 13. Main project workflow
# ------------------------------------------------------------

def main():
    # Load and check data
    data = load_data(DATA_PATH)
    inspect_data(data)

    # Split lost and found posts
    lost_data, found_data = split_lost_found(data)

    # Evaluate text-only baseline
    text_evaluation_df = evaluate_matcher(
        lost_data,
        found_data,
        use_hybrid=False
    )

    print("\n========== TEXT-ONLY MATCHER EVALUATION ==========")
    print(text_evaluation_df.head())

    print("\nText-only matcher accuracy:")
    print("Top-1 Accuracy:", text_evaluation_df["top_1_correct"].mean())
    print("Top-3 Accuracy:", text_evaluation_df["top_3_correct"].mean())
    print("Top-5 Accuracy:", text_evaluation_df["top_5_correct"].mean())

    # Evaluate hybrid matcher
    hybrid_evaluation_df = evaluate_matcher(
        lost_data,
        found_data,
        use_hybrid=True
    )

    print("\n========== HYBRID MATCHER EVALUATION ==========")
    print(hybrid_evaluation_df.head())

    print("\nHybrid matcher accuracy:")
    print("Top-1 Accuracy:", hybrid_evaluation_df["top_1_correct"].mean())
    print("Top-3 Accuracy:", hybrid_evaluation_df["top_3_correct"].mean())
    print("Top-5 Accuracy:", hybrid_evaluation_df["top_5_correct"].mean())

    # Compare both approaches
    comparison = create_comparison_summary(
        text_evaluation_df,
        hybrid_evaluation_df
    )

    print("\n========== TEXT-ONLY VS HYBRID COMPARISON ==========")
    print(comparison)

    # Show one product-style example
    matched_lost_data = lost_data[lost_data["true_match_id"].notna()].copy()
    example_lost_item = matched_lost_data.iloc[0]

    print("\n========== EXAMPLE LOST ITEM ==========")
    print(example_lost_item[[
        "post_id",
        "item_name",
        "category",
        "color",
        "brand",
        "location",
        "date",
        "description",
        "true_match_id"
    ]])

    example_top_matches = get_top_matches(
        example_lost_item,
        found_data,
        use_hybrid=True,
        top_k=5
    )

    print("\n========== TOP 5 HYBRID MATCHES WITH REASONS ==========")
    print(example_top_matches[[
        "post_id",
        "item_name",
        "hybrid_score",
        "confidence_label",
        "match_reasons"
    ]])

    # Save CSV outputs
    save_outputs(
        text_evaluation_df,
        hybrid_evaluation_df,
        comparison,
        example_top_matches
    )

    # Save charts
    create_accuracy_chart(comparison)
    create_category_chart(data)
    create_location_chart(data)


if __name__ == "__main__":
    main()