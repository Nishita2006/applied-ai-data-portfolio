## Live Demo

Try the app here: https://campus-lost-found-ai-matcher.streamlit.app

# Campus Lost & Found AI Matcher

An AI-powered Streamlit app that matches lost item reports with possible found item reports using NLP text similarity, metadata-based scoring, confidence labels, and explainable match reasons.

## Project Overview

Campus lost and found systems often rely on manual searching, which can make it difficult to connect lost item reports with matching found item reports. This project builds an AI-assisted matching system that compares lost and found item descriptions and ranks the most likely matches.

The app allows a user to select a lost item and view the top possible found item matches with a hybrid score, confidence label, and explanation for why each match was recommended.

## Features

* Match lost item reports with possible found item reports
* NLP-based text similarity using TF-IDF and cosine similarity
* Hybrid scoring using item name, category, color, location, date, brand, and description similarity
* Confidence labels: High, Medium, Low
* Explainable match reasons for each recommendation
* Streamlit web app for interactive demo
* Evaluation comparing text-only matching vs hybrid matching
* Dashboard with model performance and dataset visualizations

## Tech Stack

* Python
* Pandas
* NumPy
* Scikit-learn
* Matplotlib
* Streamlit

## Dataset

The dataset contains synthetic campus lost and found posts with the following fields:

* post_id
* post_type
* item_name
* category
* color
* brand
* description
* location
* date
* contact_method
* true_match_id
* match_group

The dataset includes both lost and found posts, along with known true matches for evaluation.

## Matching Approach

The project first uses text-only matching by comparing lost item descriptions against found item descriptions using TF-IDF and cosine similarity.

Then, it improves the system using a hybrid scoring method that combines text similarity with structured metadata.

The hybrid score considers:

* Description similarity
* Item name match
* Category match
* Color match
* Location match
* Date closeness
* Brand match

This helps the system rank matches more realistically than text similarity alone.

## Results

The hybrid matcher improved performance compared to the text-only baseline.

| Metric         | Text-only | Hybrid |
| -------------- | --------: | -----: |
| Top-1 Accuracy |      0.74 |   1.00 |
| Top-3 Accuracy |      0.84 |   1.00 |
| Top-5 Accuracy |      0.90 |   1.00 |

## Screenshots

### App Home

![App Home](screenshots/app_home.png)

### Match Results

![Match Results](screenshots/match_results.png)

### Results Dashboard

![Dashboard](screenshots/dashboard.png)

## How to Run

1. Clone the repository.

2. Install the required packages.

```bash
pip install pandas numpy scikit-learn matplotlib streamlit
```

3. Run the Streamlit app.

```bash
streamlit run Resume-projects/campus-lost-found-ai-matcher/src/app.py
```

## Project Structure

```text
campus-lost-found-ai-matcher/
├── data/
│   └── lost_found_posts.csv
├── outputs/
│   ├── accuracy_comparison.png
│   ├── category_distribution.png
│   ├── top_locations.png
│   ├── text_only_evaluation.csv
│   ├── hybrid_evaluation.csv
│   ├── comparison_summary.csv
│   └── example_top_matches.csv
├── screenshots/
│   ├── app_home.png
│   ├── match_results.png
│   └── dashboard.png
├── src/
│   ├── app.py
│   └── lost_found_matcher.py
└── README.md
```

## Limitations

* The dataset is synthetic, so performance may be higher than it would be on real-world campus data.
* Real lost and found descriptions may contain more spelling mistakes, incomplete details, or vague descriptions.
* Some categories are broad, so additional item-specific logic may be needed for real deployment.
* The app currently works with preloaded data and does not yet support user-submitted new reports.

## Future Improvements

* Add user input forms for new lost and found reports
* Store reports in a database
* Add fuzzy matching for spelling mistakes
* Improve brand and item-name matching
* Add image-based matching for uploaded item photos
* Deploy the Streamlit app online

## Resume Summary

Built an AI-powered campus lost and found matching app using Python, Streamlit, and Scikit-learn. Implemented TF-IDF text similarity, hybrid metadata scoring, confidence labels, explainable match reasons, and an interactive dashboard comparing text-only and hybrid model performance.
