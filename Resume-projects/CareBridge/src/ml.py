"""Small explainable ML example: TF-IDF + logistic regression document routing."""
from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

TRAINING_TEXTS = [
    "referral requested specialist consultation reason for referral",
    "referring clinician authorization specialist appointment",
    "laboratory results specimen collected reference range panel",
    "blood test result laboratory value collected",
    "insurance member id group number coverage plan",
    "health plan insurance card subscriber member",
    "visit summary assessment follow up appointment provider",
    "previous visit note instructions follow-up plan",
]
TRAINING_LABELS = ["Referral", "Referral", "Lab result", "Lab result", "Insurance", "Insurance", "Visit note", "Visit note"]


def build_classifier() -> Pipeline:
    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), stop_words="english")),
        ("model", LogisticRegression(max_iter=500, random_state=42)),
    ])
    return model.fit(TRAINING_TEXTS, TRAINING_LABELS)


def classify_document(text: str) -> tuple[str, float]:
    model = build_classifier()
    probabilities = model.predict_proba([text])[0]
    index = probabilities.argmax()
    return str(model.classes_[index]), float(probabilities[index])

