# Financial News Sentiment Mini Project
# Classifies short financial sentences as positive, negative, or neutral using TF-IDF and Logistic Regression.

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

data = {
    "text": [
        # positive
        "The company reported strong revenue growth",
        "Earnings increased compared to last quarter",
        "The firm exceeded analyst expectations",
        "Sales rose due to higher customer demand",
        "The company expanded into new markets",
        "Profit improved after cost reductions",
        "The business reported record quarterly revenue",
        "Investors reacted positively to the earnings report",
        "The company raised its full year guidance",
        "Operating income increased significantly",

        # negative
        "Profit margins declined due to higher costs",
        "The company missed analyst expectations",
        "Revenue fell compared to last quarter",
        "The firm warned of weaker demand",
        "Operating expenses increased sharply",
        "The company reported a quarterly loss",
        "Investors reacted negatively to the earnings report",
        "The business lowered its full year guidance",
        "Sales declined because of supply chain issues",
        "The company faced pressure from rising costs",

        # neutral
        "The company announced its quarterly results",
        "The board appointed a new chief financial officer",
        "The firm released its annual report",
        "The company held an investor conference",
        "The business updated its corporate strategy",
        "The company opened a new office",
        "The annual meeting will take place next month",
        "The firm published details about its operations",
        "The company completed a scheduled leadership transition",
        "The report included information about market conditions"
    ],
    "label": [
        # positive
        "positive", "positive", "positive", "positive", "positive",
        "positive", "positive", "positive", "positive", "positive",

        # negative
        "negative", "negative", "negative", "negative", "negative",
        "negative", "negative", "negative", "negative", "negative",

        # neutral
        "neutral", "neutral", "neutral", "neutral", "neutral",
        "neutral", "neutral", "neutral", "neutral", "neutral"
    ]
}

df = pd.DataFrame(data)
X = df["text"]
y = df["label"]
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size = 0.2, random_state = 45, stratify = y)
vectorizer = TfidfVectorizer(ngram_range=(1,2))
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)
model = LogisticRegression()
model.fit(X_train_tfidf, y_train)
predictions = model.predict(X_test_tfidf)

print("Test Data Results")
print(f"Accuracy: {accuracy_score(y_test, predictions)}")
print(f"Classification-report:\n{classification_report(y_test, predictions)}")
print(f"Confusion-matrix:\n{confusion_matrix(y_test, predictions)}")

#Testing on custom data to evaluate the model
custom_data = {
    "sentence": [
        "The company reported higher revenue and stronger earnings",
        "Profit margins declined because of rising expenses",
        "The firm announced a new investor presentation",
        "Sales increased but operating costs also rose sharply",
        "The company lowered its full year guidance"
    ],
    "actual_label": [
        "positive",
        "negative",
        "neutral",
        "neutral",
        "negative"
    ]
}

df_testing = pd.DataFrame(custom_data)
X_testing = df_testing["sentence"]
y_testing = df_testing["actual_label"]
X_testing_tfidf = vectorizer.transform(X_testing)
testing_predictions = model.predict(X_testing_tfidf)

print("Custom Data Results")
print(f"Accuracy: {accuracy_score(y_testing, testing_predictions)}")
print(f"Classification-report:\n{classification_report(y_testing, testing_predictions)}")
print(f"Confusion-matrix:\n{confusion_matrix(y_testing, testing_predictions)}")

results = {
    "sentences" : X_testing,
    "actual_label" : y_testing,
    "predicted_label" : testing_predictions,
}

results = pd.DataFrame(results)
results["correct"] = results["actual_label"] == results["predicted_label"]

print(results.to_string())







